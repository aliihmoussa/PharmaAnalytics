# ML Dashboard Visualizations - Quick Reference

## 🎯 Essential Visualizations for ML Predictions

Based on your existing dashboard infrastructure, here are the **critical visualizations** you need to implement:

---

## 1. Forecast vs Actual Chart ⭐ **MOST CRITICAL**

**What**: Line chart showing historical demand (solid line) + predicted demand (dashed line) + confidence interval (shaded area)

**Why**: Core visualization for all ML predictions - shows model performance at a glance

**API**: `GET /api/ml/forecast/{drug_code}`

**Chart Type**: Multi-line chart with confidence bands

**Frontend Library**: Recharts `<LineChart>` or Chart.js

**Priority**: ⭐⭐⭐ **Start here!**

---

## 2. Model Accuracy Metrics (KPI Cards)

**What**: Display MAPE, MAE, RMSE, R² as dashboard cards

**Why**: Quick assessment of model quality

**API**: `GET /api/ml/metrics/{drug_code}`

**Chart Type**: KPI cards + optional bar chart for comparison

**Priority**: ⭐⭐⭐ **Essential for trust**

---

## 3. Anomaly Detection Visualization

**What**: Line chart with anomaly markers (red circles) on unusual data points

**Why**: Identify data quality issues and exceptional events

**API**: `GET /api/ml/anomalies`

**Chart Type**: Line chart with scatter markers

**Priority**: ⭐⭐ **High value**

---

## 4. Multi-Horizon Forecast

**What**: Multiple forecast lines for different time horizons (7d, 14d, 30d, 90d)

**Why**: Compare short-term vs long-term predictions

**API**: `GET /api/ml/forecast/multi-horizon/{drug_code}`

**Chart Type**: Multi-line chart

**Priority**: ⭐⭐ **Useful for planning**

---

## 5. Stockout Risk Matrix

**What**: Scatter plot showing risk score vs days until stockout

**Why**: Proactive inventory management

**API**: `GET /api/ml/stockout-risk`

**Chart Type**: Scatter plot with risk zones

**Priority**: ⭐⭐ **Business value**

---

## Implementation Priority

### Phase 1 (Week 1-2) - MVP
1. ✅ Forecast vs Actual Chart
2. ✅ Model Accuracy Metrics (KPI cards)

### Phase 2 (Week 3-4) - Enhanced
3. ✅ Anomaly Detection Chart
4. ✅ Multi-Horizon Forecast

### Phase 3 (Week 5+) - Advanced
5. ✅ Stockout Risk Matrix
6. ✅ Model Performance Trends
7. ✅ Error Distribution Analysis

---

## Quick Integration Guide

### Backend (Python/Flask)

**Extend existing charts.py:**
```python
# backend/app/modules/ml/charts.py
from backend.app.modules.dashboard.charts import *

def create_forecast_comparison_chart(historical, forecast):
    # Implementation (see ML_DASHBOARD_VISUALIZATIONS.md)
    pass
```

**Add ML routes:**
```python
# backend/app/modules/ml/routes.py
@ml_bp.route('/forecast/<drug_code>', methods=['GET'])
def get_forecast(drug_code):
    # Return forecast data
    pass
```

### Frontend (React/Next.js)

**Install Recharts:**
```bash
npm install recharts
```

**Create Forecast Component:**
```tsx
import { LineChart, Line } from 'recharts';

<LineChart data={forecastData}>
  <Line dataKey="actual" stroke="#1f77b4" />
  <Line dataKey="forecast" stroke="#ff7f0e" strokeDasharray="5 5" />
</LineChart>
```

---

## API Response Format

### Forecast Endpoint Response
```json
{
  "success": true,
  "data": {
    "drug_code": "P733036",
    "historical": [
      {"date": "2024-01-01", "demand": 420, "type": "actual"}
    ],
    "forecast": [
      {
        "date": "2024-02-01",
        "demand": 450,
        "confidence_lower": 380,
        "confidence_upper": 520
      }
    ],
    "model_info": {
      "model_type": "xgboost",
      "mape": 12.5
    }
  }
}
```

---

## Chart Library Recommendations

| Library | Best For | Install |
|---------|----------|---------|
| **Recharts** | Line charts, general use | `npm install recharts` |
| **Chart.js** | All chart types | `npm install chart.js react-chartjs-2` |
| **Nivo** | Heatmaps, advanced charts | `npm install @nivo/core @nivo/line` |
| **Plotly.js** | Interactive, 3D charts | `npm install plotly.js react-plotly.js` |

**Recommendation**: Start with **Recharts** - easiest to integrate with your React/Next.js setup.

---

## Existing Dashboard Integration

### Extend Current Endpoint
```python
# backend/app/modules/dashboard/services.py

def get_chart_data(self, chart_type: str, request_data):
    chart_processors = {
        'trends': self._process_trends_chart,
        'seasonal': self._process_seasonal_chart,
        'forecast': self._process_forecast_chart,  # ADD THIS
    }
    # ...
```

### Or Create Separate ML Endpoints
```python
# backend/app/modules/ml/routes.py
@ml_bp.route('/forecast/<drug_code>/chart')
def get_forecast_chart(drug_code):
    # Return chart-ready data
    pass
```

**Recommendation**: Create separate ML endpoints initially, integrate later.

---

## Data Flow

```
User Request
    ↓
Frontend: GET /api/ml/forecast/{drug_code}
    ↓
Backend: MLService.get_forecast_with_history()
    ↓
ML Model: Generate predictions
    ↓
Data Loader: Fetch historical data from PostgreSQL
    ↓
Response: {historical: [...], forecast: [...], model_info: {...}}
    ↓
Frontend: Render with Recharts/Chart.js
```

---

## Key Files to Create/Modify

### New Files
- `backend/app/modules/ml/charts.py` - ML chart functions
- `backend/app/modules/ml/routes.py` - ML API endpoints
- `backend/app/modules/ml/requests.py` - Request models

### Modify Existing Files
- `backend/app/__init__.py` - Register ML blueprint
- `backend/app/modules/dashboard/services.py` - Add forecast chart processor (optional)

---

## Testing Checklist

- [ ] Forecast endpoint returns correct data format
- [ ] Historical and forecast data are properly separated
- [ ] Confidence intervals are included when requested
- [ ] Chart renders correctly in frontend
- [ ] Dates are properly formatted
- [ ] Error handling works

---

## Next Steps

1. **Read**: `ML_DASHBOARD_VISUALIZATIONS.md` - Detailed visualization specs
2. **Read**: `ML_DASHBOARD_IMPLEMENTATION_PLAN.md` - Step-by-step guide
3. **Start**: Create `backend/app/modules/ml/charts.py`
4. **Test**: Generate sample forecast data and test chart rendering
5. **Iterate**: Add more visualizations based on feedback

---

## Quick Start Command

```bash
# 1. Create ML charts file
touch backend/app/modules/ml/charts.py

# 2. Create ML routes file
touch backend/app/modules/ml/routes.py

# 3. Install frontend library
npm install recharts

# 4. Test with sample data
# (See ML_DASHBOARD_IMPLEMENTATION_PLAN.md for details)
```

---

**Remember**: Start simple with Forecast vs Actual chart, then iterate based on user needs!

