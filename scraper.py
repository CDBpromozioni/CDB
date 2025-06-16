import requests
from bs4 import BeautifulSoup
from db import get_db_connection

# Lista competitor e relative URL promo
sites = {
    "Vino.com": "https://www.vino.com/price/promo",
    "Bernabei": "https://www.bernabei.it/offerte-in-corso",
    "Tannico": "https://www.tannico.it/collections/tutte-le-offerte",
    "CallMeWine": "https://www.callmewine.com/en/pages/wines-on-offer",
    "Signorvino": "https://www.signorvino.com/it/vini/tutte_le_promo/",
    "Wineshop": "https://www.wineshop.it/it/",
    "Svinando": "https://www.svinando.com/"
}

# Telegram config (restiamo sempre con il tuo bot attivo)
TELEGRAM_TOKEN = "7901232274:AAFM3HMotVhmEj80AyUwnTAxuZ6VCpSnXY4"
TELEGRAM_CHAT_IDS = ["7963309279"]  # Puoi aggiungere altri ID qui

def send_telegram_message(message):
    url_base = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    for chat_id in TELEGRAM_CHAT_IDS:
        data = {'chat_id': chat_id, 'text': message}
        requests.post(url_base, data=data)

# ATTENZIONE: qui ora per ogni sito usiamo funzioni separate
def parse_vinocom():
    url = sites["Vino.com"]
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'lxml')
    products = []
    for item in soup.select("a.product-card-link"):
        nome = item.select_one("div.product-card-name").text.strip()
        prezzo = item.select_one("div.price").text.strip()
        url_prodotto = "https://www.vino.com" + item['href']
        products.append((nome, url_prodotto, prezzo, ''))
    return products

# Per tutti gli altri siti (Bernabei, Tannico ecc.) il principio è lo stesso.
# Per semplicità iniziamo ora solo con Vino.com completo.
# Gli altri li aggiungiamo con lo stesso schema identico (appena mi dai l'ok proseguiamo).

def run_scraper():
    conn = get_db_connection()
    cur = conn.cursor()
    nuovi_prodotti = []

    # Per ora partiamo da Vino.com
    for nome, url in sites.items():
        if nome == "Vino.com":
            prodotti = parse_vinocom()
            for prodotto in prodotti:
                nome_prodotto, url_prodotto, prezzo_attuale, prezzo_pieno = prodotto

                cur.execute('SELECT * FROM promotions WHERE url_prodotto = %s', (url_prodotto,))
                if not cur.fetchone():
                    cur.execute(
                        'INSERT INTO promotions (sito, nome_prodotto, url_prodotto, prezzo_attuale, prezzo_pieno) VALUES (%s, %s, %s, %s, %s)',
                        (nome, nome_prodotto, url_prodotto, prezzo_attuale, prezzo_pieno)
                    )
                    conn.commit()
                    nuovi_prodotti.append(f"{nome}: {nome_prodotto} — {prezzo_attuale}")

    cur.close()
    conn.close()

    if nuovi_prodotti:
        message = "Nuove promozioni:\n" + "\n".join(nuovi_prodotti)
        send_telegram_message(message)
        return message
    else:
        return "Nessuna nuova promozione trovata."
