# End-to-End Data Pipeline

Проект по созданию полнофункционального пайплайна данных: от извлечения сырых данных до аналитического хранилища.

## Обзор
Цель проекта — освоить современные инструменты инженерии данных (Data Engineering) и построить надежную систему обработки данных с использованием Python, SQL и контейнеризации.

## Дорожная карта (Roadmap)
Подробный план реализации разбит на 5 этапов. Вы можете отслеживать прогресс в файле:
[ROADMAP.md](./ROADMAP.md)

### Статус проекта
- [x] Этап 1: Ingestion (Python + CCXT + Postgres + Docker) — **Готово**
- [x] Этап 2: Orchestration (Airflow) — **Готово**
- [x] Этап 3: Transformation (dbt) — **В процессе**

## Текущий стек
- **Data Ingestion:** CCXT
- **Database:** PostgreSQL 15
- **Orchestration:** Apache Airflow
- **Transformation:** dbt
- **CI/CD:** GitHub Actions
- **Containerization:** Docker, Docker Compose

## Локальный запуск на сервере

```bash
docker compose up -d --build
```

Airflow Web UI опубликован только на localhost сервера:

```yaml
127.0.0.1:8080:8080
```

Для доступа с локальной машины используется SSH-туннель:

```bash
ssh -L 8080:localhost:8080 bogdan@111.88.150.78
```

После этого Airflow доступен в браузере:

```text
http://localhost:8080
```

Логин и пароль администратора Airflow:

```text
airflow / airflow
```

## Deployment

Ветка `demo` используется как deploy-ветка. После `push` в `demo` GitHub Actions запускает CI и, если проверки прошли успешно, автоматически обновляет сервер только при runtime-изменениях:

```text
push origin demo -> CI -> runtime changes check -> SSH deploy -> git pull --ff-only origin demo -> docker compose up -d --build
```

Runtime-изменениями считаются изменения в:

```text
dags/**
dbt/**
docker-compose.yml
Dockerfile*
requirements*.txt
```

Изменения только в документации, например `README.md` или `ROADMAP.md`, проходят CI, но не запускают deploy.

Для автоматического деплоя в GitHub repository secrets должны быть настроены:

```text
SERVER_HOST=111.88.150.78
SERVER_USER=bogdan
SERVER_SSH_KEY=<private SSH key for deploy>
```

Если CI падает, deploy job не запускается.

CI workflow включает:

- `validate` - проверка Docker Compose config, синтаксиса DAG, сборки Airflow/dbt images и dbt parse.
- `integration` - поднимает PostgreSQL, загружает fixture-данные в `raw_assets`, запускает `dbt build` и проверяет результат mart.
- `deploy` - обновляет сервер по SSH только после успешных `validate` и `integration`, только для `demo`, только при runtime-изменениях.

## Текущий пайплайн

DAG `crypto_ingestion_dag` запускается каждые 15 минут:

1. `fetch_crypto_prices` сохраняет цены криптовалютных пар с Binance в `public.raw_assets`.
2. `dbt_build` запускает `dbt build`, обновляет модели в схеме `analytics` и выполняет dbt-тесты.

Сейчас собираются пары:

```text
BTC/USDT
ETH/USDT
BNB/USDT
SOL/USDT
XRP/USDT
ADA/USDT
DOGE/USDT
TON/USDT
DOT/USDT
LINK/USDT
```

Старый standalone ingestion из Этапа 1 перенесен в `legacy/`. Актуальная точка запуска проекта - Airflow через `docker compose`.

Текущая raw-схема:

```sql
CREATE TABLE IF NOT EXISTS raw_assets (
    id SERIAL PRIMARY KEY,
    exchange TEXT NOT NULL,
    symbol TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    price NUMERIC NOT NULL,
    raw_payload JSONB NOT NULL
);
```

Подключение к Postgres с сервера:

```bash
docker compose exec db psql -U user -d crypto_db
```

## Ручной запуск dbt

dbt-проект находится в папке `dbt/`. Основной запуск выполняется из Airflow, но для разработки и проверки доступен отдельный dbt-контейнер.

Проверка подключения:

```bash
docker compose run --rm dbt debug
```

Сборка моделей и запуск тестов:

```bash
docker compose run --rm dbt build
```

Генерация dbt docs:

```bash
docker compose run --rm dbt docs generate
docker compose run --rm -p 127.0.0.1:8081:8081 dbt docs serve --host 0.0.0.0 --port 8081
```

Для просмотра docs с локальной машины используется SSH-туннель:

```bash
ssh -N -L 8081:127.0.0.1:8081 bogdan@111.88.150.78
```

После этого документация доступна по адресу:

```text
http://127.0.0.1:8081
```

Текущие dbt-модели:

- `stg_asset_prices` - staging view поверх `public.raw_assets` с дедупликацией по `exchange`, `symbol` и минуте `fetched_at`
- `mart_asset_prices_daily` - incremental дневная аналитическая таблица по `exchange`, `symbol` и `price_date`

## Ограничения ingestion

Текущий ingestion собирает live snapshots через Binance ticker API. Pipeline не выполняет backfill: если сервер, Airflow или DAG были выключены, пропущенные интервалы не восстанавливаются.

Дневная витрина агрегирует только фактически собранные наблюдения. Поэтому строгие проверки полноты временного ряда пока не используются.
