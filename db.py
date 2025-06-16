import os
import psycopg2

def get_db_connection():
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL)
    return conn
