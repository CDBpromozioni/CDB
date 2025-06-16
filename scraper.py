import requests
from bs4 import BeautifulSoup
from db import get_db_connection

# Lista competitor
sites = {
    "Vino.com": "https://vino.com/",
    "Bernabei": "https://bernabei.it/",
    "CallMeWine": "https://callmewine.com/",
    "Tannico": "https://tannico.it/",
    "Signorvino": "https://signorvino.com/",
    "Wineshop": "https://wineshop.it/",
    "Svinando": "https://svinando.com/"
}

# Telegram config
TELEGRAM_TOKEN = "7901232274:AAFM3HMotVhmEj80AyUwnTAxuZ6VCpSnXY4"
TELEGRAM_CHAT_ID = "7963309279"

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=data)

def run_scraper():
    conn = get_db_connection()
    cur = conn.cursor()

    new_promotions = []

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
                new_promotions.append(f"{name}: {title}")

        except Exception as e:
            print(f"Errore su {name}: {str(e)}")

    cur.close()
    conn.close()

    if new_promotions:
        message = "Nuove promozioni rilevate:\n" + "\n".join(new_promotions)
        send_telegram_message(message)
        return message
    else:
        return "Nessuna nuova promozione trovata."
