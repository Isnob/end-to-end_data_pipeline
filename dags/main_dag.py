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

with DAG(
    'crypto_ingestion_dag',
    default_args=default_args,
    description='Collect BTC prices every minute',
    schedule_interval='@minute',
    catchup=False
) as dag:

    get_crypto_data = PythonOperator(
        task_id='fetch_btc_price',
        python_callable=fetch_and_save
    )