# ML Prediction Dashboard Visualizations - Implementation Guide

## Executive Summary

This document outlines the **specific visualizations** needed in your dashboard to effectively display ML predictions. Based on your existing dashboard APIs and chart infrastructure, we'll extend them to support ML prediction visualizations.

## Current Dashboard Capabilities

### Existing Chart Types
✅ **Line Charts** - Time-series trends (`/drug-demand`)  
✅ **Bar Charts** - Top drugs, departments  
✅ **Heatmaps** - Seasonal patterns  
✅ **Pie/Donut Charts** - Demographics  
✅ **Area Charts** - Mentioned in docs  

### Existing Infrastructure
- Plotly-based chart generation (`charts.py`)
- Pre-formatted chart data endpoints (`/chart-data/<type>`)
- Consistent API response format
- Date range filtering support

---

## Required ML Visualizations

### 1. Forecast vs Actual Comparison Chart ⭐ **CRITICAL**

**Purpose**: Show predicted demand vs actual historical demand

**Chart Type**: **Line Chart with Dual Series** (Historical + Forecast)

**Data Structure**:
```json
{
  "historical": [
    {"date": "2023-01-01", "demand": 450, "type": "actual"},
    {"date": "2023-01-02", "demand": 520, "type": "actual"}
  ],
  "forecast": [
    {"date": "2024-01-01", "demand": 480, "type": "predicted", "confidence_lower": 420, "confidence_upper": 540},
    {"date": "2024-01-02", "demand": 510, "type": "predicted", "confidence_lower": 450, "confidence_upper": 570}
  ],
  "model_info": {
    "model_type": "xgboost",
    "training_samples": 730,
    "mape": 12.5,
    "last_trained": "2024-01-15"
  }
}
```

**Visual Design**:
- **Historical data**: Solid line (blue) with markers
- **Forecast data**: Dashed line (orange) with markers
- **Confidence interval**: Shaded area (light orange, semi-transparent)
- **Split point**: Vertical line separating historical from forecast
- **Legend**: Clear distinction between actual and predicted

**Implementation**:
```python
# backend/app/modules/ml/charts.py
def create_forecast_comparison_chart(
    historical_data: List[Dict],
    forecast_data: List[Dict],
    show_confidence: bool = True
) -> go.Figure:
    """Create forecast vs actual comparison chart."""
    fig = go.Figure()
    
    # Historical data (actual)
    if historical_data:
        hist_dates = [d['date'] for d in historical_data]
        hist_values = [d['demand'] for d in historical_data]
        
        fig.add_trace(go.Scatter(
            x=hist_dates,
            y=hist_values,
            mode='lines+markers',
            name='Actual Demand',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=4)
        ))
    
    # Forecast data (predicted)
    if forecast_data:
        forecast_dates = [d['date'] for d in forecast_data]
        forecast_values = [d['demand'] for d in forecast_data]
        
        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=forecast_values,
            mode='lines+markers',
            name='Predicted Demand',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=4)
        ))
        
        # Confidence interval (if available)
        if show_confidence and 'confidence_lower' in forecast_data[0]:
            lower_bounds = [d.get('confidence_lower', d['demand']) for d in forecast_data]
            upper_bounds = [d.get('confidence_upper', d['demand']) for d in forecast_data]
            
            fig.add_trace(go.Scatter(
                x=forecast_dates + forecast_dates[::-1],
                y=upper_bounds + lower_bounds[::-1],
                fill='toself',
                fillcolor='rgba(255, 127, 14, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=True,
                name='Confidence Interval (80%)'
            ))
    
    # Add vertical line separating historical from forecast
    if historical_data and forecast_data:
        split_date = forecast_data[0]['date']
        fig.add_vline(
            x=split_date,
            line_dash="dot",
            line_color="gray",
            annotation_text="Forecast Start"
        )
    
    fig.update_layout(
        title='Demand Forecast vs Actual',
        xaxis_title='Date',
        yaxis_title='Demand (Quantity)',
        height=500,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig
```

**API Endpoint**: `/api/ml/forecast/{drug_code}`

---

### 2. Multi-Horizon Forecast Chart

**Purpose**: Show predictions at different time horizons (7, 14, 30, 90 days)

**Chart Type**: **Multi-Line Chart** with different forecast horizons

**Visual Design**:
- Multiple forecast lines for different horizons
- Color-coded by horizon (7d=green, 14d=yellow, 30d=orange, 90d=red)
- Each line labeled with horizon
- Confidence intervals for each horizon

