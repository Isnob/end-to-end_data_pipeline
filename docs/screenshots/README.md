# Screenshots

Сделай скриншоты и сохрани их в эту папку с такими именами:

```text
01_airflow_dag_graph.png
02_airflow_successful_run.png
03_postgres_raw_assets.png
04_dbt_docs_lineage.png
05_clickhouse_tables.png
06_clickhouse_daily_mart.png
07_github_actions_deploy.png
```

Что должно быть на скриншотах:

- `01_airflow_dag_graph.png` - Airflow graph для `crypto_ingestion_dag`: `fetch_crypto_prices -> dbt_build -> sync_clickhouse`.
- `02_airflow_successful_run.png` - успешный DAG run, все задачи зеленые.
- `03_postgres_raw_assets.png` - query result с последними строками из `public.raw_assets`.
- `04_dbt_docs_lineage.png` - dbt docs lineage с моделями `stg_asset_prices` и `mart_asset_prices_daily`.
- `05_clickhouse_tables.png` - ClickHouse `system.tables` с engines для объектов в базе `analytics`.
- `06_clickhouse_daily_mart.png` - результат `SELECT * FROM analytics.mart_asset_prices_daily`.
- `07_github_actions_deploy.png` - успешный GitHub Actions workflow с `validate`, `integration`, `deploy`.
