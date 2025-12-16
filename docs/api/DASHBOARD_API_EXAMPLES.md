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

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Top Drugs"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/dashboard/top-drugs`

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `start_date` | `2019-01-01` | Required: Start date |
   | `end_date` | `2019-12-31` | Required: End date |
   | `limit` | `10` | Optional: Number of results (default: 10) |
   | `category_id` | `5` | Optional: Filter by category |
   | `department_id` | `3` | Optional: Filter by department |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request:**
```
GET http://localhost:5000/api/dashboard/top-drugs?start_date=2019-01-01&end_date=2019-12-31&limit=10&category_id=5&department_id=3
```

**Expected Response Status:** `200 OK`

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

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Drug Demand"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/dashboard/drug-demand`

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `start_date` | `2019-01-01` | Required: Start date |
   | `end_date` | `2019-12-31` | Required: End date |
   | `granularity` | `monthly` | Optional: 'daily', 'weekly', 'monthly' (default: 'daily') |
   | `drug_code` | `DRUG001` | Optional: Filter by specific drug code |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request:**
```
GET http://localhost:5000/api/dashboard/drug-demand?start_date=2019-01-01&end_date=2019-12-31&granularity=monthly&drug_code=DRUG001
```

**Expected Response Status:** `200 OK`

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

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Summary Statistics"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/dashboard/summary-stats`

3. **Add query parameters (optional)**
   - Go to the "Params" tab
   - Add the following parameters (both are optional):

   | Key | Value | Description |
   |-----|-------|-------------|
   | `start_date` | `2019-01-01` | Optional: Start date |
   | `end_date` | `2019-12-31` | Optional: End date |

   **Note:** If no parameters are provided, returns statistics for all time.

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request (with date range):**
```
GET http://localhost:5000/api/dashboard/summary-stats?start_date=2019-01-01&end_date=2019-12-31
```

**Example Postman Request (all time):**
```
GET http://localhost:5000/api/dashboard/summary-stats
```

**Expected Response Status:** `200 OK`

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

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Chart Data - Trends" (or "Seasonal" or "Department")

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/dashboard/chart-data/trends`
     - Replace `trends` with `seasonal` or `department` for other chart types

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `start_date` | `2019-01-01` | Required: Start date |
   | `end_date` | `2019-12-31` | Required: End date |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Requests:**

**Trends Chart:**
```
GET http://localhost:5000/api/dashboard/chart-data/trends?start_date=2019-01-01&end_date=2019-12-31
```

**Seasonal Chart:**
```
GET http://localhost:5000/api/dashboard/chart-data/seasonal?start_date=2019-01-01&end_date=2019-12-31
```

**Department Chart:**
```
GET http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-12-31
```

**Expected Response Status:** `200 OK`

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

## 4.1. Department Chart Data - Detailed Examples

### Endpoint
```
GET /api/dashboard/chart-data/department
```

### Description
Get department performance chart data for visualization. Returns department-level metrics including total dispensed quantities and values within the specified date range.

### Query Parameters
- **start_date** (required): Start date in YYYY-MM-DD format
- **end_date** (required): End date in YYYY-MM-DD format (must be >= start_date)

### Example Requests with Different Query Parameters

#### 1. Single Month Analysis
Get department performance for a specific month:

**cURL:**
```bash
# January 2019
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-01-31"

# February 2019
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-02-01&end_date=2019-02-28"

# March 2019 (31 days)
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-03-01&end_date=2019-03-31"
```

**Python:**
```python
import requests

# Single month
params = {
    "start_date": "2019-01-01",
    "end_date": "2019-01-31"
}
response = requests.get("http://localhost:5000/api/dashboard/chart-data/department", params=params)
print(response.json())
```

#### 2. Quarter Analysis
Get department performance for a quarter:

**cURL:**
```bash
# Q1 2019 (January - March)
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-03-31"

# Q2 2019 (April - June)
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-04-01&end_date=2019-06-30"

# Q3 2019 (July - September)
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-07-01&end_date=2019-09-30"

# Q4 2019 (October - December)
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-10-01&end_date=2019-12-31"
```

**Python:**
```python
import requests

