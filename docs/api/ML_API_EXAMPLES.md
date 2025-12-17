# ML API - Complete Examples

## Base URL
```
http://localhost:5000/api/ml
```

---

## 1. Simple Forecast (Moving Average)

### Endpoint
```
GET /api/ml/forecast/<drug_code>
```

### Description
Get a simple time-series forecast using moving average method. This is a lightweight forecasting approach suitable for quick predictions.

### Path Parameters
- **drug_code** (required): Drug code identifier (e.g., "DRUG001", "ABC123")

### Query Parameters

| Parameter | Type | Required | Default | Description | Constraints |
|-----------|------|----------|---------|-------------|-------------|
| `forecast_days` | int | No | 30 | Days to forecast ahead | 1-365 |
| `lookback_days` | int | No | 90 | Days of historical data to use | Minimum 7 |

### Using cURL

```bash
# Basic forecast (30 days, 90 days lookback)
curl "http://localhost:5000/api/ml/forecast/DRUG001"

# Custom forecast period
curl "http://localhost:5000/api/ml/forecast/DRUG001?forecast_days=60&lookback_days=180"

# Short-term forecast
curl "http://localhost:5000/api/ml/forecast/DRUG001?forecast_days=7&lookback_days=30"
```

### Using Python requests

```python
import requests

base_url = "http://localhost:5000/api/ml"

# Basic forecast
response = requests.get(f"{base_url}/forecast/DRUG001")
print(response.json())

# Custom parameters
params = {
    "forecast_days": 60,
    "lookback_days": 180
}
response = requests.get(f"{base_url}/forecast/DRUG001", params=params)
data = response.json()

if data.get('success'):
    forecast = data.get('data', {})
    print(f"Drug: {forecast.get('drug_name')}")
    print(f"Forecast period: {forecast.get('forecast_period')}")
    print(f"Average daily demand: {forecast.get('summary', {}).get('average_daily_demand')}")
```

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Simple Forecast"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/ml/forecast/DRUG001`
     - Replace `DRUG001` with an actual drug code

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `forecast_days` | `30` | Optional: Days to forecast (default: 30) |
   | `lookback_days` | `90` | Optional: Historical data days (default: 90) |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request:**
```
GET http://localhost:5000/api/ml/forecast/DRUG001?forecast_days=30&lookback_days=90
```

**Expected Response Status:** `200 OK`

### Response Example

```json
{
  "success": true,
  "data": {
    "drug_code": "DRUG001",
    "drug_name": "Paracetamol 500mg",
    "forecast_period": {
      "start_date": "2024-01-16",
      "end_date": "2024-02-14",
      "days": 30
    },
    "summary": {
      "total_predicted_demand": 1500.0,
      "average_daily_demand": 50.0,
      "peak_demand_day": "2024-01-20",
      "peak_demand_value": 75.5
    },
    "historical_data": [
      {
        "date": "2023-10-15",
        "demand": 45.0
      }
    ],
    "forecast_data": [
      {
        "date": "2024-01-16",
        "predicted_demand": 48.5
      }
    ]
  }
}
```

### Error Responses

**Invalid forecast_days:**
```json
{
  "success": false,
  "error": {
    "message": "forecast_days must be between 1 and 365",
    "code": "VALIDATION_ERROR"
  }
}
```

**Invalid lookback_days:**
```json
{
  "success": false,
  "error": {
    "message": "lookback_days must be at least 7",
    "code": "VALIDATION_ERROR"
  }
}
```

**Insufficient Data:**
```json
{
  "success": false,
  "error": {
    "message": "Insufficient historical data for drug DRUG001",
    "code": "INSUFFICIENT_DATA"
  }
}
```

---

## 2. Gradient Boosting Forecast (Advanced ML)

### Endpoint
```
GET /api/ml/forecast/gradient-boosting/<drug_code>
```

### Description
Get an advanced ML-based forecast using Gradient Boosting Regressor. This method includes:
- Time-based features (day of week, month, holidays)
- Lag features (previous demand values)
- Rolling statistics
- Confidence intervals
- Inventory recommendations

