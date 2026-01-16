# Frontend API Migration - Quick Reference for Cursor

## What Changed
Backend combined `/api/viz/*` and `/api/dashboard/*` into `/api/analytics/*`. Only URLs changed - no request/response format changes.

## Endpoint Mapping

**Old → New:**

```
/api/viz/cost-analysis                    → /api/analytics/cost-analysis
/api/viz/hospital-stay-duration           → /api/analytics/hospital-stay-duration
/api/dashboard/top-drugs                  → /api/analytics/top-drugs
/api/dashboard/drug-demand                 → /api/analytics/drug-demand
/api/dashboard/summary-stats               → /api/analytics/summary-stats
/api/dashboard/chart-data/<type>           → /api/analytics/chart-data/<type>
/api/dashboard/department-performance     → /api/analytics/department-performance
/api/dashboard/year-comparison             → /api/analytics/year-comparison
/api/dashboard/category-analysis           → /api/analytics/category-analysis
/api/dashboard/patient-demographics        → /api/analytics/patient-demographics
```

## Migration Task

**Find and replace all API endpoint URLs:**

1. Search for: `/api/viz/` → Replace with: `/api/analytics/`
2. Search for: `/api/dashboard/` → Replace with: `/api/analytics/`

**Check these files:**
- API service files (`src/api/`, `src/services/`)
- API config files (`src/config/`)
- Components making direct API calls
- Any constants defining API endpoints

**Important:** 
- ✅ Query parameters stay the same
- ✅ Request/response formats unchanged
- ✅ Only URL paths changed

**Example:**
```javascript
// Before
fetch('/api/dashboard/top-drugs?start_date=2019-01-01&end_date=2019-12-31')

// After
fetch('/api/analytics/top-drugs?start_date=2019-01-01&end_date=2019-12-31')
```

That's it! Simple find & replace operation.

