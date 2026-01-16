# Forecasting Endpoint Migration Guide - Frontend

## 🔄 Endpoint Changes

### **Old Endpoint (Deprecated)**
```
GET /api/ml-xgboost/forecast-enhanced/{drug_code}
```

### **New Endpoint (Current)**
```
GET /api/forecasting/{drug_code}
```

---

## 📋 What Changed

### **1. URL Path**
- **Old**: `/api/ml-xgboost/forecast-enhanced/{drug_code}`
- **New**: `/api/forecasting/{drug_code}`

### **2. Query Parameters** (Same)
All query parameters remain the same:
- `algorithm` (optional, default: `'xgboost'`) - **NEW** parameter
- `forecast_days` (default: 30)
- `test_size` (default: 30)
- `lookback_days` (optional)
- `start_date` (optional, YYYY-MM-DD)
- `end_date` (optional, YYYY-MM-DD)
- `department` (optional)

### **3. Response Format** (Same)
Response format is unchanged, but now includes `algorithm` field:
```json
{
  "success": true,
  "data": {
    "algorithm": "xgboost",
    "drug_code": "P182054",
    "drug_name": "...",
    "historical": [...],
    "forecast": [...],
    "test_predictions": [...],
    "metrics": {...},
    "feature_importance": {...},
    ...
  }
}
```

---

## 🔧 Frontend Migration Steps

### **Step 1: Update API Base URL**

**Before:**
```typescript
const FORECAST_API_BASE = '/api/ml-xgboost';
```

**After:**
```typescript
const FORECAST_API_BASE = '/api/forecasting';
```

### **Step 2: Update Endpoint Path**

**Before:**
```typescript
const url = `${FORECAST_API_BASE}/forecast-enhanced/${drugCode}`;
```

**After:**
```typescript
const url = `${FORECAST_API_BASE}/${drugCode}`;
```

### **Step 3: Update API Client Function**

**Before:**
```typescript
export async function getForecast(drugCode: string, params: ForecastParams) {
  const url = `${API_BASE}/api/ml-xgboost/forecast-enhanced/${drugCode}`;
  const queryParams = new URLSearchParams({
    forecast_days: params.forecastDays.toString(),
    test_size: params.testSize.toString(),
    // ... other params
  });
  
  const response = await fetch(`${url}?${queryParams}`);
  return response.json();
}
```

**After:**
```typescript
export async function getForecast(drugCode: string, params: ForecastParams) {
  const url = `${API_BASE}/api/forecasting/${drugCode}`;
  const queryParams = new URLSearchParams({
    algorithm: params.algorithm || 'xgboost',  // NEW: optional algorithm param
    forecast_days: params.forecastDays.toString(),
    test_size: params.testSize.toString(),
    // ... other params
  });
  
  const response = await fetch(`${url}?${queryParams}`);
  return response.json();
}
```

### **Step 4: Update TypeScript Types (Optional)**

Add algorithm parameter to your types:

```typescript
interface ForecastParams {
  algorithm?: string;  // NEW: optional, defaults to 'xgboost'
  forecastDays: number;
  testSize: number;
  lookbackDays?: number;
  startDate?: string;
  endDate?: string;
  department?: number;
}

interface ForecastResponse {
  success: boolean;
  data: {
    algorithm: string;  // NEW: algorithm used
    drug_code: string;
    drug_name: string;
    historical: Array<{...}>;
    forecast: Array<{...}>;
    test_predictions: Array<{...}>;
    metrics: {...};
    feature_importance: {...};
    // ... rest of response
  };
}
```

---

## 📝 Complete Example

### **React Hook Example**

**Before:**
```typescript
// hooks/useForecast.ts
export function useForecast(drugCode: string, params: ForecastParams) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    async function fetchForecast() {
      try {
        setLoading(true);
        const url = `${API_BASE}/api/ml-xgboost/forecast-enhanced/${drugCode}`;
        const queryParams = new URLSearchParams({
          forecast_days: params.forecastDays.toString(),
          test_size: params.testSize.toString(),
        });
        
        const response = await fetch(`${url}?${queryParams}`);
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    
    fetchForecast();
  }, [drugCode, params]);
  
  return { data, loading, error };
}
```