**Implementation**:
```python
def create_multi_horizon_forecast_chart(
    forecasts: Dict[str, List[Dict]]  # {"7d": [...], "14d": [...], "30d": [...]}
) -> go.Figure:
    """Create multi-horizon forecast chart."""
    fig = go.Figure()
    
    colors = {
        "7d": "#2ca02c",
        "14d": "#ffbb78",
        "30d": "#ff7f0e",
        "90d": "#d62728"
    }
    
    for horizon, data in forecasts.items():
        dates = [d['date'] for d in data]
        values = [d['demand'] for d in data]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name=f'{horizon} Forecast',
            line=dict(color=colors.get(horizon, '#000'), width=2, dash='dash'),
            marker=dict(size=3)
        ))
    
    fig.update_layout(
        title='Multi-Horizon Demand Forecast',
        xaxis_title='Date',
        yaxis_title='Predicted Demand',
        height=500,
        hovermode='x unified'
    )
    
    return fig
```

---

### 3. Forecast Accuracy Metrics Dashboard

**Purpose**: Display model performance metrics

**Chart Type**: **KPI Cards + Bar Chart** for metrics

**Metrics to Display**:
- MAPE (Mean Absolute Percentage Error)
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score
- Forecast Accuracy (by drug/department)

**Visual Design**:
- **KPI Cards**: Large numbers with trend indicators
- **Bar Chart**: Compare accuracy across different drugs
- **Gauge Chart**: Overall model performance (0-100%)

**Implementation**:
```python
def create_accuracy_metrics_chart(metrics: Dict) -> go.Figure:
    """Create accuracy metrics visualization."""
    fig = go.Figure()
    
    # Bar chart comparing MAPE across drugs
    drugs = list(metrics.keys())
    mape_values = [metrics[drug]['mape'] for drug in drugs]
    
    fig.add_trace(go.Bar(
        x=drugs,
        y=mape_values,
        marker=dict(
            color=mape_values,
            colorscale='RdYlGn_r',  # Red-Yellow-Green reversed (lower is better)
            showscale=True,
            colorbar=dict(title="MAPE %")
        ),
        text=[f"{v:.2f}%" for v in mape_values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Forecast Accuracy by Drug (MAPE)',
        xaxis_title='Drug Code',
        yaxis_title='MAPE (%)',
        height=400
    )
    
    return fig
```

**API Endpoint**: `/api/ml/metrics/{drug_code}` or `/api/ml/metrics/overall`

---

### 4. Anomaly Detection Visualization

**Purpose**: Highlight detected anomalies in historical data

**Chart Type**: **Line Chart with Anomaly Markers**

**Visual Design**:
- Normal data: Standard line
- Anomalies: Red markers/circles
- Anomaly score: Color intensity
- Tooltip: Show anomaly reason/score

**Implementation**:
```python
def create_anomaly_detection_chart(
    data: List[Dict],
    anomalies: List[Dict]  # List of anomaly records with dates
) -> go.Figure:
    """Create anomaly detection visualization."""
    fig = go.Figure()
    
    dates = [d['date'] for d in data]
    values = [d['demand'] for d in data]
    
    # Normal data line
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name='Normal Demand',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4)
    ))
    
    # Anomaly markers
    anomaly_dates = [a['date'] for a in anomalies]
    anomaly_values = [a['demand'] for a in anomalies]
    anomaly_scores = [a.get('score', 1.0) for a in anomalies]
    
    fig.add_trace(go.Scatter(
        x=anomaly_dates,
        y=anomaly_values,
        mode='markers',
        name='Anomalies',
        marker=dict(
            size=12,
            color=anomaly_scores,
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Anomaly Score"),
            line=dict(width=2, color='red')
        ),
        text=[f"Score: {s:.2f}" for s in anomaly_scores],
        hovertemplate='<b>Anomaly Detected</b><br>Date: %{x}<br>Demand: %{y}<br>Score: %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Anomaly Detection Results',
        xaxis_title='Date',
        yaxis_title='Demand',
        height=500,
        hovermode='closest'
    )
    
    return fig
```

**API Endpoint**: `/api/ml/anomalies`

---

### 5. Model Performance Over Time

**Purpose**: Track how model accuracy changes over time

**Chart Type**: **Line Chart** showing accuracy trends

**Visual Design**:
- X-axis: Training date/model version
- Y-axis: Accuracy metric (MAPE, R²)
- Multiple lines for different metrics
- Annotations for model updates

