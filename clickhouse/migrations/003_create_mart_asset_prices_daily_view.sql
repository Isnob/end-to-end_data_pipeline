CREATE VIEW IF NOT EXISTS analytics.mart_asset_prices_daily AS
SELECT
    exchange,
    symbol,
    toDate(fetched_at) AS price_date,
    min(price) AS min_price,
    max(price) AS max_price,
    round(avg(price), 8) AS avg_price,
    count() AS records_count,
    min(fetched_at) AS first_fetched_at,
    max(fetched_at) AS last_fetched_at
FROM analytics.fact_asset_prices
GROUP BY
    exchange,
    symbol,
    price_date;
