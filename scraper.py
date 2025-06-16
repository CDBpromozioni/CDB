import requests
from bs4 import BeautifulSoup
from db import get_db_connection

sites = {
    "Vino.com": "https://vino.com/",
    "Bernabei": "https://bernabei.it/",
    "CallMeWine": "https://callmewine.com/",
    "Tannico": "https://tannico.it/",
    "Signorvino": "https://signorvino.com/",
    "Wineshop": "https://wineshop.it/",
    "Svinando": "https://svinando.com/"
}

def run_scraper():
    conn = get_db_connection()
    cur = conn.cursor()

    for name, url in sites.items():
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else 'Titolo non trovato'

            cur.execute('SELECT * FROM promotions WHERE titolo = %s AND sito = %s', (title, name))
            if not cur.fetchone():
                cur.execute(
                    'INSERT INTO promotions (sito, titolo, url, prezzo) VALUES (%s, %s, %s, %s)',
                    (name, title, url, 'N/A')
                )
                conn.commit()

        except Exception as e:
            print(f"Errore su {name}: {str(e)}")

    cur.close()
    conn.close()
    return "Scraping completato."
