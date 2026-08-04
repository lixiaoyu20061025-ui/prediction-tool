# Sporttery scraper documentation

This directory contains the scraper implementation for the China Sporttery mobile odds page: https://m.sporttery.cn/mjc/jsq/zqhhgg/

Files added:
- backend/football/odds_scraper.py  - main scraper (requests + optional Selenium fallback)
- backend/football/api_odds.py      - Flask blueprint providing endpoints to fetch latest odds and reports
- backend/football/scheduler.py     - simple scheduler script to run scraper (for cron)

Usage
-----

1. Install dependencies:

    pip install requests beautifulsoup4 lxml

Optionally install Selenium and ChromeDriver for pages requiring JS rendering:

    pip install selenium
    # install chromedriver and ensure it's on PATH

2. Run scraper once:

    python backend/football/odds_scraper.py --fetch

If the page is JS heavy, use:

    python backend/football/odds_scraper.py --fetch --use-selenium

3. Start Flask app (for API access):

    export FLASK_APP=backend/app.py
    flask run

4. API endpoints

- GET /api/football/odds/latest  - latest odds JSON
- GET /api/football/odds/<YYYYMMDD> - get odds JSON for a specific date
- GET /api/football/reports - list available report files
- GET /api/football/reports/download/<YYYYMMDD> - download JSON report

Notes
-----
- The scraper respects robots.txt; if the site disallows scraping the script will abort.
- By default results are saved in backend/reports/odds_YYYYMMDD.json and in SQLite backend/odds.sqlite (table odds_history).
- Parsing is heuristic and may require adjustments if the site changes. If results look incorrect, provide the generated raw file and I will refine parsing rules.