### Path Parameters
- **drug_code** (required): Drug code identifier (e.g., "DRUG001", "ABC123")

### Query Parameters

| Parameter | Type | Required | Default | Description | Constraints |
|-----------|------|----------|---------|-------------|-------------|
| `forecast_days` | int | No | 30 | Days to forecast ahead | 1-365 |

### Using cURL

```bash
# Basic forecast (30 days)
curl "http://localhost:5000/api/ml/forecast/gradient-boosting/DRUG001"

# Custom forecast period
curl "http://localhost:5000/api/ml/forecast/gradient-boosting/DRUG001?forecast_days=60"

# Short-term forecast
curl "http://localhost:5000/api/ml/forecast/gradient-boosting/DRUG001?forecast_days=14"
```

### Using Python requests

```python
import requests

base_url = "http://localhost:5000/api/ml"

# Basic forecast
response = requests.get(f"{base_url}/forecast/gradient-boosting/DRUG001")
data = response.json()

if data.get('success'):
    forecast = data.get('data', {})
    print(f"Drug: {forecast.get('drug_name')}")
    print(f"Total Predicted Demand: {forecast.get('summary', {}).get('total_predicted_demand')}")
    
    # Print recommendations
    for rec in forecast.get('recommendations', []):
        print(f"{rec['type']}: {rec['value']} - {rec['description']}")

# Custom forecast period
params = {"forecast_days": 60}
response = requests.get(f"{base_url}/forecast/gradient-boosting/DRUG001", params=params)
```

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Gradient Boosting Forecast"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/ml/forecast/gradient-boosting/DRUG001`
     - Replace `DRUG001` with an actual drug code

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameter:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `forecast_days` | `30` | Optional: Days to forecast (default: 30) |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request:**
```
GET http://localhost:5000/api/ml/forecast/gradient-boosting/DRUG001?forecast_days=30
```

**Expected Response Status:** `200 OK`

### Response Example

```json
{
  "success": true,
  "data": {
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
      ],
      "forecast": [
        {
          "date": "2024-01-16",
          "demand": 48.5,
          "confidence_lower": 35.2,
          "confidence_upper": 61.8,
          "type": "predicted"
        }
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
}
```

### Response Fields

- **drug_code**: Drug identifier
- **drug_name**: Full name of the drug
- **unit_price**: Unit price of the drug
- **forecast_generated**: Timestamp when forecast was generated
- **forecast_period**: Start date, end date, and number of days
- **summary**: Aggregated statistics
  - **total_predicted_demand**: Sum of all predicted demand
  - **average_daily_demand**: Average daily predicted demand
  - **peak_demand_day**: Date with highest predicted demand
  - **peak_demand_value**: Highest predicted demand value
  - **total_predicted_cost**: Total cost based on unit price
- **chart_data**: Data formatted for visualization
  - **historical**: Last 90 days of actual demand
  - **forecast**: Forecast data with confidence intervals
- **chart_config**: Chart configuration hints for frontend
- **daily_forecasts**: Detailed daily predictions with metadata
- **recommendations**: Inventory management recommendations

### Error Responses

**Invalid forecast_days:**
```json
{
  "success": false,
  "error": {
    "message": "forecast_days must be between 1 and 365",
    "code": "VALIDATION_ERROR"
  }
}
```

**Insufficient Data:**
```json
{
  "success": false,
  "error": {
    "message": "Insufficient historical data for drug DRUG001. Need at least 30 days.",
    "code": "INSUFFICIENT_DATA"
  }
}
```

**Model Training Error:**
```json
{
  "success": false,
  "error": {
    "message": "Error training model: [error details]",
    "code": "MODEL_TRAINING_ERROR"
  }
}
```

---

## 3. Train Model

### Endpoint
```
POST /api/ml/train/<drug_code>
```

