# Drug Demand Forecasting - Prediction Task Summary

## Executive Summary

You are building a **time-series forecasting system** to predict future drug demand (quantity dispensed) for specific pharmaceutical drugs in your hospital. This prediction will help optimize inventory management, prevent stockouts, and improve procurement planning.

---

## 1. What Are You Predicting?

### Prediction Target
**Daily drug demand** - The quantity of a specific drug that will be dispensed to patients on future dates.

### Key Details
- **Target Variable**: `demand` (daily aggregated quantity dispensed)
- **Unit**: Number of units/items dispensed per day
- **Granularity**: Daily predictions (can aggregate to weekly/monthly if needed)
- **Forecast Horizon**: 7, 14, or 30 days ahead (configurable)
- **Scope**: Per drug code (e.g., predict demand for drug "P733036")

### Example Prediction
```
For drug code "P733036":
- Today: January 15, 2024
- Prediction: Next 30 days of daily demand
- Output: 
  - Jan 16: 480 units
  - Jan 17: 495 units
  - Jan 18: 510 units
  - ... (30 days total)
```

---

## 2. Why Is This Prediction Important?

### Business Value
1. **Inventory Management**: Prevent stockouts by ordering the right quantity in advance
2. **Cost Optimization**: Avoid overstocking (waste) and understocking (emergency orders)
3. **Procurement Planning**: Schedule purchases based on predicted demand
4. **Budget Allocation**: Plan budgets for future periods accurately
5. **Operational Efficiency**: Reduce manual forecasting effort

### Use Cases
- **Pharmacy Manager**: "How much of Drug X should I order for next month?"
- **Procurement Team**: "When should we place orders to avoid stockouts?"
- **Finance Team**: "What's our expected drug expenditure for Q2?"
- **Inventory System**: Automatic reorder point calculations

---

## 3. What Data Are You Using?

### Historical Data Source
Your **4-year pharmaceutical transaction database** containing:
- **Time Range**: 4 years of historical transactions (2019-2023 approximately)
- **Data Source**: `drug_transactions` table in PostgreSQL
- **Key Fields**:
  - `transaction_date`: When the transaction occurred
  - `drug_code`: Unique identifier for each drug
  - `quantity`: Amount dispensed (negative values = dispensed to patients)
  - `drug_name`: Name of the drug
  - `cat`: Drug category
  - `cr`: Consuming department
  - `unit_price`, `total_price`: Pricing information

### Data Preparation
- **Aggregation**: Daily aggregation of `quantity` (sum of all transactions per day)
- **Filtering**: Only negative quantities (dispensed to patients, not received)
- **Time Series Format**: 
  ```
  Date       | Drug Code | Demand (quantity)
  2023-01-01 | P733036   | 450
  2023-01-02 | P733036   | 520
  2023-01-03 | P733036   | 480
  ...
  ```

### Data Access
- **Method**: `AnalyticsDAL.get_drug_demand_time_series()`
- **Parameters**: 
  - `drug_code`: Specific drug to forecast
  - `start_date`, `end_date`: Date range
  - `granularity`: 'daily', 'weekly', or 'monthly'

---

## 4. How Does the Prediction Work?

### Methodology: XGBoost Time-Series Forecasting

