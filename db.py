import os
import psycopg2

def get_db_connection():
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS promotions (
            id SERIAL PRIMARY KEY,
            sito TEXT,
            titolo TEXT,
            url TEXT,
            prezzo TEXT,
            data TIMESTAMP DEFAULT NOW()
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()
