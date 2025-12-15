# Colab Script to Backend Migration Plan

## Overview
This plan adapts the Colab XGBoost time-series forecasting script to work with the backend PostgreSQL database in a modular, production-ready structure.

## Key Differences from Colab Script

1. **Data Source**: 
   - Colab: Excel file (`/content/drive/MyDrive/Pharma/2019.xlsx`)
   - Backend: PostgreSQL database via `AnalyticsDAL.get_drug_demand_time_series()`

2. **Data Format**:
   - Colab: Reads raw Excel, cleans DATE column, resamples to daily
   - Backend: Already aggregated daily via SQL query, returns list of dicts

3. **Target Variable**:
   - Colab: `QTY` column from Excel
   - Backend: `quantity` field from database (already ABS and filtered for negative quantities)

4. **Structure**:
   - Colab: Single script with all steps
   - Backend: Modular components following existing architecture

---

## Implementation Plan

### Phase 1: Enhanced Feature Engineering Module
**File**: `backend/app/modules/ml/features/xgboost_features.py` (NEW)

**Purpose**: Create comprehensive feature engineering matching Colab script

**Functions to implement**:
1. `create_time_features()` - Basic time features (hour, dayofweek, quarter, month, year, dayofyear, dayofmonth, weekofyear)
2. `create_cyclical_features()` - Sin/cos encoding for periodic features (dayofweek, month, dayofyear)
3. `create_lag_features()` - Lag features for [1, 2, 3, 7, 14, 21, 30] days
4. `create_rolling_features()` - Rolling stats (mean, std, min, max) for windows [7, 14, 30]
5. `create_difference_features()` - diff_1, diff_7
6. `create_binary_features()` - is_weekend, is_month_start, is_month_end, is_quarter_start, is_quarter_end
7. `prepare_features()` - Master function that combines all features

**Note**: Use pandas DataFrame (not Polars) to match Colab script exactly, then convert to numpy arrays for XGBoost.

---

### Phase 2: Enhanced XGBoost Forecaster
**File**: `backend/app/modules/ml/models/xgboost_forecaster.py` (NEW)

**Purpose**: XGBoost model wrapper matching Colab configuration

**Class**: `XGBoostForecaster`

**Methods**:
1. `__init__(**params)` - Initialize with hyperparameters matching Colab:
   - `n_estimators=1000`
   - `learning_rate=0.01`
   - `max_depth=7`
   - `min_child_weight=1`
   - `subsample=0.8`
   - `colsample_bytree=0.8`
   - `random_state=42`
   - `n_jobs=-1`
   - `eval_metric=['rmse', 'mae']`
   - `early_stopping_rounds=50`

2. `train(X_train, y_train, X_val=None, y_val=None)` - Train with eval_set support
3. `predict(X)` - Generate predictions
4. `get_feature_importance()` - Return feature importance as dict
5. `get_eval_results()` - Return training history (RMSE over rounds)

**Note**: Keep existing `demand_forecast.py` for backward compatibility, create new file for Colab-style implementation.

---

### Phase 3: Evaluation Utilities
**File**: `backend/app/modules/ml/utils/evaluation.py` (NEW)

**Purpose**: Calculate evaluation metrics matching Colab script

**Functions**:
1. `calculate_metrics(y_true, y_pred)` - Returns RMSE, MAE, MAPE
2. `create_results_dataframe(y_test, y_pred, dates)` - Create results DataFrame
3. `calculate_confidence_intervals(errors, predictions)` - Calculate 95% CI using error std

---

### Phase 4: Data Preparation Service
**File**: `backend/app/modules/ml/utils/data_preparation.py` (NEW)

**Purpose**: Convert database data to pandas DataFrame format matching Colab

**Functions**:
1. `load_and_prepare_data(drug_code, start_date, end_date)` - Load from DB, convert to pandas DataFrame
2. `resample_to_daily(df, target_col='quantity')` - Resample to daily frequency (handle missing dates)
3. `handle_missing_values(daily_data)` - Forward fill zeros/missing values
4. `create_train_test_split(features_df, test_size=30)` - Time-aware split (last N days for test)

---

### Phase 5: Future Forecast Generator
**File**: `backend/app/modules/ml/utils/forecast_generator.py` (NEW)

