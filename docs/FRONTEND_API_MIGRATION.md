# Frontend API Migration Guide

## Overview

The backend has been refactored to combine the `viz` and `dashboard` modules into a single unified `analytics` module. **All API endpoints have been moved from `/api/viz/*` and `/api/dashboard/*` to `/api/analytics/*`.**

### Important Notes
- ✅ **No breaking changes to request/response formats** - Only URL paths changed
- ✅ **All query parameters remain the same**
- ✅ **All response structures remain identical**
- ✅ **Authentication/authorization unchanged**

---

## Complete Endpoint Mapping

### Cost Analysis Endpoints (formerly `/api/viz/*`)

| Old Endpoint | New Endpoint | Method | Description |
|-------------|--------------|--------|-------------|
| `/api/viz/cost-analysis` | `/api/analytics/cost-analysis` | GET | Cost analysis with sunburst, trends, bubble charts |
| `/api/viz/hospital-stay-duration` | `/api/analytics/hospital-stay-duration` | GET | Hospital stay duration analysis |

### Dashboard Analytics Endpoints (formerly `/api/dashboard/*`)

| Old Endpoint | New Endpoint | Method | Description |
|-------------|--------------|--------|-------------|
| `/api/dashboard/top-drugs` | `/api/analytics/top-drugs` | GET | Top dispensed drugs by quantity |
| `/api/dashboard/drug-demand` | `/api/analytics/drug-demand` | GET | Drug demand time-series data |
| `/api/dashboard/summary-stats` | `/api/analytics/summary-stats` | GET | Overall dashboard statistics |
| `/api/dashboard/chart-data/<chart_type>` | `/api/analytics/chart-data/<chart_type>` | GET | Pre-formatted chart data (trends/seasonal/department) |
| `/api/dashboard/department-performance` | `/api/analytics/department-performance` | GET | Department performance metrics |
| `/api/dashboard/year-comparison` | `/api/analytics/year-comparison` | GET | Year-over-year comparison |
| `/api/dashboard/category-analysis` | `/api/analytics/category-analysis` | GET | Drug category analysis over time |
| `/api/dashboard/patient-demographics` | `/api/analytics/patient-demographics` | GET | Patient demographics analysis |

---

## Migration Steps

### Step 1: Update API Configuration

**Find your API base URL configuration file** (usually in `src/config/`, `src/constants/`, or `src/api/`):

```javascript
// ❌ OLD Configuration
const API_CONFIG = {
  base: '/api',
  viz: '/api/viz',
  dashboard: '/api/dashboard'
};

// ✅ NEW Configuration
const API_CONFIG = {
  base: '/api',
  analytics: '/api/analytics'
};
```

### Step 2: Update API Service Files

**If you have separate service files for viz and dashboard:**

```javascript
// ❌ OLD: src/api/viz.js
export const getCostAnalysis = (params) => {
  return axios.get('/api/viz/cost-analysis', { params });
};

export const getHospitalStayDuration = (params) => {
  return axios.get('/api/viz/hospital-stay-duration', { params });
};

// ✅ NEW: src/api/analytics.js (or merge into existing)
export const getCostAnalysis = (params) => {
  return axios.get('/api/analytics/cost-analysis', { params });
};

export const getHospitalStayDuration = (params) => {
  return axios.get('/api/analytics/hospital-stay-duration', { params });
};
```

```javascript
// ❌ OLD: src/api/dashboard.js
export const getTopDrugs = (params) => {
  return axios.get('/api/dashboard/top-drugs', { params });
};

export const getDrugDemand = (params) => {
  return axios.get('/api/dashboard/drug-demand', { params });
};

// ✅ NEW: src/api/analytics.js (merge all endpoints here)
export const getTopDrugs = (params) => {
  return axios.get('/api/analytics/top-drugs', { params });
};

export const getDrugDemand = (params) => {
  return axios.get('/api/analytics/drug-demand', { params });
};
```

