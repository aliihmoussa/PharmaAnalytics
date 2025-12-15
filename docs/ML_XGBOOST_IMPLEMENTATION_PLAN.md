# XGBoost Time-Series Forecasting - Implementation Plan

## Overview
This plan follows the YouTube tutorial steps (https://www.youtube.com/watch?v=vV12dGe_Fho) adapted for pharmaceutical drug demand forecasting.

---

## Step-by-Step Implementation Plan

### Step 1: Problem Setup & Data Understanding ✅

**Goal**: Predict future drug demand based on historical transaction patterns

**Your Data**:
- **Time Series**: Daily drug demand (quantity dispensed) over 4 years
- **Target Variable**: `quantity` (negative values = dispensed to patients)
- **Forecasting Goal**: Predict next 7/14/30 days of demand for a specific drug

**Current Status**: ✅ Data already loaded via `AnalyticsDAL.get_drug_demand_time_series()`

**Action Items**:
- [x] Data source identified (PostgreSQL via AnalyticsDAL)
- [x] Time series format understood (daily aggregations)
- [ ] Add data exploration/statistics endpoint

---

### Step 2: Preprocessing & Feature Engineering 🔄

**What to Build**:

#### 2.1 Lag Features (Previous Time Steps)
- `lag_1`: Demand 1 day ago
- `lag_7`: Demand 7 days ago (weekly pattern)
- `lag_14`: Demand 14 days ago
- `lag_30`: Demand 30 days ago (monthly pattern)

#### 2.2 Rolling Window Features
- `rolling_mean_7`: 7-day moving average
- `rolling_mean_14`: 14-day moving average
- `rolling_mean_30`: 30-day moving average
- `rolling_std_7`: 7-day standard deviation

#### 2.3 Calendar-Based Features
- `day_of_week`: 1-7 (Monday-Sunday)
- `day_of_month`: 1-31
- `month`: 1-12
- `quarter`: 1-4
- `is_weekend`: 0 or 1
- `is_month_start`: 0 or 1
- `is_month_end`: 0 or 1

**Implementation Location**: `backend/app/modules/ml/features/feature_engineering.py` (NEW)

---

### Step 3: Train/Test Split for Time Series ✅

**Critical**: Use time-aware split (preserve temporal order)

**Split Strategy**:
- **Training**: First 80% of chronological data
- **Test**: Last 20% of chronological data
- **No shuffling**: Maintain time order to avoid look-ahead bias

**Implementation**:
```python
# Sort by date first
df = df.sort('date')

# Time-aware split
split_idx = int(len(df) * 0.8)
train_df = df[:split_idx]
test_df = df[split_idx:]
```

---

### Step 4: Model Training (XGBoost) 🔄

**XGBoost Configuration**:
```python
XGBRegressor(
    n_estimators=100,      # Number of trees
    max_depth=6,            # Tree depth
    learning_rate=0.1,      # Step size
    subsample=0.8,          # Row sampling
    colsample_bytree=0.8,   # Feature sampling
    random_state=42
)
```

**Hyperparameter Tuning** (Optional):
- Grid search or random search
- Focus on: `n_estimators`, `max_depth`, `learning_rate`

**Implementation Location**: `backend/app/modules/ml/models/xgboost_forecaster.py` (NEW)

---

### Step 5: Evaluation & Forecasting 🔄

**Metrics to Calculate**:
- **RMSE** (Root Mean Squared Error)
- **MAE** (Mean Absolute Error)
- **MAPE** (Mean Absolute Percentage Error)
- **R² Score** (Coefficient of determination)

**Forecasting**:
- Generate predictions for test period
- Generate out-of-sample forecasts for future dates
- Include confidence intervals (optional)

**Implementation**: Add to service layer

---

### Step 6: Visualization 📊

**Plots to Generate**:
1. **Historical vs Predicted** (on test set)
2. **Forecast vs Actual** (future predictions)
3. **Residuals Plot** (errors over time)
4. **Feature Importance** (which features matter most)

**Implementation**: 
- Return data in format ready for frontend charts
- Use existing dashboard chart infrastructure

---

## Implementation Structure

```
backend/app/modules/ml/
├── __init__.py
├── routes.py                    # API endpoints
├── services.py                  # Main forecasting service
├── features/
│   └── feature_engineering.py  # Step 2: Feature creation
├── models/
│   └── xgboost_forecaster.py   # Step 4: XGBoost model
└── utils/
    └── evaluation.py           # Step 5: Metrics calculation
```

---

## Detailed Implementation Steps

### Phase 1: Feature Engineering (Step 2)

**File**: `backend/app/modules/ml/features/feature_engineering.py`

```python
def create_lag_features(df, target_col='demand', lags=[1, 7, 14, 30]):
    """Create lag features from previous time steps"""
    pass

def create_rolling_features(df, target_col='demand', windows=[7, 14, 30]):
    """Create rolling window statistics"""
    pass

def create_calendar_features(df, date_col='date'):
    """Create calendar-based temporal features"""
    pass

def prepare_features(df, target_col='demand', date_col='date'):
    """Combine all feature engineering steps"""
    pass
```

### Phase 2: XGBoost Model (Step 4)

**File**: `backend/app/modules/ml/models/xgboost_forecaster.py`

```python
class XGBoostForecaster:
    def __init__(self, **params):
        """Initialize with hyperparameters"""
        pass
    
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """Train XGBoost model"""
        pass
    
    def predict(self, X):
        """Generate predictions"""
        pass
    
    def evaluate(self, X_test, y_test):
        """Calculate evaluation metrics"""
        pass
```

### Phase 3: Service Integration (Steps 1-6)

**File**: `backend/app/modules/ml/services.py`

```python
def xgboost_forecast(self, drug_code, forecast_days=30):
    """
    Complete XGBoost forecasting pipeline:
    1. Load data
    2. Create features
    3. Train/test split
    4. Train model
    5. Evaluate
    6. Forecast future
    """
    pass
```

---

## API Endpoints

### GET /api/ml/forecast/{drug_code}

**Query Parameters**:
- `forecast_days`: int (default: 30)
- `method`: str (default: 'xgboost')
- `train_test_split`: float (default: 0.8)

**Response**:
```json
{
  "data": {
    "drug_code": "P733036",
    "historical": [...],
    "forecast": [...],
    "test_predictions": [...],
    "metrics": {
      "rmse": 45.2,
      "mae": 38.5,
      "mape": 12.3,
      "r2": 0.85
    },
    "feature_importance": {...}
  }
}
```

---

## Testing Checklist

- [ ] Feature engineering creates correct lag features
- [ ] Train/test split preserves temporal order
- [ ] XGBoost model trains without errors
- [ ] Metrics are calculated correctly
- [ ] Forecasts are generated for future dates
- [ ] API returns data in correct format

---

## Next Steps

1. **Start with Feature Engineering** (Step 2)
   - Create `feature_engineering.py`
   - Implement lag, rolling, and calendar features
   - Test with sample data

2. **Add XGBoost Model** (Step 4)
   - Create `xgboost_forecaster.py`
   - Implement training and prediction
   - Add hyperparameter support

3. **Integrate into Service** (Steps 1-6)
   - Update `services.py` with full pipeline
   - Add evaluation metrics
   - Format response for visualization

4. **Add Visualization Support** (Step 6)
   - Return chart-ready data
   - Add feature importance endpoint

---

## Questions to Discuss

1. **Data Requirements**: Minimum days needed? (suggest: 60+ days)
2. **Forecast Horizon**: Default 30 days? Configurable?
3. **Feature Selection**: Which lags/windows work best for your data?
4. **Model Persistence**: Save trained models? Retrain schedule?
5. **Evaluation**: Show test metrics in API response?

---

**Ready to start implementation?** Let's begin with Step 2 (Feature Engineering)!