# Q1 2019
params = {
    "start_date": "2019-01-01",
    "end_date": "2019-03-31"
}
response = requests.get("http://localhost:5000/api/dashboard/chart-data/department", params=params)
print(response.json())
```

#### 3. Full Year Analysis
Get department performance for an entire year:

**cURL:**
```bash
# Full year 2019
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-12-31"

# Full year 2020
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2020-01-01&end_date=2020-12-31"

# Full year 2021
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2021-01-01&end_date=2021-12-31"
```

**Python:**
```python
import requests

# Full year 2019
params = {
    "start_date": "2019-01-01",
    "end_date": "2019-12-31"
}
response = requests.get("http://localhost:5000/api/dashboard/chart-data/department", params=params)
print(response.json())
```

#### 4. Custom Date Range
Get department performance for a custom date range:

**cURL:**
```bash
# First half of 2019
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-06-30"

# Last 6 months of 2019
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-07-01&end_date=2019-12-31"

# Specific 2-month period
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-05-01&end_date=2019-06-30"

# Week range
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-01-07"

# 90-day period
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-03-31"
```

**Python:**
```python
import requests
from datetime import datetime, timedelta

# Custom date range
params = {
    "start_date": "2019-05-01",
    "end_date": "2019-06-30"
}
response = requests.get("http://localhost:5000/api/dashboard/chart-data/department", params=params)
print(response.json())
```

#### 5. Multi-Year Comparison
Get department performance across multiple years:

**cURL:**
```bash
# 2019-2020
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2020-12-31"

# 2019-2021 (3 years)
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2021-12-31"

# 2020-2022
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2020-01-01&end_date=2022-12-31"
```

**Python:**
```python
import requests

# Multi-year
params = {
    "start_date": "2019-01-01",
    "end_date": "2021-12-31"
}
response = requests.get("http://localhost:5000/api/dashboard/chart-data/department", params=params)
print(response.json())
```

#### 6. Recent Periods
Get department performance for recent time periods:

**cURL:**
```bash
# Last 30 days (relative to current date - adjust dates as needed)
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2022-11-01&end_date=2022-11-30"

# Last 7 days
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2022-11-24&end_date=2022-11-30"

# Current month (example for November 2022)
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2022-11-01&end_date=2022-11-30"

# Year-to-date (example for 2022)
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2022-01-01&end_date=2022-11-30"
```

**Python:**
```python
import requests
from datetime import datetime, timedelta

# Last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

params = {
    "start_date": start_date.strftime("%Y-%m-%d"),
    "end_date": end_date.strftime("%Y-%m-%d")
}
response = requests.get("http://localhost:5000/api/dashboard/chart-data/department", params=params)
print(response.json())
```

#### 7. Specific Date Comparisons
Compare same periods across different years:

**cURL:**
```bash
# January 2019 vs January 2020
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-01-31"
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2020-01-01&end_date=2020-01-31"

# Q1 2019 vs Q1 2020
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-03-31"
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2020-01-01&end_date=2020-03-31"

# Summer months (June-August) comparison
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-06-01&end_date=2019-08-31"
curl "http://localhost:5000/api/dashboard/chart-data/department?start_date=2020-06-01&end_date=2020-08-31"
```

**Python:**
```python
import requests

# Compare same period across years
periods = [
    {"start_date": "2019-01-01", "end_date": "2019-01-31"},
    {"start_date": "2020-01-01", "end_date": "2020-01-31"},
    {"start_date": "2021-01-01", "end_date": "2021-01-31"}
]

for period in periods:
    response = requests.get(
        "http://localhost:5000/api/dashboard/chart-data/department",
        params=period
    )
    print(f"Period {period['start_date']} to {period['end_date']}:")
    print(response.json())
    print("\n")
```

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Department Chart Data"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/dashboard/chart-data/department`

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description | Example Use Cases |
   |-----|-------|-------------|-------------------|
   | `start_date` | `2019-01-01` | Required: Start date (YYYY-MM-DD) | Single month, quarter start, year start |
   | `end_date` | `2019-01-31` | Required: End date (YYYY-MM-DD) | Month end, quarter end, year end |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Requests:**

**Single Month:**
```
GET http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-01-31
```

**Quarter:**
```
GET http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-03-31
```

**Full Year:**
```
GET http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-01-01&end_date=2019-12-31
```

