# ML Module Quick Start Guide

## Overview

This guide provides a practical starting point for implementing prediction models in the PharmaAnalytics ML module.

## Recommended Starting Point: Drug Demand Forecasting

Based on your 4-year dataset, **Drug Demand Forecasting** is the most valuable and straightforward model to implement first.

## Step 1: Install Required Dependencies

Add to `requirements.txt`:

```txt
# Machine Learning
scikit-learn==1.4.0
xgboost==2.0.3
lightgbm==4.1.0

# Time Series Forecasting
prophet==1.1.5
statsmodels==0.14.1
pmdarima==2.0.4

# Anomaly Detection
pyod==1.1.2

# Model Management
joblib==1.3.2  # For model serialization
```

## Step 2: Module Structure

```
backend/app/modules/ml/
├── __init__.py
├── routes.py              # API endpoints
├── services.py            # Business logic
├── models/                # ML model implementations
│   ├── __init__.py
│   ├── demand_forecast.py # Drug demand forecasting
│   ├── anomaly_detector.py
│   └── price_predictor.py
├── features/              # Feature engineering
│   ├── __init__.py
│   ├── time_features.py
│   └── aggregations.py
├── training/              # Model training utilities
│   ├── __init__.py
│   ├── trainer.py
│   └── evaluator.py
└── utils/                 # Helper functions
    ├── __init__.py
    └── data_loader.py
```

## Step 3: Basic Implementation Example

### Feature Engineering

Create time-based features from your transaction data:

```python
# features/time_features.py
from datetime import datetime, timedelta
import polars as pl

def create_time_features(df: pl.DataFrame, date_col: str = 'transaction_date'):
    """Create time-based features for forecasting."""
    df = df.with_columns([
        pl.col(date_col).dt.weekday().alias('day_of_week'),
        pl.col(date_col).dt.month().alias('month'),
        pl.col(date_col).dt.quarter().alias('quarter'),
        pl.col(date_col).dt.year().alias('year'),
        (pl.col(date_col).dt.weekday() >= 5).alias('is_weekend'),
    ])
    return df

def create_lag_features(df: pl.DataFrame, value_col: str, date_col: str, lags: list = [7, 14, 30, 90]):
    """Create lag features for time series."""
    df = df.sort(date_col)
    for lag in lags:
        df = df.with_columns(
            pl.col(value_col).shift(lag).alias(f'{value_col}_lag_{lag}')
        )
    return df

def create_rolling_features(df: pl.DataFrame, value_col: str, windows: list = [7, 14, 30]):
    """Create rolling statistics."""
    for window in windows:
        df = df.with_columns([
            pl.col(value_col).rolling_mean(window).alias(f'{value_col}_mean_{window}d'),
            pl.col(value_col).rolling_std(window).alias(f'{value_col}_std_{window}d'),
        ])
    return df
```

### Data Preparation

**Note**: This uses direct PostgreSQL access, which is appropriate for your current setup. See `ML_DATA_ACCESS_STRATEGY.md` for detailed discussion.

```python
# utils/data_loader.py
from backend.app.modules.dashboard.queries import AnalyticsDAL
import polars as pl
from datetime import date, timedelta
from typing import Optional

class MLDataLoader:
    """
    Load ML training data directly from PostgreSQL.
    Reuses existing optimized queries from AnalyticsDAL.
    """
    
    def __init__(self):
        self.dal = AnalyticsDAL()
    
    def load_demand_data(
        self,
        drug_code: Optional[str] = None,
        department: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        training_months: int = 24,  # Limit to recent data for performance
        granularity: str = 'daily'  # 'daily', 'weekly', 'monthly'
    ) -> pl.DataFrame:
        """
        Load and aggregate transaction data for forecasting.
        
        Optimizations:
        - Uses existing indexed queries from AnalyticsDAL
        - Limits training window (default: 24 months)
        - Aggregates at database level
        """
        # Set defaults
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=training_months * 30)
        
        with self.dal:
            # Use existing optimized query (already aggregates efficiently)
            raw_data = self.dal.get_drug_demand_time_series(
                start_date=start_date,
                end_date=end_date,
                drug_code=drug_code,
                granularity=granularity
            )
        
        if not raw_data:
            return pl.DataFrame()
        
        # Convert to Polars DataFrame
        df = pl.DataFrame(raw_data)
        
        # Ensure date column is proper date type
        if 'date' in df.columns:
            # Handle different date formats
            if df['date'].dtype == pl.Utf8:
                # Try parsing different formats
                try:
                    df = df.with_columns(
                        pl.col('date').str.strptime(pl.Date, format="%Y-%m-%d")
                    )
                except:
                    # Fallback to other formats if needed
                    df = df.with_columns(
                        pl.col('date').str.strptime(pl.Date, format="%Y-%m-%d %H:%M:%S")
                    )
            df = df.sort('date')
        
        # Rename columns for consistency
        if 'quantity' in df.columns:
            df = df.rename({'quantity': 'demand'})
        
        return df
```

### Model Implementation

