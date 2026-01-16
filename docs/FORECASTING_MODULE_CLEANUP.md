# Forecasting Module Cleanup & Rename

## 🎯 Goals

1. **Rename module** from `ml_xgboost` to `forecasting` (more professional)
2. **Remove unused code** - keep only what's needed for `/forecast-enhanced/{drug_code}` endpoint
3. **Update URL prefix** from `/api/ml-xgboost` to `/api/forecasting`

---

## 📋 Current State

### **Endpoints in routes.py:**
- ✅ `/forecast-enhanced/<drug_code>` - **KEEP** (main endpoint)
- ❌ `/forecast/<drug_code>` - **REMOVE** (unused)
- ❌ `/data-check/<drug_code>` - **REMOVE** (unused)
- ✅ `/health` - **KEEP** (useful for monitoring)

---

## 🗑️ Files to Remove

### **1. `service.py`** ❌
**Reason:** Only used by `/forecast/<drug_code>` endpoint which we're removing
- Contains `XGBoostForecastService` class
- Not imported by `service_enhanced.py`
- Not used anywhere else

### **2. Unused code in `parsers.py`** ❌
**Remove:**
- `ForecastParams` class (only used by removed endpoint)
- `DataCheckParams` class (only used by removed endpoint)

**Keep:**
- `EnhancedForecastParams` class ✅
- `ValidationError` exception ✅

### **3. Unused endpoints in `routes.py`** ❌
**Remove:**
- `get_xgboost_forecast()` function
- `check_data_availability()` function

**Keep:**
- `get_enhanced_forecast()` function ✅
- `health_check()` function ✅

---

## ✅ Files to Keep (All Used by Enhanced Endpoint)

### **Core Files:**
- ✅ `routes.py` (cleaned)
- ✅ `parsers.py` (cleaned)
- ✅ `service_enhanced.py`
- ✅ `__init__.py`

### **Utils:**
- ✅ `utils/enhanced_data_preparation.py`
- ✅ `utils/data_preparation.py` (used by enhanced)
- ✅ `utils/evaluation.py`
- ✅ `utils/forecast_generator.py`

### **Features:**
- ✅ `features/xgboost_features.py`
- ✅ `features/enhanced_features.py`

### **Models:**
- ✅ `models/xgboost_forecaster.py`

---

## 🔄 Module Rename: `ml_xgboost` → `forecasting`

### **Why `forecasting`?**
- ✅ Professional and clear
- ✅ Describes the purpose (forecasting demand)
- ✅ Not tied to specific algorithm (XGBoost)
- ✅ Shorter and cleaner than `ml_xgboost`
- ✅ Matches naming pattern with `diagnostics` module

### **Alternative Names Considered:**
- `demand_forecast` - Too specific
- `forecast_engine` - Too technical
- `forecasting_service` - Too long
- `forecasting` - ✅ **Best choice**

---

## 📝 Changes Required

### **1. Rename Directory**
```bash
mv backend/app/modules/ml_xgboost backend/app/modules/forecasting
```

### **2. Update Blueprint**
```python
# OLD
ml_xgboost_bp = Blueprint('ml_xgboost', __name__, url_prefix='/api/ml-xgboost')

# NEW
forecasting_bp = Blueprint('forecasting', __name__, url_prefix='/api/forecasting')
```

### **3. Update Imports in `__init__.py` (app)**
```python
# OLD
from backend.app.modules.ml_xgboost.routes import ml_xgboost_bp
app.register_blueprint(ml_xgboost_bp)

# NEW
from backend.app.modules.forecasting.routes import forecasting_bp
app.register_blueprint(forecasting_bp)
```

### **4. Update Internal Imports**
All files in the module need to update:
```python
# OLD
from backend.app.modules.ml_xgboost.service_enhanced import ...

# NEW
from backend.app.modules.forecasting.service_enhanced import ...
```

### **5. Update API Endpoint**
```
# OLD
GET /api/ml-xgboost/forecast-enhanced/{drug_code}

# NEW
GET /api/forecasting/forecast-enhanced/{drug_code}
```

---

## 🎯 Final Structure

```
forecasting/
├── __init__.py
├── routes.py                    # Only enhanced endpoint + health
├── parsers.py                   # Only EnhancedForecastParams
├── service_enhanced.py          # Main service
├── features/
│   ├── xgboost_features.py
│   └── enhanced_features.py
├── models/
│   └── xgboost_forecaster.py
└── utils/
    ├── enhanced_data_preparation.py
    ├── data_preparation.py
    ├── evaluation.py
    └── forecast_generator.py
```

---

## ✅ Benefits

1. **Cleaner codebase** - No unused code
2. **Professional naming** - `forecasting` is clearer than `ml_xgboost`
3. **Better URL** - `/api/forecasting` is more intuitive
4. **Easier maintenance** - Less code to maintain
5. **Clearer purpose** - Name reflects what it does

---

## 📋 Implementation Checklist

- [ ] Create this cleanup plan
- [ ] Remove `service.py`
- [ ] Clean up `parsers.py` (remove unused classes)
- [ ] Clean up `routes.py` (remove unused endpoints)
- [ ] Rename module directory
- [ ] Update blueprint name and URL prefix
- [ ] Update all internal imports
- [ ] Update app registration in `__init__.py`
- [ ] Test the endpoint still works
- [ ] Update documentation

---

**Status**: Ready for implementation

