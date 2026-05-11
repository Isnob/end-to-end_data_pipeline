select *
from {{ ref('mart_asset_prices_daily') }}
where records_count <= 0
