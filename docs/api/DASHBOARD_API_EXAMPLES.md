# Dashboard API - Complete Examples

## Base URL
```
http://localhost:5000/api/dashboard
```

---

## 1. Get Top Drugs

### Endpoint
```
GET /api/dashboard/top-drugs
```

### Description
Get top dispensed drugs by quantity within a date range. Supports filtering by category and department.

### Using cURL
```bash
# Basic request
curl "http://localhost:5000/api/dashboard/top-drugs?start_date=2019-01-01&end_date=2019-12-31&limit=10"

# With category filter
curl "http://localhost:5000/api/dashboard/top-drugs?start_date=2019-01-01&end_date=2019-12-31&limit=20&category_id=5"

# With department filter
curl "http://localhost:5000/api/dashboard/top-drugs?start_date=2019-01-01&end_date=2019-12-31&limit=15&department_id=3"

# With both filters
curl "http://localhost:5000/api/dashboard/top-drugs?start_date=2019-01-01&end_date=2019-12-31&limit=25&category_id=5&department_id=3"
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/dashboard/top-drugs"

params = {
    "start_date": "2019-01-01",
    "end_date": "2019-12-31",
    "limit": 10,              # Optional: default 10, max 100
    "category_id": 5,         # Optional: filter by category
    "department_id": 3        # Optional: filter by department
}

response = requests.get(url, params=params)
print(response.json())
```

### Query Parameters
- **start_date** (required): Start date in YYYY-MM-DD format
- **end_date** (required): End date in YYYY-MM-DD format (must be >= start_date)
- **limit** (optional): Number of results to return (default: 10, max: 100)
- **category_id** (optional): Filter by drug category ID
- **department_id** (optional): Filter by department ID

### Response Example
```json
{
  "success": true,
  "data": {
    "drugs": [
      {
        "drug_code": "DRUG001",
        "drug_name": "Paracetamol 500mg",
        "total_dispensed": 15000,
        "total_value": 45000.50,
        "transaction_count": 1250
      },
      {
        "drug_code": "DRUG002",
        "drug_name": "Ibuprofen 400mg",
        "total_dispensed": 12000,
        "total_value": 36000.25,
        "transaction_count": 980
      }
    ],
    "period": {
      "start_date": "2019-01-01",
      "end_date": "2019-12-31"
    },
    "total_unique_drugs": 150
  }
}
```

### Visualization Recommendations

**Recommended Chart Types:**
1. **Horizontal Bar Chart** (Primary) - Best for ranking and comparing multiple drugs
   - X-axis: `total_dispensed` or `total_value`
   - Y-axis: `drug_name`
   - Color coding by category (if filtered)
   - Tooltip showing all metrics (quantity, value, transactions)

2. **Vertical Bar Chart** - Alternative for better horizontal space usage
   - X-axis: `drug_name` (truncated if long)
   - Y-axis: `total_dispensed` or `total_value`
   - Stacked bars for quantity + value comparison

3. **Data Table with Sorting** - For detailed analysis
   - Sortable columns for all metrics
   - Search/filter functionality
   - Export to CSV/Excel

**Next.js Implementation Libraries:**
- **Recharts**: `<BarChart>` with horizontal layout
- **Chart.js**: Bar chart with `indexAxis: 'y'`
- **Nivo**: `<Bar>` component with horizontal orientation
- **React Table**: For data table implementation

**Example Component Structure:**
```tsx
// Using Recharts
<BarChart layout="vertical" data={drugs}>
  <XAxis type="number" />
  <YAxis dataKey="drug_name" type="category" width={150} />
  <Bar dataKey="total_dispensed" fill="#8884d8" />
  <Tooltip />
</BarChart>
```

---

## 2. Get Drug Demand Trends

### Endpoint
```
GET /api/dashboard/drug-demand
```

### Description
Get drug demand trends over time with configurable granularity (daily, weekly, monthly). Can filter by specific drug code.

### Using cURL
```bash
# Daily granularity (default)
curl "http://localhost:5000/api/dashboard/drug-demand?start_date=2019-01-01&end_date=2019-01-31"

# Weekly granularity
curl "http://localhost:5000/api/dashboard/drug-demand?start_date=2019-01-01&end_date=2019-03-31&granularity=weekly"

# Monthly granularity
curl "http://localhost:5000/api/dashboard/drug-demand?start_date=2019-01-01&end_date=2019-12-31&granularity=monthly"

# For specific drug
curl "http://localhost:5000/api/dashboard/drug-demand?start_date=2019-01-01&end_date=2019-12-31&drug_code=DRUG001&granularity=monthly"
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/dashboard/drug-demand"

params = {
    "start_date": "2019-01-01",
    "end_date": "2019-12-31",
    "granularity": "monthly",  # Optional: 'daily', 'weekly', 'monthly' (default: 'daily')
    "drug_code": "DRUG001"      # Optional: filter by specific drug code
}

response = requests.get(url, params=params)
print(response.json())
```