**Custom Range:**
```
GET http://localhost:5000/api/dashboard/chart-data/department?start_date=2019-05-01&end_date=2019-06-30
```

**Expected Response Status:** `200 OK`

### Response Example

**Success Response:**
```json
{
  "success": true,
  "data": {
    "chart_type": "department",
    "data": {
      "departments": [
        {
          "department_id": 1,
          "department_name": "Cardiology",
          "total_dispensed": 12500,
          "total_value": 45000.50
        },
        {
          "department_id": 2,
          "department_name": "Pediatrics",
          "total_dispensed": 9800,
          "total_value": 32000.25
        },
        {
          "department_id": 3,
          "department_name": "Emergency",
          "total_dispensed": 15200,
          "total_value": 58000.75
        }
      ]
    },
    "config": {
      "type": "bar",
      "x_axis": "department_id",
      "y_axis": "total_dispensed"
    }
  }
}
```

**Error Response (Missing Parameters):**
```json
{
  "success": false,
  "error": {
    "message": "start_date is required",
    "code": "VALIDATION_ERROR"
  }
}
```

**Error Response (Invalid Date Range):**
```json
{
  "success": false,
  "error": {
    "message": "end_date must be after or equal to start_date",
    "code": "VALIDATION_ERROR"
  }
}
```

**Error Response (No Data Found):**
```json
{
  "success": false,
  "error": {
    "message": "No department data found",
    "code": "NO_DATA_FOUND"
  }
}
```

### Response Fields

- **chart_type**: Always `"department"` for this endpoint
- **data.departments**: Array of department objects containing:
  - **department_id**: Unique identifier for the department
  - **department_name**: Name of the department
  - **total_dispensed**: Total quantity of drugs dispensed by the department
  - **total_value**: Total monetary value of drugs dispensed
- **config**: Chart configuration object:
  - **type**: Chart type recommendation (`"bar"`)
  - **x_axis**: Recommended x-axis field (`"department_id"`)
  - **y_axis**: Recommended y-axis field (`"total_dispensed"`)

### Visualization Recommendations

**Recommended Chart Types:**
- **Horizontal Bar Chart** (Primary) - Best for comparing department performance
  - X-axis: Total dispensed or total value
  - Y-axis: Department names
  - Easy to read and compare values
- **Vertical Bar Chart** - Alternative layout
  - X-axis: Department names
  - Y-axis: Total dispensed or total value
- **Treemap** - Size-based visualization
  - Each department as a rectangle
  - Size represents total dispensed or value
  - Color intensity can show additional metrics
- **Donut/Pie Chart** - Distribution visualization
  - Shows percentage distribution across departments
  - Useful for understanding department share

**Next.js Implementation Example:**
```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function DepartmentChart({ data }) {
  const chartData = data.data.departments.map(dept => ({
    name: dept.department_name,
    dispensed: dept.total_dispensed,
    value: dept.total_value
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={chartData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="name" type="category" width={150} />
        <Tooltip />
        <Legend />
        <Bar dataKey="dispensed" fill="#8884d8" name="Total Dispensed" />
        <Bar dataKey="value" fill="#82ca9d" name="Total Value" />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

### Common Use Cases

1. **Monthly Department Performance Review**
   - Use single month date ranges
   - Compare departments within the same month
   - Identify top-performing departments

2. **Quarterly Business Reviews**
   - Use quarter date ranges (3-month periods)
   - Track department trends over quarters
   - Compare QoQ performance

3. **Annual Reports**
   - Use full year date ranges
   - Generate comprehensive department analytics
   - Year-over-year comparisons

4. **Custom Analysis**
   - Use flexible date ranges for specific analysis needs
   - Compare different time periods
   - Identify seasonal patterns

### Best Practices

1. **Date Range Selection**
   - Use appropriate date ranges for your analysis needs
   - Avoid very large date ranges (>3 years) unless necessary
   - Consider data volume and performance

2. **Error Handling**
   - Always check for `success: false` in responses
   - Handle `NO_DATA_FOUND` errors gracefully
   - Validate date formats before sending requests

3. **Caching**
   - Consider caching responses for frequently accessed date ranges
   - Implement cache invalidation for real-time data needs

4. **Visualization**
   - Sort departments by value for better readability
   - Use consistent color schemes across charts
   - Include tooltips with detailed information

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

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Department Performance"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/dashboard/department-performance`

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `start_date` | `2019-01-01` | Required: Start date |
   | `end_date` | `2019-12-31` | Required: End date |
   | `limit` | `20` | Optional: Number of departments (default: 10) |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request:**
