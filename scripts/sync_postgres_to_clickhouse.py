import os

import clickhouse_connect
import psycopg2


POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'db'),
    'database': os.getenv('POSTGRES_DB', 'crypto_db'),
    'user': os.getenv('POSTGRES_USER', 'user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password'),
}

CLICKHOUSE_CONFIG = {
    'host': os.getenv('CLICKHOUSE_HOST', 'clickhouse'),
    'port': int(os.getenv('CLICKHOUSE_PORT', '8123')),
    'username': os.getenv('CLICKHOUSE_USER', 'user'),
    'password': os.getenv('CLICKHOUSE_PASSWORD', 'password'),
    'database': os.getenv('CLICKHOUSE_DATABASE', 'analytics'),
}

BATCH_SIZE = int(os.getenv('CLICKHOUSE_SYNC_BATCH_SIZE', '10000'))


def sync_asset_prices_to_clickhouse():
    clickhouse_client = clickhouse_connect.get_client(**CLICKHOUSE_CONFIG)

    last_loaded_raw_asset_id = clickhouse_client.query(
        """
        SELECT coalesce(max(raw_asset_id), 0)
        FROM analytics.fact_asset_prices
        """
    ).result_rows[0][0]

    total_synced_rows = 0

    with psycopg2.connect(**POSTGRES_CONFIG) as postgres_conn:
        with postgres_conn.cursor() as cursor:
            while True:
                rows = fetch_next_batch(cursor, last_loaded_raw_asset_id)

                if not rows:
                    break

                clickhouse_client.insert(
                    'analytics.fact_asset_prices',
                    rows,
                    column_names=[
                        'raw_asset_id',
                        'exchange',
                        'symbol',
                        'fetched_at',
                        'price',
                    ],
                )

                total_synced_rows += len(rows)
                last_loaded_raw_asset_id = rows[-1][0]

                print(
                    f'Synced {len(rows)} rows to ClickHouse. '
                    f'Last raw_asset_id in batch: {last_loaded_raw_asset_id}'
                )

    if total_synced_rows == 0:
        print(
            'No new rows to sync. '
            f'Last loaded raw_asset_id: {last_loaded_raw_asset_id}'
        )
        return

    print(f'Sync finished. Total synced rows: {total_synced_rows}')


def fetch_next_batch(cursor, last_loaded_raw_asset_id):
    cursor.execute(
        """
        SELECT
            raw_asset_id,
            exchange,
            symbol,
            fetched_at,
            price
        FROM analytics.stg_asset_prices
        WHERE raw_asset_id > %s
        ORDER BY raw_asset_id
        LIMIT %s
        """,
        (last_loaded_raw_asset_id, BATCH_SIZE),
    )
    return cursor.fetchall()
