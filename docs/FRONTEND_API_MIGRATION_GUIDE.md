# Frontend API Migration Guide

## Overview
The backend has been refactored to combine the `viz` and `dashboard` modules into a single `analytics` module. All API endpoints have been moved to `/api/analytics/*`.

**No breaking changes to request/response formats** - only the URL paths have changed.

---

## Endpoint Migration Table

### Cost Analysis Endpoints (formerly `/api/viz/*`)

| Old Endpoint | New Endpoint | Method | Notes |
|-------------|--------------|--------|-------|
| `/api/viz/cost-analysis` | `/api/analytics/cost-analysis` | GET | Same query params, same response |
| `/api/viz/hospital-stay-duration` | `/api/analytics/hospital-stay-duration` | GET | Same query params, same response |

### Dashboard Analytics Endpoints (formerly `/api/dashboard/*`)

| Old Endpoint | New Endpoint | Method | Notes |
|-------------|--------------|--------|-------|
| `/api/dashboard/top-drugs` | `/api/analytics/top-drugs` | GET | Same query params, same response |
| `/api/dashboard/drug-demand` | `/api/analytics/drug-demand` | GET | Same query params, same response |
| `/api/dashboard/summary-stats` | `/api/analytics/summary-stats` | GET | Same query params, same response |
| `/api/dashboard/chart-data/<chart_type>` | `/api/analytics/chart-data/<chart_type>` | GET | Same query params, same response |
| `/api/dashboard/department-performance` | `/api/analytics/department-performance` | GET | Same query params, same response |
| `/api/dashboard/year-comparison` | `/api/analytics/year-comparison` | GET | Same query params, same response |
| `/api/dashboard/category-analysis` | `/api/analytics/category-analysis` | GET | Same query params, same response |
| `/api/dashboard/patient-demographics` | `/api/analytics/patient-demographics` | GET | Same query params, same response |

---

## Migration Steps

### 1. Update API Base URLs

**Find and replace in your API configuration:**

```javascript
// OLD
const API_BASE = '/api';
const VIZ_BASE = '/api/viz';
const DASHBOARD_BASE = '/api/dashboard';

// NEW
const API_BASE = '/api';
const ANALYTICS_BASE = '/api/analytics';
```

### 2. Update API Service Files

**Example: If you have a service file like `api/dashboard.js` or `api/viz.js`:**

```javascript
// OLD
export const getTopDrugs = (params) => {
  return axios.get('/api/dashboard/top-drugs', { params });
};

// NEW
export const getTopDrugs = (params) => {
  return axios.get('/api/analytics/top-drugs', { params });
};
```

### 3. Update All API Calls

**Search and replace patterns:**

- `/api/viz/` → `/api/analytics/`
- `/api/dashboard/` → `/api/analytics/`

---

## Example Migrations

### Example 1: Cost Analysis

```javascript
// OLD
const response = await fetch('/api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31');

// NEW
const response = await fetch('/api/analytics/cost-analysis?start_date=2019-01-01&end_date=2019-12-31');
```

### Example 2: Top Drugs

```javascript
// OLD
axios.get('/api/dashboard/top-drugs', {
  params: {
    start_date: '2019-01-01',
    end_date: '2019-12-31',
    limit: 10
  }
});

// NEW
axios.get('/api/analytics/top-drugs', {
  params: {
    start_date: '2019-01-01',
    end_date: '2019-12-31',
    limit: 10
  }
});
```

### Example 3: Chart Data

```javascript
// OLD
const chartData = await api.get(`/api/dashboard/chart-data/trends`, {
  params: { start_date, end_date }
});

// NEW
const chartData = await api.get(`/api/analytics/chart-data/trends`, {
  params: { start_date, end_date }
});
```

---

## Quick Find & Replace Guide

### For TypeScript/JavaScript Projects:

1. **Search for all occurrences:**
   - `'/api/viz/`
   - `'/api/dashboard/`
   - `"/api/viz/`
   - `"/api/dashboard/`

2. **Replace with:**
   - `'/api/analytics/`
   - `"/api/analytics/`

### For React/Vue/Angular Projects:

**Check these common locations:**
- `src/api/` or `src/services/` - API service files
- `src/config/` - API configuration files
- `src/utils/` - API utility functions
- Component files that make direct API calls

---

## Important Notes

✅ **No response format changes** - All responses remain exactly the same  
✅ **No query parameter changes** - All query params work exactly the same  
✅ **No authentication changes** - Same auth headers and tokens  
✅ **Only URL paths changed** - Simple find & replace operation  

---

## Testing Checklist

After migration, verify these endpoints work:

- [ ] `/api/analytics/cost-analysis`
- [ ] `/api/analytics/hospital-stay-duration`
- [ ] `/api/analytics/top-drugs`
- [ ] `/api/analytics/drug-demand`
- [ ] `/api/analytics/summary-stats`
- [ ] `/api/analytics/chart-data/trends`
- [ ] `/api/analytics/chart-data/seasonal`
- [ ] `/api/analytics/chart-data/department`
- [ ] `/api/analytics/department-performance`
- [ ] `/api/analytics/year-comparison`
- [ ] `/api/analytics/category-analysis`
- [ ] `/api/analytics/patient-demographics`

---

## Need Help?

If you encounter any issues during migration:
1. Check browser console for 404 errors (old endpoints)
2. Verify the new endpoint URLs are correct
3. Ensure query parameters are still being passed correctly
4. Check that response parsing logic still works (should be identical)

