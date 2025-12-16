# Gradient Boosting Forecast - Quick Start Guide

This guide will help you quickly test the new Gradient Boosting forecasting service.

## Overview

The Gradient Boosting forecast service provides advanced ML-based predictions with:
- Time-based features (day of week, month, holidays)
- Lag features (previous demand values)
- Rolling statistics
- Confidence intervals
- Inventory recommendations

## Installation

First, install the new dependency:

```bash
pip install holidays==0.34
```

Or if using requirements.txt:

```bash
pip install -r requirements.txt
```

## API Endpoints

### 1. Generate Forecast (Quick Test)

**Endpoint:** `GET /api/ml/forecast/gradient-boosting/{drug_code}`

**Query Parameters:**
- `forecast_days` (optional, default: 30) - Number of days to forecast

**Example Request:**
```bash
# Get a 30-day forecast for a drug
curl http://localhost:5000/api/ml/forecast/gradient-boosting/DRUG001?forecast_days=30
```

**Example Response:**
```json
{
  "success": true,
  "drug_code": "DRUG001",
  "drug_name": "Paracetamol 500mg",
  "unit_price": 2.50,
  "forecast_generated": "2024-01-15T10:30:00",
  "forecast_period": {
    "start_date": "2024-01-16",
    "end_date": "2024-02-14",
    "days": 30
  },
  "summary": {
    "total_predicted_demand": 1500.0,
    "average_daily_demand": 50.0,
    "peak_demand_day": "2024-01-20",
    "peak_demand_value": 75.5,
    "total_predicted_cost": 3750.0
  },
  "chart_data": {
    "historical": [
      {
        "date": "2023-10-15",
        "demand": 45.0,
        "type": "actual"
      }
      // ... last 90 days of historical data
    ],
    "forecast": [
      {
        "date": "2024-01-16",
        "demand": 48.5,
        "confidence_lower": 35.2,
        "confidence_upper": 61.8,
        "type": "predicted"
      }
      // ... forecast days
    ]
  },
  "chart_config": {
    "type": "line",
    "title": "Demand Forecast: Paracetamol 500mg",
    "x_axis": "date",
    "y_axis": "demand",
    "series": [
      {
        "name": "Historical Demand",
        "color": "#3b82f6",
        "type": "line"
      },
      {
        "name": "Predicted Demand",
        "color": "#f59e0b",
        "type": "line",
        "stroke_dasharray": "5 5"
      }
    ]
  },
  "daily_forecasts": [
    {
      "date": "2024-01-16",
      "predicted_demand": 48.5,
      "confidence_lower": 35.2,
      "confidence_upper": 61.8,
      "day_of_week": "Tuesday",
      "is_weekend": false,
      "is_holiday": false
    }
    // ... more days
  ],
  "recommendations": [
    {
      "type": "SAFETY_STOCK",
      "value": 75.0,
      "description": "Recommended safety stock to cover 95% of demand variability"
    },
    {
      "type": "REORDER_POINT",
      "value": 425.0,
      "description": "Reorder when inventory falls below this level (based on 7-day lead time)"
    },
    {
      "type": "ECONOMIC_ORDER_QUANTITY",
      "value": 346.0,
      "description": "Optimal order quantity to minimize total inventory costs"
    }
  ]
}
```

**Note:** The response includes `chart_data` with historical and forecast data ready for plotting, plus `chart_config` with styling hints for frontend integration.

### 2. Train Model (Optional)

**Endpoint:** `POST /api/ml/train/{drug_code}`

**Query Parameters:**
- `forecast_horizon` (optional, default: 30) - Forecast horizon for training

**Example Request:**
```bash
# Train a model for a specific drug
curl -X POST http://localhost:5000/api/ml/train/DRUG001?forecast_horizon=30
```

**Example Response:**
```json
{
  "success": true,
  "drug_code": "DRUG001",
  "training_samples": 365,
  "cv_scores": [
    {"mae": 5.2, "rmse": 7.8},
    {"mae": 4.9, "rmse": 7.5},
    // ... more CV folds
  ],
  "feature_importance": {
    "demand_lag_1": 0.25,
    "demand_lag_7": 0.18,
    "day_of_week": 0.12,
    // ... more features
  },
  "last_training_date": "2024-01-15T10:30:00",
  "forecast_horizon": 30
}
```

## Quick Test Steps

### Step 1: Find a Drug Code

First, you need to find a drug code that has sufficient historical data (at least 30 days). You can query the database:

```sql
-- Get top drugs with most transactions
SELECT 
    drug_code,
    drug_name,
    COUNT(*) as transaction_count,
    MIN(transaction_date) as first_date,
    MAX(transaction_date) as last_date,
    COUNT(DISTINCT transaction_date) as unique_days
FROM drug_transactions
WHERE quantity < 0  -- Only consumption
GROUP BY drug_code, drug_name
HAVING COUNT(DISTINCT transaction_date) >= 30  -- At least 30 days of data
ORDER BY transaction_count DESC
LIMIT 10;
```

### Step 2: Test the Forecast

Use one of the drug codes from Step 1:

```bash
# Replace DRUG001 with an actual drug code from your database
curl http://localhost:5000/api/ml/forecast/gradient-boosting/DRUG001?forecast_days=30
```

### Step 3: Check the Results

The response will include:
- Daily forecasts with confidence intervals
- Summary statistics
- Inventory recommendations

## Python Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:5000"

# Get forecast for a drug
drug_code = "DRUG001"  # Replace with actual drug code
response = requests.get(
    f"{BASE_URL}/api/ml/forecast/gradient-boosting/{drug_code}",
    params={"forecast_days": 30}
)

if response.status_code == 200:
    data = response.json()
    print(f"Drug: {data['drug_name']}")
    print(f"Total Predicted Demand: {data['summary']['total_predicted_demand']}")
    print(f"Average Daily: {data['summary']['average_daily_demand']}")
    
    # Print recommendations
    for rec in data['recommendations']:
        print(f"{rec['type']}: {rec['value']} - {rec['description']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

## Troubleshooting

### Error: "Insufficient historical data"

**Solution:** The drug needs at least 30 days of historical consumption data. Try a different drug code or wait for more data.

### Error: "No recent data available"

**Solution:** The drug has historical data but no recent transactions. Check the database for the latest transaction date.

### Model Training Takes Time

**Note:** The first forecast request will automatically train the model, which may take 10-30 seconds depending on data size. Subsequent requests for the same drug will be faster as the model is cached.

## Key Features

1. **Automatic Training**: Models are trained automatically on first use
2. **Feature Engineering**: Includes time features, lags, and rolling statistics
3. **Confidence Intervals**: Provides upper and lower bounds for predictions
4. **Recommendations**: Generates inventory management recommendations
5. **Holiday Awareness**: Considers Saudi Arabia holidays in predictions

## Frontend Integration

The API response is **ready for plotting** with minimal processing:

- **`chart_data.historical`**: Last 90 days of actual demand (for comparison)
- **`chart_data.forecast`**: Forecast data with confidence intervals
- **`chart_config`**: Chart configuration hints (colors, types, etc.)

See `docs/ML_FORECAST_FRONTEND_INTEGRATION.md` for detailed frontend examples using:
- Recharts (React)
- Chart.js
- Plotly.js
- Vue.js

## Next Steps

- Try forecasting multiple drugs
- Compare results with the simple moving average forecast (`/api/ml/forecast/{drug_code}`)
- Use the recommendations for inventory planning
- Train models in advance using the `/train` endpoint for faster forecasts
- Integrate charts in your frontend using the `chart_data` section