### Query Parameters
- **start_date** (required): Start date in YYYY-MM-DD format
- **end_date** (required): End date in YYYY-MM-DD format (must be >= start_date)
- **granularity** (optional): Time granularity - `daily`, `weekly`, or `monthly` (default: `daily`)
- **drug_code** (optional): Filter by specific drug code

### Response Example
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "date": "2019-01-01",
        "quantity": 450,
        "value": 1350.50,
        "transaction_count": 38
      },
      {
        "date": "2019-01-02",
        "quantity": 520,
        "value": 1560.75,
        "transaction_count": 42
      }
    ],
    "drug_code": null,
    "granularity": "daily"
  }
}
```

### Visualization Recommendations

**Recommended Chart Types:**
1. **Line Chart** (Primary) - Best for time-series trends
   - X-axis: `date` (formatted based on granularity)
   - Y-axis: `quantity` or `value`
   - Multiple lines for quantity, value, and transaction_count
   - Smooth curves for better trend visualization
   - Interactive tooltip with all metrics

2. **Area Chart** - Shows volume and trends simultaneously
   - Stacked area for multiple metrics
   - Gradient fills for visual appeal
   - Good for showing cumulative patterns

3. **Multi-Axis Chart** - Compare different metrics on separate scales
   - Primary Y-axis: `quantity`
   - Secondary Y-axis: `value` or `transaction_count`
   - Different colors for each metric

4. **Sparkline** - For dashboard widgets showing quick trends
   - Mini line chart in summary cards
   - Shows trend direction at a glance

**Next.js Implementation Libraries:**
- **Recharts**: `<LineChart>` or `<AreaChart>` with responsive design
- **Chart.js**: Line chart with time scale
- **Nivo**: `<Line>` or `<AreaBump>` component
- **Victory**: `<VictoryLine>` for time series

**Example Component Structure:**
```tsx
// Using Recharts
<LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="date" />
  <YAxis />
  <Tooltip />
  <Legend />
  <Line type="monotone" dataKey="quantity" stroke="#8884d8" />
  <Line type="monotone" dataKey="value" stroke="#82ca9d" />
</LineChart>
```

---

## 3. Get Summary Statistics

### Endpoint
```
GET /api/dashboard/summary-stats
```

### Description
Get overall statistics for dashboard cards. Date range is optional - if not provided, returns statistics for all time.

### Using cURL
```bash
# All time statistics
curl "http://localhost:5000/api/dashboard/summary-stats"

# With date range
curl "http://localhost:5000/api/dashboard/summary-stats?start_date=2019-01-01&end_date=2019-12-31"
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/dashboard/summary-stats"

# All time
response = requests.get(url)
print(response.json())

# With date range
params = {
    "start_date": "2019-01-01",  # Optional
    "end_date": "2019-12-31"     # Optional
}
response = requests.get(url, params=params)
print(response.json())
```

### Query Parameters
- **start_date** (optional): Start date in YYYY-MM-DD format
- **end_date** (optional): End date in YYYY-MM-DD format

### Response Example
```json
{
  "success": true,
  "data": {
    "total_dispensed": 500000,
    "total_value": 1500000.75,
    "total_transactions": 25000,
    "unique_drugs": 150,
    "unique_departments": 12,
    "date_range": {
      "start_date": "2019-01-01",
      "end_date": "2019-12-31"
    },
    "avg_daily_dispensed": 1370.0
  }
}
```

### Visualization Recommendations

**Recommended Chart Types:**
1. **KPI Cards/Metric Cards** (Primary) - Dashboard overview cards
   - Large number display with formatted values
   - Icon or small trend indicator (up/down arrow)
   - Optional mini sparkline chart
   - Color-coded by metric type
   - Responsive grid layout (2-4 columns)

2. **Stat Grid Layout** - Grid of metric cards
   - Each card shows: label, value, optional change indicator
   - Hover effects for interactivity
   - Click to drill down to detailed view

3. **Gauge/Progress Indicators** - For percentage-based metrics
   - Circular progress for completion rates
   - Linear progress bars for comparisons

**Next.js Implementation Libraries:**
- **Custom Components**: Simple card components with Tailwind CSS
- **Recharts**: For mini sparklines in cards
- **React Icons**: For metric icons
- **Framer Motion**: For animated number counting

**Example Component Structure:**
```tsx
// Custom KPI Card Component
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  <MetricCard
    title="Total Dispensed"
    value={formatNumber(data.total_dispensed)}
    icon={<PackageIcon />}
    trend={+5.2}
  />
  <MetricCard
    title="Total Value"
    value={formatCurrency(data.total_value)}
    icon={<DollarIcon />}
  />
  {/* More cards... */}
