select
    exchange,
    symbol,
    date_trunc('day', fetched_at) as price_date,
    min(price) as min_price,
    max(price) as max_price,
    avg(price) as avg_price,
    count(*) as records_count,
    min(fetched_at) as first_fetched_at,
    max(fetched_at) as last_fetched_at
from {{ ref('stg_asset_prices') }}
group by
    exchange,
    symbol,
    date_trunc('day', fetched_at)
