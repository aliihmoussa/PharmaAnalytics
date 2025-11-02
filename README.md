# Hospital Pharmacy Data Analysis Platform

A robust, scalable data analysis and machine learning solution for hospital pharmacy datasets. The system supports large-scale data ingestion, exploratory analysis, visualization, and predictive modeling.

## Project Overview

This platform provides:
- **Data Ingestion & Processing**: Efficient upload, validation, cleaning, and transformation of large datasets (800k+ records per file)
- **Dashboard Analytics**: RESTful APIs for frontend visualization and reporting
- **Machine Learning**: Framework for model training and prediction (future implementation)
- **Scalable Architecture**: Three-module architecture with class-based services for maintainability

## Technology Stack

- **Backend**: Python Flask with class-based services
- **Database**: PostgreSQL 15
- **Task Queue**: Celery with Redis
- **Data Processing**: Polars (for performance), pandas (fallback)
- **Containerization**: Docker & Docker Compose
- **Visualization**: Plotly, Seaborn, Matplotlib
- **ML Frameworks**: Scikit-learn, XGBoost (for future modeling)

## Project Structure

```
PharmaAnalytics/
├── backend/
│   └── app/
│       ├── __init__.py           # Flask app factory
│       ├── config.py             # Configuration settings
│       ├── extensions.py         # Celery and extensions initialization
│       ├── modules/              # Three main modules
│       │   ├── ingestion/        # Module 1: Data ingestion & processing
│       │   │   ├── routes.py     # API endpoints
│       │   │   ├── services.py   # Class-based service layer
│       │   │   ├── processors.py # Data processing logic
│       │   │   ├── dal.py        # Data access layer
│       │   │   ├── tasks.py      # Celery async tasks
│       │   │   ├── ingestion.py  # File loading utilities
│       │   │   ├── cleaning.py   # Data cleaning
│       │   │   └── transformation.py # Data transformation
│       │   ├── dashboard/        # Module 2: Dashboard & analytics
│       │   │   ├── routes.py     # API endpoints
│       │   │   ├── services.py   # Class-based service layer
│       │   │   ├── queries.py    # Complex database queries
│       │   │   ├── serializers.py # Response formatting
│       │   │   ├── charts.py     # Chart generation
│       │   │   └── dashboard_data.py # Dashboard data prep
│       │   └── ml/               # Module 3: Machine Learning (placeholder)
│       ├── shared/               # Shared utilities
│       │   ├── base_service.py   # Base service class
│       │   ├── middleware.py     # Error handling & request processing
│       │   ├── exceptions.py     # Custom exceptions
│       │   └── validators.py     # Validation utilities
│       └── database/             # Database layer
│           ├── models.py         # SQLAlchemy models
│           ├── connection.py     # Connection pooling
│           ├── session.py        # Session management
│           └── base.py           # Base repository pattern
├── src/
│   └── analysis/                 # Framework-agnostic analysis (for notebooks)
│       ├── eda.py                # Exploratory data analysis
│       ├── metrics.py            # Statistical metrics
│       └── statistics.py         # Statistical functions
├── data/
│   ├── schema/                   # Schema definitions
│   └── uploads/                  # Uploaded files (temp & archive)
├── notebooks/                     # Jupyter notebooks for exploration
├── scripts/                       # Database setup scripts
├── docker/                        # Docker configurations
│   ├── Dockerfile.backend        # Production backend container
│   └── Dockerfile.analysis       # Development/analysis container
├── run.py                         # Application entry point
├── celery_worker.py              # Celery worker entry point
├── requirements.txt               # Production dependencies
└── requirements-dev.txt           # Development dependencies
```

## Three-Module Architecture

### Module 1: Ingestion (`backend/app/modules/ingestion/`)
**Purpose**: Handle all data ingestion and preprocessing
- Upload and validate data files
- Preprocess and clean data
- Transform and standardize formats
- Store processed data in database
- **API**: `/api/ingestion/*`

