{{ config(
    materialized='incremental',
    unique_key=['exchange', 'symbol', 'price_date']
) }}

with source as (
    select *
    from {{ ref('stg_asset_prices') }}

    {% if is_incremental() %}
        where date_trunc('day', fetched_at) >= (
            select coalesce(max(price_date), '1900-01-01'::timestamp)
            from {{ this }}
        )
    {% endif %}
)

select
    exchange,
    symbol,
    date_trunc('day', fetched_at) as price_date,
    min(price) as min_price,
    max(price) as max_price,
    round(avg(price), 8) as avg_price,
    count(*) as records_count,
    min(fetched_at) as first_fetched_at,
    max(fetched_at) as last_fetched_at
from source
group by
    exchange,
    symbol,
    date_trunc('day', fetched_at)
