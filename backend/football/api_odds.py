from flask import Blueprint, jsonify, current_app, send_file
import os
import json
import sqlite3
from datetime import datetime

odds_bp = Blueprint('odds_api', __name__)

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
DB_PATH = os.path.join(BASE_DIR, 'odds.sqlite')


def _latest_json_path():
    fn = os.path.join(REPORT_DIR, f"odds_{datetime.now().strftime('%Y%m%d')}.json")
    return fn


@odds_bp.route('/odds/latest', methods=['GET'])
def get_latest_odds():
    """Return latest scraped odds (by file) or from DB if file not found."""
    fn = _latest_json_path()
    if os.path.exists(fn):
        with open(fn, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'source': 'file', 'file': os.path.basename(fn), 'data': data}), 200

    # fallback to DB
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT data_json, fetched_at FROM odds_history ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            try:
                data = json.loads(row[0])
            except Exception:
                data = row[0]
            return jsonify({'source': 'db', 'fetched_at': row[1], 'data': data}), 200

    return jsonify({'error': 'no data found'}), 404


@odds_bp.route('/odds/<date>', methods=['GET'])
def get_odds_by_date(date):
    """Return odds file for specific date in YYYYMMDD format if exists."""
    try:
        datetime.strptime(date, '%Y%m%d')
    except Exception:
        return jsonify({'error': 'invalid date format, expected YYYYMMDD'}), 400

    fn = os.path.join(REPORT_DIR, f"odds_{date}.json")
    if os.path.exists(fn):
        with open(fn, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'source': 'file', 'file': os.path.basename(fn), 'data': data}), 200

    return jsonify({'error': 'file not found'}), 404


@odds_bp.route('/reports', methods=['GET'])
def list_reports():
    """List available report files (odds_YYYYMMDD.json)"""
    items = []
    if os.path.isdir(REPORT_DIR):
        for fn in sorted(os.listdir(REPORT_DIR), reverse=True):
            if fn.startswith('odds_') and fn.endswith('.json'):
                items.append(fn)
    return jsonify({'reports': items}), 200


@odds_bp.route('/reports/download/<date>', methods=['GET'])
def download_report(date):
    fn = os.path.join(REPORT_DIR, f"odds_{date}.json")
    if os.path.exists(fn):
        return send_file(fn, mimetype='application/json', as_attachment=True, download_name=f'odds_{date}.json')
    return jsonify({'error': 'not found'}), 404