**Implementation**:
```python
def create_model_performance_trend_chart(
    performance_history: List[Dict]  # [{date, mape, mae, r2, model_version}]
) -> go.Figure:
    """Create model performance trend chart."""
    fig = go.Figure()
    
    dates = [p['date'] for p in performance_history]
    
    # MAPE (lower is better)
    fig.add_trace(go.Scatter(
        x=dates,
        y=[p['mape'] for p in performance_history],
        mode='lines+markers',
        name='MAPE (%)',
        yaxis='y',
        line=dict(color='red', width=2)
    ))
    
    # R² (higher is better)
    fig.add_trace(go.Scatter(
        x=dates,
        y=[p['r2'] * 100 for p in performance_history],  # Convert to percentage
        mode='lines+markers',
        name='R² Score (%)',
        yaxis='y2',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title='Model Performance Over Time',
        xaxis_title='Model Training Date',
        yaxis=dict(title='MAPE (%)', side='left'),
        yaxis2=dict(title='R² Score (%)', side='right', overlaying='y'),
        height=500,
        hovermode='x unified'
    )
    
    return fig
```

---

### 6. Forecast Error Distribution

**Purpose**: Show distribution of forecast errors

**Chart Type**: **Histogram** or **Box Plot**

**Visual Design**:
- Histogram: Distribution of errors
- Box plot: Error quartiles and outliers
- Overlay: Normal distribution curve

**Implementation**:
```python
def create_error_distribution_chart(errors: List[float]) -> go.Figure:
    """Create forecast error distribution chart."""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=errors,
        nbinsx=30,
        name='Error Distribution',
        marker_color='steelblue',
        opacity=0.7
    ))
    
    # Add mean line
    mean_error = np.mean(errors)
    fig.add_vline(
        x=mean_error,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {mean_error:.2f}"
    )
    
    fig.update_layout(
        title='Forecast Error Distribution',
        xaxis_title='Forecast Error',
        yaxis_title='Frequency',
        height=400
    )
    
    return fig
```

---

### 7. Stockout Risk Visualization

**Purpose**: Show drugs at risk of stockout

**Chart Type**: **Gauge Chart** or **Risk Matrix**

**Visual Design**:
- Gauge: Risk level (Low/Medium/High)
- Risk matrix: Risk vs Impact
- Color coding: Green/Yellow/Red

**Implementation**:
```python
def create_stockout_risk_chart(risk_data: List[Dict]) -> go.Figure:
    """Create stockout risk visualization."""
    fig = go.Figure()
    
    drugs = [d['drug_code'] for d in risk_data]
    risk_scores = [d['risk_score'] for d in risk_data]
    days_until_stockout = [d.get('days_until_stockout', 0) for d in risk_data]
    
    # Scatter plot: Risk score vs Days until stockout
    fig.add_trace(go.Scatter(
        x=days_until_stockout,
        y=risk_scores,
        mode='markers+text',
        text=drugs,
        textposition='top center',
        marker=dict(
            size=15,
            color=risk_scores,
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Risk Score"),
            line=dict(width=2)
        )
    ))
    
    # Add risk zones
    fig.add_hrect(y0=0.7, y1=1.0, fillcolor="red", opacity=0.2, layer="below", line_width=0)
    fig.add_hrect(y0=0.4, y1=0.7, fillcolor="yellow", opacity=0.2, layer="below", line_width=0)
    fig.add_hrect(y0=0.0, y1=0.4, fillcolor="green", opacity=0.2, layer="below", line_width=0)
    
    fig.update_layout(
        title='Stockout Risk Matrix',
        xaxis_title='Days Until Potential Stockout',
        yaxis_title='Risk Score',
        height=500
    )
    
    return fig
```

---

## API Endpoints to Add

### 1. Forecast Endpoint
```
GET /api/ml/forecast/{drug_code}
Query params:
  - horizon_days: int (default: 30)
  - include_confidence: bool (default: true)
  - include_historical: bool (default: true)
```

### 2. Multi-Horizon Forecast
```
GET /api/ml/forecast/multi-horizon/{drug_code}
Query params:
  - horizons: str (comma-separated, e.g., "7,14,30,90")
```

### 3. Forecast Metrics
```
GET /api/ml/metrics/{drug_code}
GET /api/ml/metrics/overall
```

### 4. Anomaly Detection
```
GET /api/ml/anomalies
Query params:
  - start_date: YYYY-MM-DD
  - end_date: YYYY-MM-DD
  - drug_code: str (optional)
  - min_score: float (optional, default: 0.7)
```

### 5. Model Performance
```
GET /api/ml/model-performance
Query params:
  - drug_code: str (optional)
  - metric_type: str (mape, mae, rmse, r2)
```