Following the **Kaggle notebook approach** (https://www.kaggle.com/code/robikscube/time-series-forecasting-with-machine-learning-yt), you're using **XGBoost** (gradient-boosted decision trees) adapted for time-series prediction.

### Step-by-Step Process

#### Step 1: Feature Engineering
Transform historical demand into features that help the model learn patterns:

**Lag Features** (Previous time steps):
- `lag_1`: Demand 1 day ago
- `lag_7`: Demand 7 days ago (weekly pattern)
- `lag_14`: Demand 14 days ago
- `lag_30`: Demand 30 days ago (monthly pattern)

**Rolling Window Statistics** (Moving averages):
- `rolling_mean_7`: 7-day moving average
- `rolling_mean_14`: 14-day moving average
- `rolling_mean_30`: 30-day moving average
- `rolling_std_7`: 7-day standard deviation
- `rolling_max_7`, `rolling_min_7`: Min/max over 7 days

**Time-Based Features** (Calendar patterns):
- `day_of_week`: 1-7 (Monday-Sunday)
- `day_of_month`: 1-31
- `month`: 1-12
- `quarter`: 1-4
- `year`: Year value
- `is_weekend`: 0 or 1
- `is_month_start`, `is_month_end`: 0 or 1

**Total Features**: ~25 features per prediction

#### Step 2: Train/Test Split
- **Training Set**: First 80% of chronological data (earlier dates)
- **Test Set**: Last 20% of chronological data (later dates)
- **Critical**: Preserve temporal order (no shuffling) to avoid look-ahead bias

#### Step 3: Model Training
- **Algorithm**: XGBoost Regressor
- **Hyperparameters**:
  - `n_estimators`: 100 trees
  - `max_depth`: 6 levels
  - `learning_rate`: 0.1
  - `subsample`: 0.8 (row sampling)
  - `colsample_bytree`: 0.8 (feature sampling)
- **Training**: Model learns relationship between features and future demand

#### Step 4: Evaluation
Calculate performance metrics on test set:
- **RMSE** (Root Mean Squared Error): Average prediction error
- **MAE** (Mean Absolute Error): Average absolute error
- **MAPE** (Mean Absolute Percentage Error): Percentage error
- **R² Score**: How well model fits the data (0-1, higher is better)

#### Step 5: Future Forecasting
- **Multi-step Ahead**: Predict next N days iteratively
- **Method**: Use previous predictions to create features for next day
- **Output**: Daily demand predictions for future dates

---

## 5. What Does the Output Look Like?

### API Response Structure

```json
{
  "success": true,
  "data": {
    "drug_code": "P733036",
    "method": "xgboost",
    
    // Complete timeline: Historical + Forecast
    "timeline": [
      {
        "date": "2023-01-01",
        "actual": 450,
        "type": "historical"
      },
      {
        "date": "2024-01-15",
        "actual": null,
        "predicted": 480,
        "type": "forecast",
        "confidence_lower": 420,
        "confidence_upper": 540
      }
    ],
    
    // Test set: Actual vs Predicted (for evaluation)
    "test_predictions": [
      {
        "date": "2023-12-01",
        "actual": 500,
        "predicted": 485,
        "error": 15,
        "error_percent": 3.0
      }
    ],
    
    // Future forecast only
    "forecast": [
      {
        "date": "2024-01-16",
        "predicted": 495,
        "confidence_lower": 435,
        "confidence_upper": 555
      }
    ],
    
    // Model performance metrics
    "metrics": {
      "rmse": 45.2,
      "mae": 38.5,
      "mape": 12.3,
      "r2": 0.85
    },
    
    // Feature importance (which features matter most)
    "feature_importance": [
      {
        "feature": "demand_lag_7d",
        "importance": 0.25,
        "rank": 1
      },
      {
        "feature": "rolling_mean_7d",
        "importance": 0.18,
        "rank": 2
      }
    ]
  }
}
```

---

## 6. How Will It Be Visualized?

### Chart Types (Kaggle Notebook Style)

#### 1. **Main Forecast Chart** (Timeline)
- **Type**: Line chart with dual series
- **Data**: `timeline` array
- **Visualization**:
  - **Historical data**: Solid blue line with markers
  - **Forecast data**: Dashed orange line with markers
  - **Confidence interval**: Shaded area (light orange, semi-transparent)
  - **Split point**: Vertical line separating historical from forecast
- **Purpose**: Show complete picture - past performance + future predictions

#### 2. **Test Set Comparison Chart**
- **Type**: Dual line chart
- **Data**: `test_predictions` array
- **Visualization**:
  - **Actual**: Blue line
  - **Predicted**: Orange line
- **Purpose**: Evaluate model accuracy on unseen data

#### 3. **Feature Importance Chart**
- **Type**: Horizontal bar chart
- **Data**: `feature_importance` array
- **Visualization**: Bars sorted by importance (highest first)
- **Purpose**: Understand which features drive predictions (e.g., weekly patterns vs monthly)

#### 4. **Metrics Display**
- **Type**: KPI cards or table
- **Data**: `metrics` object
- **Visualization**: 
  - RMSE, MAE, MAPE, R² as cards
  - Color-coded by performance (green = good, red = needs improvement)
- **Purpose**: Quick assessment of model quality

#### 5. **Residuals Plot** (Optional)
- **Type**: Scatter plot
- **Data**: `residuals` array
- **Visualization**: Date vs prediction error
- **Purpose**: Identify patterns in errors (e.g., model struggles on weekends)

### Frontend Implementation
- **Library**: Recharts or Chart.js (React-compatible)
- **Component**: `<ForecastChart>` component
- **Integration**: Use existing dashboard chart infrastructure

---

## 7. Technical Requirements

### Data Requirements
- **Minimum Historical Data**: 60+ days (for lag_30 + rolling features)
- **Recommended**: 365+ days (1 year) for better patterns
- **Maximum**: Use all available 4 years

### Model Requirements
- **Algorithm**: XGBoost (gradient-boosted trees)
- **Dependencies**: 
  - `xgboost==2.0.3`
  - `scikit-learn==1.4.0`
  - `numpy==1.26.4`
  - `pandas==2.1.4` (for feature engineering)
- **Training Time**: ~1-5 seconds per drug (depending on data size)

### API Endpoint
```
GET /api/ml/forecast/{drug_code}?method=xgboost&forecast_days=30&train_test_split=0.8
```

**Query Parameters**:
- `method`: 'simple' (moving average) or 'xgboost' (ML model)
- `forecast_days`: Number of days to predict (default: 30)
- `train_test_split`: Ratio for train/test split (default: 0.8)
- `lookback_days`: Historical data to use (default: 365)

---

## 8. Success Criteria

### Model Performance Targets
- **MAPE < 15%**: Excellent prediction accuracy
- **MAPE < 20%**: Good prediction accuracy
- **MAPE < 30%**: Acceptable for planning purposes
- **R² > 0.7**: Model explains most variance in data

### Business Success
- ✅ Predictions help prevent stockouts
- ✅ Inventory levels optimized (not over/under stocked)
- ✅ Procurement decisions improved
- ✅ Forecasts trusted by pharmacy staff

---

## 9. Example Use Case

### Scenario: Forecasting Drug "P733036" for Next Month

**Input**:
- Drug code: "P733036"
- Today: January 15, 2024
- Forecast horizon: 30 days

**Process**:
1. Load historical data (last 365 days)
2. Create features (lag, rolling, time features)
3. Split: Train on Jan 2023 - Dec 2023, Test on Jan 2024
4. Train XGBoost model
5. Evaluate: MAPE = 12.3% (good accuracy)
6. Forecast: Jan 16 - Feb 15, 2024

**Output**:
- Daily predictions for next 30 days
- Average predicted demand: ~485 units/day
- Confidence interval: ±60 units (80% confidence)
- Key insight: Higher demand on weekdays (Monday-Friday)

**Action**:
- Pharmacy manager orders 15,000 units for February
- Based on prediction: 485 units/day × 30 days = 14,550 units
- Order includes 3% safety margin = 15,000 units

---

## 10. Next Steps

1. **Implement Feature Engineering**: Create lag, rolling, and time features
2. **Implement XGBoost Model**: Train and evaluate model
3. **Build Forecasting Pipeline**: End-to-end prediction workflow
4. **Add Visualization Support**: Format response for charts
5. **Test with Real Data**: Validate on actual drug codes
6. **Deploy to Production**: Make available via API endpoint

---

## Summary

You are predicting **daily drug demand** for specific pharmaceutical drugs using **XGBoost machine learning** on **4 years of historical transaction data**. The predictions help optimize inventory, prevent stockouts, and improve procurement planning. The output includes future forecasts, model performance metrics, and feature importance, all formatted for visualization in charts similar to Kaggle notebook style.

**Key Takeaway**: This is a **time-series forecasting problem** solved with **supervised machine learning** (XGBoost), where historical patterns in drug demand are used to predict future demand.

