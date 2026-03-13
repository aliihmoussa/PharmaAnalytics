# New Developer Guide — PharmaAnalytics

A short onboarding guide to understand the project and start developing. Read in 10–15 minutes.

---

## 1. Project Overview

**PharmaAnalytics** is a **backend API** for pharmaceutical analytics. It:

- **Ingests** drug transaction and inventory (STORE) data from Excel/CSV files.
- **Stores** data in PostgreSQL (transactions, ingestion logs, inventory stock).
- **Exposes** analytics (cost, stay duration, top drugs, demand, charts, demographics).
- **Provides** diagnostics (time-series features, profiling) and **demand/stock-out forecasting** (XGBoost).

There is **no frontend** in this repo; the API is consumed by external clients. There is **no user authentication**; the API is open (CORS is configured for allowed origins).

---

## 2. Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask 3, Flask-CORS |
| **Language** | Python 3.10+ (3.11 in Docker) |
| **Database** | PostgreSQL 15, SQLAlchemy 2, Alembic |
| **Data processing** | Polars, Pandas, OpenPyXL (Excel) |
| **ML / forecasting** | scikit-learn, XGBoost, joblib, holidays |
| **Background tasks** | Celery 5, Redis (broker + result backend) |
| **Config / validation** | pydantic, pydantic-settings, python-dotenv |

**Important:** Redis is used only for Celery (task queue and results). All business data lives in PostgreSQL.

---

## 3. Project Structure

```
PharmaAnalytics/
├── backend/
│   └── app/
│       ├── __init__.py          # create_app(), blueprint registration, CORS
│       ├── config.py             # Pydantic settings (DB, Redis, Celery, CORS, paths)
│       ├── extensions.py        # Celery app instance
│       ├── database/
│       │   ├── models/          # One file per SQLAlchemy model
│       │   │   ├── base.py
│       │   │   ├── drug_transaction.py
│       │   │   ├── data_ingestion_log.py
│       │   │   ├── data_ingestion_error.py
│       │   │   └── inventory_stock.py
│       │   └── session.py       # Engine, get_db_session(), init_db, close_db
│       ├── shared/
│       │   ├── middleware.py    # handle_exceptions, format_success_response, validate_request
│       │   ├── validators.py
│       │   ├── exceptions.py
│       │   └── base_service.py
│       └── modules/
│           ├── ingestion/       # Upload, ingest-path, status, history, cancel
│           ├── inventory/       # STORE file upload → inventory_stock
│           ├── analytics/       # Cost, stay duration, dashboard, charts, demographics
│           ├── diagnostics/    # Features/profiling per drug
│           └── forecasting/    # Demand forecast, algorithms, stock-out forecast
├── migrations/                  # Alembic (env.py + versions/*.py)
├── docker/                      # Dockerfile.backend
├── docker-compose.yml           # postgres, redis, backend, celery_worker
├── run.py                       # Flask entry point
├── celery_worker.py             # Celery worker entry (imports ingestion tasks)
├── alembic.ini
├── requirements.txt
└── requirements-dev.txt
```

- **`backend/app`**: Flask app factory, config, extensions, database, shared utilities, and feature modules.
- **`backend/app/modules/*`**: Each module has `routes.py` (API) and often `services`, `dal`/queries, schemas, processors.
- **`migrations`**: Alembic; **do not** use `flask db` — use `alembic` only.
- **`run.py`**: Creates the app and runs the dev server (host `0.0.0.0`, port 5000).

---

## 4. Core Modules

| Module | Prefix | Purpose |
|--------|--------|--------|
| **Ingestion** | `/api/ingestion` | Upload Excel/CSV → Celery task → `drug_transactions`; ingest from path; status; history; cancel |
| **Inventory** | `/api/inventory` | Upload STORE Excel → sync processing → `inventory_stock` |
| **Analytics** | `/api/analytics` | Cost analysis, hospital stay, top drugs, drug demand, summary stats, chart data, department performance, year comparison, category analysis, patient demographics |
| **Diagnostics** | `/api/diagnostics` | Drug features/profiling (e.g. `/api/diagnostics/features/<drug_code>`) |
| **Forecasting** | `/api/forecasting` | Demand forecast by drug code (XGBoost), algorithms list, stock-out forecast (inventory + demand) |

**Interaction:** Ingestion and inventory fill the DB. Analytics and diagnostics read from `drug_transactions`. Forecasting reads from `drug_transactions` and (for stock-out) from `inventory_stock` and uses XGBoost to predict demand and days until stock-out.

---

## 5. Database Architecture

- **Engine/session:** `backend/app/database/session.py` — single engine, `get_db_session()` (scoped session). Use as context or call `.close()`.

**Main tables:**

