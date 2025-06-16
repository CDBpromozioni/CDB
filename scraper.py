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
    url = "https://www.vino.com/price/promo"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    prodotti_trovati = []
    prodotti_html = soup.find_all("div", class_="ProductCardCardWrapper")

    for prodotto in prodotti_html:
        try:
            nome = prodotto.find("div", class_="product-card-name").get_text(strip=True)
            prezzo = prodotto.find("div", class_="ProductCardPrice__StyledPriceValue").get_text(strip=True)
            link = "https://www.vino.com" + prodotto.find("a", class_="product-card-link")['href']

            prodotti_trovati.append((nome, prezzo, link))
        except Exception as e:
            print("Errore parsing vino.com:", e)

    return prodotti_trovati

def main():
    conn = get_db_connection()
    cur = conn.cursor()

    prodotti = parse_vinocom()
    nuovi = []

    for nome, prezzo, link in prodotti:
        cur.execute("SELECT 1 FROM promozioni WHERE prodotto = %s", (nome,))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO promozioni (prodotto, prezzo, link) VALUES (%s, %s, %s)", (nome, prezzo, link))
            nuovi.append(f"{nome} - {prezzo}\n🔗 {link}")

    conn.commit()
    conn.close()

    if nuovi:
        messaggio = "📢 Nuove promozioni trovate:\n\n" + "\n\n".join(nuovi)
        send_telegram_message(messaggio)
    else:
        send_telegram_message("✅ Nessuna nuova promozione trovata oggi.")

if __name__ == "__main__":
    main()
