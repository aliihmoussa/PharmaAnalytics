# Forecasting Endpoint Naming - Expert Analysis

## 🎯 Current Issue

**Current endpoint**: `/api/forecasting/forecast-enhanced/{drug_code}`

### Problems:
1. ❌ **Redundant**: "forecast" is already in the module name (`forecasting`)
2. ❌ **Vague**: "enhanced" doesn't tell us what makes it enhanced
3. ❌ **Not RESTful**: Should be resource-based, not action-based
4. ❌ **Too long**: Unnecessarily verbose

---

## ✅ Recommended Solution

### **Best Option: `/api/forecasting/{drug_code}`**

**Why this is best:**
- ✅ **Clean & Simple**: No redundant words
- ✅ **RESTful**: Resource-based naming (the resource is the forecast for a drug)
- ✅ **Professional**: Follows REST API best practices
- ✅ **Clear**: The module name already indicates it's forecasting
- ✅ **Scalable**: Easy to add related endpoints later (e.g., `/api/forecasting/{drug_code}/metrics`)

### **Alternative Options Considered:**

1. `/api/forecasting/drugs/{drug_code}`
   - ✅ More explicit about resource
   - ❌ Longer, less clean
   - ❌ "drugs" is plural but we're getting one drug

2. `/api/forecasting/demand/{drug_code}`
   - ✅ More specific (demand forecasting)
   - ❌ "demand" is implied by "forecasting"
   - ❌ Adds unnecessary word

3. `/api/forecasting/predictions/{drug_code}`
   - ✅ Clear purpose
   - ❌ Redundant with "forecasting"
   - ❌ Less RESTful

---

## 📋 REST API Best Practices Applied

### **Resource-Based Naming**
- ✅ Resource: Forecast for a drug
- ✅ Identifier: `{drug_code}`
- ✅ Method: GET (implicit in REST)

### **Simplicity Principle**
- ✅ Shortest path that clearly identifies the resource
- ✅ No redundant words
- ✅ Module name provides context

### **Consistency**
- ✅ Matches pattern: `/api/{module}/{resource_id}`
- ✅ Similar to: `/api/diagnostics/features/{drug_code}`

---

## 🔄 Migration Plan

### **Changes Required:**

1. **Update route**:
   ```python
   # OLD
   @forecasting_bp.route('/forecast-enhanced/<drug_code>', methods=['GET'])
   
   # NEW
   @forecasting_bp.route('/<drug_code>', methods=['GET'])
   ```

2. **Update function name**:
   ```python
   # OLD
   def get_enhanced_forecast(drug_code: str):
   
   # NEW
   def get_forecast(drug_code: str):
   ```

3. **Update service class name** (optional, for consistency):
   ```python
   # OLD
   class EnhancedXGBoostForecastService:
   
   # NEW
   class ForecastService:  # or XGBoostForecastService
   ```

4. **Update documentation** - All references to old endpoint

---

## 📊 Comparison

| Aspect | Current | Recommended |
|--------|---------|-------------|
| **URL** | `/api/forecasting/forecast-enhanced/{drug_code}` | `/api/forecasting/{drug_code}` |
| **Length** | 47 chars | 33 chars |
| **Clarity** | ⚠️ Vague ("enhanced"?) | ✅ Clear |
| **RESTful** | ❌ Action-based | ✅ Resource-based |
| **Redundancy** | ❌ "forecast" redundant | ✅ No redundancy |
| **Professional** | ⚠️ OK | ✅ Excellent |

---

## ✅ Final Recommendation

**Use**: `/api/forecasting/{drug_code}`

This is the cleanest, most professional, and most RESTful option.

---

**Status**: Ready for implementation

