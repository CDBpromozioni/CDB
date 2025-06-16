import requests
from bs4 import BeautifulSoup

def run_scraper():
    url = 'https://vino.com/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'Titolo non trovato'
        return f"Scraping riuscito! Titolo pagina: {title}"
    else:
        return f"Errore nel caricamento: {response.status_code}"
