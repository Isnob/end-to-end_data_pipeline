with source as (
    select
        id as raw_asset_id,
        exchange,
        symbol,
        fetched_at,
        date_trunc('minute', fetched_at) as fetched_minute,
        cast(price as numeric) as price,
        raw_payload
    from {{ source('raw', 'raw_assets') }}
    where price is not null
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by exchange, symbol, fetched_minute
            order by fetched_at desc, raw_asset_id desc
        ) as row_number
    from source
)

select
    raw_asset_id,
    exchange,
    symbol,
    fetched_at,
    price,
    raw_payload
from deduplicated
where row_number = 1
