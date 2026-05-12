CREATE TABLE IF NOT EXISTS analytics.fact_asset_prices
(
    raw_asset_id UInt64,
    exchange LowCardinality(String),
    symbol LowCardinality(String),
    fetched_at DateTime64(6, 'UTC'),
    price Decimal(18, 8)
)
ENGINE = MergeTree
ORDER BY (exchange, symbol, fetched_at, raw_asset_id);
