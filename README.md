# Hospital Pharmacy Data Analysis Platform

A robust, scalable data analysis and machine learning solution for hospital pharmacy datasets. The system supports large-scale data ingestion, exploratory analysis, visualization, and predictive modeling.

## Project Overview

This platform provides:
- **Data Processing**: Efficient ingestion and cleaning of large datasets (800k+ records per file)
- **Analytics APIs**: RESTful endpoints for dashboard integration
- **Exploratory Analysis**: Tools for data exploration and visualization
- **Scalable Architecture**: Feature-based backend design for maintainability

## Technology Stack

- **Backend**: Python Flask (Feature-based architecture)
- **Database**: PostgreSQL
- **Data Processing**: Polars (for performance), pandas (fallback)
- **Containerization**: Docker & Docker Compose
- **Visualization**: Plotly, Seaborn (for initial EDA)
- **ML Frameworks**: Scikit-learn, XGBoost (for future modeling)

## Project Structure

```
PharmaAnalytics/
├── backend/              # Flask API (feature-based architecture)
│   ├── features/         # Feature modules (health, analytics)
│   ├── shared/           # Shared utilities
│   └── database/         # Database connection & base repository
├── src/                  # Data processing & analysis (initial EDA)
│   ├── data_processing/  # File ingestion and cleaning
│   ├── analysis/         # Statistical analysis
│   └── visualization/   # Chart generation (for reports)
├── data/                 # Data files and schema documentation
├── notebooks/            # Jupyter notebooks for exploration
├── scripts/              # Database setup and utility scripts
└── docker/               # Docker configurations
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)

### Installation

1. **Clone the repository** (if applicable)

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Start services with Docker**
   ```bash
   docker-compose up -d
   ```

6. **Initialize database**
   ```bash
   python scripts/setup_database.py
   ```

7. **Run the application**
   ```bash
   python -m flask run
   # Or: python backend/app.py
   ```

## API Endpoints

### Health Check
```
GET /api/health
```

### Analytics Endpoints

- `GET /api/analytics/top-drugs` - Top dispensed drugs
- `GET /api/analytics/drug-demand` - Drug demand trends
- `GET /api/analytics/summary-stats` - Overall statistics
- `GET /api/analytics/chart-data/{chart_type}` - Pre-formatted chart data
- `GET /api/analytics/department-performance` - Department metrics

### Example Request

```bash
curl "http://localhost:5000/api/analytics/top-drugs?start_date=2023-01-01&end_date=2023-12-31&limit=10"
```

## Development

### Running Tests

```bash
pytest backend/tests/
```

### Code Quality

```bash
black backend/
flake8 backend/
mypy backend/
```

### Database Setup

Initialize database schema:
```bash
python scripts/setup_database.py
```

## Architecture

### Feature-Based Backend

Each feature module is self-contained:
- `routes.py` - HTTP endpoints (controllers)
- `service.py` - Business logic
- `dal.py` - Data access layer (SQL queries)
- `models.py` - Request/Response DTOs (Pydantic)
- `exceptions.py` - Feature-specific exceptions

### Data Flow

```
Frontend → API Endpoint → Service Layer → Data Access Layer → PostgreSQL
                                    ↓
                            Format Response → Frontend
```

## Database Schema

### Core Tables

- `drug_transactions` - Main transaction table
- `data_ingestion_log` - File upload tracking

See `scripts/setup_database.py` for full schema definition.

## Data Processing

### Initial EDA Phase

Use `src/` modules for initial data exploration:

```python
from src.data_processing.ingestion import load_file
from src.data_processing.cleaning import generate_quality_report
from src.analysis.eda import data_profile

# Load data
df = load_file('data/raw/sample.csv')

# Generate quality report
report = generate_quality_report(df)

# Data profile
profile = data_profile(df)
```

## Configuration

Environment variables (`.env`):
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name
- `DB_HOST` - Database host
- `FLASK_ENV` - Flask environment (development/production)
- `SECRET_KEY` - Flask secret key

## Docker

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Stop Services
```bash
docker-compose down
```

## Future Enhancements

- ML model integration for predictive analytics
- Data upload API for file ingestion
- Advanced caching with Redis
- Real-time analytics
- Authentication & authorization

## Contributing

1. Follow feature-based architecture pattern
2. Write tests for new features
3. Update documentation
4. Follow code style (black, flake8)

## License

[Your License Here]

## Contact

[Your Contact Information]

