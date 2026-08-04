"""
Simple scheduler script to run scraper. Meant to be invoked by cron or a task runner.
Usage (example cron):
  0 12 * * * /path/to/venv/bin/python /repo/backend/football/scheduler.py

This will call the odds_scraper.run() and store results.
"""
import os
import logging
from datetime import datetime

LOG = logging.getLogger('football.scheduler')
logging.basicConfig(level=logging.INFO)

from odds_scraper import run

if __name__ == '__main__':
    logging.info('Scheduler started at %s', datetime.utcnow().isoformat())
    try:
        res = run()
        if res:
            logging.info('Scraper returned %d records', len(res))
        else:
            logging.warning('Scraper returned no records')
    except Exception as e:
        logging.exception('Scheduler run failed: %s', e)
