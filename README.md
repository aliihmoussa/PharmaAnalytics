# PharmaAnalytics

Backend API for pharmaceutical analytics: data ingestion, inventory, analytics, diagnostics, and demand/stock-out forecasting.

## Tech stack

- **API:** Flask 3, Flask-CORS  
- **Database:** PostgreSQL 15, SQLAlchemy 2, Alembic  
- **Data:** Polars, Pandas, OpenPyXL (Excel)  
- **ML:** scikit-learn, XGBoost (forecasting)  
- **Tasks:** Celery, Redis (broker & result backend)

## Quick start (Docker)

From the project root:

```bash
# 1. From project root
cd /path/to/PharmaAnalytics

# 2. Start everything (build first if needed)
docker compose up -d --build

# 3. Run migrations (Alembic, not flask db)
docker compose exec backend alembic upgrade head

# 4. Check API
curl http://localhost:5000/
```

You should see: `{"message": "Pharma Analytics API", "version": "1.0.0"}`.

---

## Run with Docker (recommended)

You only need **Docker** and **Docker Compose** installed. No need to install Python, PostgreSQL, or Redis on your machine.

### 1. Start everything

From the project root:

```bash
docker compose up -d
```

If you don’t have the images yet, build and start in one go:

```bash
docker compose up -d --build
```

This starts:

- **PostgreSQL** (database) — internal port 5432, host port **5433** by default  
- **Redis** — for Celery (broker & result backend)  
- **Flask backend** — API on **http://localhost:5000**  
- **Celery worker** — for background tasks  

### 2. Apply database migrations

After the first start, run migrations once (the project uses Alembic):

```bash
docker compose exec backend alembic upgrade head
```

### 3. Check it’s running

Open **http://localhost:5000** in your browser or:

```bash
curl http://localhost:5000
```

You should see: `{"message": "Pharma Analytics API", "version": "1.0.0"}`.

### Optional: environment variables

Create a `.env` file in the project root to override defaults (e.g. ports or passwords):

```env
DB_USER=pharma_user
DB_PASSWORD=pharma_password
DB_NAME=pharma_analytics_db
DB_PORT=5433
REDIS_PORT=6379
BACKEND_PORT=5000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
SECRET_KEY=your-secret-key
```

### Useful Docker commands

| Command | Description |
|--------|-------------|
| `docker compose up -d` | Start all services in the background |
| `docker compose down` | Stop and remove containers |
| `docker compose logs -f backend` | Follow backend logs |
| `docker compose exec backend alembic upgrade head` | Run migrations |

---

## Run without Docker (local)

If you prefer to run the app directly on your machine.

**Prerequisites:** Python 3.10+, PostgreSQL 15, Redis

### 1. Setup

```bash
cd /path/to/PharmaAnalytics
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment

Create a `.env` in the project root (see [Optional: environment variables](#optional-environment-variables) above). For local run, set:

- `DB_HOST=localhost`, `REDIS_HOST=localhost`
- Or leave defaults if PostgreSQL and Redis run on localhost.

### 3. Migrations (Alembic, no Docker)

From the project root, with the virtualenv activated and PostgreSQL running:

```bash
# Apply all pending migrations
alembic upgrade head
```

To create a new migration after changing models:

```bash
# Generate a new revision (edit migrations/versions/... if needed)
alembic revision -m "description of change"
# Then apply it
alembic upgrade head
```

### 4. Run the app

```bash
python run.py
```

API will be at **http://localhost:5000**.

### 5. Celery (optional)

In another terminal, with Redis running:

```bash
source venv/bin/activate
celery -A celery_worker worker --loglevel=info
```

## API overview

| Module       | Prefix                  | Purpose |
|-------------|-------------------------|--------|
| Ingestion   | `/api/ingestion`        | Upload Excel/data, ingest from path, status, history |
| Inventory   | `/api/inventory`        | Inventory upload and management |
| Analytics   | `/api/analytics`        | Cost analysis, stay duration, top drugs, demand, charts, department performance, demographics |
| Diagnostics | `/api/diagnostics`      | Health and diagnostics endpoints |
| Forecasting | `/api/forecasting`      | Drug demand forecast by code, algorithms list, stock-out forecast |

## Project structure

```
PharmaAnalytics/
├── backend/
│   └── app/
│       ├── config.py           # Pydantic settings, DB, CORS, Celery
│       ├── extensions.py       # Celery app
│       ├── database/
│       │   ├── models/         # One file per model
│       │   │   ├── base.py
│       │   │   ├── drug_transaction.py
│       │   │   ├── data_ingestion_log.py
│       │   │   ├── data_ingestion_error.py
│       │   │   └── inventory_stock.py
│       │   └── session.py      # Engine, session factory
│       └── modules/
│           ├── ingestion/
│           ├── inventory/
│           ├── analytics/
│           ├── diagnostics/
│           └── forecasting/
├── migrations/                # Alembic
├── docker/                    # Dockerfiles
├── docker-compose.yml
├── run.py                     # App entry point
├── celery_worker.py
├── requirements.txt
└── requirements-dev.txt
```

## Development

- **Migrations:** `alembic revision -m "message"` then `alembic upgrade head`
- **Dev deps:** `pip install -r requirements-dev.txt`

## License

See repository or project terms.
