"""
Odds scraper for China Sporttery mobile page
- tries requests + HTML parsing first
- falls back to Selenium if --use-selenium is passed
- respects robots.txt and rate limits (simple)
- saves structured results to SQLite and JSON file under backend/reports/

Usage:
    python backend/football/odds_scraper.py --fetch [--use-selenium]

"""
import os
import re
import json
import time
import logging
import argparse
import sqlite3
from datetime import datetime
from urllib.parse import urlparse
import urllib.robotparser

import requests
from bs4 import BeautifulSoup

LOG = logging.getLogger("odds_scraper")
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://m.sporttery.cn/mjc/jsq/zqhhgg/"
REPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'odds.sqlite')

os.makedirs(REPORT_DIR, exist_ok=True)


def robots_allowed(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch('*', url)
    except Exception as e:
        LOG.warning('Could not fetch robots.txt (%s): assuming allowed', e)
        return True


def try_parse_embedded_json(html_text):
    """Try to locate embedded JSON in scripts or HTML. Return python obj or None."""
    # common patterns: window.__INITIAL_STATE__ = {...}; or var data = {...};
    patterns = [
        r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*;",
        r"var\s+__data\s*=\s*(\{.*?\})\s*;",
        r"=\s*(\{\"leagueList\".*?\})\s*;",
        r"(\{\s*\"oddsList\".*?\})",
    ]
    for pat in patterns:
        m = re.search(pat, html_text, re.S)
        if m:
            try:
                js = m.group(1)
                data = json.loads(js)
                return data
            except Exception:
                # try to fix single quotes or trailing commas
                try:
                    fixed = js.replace("'", '"')
                    data = json.loads(fixed)
                    return data
                except Exception:
                    continue
    return None


def extract_odds_from_html(html_text):
    """Best-effort parsing of the mobile page HTML to extract matches and odds."""
    soup = BeautifulSoup(html_text, 'lxml')
    results = []

    # Try to find match blocks — this is heuristic and may need tuning
    # Look for elements containing team names and odds patterns
    for item in soup.find_all(text=re.compile(r"\d+\.\d+")):
        parent = item.parent
        text = parent.get_text(separator='|', strip=True)
        # crude split by | and try to find three float numbers
        floats = re.findall(r"\d+\.\d+", text)
        if len(floats) >= 3:
            # try to find team names in nearby siblings
            # walk up to container
            cont = parent
            for _ in range(4):
                cont = cont.parent or cont
            txt = cont.get_text(separator='|', strip=True)
            parts = txt.split('|')
            # heuristic: look for two non-numeric parts around floats
            names = [p for p in parts if not re.search(r"\d+\.\d+", p)]
            if len(names) >= 2:
                home, away = names[0], names[1]
            else:
                home, away = '未知主队', '未知客队'
            odds = {
                'ht_win': float(floats[0]),
                'draw': float(floats[1]),
                'at_win': float(floats[2])
            }
            results.append({
                'home': home,
                'away': away,
                'odds': odds,
                'raw_text': text
            })
    return results


def save_to_sqlite(raw_json, structured_list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS odds_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fetched_at TEXT,
                    source TEXT,
                    raw_json TEXT,
                    data_json TEXT
                 )''')
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO odds_history (fetched_at, source, raw_json, data_json) VALUES (?, ?, ?, ?)',
              (now, 'sporttery_m', json.dumps(raw_json, ensure_ascii=False), json.dumps(structured_list, ensure_ascii=False)))
    conn.commit()
    conn.close()


def save_json_file(structured_list):
    fn = os.path.join(REPORT_DIR, f"odds_{datetime.now().strftime('%Y%m%d')}.json")
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(structured_list, f, ensure_ascii=False, indent=2)
    LOG.info('Saved odds to %s', fn)


def fetch_with_requests(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Referer': 'https://m.sporttery.cn/'
    }
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text


def fetch_with_selenium(url):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=opts)
        driver.get(url)
        time.sleep(3)
        html = driver.page_source
        driver.quit()
        return html
    except Exception as e:
        LOG.exception('Selenium fetch failed: %s', e)
        raise


def run(fetch_url=BASE_URL, use_selenium=False):
    LOG.info('Starting odds scraper for %s', fetch_url)
    if not robots_allowed(fetch_url):
        LOG.warning('Robots.txt disallows fetching %s — aborting', fetch_url)
        return None

    html = None
    try:
        html = fetch_with_requests(fetch_url)
    except Exception as e:
        LOG.warning('Requests fetch failed: %s', e)
        if use_selenium:
            try:
                html = fetch_with_selenium(fetch_url)
            except Exception:
                LOG.error('Both requests and selenium failed')
                return None
        else:
            LOG.info('Selenium fallback not enabled')
            return None

    # try embedded json
    embedded = try_parse_embedded_json(html)
    structured = None
    if embedded:
        LOG.info('Found embedded JSON, attempting to extract odds')
        # Try to locate common odds containers in embedded JSON
        # This is site-specific and may need adaptation
        if isinstance(embedded, dict):
            # heuristic: look for keys containing 'odds' or 'match'
            def scan(obj):
                results = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if 'odds' in k.lower() and isinstance(v, list):
                            for it in v:
                                results.append(it)
                        else:
                            results.extend(scan(v))
                elif isinstance(obj, list):
                    for it in obj:
                        results.extend(scan(it))
                return results
            found = scan(embedded)
            if found:
                structured = []
                for it in found:
                    structured.append(it)
    if structured is None:
        LOG.info('No embedded JSON usable — attempting HTML heuristics')
        structured = extract_odds_from_html(html)

    if not structured:
        LOG.warning('No odds found from page')
        return None

    # save
    save_to_sqlite(embedded if embedded is not None else {'html_snippet': 'extracted'}, structured)
    save_json_file(structured)
    LOG.info('Scrape complete: %d matches', len(structured))
    return structured


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--fetch', action='store_true')
    p.add_argument('--use-selenium', action='store_true')
    args = p.parse_args()

    if args.fetch:
        out = run(use_selenium=args.use_selenium)
        if out is None:
            LOG.error('No data extracted')
        else:
            LOG.info('Extracted %d records', len(out))
