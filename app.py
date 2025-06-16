from flask import Flask
from scraper import run_scraper

app = Flask(__name__)

@app.route('/')
def home():
    return "Il monitoraggio è attivo."

@app.route('/run-scraper')
def run():
    result = run_scraper()
    return result

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
