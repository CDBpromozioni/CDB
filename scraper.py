import requests
from bs4 import BeautifulSoup
from db import get_db_connection

def check_vinocom():
    url = 'https://vino.com/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # ATTENZIONE: qui è solo struttura base da personalizzare
        products = soup.find_all('div')  # Da sostituire con il vero selettore
        print("Pagina caricata correttamente, prodotti trovati:", len(products))
    else:
        print("Errore nel caricamento pagina:", response.status_code)

if __name__ == '__main__':
    check_vinocom()
