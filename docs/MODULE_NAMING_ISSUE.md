# Module Naming Issue: `ml` Module

## 🚨 Problem

The module is named `ml` but it **does NOT do machine learning forecasting**. It does **diagnostics and analysis**.

**Current Situation:**
- `ml` module = Diagnostics/Analysis (misleading name!)
- `ml_xgboost` module = Actual ML Forecasting (correct name)

**This is confusing because:**
- `ml` suggests machine learning, but it's actually statistical analysis
- The actual ML forecasting is in `ml_xgboost`
- Users might think `ml` does forecasting

---

## ✅ Better Name Options

### **Option 1: `diagnostics`** ⭐ (Recommended)
**Why:**
- Most accurate - the module does diagnostic analysis
- Has `diagnostics/` subdirectory already
- Clear purpose: analyze and diagnose drug demand patterns
- Not confused with ML

**API would become:**
```
GET /api/diagnostics/features/{drug_code}
```

### **Option 2: `analysis`**
**Why:**
- Simple and clear
- Describes what it does (analysis)
- Generic enough

**API would become:**
```
GET /api/analysis/features/{drug_code}
```

### **Option 3: `profiling`**
**Why:**
- Uses `DrugProfiler` class
- Describes the main function
- Clear purpose

**API would become:**
```
GET /api/profiling/features/{drug_code}
```

### **Option 4: `drug_analysis`**
**Why:**
- Very descriptive
- Clear it's about drug analysis
- Specific to domain

**API would become:**
```
GET /api/drug-analysis/features/{drug_code}
```

---

## 🎯 Recommendation: `diagnostics`

**Best choice:** `diagnostics`

**Reasons:**
1. ✅ Most accurate - module does diagnostic analysis
2. ✅ Already has `diagnostics/` subdirectory
3. ✅ Clear separation from ML forecasting
4. ✅ Professional terminology
5. ✅ Matches the purpose: diagnose data quality, patterns, risks

---

## 📋 What Needs to Change

If we rename `ml` → `diagnostics`:

### **Files to Rename:**
```
backend/app/modules/ml/
  → backend/app/modules/diagnostics/
```

### **Code Changes:**
1. **Import statements:**
   ```python
   # OLD
   from backend.app.modules.ml.routes import ml_bp
   from backend.app.modules.ml.services import FeatureService
   from backend.app.modules.ml.diagnostics import DrugProfiler
   
   # NEW
   from backend.app.modules.diagnostics.routes import diagnostics_bp
   from backend.app.modules.diagnostics.services import FeatureService
   from backend.app.modules.diagnostics.diagnostics import DrugProfiler
   ```

2. **Blueprint name:**
   ```python
   # OLD
   diagnostics_bp = Blueprint('diagnostics', __name__, url_prefix='/api/diagnostics')
   
   # NEW
   diagnostics_bp = Blueprint('diagnostics', __name__, url_prefix='/api/diagnostics')
   ```

3. **App registration:**
   ```python
   # OLD
   from backend.app.modules.ml.routes import ml_bp
   app.register_blueprint(ml_bp)
   
   # NEW
   from backend.app.modules.diagnostics.routes import diagnostics_bp
   app.register_blueprint(diagnostics_bp)
   ```

4. **API endpoint:**
   ```
   # OLD
   GET /api/diagnostics/features/{drug_code}
   
   # NEW
   GET /api/diagnostics/features/{drug_code}
   ```

### **Files to Update:**
- `backend/app/__init__.py` - Import and registration
- `backend/app/modules/ml/routes.py` - Blueprint name
- `backend/app/modules/ml/services/feature_service.py` - Imports
- `backend/app/modules/ml/services.py` - Imports (if any)
- All files in `backend/app/modules/ml/` - Internal imports
- Documentation files

---

## 🔄 Alternative: Keep Name, Update Documentation

If renaming is too much work, you could:

1. **Keep `ml` name** but clarify in documentation
2. **Add comments** explaining it's for diagnostics
3. **Update API docs** to make it clear

**But this is NOT recommended** - the name is still misleading.

---

## 📊 Comparison After Rename

### **Before (Confusing):**
```
ml/              → Suggests ML, but does diagnostics
ml_xgboost/      → Does actual ML
```

### **After (Clear):**
```
diagnostics/     → Does diagnostics/analysis ✅
ml_xgboost/      → Does ML forecasting ✅
```

---

## 🎯 Summary

**Current Problem:**
- `ml` module name is misleading
- It does diagnostics, not ML forecasting
- Actual ML is in `ml_xgboost`

**Solution:**
- Rename `ml` → `diagnostics`
- Makes purpose clear
- Separates analysis from forecasting

**Recommendation:**
- ✅ Rename to `diagnostics`
- ✅ Update all imports and references
- ✅ Update API endpoint to `/api/diagnostics/features/{drug_code}`
- ✅ Update documentation

---

## 🚀 Next Steps

1. **Decide on new name** (recommend `diagnostics`)
2. **Rename directory** `ml/` → `diagnostics/`
3. **Update all imports** in codebase
4. **Update API endpoint** documentation
5. **Test** that everything still works
6. **Update** frontend/client code if any

Would you like me to help with the renaming? I can:
- Find all references
- Create a migration script
- Update all files automatically

