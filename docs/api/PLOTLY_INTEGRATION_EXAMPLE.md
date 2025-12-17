# Plotly Integration Example - Enhanced Forecast API

## Quick Answer

**Yes!** Your API response contains **ALL** the data needed. The frontend team can consume it and plot using **Plotly** (or any charting library).

---

## API Response Structure

Your API returns everything needed:

```json
{
  "success": true,
  "data": {
    "drug_code": "P182054",
    "drug_name": "VANCO MEDIS 500MG VI",
    
    // ✅ Chart 1: Main Forecast (Historical + Future)
    "historical": [
      {"date": "2024-01-01", "demand": 5.0, "type": "actual"}
    ],
    "forecast": [
      {"date": "2024-12-16", "predicted": 4.2, "lower": 3.1, "upper": 5.3}
    ],
    "test_predictions": [
      {"date": "2024-11-15", "actual": 4.2, "predicted": 4.5, "error": 0.3}
    ],
    
    // ✅ Chart 2: Feature Importance
    "feature_importance": {
      "lag_7": 0.15,
      "rolling_mean_7": 0.12
    },
    
    // ✅ Chart 3: Training History (optional)
    "training_history": {
      "train_rmse": [2.5, 1.8, 1.2],
      "val_rmse": [2.8, 2.0, 1.4]
    },
    
    // ✅ Metric Cards
    "metrics": {
      "rmse": 0.85,
      "mae": 0.62,
      "mape": 15.3,
      "r2": 0.78
    }
  }
}
```

---

## Plotly Implementation Example

### Complete React Component with Plotly