</div>
```

---

## 4. Get Chart Data

### Endpoint
```
GET /api/dashboard/chart-data/<chart_type>
```

### Description
Get pre-formatted chart data for frontend visualization. Supports multiple chart types.

### Chart Types
- `trends`: Time-series trend chart
- `seasonal`: Seasonal patterns heatmap
- `department`: Department performance chart

### Using cURL
```bash
# Trends chart
curl "http://localhost:5000/api/dashboard/chart-data/trends?start_date=2019-01-01&end_date=2019-12-31"

# Seasonal patterns chart
curl "http://localhost:5000/api/dashboard/chart-data/seasonal?start_date=2019-01-01&end_date=2019-12-31"

# Department performance chart
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-12-31"
```

### Using Python requests
```python
import requests

base_url = "http://localhost:5000/api/dashboard/chart-data"

params = {
    "start_date": "2019-01-01",
    "end_date": "2019-12-31"
}

# Trends chart
response = requests.get(f"{base_url}/trends", params=params)
print("Trends:", response.json())

# Seasonal chart
response = requests.get(f"{base_url}/seasonal", params=params)
print("Seasonal:", response.json())

# Department chart
response = requests.get(f"{base_url}/department", params=params)
print("Department:", response.json())
```

### Query Parameters
- **start_date** (required): Start date in YYYY-MM-DD format
- **end_date** (required): End date in YYYY-MM-DD format

### Response Example
```json
{
  "success": true,
  "data": {
    "chart_type": "trends",
    "data": {
      "labels": ["2019-01", "2019-02", "2019-03"],
      "datasets": [
        {
          "label": "Quantity",
          "data": [45000, 52000, 48000]
        }
      ]
    },
    "config": {
      "type": "line",
      "options": {}
    }
  }
}
```

### Visualization Recommendations

**Chart Type: `trends`**
- **Line Chart** or **Area Chart** - Time-series visualization
- Multiple datasets can be displayed as separate lines
- Interactive tooltips and zoom functionality

**Chart Type: `seasonal`**
- **Heatmap** (Primary) - Best for seasonal pattern visualization
  - X-axis: Months (Jan-Dec) or Weeks
  - Y-axis: Years
  - Color intensity: Quantity/Value
  - Shows patterns like peak seasons, monthly trends
- **Calendar Heatmap** - Day-by-day visualization
  - Each day as a cell
  - Color intensity based on value
  - Shows weekly/monthly patterns

**Chart Type: `department`**
- **Horizontal Bar Chart** - Department comparison
- **Treemap** - Size-based department visualization
- **Donut/Pie Chart** - Department distribution (if showing percentages)

**Next.js Implementation Libraries:**
- **Recharts**: `<LineChart>`, `<AreaChart>`, `<BarChart>`
- **Nivo**: `<HeatMap>` for seasonal patterns, `<Treemap>` for departments
- **React-Calendar-Heatmap**: For calendar-style heatmaps
- **Chart.js**: All chart types with good customization

**Example Component Structure:**
```tsx
// Seasonal Heatmap using Nivo
<HeatMap
  data={transformedData}
  keys={['quantity']}
  indexBy="month"
  margin={{ top: 60, right: 90, bottom: 60, left: 90 }}
  colors={{ scheme: 'nivo' }}
/>
```

---

## 5. Get Department Performance

### Endpoint
```
GET /api/dashboard/department-performance
```

### Description
Get department-level performance metrics and comparison.

### Using cURL
```bash
# Default limit (10)
curl "http://localhost:5000/api/dashboard/department-performance?start_date=2019-01-01&end_date=2019-12-31"

# Custom limit
curl "http://localhost:5000/api/dashboard/department-performance?start_date=2019-01-01&end_date=2019-12-31&limit=20"
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/dashboard/department-performance"

params = {
    "start_date": "2019-01-01",
    "end_date": "2019-12-31",
    "limit": 20  # Optional: default 10
}

