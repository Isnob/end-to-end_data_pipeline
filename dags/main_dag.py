from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import ccxt
import psycopg2

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def fetch_and_save():
    exchange = ccxt.binance()
    ticker = exchange.fetch_ticker('BTC/USDT')
    price = ticker['last']
    
    conn = psycopg2.connect(
        host='db',
        database='crypto_db',
        user='user',
        password='password'
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO btc_prices (timestamp, price) VALUES (%s, %s)",
        (datetime.now(), price)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully saved price: {price}")

def create_table_if_not_exists():
    conn = psycopg2.connect(
        host='db',
        database='crypto_db',
        user='user',
        password='password'
    )
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS btc_prices(" \
        "id SERIAL PRIMARY KEY," \
        "timestamp TIMESTAMP," \
        "price DECIMAL)"
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully created table btc_price")

with DAG(
    'crypto_ingestion_dag',
    default_args=default_args,
    description='Collect BTC prices every minute',
    schedule='* * * * *',
    catchup=False
) as dag:
    
    create_table = PythonOperator(
        task_id='create_table_btc_prices',
        python_callable=create_table_if_not_exists
    )

    get_crypto_data = PythonOperator(
        task_id='fetch_btc_price',
        python_callable=fetch_and_save
    )

    create_table >> get_crypto_data