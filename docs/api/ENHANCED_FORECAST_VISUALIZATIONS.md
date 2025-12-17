# Enhanced Forecast API - Available Visualizations

## Summary

Based on the Enhanced Forecasting API response, you can create **5 main charts** plus **4 metric cards** for a complete dashboard.

---

## 📊 Available Charts & Visualizations

### 1. **Main Forecast Chart** (Primary - Required)
**Type**: Area/Line Chart with Confidence Intervals

**Data Sources**:
- `historical[]` - Historical actual demand
- `forecast[]` - Future predicted demand with confidence bounds
- `test_predictions[]` - Model validation data (optional overlay)

**What it shows**:
- Historical demand trend (blue solid line/area)
- Predicted future demand (orange dashed line)
- 95% confidence interval (shaded area)
- Test predictions overlay (shows model accuracy on recent data)

**Visual Elements**:
- **Historical Data**: Blue line/area showing actual past demand
- **Predicted Data**: Orange dashed line showing future forecast
- **Confidence Interval**: Shaded area between `lower` and `upper` bounds
- **Test Predictions**: Can overlay actual vs predicted for validation period

**Example**:
```
Historical: [2024-01-01 to 2024-11-15] - Blue solid line
Test: [2024-11-16 to 2024-12-15] - Blue dots (actual) + Orange dots (predicted)
Forecast: [2024-12-16 to 2025-01-15] - Orange dashed line + shaded confidence
```

---

### 2. **Feature Importance Chart** (Recommended)
**Type**: Horizontal Bar Chart

**Data Source**: `feature_importance{}` object

**What it shows**:
- Top 10-15 most important features that drive predictions
- Helps understand what factors influence demand most

**Visual Elements**:
- Horizontal bars sorted by importance (highest first)
- Shows feature names (e.g., "lag_7", "dept_demand_ratio", "category_trend")
- Importance scores (0-1 scale, higher = more important)

**Example Features**:
- `lag_7` - Demand 7 days ago
- `rolling_mean_7` - 7-day moving average
- `dept_demand_ratio` - Department demand patterns
- `category_trend` - Category-level trends
- `dayofweek` - Day of week patterns

---

### 3. **Model Training History Chart** (Optional)
**Type**: Line Chart

**Data Source**: `training_history{}` object

**What it shows**:
- Model training progress over epochs
- Training RMSE vs Validation RMSE
- Helps assess if model is overfitting

**Visual Elements**:
- Two lines: `train_rmse` and `val_rmse`
- X-axis: Training epochs/iterations
- Y-axis: RMSE values (lower is better)
- Shows convergence and overfitting patterns

---

### 4. **Prediction Error Distribution** (Optional)
**Type**: Histogram or Box Plot

**Data Source**: `test_predictions[].error` array

**What it shows**:
- Distribution of prediction errors
- Helps identify if errors are normally distributed
- Shows outliers and bias

**Visual Elements**:
- Histogram of error values
- Mean error line (should be near 0)
- Shows if model has systematic bias

---

### 5. **Actual vs Predicted Scatter Plot** (Optional)
**Type**: Scatter Plot

**Data Source**: `test_predictions[]` array

**What it shows**:
- Actual values vs Predicted values
- Perfect predictions would form a diagonal line
- Helps visualize model accuracy

**Visual Elements**:
- X-axis: Actual demand
- Y-axis: Predicted demand
- Diagonal reference line (perfect predictions)
- Points closer to line = better predictions

---

## 📈 Metric Cards (Not Charts, but Visual Elements)

### 6. **RMSE Card**
**Data**: `metrics.rmse`
**Display**: Large number with label "Root Mean Squared Error"
**Color**: Red if > 2.0, Yellow if 1.0-2.0, Green if < 1.0

### 7. **MAE Card**
**Data**: `metrics.mae`
**Display**: Large number with label "Mean Absolute Error"
**Color**: Red if > 1.5, Yellow if 0.5-1.5, Green if < 0.5

### 8. **MAPE Card**
**Data**: `metrics.mape`
**Display**: Large number with "%" and label "Mean Absolute % Error"
**Color**: Red if > 20%, Yellow if 10-20%, Green if < 10%

### 9. **R² Score Card**
**Data**: `metrics.r2`
**Display**: Large number with label "Model Accuracy (R²)"
**Color**: Red if < 0.5, Yellow if 0.5-0.7, Green if > 0.7

---

## 🎯 Recommended Dashboard Layout

### Minimal Demo (2 Charts + 4 Cards)
1. **Main Forecast Chart** - Shows historical + forecast
2. **Feature Importance Chart** - Shows what drives predictions
3. **4 Metric Cards** - RMSE, MAE, MAPE, R²

