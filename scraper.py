import psycopg2
import os
import telebot
from playwright.sync_api import sync_playwright

# Configurazione database
def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    return psycopg2.connect(DATABASE_URL)

# Configurazione Telegram
TELEGRAM_TOKEN = "7901232274:AAFM3HMotVhmEj80AyUwnTAxuZ6VCpSnXY4"
TELEGRAM_CHAT_IDS = ["7963309279"]

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def send_telegram_message(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        bot.send_message(chat_id, message)

# Funzione scraping su Vino.com con Playwright
def parse_vinocom():
    prodotti = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.vino.com/price/promo", timeout=60000)
        page.wait_for_timeout(5000)  # aspetta 5 secondi per il caricamento dinamico

        items = page.query_selector_all("a.product-card-link")

        for item in items:
            try:
                nome = item.query_selector("div.product-card-name").inner_text().strip()
                prezzo = item.query_selector("div.ProductCardPrice__StyledPriceValue").inner_text().strip()
                link = "https://www.vino.com" + item.get_attribute("href")
                prodotti.append((nome, prezzo, link))
            except Exception as e:
                print("Errore parsing:", e)

        browser.close()

    return prodotti

# Funzione principale
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