```tsx
import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

interface ForecastData {
  drug_code: string;
  drug_name: string;
  historical: Array<{ date: string; demand: number }>;
  forecast: Array<{ date: string; predicted: number; lower: number; upper: number }>;
  test_predictions: Array<{ date: string; actual: number; predicted: number }>;
  metrics: { rmse: number; mae: number; mape: number; r2: number };
  feature_importance: Record<string, number>;
  training_history?: { train_rmse: number[]; val_rmse: number[] };
}

function ForecastDashboard({ drugCode }: { drugCode: string }) {
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:5000/api/ml-xgboost/forecast-enhanced/${drugCode}?forecast_days=30`)
      .then(res => res.json())
      .then(result => {
        if (result.success) {
          setData(result.data);
        }
      })
      .finally(() => setLoading(false));
  }, [drugCode]);

  if (loading) return <div>Loading...</div>;
  if (!data) return <div>No data</div>;

  // ============================================
  // CHART 1: Main Forecast Chart
  // ============================================
  const mainForecastData = [
    // Historical actual demand
    {
      x: data.historical.map(d => d.date),
      y: data.historical.map(d => d.demand),
      type: 'scatter',
      mode: 'lines',
      name: 'Historical Demand',
      line: { color: '#3b82f6', width: 2 }
    },
    // Predicted future demand
    {
      x: data.forecast.map(d => d.date),
      y: data.forecast.map(d => d.predicted),
      type: 'scatter',
      mode: 'lines',
      name: 'Predicted Demand',
      line: { color: '#f59e0b', width: 2, dash: 'dash' }
    },
    // Upper confidence bound
    {
      x: data.forecast.map(d => d.date),
      y: data.forecast.map(d => d.upper),
      type: 'scatter',
      mode: 'lines',
      name: 'Upper Bound (95% CI)',
      line: { color: '#f59e0b', width: 1, dash: 'dot' },
      showlegend: false
    },
    // Lower confidence bound
    {
      x: data.forecast.map(d => d.date),
      y: data.forecast.map(d => d.lower),
      type: 'scatter',
      mode: 'lines',
      name: 'Lower Bound (95% CI)',
      line: { color: '#f59e0b', width: 1, dash: 'dot' },
      fill: 'tonexty',
      fillcolor: 'rgba(245, 158, 11, 0.2)',
      showlegend: false
    },
    // Test predictions (optional overlay)
    {
      x: data.test_predictions.map(d => d.date),
      y: data.test_predictions.map(d => d.actual),
      type: 'scatter',
      mode: 'markers',
      name: 'Test Actual',
      marker: { color: '#3b82f6', size: 6 }
    },
    {
      x: data.test_predictions.map(d => d.date),
      y: data.test_predictions.map(d => d.predicted),
      type: 'scatter',
      mode: 'markers',
      name: 'Test Predicted',
      marker: { color: '#f59e0b', size: 6 }
    }
  ];

  const mainForecastLayout = {
    title: `${data.drug_name} - Demand Forecast`,
    xaxis: { title: 'Date' },
    yaxis: { title: 'Demand' },
    hovermode: 'x unified',
    legend: { x: 0, y: 1 },
    height: 500
  };

  // ============================================
  // CHART 2: Feature Importance
  // ============================================
  const featureImportanceData = [
    {
      x: Object.values(data.feature_importance),
      y: Object.keys(data.feature_importance),
      type: 'bar',
      orientation: 'h',
      marker: { color: '#3b82f6' }
    }
  ].sort((a, b) => b.x[0] - a.x[0]).slice(0, 10); // Top 10

  const featureImportanceLayout = {
    title: 'Top 10 Feature Importance',
    xaxis: { title: 'Importance Score' },
    yaxis: { title: 'Feature' },
    height: 400
  };

  // ============================================
  // CHART 3: Training History (if available)
  // ============================================
  const trainingHistoryData = data.training_history ? [
    {
      x: Array.from({ length: data.training_history.train_rmse.length }, (_, i) => i + 1),
      y: data.training_history.train_rmse,
      type: 'scatter',
      mode: 'lines',
      name: 'Training RMSE',
      line: { color: '#3b82f6' }
    },
    {
      x: Array.from({ length: data.training_history.val_rmse.length }, (_, i) => i + 1),
      y: data.training_history.val_rmse,
      type: 'scatter',
      mode: 'lines',
      name: 'Validation RMSE',
      line: { color: '#f59e0b' }
    }
  ] : [];

  const trainingHistoryLayout = {
    title: 'Model Training Progress',
    xaxis: { title: 'Epoch' },
    yaxis: { title: 'RMSE' },
    height: 300
  };

  // ============================================
  // CHART 4: Error Distribution
  // ============================================
  const errors = data.test_predictions.map(d => d.error);
  const errorDistributionData = [
    {
      x: errors,
      type: 'histogram',
      marker: { color: '#3b82f6' },
      name: 'Prediction Errors'
    }
  ];

  const errorDistributionLayout = {
    title: 'Prediction Error Distribution',
    xaxis: { title: 'Error' },
    yaxis: { title: 'Frequency' },
    height: 300
  };

  // ============================================
  // CHART 5: Actual vs Predicted Scatter
  // ============================================
  const scatterData = [
    {
      x: data.test_predictions.map(d => d.actual),
      y: data.test_predictions.map(d => d.predicted),
      type: 'scatter',
      mode: 'markers',
      marker: { color: '#3b82f6', size: 8 },
      name: 'Predictions'
    },
    // Perfect prediction line
    {
      x: [Math.min(...data.test_predictions.map(d => d.actual)), 
          Math.max(...data.test_predictions.map(d => d.actual))],
      y: [Math.min(...data.test_predictions.map(d => d.actual)), 
          Math.max(...data.test_predictions.map(d => d.actual))],
      type: 'scatter',
      mode: 'lines',
      line: { color: 'red', dash: 'dash' },
      name: 'Perfect Prediction'
    }
  ];

  const scatterLayout = {
    title: 'Actual vs Predicted',
    xaxis: { title: 'Actual Demand' },
    yaxis: { title: 'Predicted Demand' },
    height: 400
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>{data.drug_name}</h1>
      <p>Drug Code: {data.drug_code}</p>

      {/* Metrics Cards */}
      <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
        <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6c757d' }}>RMSE</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{data.metrics.rmse.toFixed(2)}</div>
        </div>
        <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6c757d' }}>MAE</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{data.metrics.mae.toFixed(2)}</div>
        </div>
        <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6c757d' }}>MAPE</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{data.metrics.mape.toFixed(1)}%</div>
        </div>
        <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6c757d' }}>R²</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{data.metrics.r2.toFixed(2)}</div>
        </div>
      </div>

      {/* Chart 1: Main Forecast */}
      <Plot
        data={mainForecastData}
        layout={mainForecastLayout}
        style={{ width: '100%' }}
      />

      {/* Chart 2: Feature Importance */}
      <Plot
        data={featureImportanceData}
        layout={featureImportanceLayout}
        style={{ width: '100%' }}
      />

      {/* Chart 3: Training History (if available) */}
      {data.training_history && (
        <Plot
          data={trainingHistoryData}
          layout={trainingHistoryLayout}
          style={{ width: '100%' }}
        />
      )}

      {/* Charts 4 & 5: Side by side */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <Plot
          data={errorDistributionData}
          layout={errorDistributionLayout}
          style={{ width: '100%' }}
        />
        <Plot
          data={scatterData}
          layout={scatterLayout}
          style={{ width: '100%' }}
        />
      </div>
    </div>
  );
}