### Module 2: Dashboard (`backend/app/modules/dashboard/`)
**Purpose**: Provide APIs for frontend visualization
- Retrieve processed data from database
- Provide APIs for frontend visualization
- Support dynamic charting and dashboard updates
- **API**: `/api/dashboard/*`

### Module 3: Machine Learning (`backend/app/modules/ml/`)
**Purpose**: Manage ML tasks (placeholder for future)
- Train and maintain ML models
- Generate predictions and insights
- Expose results via APIs
- **Status**: Not yet implemented

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Redis (or use Docker)

### Installation

1. **Clone the repository** (if applicable)

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Production
   pip install -r requirements.txt
   
   # Development (includes testing, code quality tools, Jupyter)
   pip install -r requirements-dev.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis credentials
   ```

5. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```
   This starts:
   - PostgreSQL database
   - Redis (for Celery)
   - Flask backend application
   - Celery worker

6. **Initialize database**
   ```bash
   python scripts/setup_database.py
   ```

7. **Run the application locally** (optional, if not using Docker)
   ```bash
   # Start Redis (required for Celery)
   redis-server
   
   # Start Celery worker (in separate terminal)
   celery -A celery_worker worker --loglevel=info
   
   # Start Flask app
   python run.py
   ```

## API Endpoints

### Ingestion Module

- `POST /api/ingestion/upload` - Upload a file for ingestion
- `GET /api/ingestion/status/<ingestion_log_id>` - Get ingestion status
- `GET /api/ingestion/history` - List ingestion history
- `DELETE /api/ingestion/<ingestion_log_id>/cancel` - Cancel ingestion

### Dashboard Module

- `GET /api/dashboard/top-drugs` - Top dispensed drugs
- `GET /api/dashboard/drug-demand` - Drug demand trends over time
- `GET /api/dashboard/summary-stats` - Overall statistics
- `GET /api/dashboard/chart-data/<chart_type>` - Pre-formatted chart data
- `GET /api/dashboard/department-performance` - Department metrics

### Example Requests

```bash
# Upload file
curl -X POST http://localhost:5000/api/ingestion/upload \
  -F "file=@data.csv" \
  -F "file_name=data.csv" \
  -F "file_year=2023"

# Get top drugs
curl "http://localhost:5000/api/dashboard/top-drugs?start_date=2023-01-01&end_date=2023-12-31&limit=10"

# Get summary statistics
curl "http://localhost:5000/api/dashboard/summary-stats?start_date=2023-01-01&end_date=2023-12-31"
```

## Development

### Running Tests

```bash
pytest backend/tests/
```

### Code Quality

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/

# Import sorting
isort backend/
```

### Database Setup

Initialize database schema:
```bash
python scripts/setup_database.py
```

### Running Celery Worker

```bash
# Local development
celery -A celery_worker worker --loglevel=info

# With Docker
docker-compose up celery_worker
```

## Architecture

### Class-Based Services

All services inherit from `BaseService` and follow a consistent pattern:

```python
from backend.app.shared.base_service import BaseService

class MyService(BaseService):
    def __init__(self):
        super().__init__()
        self.dal = MyDAL()
    
    def my_method(self):
        # Use self.logger for logging
        # Use self._format_response() for responses
        # Use self._validate_input() for validation
        pass
```

### Data Flow

```
Frontend → API Endpoint (routes.py)
         → Service Layer (services.py - class-based)
         → Data Access Layer (dal.py/queries.py)
         → PostgreSQL Database
         ↓
    Format Response (serializers.py)
         ↓
    Frontend
```

### Module Interactions

- **Ingestion Module** processes files and stores data in database
- **Dashboard Module** reads processed data from database
- **ML Module** (future) will consume processed data for training and predictions

## Database Schema

### Core Tables

- `drug_transactions` - Main transaction table
- `data_ingestion_log` - File upload tracking
- `data_ingestion_errors` - Failed records during ingestion

See `scripts/setup_database.py` and `backend/app/database/models.py` for full schema definition.

## Configuration

Environment variables (`.env`):

### Database
- `DB_USER` - Database user (default: pharma_user)
- `DB_PASSWORD` - Database password (default: pharma_password)
- `DB_NAME` - Database name (default: pharma_analytics_db)
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DATABASE_URL` - Full database URL (auto-generated if not provided)