response = requests.get(url, params=params)
print(response.json())
```

### Query Parameters
- **start_date** (required): Start date in YYYY-MM-DD format
- **end_date** (required): End date in YYYY-MM-DD format
- **limit** (optional): Number of departments to return (default: 10)

### Response Example
```json
{
  "success": true,
  "data": {
    "departments": [
      {
        "department_id": 1,
        "department_name": "Cardiology",
        "total_dispensed": 50000,
        "total_value": 150000.50,
        "transaction_count": 2500
      },
      {
        "department_id": 2,
        "department_name": "Pediatrics",
        "total_dispensed": 45000,
        "total_value": 135000.25,
        "transaction_count": 2200
      }
    ]
  }
}
```

### Visualization Recommendations

**Recommended Chart Types:**
1. **Horizontal Bar Chart** (Primary) - Best for department ranking
   - X-axis: `total_dispensed` or `total_value`
   - Y-axis: `department_name`
   - Color gradient based on performance
   - Tooltip with all metrics

2. **Grouped Bar Chart** - Compare multiple metrics side-by-side
   - Groups: `total_dispensed`, `total_value`, `transaction_count`
   - X-axis: `department_name`
   - Different colors for each metric

3. **Treemap** - Size-based visualization
   - Size: `total_dispensed` or `total_value`
   - Color: Performance indicator
   - Labels: `department_name`
   - Interactive: Click to drill down

4. **Donut/Pie Chart** - Show department distribution
   - Percentage of total
   - Color-coded by department
   - Center label with total

**Next.js Implementation Libraries:**
- **Recharts**: `<BarChart>` with horizontal layout, `<Treemap>`, `<PieChart>`
- **Nivo**: `<Bar>`, `<Treemap>`, `<Pie>` components
- **Chart.js**: Bar chart, pie chart with good animations

**Example Component Structure:**
```tsx
// Using Recharts - Horizontal Bar
<BarChart layout="vertical" data={departments}>
  <XAxis type="number" />
  <YAxis dataKey="department_name" type="category" />
  <Bar dataKey="total_dispensed" fill="#8884d8" />
  <Tooltip />
</BarChart>

// Treemap alternative
<Treemap
  data={departments}
  dataKey="total_dispensed"
  nameKey="department_name"
/>
```

---

## 6. Get Year Comparison

### Endpoint
```
GET /api/dashboard/year-comparison
```

### Description
Get year-over-year comparison metrics. Compare quantity, value, or transaction counts across years.

### Using cURL
```bash
# Quantity comparison (default)
curl "http://localhost:5000/api/dashboard/year-comparison?start_year=2019&end_year=2022"

# Value comparison
curl "http://localhost:5000/api/dashboard/year-comparison?metric_type=value&start_year=2019&end_year=2022"

# Transactions comparison
curl "http://localhost:5000/api/dashboard/year-comparison?metric_type=transactions&start_year=2019&end_year=2022"

# For specific drug
curl "http://localhost:5000/api/dashboard/year-comparison?metric_type=quantity&drug_code=DRUG001&start_year=2019&end_year=2022"
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/dashboard/year-comparison"

params = {
    "metric_type": "quantity",  # Optional: 'quantity', 'value', 'transactions' (default: 'quantity')
    "drug_code": "DRUG001",     # Optional: filter by specific drug
    "start_year": 2019,         # Optional: default 2019
    "end_year": 2022            # Optional: default 2022
}

response = requests.get(url, params=params)
print(response.json())
```

### Query Parameters
- **metric_type** (optional): Type of metric to compare - `quantity`, `value`, or `transactions` (default: `quantity`)
- **drug_code** (optional): Filter by specific drug code
- **start_year** (optional): Starting year (default: 2019, range: 2010-2030)
- **end_year** (optional): Ending year (default: 2022, range: 2010-2030, must be >= start_year)

### Response Example
```json
{
  "success": true,
  "data": {
    "metric_type": "quantity",
    "data": [
      {
        "year": 2019,
        "metric_value": 500000
      },
      {
        "year": 2020,
        "metric_value": 550000
      },
      {
        "year": 2021,
        "metric_value": 600000
      },
      {
        "year": 2022,
        "metric_value": 650000
      }
    ],
    "drug_code": null,
    "years_compared": [2019, 2020, 2021, 2022]
  }
}
```

### Visualization Recommendations

**Recommended Chart Types:**
1. **Grouped Bar Chart** (Primary) - Compare years side-by-side
   - X-axis: `year`
   - Y-axis: `metric_value`
   - Different bars for different metric types (if showing multiple)
   - Color-coded bars
   - Show percentage change annotations

2. **Line Chart with Markers** - Show trend over years
   - X-axis: `year`
   - Y-axis: `metric_value`
   - Markers at each data point
   - Trend line with growth percentage
   - Area fill for visual impact

3. **Column Chart** - Vertical bars for year comparison
   - X-axis: `year`
   - Y-axis: `metric_value`
   - Gradient fills
   - Value labels on top of bars

4. **Combo Chart** - Multiple metrics on same chart
   - Bars for quantity
   - Line for value
   - Secondary Y-axis for different scales

**Next.js Implementation Libraries:**
- **Recharts**: `<BarChart>`, `<LineChart>`, `<ComposedChart>`
- **Chart.js**: Bar chart, line chart with year comparison
- **Nivo**: `<Bar>`, `<Line>` components

**Example Component Structure:**
```tsx
// Using Recharts - Grouped Bar
<BarChart data={data}>
  <XAxis dataKey="year" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="metric_value" fill="#8884d8" />
  <Cell fill="#8884d8" />
