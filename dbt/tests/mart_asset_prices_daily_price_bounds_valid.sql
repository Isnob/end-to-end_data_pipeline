select *
from {{ ref('mart_asset_prices_daily') }}
where
    min_price > avg_price
    or avg_price > max_price
