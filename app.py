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

if __name__ == '__main__':
    app.run()