</BarChart>

// With trend line
<ComposedChart data={data}>
  <Bar dataKey="metric_value" fill="#8884d8" />
  <Line type="monotone" dataKey="metric_value" stroke="#ff7300" />
</ComposedChart>
```

---

## 7. Get Category Analysis

### Endpoint
```
GET /api/dashboard/category-analysis
```

### Description
Get drug category analysis over time with monthly or quarterly granularity.

### Using cURL
```bash
# Monthly granularity (default)
curl "http://localhost:5000/api/dashboard/category-analysis?start_date=2019-01-01&end_date=2019-12-31"

# Quarterly granularity
curl "http://localhost:5000/api/dashboard/category-analysis?start_date=2019-01-01&end_date=2019-12-31&granularity=quarterly"
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/dashboard/category-analysis"

params = {
    "start_date": "2019-01-01",
    "end_date": "2019-12-31",
    "granularity": "monthly"  # Optional: 'monthly' or 'quarterly' (default: 'monthly')
}

response = requests.get(url, params=params)
print(response.json())
```

### Query Parameters
- **start_date** (required): Start date in YYYY-MM-DD format
- **end_date** (required): End date in YYYY-MM-DD format (must be >= start_date)
- **granularity** (optional): Time granularity - `monthly` or `quarterly` (default: `monthly`)

### Response Example
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "period": "2019-01",
        "category_id": 1,
        "total_quantity": 50000,
        "total_value": 150000.50,
        "transaction_count": 2500,
        "unique_drugs": 25
      },
      {
        "period": "2019-02",
        "category_id": 1,
        "total_quantity": 52000,
        "total_value": 156000.75,
        "transaction_count": 2600,
        "unique_drugs": 25
      }
    ],
    "granularity": "monthly",
    "period": {
      "start_date": "2019-01-01",
      "end_date": "2019-12-31"
    },
    "total_categories": 10
  }
}
```

### Visualization Recommendations

**Recommended Chart Types:**
1. **Stacked Area Chart** (Primary) - Show category trends over time
   - X-axis: `period`
   - Y-axis: `total_quantity` or `total_value`
   - Stacked areas by `category_id`
   - Color-coded categories
   - Shows both individual and total trends

2. **Stacked Bar Chart** - Alternative for clearer category comparison
   - X-axis: `period`
   - Y-axis: `total_quantity` or `total_value`
   - Stacked bars by category
   - Better for discrete time periods

3. **Heatmap** - Time vs Category matrix
   - X-axis: `period` (months/quarters)
   - Y-axis: `category_id` or category name
   - Color intensity: `total_quantity` or `total_value`
   - Shows patterns and outliers

4. **Stream Graph** - Flow visualization
   - Shows category proportions over time
   - Smooth flowing curves
   - Good for showing relative changes

5. **Grouped Bar Chart** - Compare categories side-by-side
   - X-axis: `period`
   - Y-axis: `total_quantity`
   - Groups by category
   - Better for comparing specific categories

**Next.js Implementation Libraries:**
- **Recharts**: `<AreaChart>` with stacked areas, `<BarChart>` stacked
- **Nivo**: `<Stream>`, `<HeatMap>`, `<AreaBump>` components
- **Chart.js**: Stacked area/bar charts
- **D3.js**: For custom stream graphs

**Example Component Structure:**
```tsx
// Using Recharts - Stacked Area
<AreaChart data={transformedData}>
  <XAxis dataKey="period" />
  <YAxis />
  <CartesianGrid strokeDasharray="3 3" />
  <Tooltip />
  <Area type="monotone" dataKey="category_1" stackId="1" stroke="#8884d8" fill="#8884d8" />
  <Area type="monotone" dataKey="category_2" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
  {/* More categories... */}
</AreaChart>

// Heatmap alternative
<HeatMap
  data={heatmapData}
  xKey="period"
  yKey="category_id"
  valueKey="total_quantity"
/>
```

---

## 8. Get Patient Demographics

### Endpoint
```
GET /api/dashboard/patient-demographics
```

### Description
Get patient demographics analysis grouped by age, room, or bed.