```
GET http://localhost:5000/api/dashboard/department-performance?start_date=2019-01-01&end_date=2019-12-31&limit=20
```

**Expected Response Status:** `200 OK`

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

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Year Comparison"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/dashboard/year-comparison`

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `metric_type` | `quantity` | Optional: 'quantity', 'value', 'transactions' (default: 'quantity') |
   | `drug_code` | `DRUG001` | Optional: Filter by specific drug code |
   | `start_year` | `2019` | Optional: Starting year (default: 2019) |
   | `end_year` | `2022` | Optional: Ending year (default: 2022) |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request:**
```
GET http://localhost:5000/api/dashboard/year-comparison?metric_type=quantity&drug_code=DRUG001&start_year=2019&end_year=2022
```

**Expected Response Status:** `200 OK`

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

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Category Analysis"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/dashboard/category-analysis`

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `start_date` | `2019-01-01` | Required: Start date |
   | `end_date` | `2019-12-31` | Required: End date |
   | `granularity` | `monthly` | Optional: 'monthly' or 'quarterly' (default: 'monthly') |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request:**
```
GET http://localhost:5000/api/dashboard/category-analysis?start_date=2019-01-01&end_date=2019-12-31&granularity=monthly
```

**Expected Response Status:** `200 OK`

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

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Patient Demographics"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/dashboard/patient-demographics`

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `start_date` | `2019-01-01` | Required: Start date |
   | `end_date` | `2019-12-31` | Required: End date |
   | `group_by` | `age` | Optional: 'age', 'room', or 'bed' (default: 'age') |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request (group by age):**
```
GET http://localhost:5000/api/dashboard/patient-demographics?start_date=2019-01-01&end_date=2019-12-31&group_by=age
```

**Example Postman Request (group by room):**
```
GET http://localhost:5000/api/dashboard/patient-demographics?start_date=2019-01-01&end_date=2019-12-31&group_by=room
```

**Example Postman Request (group by bed):**
```
GET http://localhost:5000/api/dashboard/patient-demographics?start_date=2019-01-01&end_date=2019-12-31&group_by=bed
```

**Expected Response Status:** `200 OK`

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

---

## Postman Quick Reference

### Setting Up Postman Collection

**Recommended Setup:**

1. **Create a new Collection**
   - Click "New" → "Collection"
   - Name it: "PharmaAnalytics Dashboard API"
   - Add description: "Dashboard analytics endpoints for PharmaAnalytics"

2. **Set Collection Variables**
   - Go to Collection → Variables tab
   - Add the following variables:

   | Variable | Initial Value | Current Value |
   |----------|---------------|---------------|
   | `base_url` | `http://localhost:5000/api/dashboard` | `http://localhost:5000/api/dashboard` |
   | `start_date` | `2019-01-01` | `2019-01-01` |
   | `end_date` | `2019-12-31` | `2019-12-31` |

3. **Use Variables in Requests**
   - In request URLs, use: `{{base_url}}/top-drugs`
   - In query parameters, use: `{{start_date}}` and `{{end_date}}`

### All Endpoints Summary

| Endpoint | Method | Required Params | Optional Params |
|----------|--------|----------------|-----------------|
| `/top-drugs` | GET | `start_date`, `end_date` | `limit`, `category_id`, `department_id` |
| `/drug-demand` | GET | `start_date`, `end_date` | `granularity`, `drug_code` |
| `/summary-stats` | GET | None | `start_date`, `end_date` |
| `/chart-data/{chart_type}` | GET | `start_date`, `end_date` | None |
| `/department-performance` | GET | `start_date`, `end_date` | `limit` |
| `/year-comparison` | GET | None | `metric_type`, `drug_code`, `start_year`, `end_year` |
| `/category-analysis` | GET | `start_date`, `end_date` | `granularity` |
| `/patient-demographics` | GET | `start_date`, `end_date` | `group_by` |

### Common Postman Workflows

**1. Testing All Endpoints Sequentially:**