### Step 3: Global Find & Replace

**Search for all occurrences and replace:**

1. **Search for:** `/api/viz/`
   **Replace with:** `/api/analytics/`

2. **Search for:** `/api/dashboard/`
   **Replace with:** `/api/analytics/`

**Common locations to check:**
- `src/api/` - API service files
- `src/services/` - Service layer files
- `src/config/` - Configuration files
- `src/constants/` - Constants files
- Component files making direct API calls
- Hook files (React hooks, Vue composables, etc.)

### Step 4: Update Environment Variables (if used)

```bash
# ❌ OLD
REACT_APP_VIZ_API=/api/viz
REACT_APP_DASHBOARD_API=/api/dashboard

# ✅ NEW
REACT_APP_ANALYTICS_API=/api/analytics
```

---

## Detailed Examples

### Example 1: Cost Analysis

```javascript
// ❌ OLD
const fetchCostAnalysis = async (filters) => {
  const response = await fetch(
    `/api/viz/cost-analysis?start_date=${filters.startDate}&end_date=${filters.endDate}`
  );
  return response.json();
};

// ✅ NEW
const fetchCostAnalysis = async (filters) => {
  const response = await fetch(
    `/api/analytics/cost-analysis?start_date=${filters.startDate}&end_date=${filters.endDate}`
  );
  return response.json();
};
```

### Example 2: Top Drugs (Axios)

```javascript
// ❌ OLD
import axios from 'axios';

const getTopDrugs = async (startDate, endDate, limit = 10) => {
  const { data } = await axios.get('/api/dashboard/top-drugs', {
    params: {
      start_date: startDate,
      end_date: endDate,
      limit
    }
  });
  return data;
};

// ✅ NEW
import axios from 'axios';

const getTopDrugs = async (startDate, endDate, limit = 10) => {
  const { data } = await axios.get('/api/analytics/top-drugs', {
    params: {
      start_date: startDate,
      end_date: endDate,
      limit
    }
  });
  return data;
};
```

### Example 3: Chart Data (React Hook)

```javascript
// ❌ OLD
import { useState, useEffect } from 'react';
import api from '@/services/api';

const useChartData = (chartType, startDate, endDate) => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    api.get(`/api/dashboard/chart-data/${chartType}`, {
      params: { start_date: startDate, end_date: endDate }
    }).then(response => setData(response.data));
  }, [chartType, startDate, endDate]);
  
  return data;
};

// ✅ NEW
import { useState, useEffect } from 'react';
import api from '@/services/api';

const useChartData = (chartType, startDate, endDate) => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    api.get(`/api/analytics/chart-data/${chartType}`, {
      params: { start_date: startDate, end_date: endDate }
    }).then(response => setData(response.data));
  }, [chartType, startDate, endDate]);
  
  return data;
};
```

### Example 4: Vue Composition API

```javascript
// ❌ OLD
import { ref, onMounted } from 'vue';
import axios from 'axios';

export const useDepartmentPerformance = () => {
  const departments = ref([]);
  
  const fetchData = async (startDate, endDate) => {
    const { data } = await axios.get('/api/dashboard/department-performance', {
      params: { start_date: startDate, end_date: endDate }
    });
    departments.value = data.data.departments;
  };
  
  return { departments, fetchData };
};

// ✅ NEW
import { ref, onMounted } from 'vue';
import axios from 'axios';

export const useDepartmentPerformance = () => {
  const departments = ref([]);
  
  const fetchData = async (startDate, endDate) => {
    const { data } = await axios.get('/api/analytics/department-performance', {
      params: { start_date: startDate, end_date: endDate }
    });
    departments.value = data.data.departments;
  };
  
  return { departments, fetchData };
};
```

---

## Complete API Reference

### All Analytics Endpoints

