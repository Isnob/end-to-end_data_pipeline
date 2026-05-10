select *
from {{ ref('stg_asset_prices') }}
where price <= 0
