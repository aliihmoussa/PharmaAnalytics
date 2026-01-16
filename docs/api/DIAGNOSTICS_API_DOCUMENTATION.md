# Diagnostics API Documentation

Complete guide for using the Diagnostics API endpoints in Next.js frontend applications.

---

## 📋 Table of Contents

1. [API Overview](#api-overview)
2. [Endpoint Details](#endpoint-details)
3. [Request Examples](#request-examples)
4. [Response Structure](#response-structure)
5. [Next.js Integration Guide](#nextjs-integration-guide)
6. [Chart Visualization Ideas](#chart-visualization-ideas)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## 🎯 API Overview

The Diagnostics API provides comprehensive drug demand analysis including:
- **Data Health Metrics**: Completeness, outliers, data quality
- **Time Series Characteristics**: Trend, volatility, seasonality
- **Statistical Analysis**: Decomposition, autocorrelation, classification
- **Risk Assessment**: Forecast reliability, recommendations

**Base URL**: `/api/diagnostics`

---

## 📡 Endpoint Details

### **GET `/api/diagnostics/features/<drug_code>`**

Get comprehensive drug features and profiling data.

#### **URL Parameters**
- `drug_code` (required): Drug code identifier (e.g., `P182054`)

#### **Query Parameters**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `department` | integer | No | `null` | Department ID (cr) to filter by specific department |
| `start_date` | string | No | `null` | Start date in `YYYY-MM-DD` format (defaults to 2 years ago) |
| `end_date` | string | No | `null` | End date in `YYYY-MM-DD` format (defaults to today) |
| `use_cache` | boolean | No | `true` | Whether to use cached results (24h TTL) |

#### **Example Requests**

```bash
# Basic request
GET /api/diagnostics/features/P182054

# With department filter
GET /api/diagnostics/features/P182054?department=5

# With date range
GET /api/diagnostics/features/P182054?start_date=2024-01-01&end_date=2024-12-31

# Full example
GET /api/diagnostics/features/P182054?department=5&start_date=2024-01-01&end_date=2024-12-31&use_cache=true
```

#### **Response Status Codes**
- `200`: Success
- `400`: Invalid parameters (e.g., invalid date format)
- `404`: No data found for the drug code
- `500`: Internal server error

---

## 📦 Response Structure

### **Success Response (200)**

```json
{
  "success": true,
  "data": {
    "drug_code": "P182054",
    "department": 5,
    "data_health": {
      "history_length_days": 730,
      "missing_days": 0,
      "missing_percentage": 0.0,
      "zero_demand_frequency": 0.15,
      "zero_demand_count": 110,
      "data_completeness_score": 1.0,
      "date_range": {
        "start": "2023-01-01T00:00:00",
        "end": "2024-12-31T00:00:00"
      },
      "outlier_count": 12,
      "outlier_percentage": 1.64
    },
    "time_series_characteristics": {
      "mean_demand": 45.2,
      "std_demand": 12.8,
      "volatility": 0.283,
      "trend": "increasing",
      "min_demand": 0.0,
      "max_demand": 89.5,
      "median_demand": 42.0,
      "stationarity": "non-stationary",
      "seasonality_detected": true,
      "seasonal_periods": [7, 30],
      "seasonality_strength": {
        "weekly": 0.65,
        "monthly": 0.42
      }
    },
    "outliers": {
      "count": 12,
      "percentage": 1.64,
      "indices": ["2024-03-15", "2024-06-22", ...],
      "values": [125.5, 98.3, ...]
    },
    "decomposition": {
      "model": "additive",
      "period": 7,
      "trend": {
        "direction": "increasing",
        "strength": 0.15
      },
      "seasonal_strength": 0.65,
      "residual_variance": 8.2,
      "decomposition_quality": "good"
    },
    "acf_pacf": {
      "significant_lags": [1, 7, 14],
      "seasonal_lags": [7, 14, 21, 28],
      "arima_suggested_orders": {
        "ar": 1,
        "ma": 1,
        "seasonal": true
      },
      "acf_summary": {
        "max_acf_lag": 7,
        "max_acf_value": 0.68
      }
    },
    "classification": {
      "category": "smooth",
      "confidence": 0.85,
      "characteristics": {
        "regular": true,
        "seasonal": true,
        "erratic": false
      },
      "metrics": {
        "demand_frequency": 0.85,
        "zero_frequency": 0.15,
        "volatility": 0.283,
        "mean_demand": 45.2,
        "seasonal_strength": 0.65
      }
    },
    "risks": {
      "data_quality_issues": [],
      "forecast_reliability": "high",
      "recommendations": [
        "Strong seasonality detected - use seasonal models",
        "Data quality is good for accurate forecasting"
      ]
    },
    "profiled_at": "2024-12-31T10:30:00.000000"
  },
  "meta": {
    "status_code": 200
  }
}
```

### **Error Response (400/404/500)**

```json
{
  "success": false,
  "data": {
    "error": "No data found for drug_code=P182054"
  },
  "meta": {
    "status_code": 404
  }
}
```

---

## ⚛️ Next.js Integration Guide

### **1. API Client Setup**

Create a utility file for API calls:

```typescript
// lib/api/diagnostics.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface DiagnosticsParams {
  drug_code: string;
  department?: number;
  start_date?: string; // YYYY-MM-DD
  end_date?: string;   // YYYY-MM-DD
  use_cache?: boolean;
}

export interface DiagnosticsResponse {
  success: boolean;
  data: {
    drug_code: string;
    department: number | null;
    data_health: DataHealth;
    time_series_characteristics: TimeSeriesCharacteristics;
    outliers: Outliers;
    decomposition: Decomposition;
    acf_pacf: AcfPacf;
    classification: Classification;
    risks: Risks;
    profiled_at: string;
  };
  meta: {
    status_code: number;
  };
}

// Type definitions (add these based on response structure)
export interface DataHealth {
  history_length_days: number;
  missing_days: number;
  missing_percentage: number;
  zero_demand_frequency: number;
  zero_demand_count: number;
  data_completeness_score: number;
  date_range: {
    start: string;
    end: string;
  };
  outlier_count: number;
  outlier_percentage: number;
}

// ... (add other interfaces)

export async function getDrugDiagnostics(
  params: DiagnosticsParams
): Promise<DiagnosticsResponse> {
  const { drug_code, department, start_date, end_date, use_cache } = params;
  
  const queryParams = new URLSearchParams();
  if (department !== undefined) queryParams.append('department', department.toString());
  if (start_date) queryParams.append('start_date', start_date);
  if (end_date) queryParams.append('end_date', end_date);
  if (use_cache !== undefined) queryParams.append('use_cache', use_cache.toString());
  
  const url = `${API_BASE_URL}/api/diagnostics/features/${drug_code}?${queryParams.toString()}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.data?.error || 'Failed to fetch diagnostics');
  }
  
  return response.json();
}
```

### **2. React Hook for Data Fetching**

```typescript
// hooks/useDiagnostics.ts

import { useState, useEffect } from 'react';
import { getDrugDiagnostics, DiagnosticsParams, DiagnosticsResponse } from '@/lib/api/diagnostics';

export function useDiagnostics(params: DiagnosticsParams) {
  const [data, setData] = useState<DiagnosticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const result = await getDrugDiagnostics(params);
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }
    
    if (params.drug_code) {
      fetchData();
    }
  }, [params.drug_code, params.department, params.start_date, params.end_date]);
  
  return { data, loading, error };
}
```

### **3. Component Example**

```typescript
// components/DiagnosticsCard.tsx