Create a Postman Collection Runner:
- Create a collection with all 8 endpoints
- Use Collection Runner to execute all requests
- View results in the Runner summary

**2. Testing with Different Date Ranges:**

Use Environment Variables:
- Create environments: "2019", "2020", "2021", "2022"
- Set `start_date` and `end_date` per environment
- Switch environments to test different time periods

**3. Testing Error Cases:**

Create test requests for:
- Missing required parameters
- Invalid date formats
- Invalid date ranges (end_date < start_date)
- Invalid parameter values (e.g., invalid granularity)

**Example Error Test Request:**
```
GET {{base_url}}/top-drugs
# Missing start_date and end_date - should return 400 Bad Request
```

### Postman Pre-request Scripts (Optional)

Add this script to your collection to automatically set date ranges:

```javascript
// Set default date range if not provided
if (!pm.environment.get("start_date")) {
    pm.environment.set("start_date", "2019-01-01");
}
if (!pm.environment.get("end_date")) {
    pm.environment.set("end_date", "2019-12-31");
}
```

### Postman Tests (Optional)

Add this test script to validate responses:

```javascript
// Test that response is successful
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Test that response has data
pm.test("Response has data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('data');
});

// Test response time
pm.test("Response time is less than 2000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});
```

### Importing Postman Collection

If you have a Postman Collection JSON file:

1. Open Postman
2. Click "Import" button (top left)
3. Select "File" tab
4. Choose your collection JSON file
5. Click "Import"

**Collection Structure Example:**
```json
{
  "info": {
    "name": "PharmaAnalytics Dashboard API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Top Drugs",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/top-drugs?start_date={{start_date}}&end_date={{end_date}}&limit=10",
          "host": ["{{base_url}}"],
          "path": ["top-drugs"],
          "query": [
            {"key": "start_date", "value": "{{start_date}}"},
            {"key": "end_date", "value": "{{end_date}}"},
            {"key": "limit", "value": "10"}
          ]
        }
      }
    }
  ]
}
```

---

## Cost Analysis Dashboard

### Endpoint
```
GET /api/viz/cost-analysis
```

### Description
Get comprehensive cost analysis data for visualization. Returns data for multiple chart types including sunburst, horizontal bar, line, and bubble charts. Supports advanced filtering by date range, departments, price range, and drug categories.

### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `start_date` | string (YYYY-MM-DD) | Yes | Start date for analysis | `2019-01-01` |
| `end_date` | string (YYYY-MM-DD) | Yes | End date for analysis | `2019-12-31` |
| `departments` | int[] | No | Filter by department IDs (comma-separated or multiple params) | `1,2,3` or `departments[]=1&departments[]=2` |
| `price_min` | float | No | Minimum unit price filter | `10.0` |
| `price_max` | float | No | Maximum unit price filter | `1000.0` |
| `drug_categories` | int[] | No | Filter by drug category IDs (comma-separated or multiple params) | `5,6,7` or `drug_categories[]=5&drug_categories[]=6` |

### Using cURL

#### Basic Request
```bash
curl "http://localhost:5000/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31"
```

#### With Department Filter
```bash
# Single department
curl "http://localhost:5000/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&departments=1"

# Multiple departments (comma-separated)
curl "http://localhost:5000/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&departments=1,2,3"
```

#### With Price Range Filter
```bash
# Minimum price only
curl "http://localhost:5000/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&price_min=10.0"

# Price range
curl "http://localhost:5000/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&price_min=10.0&price_max=1000.0"
```

#### With Drug Category Filter
```bash
# Single category
curl "http://localhost:5000/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&drug_categories=5"

# Multiple categories (comma-separated)
curl "http://localhost:5000/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&drug_categories=5,6,7"
```

#### Combined Filters
```bash
curl "http://localhost:5000/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&departments=1,2,3&price_min=10.0&price_max=1000.0&drug_categories=5,6"
```

### Using Python requests

