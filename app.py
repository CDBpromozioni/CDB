from flask import Flask
from scraper import run_scraper
from db import create_table
import schedule
import time
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Il monitoraggio è attivo."

@app.route('/run-scraper')
def manual_run():
    return run_scraper()

def schedule_scraping():
    schedule.every().day.at("03:00").do(run_scraper)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    create_table()
    threading.Thread(target=schedule_scraping).start()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
