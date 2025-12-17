# Enhanced Forecasting API - Complete Documentation

## Overview

The Enhanced Forecasting API provides advanced drug demand forecasting using XGBoost machine learning with domain-specific features extracted from your transaction data (departments, categories, rooms, admission patterns). This API returns historical data, test predictions, and future forecasts in a frontend-ready format.

## Base URL
```
http://localhost:5000/api/ml-xgboost
```

---

## Endpoint

### Enhanced Forecast

```
GET /api/ml-xgboost/forecast-enhanced/<drug_code>
```

### Description

Get an enhanced XGBoost-based forecast with domain-specific features. This endpoint:
- Extracts rich features from transaction metadata (departments, categories, rooms, admission dates)
- Trains an XGBoost model on historical data
- Returns historical data, test predictions, and future forecasts
- Provides confidence intervals and model metrics

### Path Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `drug_code` | string | Yes | Drug code identifier | `P182054` |

### Query Parameters

| Parameter | Type | Required | Default | Description | Constraints |
|-----------|------|----------|---------|-------------|-------------|
| `forecast_days` | int | No | 30 | Days to forecast ahead | 1-365 |
| `test_size` | int | No | 30 | Days to use for testing/validation | Minimum 7 |
| `lookback_days` | int | No | 730 | Days of historical data to use | Minimum 60 |
| `start_date` | string | No | - | Start date for historical data (YYYY-MM-DD) | Valid date |
| `end_date` | string | No | Today | End date for historical data (YYYY-MM-DD) | Valid date |

### Example Requests

#### Basic Request
```bash
curl "http://localhost:5000/api/ml-xgboost/forecast-enhanced/P182054"
```

#### Custom Forecast Period
```bash
curl "http://localhost:5000/api/ml-xgboost/forecast-enhanced/P182054?forecast_days=60&test_size=30"
```

#### With Date Range
```bash
curl "http://localhost:5000/api/ml-xgboost/forecast-enhanced/P182054?start_date=2024-01-01&end_date=2024-12-31&forecast_days=30"
```

---

## Response Format

### Success Response (200 OK)

```json
{
  "success": true,
  "data": {
    "drug_code": "P182054",
    "drug_name": "VANCO MEDIS 500MG VI",
    "historical": [
      {
        "date": "2024-01-01",
        "demand": 5.0,
        "type": "actual"
      },
      {
        "date": "2024-01-02",
        "demand": 3.0,
        "type": "actual"
      }
      // ... more historical data points
    ],
    "test_predictions": [
      {
        "date": "2024-11-15",
        "actual": 4.2,
        "predicted": 4.5,
        "error": 0.3,
        "type": "test"
      }
      // ... more test predictions
    ],
    "forecast": [
      {
        "date": "2024-12-16",
        "predicted": 4.2,
        "lower": 3.1,
        "upper": 5.3,
        "type": "predicted"
      },
      {
        "date": "2024-12-17",
        "predicted": 4.5,
        "lower": 3.4,
        "upper": 5.6,
        "type": "predicted"
      }
      // ... more forecast points
    ],
    "metrics": {
      "rmse": 0.85,
      "mae": 0.62,
      "mape": 15.3,
      "r2": 0.78
    },
    "feature_importance": {
      "lag_7": 0.15,
      "rolling_mean_7": 0.12,
      "dept_demand_ratio": 0.10,
      "category_trend": 0.08,
      "dayofweek": 0.07
      // ... more features
    },
    "training_history": {
      "train_rmse": [2.5, 1.8, 1.2, 0.9, 0.85],
      "val_rmse": [2.8, 2.0, 1.4, 1.0, 0.92]
    },
    "forecast_days": 30,
    "test_size": 30,
    "data_info": {
      "total_days": 365,
      "train_days": 305,
      "test_days": 30,
      "date_range": {
        "start": "2024-01-01",
        "end": "2024-12-31"
      }
    }
  },
  "meta": {
    "request_id": "...",
    "status": "success"
  }
}
```

### Error Response (400 Bad Request)

```json
{
  "success": false,
  "data": {
    "error": "Insufficient data for drug_code 'P182054': need at least 60 days, got 45."
  },
  "meta": {
    "request_id": "...",
    "status": "error"
  }
}
```

---

## Response Fields Explained

### Historical Data
- **`historical`**: Array of actual demand data points
  - `date`: ISO date string
  - `demand`: Actual daily demand (quantity consumed)
  - `type`: Always `"actual"`

