# ML Dashboard Integration - Step-by-Step Implementation Plan

## Overview

This document provides a **practical, step-by-step plan** to integrate ML predictions into your existing dashboard infrastructure.

## Current State Analysis

### ✅ What You Have
- Dashboard API endpoints (`/api/dashboard/*`)
- Chart generation utilities (`charts.py` with Plotly)
- Pre-formatted chart data endpoints (`/chart-data/<type>`)
- Consistent API response format
- Date range filtering support

### 🎯 What You Need to Add
- ML-specific chart functions
- ML API endpoints
- Forecast data serialization
- Integration with existing dashboard patterns

---

## Implementation Steps

### Step 1: Extend Chart Utilities (Day 1-2)

**File**: `backend/app/modules/ml/charts.py` (NEW)

```python
"""ML-specific chart generation utilities."""

import plotly.graph_objects as go
from typing import List, Dict, Optional
from backend.app.modules.dashboard.charts import *  # Reuse base utilities

def create_forecast_comparison_chart(
    historical_data: List[Dict],
    forecast_data: List[Dict],
    show_confidence: bool = True
) -> go.Figure:
    """
    Create forecast vs actual comparison chart.
    
    Args:
        historical_data: List of {date, demand} dicts
        forecast_data: List of {date, demand, confidence_lower, confidence_upper} dicts
        show_confidence: Whether to show confidence intervals
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Historical data (actual) - solid line
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
    
    # Forecast data (predicted) - dashed line
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
        
        # Confidence interval (shaded area)
        if show_confidence and forecast_data and 'confidence_lower' in forecast_data[0]:
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
    
    # Vertical line separating historical from forecast
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


def create_anomaly_detection_chart(
    data: List[Dict],
    anomalies: List[Dict]
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
    if anomalies:
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

**Action**: Create this file and test with sample data.

---

### Step 2: Create ML Service Layer (Day 2-3)

**File**: `backend/app/modules/ml/services.py` (EXTEND)

```python
"""ML Service - Extend existing service pattern."""

from backend.app.shared.base_service import BaseService
from backend.app.modules.ml.models.demand_forecast import DrugDemandForecaster
from backend.app.modules.ml.utils.data_loader import MLDataLoader
from backend.app.modules.ml.features.time_features import (
    create_time_features,
    create_lag_features,
    create_rolling_features
)
from backend.app.modules.dashboard.queries import AnalyticsDAL
from datetime import date, timedelta
from typing import Dict, List, Optional
import polars as pl
import numpy as np

class MLService(BaseService):
    """Service for ML predictions - follows existing service pattern."""
    
    def __init__(self):
        """Initialize ML service."""
        super().__init__()
        self.data_loader = MLDataLoader()
        self.dal = AnalyticsDAL()  # Reuse existing DAL
    
    def get_forecast_with_history(
        self,
        drug_code: str,
        forecast_horizon_days: int = 30,
        training_months: int = 24,
        include_confidence: bool = True
    ) -> Dict:
        """
        Get forecast with historical data for visualization.
        
        Returns data in format ready for forecast chart.
        """
        # Get forecast
        forecast_result = self.forecast_drug_demand(
            drug_code=drug_code,
            forecast_horizon_days=forecast_horizon_days,
            training_months=training_months
        )
        
        # Get historical data for comparison
        end_date = date.today()
        start_date = end_date - timedelta(days=90)  # Last 90 days for context
        
        with self.dal:
            historical_raw = self.dal.get_drug_demand_time_series(
                start_date=start_date,
                end_date=end_date,
                drug_code=drug_code,
                granularity='daily'
            )
        
        # Format historical data
        historical = [
            {
                'date': row['date'].isoformat() if isinstance(row['date'], date) else str(row['date']),
                'demand': int(row.get('quantity', 0)),
                'type': 'actual'
            }
            for row in historical_raw
        ]
        
        # Format forecast data
        forecast = [
            {
                'date': forecast_date,
                'demand': int(pred),
                'type': 'predicted',
                'confidence_lower': int(pred * 0.85) if include_confidence else None,
                'confidence_upper': int(pred * 1.15) if include_confidence else None
            }
            for forecast_date, pred in zip(forecast_result['forecast_dates'], forecast_result['forecasted_demand'])
        ]
        
        return {
            'drug_code': drug_code,
            'historical': historical,
            'forecast': forecast,
            'model_info': {
                'model_type': forecast_result['model_type'],
                'training_samples': forecast_result['training_samples'],
                'forecast_horizon_days': forecast_horizon_days
            }
        }
    
    def forecast_drug_demand(
        self,
        drug_code: str,
        forecast_horizon_days: int = 30,
        training_months: int = 24
    ) -> Dict:
        """Forecast drug demand (existing method)."""
        # ... (implementation from ML_QUICK_START.md)
        pass
