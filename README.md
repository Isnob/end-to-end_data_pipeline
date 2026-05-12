# End-to-End Crypto Data Pipeline

Пет-проект по data engineering: автоматический сбор live-цен криптовалют, обработка данных через dbt, оркестрация в Airflow, хранение raw/staging слоя в PostgreSQL и аналитический OLAP-слой в ClickHouse.

Проект показывает полный путь данных:

```text
Binance API -> Airflow -> PostgreSQL -> dbt -> ClickHouse -> analytical mart
```

## What Is Built

- Ingestion каждые 15 минут через Airflow DAG.
- Raw-данные сохраняются в PostgreSQL.
- dbt строит staging/mart модели и запускает data tests.
- Очищенные staging-данные синхронизируются в ClickHouse.
- ClickHouse хранит fact table и materialized daily mart через `AggregatingMergeTree`.
- GitHub Actions проверяет проект и автоматически деплоит ветку `demo` на сервер.
- Все сервисы работают в Docker Compose и закрыты за SSH-туннелями.

## Architecture

```text
crypto_ingestion_dag

fetch_crypto_prices
  -> PostgreSQL public.raw_assets

dbt_build
  -> PostgreSQL analytics.stg_asset_prices
  -> PostgreSQL analytics.mart_asset_prices_daily
  -> dbt tests

sync_clickhouse
  -> ClickHouse analytics.fact_asset_prices
  -> ClickHouse materialized daily mart
```

ClickHouse mart:

```text
analytics.fact_asset_prices
  -> analytics.mv_mart_asset_prices_daily
  -> analytics.mart_asset_prices_daily_agg
  -> analytics.mart_asset_prices_daily
```

`mart_asset_prices_daily` - read view для аналитических запросов. Он больше не считает дневную витрину напрямую из fact-таблицы: новые данные попадают в агрегатные состояния через materialized view.

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Python, CCXT |
| Orchestration | Apache Airflow |
| Raw/Staging Storage | PostgreSQL 15 |
| Transformations | dbt |
| OLAP Storage | ClickHouse |
| Containers | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | SSH deploy to VPS |

## Screenshots

### Airflow DAG

Airflow управляет полным пайплайном: ingestion, dbt build и sync в ClickHouse.

![Airflow DAG graph](docs/screenshots/01_airflow_dag_graph.png)

### Successful Pipeline Run

Все задачи DAG завершаются успешно: данные собраны, dbt-модели обновлены, ClickHouse синхронизирован.

![Airflow successful run](docs/screenshots/02_airflow_successful_run.png)

### PostgreSQL Raw Data

Raw-слой хранит live snapshots цен, полученные из Binance через CCXT.

![PostgreSQL raw data](docs/screenshots/03_postgres_raw_assets.png)

### dbt Docs

dbt documentation показывает lineage моделей и структуру transformation layer.

![dbt docs lineage](docs/screenshots/04_dbt_docs_lineage.png)

### ClickHouse Schema

ClickHouse содержит fact table, materialized view, aggregate table и read view.

![ClickHouse tables](docs/screenshots/05_clickhouse_tables.png)

### ClickHouse Daily Mart

Финальная дневная витрина доступна для аналитических запросов в ClickHouse.

![ClickHouse daily mart](docs/screenshots/06_clickhouse_daily_mart.png)

### CI/CD

GitHub Actions запускает validation, integration checks и deploy.

![GitHub Actions deploy](docs/screenshots/07_github_actions_deploy.png)

## Data Model

### PostgreSQL

```text
public.raw_assets
analytics.stg_asset_prices
analytics.mart_asset_prices_daily
```

`raw_assets` хранит исходные snapshots:

```sql
CREATE TABLE raw_assets (
    id SERIAL PRIMARY KEY,
    exchange TEXT NOT NULL,
    symbol TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    price NUMERIC NOT NULL,
    raw_payload JSONB NOT NULL
);
```

`stg_asset_prices` очищает raw-данные и дедуплицирует наблюдения по `exchange`, `symbol` и минуте `fetched_at`.

`mart_asset_prices_daily` в PostgreSQL остается dbt-витриной для сравнения и учебной части dbt.

### ClickHouse

```text
analytics.fact_asset_prices                  MergeTree
analytics.mv_mart_asset_prices_daily         MaterializedView
analytics.mart_asset_prices_daily_agg        AggregatingMergeTree
analytics.mart_asset_prices_daily            View
```

`fact_asset_prices` - очищенные факты цен.

`mv_mart_asset_prices_daily` срабатывает на новые inserts в fact table.

`mart_asset_prices_daily_agg` хранит aggregate states:

```text
minState(price)
maxState(price)
avgState(price)
countState()
```

