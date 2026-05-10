select
    id as raw_asset_id,
    exchange,
    symbol,
    fetched_at,
    cast(price as numeric) as price,
    raw_payload
from {{ source('raw', 'raw_assets') }}
where price is not null
