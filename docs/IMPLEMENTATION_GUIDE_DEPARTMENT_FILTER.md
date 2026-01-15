# Implementation Guide: Adding Department Filter to Forecast API

## 🎯 Goal

Add `department` query parameter to filter forecasts by consuming department (C.R).

---

## 📋 Current State

- ✅ API endpoint exists: `/api/ml-xgboost/forecast-enhanced/{drug_code}`
- ✅ Supports: `forecast_days`, `test_size`, `start_date`, `end_date`, `lookback_days`
- ❌ Does NOT support: `department` filtering

---

## 🔧 Implementation Steps

### Step 1: Update Route Handler

**File:** `backend/app/modules/ml_xgboost/routes.py`

**Location:** `get_enhanced_forecast()` function (around line 100)

**Change:**

```python
# Add department parameter parsing (after line 128)
department = request.args.get('department')
department = int(department) if department else None

# Update service call (around line 166)
result = service.forecast(
    drug_code=drug_code,
    forecast_days=forecast_days,
    test_size=test_size,
    lookback_days=lookback_days,
    start_date=start_date,
    end_date=end_date,
    department=department  # Add this line
)
```

**Full updated function snippet:**

```python
@ml_xgboost_bp.route('/forecast-enhanced/<drug_code>', methods=['GET'])
@handle_exceptions
def get_enhanced_forecast(drug_code: str):
    """
    GET /api/ml-xgboost/forecast-enhanced/{drug_code}
    
    Enhanced XGBoost forecast with domain-specific features (departments, categories, rooms).
    Returns frontend-ready format with historical and forecast data.
    
    Query params:
    - forecast_days: int (default: 30) - Days to forecast ahead
    - test_size: int (default: 30) - Days to use for testing
    - lookback_days: int (optional) - Limit historical data
    - start_date: YYYY-MM-DD (optional) - Start date for historical data
    - end_date: YYYY-MM-DD (optional) - End date for historical data
    - department: int (optional) - Filter by consuming department (C.R)
    
    Returns:
        Frontend-ready forecast data with:
        - historical: Array of {date, demand, type: 'actual'}
        - forecast: Array of {date, predicted, lower, upper, type: 'predicted'}
        - test_predictions: Array of {date, actual, predicted, error, type: 'test'}
        - metrics: {rmse, mae, mape, r2}
        - feature_importance: Object with feature importance scores
    """
    # Parse query parameters
    forecast_days = int(request.args.get('forecast_days', 30))
    test_size = int(request.args.get('test_size', 30))
    lookback_days = request.args.get('lookback_days')
    lookback_days = int(lookback_days) if lookback_days else None
    
    # Add department parameter
    department = request.args.get('department')
    department = int(department) if department else None
    
    start_date = request.args.get('start_date')
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return format_success_response(
                {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                400
            )
    
    end_date = request.args.get('end_date')
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return format_success_response(
                {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                400
            )
    
    # Validation
    if forecast_days < 1 or forecast_days > 365:
        return format_success_response(
            {'error': 'forecast_days must be between 1 and 365'},
            400
        )
    
    if test_size < 7:
        return format_success_response(
            {'error': 'test_size must be at least 7'},
            400
        )
    
    service = EnhancedXGBoostForecastService()
    
    try:
        result = service.forecast(
            drug_code=drug_code,
            forecast_days=forecast_days,
            test_size=test_size,
            lookback_days=lookback_days,
            start_date=start_date,
            end_date=end_date,
            department=department  # Add this
        )
        return format_success_response(result)
    
    except ValueError as e:
        logger.error(f"Enhanced forecast error for {drug_code}: {str(e)}")
        return format_success_response(
            {'error': str(e)},
            400
        )
    except Exception as e:
        logger.error(f"Unexpected error in enhanced forecast for {drug_code}: {str(e)}", exc_info=True)
        return format_success_response(
            {'error': 'Internal server error during forecast'},
            500
        )
```

---

### Step 2: Update Service Method

**File:** `backend/app/modules/ml_xgboost/service_enhanced.py`

**Location:** `forecast()` method (around line 40)

**Change:**

```python
def forecast(
    self,
    drug_code: str,
    forecast_days: int = 30,
    test_size: int = 30,
    lookback_days: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    department: Optional[int] = None  # Add this parameter
) -> Dict:
```

**Update the data loading call (around line 69):**

```python
df = load_enhanced_transaction_data(
    drug_code=drug_code,
    start_date=start_date,
    end_date=end_date,
    lookback_days=lookback_days,
    department=department  # Add this
)
```

---

### Step 3: Update Data Loading Function

**File:** `backend/app/modules/ml_xgboost/utils/enhanced_data_preparation.py`

**Location:** `load_enhanced_transaction_data()` function (around line 16)

**Change:**