`mart_asset_prices_daily` превращает состояния в обычные аналитические поля:

```text
min_price
max_price
avg_price
records_count
first_fetched_at
last_fetched_at
```

## Repository Structure

```text
.github/workflows/ci.yml              CI/CD pipeline
clickhouse/migrations/                ClickHouse schema migrations
clickhouse/migrate.sh                 ClickHouse migration runner
dags/main_dag.py                      Airflow DAG
dbt/models/                           dbt staging and mart models
dbt/tests/                            dbt custom data tests
scripts/sync_postgres_to_clickhouse.py PostgreSQL -> ClickHouse sync
docker-compose.yml                    Service definitions
Dockerfile.airflow                    Airflow image with project deps
Dockerfile.dbt                        dbt image
ROADMAP.md                            Project roadmap
```

## Deployment Flow

The `demo` branch is used as the deployment branch.

```text
push to demo
  -> GitHub Actions validate
  -> GitHub Actions integration
  -> SSH deploy
  -> git pull --ff-only origin demo
  -> ClickHouse migrations
  -> docker compose up -d --build
```

Deploy runs only for runtime changes:

```text
dags/**
scripts/**
dbt/**
clickhouse/**
docker-compose.yml
Dockerfile*
requirements*.txt
```

Documentation-only changes pass CI but do not trigger deploy.

## Access Through SSH Tunnels

Services are bound to `127.0.0.1` on the server. They are not exposed directly to the internet.

Common tunnel from local machine:

```bash
ssh -N \
  -L 8080:127.0.0.1:8080 \
  -L 8081:127.0.0.1:8081 \
  -L 5433:127.0.0.1:5433 \
  -L 8123:127.0.0.1:8123 \
  -L 9000:127.0.0.1:9000 \
  bogdan@111.88.150.78
```

Available services after tunnel:

| Service | URL / Connection |
|---|---|
| Airflow | `http://127.0.0.1:8080` |
| dbt docs | `http://127.0.0.1:8081` |
| PostgreSQL | `127.0.0.1:5433`, database `crypto_db` |
| ClickHouse HTTP | `http://127.0.0.1:8123` |
| ClickHouse Play UI | `http://127.0.0.1:8123/play` |
| ClickHouse native | `127.0.0.1:9000` |

Credentials used in the pet-project environment:

```text
Airflow:    airflow / airflow
PostgreSQL: user / password
ClickHouse: user / password
```

## Useful Commands

Start services:

```bash
docker compose up -d --build
```

Check containers:

```bash
docker compose ps
```

Run dbt manually:

```bash
docker compose run --rm dbt build
```

Generate and serve dbt docs:

```bash
docker compose run --rm dbt docs generate
docker compose run --rm -p 127.0.0.1:8081:8081 dbt docs serve --host 0.0.0.0 --port 8081
```

Apply ClickHouse migrations:

```bash
docker compose up --build --force-recreate clickhouse-migrate
```

Connect to PostgreSQL:

```bash
psql -h 127.0.0.1 -p 5433 -U user -d crypto_db
```

Connect to ClickHouse with local client:

```bash
clickhouse-client \
  --host 127.0.0.1 \
  --port 9000 \
  --user user \
  --password password \
  --database analytics
```

Open ClickHouse Play UI:

```text
http://127.0.0.1:8123/play
```

## Verification Queries

PostgreSQL raw:

```sql
SELECT
    symbol,
    price,
    fetched_at
FROM public.raw_assets
ORDER BY fetched_at DESC
LIMIT 20;
```

PostgreSQL dbt staging:

```sql
SELECT
    exchange,
    symbol,
    fetched_at,
    price
FROM analytics.stg_asset_prices
ORDER BY fetched_at DESC
LIMIT 20;
```

ClickHouse objects:

```sql
SELECT
    name,
    engine
FROM system.tables
WHERE database = 'analytics'
ORDER BY name;
```

ClickHouse fact table:

```sql
SELECT
    count() AS rows_count,
    max(raw_asset_id) AS last_raw_asset_id
FROM analytics.fact_asset_prices;
```

ClickHouse daily mart:

```sql
SELECT *
FROM analytics.mart_asset_prices_daily
ORDER BY price_date DESC, symbol
LIMIT 20;
```

## Current Limitations

- Ingestion collects live snapshots only.
- There is no historical backfill for periods when Airflow/server was down.
- Credentials are intentionally simple for a pet-project environment.
- Services are protected by localhost bindings and SSH tunnels, not by production-grade secret management.

## Roadmap

The main planned stages are tracked in [ROADMAP.md](./ROADMAP.md). Current project state: ingestion, orchestration, dbt, CI/CD and ClickHouse OLAP layer are implemented.