```python
import requests

base_url = "http://localhost:5000/api/viz/cost-analysis"

# Basic request
params = {
    "start_date": "2019-01-01",
    "end_date": "2019-12-31"
}
response = requests.get(base_url, params=params)
print(response.json())

# With all filters
params = {
    "start_date": "2019-01-01",
    "end_date": "2019-12-31",
    "departments": "1,2,3",  # Comma-separated string
    "price_min": 10.0,
    "price_max": 1000.0,
    "drug_categories": "5,6,7"  # Comma-separated string
}
response = requests.get(base_url, params=params)
data = response.json()

# Access different chart data
sunburst_data = data['data']['sunburst']['data']
top_drivers = data['data']['top_cost_drivers']['data']
daily_trends = data['data']['cost_trends']['daily']['data']
monthly_trends = data['data']['cost_trends']['monthly']['data']
bubble_data = data['data']['bubble_chart']['data']
```

### Using Postman

**Step-by-step instructions:**

1. **Create a new request**
   - Click "New" → "HTTP Request"
   - Name it: "Get Cost Analysis"

2. **Set the HTTP method and URL**
   - Method: `GET`
   - URL: `http://localhost:5000/api/viz/cost-analysis`

3. **Add query parameters**
   - Go to the "Params" tab
   - Add the following parameters:

   | Key | Value | Description |
   |-----|-------|-------------|
   | `start_date` | `2019-01-01` | Required: Start date |
   | `end_date` | `2019-12-31` | Required: End date |
   | `departments` | `1,2,3` | Optional: Comma-separated department IDs |
   | `price_min` | `10.0` | Optional: Minimum unit price |
   | `price_max` | `1000.0` | Optional: Maximum unit price |
   | `drug_categories` | `5,6,7` | Optional: Comma-separated category IDs |

4. **Send the request**
   - Click "Send"
   - View the response in the "Body" tab

**Example Postman Request:**
```
GET http://localhost:5000/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&departments=1,2,3&price_min=10.0&price_max=1000.0&drug_categories=5,6
```

**Expected Response Status:** `200 OK`

### Response Structure

The response contains data for four different chart types:

```json
{
  "success": true,
  "data": {
    "sunburst": {
      "data": [...],
      "config": {
        "type": "sunburst",
        "description": "Hierarchical cost breakdown: Department → Category → Drug"
      }
    },
    "top_cost_drivers": {
      "data": [...],
      "config": {
        "type": "horizontal_bar",
        "description": "Top 20 drugs by total cost",
        "x_axis": "total_cost",
        "y_axis": "drug_name"
      }
    },
    "cost_trends": {
      "daily": {
        "data": [...],
        "config": {
          "type": "line",
          "description": "Daily cost trends",
          "x_axis": "date",
          "y_axis": "total_cost"
        }
      },
      "monthly": {
        "data": [...],
        "config": {
          "type": "line",
          "description": "Monthly cost trends",
          "x_axis": "date",
          "y_axis": "total_cost"
        }
      }
    },
    "bubble_chart": {
      "data": [...],
      "config": {
        "type": "bubble",
        "description": "Unit Price vs Quantity vs Frequency",
        "x_axis": "unit_price",
        "y_axis": "quantity",
        "size": "frequency"
      }
    },
    "filters_applied": {
      "start_date": "2019-01-01",
      "end_date": "2019-12-31",
      "departments": [1, 2, 3],
      "price_min": 10.0,
      "price_max": 1000.0,
      "drug_categories": [5, 6]
    }
  }
}
```

### Response Examples

#### 1. Sunburst Chart Data

**Structure:** Hierarchical data for sunburst visualization (Department → Category → Drug)

```json
{
  "sunburst": {
    "data": [
      {
        "id": "dept_1",
        "name": "Department 1",
        "value": 125000.50,
        "children": [
          {
            "id": "dept_1_cat_5",
            "name": "Category 5",
            "value": 75000.25,
            "children": [
              {
                "id": "dept_1_cat_5_drug_ABC123",
                "name": "Drug Name ABC",
                "value": 25000.00,
                "drug_code": "ABC123",
                "quantity": 500.0,
                "transaction_count": 45
              }
            ]
          }
        ]
      }
    ],
    "config": {
      "type": "sunburst",
      "description": "Hierarchical cost breakdown: Department → Category → Drug"
    }
  }
}
```

#### 2. Top Cost Drivers (Horizontal Bar Chart)

**Structure:** Top 20 drugs by total cost

