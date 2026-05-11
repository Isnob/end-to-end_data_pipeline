SELECT *
FROM analytics.stg_asset_prices
ORDER BY fetched_at DESC;


SELECT *
FROM analytics.mart_asset_prices_daily
ORDER BY price_date DESC
LIMIT 10;

SELECT symbol, count(*), min(fetched_at), max(fetched_at)
FROM raw_assets
GROUP BY symbol
ORDER BY symbol;

SELECT
    symbol,
    date_trunc('minute', fetched_at) as fetched_minute,
    count(*) as rows_count
FROM raw_assets
GROUP BY symbol, date_trunc('minute', fetched_at)
HAVING count(*) > 1
ORDER BY fetched_minute DESC, symbol;

SELECT
    symbol,
    price_date,
    min_price,
    max_price,
    avg_price,
    records_count
FROM analytics.mart_asset_prices_daily
ORDER BY price_date DESC, symbol;
