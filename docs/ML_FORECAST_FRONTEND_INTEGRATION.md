# Frontend Integration Guide - Gradient Boosting Forecast

## Overview

The forecast API returns data that's **ready for plotting** with minimal processing. The response includes:
- Historical data (last 90 days)
- Forecast data with confidence intervals
- Chart configuration hints
- Summary statistics

## API Response Structure

```json
{
  "success": true,
  "drug_code": "DRUG001",
  "drug_name": "Paracetamol 500mg",
  "summary": {
    "total_predicted_demand": 1500.0,
    "average_daily_demand": 50.0,
    "peak_demand_day": "2024-01-20",
    "peak_demand_value": 75.5
  },
  "chart_data": {
    "historical": [
      {
        "date": "2023-10-15",
        "demand": 45.0,
        "type": "actual"
      }
      // ... more historical points
    ],
    "forecast": [
      {
        "date": "2024-01-16",
        "demand": 48.5,
        "confidence_lower": 35.2,
        "confidence_upper": 61.8,
        "type": "predicted"
      }
      // ... more forecast points
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
      },
      {
        "name": "Confidence Interval",
        "color": "#f59e0b",
        "type": "area",
        "opacity": 0.2
      }
    ]
  },
  "daily_forecasts": [...],
  "recommendations": [...]
}
```

## Frontend Implementation Examples

### 1. Recharts (React)

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, AreaChart } from 'recharts';