```json
{
  "top_cost_drivers": {
    "data": [
      {
        "drug_code": "ABC123",
        "drug_name": "Drug Name ABC",
        "department_id": 1,
        "category_id": 5,
        "total_cost": 25000.00,
        "total_quantity": 500.0,
        "avg_unit_price": 50.0,
        "transaction_count": 45
      },
      {
        "drug_code": "XYZ789",
        "drug_name": "Drug Name XYZ",
        "department_id": 2,
        "category_id": 6,
        "total_cost": 18000.50,
        "total_quantity": 300.0,
        "avg_unit_price": 60.0,
        "transaction_count": 30
      }
    ],
    "config": {
      "type": "horizontal_bar",
      "description": "Top 20 drugs by total cost",
      "x_axis": "total_cost",
      "y_axis": "drug_name"
    }
  }
}
```

#### 3. Cost Trends (Line Chart)

**Daily Trends:**
```json
{
  "cost_trends": {
    "daily": {
      "data": [
        {
          "date": "2019-01-01",
          "total_cost": 5000.00,
          "total_quantity": 100.0,
          "transaction_count": 25,
          "avg_unit_price": 50.0
        },
        {
          "date": "2019-01-02",
          "total_cost": 5200.50,
          "total_quantity": 105.0,
          "transaction_count": 27,
          "avg_unit_price": 49.5
        }
      ],
      "config": {
        "type": "line",
        "description": "Daily cost trends",
        "x_axis": "date",
        "y_axis": "total_cost"
      }
    }
  }
}
```

**Monthly Trends:**
```json
{
  "cost_trends": {
    "monthly": {
      "data": [
        {
          "date": "2019-01",
          "total_cost": 150000.00,
          "total_quantity": 3000.0,
          "transaction_count": 750,
          "avg_unit_price": 50.0
        },
        {
          "date": "2019-02",
          "total_cost": 165000.50,
          "total_quantity": 3200.0,
          "transaction_count": 800,
          "avg_unit_price": 51.5
        }
      ],
      "config": {
        "type": "line",
        "description": "Monthly cost trends",
        "x_axis": "date",
        "y_axis": "total_cost"
      }
    }
  }
}
```

#### 4. Bubble Chart Data

**Structure:** Unit Price (x) vs Quantity (y) vs Frequency (size)

```json
{
  "bubble_chart": {
    "data": [
      {
        "drug_code": "ABC123",
        "drug_name": "Drug Name ABC",
        "department_id": 1,
        "category_id": 5,
        "unit_price": 50.0,
        "quantity": 500.0,
        "frequency": 45,
        "total_cost": 25000.00
      },
      {
        "drug_code": "XYZ789",
        "drug_name": "Drug Name XYZ",
        "department_id": 2,
        "category_id": 6,
        "unit_price": 60.0,
        "quantity": 300.0,
        "frequency": 30,
        "total_cost": 18000.50
      }
    ],
    "config": {
      "type": "bubble",
      "description": "Unit Price vs Quantity vs Frequency",
      "x_axis": "unit_price",
      "y_axis": "quantity",
      "size": "frequency"
    }
  }
}
```

### Error Responses

**Missing Required Parameters:**
```json
{
  "success": false,
  "error": {
    "message": "start_date is required",
    "code": "VALIDATION_ERROR"
  }
}
```

**Invalid Date Range:**
```json
{
  "success": false,
  "error": {
    "message": "end_date must be after or equal to start_date",
    "code": "VALIDATION_ERROR"
  }
}
```

**Invalid Price Range:**
```json
{
  "success": false,
  "error": {
    "message": "price_max must be greater than or equal to price_min",
    "code": "VALIDATION_ERROR"
  }
}
```

**No Data Found:**
```json
{
  "success": false,
  "error": {
    "message": "No cost data found for the specified filters",
    "code": "NO_DATA_FOUND"
  }
}
```

### Visualization Recommendations

#### 1. Sunburst Chart
**Purpose:** Hierarchical cost breakdown visualization

**Recommended Libraries:**
- **D3.js**: Full control and customization
- **Plotly.js**: `<Plotly>` component with built-in sunburst support
- **Recharts**: Custom implementation using `<PieChart>` with nested structure
- **Nivo**: `<Sunburst>` component

