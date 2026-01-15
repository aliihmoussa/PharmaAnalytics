# Unused Files in Diagnostics Module

## 🚨 Issue: `demand_forecast.py` in Diagnostics Module

### **Problem:**

The file `backend/app/modules/diagnostics/models/demand_forecast.py` is:
1. ❌ **Not being used** - No imports found anywhere
2. ❌ **Wrong location** - It's a forecasting model, not a diagnostic tool
3. ❌ **Conflicts with purpose** - Diagnostics module should only do analysis, not forecasting

---

## 📊 Analysis

### **What `demand_forecast.py` Contains:**

- `DrugDemandForecaster` class
- ML model wrapper (XGBoost/RandomForest)
- Training and prediction methods
- Model persistence (save/load)

**This is a FORECASTING model, not a diagnostic tool!**

### **What's Actually Being Used:**

The `services.py` file uses:
```python
from backend.app.modules.diagnostics.forecast_service import DrugDemandForecaster
```

This imports from `forecast_service.py` (which also shouldn't be in diagnostics, but that's a separate issue).

**`models/demand_forecast.py` is NOT imported anywhere!**

---

## 🔍 Current Situation

### **Two Different `DrugDemandForecaster` Classes:**

1. **`forecast_service.py`** (USED)
   - Uses sklearn's `GradientBoostingRegressor`
   - Used by `services.py`
   - Still shouldn't be in diagnostics module

2. **`models/demand_forecast.py`** (UNUSED)
   - Generic ML wrapper for XGBoost/RandomForest
   - Not imported anywhere
   - Should be removed or moved

---

## 🎯 Recommendations

### **Option 1: Remove It** ⭐ (Recommended)

**Why:**
- Not being used
- Wrong location (diagnostics shouldn't have forecasting models)
- You already have `ml_xgboost` module for forecasting

**Action:**
```bash
rm backend/app/modules/diagnostics/models/demand_forecast.py
```

### **Option 2: Move to `ml_xgboost` Module**

**Why:**
- If you want to keep it for future use
- Belongs with other forecasting code

**Action:**
```bash
mv backend/app/modules/diagnostics/models/demand_forecast.py \
   backend/app/modules/ml_xgboost/models/demand_forecast.py
```

**Then update imports if needed.**

### **Option 3: Keep for Reference**

**Why:**
- Might be useful later
- Different implementation than `ml_xgboost`

**Action:**
- Move to a `legacy/` or `archive/` folder
- Document why it's there

---

## 📋 Also Check: `forecast_service.py`

The `forecast_service.py` file also shouldn't be in diagnostics:

- It's a forecasting service, not diagnostics
- Used by `services.py` for `gradient_boosting_forecast()`
- But `services.py` methods are not exposed via routes

**Recommendation:** 
- Either remove `forecast_service.py` and `services.py` methods (if not used)
- Or move them to `ml_xgboost` module

---

## ✅ Recommended Action Plan

1. **Remove `demand_forecast.py`** (unused, wrong location)
2. **Check if `forecast_service.py` is needed** (used by `services.py`, but `services.py` methods not exposed)
3. **Clean up `services.py`** - Remove unused forecasting methods if not needed
4. **Keep diagnostics module clean** - Only diagnostics/analysis code

---

## 🎯 Summary

**`demand_forecast.py` should be removed because:**
- ✅ Not used anywhere
- ✅ Wrong module (diagnostics ≠ forecasting)
- ✅ You have `ml_xgboost` for forecasting
- ✅ Keeps diagnostics module focused on its purpose

**The diagnostics module should only contain:**
- ✅ Diagnostic tools (profiler, seasonality, outliers, etc.)
- ✅ Analysis tools (decomposition, autocorrelation, etc.)
- ❌ NOT forecasting models