### Description
Train a Gradient Boosting model for a specific drug. This endpoint allows you to pre-train models to improve forecast response times. Models are automatically trained on first forecast request, but you can train them in advance using this endpoint.

### Path Parameters
- **drug_code** (required): Drug code identifier (e.g., "DRUG001", "ABC123")

### Query Parameters

| Parameter | Type | Required | Default | Description | Constraints |
|-----------|------|----------|---------|-------------|-------------|
| `forecast_horizon` | int | No | 30 | Forecast horizon for training | Positive integer |

### Using cURL

```bash
# Train with default horizon (30 days)
curl -X POST "http://localhost:5000/api/ml/train/DRUG001"

# Train with custom horizon
curl -X POST "http://localhost:5000/api/ml/train/DRUG001?forecast_horizon=60"
```

### Using Python requests

```python
import requests

base_url = "http://localhost:5000/api/ml"

# Train model
response = requests.post(f"{base_url}/train/DRUG001")
data = response.json()

if data.get('success'):
    result = data.get('data', {})
    print(f"Drug: {result.get('drug_code')}")
    print(f"Training samples: {result.get('training_samples')}")
    print(f"CV Scores: {result.get('cv_scores')}")
    
    # Print feature importance
    for feature, importance in result.get('feature_importance', {}).items():
        print(f"{feature}: {importance}")

# Train with custom horizon
params = {"forecast_horizon": 60}
response = requests.post(f"{base_url}/train/DRUG001", params=params)
```

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Train Model"

2. **Set the HTTP method and URL**
   - Method: `POST`
   - URL: `http://localhost:5000/api/ml/train/DRUG001`
     - Replace `DRUG001` with an actual drug code

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameter:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `forecast_horizon` | `30` | Optional: Forecast horizon (default: 30) |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request:**
```
POST http://localhost:5000/api/ml/train/DRUG001?forecast_horizon=30
```

**Expected Response Status:** `200 OK`

### Response Example

```json
{
  "success": true,
  "data": {
    "drug_code": "DRUG001",
    "training_samples": 365,
    "cv_scores": [
      {
        "fold": 1,
        "mae": 5.2,
        "rmse": 7.8,
        "mape": 12.5
      },
      {
        "fold": 2,
        "mae": 4.9,
        "rmse": 7.5,
        "mape": 11.8
      },
      {
        "fold": 3,
        "mae": 5.1,
        "rmse": 7.6,
        "mape": 12.1
      }
    ],
    "average_cv_scores": {
      "mae": 5.07,
      "rmse": 7.63,
      "mape": 12.13
    },
    "feature_importance": {
      "demand_lag_1": 0.25,
      "demand_lag_7": 0.18,
      "day_of_week": 0.12,
      "rolling_mean_7": 0.10,
      "month": 0.08,
      "rolling_std_7": 0.07,
      "is_weekend": 0.05,
      "is_holiday": 0.04
    },
    "last_training_date": "2024-01-15T10:30:00",
    "forecast_horizon": 30,
    "model_ready": true
  }
}
```

### Response Fields

- **drug_code**: Drug identifier
- **training_samples**: Number of samples used for training
- **cv_scores**: Cross-validation scores for each fold
  - **fold**: Fold number
  - **mae**: Mean Absolute Error
  - **rmse**: Root Mean Squared Error
  - **mape**: Mean Absolute Percentage Error
- **average_cv_scores**: Average scores across all folds
- **feature_importance**: Importance of each feature (sums to 1.0)
- **last_training_date**: Timestamp when model was trained
- **forecast_horizon**: Forecast horizon used for training
- **model_ready**: Whether model is ready for forecasting

### Error Responses

**Training Error:**
```json
{
  "success": false,
  "error": {
    "message": "Error training model: [error details]",
    "code": "TRAINING_ERROR"
  }
}
```

**Insufficient Data:**
```json
{
  "success": false,
  "error": {
    "message": "Insufficient historical data for training. Need at least 30 days.",
    "code": "INSUFFICIENT_DATA"
  }
}
```

