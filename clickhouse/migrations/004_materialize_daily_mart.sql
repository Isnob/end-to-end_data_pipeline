DROP VIEW IF EXISTS analytics.mart_asset_prices_daily;
DROP VIEW IF EXISTS analytics.mv_mart_asset_prices_daily;

CREATE TABLE IF NOT EXISTS analytics.mart_asset_prices_daily_agg
(
    exchange LowCardinality(String),
    symbol LowCardinality(String),
    price_date Date,

    min_price_state AggregateFunction(min, Decimal(18, 8)),
    max_price_state AggregateFunction(max, Decimal(18, 8)),
    avg_price_state AggregateFunction(avg, Decimal(18, 8)),
    records_count_state AggregateFunction(count),
    first_fetched_at_state AggregateFunction(min, DateTime64(6, 'UTC')),
    last_fetched_at_state AggregateFunction(max, DateTime64(6, 'UTC'))
)
ENGINE = AggregatingMergeTree
ORDER BY (exchange, symbol, price_date);

CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_mart_asset_prices_daily
TO analytics.mart_asset_prices_daily_agg
AS
SELECT
    exchange,
    symbol,
    toDate(fetched_at) AS price_date,

    minState(price) AS min_price_state,
    maxState(price) AS max_price_state,
    avgState(price) AS avg_price_state,
    countState() AS records_count_state,
    minState(fetched_at) AS first_fetched_at_state,
    maxState(fetched_at) AS last_fetched_at_state
FROM analytics.fact_asset_prices
GROUP BY
    exchange,
    symbol,
    price_date;

TRUNCATE TABLE analytics.mart_asset_prices_daily_agg;

INSERT INTO analytics.mart_asset_prices_daily_agg
SELECT
    exchange,
    symbol,
    toDate(fetched_at) AS price_date,

    minState(price),
    maxState(price),
    avgState(price),
    countState(),
    minState(fetched_at),
    maxState(fetched_at)
FROM analytics.fact_asset_prices
GROUP BY
    exchange,
    symbol,
    price_date;

CREATE VIEW IF NOT EXISTS analytics.mart_asset_prices_daily AS
SELECT
    exchange,
    symbol,
    price_date,

    minMerge(min_price_state) AS min_price,
    maxMerge(max_price_state) AS max_price,
    round(avgMerge(avg_price_state), 8) AS avg_price,
    countMerge(records_count_state) AS records_count,
    minMerge(first_fetched_at_state) AS first_fetched_at,
    maxMerge(last_fetched_at_state) AS last_fetched_at
FROM analytics.mart_asset_prices_daily_agg
GROUP BY
    exchange,
    symbol,
    price_date;