### Test Predictions
- **`test_predictions`**: Model validation data (last N days used for testing)
  - `date`: ISO date string
  - `actual`: Actual demand value
  - `predicted`: Model prediction
  - `error`: Prediction error (actual - predicted)
  - `type`: Always `"test"`

### Forecast Data
- **`forecast`**: Future predictions
  - `date`: ISO date string
  - `predicted`: Predicted demand
  - `lower`: Lower confidence bound (95% CI)
  - `upper`: Upper confidence bound (95% CI)
  - `type`: Always `"predicted"`

### Metrics
- **`rmse`**: Root Mean Squared Error (lower is better)
- **`mae`**: Mean Absolute Error (lower is better)
- **`mape`**: Mean Absolute Percentage Error (lower is better, in %)
- **`r2`**: R-squared score (higher is better, 0-1 range)

### Feature Importance
- Shows which features are most important for predictions
- Higher values indicate more important features
- Helps understand what drives demand patterns

---

## Frontend Integration Guide

### 1. React with Recharts

```tsx
import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface ForecastData {
  drug_code: string;
  drug_name: string;
  historical: Array<{ date: string; demand: number; type: string }>;
  test_predictions: Array<{
    date: string;
    actual: number;
    predicted: number;
    error: number;
    type: string;
  }>;
  forecast: Array<{
    date: string;
    predicted: number;
    lower: number;
    upper: number;
    type: string;
  }>;
  metrics: {
    rmse: number;
    mae: number;
    mape: number;
    r2: number;
  };
}

function EnhancedForecastChart({ drugCode }: { drugCode: string }) {
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchForecast = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:5000/api/ml-xgboost/forecast-enhanced/${drugCode}?forecast_days=30&test_size=30`
        );
        const result = await response.json();
        
        if (result.success) {
          setData(result.data);
        } else {
          setError(result.data?.error || 'Failed to fetch forecast');
        }
      } catch (err) {
        setError('Network error');
      } finally {
        setLoading(false);
      }
    };

    fetchForecast();
  }, [drugCode]);

  if (loading) return <div>Loading forecast...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return null;

  // Combine all data for charting
  const chartData = [
    // Historical data
    ...data.historical.map((d) => ({
      date: d.date,
      actual: d.demand,
      predicted: null,
      lower: null,
      upper: null,
      type: 'historical'
    })),
    // Test predictions (overlap with historical)
    ...data.test_predictions.map((d) => ({
      date: d.date,
      actual: d.actual,
      predicted: d.predicted,
      lower: null,
      upper: null,
      type: 'test'
    })),
    // Future forecast
    ...data.forecast.map((d) => ({
      date: d.date,
      actual: null,
      predicted: d.predicted,
      lower: d.lower,
      upper: d.upper,
      type: 'forecast'
    }))
  ];

  // Format date for display
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="forecast-chart-container">
      <h2>{data.drug_name} - Demand Forecast</h2>
      
      {/* Metrics Summary */}
      <div className="metrics-summary">
        <div className="metric">
          <label>RMSE</label>
          <value>{data.metrics.rmse.toFixed(2)}</value>
        </div>
        <div className="metric">
          <label>MAE</label>
          <value>{data.metrics.mae.toFixed(2)}</value>
        </div>
        <div className="metric">
          <label>MAPE</label>
          <value>{data.metrics.mape.toFixed(1)}%</value>
        </div>
        <div className="metric">
          <label>R²</label>
          <value>{data.metrics.r2.toFixed(2)}</value>
        </div>
      </div>

      {/* Main Chart */}
      <ResponsiveContainer width="100%" height={500}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis label={{ value: 'Demand', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value: any, name: string) => {
              if (name === 'Confidence Interval') return null;
              return [value?.toFixed(2), name];
            }}
            labelFormatter={(label) => `Date: ${formatDate(label)}`}
          />
          <Legend />
          
          {/* Historical Actual Demand */}
          <Area
            type="monotone"
            dataKey="actual"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.6}
            name="Historical Demand"
            connectNulls={false}
          />
          
          {/* Predicted Demand */}
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#f59e0b"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Predicted Demand"
            connectNulls={false}
          />
          
          {/* Confidence Interval */}
          <Area
            type="monotone"
            dataKey="upper"
            stroke="none"
            fill="url(#confidenceGradient)"
            name="Confidence Interval"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="lower"
            stroke="#f59e0b"
            strokeWidth={1}
            strokeDasharray="3 3"
            dot={false}
            connectNulls={false}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Forecast Summary */}
      <div className="forecast-summary">
        <h3>Forecast Summary</h3>
        <p>
          Average predicted demand: {
            (data.forecast.reduce((sum, d) => sum + d.predicted, 0) / data.forecast.length).toFixed(2)
          } units/day
        </p>
        <p>
          Forecast period: {data.forecast[0]?.date} to {data.forecast[data.forecast.length - 1]?.date}
        </p>
      </div>
    </div>
  );
}