```python
# models/demand_forecast.py
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import joblib
from typing import Dict, List
import numpy as np

class DrugDemandForecaster:
    """Forecast drug demand using machine learning."""
    
    def __init__(self, model_type: str = 'xgboost'):
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """Train the forecasting model."""
        if self.model_type == 'xgboost':
            self.model = XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        elif self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        
        self.model.fit(X_train, y_train)
        self.feature_names = X_train.columns if hasattr(X_train, 'columns') else None
        
        if X_val is not None:
            val_score = self.model.score(X_val, y_val)
            print(f"Validation R² Score: {val_score:.4f}")
    
    def predict(self, X) -> np.ndarray:
        """Generate demand predictions."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        return self.model.predict(X)
    
    def save(self, filepath: str):
        """Save model to disk."""
        joblib.dump({
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names
        }, filepath)
    
    @classmethod
    def load(cls, filepath: str):
        """Load model from disk."""
        data = joblib.load(filepath)
        forecaster = cls(model_type=data['model_type'])
        forecaster.model = data['model']
        forecaster.feature_names = data['feature_names']
        return forecaster
```

### Service Layer

```python
# services.py
from backend.app.shared.base_service import BaseService
from backend.app.modules.ml.models.demand_forecast import DrugDemandForecaster
from backend.app.modules.ml.utils.data_loader import MLDataLoader
from backend.app.modules.ml.features.time_features import (
    create_time_features,
    create_lag_features,
    create_rolling_features
)
from datetime import date, timedelta
import polars as pl
import numpy as np
from typing import Dict

class MLService(BaseService):
    """Service for ML predictions."""
    
    def __init__(self):
        """Initialize ML service with data loader."""
        super().__init__()
        self.data_loader = MLDataLoader()
    
    def forecast_drug_demand(
        self,
        drug_code: str,
        forecast_horizon_days: int = 30,
        training_months: int = 24
    ) -> Dict:
        """
        Forecast drug demand for specified horizon.
        
        Uses direct PostgreSQL access via optimized queries.
        """
        # Load historical data from PostgreSQL
        df = self.data_loader.load_demand_data(
            drug_code=drug_code,
            training_months=training_months,
            granularity='daily'
        )
        
        if df.is_empty() or len(df) < 30:
            raise ValueError(f"Insufficient data for drug {drug_code}. Need at least 30 days.")
        
        # Feature engineering
        df = create_time_features(df, 'date')
        df = create_lag_features(df, 'demand', 'date', lags=[7, 14, 30])
        df = create_rolling_features(df, 'demand', windows=[7, 14, 30])
        
        # Prepare training data
        feature_cols = [col for col in df.columns if col not in ['date', 'drug_code', 'demand']]
        X = df.select(feature_cols).to_numpy()
        y = df['demand'].to_numpy()
        
        # Train/test split (temporal - CRITICAL for time series!)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Train model
        forecaster = DrugDemandForecaster(model_type='xgboost')
        forecaster.train(X_train, y_train, X_test, y_test)
        
        # Generate forecasts
        # Use the last available features to predict future
        last_features = X[-1:].reshape(1, -1)
        predictions = []
        
        for _ in range(forecast_horizon_days):
            pred = forecaster.predict(last_features)[0]
            predictions.append(max(0, pred))  # Ensure non-negative
        
        return {
            'drug_code': drug_code,
            'forecast_dates': [(date.today() + timedelta(days=i)).isoformat() 
                              for i in range(1, forecast_horizon_days + 1)],
            'forecasted_demand': predictions,
            'model_type': 'xgboost',
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
```

## Step 4: API Endpoints

```python
# routes.py
from flask import Blueprint, request, jsonify
from backend.app.modules.ml.services import MLService
from backend.app.modules.ml.requests import ForecastRequest
from pydantic import ValidationError

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')

@ml_bp.route('/forecast/demand', methods=['POST'])
def forecast_demand():
    """Forecast drug demand."""
    try:
        data = request.get_json()
        request_obj = ForecastRequest(**data)
        
        service = MLService()
        result = service.forecast_drug_demand(
            drug_code=request_obj.drug_code,
            forecast_horizon_days=request_obj.horizon_days,
            training_months=request_obj.training_months
        )
        
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Step 5: Testing Your First Model

1. **Load your data**: Ensure 4 years of data is ingested
2. **Identify top drugs**: Find most frequently dispensed drugs
3. **Test on one drug**: Start with a single drug code
4. **Evaluate**: Check forecast accuracy on historical data
5. **Iterate**: Adjust features and model parameters

## Next Steps

1. Implement the basic structure above
2. Test with a single drug (e.g., top 10 by volume)
3. Evaluate model performance
4. Add more sophisticated features
5. Expand to multiple drugs/categories
6. Implement model versioning and retraining

## Evaluation Checklist

- [ ] Model trains without errors
- [ ] Predictions are reasonable (non-negative, within expected range)
- [ ] Feature importance makes sense
- [ ] Validation metrics are acceptable (R² > 0.5, MAPE < 30%)
- [ ] Model generalizes to unseen data

## Common Issues & Solutions

**Issue**: Insufficient data
- **Solution**: Aggregate by week/month instead of daily

**Issue**: Poor predictions
- **Solution**: Add more features (lag, rolling stats, seasonal)

**Issue**: Model overfitting
- **Solution**: Reduce model complexity, add regularization

**Issue**: Slow training
- **Solution**: Use LightGBM instead of XGBoost, sample data

---

For detailed approaches, see `ML_PREDICTION_APPROACHES.md`.