---

## 4. Health Check

### Endpoint
```
GET /api/ml/health
```

### Description
Health check endpoint to verify the ML module is operational.

### Using cURL

```bash
curl "http://localhost:5000/api/ml/health"
```

### Using Python requests

```python
import requests

response = requests.get("http://localhost:5000/api/ml/health")
print(response.json())
```

### Response Example

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "module": "ml",
    "method": "simple_moving_average"
  }
}
```

---

## Comparison: Simple vs Gradient Boosting Forecast

| Feature | Simple Forecast | Gradient Boosting |
|---------|----------------|-------------------|
| **Method** | Moving Average | Gradient Boosting Regressor |
| **Speed** | Fast (< 1 second) | Slower (10-30 seconds first time) |
| **Accuracy** | Basic | Advanced (higher accuracy) |
| **Features** | Historical average | Time features, lags, rolling stats |
| **Confidence Intervals** | No | Yes |
| **Recommendations** | No | Yes (inventory management) |
| **Chart Data** | Basic | Advanced with config |
| **Use Case** | Quick estimates | Production forecasting |

### When to Use Each

**Use Simple Forecast when:**
- You need quick estimates
- Historical patterns are stable
- You don't need confidence intervals
- Response time is critical

**Use Gradient Boosting when:**
- You need accurate predictions
- You want confidence intervals
- You need inventory recommendations
- You can wait for model training (first time)

---

## Finding Drug Codes

Before using the forecast endpoints, you need valid drug codes. Here are some ways to find them:

### SQL Query

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

### Using Dashboard API

```python
import requests

# Get top drugs from dashboard API
response = requests.get(
    "http://localhost:5000/api/dashboard/top-drugs",
    params={
        "start_date": "2019-01-01",
        "end_date": "2019-12-31",
        "limit": 10
    }
)

drugs = response.json()['data']['drugs']
for drug in drugs:
    print(f"{drug['drug_code']}: {drug['drug_name']}")
```

---

## Best Practices

1. **Data Requirements**
   - Ensure at least 30 days of historical data for gradient boosting
   - More data generally leads to better predictions

2. **Forecast Horizon**
   - Shorter horizons (7-14 days) are more accurate
   - Longer horizons (60-90 days) show trends but less accuracy

3. **Model Training**
   - Train models in advance during off-peak hours
   - Retrain periodically as new data becomes available
   - Cache trained models for faster responses

4. **Error Handling**
   - Always check `success` field in response
   - Handle `INSUFFICIENT_DATA` errors gracefully
   - Implement retry logic for transient errors

5. **Performance**
   - First forecast request may take 10-30 seconds (model training)
   - Subsequent requests are faster (cached models)
   - Use simple forecast for real-time needs

---

## Frontend Integration

The gradient boosting forecast response includes `chart_data` and `chart_config` that are ready for visualization. See `docs/ML_FORECAST_FRONTEND_INTEGRATION.md` for detailed frontend examples using:
- Recharts (React)
- Chart.js
- Plotly.js
- Vue.js

---

## Troubleshooting

### Error: "Insufficient historical data"
**Solution:** The drug needs at least 30 days of historical consumption data. Try a different drug code or wait for more data.

### Error: "No recent data available"
**Solution:** The drug has historical data but no recent transactions. Check the database for the latest transaction date.

### Model Training Takes Time
**Note:** The first forecast request will automatically train the model, which may take 10-30 seconds depending on data size. Subsequent requests for the same drug will be faster as the model is cached.

### Forecast Values Seem Unrealistic
**Solution:** Check the historical data quality. Ensure there are no data anomalies or missing periods that could affect predictions.

---

## Related Documentation

- **Quick Start Guide**: `docs/ML_GRADIENT_BOOSTING_QUICK_START.md`
- **Frontend Integration**: `docs/ML_FORECAST_FRONTEND_INTEGRATION.md`
- **Dashboard API**: `docs/api/DASHBOARD_API_EXAMPLES.md`