| Table | Model | Description |
|-------|--------|-------------|
| `drug_transactions` | `DrugTransaction` | One row per transaction: doc_id, dates, drug_code, drug_name, cr/cs (departments), quantity, prices, room/bed, date_of_birth, source_file, etc. Indexes on date, drug_code, cr, cs, cat, negative quantity. |
| `data_ingestion_log` | `DataIngestionLog` | One row per file ingestion: file_name, file_year, file_hash, total/successful/failed records, ingestion_status (pending, processing, completed, failed, cancelled), error_message, started_at, completed_at. |
| `data_ingestion_errors` | `DataIngestionError` | Failed rows: ingestion_log_id, row_number, raw_data (text), error_type, error_message. |
| `inventory_stock` | `InventoryStock` | STORE movements: same shape as transactions (doc_id, transaction_date, drug_code, quantity, unit_price, total_price, voucher, etc.). Current stock = sum(quantity) per drug. Indexes on drug_code, transaction_date. |

**Relationships:** `DataIngestionError.ingestion_log_id` → `DataIngestionLog.id`. No FK from `DrugTransaction` or `InventoryStock` to ingestion log; linkage is by `source_file` / ingestion run in application logic.

**Important:** All primary keys are UUIDs. Numeric fields use `Numeric(12,2)` or `(14,2)` for prices. Dates use `Date`/`DateTime`; `ingestion_date`/`created_at` have `server_default=now()`.

---

## 6. Main Application Flows

### Ingestion (transaction data)

1. **POST /api/ingestion/upload** (or **POST /api/ingestion/ingest-path**): Request includes file (or path). Service validates file, creates a `DataIngestionLog` (status `pending`), enqueues Celery task `ingestion.process_file` with `ingestion_log_id`, file path, file name.
2. **Celery worker** runs `process_ingestion_task`: loads file via `IngestionProcessor`, transforms/normalizes (transformation module), cleans, prepares for DB, bulk inserts into `drug_transactions`, updates `DataIngestionLog` (successful/failed counts, status `completed`/`failed`), writes failures to `DataIngestionError`, deletes temp file.
3. **GET /api/ingestion/status/<id>**: Returns log status and progress from DB (and optionally Celery task state).
4. **GET /api/ingestion/history**: Lists ingestion logs (optional status filter, limit, offset).
5. **DELETE /api/ingestion/<id>/cancel**: Sets log status to `cancelled` if still pending/processing.

### Inventory (STORE)

1. **POST /api/inventory/upload**: Receives Excel file. Saves to temp dir, calls `process_store_file(path, file_name)`.
2. **process_store_file**: Loads sheet `rep25071808450909` (or configured), maps columns via `INVENTORY_FIELD_MAPPINGS`, normalizes (dates, types), inserts rows into `inventory_stock` in one transaction. Returns successful/failed counts. Temp file is deleted after.

### Forecasting

1. **GET /api/forecasting/<drug_code>**: Query params (algorithm, forecast_days, test_size, lookback_days, start_date, end_date, department). Factory returns algorithm (e.g. XGBoost); algorithm loads transaction data, trains, predicts; returns frontend-ready structure (historical, forecast, test_predictions, metrics, feature_importance).
2. **GET /api/forecasting/stock-out-forecast**: Optional `drug_code` and `limit`. For one drug: current stock from `inventory_stock` (sum of quantity), forecasted daily demand via internal ForecastService (XGBoost), then days until stock-out and at_risk flag. Without drug_code: top N drugs at risk (lowest days until stock-out).

### Analytics

- All **GET** endpoints. They use request validators (Pydantic) and services/DALs that query `drug_transactions` (and sometimes other tables). Examples: cost analysis, hospital stay duration, top drugs, drug demand, summary stats, chart data, department performance, year comparison, category analysis, patient demographics.

### Diagnostics

- **GET /api/diagnostics/features/<drug_code>**: Optional department, start_date, end_date, use_cache. FeatureService builds features/profiling for the drug and returns them (with optional Redis caching).

---

## 7. Important Business Logic

- **Sessions:** Use `get_db_session()` and always `.close()` (or use a context manager). DALs use `with DAL() as dal:` and call `get_db_session()` inside `__enter__`.
- **Ingestion:** Duplicate check by filename and status; if same filename already completed, upload is rejected. Temp files are under `data/uploads/temp`; path ingestion is restricted to `ALLOWED_INGESTION_PATHS`.
- **Inventory:** Sheet name is `rep25071808450909`; column mapping is in `backend/app/modules/inventory/schema.py`. Stock level = sum of `quantity` for the drug up to a given date.
- **Stock-out:** `at_risk` when forecasted days until stock-out &lt; 7. Demand is from XGBoost forecast; current stock from `inventory_stock`.
- **Errors:** Route-level errors are caught by `@handle_exceptions`; validation by `@validate_request(RequestModel)`. AppException and validation errors return structured JSON with `error.code`, `error.message`, `meta.request_id`.
- **CORS:** Configured in `create_app()` from `config.CORS_ORIGINS` (comma-separated). Credentials and common methods/headers allowed.

