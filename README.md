# End-to-End Data Pipeline

Проект по созданию полнофункционального пайплайна данных: от извлечения сырых данных до аналитического хранилища.

## Обзор
Цель проекта — освоить современные инструменты инженерии данных (Data Engineering) и построить надежную систему обработки данных с использованием Python, SQL и контейнеризации.

## Дорожная карта (Roadmap)
Подробный план реализации разбит на 5 этапов. Вы можете отслеживать прогресс в файле:
[ROADMAP.md](./ROADMAP.md)

### Статус проекта
- [x] Этап 1: Ingestion (Python + CCXT + Postgres + Docker) — **Готово**
- [ ] Этап 2: Orchestration (Airflow) — **В процессе**

## Текущий стек
- **Data Ingestion:** CCXT
- **Database:** PostgreSQL 15
- **Orchestration:** Apache Airflow
- **Transformation:** dbt
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

## Текущий пайплайн

DAG `crypto_ingestion_dag` запускается каждые 15 минут и сохраняет цены `BTC/USDT` и `ETH/USDT` с Binance в таблицу `raw_assets`.

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

dbt-проект находится в папке `dbt/`. Пока dbt запускается вручную, без Airflow.

Установка dbt:

```bash
python3 -m pip install -r requirements-dbt.txt
```

Проверка подключения:

```bash
cd dbt
dbt debug --profiles-dir .
```

Сборка моделей:

```bash
dbt run --profiles-dir .
```

Запуск тестов:

```bash
dbt test --profiles-dir .
```

Текущие dbt-модели:

- `stg_asset_prices` - staging view поверх `public.raw_assets`
- `mart_asset_prices_daily` - дневная аналитическая таблица по `exchange` и `symbol`
