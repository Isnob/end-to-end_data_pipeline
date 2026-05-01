import ccxt
import time
import psycopg2 # Наш новый гость
from datetime import datetime

# 1. Параметры подключения к базе (совпадают с docker-compose.yml)
DB_CONFIG = {
    "host": "db",
    "database": "crypto_db",
    "user": "user",
    "password": "password"
}

def get_connection():
    """Пытаемся подключиться к базе, пока она не проснется"""
    while True:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except psycopg2.OperationalError:
            print("База еще не готова... ждем 2 секунды")
            time.sleep(2)

def init_db():
    conn = get_connection() # Используем наш новый метод
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS btc_prices (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP,
            price DECIMAL
        );
    """)
    conn.commit()
    print("Таблица проверена/создана!")
    cur.close()
    conn.close()

def save_to_db(price):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO btc_prices (timestamp, price) VALUES (%s, %s)",
        (datetime.now(), price)
    )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db() # Подготавливаем базу
    exchange = ccxt.binance()
    
    while True:
        try:
            ticker = exchange.fetch_ticker('BTC/USDT')
            price = ticker['last']
            save_to_db(price) # Сохраняем!
            print(f"Saved: {price}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(15)