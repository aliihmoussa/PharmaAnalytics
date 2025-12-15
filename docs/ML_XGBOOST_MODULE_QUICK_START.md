# XGBoost Forecasting Module - Quick Start Guide

## Overview

The `ml_xgboost` module is a separate, self-contained implementation of the Colab XGBoost time-series forecasting script, adapted to work with your PostgreSQL database.

## Module Structure

```
backend/app/modules/ml_xgboost/
├── __init__.py
├── routes.py              # API endpoints
├── service.py             # Main service orchestrator
├── features/
│   └── xgboost_features.py  # Feature engineering (matching Colab)
├── models/
│   └── xgboost_forecaster.py  # XGBoost model wrapper
└── utils/
    ├── data_preparation.py    # DB → pandas conversion
    ├── evaluation.py         # Metrics calculation
    └── forecast_generator.py # Future forecast features
```

## API Endpoint

### GET `/api/ml-xgboost/forecast/<drug_code>`

**Query Parameters:**
- `forecast_days` (int, default: 14) - Days to forecast ahead
- `test_size` (int, default: 30) - Days to use for testing
- `lookback_days` (int, optional) - Limit historical data
- `start_date` (YYYY-MM-DD, optional) - Start date for historical data
- `end_date` (YYYY-MM-DD, optional) - End date for historical data

**Example Request:**
```bash
curl "http://localhost:5000/api/ml-xgboost/forecast/P733036?forecast_days=14&test_size=30"
```

**Response Format:**
```json
{
  "data": {
    "drug_code": "P733036",
    "historical": [
      {"date": "2019-01-01", "demand": 1234.5},
      ...
    ],
    "test_predictions": [
      {
        "date": "2019-12-01",
        "actual": 1500.0,
        "predicted": 1450.0,
        "error": 50.0
      },
      ...
    ],
    "forecast": [
      {
        "date": "2020-01-01",
        "predicted": 1600.0,
        "lower_bound": 1400.0,
        "upper_bound": 1800.0
      },
      ...
    ],
    "metrics": {
      "rmse": 45.2,
      "mae": 38.5,
      "mape": 12.3
    },
    "feature_importance": {
      "diff_7": 0.31,
      "diff_1": 0.23,
      ...
    },
    "training_history": {
      "train_rmse": [1000, 950, ...],
      "val_rmse": [1100, 1050, ...]
    },
    "method": "xgboost_colab",
    "forecast_days": 14,
    "test_size": 30
  }
}
```

## Features

### Feature Engineering (Matching Colab Script)

1. **Time Features**: hour, dayofweek, quarter, month, year, dayofyear, dayofmonth, weekofyear
2. **Cyclical Encoding**: sin/cos for dayofweek, month, dayofyear
3. **Lag Features**: 1, 2, 3, 7, 14, 21, 30 days
4. **Rolling Statistics**: mean, std, min, max for windows [7, 14, 30]
5. **Difference Features**: diff_1, diff_7
6. **Binary Features**: is_weekend, is_month_start, is_month_end, is_quarter_start, is_quarter_end

### Model Configuration (Matching Colab)

- `n_estimators`: 1000
- `learning_rate`: 0.01
- `max_depth`: 7
- `min_child_weight`: 1
- `subsample`: 0.8
- `colsample_bytree`: 0.8
- `early_stopping_rounds`: 50

## Usage Examples

### Basic Forecast
```python
from backend.app.modules.ml_xgboost.service import XGBoostForecastService

service = XGBoostForecastService()
result = service.forecast(
    drug_code="P733036",
    forecast_days=14,
    test_size=30
)
```

### With Date Range
```python
from datetime import date, timedelta

end_date = date.today()
start_date = end_date - timedelta(days=365)

result = service.forecast(
    drug_code="P733036",
    forecast_days=14,
    start_date=start_date,
    end_date=end_date
)
```

## Differences from Colab Script

1. **Data Source**: Reads from PostgreSQL via `AnalyticsDAL` instead of Excel
2. **Data Format**: Already aggregated daily, converted to pandas DataFrame
3. **Target Variable**: Uses `quantity` from database (mapped to `QTY` internally)
4. **Modular Structure**: Split into separate files instead of one script

## Integration

The module is automatically registered when the Flask app starts. No additional configuration needed.

## Health Check

```bash
curl "http://localhost:5000/api/ml-xgboost/health"
```

## Notes

- The module is completely separate from the existing `ml` module
- Uses pandas DataFrame (not Polars) to match Colab script exactly
- All feature engineering matches the Colab script implementation
- Model hyperparameters match the Colab script configuration

