# PharmaAnalytics Project Summary

## Overview

PharmaAnalytics is a comprehensive hospital pharmacy data analysis and forecasting platform designed to handle large-scale data ingestion, real-time analytics, and predictive modeling. The system processes pharmaceutical transaction data (800k+ records per file) and provides insights through dashboards and demand forecasting capabilities.

## Architecture & Pipeline

### High-Level Architecture

The project follows a **three-module microservices architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Application                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask REST API Backend                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Ingestion   │  │  Dashboard   │  │ Forecasting  │       │
│  │   Module     │  │   Module     │  │   Module     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────┬──────────────────┬──────────────────┬───────────┘
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL Database (SQLAlchemy)               │
│  • drug_transactions                                        │
│  • data_ingestion_log                                       │
│  • data_ingestion_errors                                    │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│         Celery Worker (Background Processing)               │
│              Redis (Message Broker & Results)               │
└─────────────────────────────────────────────────────────────┘
```

### Data Pipeline Flow

```
1. Data Upload
   └─> Excel/CSV File Upload via API
       └─> File Validation & Temporary Storage
           └─> Create Ingestion Log Entry
               └─> Queue Celery Task (via Redis)
                   └─> Return Upload ID to Client

2. Background Processing (Celery Worker)
   └─> Load File (Polars/Pandas)
       └─> Data Cleaning & Transformation
           └─> Batch Processing (10k records/batch)
               └─> Database Insertion (SQLAlchemy)
                   └─> Update Progress (Redis)
                       └─> Update Ingestion Log Status

3. Dashboard Analytics
   └─> Query Processed Data (SQLAlchemy ORM)
       └─> Aggregate & Transform
           └─> Format Response (Serializers)
               └─> Return JSON to Frontend

4. Forecasting
   └─> Load Historical Data from Database
       └─> Feature Engineering
           └─> Model Training (XGBoost/Simple Moving Average)
               └─> Generate Forecasts
                   └─> Return Predictions with Confidence Intervals
