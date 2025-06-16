import requests
from bs4 import BeautifulSoup
import psycopg2
from db import get_db_connection
import telebot

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

# Configurazione Telegram
TELEGRAM_TOKEN = "7901232274:AAFM3HMotVhmEj80AyUwnTAxuZ6VCpSnXY4"
TELEGRAM_CHAT_IDS = ["7963309279"]

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def send_telegram_message(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        bot.send_message(chat_id, message)

def parse_vinocom():
    url = sites["Vino.com"]
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'lxml')
    products = []
    for item in soup.select("a.product-card-link"):
        nome = item.select_one("div.product-card-name").text.strip()
        prezzo = item.select_one("div.price").text.strip()
        url_prodotto = "https://www.vino.com" + item['href']
        products.append((nome, url_prodotto, prezzo))
    return products

def main():
    conn = get_db_connection()
    cur = conn.cursor()

    prodotti = parse_vinocom()
    nuovi = []

    for nome, url_prodotto, prezzo in prodotti:
        cur.execute("SELECT 1 FROM promozioni WHERE prodotto = %s", (nome,))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO promozioni (prodotto, url, prezzo) VALUES (%s, %s, %s)", (nome, url_prodotto, prezzo))
            nuovi.append(f"{nome} - {prezzo}\n{url_prodotto}")

    conn.commit()
    conn.close()

    if nuovi:
        messaggio = "📢 Nuove promozioni trovate:\n\n" + "\n\n".join(nuovi)
        send_telegram_message(messaggio)
    else:
        send_telegram_message("✅ Nessuna nuova promozione trovata oggi.")

if __name__ == "__main__":
    main()