```

**Action**: Extend existing ML service with visualization-ready methods.

---

### Step 3: Create ML API Endpoints (Day 3-4)

**File**: `backend/app/modules/ml/routes.py` (NEW)

```python
"""ML routes - API endpoints for ML predictions."""

from flask import Blueprint, request, g
from backend.app.modules.ml.services import MLService
from backend.app.modules.ml.requests import ForecastRequest  # Create this
from backend.app.shared.middleware import handle_exceptions, format_success_response, validate_request
from pydantic import ValidationError

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')


@ml_bp.route('/forecast/<drug_code>', methods=['GET'])
@handle_exceptions
def get_forecast(drug_code: str):
    """
    GET /api/ml/forecast/{drug_code}
    
    Get drug demand forecast with historical data for visualization.
    
    Query params:
    - horizon_days: int (default: 30)
    - training_months: int (default: 24)
    - include_confidence: bool (default: true)
    - include_historical: bool (default: true)
    """
    horizon_days = int(request.args.get('horizon_days', 30))
    training_months = int(request.args.get('training_months', 24))
    include_confidence = request.args.get('include_confidence', 'true').lower() == 'true'
    include_historical = request.args.get('include_historical', 'true').lower() == 'true'
    
    service = MLService()
    result = service.get_forecast_with_history(
        drug_code=drug_code,
        forecast_horizon_days=horizon_days,
        training_months=training_months,
        include_confidence=include_confidence
    )
    
    # Remove historical if not requested
    if not include_historical:
        result.pop('historical', None)
    
    return format_success_response(result)


@ml_bp.route('/forecast/<drug_code>/chart', methods=['GET'])
@handle_exceptions
def get_forecast_chart(drug_code: str):
    """
    GET /api/ml/forecast/{drug_code}/chart
    
    Get pre-formatted chart data for forecast visualization.
    Similar to existing /api/dashboard/chart-data/<type> pattern.
    """
    horizon_days = int(request.args.get('horizon_days', 30))
    training_months = int(request.args.get('training_months', 24))
    
    service = MLService()
    forecast_data = service.get_forecast_with_history(
        drug_code=drug_code,
        forecast_horizon_days=horizon_days,
        training_months=training_months
    )
    
    # Format for frontend chart library (e.g., Chart.js format)
    chart_data = {
        'chart_type': 'forecast',
        'data': {
            'labels': [d['date'] for d in forecast_data['historical'] + forecast_data['forecast']],
            'datasets': [
                {
                    'label': 'Actual Demand',
                    'data': [d['demand'] for d in forecast_data['historical']],
                    'borderColor': '#1f77b4',
                    'backgroundColor': 'rgba(31, 119, 180, 0.1)',
                    'type': 'line'
                },
                {
                    'label': 'Predicted Demand',
                    'data': [None] * len(forecast_data['historical']) + [d['demand'] for d in forecast_data['forecast']],
                    'borderColor': '#ff7f0e',
                    'backgroundColor': 'rgba(255, 127, 14, 0.1)',
                    'borderDash': [5, 5],
                    'type': 'line'
                }
            ]
        },
        'config': {
            'type': 'line',
            'options': {
                'scales': {
                    'x': {'title': {'display': True, 'text': 'Date'}},
                    'y': {'title': {'display': True, 'text': 'Demand'}}
                }
            }
        }
    }
    
    return format_success_response(chart_data)