```

## Three Core Modules

### Module 1: Ingestion

**Purpose**: Handle all data ingestion and preprocessing operations

**Key Responsibilities**:
- File upload and validation (Excel, CSV formats)
- Data cleaning and standardization
- Data transformation and normalization
- Batch processing for large datasets (800k+ records)
- Error handling and logging
- Duplicate detection

**Technology Stack**:
- **Polars/Pandas**: High-performance data processing
- **Celery**: Asynchronous task processing
- **Redis**: Task queue and result backend
- **SQLAlchemy**: Database operations
- **Flask**: REST API endpoints

**Key Components**:
- `routes.py`: API endpoints (`POST /api/ingestion/upload`)
- `services.py`: Business logic layer (class-based)
- `processors.py`: File processing orchestration
- `tasks.py`: Celery background tasks
- `cleaning.py`: Data cleaning rules and transformations
- `transformation.py`: Data standardization
- `dal.py`: Data access layer

**Workflow**:
1. Client uploads file via API
2. File is validated and saved temporarily
3. Ingestion log entry created in database
4. Celery task queued in Redis
5. Worker processes file asynchronously
6. Progress updates stored in Redis
7. Processed data inserted into PostgreSQL in batches
8. Final status updated in ingestion log

**API Endpoints**:
- `POST /api/ingestion/upload` - Upload file for processing
- `GET /api/ingestion/status/<id>` - Get processing status
- `GET /api/ingestion/history` - List ingestion history
- `DELETE /api/ingestion/<id>/cancel` - Cancel processing

---

### Module 2: Dashboard

**Purpose**: Provide analytics and visualization APIs for frontend dashboards

**Key Responsibilities**:
- Aggregate transaction data
- Generate statistics and metrics
- Create chart-ready data formats
- Support filtering and date range queries
- Department and category analytics

**Technology Stack**:
- **SQLAlchemy**: Complex database queries with ORM
- **PostgreSQL**: Advanced SQL aggregations
- **Flask**: REST API endpoints

**Key Components**:
- `routes.py`: API endpoints (`GET /api/dashboard/*`)
- `services.py`: Business logic layer
- `queries.py`: Complex SQL queries and aggregations
- `serializers.py`: Response formatting
- `charts.py`: Chart data generation
- `dashboard_data.py`: Dashboard-specific data preparation

**Key Features**:
- Top drugs by quantity/volume
- Drug demand trends over time
- Department performance metrics
- Category-wise analytics
- Summary statistics
- Custom date range filtering

**API Endpoints**:
- `GET /api/dashboard/top-drugs` - Top dispensed drugs
- `GET /api/dashboard/drug-demand` - Demand trends
- `GET /api/dashboard/summary-stats` - Overall statistics
- `GET /api/dashboard/chart-data/<type>` - Pre-formatted chart data
- `GET /api/dashboard/department-performance` - Department metrics

---

### Module 3: Forecasting

**Purpose**: Generate demand forecasts using machine learning models

**Key Responsibilities**:
- Load historical transaction data
- Feature engineering (time-based features, lag features)
- Model training and evaluation
- Generate future forecasts
- Provide confidence intervals
- Model performance metrics

**Technology Stack**:
- **XGBoost**: Advanced gradient boosting for time-series
- **Scikit-learn**: Model evaluation metrics
- **Pandas**: Data manipulation for ML
- **SQLAlchemy**: Data loading from database
- **NumPy**: Numerical computations

**Key Components**:
- `ml/services.py`: Simple moving average forecasting (MVP)
- `ml_xgboost/service.py`: XGBoost-based forecasting
- `ml_xgboost/models/xgboost_forecaster.py`: XGBoost model wrapper
- `ml_xgboost/features/xgboost_features.py`: Feature engineering
- `ml_xgboost/utils/data_preparation.py`: Data preprocessing
- `ml_xgboost/utils/evaluation.py`: Model evaluation
- `ml_xgboost/utils/forecast_generator.py`: Forecast generation

**Forecasting Methods**:

1. **Simple Moving Average** (`ml` module):
   - Basic time-series forecasting
   - Uses average of last 7 days
   - Suitable for quick estimates

2. **XGBoost Forecasting** (`ml_xgboost` module):
   - Advanced machine learning approach
   - Feature engineering: lag features, rolling statistics, time features
   - Train-test split for evaluation
   - Confidence intervals based on prediction errors
   - Feature importance analysis

**Workflow**:
1. Load historical data from database (date range filtering)
2. Resample to daily frequency
3. Handle missing values
4. Create features (lags, rolling means, time features)
5. Split into train/test sets
6. Train XGBoost model
7. Evaluate on test set
8. Generate future forecasts
9. Calculate confidence intervals
10. Return formatted results

**API Endpoints**:
- `GET /api/ml/forecast` - Simple forecast (moving average)
- `GET /api/ml-xgboost/forecast` - XGBoost forecast

---

## Technology Stack Details

### Celery & Redis

**Role**: Asynchronous task processing and message queue

**Why Celery?**
- Handles long-running data processing tasks asynchronously
- Prevents API timeouts for large file uploads
- Enables progress tracking
- Supports task retries and error handling

**Why Redis?**
- **Message Broker**: Routes tasks from Flask app to Celery workers
- **Result Backend**: Stores task results and status updates
- **Progress Tracking**: Real-time progress updates during processing
- **Note**: Redis is used ONLY for Celery, NOT as a database. All application data is stored in PostgreSQL.

**Configuration**:
- Celery broker URL: `redis://redis:6379/0`
- Celery result backend: `redis://redis:6379/0`
- Task routing: `ingestion.process_file`

**Task Flow**:
```
Flask API → Queue Task → Redis → Celery Worker → Process File → Update Redis → Flask API (status check)
```

**Key Files**:
- `celery_worker.py`: Celery worker entry point
- `backend/app/extensions.py`: Celery app initialization
- `backend/app/modules/ingestion/tasks.py`: Celery task definitions

---

### Docker

**Role**: Containerization and orchestration

**Architecture**:
- **Multi-container setup** using Docker Compose
- **Service isolation** for scalability
- **Volume mounting** for development
- **Health checks** for service dependencies

**Services**:

1. **PostgreSQL** (`postgres:15-alpine`):
   - Main application database
   - Persistent volume for data
   - Health checks for startup coordination

2. **Redis** (`redis:7-alpine`):
   - Celery message broker
   - Persistent volume for task queue
   - Health checks

3. **Backend** (`Dockerfile.backend`):
   - Flask application server
   - Production dependencies
   - Volume mounts for hot-reload

4. **Celery Worker** (`Dockerfile.backend`):
   - Background task processor
   - Same image as backend, different command
   - Processes queued tasks

**Docker Compose Benefits**:
- Single command deployment (`docker-compose up`)
- Service dependency management
- Network isolation
- Environment variable management
- Volume persistence

**Key Files**:
- `docker-compose.yml`: Service orchestration
- `docker/Dockerfile.backend`: Backend and worker image
- `docker/Dockerfile.analysis`: Jupyter notebook environment (optional)

---

### SQLAlchemy

**Role**: Object-Relational Mapping (ORM) and database abstraction

**Why SQLAlchemy?**
- **Type Safety**: Python type hints with database models
- **Query Building**: Pythonic query construction
- **Connection Pooling**: Efficient database connections
- **Migration Support**: Alembic for schema versioning
- **Cross-Database**: PostgreSQL-specific optimizations

**Architecture**:

1. **Models** (`backend/app/database/models.py`):
   - `DrugTransaction`: Main transaction table
   - `DataIngestionLog`: Upload tracking
   - `DataIngestionError`: Error logging

2. **Session Management** (`backend/app/database/session.py`):
   - Database session factory
   - Context managers for automatic cleanup
   - Connection pooling configuration

3. **Connection** (`backend/app/database/connection.py`):
   - Database URL construction
   - Engine creation and configuration
   - Connection pool settings

4. **Base Repository** (`backend/app/database/base.py`):
   - Common database operations
   - Query helpers

**Key Features**:
- **Indexes**: Optimized queries on date, drug_code, department
- **Constraints**: Data validation at database level
- **UUID Primary Keys**: Distributed system compatibility
- **Timestamps**: Automatic created_at tracking
- **Relationships**: Foreign key relationships

**Query Patterns**:
- ORM queries for simple operations
- Raw SQL for complex aggregations (in `queries.py`)
- Batch inserts for performance
- Transaction management for data integrity

**Migration Management**:
- Alembic for schema versioning
- Migration files in `migrations/versions/`
- Automatic migration generation

---

## Data Flow Summary

### Complete Pipeline

```
1. INGESTION PHASE
   ┌─────────────────────────────────────────┐
   │ User uploads Excel/CSV file             │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Flask API receives file                 │
   │ • Validates file format                 │
   │ • Saves to temporary storage            │
   │ • Creates ingestion log entry           │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Queue Celery task via Redis             │ 
   │ • Task ID returned to client            │
   │ • File path stored in task              │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Celery Worker picks up task             │
   │ • Loads file (Polars/Pandas)            │
   │ • Cleans and transforms data            │
   │ • Processes in batches (10k records)    │
   │ • Updates progress in Redis             │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ SQLAlchemy inserts into PostgreSQL      │
   │ • Batch inserts for performance         │
   │ • Error records logged separately       │
   │ • Updates ingestion log status          │
   └─────────────────────────────────────────┘

2. DASHBOARD PHASE
   ┌─────────────────────────────────────────┐
   │ Frontend requests analytics             │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Flask API receives request              │
   │ • Validates parameters                  │
   │ • Calls Dashboard Service               │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ SQLAlchemy queries PostgreSQL           │
   │ • Complex aggregations                  │
   │ • Date range filtering                  │
   │ • Department/category filters           │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Serializers format response             │
   │ • JSON structure                        │
   │ • Chart-ready formats                   │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Frontend receives formatted data        │
   └─────────────────────────────────────────┘

3. FORECASTING PHASE
   ┌─────────────────────────────────────────┐
   │ Frontend requests forecast              │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Flask API receives request              │
   │ • Validates drug_code and parameters    │
   │ • Calls Forecasting Service             │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ SQLAlchemy loads historical data        │
   │ • Date range filtering                  │
   │ • Drug-specific transactions            │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Feature Engineering                     │
   │ • Resample to daily frequency           │
   │ • Create lag features                   │
   │ • Rolling statistics                    │
   │ • Time-based features                   │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ XGBoost Model Training                  │
   │ • Train-test split                      │
   │ • Model training                        │
   │ • Evaluation metrics                    │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Generate Forecasts                      │
   │ • Future feature creation               │
   │ • Prediction generation                 │
   │ • Confidence intervals                  │
   └───────────────┬─────────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────────┐
   │ Return formatted forecast results       │
   └─────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Three-Module Architecture
- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Maintainability**: Changes in one module don't affect others
- **Scalability**: Modules can be scaled independently
- **Testability**: Each module can be tested in isolation

### 2. Class-Based Services
- **Consistency**: All services inherit from `BaseService`
- **Reusability**: Common functionality (logging, error handling) in base class
- **Type Safety**: Better IDE support and type checking

### 3. Asynchronous Processing (Celery)
- **User Experience**: Non-blocking file uploads
- **Scalability**: Can process multiple files concurrently
- **Reliability**: Task retries and error handling
- **Progress Tracking**: Real-time status updates

### 4. SQLAlchemy ORM
- **Type Safety**: Database models with Python types
- **Query Building**: Pythonic query construction
- **Migration Support**: Alembic for schema changes
- **Performance**: Connection pooling and batch operations

### 5. Docker Containerization
- **Consistency**: Same environment across development/production
- **Isolation**: Services don't interfere with each other
- **Easy Deployment**: Single command to start all services
- **Development**: Hot-reload with volume mounts

---

## Technology Integration Summary

| Technology | Purpose | Integration Point |
|------------|---------|-------------------|
| **Celery** | Async task processing | Ingestion module for file processing |
| **Redis** | Message broker & results | Celery broker/backend, progress tracking |
| **Docker** | Containerization | All services containerized via docker-compose |
| **SQLAlchemy** | Database ORM | All modules use SQLAlchemy for database access |
| **PostgreSQL** | Primary database | All application data storage |
| **Flask** | Web framework | REST API for all modules |
| **XGBoost** | ML forecasting | Forecasting module for demand prediction |
| **Polars/Pandas** | Data processing | Ingestion module for file processing |

---

## Project Structure

```
PharmaAnalytics/
├── backend/
│   └── app/
│       ├── modules/
│       │   ├── ingestion/      # Module 1: Data ingestion
│       │   ├── dashboard/       # Module 2: Analytics & visualization
│       │   └── ml_xgboost/      # Module 3: Forecasting (XGBoost)
│       │   └── ml/              # Module 3: Forecasting (Simple)
│       ├── database/            # SQLAlchemy models & session
│       └── shared/              # Common utilities
├── docker/                      # Docker configurations
├── migrations/                  # Alembic migrations
├── data/                        # Uploaded files
├── celery_worker.py            # Celery worker entry point
├── docker-compose.yml          # Service orchestration
└── requirements.txt            # Dependencies
```

---

## Conclusion

PharmaAnalytics demonstrates a modern, scalable architecture for handling large-scale pharmaceutical data processing. The three-module design (Ingestion, Dashboard, Forecasting) provides clear separation of concerns, while technologies like Celery, Redis, Docker, and SQLAlchemy ensure reliability, scalability, and maintainability. The system efficiently processes hundreds of thousands of records, provides real-time analytics, and generates accurate demand forecasts using machine learning models.

