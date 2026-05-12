# Road Map: End-to-End Data Pipeline

Этот документ описывает пошаговый план развития проекта: от сбора "сырых" данных до построения профессионального аналитического хранилища с контролем качества и CI/CD.

---

## Этап 1: Инфраструктура и Ingestion (Сбор данных)
**Статус: Завершено**
**Цель:** Научиться стабильно доставать данные и упаковывать код в контейнеры.

### Что изучено:
- [x] **Библиотеки:** `ccxt` (криптовалюты).
- [x] **Контейнеризация:** `Docker` и `docker-compose`.
- [x] **БД:** Основы PostgreSQL.

### Задача:
Написать Python-скрипт, который забирает данные (например, курсы BTC/USD и ETH/USD) и сохраняет их в PostgreSQL. Код должен быть полностью контейнеризирован.

### Результат:
- [x] В базе PostgreSQL копятся «сырые» данные в таблице `raw_assets`.
- [x] Проект запускается через `docker compose`.

---

## Этап 2: Оркестрация (Управление запуском)
**Статус: Завершено**
**Цель:** Уйти от ручного запуска и перейти к автоматическому расписанию.

### Что изучить:
- [x] **Airflow Concepts:** Архитектура (Scheduler, Worker, Webserver).
- [x] **DAGs:** Определение графов зависимостей.
- [x] **Operators vs TaskFlow API:** Базовое использование PythonOperator и BashOperator.
- [x] **Scheduling:** Cron-выражения и интервалы запуска.

### Задача:
Развернуть Airflow в Docker. Переписать запуск скрипта из Этапа 1 в виде задачи (Task) внутри Airflow DAG. Настроить запуск каждые 15 минут.

### Результат:
- [x] Автоматизированный пайплайн с логированием и retry.
- [x] UI Airflow отображает запуски DAG `crypto_ingestion_dag`.
- [x] DAG запускает `dbt build` после ingestion.
- [x] Старый standalone ingestion перенесен в `legacy/`.

---

## Этап 3: Трансформация и моделирование (dbt)
**Статус: Завершено**
**Цель:** Научиться превращать «мусор» в чистые аналитические витрины.

### Что изучить:
- [x] **dbt (Data Build Tool):** Основы, Docker-запуск, подключение к PostgreSQL.
- [x] **Методология:** Базовый слой Staging -> Marts.
- [x] **SQL:** Первые модульные SQL-модели.
- [x] **Документация:** Генерация документации через dbt.
- [x] **Incremental models:** Обновление дневной витрины без полного пересчета всей истории.

### Задача:
Подключить dbt к PostgreSQL. Написать модели, которые:
1. Очищают данные из `raw_assets` (приведение типов, фильтрация невалидных цен).
2. Создают витрину `mart_asset_prices_daily` со средними, минимальными и максимальными ценами за день.

### Результат:
- [x] dbt запускается вручную через Docker Compose.
- [x] dbt запускается автоматически из Airflow через task `dbt_build`.
- [x] Создана staging-модель `stg_asset_prices`.
- [x] Создана mart-модель `mart_asset_prices_daily`.
- [x] Добавлены базовые тесты источника и модели.
- [x] Сгенерирована и просмотрена dbt-документация.
- [x] Добавлена дедупликация staging-слоя.
- [x] `mart_asset_prices_daily` переведена на incremental materialization.
- [x] Зафиксированы ограничения текущего ingestion: live snapshots без backfill.

---

## Этап 4: Хранилище и Скорость (OLAP)
**Статус: Следующий этап**
**Цель:** Понять разницу между транзакционными (OLTP) и аналитическими (OLAP) БД.

### Что изучить:
- [ ] **ClickHouse:** Архитектура, колоночное хранение.
- [ ] **MergeTree:** Основной движок таблиц в ClickHouse.
- [ ] **Data Transfer:** Как переливать очищенные факты из Postgres в ClickHouse.
- [ ] **Views vs Materialized Views:** Сначала обычные view, затем materialized view для ускорения чтения.

### Задача:
Добавить в `docker-compose` контейнер с ClickHouse. Настроить перенос `analytics.stg_asset_prices` из PostgreSQL в ClickHouse как fact-таблицу. Дневную аналитику считать уже в ClickHouse.

### Результат:
- [ ] ClickHouse запущен в Docker Compose.
- [ ] Создана ClickHouse-таблица `fact_asset_prices` на движке MergeTree.
- [ ] Настроен перенос очищенных фактов из PostgreSQL `analytics.stg_asset_prices`.
- [ ] Создан обычный ClickHouse view `mart_asset_prices_daily`.
- [ ] Результаты ClickHouse mart сверены с PostgreSQL/dbt mart.
- [ ] Позже обычный view заменен на materialized view.

---

## Этап 5: Data Quality и CI/CD
**Статус: Базовая автоматизация завершена, расширение качества данных — позже**
**Цель:** Обеспечение надежности данных и автоматизация проверок.

### Что изучить:
- [x] **GitHub Actions:** Автоматизация базовых проверок и деплоя.
- [x] **Integration checks:** Проверка связки PostgreSQL + dbt на fixture-данных.
- [ ] **Great Expectations:** Написание тестов для данных (Expectations), если dbt-тестов станет недостаточно.
- [ ] **Data Contracts:** Базовое понимание контрактов данных.

### Задача:
1. Поддерживать GitHub Actions workflow, который проверяет Docker Compose, Airflow DAG import, dbt parse и dbt integration build.
2. Автоматически деплоить ветку `demo` на сервер только после успешных проверок и только при runtime-изменениях.
3. Позже расширить data quality слой, если появятся более строгие требования к данным.

### Результат:
- [x] CI запускается при push и pull request.
- [x] Добавлен integration job с PostgreSQL fixture data и `dbt build`.
- [x] Добавлен автоматический deploy job для ветки `demo`.
- [x] Deploy пропускается для documentation-only изменений.
- [ ] Добавить branch protection, когда появится стабильная работа через PR/main.
