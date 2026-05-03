from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
import ccxt
import psycopg2

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 1),
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

DB_CONFIG = {
    'host': 'db',
    'database': 'crypto_db',
    'user': 'user',
    'password': 'password',
}


def fetch_and_save():
    exchange = ccxt.binance()
    ticker = exchange.fetch_ticker('BTC/USDT')
    price = ticker['last']

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(9021001)")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS btc_prices (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    price DECIMAL NOT NULL
                )
                """
            )
            cur.execute(
                "INSERT INTO btc_prices (timestamp, price) VALUES (%s, %s)",
                (datetime.now(), price)
            )

    print(f"Successfully saved price: {price}")

with DAG(
    'crypto_ingestion_dag',
    default_args=default_args,
    description='Collect BTC prices every minute',
    schedule='* * * * *',
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
) as dag:
    get_crypto_data = PythonOperator(
        task_id='fetch_btc_price',
        python_callable=fetch_and_save
    )
