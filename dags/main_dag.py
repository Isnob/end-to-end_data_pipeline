from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.operators.python import PythonOperator
import ccxt
import psycopg2
from psycopg2.extras import Json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

DB_CONFIG = {
    'host': 'db',
    'database': 'crypto_db',
    'user': 'user',
    'password': 'password',
}

SYMBOLS = ('BTC/USDT', 'ETH/USDT')


def fetch_and_save():
    exchange = ccxt.binance({'enableRateLimit': True})

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(1)")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS raw_assets (
                    id SERIAL PRIMARY KEY,
                    exchange TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    fetched_at TIMESTAMPTZ NOT NULL,
                    price NUMERIC NOT NULL,
                    raw_payload JSONB NOT NULL
                )
                """
            )

            for symbol in SYMBOLS:
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                if price is None:
                    raise ValueError(f"Empty price received for {symbol}")

                fetched_at = datetime.now(timezone.utc)

                cur.execute(
                    """
                    INSERT INTO raw_assets (
                        exchange,
                        symbol,
                        fetched_at,
                        price,
                        raw_payload
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        exchange.id,
                        symbol,
                        fetched_at,
                        price,
                        Json(ticker),
                    )
                )

                print(f"Saved {symbol} price from {exchange.id}: {price}")


with DAG(
    'crypto_ingestion_dag',
    default_args=default_args,
    description='Collect crypto asset prices every 15 minutes',
    schedule='*/15 * * * *',
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
) as dag:
    get_crypto_data = PythonOperator(
        task_id='fetch_btc_price',
        python_callable=fetch_and_save
    )
