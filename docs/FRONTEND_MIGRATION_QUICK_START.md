# Frontend Migration - Quick Start Guide

## 🎯 What Changed

Backend merged `/api/viz/*` and `/api/dashboard/*` into `/api/analytics/*`

**Only URLs changed - everything else stays the same!**

---

## ⚡ Quick Migration (5 minutes)

### Step 1: Find & Replace

**In your entire frontend codebase:**

1. Find: `/api/viz/` → Replace: `/api/analytics/`
2. Find: `/api/dashboard/` → Replace: `/api/analytics/`

### Step 2: Test

Run your app and verify all API calls work.

**Done!** ✅

---

## 📋 Complete Endpoint List

### Old → New Mapping

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

---

## 🔍 Where to Look

Search these locations:

- `src/api/` - API service files
- `src/services/` - Service layer
- `src/config/` - Configuration
- `src/constants/` - Constants
- Component files - Direct API calls
- Hook files - Custom hooks

---

## ✅ What Stays the Same

- ✅ Query parameters
- ✅ Request body format
- ✅ Response structure
- ✅ Authentication
- ✅ Error handling

**Only the URL path changed!**

---

## 🧪 Quick Test

```javascript
// Test in browser console or Postman
fetch('/api/analytics/summary-stats')
  .then(r => r.json())
  .then(console.log);
```

If this works, migration is successful! 🎉