**After:**
```typescript
// hooks/useForecast.ts
export function useForecast(drugCode: string, params: ForecastParams) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    async function fetchForecast() {
      try {
        setLoading(true);
        const url = `${API_BASE}/api/forecasting/${drugCode}`;
        const queryParams = new URLSearchParams({
          algorithm: params.algorithm || 'xgboost',  // NEW
          forecast_days: params.forecastDays.toString(),
          test_size: params.testSize.toString(),
        });
        
        const response = await fetch(`${url}?${queryParams}`);
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    
    fetchForecast();
  }, [drugCode, params]);
  
  return { data, loading, error };
}
```

---

## 🎯 Quick Migration Checklist

- [ ] Update API base URL from `/api/ml-xgboost` to `/api/forecasting`
- [ ] Remove `/forecast-enhanced` from endpoint path
- [ ] Update all API client functions
- [ ] Update all fetch/axios calls
- [ ] Update TypeScript types (add `algorithm` field)
- [ ] Test with existing drug codes
- [ ] Verify response format (should be same)
- [ ] Update any hardcoded URLs in tests
- [ ] Update API documentation in frontend

---

## 🔍 Finding All References

### **Search for old endpoint in your frontend code:**

```bash
# Search for old endpoint
grep -r "ml-xgboost" frontend/
grep -r "forecast-enhanced" frontend/
grep -r "ml_xgboost" frontend/
```

### **Common places to check:**
- API client files (`lib/api/`, `services/`, `utils/api.ts`)
- React hooks (`hooks/useForecast.ts`, etc.)
- Components that call the API
- Test files
- Environment variables/config files
- Documentation files

---

## ✅ Testing

### **Test the new endpoint:**

```bash
# Test basic forecast
curl "http://localhost:5000/api/forecasting/P182054?forecast_days=30"

# Test with algorithm parameter
curl "http://localhost:5000/api/forecasting/P182054?forecast_days=30&algorithm=xgboost"

# Test with department filter
curl "http://localhost:5000/api/forecasting/P182054?forecast_days=30&department=5"

# List available algorithms
curl "http://localhost:5000/api/forecasting/algorithms"
```

---

## 📚 New Features Available

### **1. Algorithm Selection (NEW)**
You can now specify which algorithm to use:
```typescript
// Use default (xgboost)
getForecast(drugCode, { forecastDays: 30 });

// Explicitly specify algorithm
getForecast(drugCode, { 
  forecastDays: 30, 
  algorithm: 'xgboost' 
});
```

### **2. List Available Algorithms (NEW)**
```typescript
// GET /api/forecasting/algorithms
const algorithms = await fetch(`${API_BASE}/api/forecasting/algorithms`)
  .then(r => r.json());

console.log(algorithms.data.algorithms);  // ['xgboost']
console.log(algorithms.data.default);     // 'xgboost'
```

---

## ⚠️ Breaking Changes

### **What Breaks:**
- ❌ Old endpoint `/api/ml-xgboost/forecast-enhanced/{drug_code}` no longer exists
- ❌ Any hardcoded URLs using old path will fail

### **What Still Works:**
- ✅ All query parameters (same names and behavior)
- ✅ Response format (same structure)
- ✅ All existing functionality

---

## 🚀 Migration Timeline

### **Recommended Approach:**

1. **Phase 1**: Update frontend to use new endpoint
2. **Phase 2**: Test thoroughly
3. **Phase 3**: Deploy frontend update
4. **Phase 4**: Remove old endpoint support (if any)

---

## 📞 Support

If you encounter issues:
1. Check the new endpoint is accessible: `GET /api/forecasting/health`
2. Verify the drug code exists
3. Check query parameters are correct
4. Review response format matches expectations

---

## 📋 Summary

**Old**: `GET /api/ml-xgboost/forecast-enhanced/{drug_code}`  
**New**: `GET /api/forecasting/{drug_code}`

**Changes:**
- ✅ Simpler, cleaner URL
- ✅ More professional naming
- ✅ Same functionality
- ✅ New: Algorithm selection via query parameter
- ✅ New: `/algorithms` endpoint

**Action Required**: Update all frontend API calls to use new endpoint.

---

**Last Updated**: 2024-12-31