export default ForecastDashboard;
```

---

## Python/Plotly (if using Python frontend)

```python
import plotly.graph_objects as go
import plotly.express as px
import requests
import pandas as pd

# Fetch data
response = requests.get('http://localhost:5000/api/ml-xgboost/forecast-enhanced/P182054?forecast_days=30')
data = response.json()['data']

# Chart 1: Main Forecast
fig1 = go.Figure()

# Historical
fig1.add_trace(go.Scatter(
    x=[d['date'] for d in data['historical']],
    y=[d['demand'] for d in data['historical']],
    mode='lines',
    name='Historical Demand',
    line=dict(color='#3b82f6', width=2)
))

# Forecast
fig1.add_trace(go.Scatter(
    x=[d['date'] for d in data['forecast']],
    y=[d['predicted'] for d in data['forecast']],
    mode='lines',
    name='Predicted Demand',
    line=dict(color='#f59e0b', width=2, dash='dash')
))

# Confidence interval
fig1.add_trace(go.Scatter(
    x=[d['date'] for d in data['forecast']] + [d['date'] for d in reversed(data['forecast'])],
    y=[d['upper'] for d in data['forecast']] + [d['lower'] for d in reversed(data['forecast'])],
    fill='toself',
    fillcolor='rgba(245, 158, 11, 0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    name='95% Confidence Interval'
))

fig1.update_layout(
    title=f"{data['drug_name']} - Demand Forecast",
    xaxis_title='Date',
    yaxis_title='Demand',
    height=500
)

fig1.show()

# Chart 2: Feature Importance
feature_df = pd.DataFrame({
    'feature': list(data['feature_importance'].keys()),
    'importance': list(data['feature_importance'].values())
}).sort_values('importance', ascending=True).tail(10)

fig2 = go.Figure(go.Bar(
    x=feature_df['importance'],
    y=feature_df['feature'],
    orientation='h',
    marker_color='#3b82f6'
))

fig2.update_layout(
    title='Top 10 Feature Importance',
    xaxis_title='Importance Score',
    yaxis_title='Feature',
    height=400
)

fig2.show()
```

---

## Summary

✅ **Your API response has ALL the data needed**

✅ **Frontend can use Plotly, Recharts, Chart.js, D3.js, or any library**

✅ **All 5 charts can be created from the response:**
1. Main Forecast Chart ✅
2. Feature Importance ✅
3. Training History ✅
4. Error Distribution ✅
5. Actual vs Predicted Scatter ✅

✅ **Plus 4 metric cards** (RMSE, MAE, MAPE, R²)

**No additional backend work needed!** The frontend team can start building charts immediately. 🚀