@ml_bp.route('/metrics/<drug_code>', methods=['GET'])
@handle_exceptions
def get_forecast_metrics(drug_code: str):
    """
    GET /api/ml/metrics/{drug_code}
    
    Get forecast accuracy metrics for a drug.
    """
    service = MLService()
    # Implement metrics calculation
    metrics = service.get_model_metrics(drug_code)
    return format_success_response(metrics)


@ml_bp.route('/anomalies', methods=['GET'])
@handle_exceptions
def get_anomalies():
    """
    GET /api/ml/anomalies
    
    Get detected anomalies.
    
    Query params:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    - drug_code: str (optional)
    - min_score: float (optional, default: 0.7)
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    drug_code = request.args.get('drug_code')
    min_score = float(request.args.get('min_score', 0.7))
    
    service = MLService()
    anomalies = service.detect_anomalies(
        start_date=start_date,
        end_date=end_date,
        drug_code=drug_code,
        min_score=min_score
    )
    
    return format_success_response({'anomalies': anomalies})
```

**Action**: Create ML routes following existing dashboard route patterns.

---

### Step 4: Register ML Blueprint (Day 4)

**File**: `backend/app/__init__.py` (MODIFY)

```python
# Add to create_app() function
from backend.app.modules.ml.routes import ml_bp

def create_app():
    # ... existing code ...
    
    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ingestion_bp)
    app.register_blueprint(ml_bp)  # ADD THIS
    
    return app
```

**Action**: Register ML blueprint in app factory.

---

### Step 5: Extend Dashboard Chart Data Endpoint (Day 4-5)

**File**: `backend/app/modules/dashboard/services.py` (MODIFY)

```python
# Add to DashboardService class

def get_chart_data(self, chart_type: str, request_data: ChartDataRequest) -> Dict:
    """Get pre-formatted chart data for frontend."""
    chart_processors = {
        'trends': self._process_trends_chart,
        'seasonal': self._process_seasonal_chart,
        'department': self._process_department_chart,
        'forecast': self._process_forecast_chart,  # ADD THIS
        'anomalies': self._process_anomalies_chart,  # ADD THIS
    }
    
    processor = chart_processors.get(chart_type)
    if not processor:
        raise InvalidChartTypeException(chart_type)
    
    return processor(request_data)

def _process_forecast_chart(self, request_data: ChartDataRequest) -> Dict:
    """Format data for forecast chart."""
    from backend.app.modules.ml.services import MLService
    
    drug_code = request_data.drug_code  # Add drug_code to ChartDataRequest
    if not drug_code:
        raise ValueError("drug_code required for forecast chart")
    
    ml_service = MLService()
    forecast_data = ml_service.get_forecast_with_history(
        drug_code=drug_code,
        forecast_horizon_days=30
    )
    
    return {
        'chart_type': 'forecast',
        'data': forecast_data,
        'config': {
            'type': 'line',
            'x_axis': 'date',
            'y_axis': 'demand'
        }
    }
```

**Action**: Extend existing chart data endpoint to support ML charts.

---

### Step 6: Create Request/Response Models (Day 5)

**File**: `backend/app/modules/ml/requests.py` (NEW)

```python
"""Request models for ML endpoints."""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date

class ForecastRequest(BaseModel):
    """Request model for forecast endpoint."""
    drug_code: str = Field(..., description="Drug code to forecast")
    horizon_days: int = Field(30, ge=1, le=365, description="Forecast horizon in days")
    training_months: int = Field(24, ge=6, le=48, description="Training data months")
    include_confidence: bool = Field(True, description="Include confidence intervals")
    include_historical: bool = Field(True, description="Include historical data")
    
    @classmethod
    def from_query_params(cls, drug_code: str, **kwargs):
        """Create from query parameters."""
        return cls(
            drug_code=drug_code,
            horizon_days=int(kwargs.get('horizon_days', 30)),
            training_months=int(kwargs.get('training_months', 24)),
            include_confidence=kwargs.get('include_confidence', 'true').lower() == 'true',
            include_historical=kwargs.get('include_historical', 'true').lower() == 'true'
        )


class AnomalyDetectionRequest(BaseModel):
    """Request model for anomaly detection."""
    start_date: date
    end_date: date
    drug_code: Optional[str] = None
    min_score: float = Field(0.7, ge=0.0, le=1.0)
    
    @classmethod
    def from_query_params(cls, **kwargs):
        """Create from query parameters."""
        return cls(
            start_date=date.fromisoformat(kwargs['start_date']),
            end_date=date.fromisoformat(kwargs['end_date']),
            drug_code=kwargs.get('drug_code'),
            min_score=float(kwargs.get('min_score', 0.7))
        )
```

**Action**: Create request models following existing patterns.

---

## Testing Checklist

### API Endpoints
- [ ] `GET /api/ml/forecast/{drug_code}` returns correct format
- [ ] `GET /api/ml/forecast/{drug_code}/chart` returns chart-ready data
- [ ] `GET /api/ml/metrics/{drug_code}` returns metrics
- [ ] `GET /api/ml/anomalies` returns anomalies

### Data Format
- [ ] Forecast data includes historical and predicted
- [ ] Confidence intervals are included when requested
- [ ] Dates are properly formatted (ISO format)
- [ ] Response matches frontend expectations

### Integration
- [ ] ML charts work with existing dashboard
- [ ] Chart data endpoint supports 'forecast' type
- [ ] Error handling follows existing patterns

---

## Frontend Integration (Next Steps)

### 1. Create Forecast Chart Component

```tsx
// components/ml/ForecastChart.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ForecastChartProps {
  data: {
    historical: Array<{date: string, demand: number}>;
    forecast: Array<{date: string, demand: number, confidence_lower?: number, confidence_upper?: number}>;
  };
}

export const ForecastChart: React.FC<ForecastChartProps> = ({ data }) => {
  // Combine historical and forecast data
  const chartData = [
    ...data.historical.map(d => ({ ...d, type: 'actual' })),
    ...data.forecast.map(d => ({ ...d, type: 'forecast' }))
  ];
  
  return (
    <ResponsiveContainer width="100%" height={500}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="demand" 
          stroke="#1f77b4" 
          strokeWidth={2}
          dot={false}
          name="Demand"
          dataKey="demand"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

### 2. Fetch and Display

```tsx
// pages/ml/forecast/[drugCode].tsx
import { useEffect, useState } from 'react';
import { ForecastChart } from '@/components/ml/ForecastChart';

export default function ForecastPage({ drugCode }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch(`/api/ml/forecast/${drugCode}?horizon_days=30`)
      .then(res => res.json())
      .then(result => setData(result.data));
  }, [drugCode]);
  
  if (!data) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>Forecast for {drugCode}</h1>
      <ForecastChart data={data} />
    </div>
  );
}
```

---

## Summary

### What You're Building
1. **ML Chart Utilities** - Extend existing `charts.py`
2. **ML Service Layer** - Follow existing service patterns
3. **ML API Endpoints** - Follow existing route patterns
4. **Integration** - Extend existing dashboard endpoints

### Key Principles
- ✅ **Reuse existing patterns** - Don't reinvent the wheel
- ✅ **Consistent API format** - Match existing dashboard APIs
- ✅ **Follow existing structure** - Services, DAL, Routes
- ✅ **Extend, don't replace** - Build on what works

### Timeline
- **Week 1**: Steps 1-3 (Charts, Services, Routes)
- **Week 2**: Steps 4-6 (Integration, Models, Testing)
- **Week 3**: Frontend integration and polish

---

**Next Action**: Start with Step 1 - Create `backend/app/modules/ml/charts.py` and test with sample data.