export default EnhancedForecastChart;
```

### 2. Vue.js with Chart.js

```vue
<template>
  <div class="forecast-chart">
    <h2>{{ forecastData?.drug_name }} - Demand Forecast</h2>
    
    <div v-if="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Metrics -->
      <div class="metrics">
        <div class="metric">
          <span class="label">RMSE:</span>
          <span class="value">{{ forecastData?.metrics.rmse.toFixed(2) }}</span>
        </div>
        <div class="metric">
          <span class="label">R²:</span>
          <span class="value">{{ forecastData?.metrics.r2.toFixed(2) }}</span>
        </div>
      </div>

      <!-- Chart -->
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'EnhancedForecastChart',
  props: {
    drugCode: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      forecastData: null,
      loading: true,
      error: null,
      chart: null
    };
  },
  async mounted() {
    await this.fetchForecast();
    if (this.forecastData) {
      this.renderChart();
    }
  },
  methods: {
    async fetchForecast() {
      try {
        this.loading = true;
        const response = await fetch(
          `http://localhost:5000/api/ml-xgboost/forecast-enhanced/${this.drugCode}?forecast_days=30`
        );
        const result = await response.json();
        
        if (result.success) {
          this.forecastData = result.data;
        } else {
          this.error = result.data?.error || 'Failed to fetch forecast';
        }
      } catch (err) {
        this.error = 'Network error';
      } finally {
        this.loading = false;
      }
    },
    renderChart() {
      const ctx = this.$refs.chartCanvas;
      if (!ctx || !this.forecastData) return;

      // Prepare data
      const historical = this.forecastData.historical.map(d => ({
        x: d.date,
        y: d.demand
      }));
      
      const forecast = this.forecastData.forecast.map(d => ({
        x: d.date,
        y: d.predicted,
        lower: d.lower,
        upper: d.upper
      }));

      // Destroy existing chart
      if (this.chart) {
        this.chart.destroy();
      }

      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [
            {
              label: 'Historical Demand',
              data: historical,
              borderColor: '#3b82f6',
              backgroundColor: '#3b82f680',
              tension: 0.4
            },
            {
              label: 'Predicted Demand',
              data: forecast,
              borderColor: '#f59e0b',
              borderDash: [5, 5],
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            x: {
              type: 'time',
              time: {
                unit: 'day',
                displayFormats: {
                  day: 'MMM DD'
                }
              }
            },
            y: {
              title: {
                display: true,
                text: 'Demand'
              }
            }
          },
          plugins: {
            legend: {
              display: true
            },
            tooltip: {
              mode: 'index',
              intersect: false
            }
          }
        }
      });
    }
  }
};
</script>
```

### 3. Vanilla JavaScript with Chart.js

```html
<!DOCTYPE html>
<html>
<head>
  <title>Enhanced Forecast Chart</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
</head>
<body>
  <div id="forecast-container">
    <h2 id="drug-name">Loading...</h2>
    <div id="metrics"></div>
    <canvas id="forecast-chart"></canvas>
  </div>

  <script>
    async function loadForecast(drugCode) {
      try {
        const response = await fetch(
          `http://localhost:5000/api/ml-xgboost/forecast-enhanced/${drugCode}?forecast_days=30`
        );
        const result = await response.json();
        
        if (result.success) {
          renderForecast(result.data);
        } else {
          document.getElementById('drug-name').textContent = 'Error: ' + result.data.error;
        }
      } catch (error) {
        document.getElementById('drug-name').textContent = 'Network error';
      }
    }

    function renderForecast(data) {
      // Update title
      document.getElementById('drug-name').textContent = data.drug_name + ' - Demand Forecast';
      
      // Display metrics
      const metricsHtml = `
        <div style="display: flex; gap: 20px; margin: 20px 0;">
          <div><strong>RMSE:</strong> ${data.metrics.rmse.toFixed(2)}</div>
          <div><strong>MAE:</strong> ${data.metrics.mae.toFixed(2)}</div>
          <div><strong>R²:</strong> ${data.metrics.r2.toFixed(2)}</div>
        </div>
      `;
      document.getElementById('metrics').innerHTML = metricsHtml;

      // Prepare chart data
      const historicalData = data.historical.map(d => ({
        x: d.date,
        y: d.demand
      }));
      
      const forecastData = data.forecast.map(d => ({
        x: d.date,
        y: d.predicted
      }));

      // Create chart
      const ctx = document.getElementById('forecast-chart').getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [
            {
              label: 'Historical Demand',
              data: historicalData,
              borderColor: '#3b82f6',
              backgroundColor: '#3b82f680',
              tension: 0.4
            },
            {
              label: 'Predicted Demand',
              data: forecastData,
              borderColor: '#f59e0b',
              borderDash: [5, 5],
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            x: {
              type: 'time',
              time: {
                unit: 'day'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Demand'
              }
            }
          }
        }
      });
    }

    // Load forecast on page load
    const urlParams = new URLSearchParams(window.location.search);
    const drugCode = urlParams.get('drug_code') || 'P182054';
    loadForecast(drugCode);
  </script>