'use client';

import { useDiagnostics } from '@/hooks/useDiagnostics';

interface DiagnosticsCardProps {
  drugCode: string;
  department?: number;
}

export function DiagnosticsCard({ drugCode, department }: DiagnosticsCardProps) {
  const { data, loading, error } = useDiagnostics({
    drug_code: drugCode,
    department,
    use_cache: true,
  });
  
  if (loading) return <div>Loading diagnostics...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data?.success) return <div>No data available</div>;
  
  const diagnostics = data.data;
  
  return (
    <div className="diagnostics-container">
      <h2>Drug Diagnostics: {diagnostics.drug_code}</h2>
      
      {/* Data Health Section */}
      <section>
        <h3>Data Health</h3>
        <p>Completeness: {(diagnostics.data_health.data_completeness_score * 100).toFixed(1)}%</p>
        <p>Outliers: {diagnostics.data_health.outlier_count} ({diagnostics.data_health.outlier_percentage.toFixed(2)}%)</p>
      </section>
      
      {/* Classification Section */}
      <section>
        <h3>Classification</h3>
        <p>Category: {diagnostics.classification.category}</p>
        <p>Confidence: {(diagnostics.classification.confidence * 100).toFixed(1)}%</p>
      </section>
      
      {/* Risks Section */}
      <section>
        <h3>Risks & Recommendations</h3>
        <p>Forecast Reliability: {diagnostics.risks.forecast_reliability}</p>
        <ul>
          {diagnostics.risks.recommendations.map((rec, i) => (
            <li key={i}>{rec}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
```

---

## 📊 Chart Visualization Ideas

### **1. Data Health Dashboard**

#### **A. Data Completeness Gauge Chart**
- **Data Source**: `data_health.data_completeness_score`
- **Chart Type**: Gauge/Semi-circle Progress Chart
- **Visualization**: 
  - Show completeness score (0-100%)
  - Color coding: Green (>90%), Yellow (70-90%), Red (<70%)
  - Include missing days count

#### **B. Outlier Distribution Chart**
- **Data Source**: `outliers.count`, `outliers.percentage`, `outliers.values`
- **Chart Type**: Scatter Plot or Box Plot
- **Visualization**:
  - X-axis: Date (from `outliers.indices`)
  - Y-axis: Outlier values
  - Highlight outliers on time series
  - Show outlier percentage as annotation

#### **C. Zero Demand Frequency Chart**
- **Data Source**: `data_health.zero_demand_frequency`, `data_health.zero_demand_count`
- **Chart Type**: Donut Chart or Progress Bar
- **Visualization**:
  - Show percentage of days with zero demand
  - Compare against total days
  - Useful for intermittent demand detection

---

### **2. Time Series Characteristics**

#### **A. Trend Analysis Chart**
- **Data Source**: `time_series_characteristics.trend`, `time_series_characteristics.mean_demand`
- **Chart Type**: Line Chart with Trend Indicator
- **Visualization**:
  - Show trend direction (increasing/decreasing/stable)
  - Display trend strength as arrow or indicator
  - Include mean demand as reference line

#### **B. Volatility Indicator**
- **Data Source**: `time_series_characteristics.volatility`
- **Chart Type**: Gauge Chart or Progress Bar
- **Visualization**:
  - Show volatility score (0-1 scale)
  - Color coding: Low (<0.2), Medium (0.2-0.5), High (>0.5)
  - Include std_demand and mean_demand for context

#### **C. Demand Distribution Chart**
- **Data Source**: `time_series_characteristics.min_demand`, `max_demand`, `mean_demand`, `median_demand`
- **Chart Type**: Box Plot or Violin Plot
- **Visualization**:
  - Show min, max, mean, median
  - Display distribution shape
  - Highlight outliers if any

---

### **3. Seasonality Analysis**

#### **A. Seasonality Strength Chart**
- **Data Source**: `time_series_characteristics.seasonality_strength`
- **Chart Type**: Bar Chart or Radar Chart
- **Visualization**:
  - Show weekly and monthly seasonality strength
  - Compare different seasonal periods
  - Use color intensity to show strength

#### **B. Seasonal Period Indicators**
- **Data Source**: `time_series_characteristics.seasonal_periods`
- **Chart Type**: Badge/Indicator Cards
- **Visualization**:
  - Display detected seasonal periods (7, 30, etc.)
  - Show as badges with strength values
  - Highlight primary seasonal period

---

### **4. Decomposition Visualization**

#### **A. Decomposition Components Chart**
- **Data Source**: `decomposition.trend`, `decomposition.seasonal_strength`
- **Chart Type**: Multi-line Chart (if you fetch raw data) or Summary Cards
- **Visualization**:
  - Show trend direction and strength
  - Display seasonal strength score
  - Show decomposition quality indicator

#### **B. Residual Variance Chart**
- **Data Source**: `decomposition.residual_variance`
- **Chart Type**: Gauge Chart
- **Visualization**:
  - Show residual variance as quality metric
  - Lower variance = better decomposition
  - Include quality label (good/weak)

---

### **5. Autocorrelation Analysis**

#### **A. Significant Lags Chart**
- **Data Source**: `acf_pacf.significant_lags`, `acf_pacf.seasonal_lags`
- **Chart Type**: Bar Chart or Heatmap
- **Visualization**:
  - Show significant lags as bars
  - Highlight seasonal lags differently
  - Display max ACF value and lag

#### **B. ARIMA Suggestions Display**
- **Data Source**: `acf_pacf.arima_suggested_orders`
- **Chart Type**: Info Cards or Badges
- **Visualization**:
  - Display suggested AR, MA, and seasonal orders
  - Show as formatted text: "ARIMA(1,0,1) with seasonal"
  - Include confidence indicators

---

### **6. Classification & Risk Assessment**

#### **A. Drug Category Classification**
- **Data Source**: `classification.category`, `classification.confidence`
- **Chart Type**: Badge with Confidence Meter
- **Visualization**:
  - Display category (smooth, intermittent, erratic, etc.)
  - Show confidence as progress bar or gauge
  - Use color coding for different categories

#### **B. Characteristics Indicators**
- **Data Source**: `classification.characteristics`
- **Chart Type**: Icon Grid or Checkbox List
- **Visualization**:
  - Show characteristics as icons/badges:
    - ✅ Regular
    - ✅ Seasonal
    - ⚠️ Erratic
  - Use visual indicators (checkmarks, warnings)

#### **C. Risk Assessment Dashboard**
- **Data Source**: `risks.forecast_reliability`, `risks.data_quality_issues`, `risks.recommendations`
- **Chart Type**: Alert Cards or Status Dashboard
- **Visualization**:
  - Show forecast reliability as status badge (High/Medium/Low)
  - List data quality issues as warning cards
  - Display recommendations as actionable items
  - Use color coding: Green (high), Yellow (medium), Red (low)

---

### **7. Comprehensive Dashboard Layout**

#### **Suggested Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  Drug Diagnostics: P182054                              │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Data Health  │  │ Classification│  │ Risk Level   │ │
│  │ Gauge Chart  │  │ Category Badge│  │ Status Badge │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │  Time Series Characteristics                     │  │
│  │  [Trend Indicator] [Volatility Gauge] [Stats]   │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │  Seasonality Analysis                            │  │
│  │  [Weekly Strength] [Monthly Strength] [Periods]  │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │  Outlier Detection                               │  │
│  │  [Scatter Plot with Outliers Highlighted]       │  │
│  └──────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │  Recommendations                                 │  │
│  │  [List of actionable recommendations]            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Recommended Chart Libraries for Next.js

### **1. Recharts** (Recommended)
- **Pros**: React-friendly, TypeScript support, responsive
- **Best for**: Line charts, bar charts, gauges, scatter plots
- **Install**: `npm install recharts`

### **2. Chart.js with react-chartjs-2**
- **Pros**: Extensive chart types, good documentation
- **Best for**: Complex visualizations, radar charts
- **Install**: `npm install chart.js react-chartjs-2`

### **3. Victory**
- **Pros**: Beautiful defaults, animation support
- **Best for**: Interactive dashboards
- **Install**: `npm install victory`

### **4. Nivo**
- **Pros**: Beautiful, responsive, many chart types
- **Best for**: Modern dashboards, heatmaps
- **Install**: `npm install @nivo/core @nivo/bar @nivo/line`

### **5. ApexCharts**
- **Pros**: Professional look, many chart types
- **Best for**: Gauge charts, advanced visualizations
- **Install**: `npm install react-apexcharts apexcharts`

---

## ⚠️ Error Handling

### **Common Error Scenarios**

1. **No Data Found (404)**
   ```typescript
   if (response.status === 404) {
     // Show message: "No data available for this drug code"
   }
   ```

2. **Invalid Parameters (400)**
   ```typescript
   if (response.status === 400) {
     // Show validation error message
   }
   ```

3. **Server Error (500)**
   ```typescript
   if (response.status === 500) {
     // Show generic error, suggest retry
   }
   ```

4. **Network Errors**
   ```typescript
   try {
     const data = await getDrugDiagnostics(params);
   } catch (error) {
     if (error instanceof TypeError) {
       // Network error - show offline message
     }
   }
   ```

---

## 💡 Best Practices

### **1. Caching Strategy**
- Use `use_cache=true` for production (default)
- Set `use_cache=false` only when you need fresh data
- Cache expires after 24 hours automatically

### **2. Loading States**
- Show skeleton loaders during data fetch
- Display progress indicators for long-running requests

### **3. Data Validation**
- Validate `drug_code` format before API call
- Validate date formats (YYYY-MM-DD)
- Handle null/undefined department values

### **4. Performance Optimization**
- Use React Query or SWR for automatic caching and refetching
- Debounce rapid parameter changes
- Memoize expensive calculations

### **5. User Experience**
- Show helpful error messages
- Provide fallback UI for missing data
- Display loading states appropriately
- Use progressive disclosure for complex data

### **6. Type Safety**
- Define TypeScript interfaces for all response types
- Use type guards for runtime validation
- Leverage TypeScript's strict mode

---

## 📝 Example: Complete Next.js Component

```typescript
// components/DiagnosticsDashboard.tsx

'use client';

import { useState } from 'react';
import { useDiagnostics } from '@/hooks/useDiagnostics';
import { 
  GaugeChart, 
  BarChart, 
  LineChart 
} from '@/components/charts';

export function DiagnosticsDashboard() {
  const [drugCode, setDrugCode] = useState('P182054');
  const [department, setDepartment] = useState<number | undefined>();
  
  const { data, loading, error } = useDiagnostics({
    drug_code: drugCode,
    department,
    use_cache: true,
  });
  
  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorMessage error={error} />;
  if (!data?.success) return <NoDataMessage />;
  
  const diagnostics = data.data;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {/* Data Health Gauge */}
      <GaugeChart
        value={diagnostics.data_health.data_completeness_score * 100}
        label="Data Completeness"
        max={100}
      />
      
      {/* Volatility Gauge */}
      <GaugeChart
        value={diagnostics.time_series_characteristics.volatility * 100}
        label="Volatility"
        max={100}
      />
      
      {/* Seasonality Strength Bars */}
      <BarChart
        data={[
          { name: 'Weekly', value: diagnostics.time_series_characteristics.seasonality_strength.weekly },
          { name: 'Monthly', value: diagnostics.time_series_characteristics.seasonality_strength.monthly },
        ]}
        label="Seasonality Strength"
      />
      
      {/* Classification Badge */}
      <ClassificationBadge
        category={diagnostics.classification.category}
        confidence={diagnostics.classification.confidence}
      />
      
      {/* Risk Assessment */}
      <RiskCard
        reliability={diagnostics.risks.forecast_reliability}
        issues={diagnostics.risks.data_quality_issues}
        recommendations={diagnostics.risks.recommendations}
      />
    </div>
  );
}
```

---

## 🔗 Related Documentation

- [Dashboard API Examples](./DASHBOARD_API_EXAMPLES.md)
- [ML XGBoost API Documentation](../NEXT_STEPS_XGBOOST_API.md)
- [Frontend Integration Guide](../ML_FORECAST_FRONTEND_INTEGRATION.md)

---

## 📞 Support

For issues or questions:
1. Check the response `meta.status_code` for error details
2. Review the `risks.recommendations` for actionable insights
3. Verify drug code format and date parameters

---

## 🤖 Cursor Agent Implementation Prompts

For quick implementation in your frontend project using Cursor AI:

### **Quick Prompt** (Copy-Paste Ready)
See: [`CURSOR_PROMPT_DIAGNOSTICS.md`](./CURSOR_PROMPT_DIAGNOSTICS.md)

### **Detailed Implementation Guide**
See: [`DIAGNOSTICS_FRONTEND_IMPLEMENTATION_PROMPT.md`](./DIAGNOSTICS_FRONTEND_IMPLEMENTATION_PROMPT.md)

Both prompts include:
- Complete file structure
- TypeScript type definitions
- Component requirements
- Error handling patterns
- Styling guidelines

---

**Last Updated**: 2024-12-31
**API Version**: 1.0