### Complete Dashboard (5 Charts + 4 Cards)
1. **Main Forecast Chart** - Primary visualization
2. **Feature Importance Chart** - Understanding model
3. **Training History Chart** - Model quality assessment
4. **Error Distribution Chart** - Error analysis
5. **Actual vs Predicted Scatter** - Accuracy visualization
6. **4 Metric Cards** - Quick metrics overview

---

## 📋 Data Structure Reference

### API Response Structure:
```json
{
  "drug_code": "P182054",
  "drug_name": "VANCO MEDIS 500MG VI",
  
  // Chart 1: Main Forecast
  "historical": [
    {"date": "2024-01-01", "demand": 5.0, "type": "actual"}
  ],
  "test_predictions": [
    {"date": "2024-11-15", "actual": 4.2, "predicted": 4.5, "error": 0.3}
  ],
  "forecast": [
    {"date": "2024-12-16", "predicted": 4.2, "lower": 3.1, "upper": 5.3}
  ],
  
  // Charts 2-5: Analysis
  "feature_importance": {
    "lag_7": 0.15,
    "rolling_mean_7": 0.12
  },
  "training_history": {
    "train_rmse": [2.5, 1.8, 1.2],
    "val_rmse": [2.8, 2.0, 1.4]
  },
  
  // Metric Cards
  "metrics": {
    "rmse": 0.85,
    "mae": 0.62,
    "mape": 15.3,
    "r2": 0.78
  }
}
```

---

## 🎨 Visual Design Recommendations

### Color Scheme:
- **Historical Data**: Blue (`#3b82f6`) - Solid, trustworthy
- **Predicted Data**: Orange (`#f59e0b`) - Attention-grabbing
- **Confidence Interval**: Orange with 20-30% opacity
- **Test Predictions**: Can use green for actual, orange for predicted
- **Metrics**: 
  - Green: Good performance
  - Yellow: Acceptable
  - Red: Needs improvement

### Chart Sizes:
- **Main Forecast Chart**: 800px width × 400-500px height (primary focus)
- **Feature Importance**: 600px width × 300px height
- **Training History**: 600px width × 300px height
- **Error Distribution**: 400px width × 300px height
- **Scatter Plot**: 400px width × 400px height (square)

---

## 💡 Quick Implementation Priority

### For Demo (Minimum Viable):
✅ **Chart 1**: Main Forecast Chart (Historical + Forecast + Confidence)
✅ **Cards**: 4 Metric Cards (RMSE, MAE, MAPE, R²)

### For Production (Recommended):
✅ **Chart 1**: Main Forecast Chart
✅ **Chart 2**: Feature Importance
✅ **Cards**: 4 Metric Cards

### For Advanced Analysis (Optional):
✅ All 5 charts + 4 cards

---

## 📝 Example: Complete Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  Drug Name: VANCO MEDIS 500MG VI                        │
│  Drug Code: P182054                                     │
└─────────────────────────────────────────────────────────┘

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  RMSE    │ │   MAE    │ │  MAPE    │ │   R²     │
│  0.85    │ │  0.62    │ │  15.3%   │ │  0.78    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

┌─────────────────────────────────────────────────────────┐
│  MAIN FORECAST CHART (Chart 1)                         │
│  [Historical (blue) + Forecast (orange) + Confidence]  │
│  Width: 100%, Height: 500px                            │
└─────────────────────────────────────────────────────────┘

┌──────────────────────────┐ ┌──────────────────────────┐
│  FEATURE IMPORTANCE      │ │  TRAINING HISTORY        │
│  (Chart 2)               │ │  (Chart 3)               │
│  Horizontal Bar Chart    │ │  Line Chart               │
└──────────────────────────┘ └──────────────────────────┘

┌──────────────────────────┐ ┌──────────────────────────┐
│  ERROR DISTRIBUTION       │ │  ACTUAL VS PREDICTED     │
│  (Chart 4)               │ │  (Chart 5)               │
│  Histogram                │ │  Scatter Plot             │
└──────────────────────────┘ └──────────────────────────┘
```

---

## 🚀 Quick Start Code

See the complete React component example in:
`docs/api/ENHANCED_FORECAST_API.md`

The example includes:
- All 5 charts implemented
- 4 metric cards
- Responsive layout
- Error handling
- Loading states

---

## Summary

**Total Visualizations Available**: 
- **5 Charts** (Main Forecast, Feature Importance, Training History, Error Distribution, Scatter Plot)
- **4 Metric Cards** (RMSE, MAE, MAPE, R²)

**Minimum for Demo**: 
- **1 Chart** (Main Forecast) + **4 Cards**

**Recommended for Production**: 
- **2 Charts** (Main Forecast + Feature Importance) + **4 Cards**

