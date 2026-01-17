# Naming Conventions Guide - Best Practices

**Date**: 2026-01-XX  
**Purpose**: Comprehensive guide to naming conventions used in this project  
**Based on**: PEP 8, Flask conventions, and industry best practices

---

## 📋 Table of Contents

1. [Folders/Directories](#foldersdirectories)
2. [Python Files](#python-files)
3. [Python Code](#python-code)
4. [API Endpoints](#api-endpoints)
5. [Database](#database)
6. [Configuration Files](#configuration-files)
7. [Docker/Infrastructure](#dockerinfrastructure)
8. [Summary Checklist](#summary-checklist)

---

## 📁 Folders/Directories

### ✅ Best Practices

1. **Use lowercase with underscores** (snake_case)
   ```
   ✅ Good: backend/app/modules/ingestion/
   ✅ Good: backend/app/modules/analytics/
   ❌ Bad:  backend/app/modules/Ingestion/
   ❌ Bad:  backend/app/modules/Analytics/
   ```

2. **Use plural for collections, singular for modules**
   ```
   ✅ Good: modules/analytics/        (module name)
   ✅ Good: modules/ingestion/        (module name)
   ✅ Good: data/uploads/             (collection of uploads)
   ✅ Good: scripts/                 (collection of scripts)
   ❌ Bad:  module/                  (should be modules/)
   ```

3. **Keep names short but descriptive**
   ```
   ✅ Good: analytics/
   ✅ Good: ingestion/
   ✅ Good: diagnostics/
   ❌ Bad:  analytics_and_reporting_module/
   ❌ Bad:  data_ingestion_processing/
   ```

4. **Use standard folder names**
   ```
   ✅ Good: tests/        (not test/)
   ✅ Good: docs/         (not documentation/)
   ✅ Good: migrations/   (Alembic standard)
   ✅ Good: scripts/      (not script/)
   ```

### 📊 Your Project Examples

| Folder | Status | Notes |
|--------|--------|-------|
| `backend/` | ✅ Excellent | Standard, clear |
| `app/` | ✅ Excellent | Flask convention |
| `modules/` | ✅ Excellent | Clear purpose |
| `analytics/` | ✅ Excellent | Descriptive |
| `ingestion/` | ✅ Excellent | Clear purpose |
| `diagnostics/` | ✅ Excellent | Descriptive |
| `forecasting/` | ✅ Excellent | Clear purpose |
| `shared/` | ✅ Excellent | Common utilities |
| `database/` | ✅ Excellent | Clear purpose |
| `tests/` | ✅ Excellent | Standard |

---

## 📄 Python Files

### ✅ Best Practices

1. **Use lowercase with underscores** (snake_case)
   ```
   ✅ Good: ingestion_service.py
   ✅ Good: data_upload_dal.py
   ✅ Good: xgboost_algorithm.py
   ❌ Bad:  IngestionService.py
   ❌ Bad:  DataUploadDAL.py
   ❌ Bad:  XGBoostAlgorithm.py
   ```

2. **Match file name to main class/function**
   ```
   ✅ Good: services.py → class IngestionService
   ✅ Good: dal.py → class DataUploadDAL
   ✅ Good: routes.py → @analytics_bp.route()
   ```

3. **Use descriptive names**
   ```
   ✅ Good: forecast_service.py
   ✅ Good: cost_analysis_service.py
   ✅ Good: data_preparation.py
   ❌ Bad:  service.py
   ❌ Bad:  utils.py
   ❌ Bad:  helper.py
   ```

4. **Special file names**
   ```
   ✅ Good: __init__.py      (package marker)
   ✅ Good: config.py        (configuration)
   ✅ Good: extensions.py    (Flask extensions)
   ✅ Good: models.py        (database models)
   ✅ Good: routes.py        (API routes)
   ✅ Good: services.py      (service layer)
   ✅ Good: dal.py           (data access layer)
   ```

### 📊 Your Project Examples

| File | Status | Notes |
|------|--------|-------|
| `services.py` | ✅ Good | Matches class name pattern |
| `routes.py` | ✅ Good | Standard Flask name |
| `dal.py` | ✅ Good | Clear abbreviation |
| `models.py` | ✅ Good | Standard SQLAlchemy name |
| `config.py` | ✅ Good | Standard config name |
| `xgboost_algorithm.py` | ✅ Good | Descriptive, specific |
| `data_preparation.py` | ✅ Good | Clear purpose |

---

## 🐍 Python Code

### Classes

**Convention**: `PascalCase` (CapitalizedWords)

```python
✅ Good:
class IngestionService(BaseService):
    pass

class DataUploadDAL:
    pass

class DrugTransaction(Base):
    pass

class XGBoostForecaster:
    pass

❌ Bad:
class ingestion_service:      # Should be PascalCase
class dataUploadDAL:           # Should be PascalCase
class drug_transaction:        # Should be PascalCase
```

### Functions and Methods

**Convention**: `snake_case` (lowercase_with_underscores)

```python
✅ Good:
def upload_file(self, file, file_name: str):
    pass

def get_ingestion_status(self, ingestion_log_id):
    pass

def calculate_file_hash(file_path: Path):
    pass

def sanitize_string(value: str):
    pass

❌ Bad:
def uploadFile(self):          # Should be snake_case
def getIngestionStatus(self):  # Should be snake_case
def CalculateFileHash():       # Should be snake_case
```

### Private Methods

**Convention**: `_snake_case` (leading underscore)

```python
✅ Good:
def _process_csv_file(self, file_path: Path):
    pass

def _batch_insert(self, df: pl.DataFrame):
    pass

def _ensure_session(self):
    pass

❌ Bad:
def process_csv_file(self):    # Should indicate private
def batchInsert(self):         # Wrong case + not private
```

### Variables

**Convention**: `snake_case` (lowercase_with_underscores)

```python
✅ Good:
file_name = "data.csv"
ingestion_log_id = uuid.uuid4()
max_file_size = 500 * 1024 * 1024
upload_dir = Path('data/uploads/temp')

❌ Bad:
fileName = "data.csv"          # Should be snake_case
ingestionLogId = uuid.uuid4()   # Should be snake_case
maxFileSize = 500 * 1024 * 1024 # Should be snake_case
```

### Constants

**Convention**: `UPPER_SNAKE_CASE` (ALL_CAPS_WITH_UNDERSCORES)

```python
✅ Good:
MAX_FILE_SIZE = 500 * 1024 * 1024
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx'}
UPLOAD_DIR = Path('data/uploads/temp')

❌ Bad:
max_file_size = 500 * 1024 * 1024  # Should be UPPER_CASE
AllowedExtensions = {'csv', 'txt'}  # Should be UPPER_CASE
```

### Type Hints

**Convention**: Use type hints for clarity

```python
✅ Good:
def upload_file(self, file, file_name: str) -> dict:
    pass

def get_ingestion_status(
    self, 
    ingestion_log_id: Union[uuid.UUID, str]
) -> dict:
    pass

def validate_file(
    self, 
    file, 
    file_name: str
) -> tuple[Path, int]:
    pass
```

### 📊 Your Project Examples

| Code Element | Example | Status |
|-------------|---------|--------|
| Class | `IngestionService` | ✅ Perfect |
| Class | `DataUploadDAL` | ✅ Perfect |
| Method | `upload_file()` | ✅ Perfect |
| Method | `get_ingestion_status()` | ✅ Perfect |
| Private Method | `_process_csv_file()` | ✅ Perfect |
| Variable | `file_name` | ✅ Perfect |
| Constant | `MAX_FILE_SIZE` | ✅ Perfect |

---

## 🌐 API Endpoints

### ✅ Best Practices

1. **Use lowercase with hyphens** (kebab-case) for URLs
   ```
   ✅ Good: /api/analytics/cost-analysis
   ✅ Good: /api/ingestion/upload
   ✅ Good: /api/forecasting/predict
   ✅ Good: /api/diagnostics/features/{drug_code}
   ❌ Bad:  /api/analytics/costAnalysis
   ❌ Bad:  /api/analytics/cost_analysis
   ❌ Bad:  /api/Analytics/CostAnalysis
   ```

2. **Use RESTful conventions**
   ```
   ✅ Good: GET    /api/analytics/top-drugs
   ✅ Good: POST   /api/ingestion/upload
   ✅ Good: GET    /api/forecasting/predict
   ✅ Good: GET    /api/diagnostics/features/{drug_code}
   ❌ Bad:  GET    /api/getTopDrugs
   ❌ Bad:  POST   /api/uploadFile
   ```

3. **Use resource-based naming**
   ```
   ✅ Good: /api/analytics/top-drugs
   ✅ Good: /api/analytics/drug-demand
   ✅ Good: /api/forecasting/predict
   ✅ Good: /api/diagnostics/features/{drug_code}
   ❌ Bad:  /api/getTopDrugs
   ❌ Bad:  /api/calculateDrugDemand
   ```

4. **Use plural for collections**
   ```
   ✅ Good: /api/analytics/top-drugs
   ✅ Good: /api/analytics/departments
   ❌ Bad:  /api/analytics/top-drug
   ❌ Bad:  /api/analytics/department
   ```

### 📊 Your Project Examples

| Endpoint | Status | Notes |
|---------|--------|-------|
| `/api/analytics/cost-analysis` | ✅ Good | Kebab-case, descriptive |
| `/api/analytics/top-drugs` | ✅ Good | Plural, clear |
| `/api/ingestion/upload` | ✅ Good | Verb for action |
| `/api/forecasting/predict` | ✅ Good | Clear action |
| `/api/diagnostics/features/{drug_code}` | ✅ Good | Resource-based |

---

## 🗄️ Database

### Tables

**Convention**: `snake_case` plural nouns

```sql
✅ Good:
CREATE TABLE drug_transactions (...)
CREATE TABLE ingestion_logs (...)
CREATE TABLE drug_categories (...)

❌ Bad:
CREATE TABLE DrugTransactions (...)  -- Should be lowercase
CREATE TABLE drug_transaction (...)   -- Should be plural
CREATE TABLE drugTransaction (...)   -- Should be snake_case
```

### Columns

**Convention**: `snake_case` singular nouns

```sql
✅ Good:
transaction_date
drug_code
unit_price
total_price
date_of_birth
ingestion_date

❌ Bad:
transactionDate      -- Should be snake_case
TransactionDate      -- Should be lowercase
transaction-date     -- Should use underscores
```

### Indexes

**Convention**: `idx_` prefix + descriptive name

```sql
✅ Good:
CREATE INDEX idx_transactions_date_dept ON drug_transactions(transaction_date, cr);
CREATE INDEX idx_transactions_drug_date ON drug_transactions(drug_code, transaction_date);

❌ Bad:
CREATE INDEX transactions_date_dept ON ...  -- Missing prefix
CREATE INDEX idx_transactionsDateDept ON ... -- Wrong case
```

### Constraints

**Convention**: `chk_` for check, `fk_` for foreign key, `pk_` for primary key

```sql
✅ Good:
CONSTRAINT chk_quantity_not_zero CHECK (quantity != 0)
CONSTRAINT pk_drug_transactions PRIMARY KEY (id)
CONSTRAINT fk_transaction_category FOREIGN KEY (cat) REFERENCES ...

❌ Bad:
CONSTRAINT quantity_not_zero CHECK ...  -- Missing prefix
```

### 📊 Your Project Examples

| Database Element | Example | Status |
|-----------------|---------|--------|
| Table | `drug_transactions` | ✅ Perfect |
| Table | `ingestion_logs` | ✅ Perfect |
| Column | `transaction_date` | ✅ Perfect |
| Column | `drug_code` | ✅ Perfect |
| Index | `idx_transactions_date_dept` | ✅ Perfect |
| Constraint | `chk_quantity_not_zero` | ✅ Perfect |

---

## ⚙️ Configuration Files

### ✅ Best Practices

1. **Use lowercase with underscores or hyphens**
   ```
   ✅ Good: docker-compose.yml
   ✅ Good: alembic.ini
   ✅ Good: requirements.txt
   ✅ Good: .env.example
   ❌ Bad:  Docker-Compose.yml
   ❌ Bad:  requirements-dev.txt (use requirements-dev.txt is OK)
   ```

2. **Use standard names**
   ```
   ✅ Good: requirements.txt
   ✅ Good: requirements-dev.txt
   ✅ Good: .env
   ✅ Good: .gitignore
   ✅ Good: docker-compose.yml
   ✅ Good: Dockerfile.backend
   ```

### 📊 Your Project Examples

| File | Status | Notes |
|------|--------|-------|
| `requirements.txt` | ✅ Perfect | Standard name |
| `docker-compose.yml` | ✅ Perfect | Standard name |
| `alembic.ini` | ✅ Perfect | Alembic standard |
| `Dockerfile.backend` | ✅ Good | Descriptive suffix |

---

## 🐳 Docker/Infrastructure

### Services

**Convention**: `snake_case` or `kebab-case`

```yaml
✅ Good:
services:
  postgres:
    container_name: pharma_analytics_db
  redis:
    container_name: pharma_analytics_redis
  backend:
    container_name: pharma_analytics_backend

❌ Bad:
services:
  Postgres:                    # Should be lowercase
    container_name: PharmaAnalyticsDB  # Should be snake_case
```

### Container Names

**Convention**: `snake_case` with project prefix

```yaml
✅ Good:
container_name: pharma_analytics_db
container_name: pharma_analytics_redis
container_name: pharma_analytics_backend

❌ Bad:
container_name: pharmaAnalyticsDB      # Should be snake_case
container_name: PharmaAnalyticsDB     # Should be lowercase
```

### Environment Variables

**Convention**: `UPPER_SNAKE_CASE`

```yaml
✅ Good:
environment:
  - FLASK_ENV=development
  - DB_HOST=postgres
  - DB_USER=pharma_user
  - DATABASE_URL=postgresql://...

❌ Bad:
environment:
  - flask_env=development      # Should be UPPER_CASE
  - dbHost=postgres            # Should be UPPER_SNAKE_CASE
```

---

## ✅ Summary Checklist

### Quick Reference

| Element | Convention | Example |
|---------|-----------|---------|
| **Folders** | `snake_case` | `analytics/`, `ingestion/` |
| **Python Files** | `snake_case` | `services.py`, `routes.py` |
| **Classes** | `PascalCase` | `IngestionService` |
| **Functions/Methods** | `snake_case` | `upload_file()` |
| **Private Methods** | `_snake_case` | `_process_csv_file()` |
| **Variables** | `snake_case` | `file_name` |
| **Constants** | `UPPER_SNAKE_CASE` | `MAX_FILE_SIZE` |
| **API Endpoints** | `kebab-case` | `/api/analytics/cost-analysis` |
| **Database Tables** | `snake_case` plural | `drug_transactions` |
| **Database Columns** | `snake_case` | `transaction_date` |
| **Docker Services** | `snake_case` | `pharma_analytics_db` |
| **Env Variables** | `UPPER_SNAKE_CASE` | `FLASK_ENV` |

---

## 🎯 Key Principles

1. **Consistency**: Use the same convention throughout
2. **Clarity**: Names should be self-documenting
3. **Convention**: Follow language/framework standards
4. **Descriptive**: Avoid abbreviations unless standard (DAL, API, etc.)
5. **Length**: Balance between descriptive and concise

---

## 📚 References

- **PEP 8**: Python Style Guide
- **Flask Conventions**: Flask best practices
- **REST API Design**: RESTful naming conventions
- **SQL Style Guide**: Database naming conventions

---

## ✅ Your Project Compliance

**Overall Grade: A+ (Excellent)**

Your project follows naming conventions very well:
- ✅ Consistent folder naming
- ✅ Proper Python class/method naming
- ✅ RESTful API endpoints
- ✅ Standard database naming
- ✅ Clear and descriptive names throughout

**No changes needed** - your naming conventions are excellent! ✅