```javascript
// Cost Analysis
GET /api/analytics/cost-analysis
GET /api/analytics/hospital-stay-duration

// Dashboard Analytics
GET /api/analytics/top-drugs
GET /api/analytics/drug-demand
GET /api/analytics/summary-stats
GET /api/analytics/chart-data/{chart_type}
GET /api/analytics/department-performance
GET /api/analytics/year-comparison
GET /api/analytics/category-analysis
GET /api/analytics/patient-demographics
```

### Query Parameters (Unchanged)

All query parameters remain exactly the same. For example:

**Cost Analysis:**
- `start_date` (required): YYYY-MM-DD
- `end_date` (required): YYYY-MM-DD
- `departments` (optional): int[] (comma-separated)
- `price_min` (optional): float
- `price_max` (optional): float
- `drug_categories` (optional): int[] (comma-separated)

**Top Drugs:**
- `start_date` (required): YYYY-MM-DD
- `end_date` (required): YYYY-MM-DD
- `limit` (optional): int (default: 10, max: 100)
- `category_id` (optional): int
- `department_id` (optional): int

*(See backend API documentation for complete parameter lists)*

---

## Testing Checklist

After migration, test all endpoints:

- [ ] `/api/analytics/cost-analysis` - Cost analysis data loads
- [ ] `/api/analytics/hospital-stay-duration` - Hospital stay data loads
- [ ] `/api/analytics/top-drugs` - Top drugs list displays
- [ ] `/api/analytics/drug-demand` - Demand chart renders
- [ ] `/api/analytics/summary-stats` - Summary cards show data
- [ ] `/api/analytics/chart-data/trends` - Trends chart works
- [ ] `/api/analytics/chart-data/seasonal` - Seasonal chart works
- [ ] `/api/analytics/chart-data/department` - Department chart works
- [ ] `/api/analytics/department-performance` - Department table loads
- [ ] `/api/analytics/year-comparison` - Year comparison works
- [ ] `/api/analytics/category-analysis` - Category analysis displays
- [ ] `/api/analytics/patient-demographics` - Demographics chart works

---

## Troubleshooting

### Issue: 404 Not Found

**Symptom:** API calls return 404 errors

**Solution:** 
- Verify you've updated all endpoint URLs
- Check browser network tab for the exact URL being called
- Ensure you're using `/api/analytics/` not `/api/viz/` or `/api/dashboard/`

### Issue: CORS Errors

**Symptom:** CORS policy errors in browser console

**Solution:**
- CORS configuration unchanged - this shouldn't happen
- Verify backend is running and accessible
- Check if you're using the correct base URL

### Issue: Response Format Different

**Symptom:** Data structure seems different

**Solution:**
- Response formats are unchanged - this is likely a parsing issue
- Check your response handling code
- Verify you're accessing the correct nested properties

---

## Quick Reference Card

```
OLD ENDPOINTS                    →  NEW ENDPOINTS
─────────────────────────────────────────────────
/api/viz/cost-analysis           →  /api/analytics/cost-analysis
/api/viz/hospital-stay-duration  →  /api/analytics/hospital-stay-duration
/api/dashboard/top-drugs         →  /api/analytics/top-drugs
/api/dashboard/drug-demand        →  /api/analytics/drug-demand
/api/dashboard/summary-stats      →  /api/analytics/summary-stats
/api/dashboard/chart-data/*       →  /api/analytics/chart-data/*
/api/dashboard/department-*       →  /api/analytics/department-*
/api/dashboard/year-comparison    →  /api/analytics/year-comparison
/api/dashboard/category-*         →  /api/analytics/category-*
/api/dashboard/patient-*           →  /api/analytics/patient-*
```

**Find & Replace:**
- `/api/viz/` → `/api/analytics/`
- `/api/dashboard/` → `/api/analytics/`

---

## Support

If you encounter any issues during migration:
1. Check the browser console for error messages
2. Verify endpoint URLs in Network tab
3. Ensure all query parameters are being passed correctly
4. Review response structure matches expected format

