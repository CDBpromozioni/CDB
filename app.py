import requests
from bs4 import BeautifulSoup
import psycopg2
import os
import telebot
from datetime import datetime

# Variabili ambiente (tu le hai già impostate su Render)
DATABASE_URL = os.getenv("DATABASE_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Connessione al DB
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Funzione per inviare messaggio Telegram
def invia_telegram(messaggio):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio, parse_mode="HTML")

# Funzione generale di scraping (ti faccio vedere su vino.com come esempio)
def scrape_vino_com():
    url = "https://www.vino.com/price/promo"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    prodotti_trovati = []
    prodotti_html = soup.find_all("div", class_="ProductCardCardWrapper")

    for prodotto in prodotti_html:
        try:
            nome = prodotto.find("h3").get_text(strip=True)
            prezzo = prodotto.find("div", class_="ProductCardPrice__StyledPriceValue").get_text(strip=True)
            link = "https://www.vino.com" + prodotto.find("a")['href']

            # Inserisce solo se non esiste già
            cur.execute("SELECT COUNT(*) FROM promozioni WHERE prodotto = %s", (nome,))
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO promozioni (prodotto, prezzo, link) VALUES (%s, %s, %s)",
                    (nome, prezzo, link))
                conn.commit()

                prodotti_trovati.append(f"<b>{nome}</b>\n💰 {prezzo}\n🔗 {link}")
        except Exception as e:
            print("Errore:", e)

    return prodotti_trovati

# Avvio scraping
nuove_promozioni = scrape_vino_com()

# Invio su Telegram solo se ci sono novità
if nuove_promozioni:
    messaggio = "🆕 <b>Nuove promozioni trovate:</b>\n\n" + "\n\n".join(nuove_promozioni)
    invia_telegram(messaggio)
else:
    invia_telegram("✅ Nessuna nuova promozione trovata oggi.")

# Chiusura connessione
cur.close()
conn.close()