</body>
</html>
```

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```typescript
try {
  const response = await fetch(url);
  const result = await response.json();
  
  if (!result.success) {
    // Handle API error
    console.error('API Error:', result.data.error);
    showErrorMessage(result.data.error);
    return;
  }
  
  // Process successful response
  processForecastData(result.data);
} catch (error) {
  // Handle network error
  console.error('Network Error:', error);
  showErrorMessage('Failed to connect to server');
}
```

### 2. Loading States

Show loading indicators during API calls:

```tsx
const [loading, setLoading] = useState(true);

useEffect(() => {
  setLoading(true);
  fetchForecast().finally(() => setLoading(false));
}, [drugCode]);

if (loading) return <Spinner />;
```

### 3. Data Validation

Validate response data before rendering:

```typescript
function validateForecastData(data: any): data is ForecastData {
  return (
    data &&
    Array.isArray(data.historical) &&
    Array.isArray(data.forecast) &&
    data.metrics &&
    typeof data.metrics.rmse === 'number'
  );
}

if (!validateForecastData(result.data)) {
  throw new Error('Invalid forecast data format');
}
```

### 4. Performance Optimization

- Cache forecast results for recently viewed drugs
- Debounce rapid drug code changes
- Use pagination for large historical datasets

```typescript
const forecastCache = new Map<string, ForecastData>();

async function getForecast(drugCode: string, useCache = true) {
  if (useCache && forecastCache.has(drugCode)) {
    return forecastCache.get(drugCode);
  }
  
  const data = await fetchForecast(drugCode);
  forecastCache.set(drugCode, data);
  return data;
}
```

---

## Visualization Recommendations

### 1. Chart Types

- **Line Chart**: Best for showing trends over time
- **Area Chart**: Good for showing confidence intervals
- **Combined Chart**: Historical (line) + Forecast (dashed line) + Confidence (shaded area)

### 2. Color Scheme

- **Historical Data**: Blue (`#3b82f6`) - solid line
- **Predicted Data**: Orange (`#f59e0b`) - dashed line
- **Confidence Interval**: Orange with transparency (20-30% opacity)
- **Test Predictions**: Can use a different color to distinguish from historical

### 3. Interactive Features

- **Tooltips**: Show date, actual/predicted values, confidence bounds
- **Zoom**: Allow users to zoom into specific date ranges
- **Legend**: Toggle visibility of different data series
- **Export**: Allow users to export chart as image or data as CSV

### 4. Additional Visualizations

- **Metrics Cards**: Display RMSE, MAE, MAPE, R² prominently
- **Feature Importance Bar Chart**: Show which features matter most
- **Error Distribution**: Histogram of prediction errors
- **Residual Plot**: Show prediction errors over time

---

## Example Complete React Component