### Using cURL
```bash
# Group by age (default)
curl "http://localhost:5000/api/dashboard/patient-demographics?start_date=2019-01-01&end_date=2019-12-31"

# Group by room
curl "http://localhost:5000/api/dashboard/patient-demographics?start_date=2019-01-01&end_date=2019-12-31&group_by=room"

# Group by bed
curl "http://localhost:5000/api/dashboard/patient-demographics?start_date=2019-01-01&end_date=2019-12-31&group_by=bed"
```

### Using Python requests
```python
import requests

url = "http://localhost:5000/api/dashboard/patient-demographics"

params = {
    "start_date": "2019-01-01",
    "end_date": "2019-12-31",
    "group_by": "age"  # Optional: 'age', 'room', or 'bed' (default: 'age')
}

response = requests.get(url, params=params)
print(response.json())
```

### Query Parameters
- **start_date** (required): Start date in YYYY-MM-DD format
- **end_date** (required): End date in YYYY-MM-DD format (must be >= start_date)
- **group_by** (optional): Grouping method - `age`, `room`, or `bed` (default: `age`)

### Response Example
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "group": "0-18",
        "transaction_count": 5000,
        "total_quantity": 100000,
        "total_value": 300000.50,
        "unique_drugs": 50
      },
      {
        "group": "19-35",
        "transaction_count": 8000,
        "total_quantity": 150000,
        "total_value": 450000.75,
        "unique_drugs": 60
      },
      {
        "group": "36-50",
        "transaction_count": 7000,
        "total_quantity": 140000,
        "total_value": 420000.25,
        "unique_drugs": 55
      }
    ],
    "group_by": "age",
    "period": {
      "start_date": "2019-01-01",
      "end_date": "2019-12-31"
    },
    "total_groups": 5
  }
}
```

### Visualization Recommendations

**When `group_by: "age"`:**
1. **Pie Chart** (Primary) - Show age group distribution
   - Segments: Age groups
   - Size: `total_quantity` or `total_value`
   - Color-coded by age range
   - Center label with total
   - Interactive: Click to filter

2. **Donut Chart** - Alternative with center space for summary
   - Same as pie but with center hole
   - Can display total in center

3. **Horizontal Bar Chart** - For detailed comparison
   - X-axis: `total_quantity` or `total_value`
   - Y-axis: Age groups
   - Color gradient by age

**When `group_by: "room"` or `group_by: "bed"`:**
1. **Bar Chart** (Primary) - Compare rooms/beds
   - X-axis: Room/Bed number or identifier
   - Y-axis: `total_quantity` or `transaction_count`
   - Color by performance level

2. **Heatmap** - Room/Bed activity visualization
   - Grid layout showing room/bed positions
   - Color intensity: Activity level
   - Useful for hospital floor layouts

3. **Treemap** - Size-based room/bed visualization
   - Size: `total_quantity`
   - Color: Activity indicator
   - Labels: Room/Bed identifiers

**Next.js Implementation Libraries:**
- **Recharts**: `<PieChart>`, `<DonutChart>`, `<BarChart>`
- **Nivo**: `<Pie>`, `<Bar>`, `<Treemap>` components
- **Chart.js**: Pie, donut, bar charts
- **Custom Components**: For room/bed heatmaps with grid layout

**Example Component Structure:**
```tsx
// Age groups - Pie Chart
<PieChart>
  <Pie
    data={data}
    dataKey="total_quantity"
    nameKey="group"
    cx="50%"
    cy="50%"
    outerRadius={80}
    label
  />
  <Tooltip />
  <Legend />
</PieChart>

// Rooms/Beds - Bar Chart
<BarChart data={data}>
  <XAxis dataKey="group" />
  <YAxis />
  <Bar dataKey="total_quantity" fill="#8884d8" />
  <Tooltip />