**Purpose**: Generate features for future dates (matching Colab's `create_future_features`)

**Functions**:
1. `create_future_features(last_date, periods=14, feature_columns)` - Create features for future dates
2. `iterative_forecast(model, historical_data, periods)` - For production: iterative prediction with lag updates

**Note**: Colab version sets lag/rolling features to 0 for future dates. We'll do the same initially, but note that iterative forecasting would be better for production.

---

### Phase 6: Enhanced ML Service
**File**: `backend/app/modules/ml/services.py` (UPDATE)

**Purpose**: Orchestrate the complete pipeline

**New Method**: `xgboost_forecast_pipeline()`

**Steps**:
1. Load data from database using `MLDataLoader`
2. Convert to pandas DataFrame
3. Resample to daily and handle missing values
4. Create features using `xgboost_features.prepare_features()`
5. Train-test split (last 30 days for test)
6. Train XGBoost model
7. Evaluate on test set
8. Generate future forecast (14 days)
9. Format results for API response

**Response Format**:
```python
{
    "drug_code": "P733036",
    "historical": [...],  # Full historical data
    "test_predictions": [...],  # Test set predictions with actuals
    "forecast": [...],  # Future forecast (14 days)
    "metrics": {
        "rmse": 45.2,
        "mae": 38.5,
        "mape": 12.3
    },
    "feature_importance": {...},
    "training_history": {
        "train_rmse": [...],
        "val_rmse": [...]
    }
}
```

---

### Phase 7: API Routes
**File**: `backend/app/modules/ml/routes.py` (UPDATE)

**New Endpoint**: `GET /api/ml/forecast-xgboost/<drug_code>`

**Query Parameters**:
- `forecast_days`: int (default: 14)
- `test_size`: int (default: 30) - Days to use for testing
- `lookback_days`: int (default: None) - Limit historical data

**Response**: JSON matching service response format

---

## File Structure

```
backend/app/modules/ml/
├── __init__.py
├── routes.py                    # UPDATE: Add xgboost endpoint
├── services.py                  # UPDATE: Add xgboost_forecast_pipeline()
├── features/
│   ├── __init__.py
│   ├── time_features.py        # EXISTING: Keep for backward compat
│   └── xgboost_features.py      # NEW: Colab-style feature engineering
├── models/
│   ├── __init__.py
│   ├── demand_forecast.py       # EXISTING: Keep for backward compat
│   └── xgboost_forecaster.py   # NEW: Colab-style XGBoost wrapper
└── utils/
    ├── __init__.py
    ├── data_loader.py           # EXISTING: Keep as is
    ├── data_preparation.py      # NEW: DB → pandas conversion
    ├── evaluation.py            # NEW: Metrics calculation
    └── forecast_generator.py    # NEW: Future forecast features
```

---

## Implementation Order

1. ✅ **Phase 3: Evaluation Utilities** - Simple, no dependencies
2. ✅ **Phase 1: Feature Engineering** - Core functionality
3. ✅ **Phase 2: XGBoost Forecaster** - Model wrapper
4. ✅ **Phase 4: Data Preparation** - DB integration
5. ✅ **Phase 5: Forecast Generator** - Future predictions
6. ✅ **Phase 6: ML Service** - Orchestration
7. ✅ **Phase 7: API Routes** - Expose endpoint

---

## Key Implementation Notes

### Data Conversion
- Database returns list of dicts: `[{'date': date, 'quantity': int}, ...]`
- Convert to pandas DataFrame with `date` as index
- Ensure date column is `pd.DatetimeIndex`

### Feature Engineering
- Match Colab script exactly:
  - Same lag periods: [1, 2, 3, 7, 14, 21, 30]
  - Same rolling windows: [7, 14, 30]
  - Same cyclical encoding (sin/cos)
  - Same binary features

### Model Configuration
- Use exact hyperparameters from Colab script
- Support `eval_set` for training history
- Return `evals_result()` for visualization

### Missing Data Handling
- Colab: `daily_data.replace(0, np.nan).ffill()`
- Backend: Apply same logic after resampling

### Train-Test Split
- Colab: Last 30 days for test
- Backend: Make configurable via parameter

### Future Forecast
- Colab: Creates features without lag/rolling (sets to 0)
- Backend: Same approach initially, note iterative method for production

---

## Testing Strategy

1. **Unit Tests**: Each module independently
2. **Integration Test**: Full pipeline with sample drug_code
3. **Validation**: Compare results with Colab output (same drug_code, same date range)

---

## Dependencies

All required packages already in `requirements.txt`:
- ✅ pandas (for DataFrame operations)
- ✅ numpy (for numerical operations)
- ✅ xgboost (for model)
- ✅ scikit-learn (for metrics)

---

## Next Steps

1. Review and approve this plan
2. Start with Phase 3 (evaluation utilities) - simplest first
3. Implement phases sequentially
4. Test each phase before moving to next
5. Compare results with Colab output for validation

---

## Questions to Resolve

1. **Model Persistence**: Save trained models? Where? (suggest: `data/models/`)
2. **Caching**: Cache feature-engineered data? (suggest: No initially, keep it simple)
3. **Error Handling**: What if insufficient data? (suggest: Raise ValueError with clear message)
4. **Performance**: Limit historical data? (suggest: Configurable via `lookback_days`)
5. **Visualization**: Return raw data for frontend charts? (suggest: Yes, match existing dashboard format)