**Example with Plotly.js:**
```javascript
import Plotly from 'plotly.js-dist-min';

const sunburstData = {
  type: 'sunburst',
  labels: data.map(d => d.name),
  parents: data.map(d => d.parent || ''),
  values: data.map(d => d.value),
  branchvalues: 'total'
};

Plotly.newPlot('sunburst-chart', [sunburstData]);
```

**Example with Nivo:**
```tsx
import { ResponsiveSunburst } from '@nivo/sunburst';

<ResponsiveSunburst
  data={sunburstData}
  margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
  id="name"
  value="value"
  cornerRadius={2}
  borderColor={{ theme: 'background' }}
  colors={{ scheme: 'nivo' }}
/>
```

#### 2. Horizontal Bar Chart (Top Cost Drivers)
**Purpose:** Display top 20 cost drivers

**Recommended Libraries:**
- **Recharts**: `<BarChart>` with `layout="vertical"`
- **Chart.js**: Horizontal bar chart
- **Nivo**: `<BarChart>` with horizontal layout

**Example with Recharts:**
```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

<ResponsiveContainer width="100%" height={600}>
  <BarChart data={topDriversData} layout="vertical">
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis type="number" />
    <YAxis dataKey="drug_name" type="category" width={200} />
    <Tooltip />
    <Legend />
    <Bar dataKey="total_cost" fill="#8884d8" name="Total Cost" />
  </BarChart>
</ResponsiveContainer>
```

#### 3. Line Chart (Cost Trends)
**Purpose:** Show daily or monthly cost trends over time

**Recommended Libraries:**
- **Recharts**: `<LineChart>`
- **Chart.js**: Line chart
- **Nivo**: `<LineChart>`

**Example with Recharts:**
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

<ResponsiveContainer width="100%" height={400}>
  <LineChart data={dailyTrendsData}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="date" />
    <YAxis />
    <Tooltip />
    <Legend />
    <Line type="monotone" dataKey="total_cost" stroke="#8884d8" name="Total Cost" />
    <Line type="monotone" dataKey="total_quantity" stroke="#82ca9d" name="Total Quantity" />
  </LineChart>
</ResponsiveContainer>
```

#### 4. Bubble Chart
**Purpose:** Show relationship between unit price, quantity, and frequency

**Recommended Libraries:**
- **Recharts**: `<ScatterChart>` with size mapping
- **Plotly.js**: Scatter plot with size parameter
- **Nivo**: `<Bubble>` component

**Example with Recharts:**
```tsx
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

<ResponsiveContainer width="100%" height={400}>
  <ScatterChart>
    <CartesianGrid />
    <XAxis type="number" dataKey="unit_price" name="Unit Price" />
    <YAxis type="number" dataKey="quantity" name="Quantity" />
    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
    <Scatter name="Drugs" data={bubbleData} fill="#8884d8">
      {bubbleData.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={getColorByFrequency(entry.frequency)} />
      ))}
    </Scatter>
  </ScatterChart>
</ResponsiveContainer>
```

### Use Cases

1. **Cost Analysis Dashboard**
   - Use all four charts together for comprehensive cost analysis
   - Filter by department to analyze department-specific costs
   - Use price range filters to focus on high-value or low-value drugs

2. **Budget Planning**
   - Use monthly trends to identify cost patterns
   - Use top cost drivers to identify areas for cost optimization
   - Use sunburst to understand cost distribution across departments

3. **Drug Procurement Analysis**
   - Use bubble chart to identify drugs with high frequency but low cost
   - Use top cost drivers to prioritize procurement decisions
   - Filter by category to analyze category-specific costs

4. **Department Performance**
   - Filter by specific departments to compare costs
   - Use sunburst to see cost breakdown within departments
   - Use trends to track department cost changes over time

### Best Practices

1. **Date Range Selection**
   - Use appropriate date ranges (e.g., monthly for trends, yearly for comprehensive analysis)
   - Consider data volume - very large date ranges may impact performance

2. **Filtering**
   - Start with broad filters and narrow down based on insights
   - Use price range filters to focus on specific cost segments
   - Combine multiple filters for targeted analysis

3. **Performance**
   - Cache responses for frequently accessed date ranges
   - Consider pagination for very large datasets (future enhancement)

4. **Visualization**
   - Use consistent color schemes across charts
   - Include tooltips with detailed information
   - Make charts interactive for better user experience
   - Responsive design for mobile devices

---