function ForecastChart({ forecastData }) {
  const { chart_data, chart_config } = forecastData;
  
  // Combine historical and forecast data
  const allData = [
    ...chart_data.historical.map(d => ({ ...d, isForecast: false })),
    ...chart_data.forecast.map(d => ({ ...d, isForecast: true }))
  ];

  return (
    <AreaChart width={800} height={400} data={allData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis 
        dataKey="date" 
        tickFormatter={(date) => new Date(date).toLocaleDateString()}
      />
      <YAxis />
      <Tooltip />
      <Legend />
      
      {/* Historical data - solid line */}
      <Area
        type="monotone"
        dataKey="demand"
        stroke="#3b82f6"
        fill="#3b82f6"
        fillOpacity={0.1}
        name="Historical Demand"
        data={chart_data.historical}
      />
      
      {/* Forecast - dashed line */}
      <Line
        type="monotone"
        dataKey="demand"
        stroke="#f59e0b"
        strokeDasharray="5 5"
        name="Predicted Demand"
        data={chart_data.forecast}
      />
      
      {/* Confidence interval - shaded area */}
      <Area
        type="monotone"
        dataKey="confidence_upper"
        stroke="none"
        fill="#f59e0b"
        fillOpacity={0.2}
        name="Confidence Interval"
        data={chart_data.forecast}
      />
      <Area
        type="monotone"
        dataKey="confidence_lower"
        stroke="none"
        fill="#f59e0b"
        fillOpacity={0.2}
        data={chart_data.forecast}
      />
    </AreaChart>
  );
}
```

### 2. Chart.js (React/Vue/Vanilla)

```javascript
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

function createForecastChart(forecastData) {
  const { chart_data, chart_config } = forecastData;
  
  // Prepare datasets
  const historicalData = chart_data.historical.map(d => ({
    x: d.date,
    y: d.demand
  }));
  
  const forecastData = chart_data.forecast.map(d => ({
    x: d.date,
    y: d.demand
  }));
  
  const confidenceUpper = chart_data.forecast.map(d => ({
    x: d.date,
    y: d.confidence_upper
  }));
  
  const confidenceLower = chart_data.forecast.map(d => ({
    x: d.date,
    y: d.confidence_lower
  }));

  const ctx = document.getElementById('forecastChart').getContext('2d');
  
  new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [
        {
          label: 'Historical Demand',
          data: historicalData,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4
        },
        {
          label: 'Predicted Demand',
          data: forecastData,
          borderColor: '#f59e0b',
          borderDash: [5, 5],
          tension: 0.4
        },
        {
          label: 'Confidence Upper',
          data: confidenceUpper,
          borderColor: 'transparent',
          backgroundColor: 'rgba(245, 158, 11, 0.2)',
          fill: '+1',
          tension: 0.4
        },
        {
          label: 'Confidence Lower',
          data: confidenceLower,
          borderColor: 'transparent',
          backgroundColor: 'rgba(245, 158, 11, 0.2)',
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
            parser: 'YYYY-MM-DD',
            tooltipFormat: 'll',
            unit: 'day'
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
```

### 3. Plotly.js (React/Vue/Vanilla)

```javascript
import Plotly from 'plotly.js-dist';

function createForecastPlot(forecastData) {
  const { chart_data, chart_config } = forecastData;
  
  const historical = chart_data.historical;
  const forecast = chart_data.forecast;
  
  const trace1 = {
    x: historical.map(d => d.date),
    y: historical.map(d => d.demand),
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Historical Demand',
    line: { color: '#3b82f6', width: 2 }
  };
  
  const trace2 = {
    x: forecast.map(d => d.date),
    y: forecast.map(d => d.demand),
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Predicted Demand',
    line: { color: '#f59e0b', width: 2, dash: 'dash' }
  };
  
  const trace3 = {
    x: forecast.map(d => d.date),
    y: forecast.map(d => d.confidence_upper),
    type: 'scatter',
    mode: 'lines',
    name: 'Upper Confidence',
    line: { color: 'transparent' },
    showlegend: false
  };
  
  const trace4 = {
    x: forecast.map(d => d.date),
    y: forecast.map(d => d.confidence_lower),
    type: 'scatter',
    mode: 'lines',
    name: 'Confidence Interval',
    fill: 'tonexty',
    fillcolor: 'rgba(245, 158, 11, 0.2)',
    line: { color: 'transparent' }
  };
  
  const layout = {
    title: chart_config.title,
    xaxis: { title: 'Date' },
    yaxis: { title: 'Demand' },
    hovermode: 'x unified'
  };
  
  Plotly.newPlot('forecast-plot', [trace1, trace2, trace3, trace4], layout);
}
```

### 4. Vue.js with Chart.js

```vue
<template>
  <div>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'ForecastChart',
  props: {
    forecastData: {
      type: Object,
      required: true
    }
  },
  mounted() {
    this.createChart();
  },
  methods: {
    createChart() {
      const { chart_data } = this.forecastData;
      
      const ctx = this.$refs.chartCanvas.getContext('2d');
      
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: [
            ...chart_data.historical.map(d => d.date),
            ...chart_data.forecast.map(d => d.date)
          ],
          datasets: [
            {
              label: 'Historical',
              data: chart_data.historical.map(d => d.demand),
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59, 130, 246, 0.1)'
            },
            {
              label: 'Forecast',
              data: [
                ...new Array(chart_data.historical.length).fill(null),
                ...chart_data.forecast.map(d => d.demand)
              ],
              borderColor: '#f59e0b',
              borderDash: [5, 5]
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    }
  }
};
</script>
```

## Key Data Points for Plotting

### Historical Data
- **Format**: Array of `{ date, demand, type: 'actual' }`
- **Use for**: Solid line showing past demand
- **Color**: Blue (#3b82f6)

### Forecast Data
- **Format**: Array of `{ date, demand, confidence_lower, confidence_upper, type: 'predicted' }`
- **Use for**: 
  - Dashed line for predicted demand
  - Shaded area for confidence interval
- **Color**: Orange (#f59e0b)

## Visual Best Practices

1. **Separate Historical from Forecast**
   - Use a vertical divider line at the transition point
   - Different line styles (solid vs dashed)

2. **Confidence Intervals**
   - Show as shaded area (semi-transparent)
   - Helps users understand prediction uncertainty

3. **Tooltips**
   - Show date, demand value, and confidence range
   - Indicate whether it's historical or predicted

4. **Legend**
   - Clearly label "Historical" vs "Predicted"
   - Include confidence interval in legend

## Summary Statistics Display

The `summary` object provides key metrics for cards/panels:

```tsx
<div className="summary-cards">
  <Card title="Total Predicted Demand" value={forecastData.summary.total_predicted_demand} />
  <Card title="Average Daily" value={forecastData.summary.average_daily_demand} />
  <Card title="Peak Demand" value={forecastData.summary.peak_demand_value} />
  <Card title="Peak Date" value={forecastData.summary.peak_demand_day} />
</div>
```

## Recommendations Display

The `recommendations` array can be displayed as actionable cards:

```tsx
{forecastData.recommendations.map(rec => (
  <RecommendationCard
    key={rec.type}
    type={rec.type}
    value={rec.value}
    description={rec.description}
  />
))}
```

## No Changes Needed!

The API response is **already optimized for frontend plotting**. You can:
- ✅ Use `chart_data.historical` and `chart_data.forecast` directly
- ✅ Follow `chart_config` for styling hints
- ✅ Display `summary` for key metrics
- ✅ Show `recommendations` as actionable items

The data structure is chart-library agnostic and works with:
- Recharts
- Chart.js
- Plotly.js
- D3.js
- Nivo
- Any other charting library