### Redis & Celery (Redis used ONLY for Celery, not as database)
**Note**: Redis is used exclusively as Celery's message broker and result backend. All application data is stored in PostgreSQL.
- `REDIS_HOST` - Redis host (default: localhost)
- `REDIS_PORT` - Redis port (default: 6379)
- `CELERY_BROKER_URL` - Celery broker URL (default: redis://localhost:6379/0)
- `CELERY_RESULT_BACKEND` - Celery result backend (default: redis://localhost:6379/0)

### Flask
- `FLASK_ENV` - Flask environment (development/production)
- `SECRET_KEY` - Flask secret key
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `DEBUG` - Debug mode (True/False)

## Docker

### Why Two Dockerfiles?

The project uses two Dockerfiles for different purposes:

#### 1. `Dockerfile.backend` (Production Backend)
- **Purpose**: Production Flask application and Celery worker
- **Contains**: 
  - Flask runtime environment
  - Celery worker setup
  - All production dependencies (`requirements.txt`)
  - Backend application code
- **Used by**: `docker-compose.yml` for `backend` and `celery_worker` services
- **Entry Point**: `run.py` (Flask app) or `celery_worker.py` (Celery worker)

#### 2. `Dockerfile.analysis` (Development/Analysis)
- **Purpose**: Jupyter notebook environment for data exploration
- **Contains**:
  - Jupyter notebook server
  - Development dependencies (`requirements-dev.txt`)
  - Analysis tools (EDA, visualization)
  - Notebook files and `src/analysis/` utilities
- **Use Case**: Standalone container for data scientists to run notebooks
- **Entry Point**: Jupyter notebook server
- **Note**: Not currently used in `docker-compose.yml` but available for manual use

**Recommendation**: Keep both - they serve different purposes (production vs. development/analysis).

### Docker Commands

#### Start All Services
```bash
docker-compose up -d
```

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f postgres
docker-compose logs -f redis
```

#### Stop Services
```bash
docker-compose down
```

#### Rebuild After Code Changes
```bash
docker-compose build --no-cache backend
docker-compose up -d
```

#### Run Analysis Container (Manual)
```bash
docker build -f docker/Dockerfile.analysis -t pharma-analytics-analysis .
docker run -p 8888:8888 -v $(pwd)/notebooks:/app/notebooks pharma-analytics-analysis
```

## Data Processing

### Using Ingestion Module

The ingestion module handles all data preprocessing:

```python
# Upload via API
POST /api/ingestion/upload

# Or use the service directly
from backend.app.modules.ingestion.services import IngestionService

service = IngestionService()
result = service.upload_file(file, "data.csv", 2023)
```

### Using Analysis Utilities (Notebooks)

For notebook-based exploration:

```python
from src.analysis.eda import data_profile, detect_patterns
from src.analysis.metrics import calculate_key_metrics
from src.analysis.statistics import statistical_summary

# Load and analyze data
df = load_file('data/sample.csv')
profile = data_profile(df)
metrics = calculate_key_metrics(df)
```

## Future Enhancements

- ✅ Data upload API for file ingestion
- ✅ Background job processing with Celery
- ✅ Redis integration for task queue
- ✅ Class-based service architecture
- 🔄 ML model integration for predictive analytics
- 🔄 Advanced caching strategies
- 🔄 Real-time analytics
- 🔄 Authentication & authorization
- 🔄 API rate limiting

## Contributing

1. Follow the three-module architecture pattern
2. Use class-based services (inherit from `BaseService`)
3. Write tests for new features
4. Update documentation
5. Follow code style (black, flake8, mypy, isort)

## Project Status

- ✅ **Module 1 (Ingestion)**: Complete and functional
- ✅ **Module 2 (Dashboard)**: Complete and functional
- 🚧 **Module 3 (ML)**: Structure created, implementation pending

## License

[Your License Here]

## Contact

[Your Contact Information]