</BarChart>
```

---

## Complete Testing Workflow

### Step 1: Get summary statistics
```bash
curl "http://localhost:5000/api/dashboard/summary-stats?start_date=2019-01-01&end_date=2019-12-31"
```

### Step 2: Get top drugs
```bash
curl "http://localhost:5000/api/dashboard/top-drugs?start_date=2019-01-01&end_date=2019-12-31&limit=10"
```

### Step 3: Get drug demand trends
```bash
curl "http://localhost:5000/api/dashboard/drug-demand?start_date=2019-01-01&end_date=2019-12-31&granularity=monthly"
```

### Step 4: Get department performance
```bash
curl "http://localhost:5000/api/dashboard/department-performance?start_date=2019-01-01&end_date=2019-12-31"
```

### Step 5: Get year comparison
```bash
curl "http://localhost:5000/api/dashboard/year-comparison?start_year=2019&end_year=2022&metric_type=quantity"
```

---

## Python Complete Example Script

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api/dashboard"

def get_summary_stats(start_date=None, end_date=None):
    """Get summary statistics."""
    url = f"{BASE_URL}/summary-stats"
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['data']

def get_top_drugs(start_date, end_date, limit=10, category_id=None, department_id=None):
    """Get top dispensed drugs."""
    url = f"{BASE_URL}/top-drugs"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }
    if category_id:
        params["category_id"] = category_id
    if department_id:
        params["department_id"] = department_id
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['data']

def get_drug_demand(start_date, end_date, granularity="daily", drug_code=None):
    """Get drug demand trends."""
    url = f"{BASE_URL}/drug-demand"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity
    }
    if drug_code:
        params["drug_code"] = drug_code
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['data']

def get_chart_data(chart_type, start_date, end_date):
    """Get chart data."""
    url = f"{BASE_URL}/chart-data/{chart_type}"
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['data']

def get_department_performance(start_date, end_date, limit=10):
    """Get department performance."""
    url = f"{BASE_URL}/department-performance"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['data']

def get_year_comparison(metric_type="quantity", drug_code=None, start_year=2019, end_year=2022):
    """Get year-over-year comparison."""
    url = f"{BASE_URL}/year-comparison"
    params = {
        "metric_type": metric_type,
        "start_year": start_year,
        "end_year": end_year
    }
    if drug_code:
        params["drug_code"] = drug_code
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['data']

def get_category_analysis(start_date, end_date, granularity="monthly"):
    """Get category analysis."""
    url = f"{BASE_URL}/category-analysis"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['data']

def get_patient_demographics(start_date, end_date, group_by="age"):
    """Get patient demographics."""
    url = f"{BASE_URL}/patient-demographics"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "group_by": group_by
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()['data']

# Example usage
if __name__ == "__main__":
    start_date = "2019-01-01"
    end_date = "2019-12-31"
    
    print("=== Summary Statistics ===")
    stats = get_summary_stats(start_date, end_date)
    print(f"Total Dispensed: {stats['total_dispensed']}")
    print(f"Total Value: {stats['total_value']}")
    print(f"Total Transactions: {stats['total_transactions']}")
    
    print("\n=== Top 10 Drugs ===")
    top_drugs = get_top_drugs(start_date, end_date, limit=10)
    for drug in top_drugs['drugs'][:5]:
        print(f"{drug['drug_name']}: {drug['total_dispensed']} units")
    
    print("\n=== Drug Demand (Monthly) ===")
    demand = get_drug_demand(start_date, end_date, granularity="monthly")
    print(f"Data points: {len(demand['data'])}")
    
    print("\n=== Department Performance ===")
    dept_perf = get_department_performance(start_date, end_date)
    for dept in dept_perf['departments'][:3]:
        print(f"{dept.get('department_name', 'Unknown')}: {dept['total_dispensed']} units")
    
    print("\n=== Year Comparison ===")
    year_comp = get_year_comparison(metric_type="quantity", start_year=2019, end_year=2022)
    for point in year_comp['data']:
        print(f"{point['year']}: {point['metric_value']}")
```

---

## Visualization Quick Reference

### Recommended Next.js Chart Libraries

1. **Recharts** (Recommended)
   - ✅ React-friendly, declarative API
   - ✅ Good TypeScript support
   - ✅ Responsive by default
   - ✅ Active community
   - 📦 Install: `npm install recharts`

2. **Nivo**
   - ✅ Beautiful, customizable charts
   - ✅ Server-side rendering support
   - ✅ Many chart types (heatmaps, treemaps, etc.)
   - 📦 Install: `npm install @nivo/core @nivo/bar @nivo/line @nivo/pie`

3. **Chart.js with react-chartjs-2**
   - ✅ Mature library
   - ✅ Extensive customization
   - ✅ Good performance
   - 📦 Install: `npm install chart.js react-chartjs-2`

4. **Victory**
   - ✅ Flexible and powerful
   - ✅ Good animations
   - ✅ Multiple chart types
   - 📦 Install: `npm install victory`

### Endpoint to Visualization Mapping

