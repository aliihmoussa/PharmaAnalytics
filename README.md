# Hospital Pharmacy Data Analysis Platform

A robust, scalable data analysis and machine learning solution for hospital pharmacy datasets. The system supports large-scale data ingestion, exploratory analysis, visualization, and predictive modeling.

## Project Overview

This platform provides:
- **Data Ingestion & Processing**: Efficient upload, validation, cleaning, and transformation of large datasets (800k+ records per file)
- **Analytics & Visualization**: RESTful APIs for frontend visualization, reporting, and cost analysis
- **Diagnostics**: Advanced data profiling, time-series analysis, and quality assessment
- **Forecasting**: Machine learning-based demand forecasting using XGBoost
- **Scalable Architecture**: Four-module architecture with class-based services for maintainability

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
├── backend/                       # Backend application (separate from frontend)
│   └── app/                       # Flask application
│       ├── __init__.py           # Flask app factory
│       ├── config.py             # Configuration settings
│       ├── extensions.py         # Celery and extensions initialization
│       ├── modules/              # Four main feature modules
│       │   ├── ingestion/        # Module 1: Data ingestion & processing
│       │   │   ├── routes.py     # API endpoints
│       │   │   ├── services.py   # Class-based service layer
│       │   │   ├── processors.py # Data processing logic
│       │   │   ├── dal.py        # Data access layer
│       │   │   ├── tasks.py      # Celery async tasks
│       │   │   ├── ingestion.py  # File loading utilities
│       │   │   ├── cleaning.py   # Data cleaning
│       │   │   ├── transformation.py # Data transformation
│       │   │   ├── requests.py   # Pydantic request models
│       │   │   ├── responses.py  # Response models
│       │   │   ├── schema.py     # Data schemas
│       │   │   └── exceptions.py # Module-specific exceptions
│       │   ├── analytics/         # Module 2: Analytics & visualization
│       │   │   ├── routes.py     # API endpoints
│       │   │   ├── services.py   # Dashboard service layer
│       │   │   ├── cost_services.py # Cost analysis service
│       │   │   ├── queries.py    # Complex database queries
│       │   │   ├── cost_queries.py # Cost analysis queries
│       │   │   ├── serializers.py # Response formatting
│       │   │   ├── charts.py     # Chart generation
│       │   │   ├── dashboard_data.py # Dashboard data prep
│       │   │   ├── requests.py   # Pydantic request models
│       │   │   ├── themes.py     # Chart themes
│       │   │   └── exceptions.py # Module-specific exceptions
│       │   ├── diagnostics/       # Module 3: Data diagnostics & profiling
│       │   │   ├── routes.py     # API endpoints
│       │   │   ├── services/     # Service layer
│       │   │   │   └── feature_service.py
│       │   │   ├── analyzers/    # Analysis components
│       │   │   │   ├── profiler.py # Drug profiler
│       │   │   │   ├── seasonality.py # Seasonality detection
│       │   │   │   ├── outliers.py # Outlier detection
│       │   │   │   ├── decomposition.py # Time series decomposition
│       │   │   │   ├── autocorrelation.py # ACF/PACF analysis
│       │   │   │   └── classifier.py # Drug classification
│       │   │   └── cache/        # Caching layer
│       │   │       └── redis_cache.py
│       │   └── forecasting/      # Module 4: Demand forecasting
│       │       ├── routes.py     # API endpoints
│       │       ├── forecast_service.py # Forecast service
│       │       ├── base_forecaster.py # Base forecaster interface
│       │       ├── factory.py    # Algorithm factory
│       │       ├── parsers.py    # Request/response parsers
│       │       ├── algorithms/   # Forecasting algorithms
│       │       │   └── xgboost_algorithm.py
│       │       ├── models/       # ML models
│       │       │   └── xgboost_model.py
│       │       ├── features/     # Feature engineering
│       │       │   ├── domain_features.py
│       │       │   └── xgboost_features.py
│       │       └── utils/         # Utility functions
│       │           ├── data_preparation.py
│       │           ├── enhanced_data_preparation.py
│       │           ├── evaluation.py
│       │           └── forecast_generator.py
│       ├── shared/               # Shared utilities across modules
│       │   ├── base_service.py   # Base service class
│       │   ├── middleware.py     # Error handling & request processing
│       │   ├── exceptions.py     # Custom exceptions
│       │   ├── validators.py     # Validation utilities
│       │   └── background_jobs.py # Background job utilities
│       └── database/             # Database layer
│           ├── models.py         # SQLAlchemy models
│           └── session.py        # Session management
├── data/
│   ├── schema/                   # Schema definitions
│   └── uploads/                  # Uploaded files (temp & archive)
├── migrations/                    # Alembic database migrations
├── notebooks/                     # Jupyter notebooks for exploration
├── scripts/                       # Utility scripts
├── docker/                        # Docker configurations
│   ├── Dockerfile.backend        # Production backend container
│   └── Dockerfile.analysis       # Development/analysis container
├── docs/                          # Documentation
├── run.py                         # Application entry point
├── celery_worker.py              # Celery worker entry point
├── requirements.txt               # Production dependencies
└── requirements-dev.txt           # Development dependencies
```

## Four-Module Architecture

The application follows a **feature-based modular architecture** with clear separation of concerns:

```
backend/app/
├── database/      # Database models and session management
├── modules/       # Four feature modules (pipeline stages)
│   ├── ingestion/    # Stage 1: Data ingestion
│   ├── analytics/     # Stage 2: Analytics & visualization
│   ├── diagnostics/   # Stage 3: Data diagnostics
│   └── forecasting/   # Stage 4: Demand forecasting
└── shared/        # Shared utilities across all modules
```

### Module 1: Ingestion (`backend/app/modules/ingestion/`)
**Purpose**: Handle all data ingestion and preprocessing
- Upload and validate data files (CSV, Excel)
- Preprocess and clean data
- Transform and standardize formats
- Store processed data in database
- Background processing with Celery
- **API**: `/api/ingestion/*`

### Module 2: Analytics (`backend/app/modules/analytics/`)
**Purpose**: Provide APIs for frontend visualization and analytics
- Retrieve processed data from database
- Generate dashboard metrics and statistics
- Cost analysis and reporting
- Chart data preparation
- Department performance metrics
- **API**: `/api/analytics/*`

### Module 3: Diagnostics (`backend/app/modules/diagnostics/`)
**Purpose**: Advanced data profiling and quality assessment
- Drug demand profiling and classification
- Time-series characteristics analysis
- Outlier detection
- Seasonality detection
- Autocorrelation analysis (ACF/PACF)
- Data quality assessment and risk analysis
- **API**: `/api/diagnostics/*`

### Module 4: Forecasting (`backend/app/modules/forecasting/`)
**Purpose**: Machine learning-based demand forecasting
- XGBoost-based demand forecasting
- Feature engineering for time-series
- Model training and evaluation
- Forecast generation with confidence intervals
- Multiple algorithm support (factory pattern)
- **API**: `/api/forecasting/*`

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

### Ingestion Module (`/api/ingestion/*`)

- `POST /api/ingestion/upload` - Upload a file for ingestion
- `GET /api/ingestion/status/<ingestion_log_id>` - Get ingestion status
- `GET /api/ingestion/history` - List ingestion history
- `DELETE /api/ingestion/<ingestion_log_id>/cancel` - Cancel ingestion

### Analytics Module (`/api/analytics/*`)

- `GET /api/analytics/top-drugs` - Top dispensed drugs
- `GET /api/analytics/drug-demand` - Drug demand trends over time
- `GET /api/analytics/summary-stats` - Overall statistics
- `GET /api/analytics/chart-data/<chart_type>` - Pre-formatted chart data
- `GET /api/analytics/department-performance` - Department metrics
- `GET /api/analytics/cost-analysis` - Cost analysis data
- `GET /api/analytics/hospital-stay` - Hospital stay analysis

### Diagnostics Module (`/api/diagnostics/*`)

- `GET /api/diagnostics/features/{drug_code}` - Get drug diagnostics and profiling
- `GET /api/diagnostics/features/{drug_code}?department={dept_id}` - Filter by department
- `GET /api/diagnostics/features/{drug_code}?start_date={date}&end_date={date}` - Date range filter

### Forecasting Module (`/api/forecasting/*`)

- `POST /api/forecasting/predict` - Generate demand forecast
- `GET /api/forecasting/models` - List available forecasting models

### Example Requests

```bash
# Upload file
curl -X POST http://localhost:5000/api/ingestion/upload \
  -F "file=@data.csv" \
  -F "file_name=data.csv" \
  -F "file_year=2023"

# Get top drugs
curl "http://localhost:5000/api/analytics/top-drugs?start_date=2023-01-01&end_date=2023-12-31&limit=10"

# Get drug diagnostics
curl "http://localhost:5000/api/diagnostics/features/P182054?department=5"

# Generate forecast
curl -X POST http://localhost:5000/api/forecasting/predict \
  -H "Content-Type: application/json" \
  -d '{"drug_code": "P182054", "horizon": 30, "algorithm": "xgboost"}'
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

### Module Interactions (Pipeline Flow)

```
1. Ingestion Module
   ↓ (stores data)
   Database
   ↓ (reads data)
2. Analytics Module → Frontend (visualization)
   ↓ (analyzes data)
3. Diagnostics Module → Frontend (data quality insights)
   ↓ (uses diagnostics)
4. Forecasting Module → Frontend (predictions)
```

- **Ingestion Module** processes files and stores data in database
- **Analytics Module** reads processed data for visualization and reporting
- **Diagnostics Module** analyzes data quality and patterns
- **Forecasting Module** uses diagnostics insights for demand forecasting

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
  - Notebook files for data exploration
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

### Using Backend Modules in Notebooks

For notebook-based exploration, you can use the backend modules directly:

```python
# Import from backend modules
from backend.app.modules.analytics.services import DashboardService
from backend.app.modules.diagnostics.analyzers import DrugProfiler
from backend.app.modules.ingestion.ingestion import IngestionLoader

# Use services
service = DashboardService()
analytics_data = service.get_top_drugs(start_date='2023-01-01', end_date='2023-12-31')

# Use analyzers
profiler = DrugProfiler()
diagnostics = profiler.profile_drug('P182054')

# Or use Polars/pandas directly for custom analysis
import polars as pl
import pandas as pd

# Load and analyze data
df = pl.read_csv('data/sample.csv')
# Perform your analysis...
```

## Future Enhancements

- ✅ Data upload API for file ingestion
- ✅ Background job processing with Celery
- ✅ Redis integration for task queue
- ✅ Class-based service architecture
- ✅ ML model integration (XGBoost forecasting)
- ✅ Data diagnostics and profiling
- ✅ Advanced analytics and cost analysis
- 🔄 Additional forecasting algorithms (ARIMA, Prophet, etc.)
- 🔄 Advanced caching strategies
- 🔄 Real-time analytics
- 🔄 Authentication & authorization
- 🔄 API rate limiting
- 🔄 Model versioning and A/B testing

## Contributing

1. Follow the four-module architecture pattern
2. Use class-based services (inherit from `BaseService`)
3. Follow the Routes → Services → DAL pattern
4. Write tests for new features
5. Update documentation
6. Follow code style (black, flake8, mypy, isort)
7. Use Pydantic models for request validation
8. Follow naming conventions (see `docs/NAMING_CONVENTIONS_GUIDE.md`)

## Project Status

- ✅ **Module 1 (Ingestion)**: Complete and functional
- ✅ **Module 2 (Analytics)**: Complete and functional
- ✅ **Module 3 (Diagnostics)**: Complete and functional
- ✅ **Module 4 (Forecasting)**: Complete and functional (XGBoost)

## Architecture Principles

### Structure Philosophy

```
backend/
└── app/                    # Flask application
    ├── database/           # Database layer (models, session)
    ├── modules/             # Feature modules (pipeline stages)
    │   ├── ingestion/      # Stage 1: Data ingestion
    │   ├── analytics/       # Stage 2: Analytics
    │   ├── diagnostics/     # Stage 3: Diagnostics
    │   └── forecasting/     # Stage 4: Forecasting
    └── shared/              # Shared utilities
```

**Key Principles:**
- **Feature-based modules**: Each module represents a pipeline stage
- **Separation of concerns**: Database, modules, and shared utilities are clearly separated
- **Consistent structure**: All modules follow Routes → Services → DAL pattern
- **Shared utilities**: Common code in `shared/` to avoid duplication
- **Scalable**: Easy to add new modules or extend existing ones

## License

[Your License Here]

## Contact

[Your Contact Information]