```tsx
import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';

interface ForecastProps {
  drugCode: string;
  forecastDays?: number;
}

export default function EnhancedForecastDashboard({ drugCode, forecastDays = 30 }: ForecastProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchForecast();
  }, [drugCode, forecastDays]);

  const fetchForecast = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `http://localhost:5000/api/ml-xgboost/forecast-enhanced/${drugCode}?forecast_days=${forecastDays}&test_size=30`
      );
      const result = await response.json();
      
      if (result.success) {
        setData(result.data);
      } else {
        setError(result.data?.error || 'Failed to fetch forecast');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Loading forecast data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h3>Error</h3>
        <p>{error}</p>
        <button onClick={fetchForecast}>Retry</button>
      </div>
    );
  }

  if (!data) return null;

  // Prepare chart data
  const chartData = [
    ...data.historical.map(d => ({
      date: d.date,
      actual: d.demand,
      predicted: null,
      lower: null,
      upper: null
    })),
    ...data.forecast.map(d => ({
      date: d.date,
      actual: null,
      predicted: d.predicted,
      lower: d.lower,
      upper: d.upper
    }))
  ];

  // Feature importance data
  const featureImportance = Object.entries(data.feature_importance)
    .sort(([, a], [, b]) => (b as number) - (a as number))
    .slice(0, 10)
    .map(([feature, importance]) => ({
      feature,
      importance: importance as number
    }));

  return (
    <div className="forecast-dashboard">
      <header>
        <h1>{data.drug_name}</h1>
        <p className="drug-code">Drug Code: {data.drug_code}</p>
      </header>

      {/* Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">RMSE</div>
          <div className="metric-value">{data.metrics.rmse.toFixed(2)}</div>
          <div className="metric-description">Root Mean Squared Error</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">MAE</div>
          <div className="metric-value">{data.metrics.mae.toFixed(2)}</div>
          <div className="metric-description">Mean Absolute Error</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">MAPE</div>
          <div className="metric-value">{data.metrics.mape.toFixed(1)}%</div>
          <div className="metric-description">Mean Absolute % Error</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">R² Score</div>
          <div className="metric-value">{data.metrics.r2.toFixed(2)}</div>
          <div className="metric-description">Model Accuracy</div>
        </div>
      </div>

      {/* Main Forecast Chart */}
      <div className="chart-section">
        <h2>Demand Forecast</h2>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis label={{ value: 'Demand', angle: -90, position: 'insideLeft' }} />
            <Tooltip
              formatter={(value: any) => value?.toFixed(2)}
              labelFormatter={(label) => new Date(label).toLocaleDateString()}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="actual"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.6}
              name="Historical Demand"
            />
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Predicted Demand"
            />
            <Area
              type="monotone"
              dataKey="upper"
              stroke="none"
              fill="url(#confidenceGradient)"
              name="95% Confidence Interval"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Feature Importance */}
      <div className="chart-section">
        <h2>Top 10 Most Important Features</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={featureImportance} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="feature" type="category" width={150} />
            <Tooltip />
            <Bar dataKey="importance" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Forecast Summary */}
      <div className="summary-section">
        <h2>Forecast Summary</h2>
        <div className="summary-grid">
          <div>
            <strong>Forecast Period:</strong>
            <p>{data.forecast[0]?.date} to {data.forecast[data.forecast.length - 1]?.date}</p>
          </div>
          <div>
            <strong>Average Predicted Demand:</strong>
            <p>
              {(data.forecast.reduce((sum: number, d: any) => sum + d.predicted, 0) / data.forecast.length).toFixed(2)} units/day
            </p>
          </div>
          <div>
            <strong>Total Predicted Demand:</strong>
            <p>
              {data.forecast.reduce((sum: number, d: any) => sum + d.predicted, 0).toFixed(0)} units
            </p>
          </div>
          <div>
            <strong>Data Range:</strong>
            <p>{data.data_info.date_range.start} to {data.data_info.date_range.end}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## CSS Styling Example

```css
.forecast-dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.metric-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e9ecef;
}

.metric-label {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: #212529;
  margin-bottom: 4px;
}

.metric-description {
  font-size: 12px;
  color: #6c757d;
}

.chart-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.summary-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.loading-container,
.error-container {
  text-align: center;
  padding: 40px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

---

## Troubleshooting

### Common Issues

1. **"Insufficient data" error**
   - Solution: Ensure the drug has at least 60 days of historical data
   - Try increasing `lookback_days` parameter

2. **Slow response times**
   - Solution: Reduce `lookback_days` or use a smaller `test_size`
   - Consider caching results on the frontend

3. **Missing confidence intervals**
   - Check that `forecast` array contains `lower` and `upper` fields
   - These are calculated from test prediction errors

4. **Chart not rendering**
   - Verify date format is ISO string (YYYY-MM-DD)
   - Check that numeric values are not null/undefined
   - Ensure charting library is properly imported

---

## API Rate Limits & Performance

- **Recommended**: Cache forecast results for at least 5 minutes
- **Training Time**: First request may take 10-30 seconds (model training)
- **Subsequent Requests**: Cached models respond in 1-3 seconds
- **Concurrent Requests**: Limit to 5-10 simultaneous requests per drug

---

## Support

For issues or questions:
- Check API health: `GET /api/ml-xgboost/health`
- Verify data availability: `GET /api/ml-xgboost/data-check/<drug_code>`
- Review server logs for detailed error messages