```python
def load_enhanced_transaction_data(
    drug_code: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    lookback_days: Optional[int] = None,
    department: Optional[int] = None  # Add this parameter
) -> pd.DataFrame:
```

**Add department filter to SQL query (around line 63):**

```python
# Build base query
query = session.query(
    func.date(DrugTransaction.transaction_date).label('date'),
    func.sum(func.abs(DrugTransaction.quantity)).filter(
        DrugTransaction.quantity < 0
    ).label('quantity'),
    # ... other fields ...
).filter(
    DrugTransaction.drug_code == drug_code,
    DrugTransaction.transaction_date >= start_date,
    DrugTransaction.transaction_date <= end_date,
    DrugTransaction.quantity < 0  # Only consumption
)

# Add department filter if provided
if department is not None:
    query = query.filter(DrugTransaction.cr == department)

query = query.group_by(
    func.date(DrugTransaction.transaction_date)
).order_by(
    func.date(DrugTransaction.transaction_date)
)
```

**Also update the detail query (around line 83):**

```python
detail_query = session.query(
    func.date(DrugTransaction.transaction_date).label('date'),
    DrugTransaction.cr,
    DrugTransaction.cs,
    DrugTransaction.cat,
    DrugTransaction.ad_date
).filter(
    DrugTransaction.drug_code == drug_code,
    DrugTransaction.transaction_date >= start_date,
    DrugTransaction.transaction_date <= end_date,
    DrugTransaction.quantity < 0
)

# Add department filter if provided
if department is not None:
    detail_query = detail_query.filter(DrugTransaction.cr == department)

detail_query = detail_query.all()
```

---

### Step 4: Update Documentation

**File:** `docs/api/BEGINNER_GUIDE_XGBOOST_FORECAST.md`

Add department parameter to the query parameters section:

```markdown
| `department` | int | No | - | Filter by consuming department (C.R) | Valid department ID |
```

**File:** `docs/api/QUICK_EXPLANATION_XGBOOST.md`

Add to parameters list:

```markdown
- `department`: Filter by department (optional)
```

---

### Step 5: Test the Implementation

**Create test:**

```python
# Test with department filter
url = f"{BASE_URL}/forecast-enhanced/P182054"
params = {
    "forecast_days": 30,
    "department": 1  # Department ID
}
response = requests.get(url, params=params)
```

**Expected behavior:**
- Without `department`: Returns forecast for all departments (current behavior)
- With `department`: Returns forecast only for that specific department

---

## ✅ Testing Checklist

- [ ] API accepts `department` parameter
- [ ] API returns 400 if department is invalid (non-integer)
- [ ] Forecast with department filter returns different results than without
- [ ] Error handling works if department has no data
- [ ] Documentation updated
- [ ] Test script updated

---

## 🐛 Potential Issues & Solutions

### Issue 1: No data for department
**Solution:** Return clear error message:
```python
if len(df) == 0:
    raise ValueError(
        f"No data found for drug_code='{drug_code}' "
        f"and department={department} between {start_date} and {end_date}"
    )
```

### Issue 2: Department ID validation
**Solution:** Optionally validate department exists:
```python
if department is not None:
    # Check if department exists (optional)
    dept_exists = session.query(
        session.query(DrugTransaction.cr).filter(
            DrugTransaction.cr == department
        ).exists()
    ).scalar()
    
    if not dept_exists:
        raise ValueError(f"Department {department} not found")
```

### Issue 3: Feature engineering with department filter
**Solution:** When filtering by department, some enhanced features (like department demand) may not be as meaningful. Consider:
- Still calculate category demand (still relevant)
- Skip department-specific features when filtering by department
- Or calculate department demand for OTHER departments (for comparison)

---

## 📝 Example Usage

### Without Department Filter (All Departments)
```bash
curl "http://localhost:5000/api/ml-xgboost/forecast-enhanced/P182054?forecast_days=30"
```

### With Department Filter
```bash
curl "http://localhost:5000/api/ml-xgboost/forecast-enhanced/P182054?forecast_days=30&department=1"
```

### Python Example
```python
import requests

url = "http://localhost:5000/api/ml-xgboost/forecast-enhanced/P182054"
params = {
    "forecast_days": 30,
    "test_size": 30,
    "department": 1  # Cardiology department
}

response = requests.get(url, params=params)
data = response.json()
```

---

## 🎯 Summary

**Files to modify:**
1. `backend/app/modules/ml_xgboost/routes.py` - Add parameter parsing
2. `backend/app/modules/ml_xgboost/service_enhanced.py` - Pass parameter to data loading
3. `backend/app/modules/ml_xgboost/utils/enhanced_data_preparation.py` - Add filter to SQL queries
4. Documentation files - Update parameter lists

**Estimated time:** 1-2 hours

**Testing time:** 30 minutes

---

**Ready to implement?** Follow the steps above, test thoroughly, and update documentation! 🚀