---

## 8. How to Run the Project Locally

### With Docker (recommended)

```bash
# From project root
docker compose up -d --build
docker compose exec backend alembic upgrade head
curl http://localhost:5000/
```

- PostgreSQL: internal 5432, host **5433** by default.  
- Redis: 6379.  
- Backend: **http://localhost:5000**.  
- Celery worker runs in a separate container.

### Without Docker

**Prerequisites:** Python 3.10+, PostgreSQL 15, Redis.

```bash
cd /path/to/PharmaAnalytics
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` in project root (see README). For local DB/Redis use `DB_HOST=localhost`, `REDIS_HOST=localhost` (or leave defaults).

```bash
# Migrations (from project root, venv active)
alembic upgrade head

# Run API
python run.py
# API at http://localhost:5000

# Optional: Celery worker (separate terminal, Redis running)
celery -A celery_worker worker --loglevel=info
```

### Environment variables (summary)

- `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST`, `DB_PORT` (or `DATABASE_URL`).  
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` (or `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`).  
- `SECRET_KEY`, `CORS_ORIGINS`, `ALLOWED_INGESTION_PATHS`, `FLASK_ENV`, `DEBUG`.

---

## 9. Common Development Tasks

### Add a new API endpoint

1. Add a route in the right module’s `routes.py` (e.g. `backend/app/modules/analytics/routes.py`).
2. Use `@handle_exceptions` and, for validated query/body, `@validate_request(YourRequestModel)` and `g.validated_data`.
3. Call a service or DAL; return `format_success_response(data)` or `jsonify(...), status_code`.

### Add a new database migration

1. Change or add models under `backend/app/database/models/`.
2. From project root: `alembic revision --autogenerate -m "short description"`.
3. Edit the new file in `migrations/versions/` if needed (e.g. renames, data).
4. Apply: `alembic upgrade head`. With Docker: `docker compose exec backend alembic upgrade head`.

### Create a new model

1. Add a new file in `backend/app/database/models/` (e.g. `my_model.py`), subclass `Base`, set `__tablename__` and columns.
2. Import and re-export in `backend/app/database/models/__init__.py`.
3. In `migrations/env.py`, import the new model so `target_metadata` includes it.
4. Generate and run a migration as above.

### Run tests

- Dev deps: `pip install -r requirements-dev.txt`.  
- Test framework: pytest, pytest-cov, pytest-flask.  
- There are no test files in the repo at the moment; when added, run with `pytest` (and optionally `pytest --cov=backend`).

---

## 10. Current Work / Known Areas of Development

- **Inventory & stock-out:** New `inventory_stock` model and STORE ingestion; stock-out forecast combining inventory and demand. Migrations `a1b2c3d4e5f6` (add table) and `b2c3d4e5f6a7` (numeric precision) are present.
- **Models split:** `backend/app/database/models/` is now a package (one file per model); old single `models.py` removed.
- **Unfinished / to improve:**  
  - No automated tests in repo yet.  
  - Ingestion cancel does not revoke the Celery task (task_id not stored).  
  - Some ingestion service code paths have indentation/scope issues (e.g. `create_ingestion_log` call) that can cause bugs and should be cleaned up.  
  - Pagination total in ingestion history is approximated (len of list), not a real count query.

---

## 11. Useful Tips for New Developers

- **Always use Alembic** for schema changes; do not use `flask db` or `Base.metadata.create_all()` in production.
- **Session discipline:** Prefer `with DAL() as dal:` or explicit `session = get_db_session(); try: ... finally: session.close()` so connections are not leaked.
- **Config:** All config is in `backend/app/config.py` (Pydantic BaseSettings); it reads from env and `.env`. Use `config.XXX`, not raw `os.getenv` in app code.
- **New module:** Add a folder under `backend/app/modules/`, implement `routes.py` and register the blueprint in `backend/app/__init__.py` with a `url_prefix` (e.g. `/api/yourmodule`).
- **Celery:** Only ingestion defines a task (`ingestion.process_file`). To add tasks, define them in a module and import that module in `celery_worker.py` so they are registered.
- **STORE file:** Column names and sheet name are in `backend/app/modules/inventory/schema.py`; if the client uses a different Excel layout, update the mapping there and the processor.
- **Logs:** Standard logging is configured in `create_app()`. Use `logger = logging.getLogger(__name__)` in modules for traceability.