| Endpoint | Primary Visualization | Alternative Options |
|----------|----------------------|-------------------|
| `/top-drugs` | Horizontal Bar Chart | Vertical Bar, Data Table |
| `/drug-demand` | Line Chart | Area Chart, Multi-Axis Chart |
| `/summary-stats` | KPI Cards | Stat Grid, Gauge Charts |
| `/chart-data/trends` | Line Chart | Area Chart |
| `/chart-data/seasonal` | Heatmap | Calendar Heatmap |
| `/chart-data/department` | Horizontal Bar | Treemap, Donut Chart |
| `/department-performance` | Horizontal Bar Chart | Treemap, Grouped Bar |
| `/year-comparison` | Grouped Bar Chart | Line Chart, Column Chart |
| `/category-analysis` | Stacked Area Chart | Stacked Bar, Heatmap, Stream Graph |
| `/patient-demographics` (age) | Pie/Donut Chart | Horizontal Bar |
| `/patient-demographics` (room/bed) | Bar Chart | Heatmap, Treemap |

### Common Visualization Patterns

**Time Series Data:**
- Use **Line Charts** or **Area Charts**
- X-axis: Time (date, month, year)
- Y-axis: Metric value
- Multiple lines for comparing different metrics

**Ranking/Comparison:**
- Use **Horizontal Bar Charts** for ranking
- Use **Vertical Bar Charts** for comparison
- Sort by value for better readability

**Distribution:**
- Use **Pie/Donut Charts** for categorical distribution
- Use **Treemap** for hierarchical data
- Use **Stacked Charts** for multi-category over time

**Patterns/Correlations:**
- Use **Heatmaps** for time vs category patterns
- Use **Scatter Plots** for correlation analysis
- Use **Calendar Heatmaps** for daily patterns

**Performance Metrics:**
- Use **KPI Cards** for summary statistics
- Use **Gauge Charts** for progress indicators
- Use **Sparklines** for trend indicators

### Best Practices

1. **Responsive Design**: Always make charts responsive using container queries or viewport-based sizing
2. **Accessibility**: Include proper ARIA labels, keyboard navigation, and color-blind friendly palettes
3. **Loading States**: Show skeleton loaders or spinners while data is fetching
4. **Error Handling**: Display user-friendly error messages if API calls fail
5. **Tooltips**: Always include interactive tooltips with detailed information
6. **Legends**: Include legends for multi-series charts
7. **Color Schemes**: Use consistent color schemes across all visualizations
8. **Data Formatting**: Format large numbers (K, M, B) and currency values appropriately
9. **Interactivity**: Add filtering, zooming, and drill-down capabilities where appropriate
10. **Performance**: Use memoization and virtualization for large datasets

### Example Next.js Component Structure

```tsx
'use client';

import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TopDrugsData {
  drugs: Array<{
    drug_code: string;
    drug_name: string;
    total_dispensed: number;
    total_value: number;
    transaction_count: number;
  }>;
}

export default function TopDrugsChart({ startDate, endDate }: { startDate: string; endDate: string }) {
  const [data, setData] = useState<TopDrugsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:5000/api/dashboard/top-drugs?start_date=${startDate}&end_date=${endDate}&limit=10`
        );
        if (!response.ok) throw new Error('Failed to fetch data');
        const result = await response.json();
        setData(result.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [startDate, endDate]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return null;

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart layout="vertical" data={data.drugs}>
        <XAxis type="number" />
        <YAxis dataKey="drug_name" type="category" width={150} />
        <Tooltip />
        <Legend />
        <Bar dataKey="total_dispensed" fill="#8884d8" name="Total Dispensed" />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

---

## Error Responses

### Validation Error
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "start_date is required"
  }
}
```

### Invalid Date Range
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "end_date must be after or equal to start_date"
  }
}
```

### No Data Found
```json
{
  "error": {
    "code": "NO_DATA_FOUND",
    "message": "No department data found"
  }
}
```

### Invalid Parameter Value
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid granularity. Must be one of: daily, weekly, monthly"
  }
}
```

---

## Notes

1. **Date Format**: All dates must be in `YYYY-MM-DD` format
2. **Date Range Validation**: `end_date` must be greater than or equal to `start_date`
3. **Optional Parameters**: Parameters marked as optional can be omitted
4. **Default Values**: Most endpoints have sensible defaults for optional parameters
5. **Response Format**: All successful responses follow the format:
   ```json
   {
     "success": true,
     "data": { ... }
   }
   ```
6. **Error Format**: All error responses follow the format:
   ```json
   {
     "error": {
       "code": "ERROR_CODE",
       "message": "Error description"
     }
   }
   ```
7. **Chart Types**: Valid chart types for `/chart-data/<chart_type>` are: `trends`, `seasonal`, `department`
8. **Granularity Options**: 
   - Drug Demand: `daily`, `weekly`, `monthly`
   - Category Analysis: `monthly`, `quarterly`
9. **Group By Options**: Patient Demographics supports: `age`, `room`, `bed`
10. **Metric Types**: Year Comparison supports: `quantity`, `value`, `transactions`