### 6. Stockout Risk
```
GET /api/ml/stockout-risk
Query params:
  - limit: int (default: 20, top N risky drugs)
```

---

## Frontend Implementation Recommendations

### React/Next.js Chart Libraries

**Primary Recommendation: Recharts**
```bash
npm install recharts
```

**Why Recharts?**
- ✅ React-native, declarative API
- ✅ Good TypeScript support
- ✅ Responsive by default
- ✅ Easy to customize
- ✅ Active community

### Component Structure

```tsx
// components/ml/ForecastChart.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ForecastChartProps {
  historical: Array<{date: string, demand: number}>;
  forecast: Array<{date: string, demand: number, confidence_lower?: number, confidence_upper?: number}>;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({ historical, forecast }) => {
  const data = [...historical, ...forecast];
  
  return (
    <ResponsiveContainer width="100%" height={500}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="demand" 
          stroke="#8884d8" 
          strokeWidth={2}
          dot={false}
          name="Demand"
        />
        {/* Add confidence interval area if available */}
      </LineChart>
    </ResponsiveContainer>
  );
};
```

### Alternative: Chart.js with react-chartjs-2
```bash
npm install chart.js react-chartjs-2
```

---

## Integration with Existing Dashboard

### Extend Current Chart Types

**Modify `/api/dashboard/chart-data/<chart_type>` to support:**
- `forecast` - Forecast vs actual chart
- `anomalies` - Anomaly detection chart
- `metrics` - Model performance metrics

**Or create separate ML endpoints:**
- `/api/ml/charts/forecast`
- `/api/ml/charts/anomalies`
- `/api/ml/charts/metrics`

### Reuse Existing Patterns

Your existing `charts.py` already uses Plotly. **Extend it** with ML-specific chart functions:

```python
# backend/app/modules/ml/charts.py (new file)
from backend.app.modules.dashboard.charts import *  # Import base functions
# Add ML-specific chart functions here
```

---

## Implementation Priority

### Phase 1: Core Visualizations (Week 1-2)
1. ✅ **Forecast vs Actual Chart** - Most critical
2. ✅ **Forecast Accuracy Metrics** - KPI cards
3. ✅ **API Endpoints** - `/api/ml/forecast/{drug_code}`

### Phase 2: Advanced Visualizations (Week 3-4)
4. ✅ **Multi-Horizon Forecast** - Different time horizons
5. ✅ **Anomaly Detection Chart** - Visualize anomalies
6. ✅ **Model Performance Trends** - Track over time

### Phase 3: Specialized Visualizations (Week 5-6)
7. ✅ **Stockout Risk Matrix** - Risk visualization
8. ✅ **Error Distribution** - Error analysis
9. ✅ **Forecast Comparison** - Compare multiple models

---

## Data Format Standards

### Forecast Response Format
```json
{
  "success": true,
  "data": {
    "drug_code": "P733036",
    "forecast": [
      {
        "date": "2024-02-01",
        "demand": 450,
        "confidence_lower": 380,
        "confidence_upper": 520,
        "confidence_level": 0.8
      }
    ],
    "historical": [
      {
        "date": "2024-01-01",
        "demand": 420,
        "type": "actual"
      }
    ],
    "model_info": {
      "model_type": "xgboost",
      "training_samples": 730,
      "last_trained": "2024-01-15T10:30:00Z",
      "metrics": {
        "mape": 12.5,
        "mae": 45.2,
        "rmse": 58.7,
        "r2": 0.85
      }
    }
  }
}
```

---

## Next Steps

1. **Review this document** with your team
2. **Prioritize visualizations** based on business needs
3. **Extend existing charts.py** with ML chart functions
4. **Create ML API endpoints** following existing patterns
5. **Implement frontend components** using Recharts
6. **Test with sample predictions** before full integration

---

## Quick Reference: Chart Type → Use Case

| Chart Type | Use Case | Priority |
|------------|----------|----------|
| **Forecast vs Actual Line** | Show predictions vs history | ⭐⭐⭐ Critical |
| **Multi-Horizon Lines** | Compare different forecast periods | ⭐⭐ High |
| **KPI Cards** | Model accuracy metrics | ⭐⭐⭐ Critical |
| **Anomaly Scatter** | Highlight unusual patterns | ⭐⭐ High |
| **Performance Trend** | Track model improvements | ⭐ Medium |
| **Risk Matrix** | Stockout risk visualization | ⭐⭐ High |
| **Error Histogram** | Error distribution analysis | ⭐ Low |

---

This document provides a complete roadmap for integrating ML predictions into your dashboard. Start with Phase 1 visualizations and iterate based on user feedback.

