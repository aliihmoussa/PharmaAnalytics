# Forecasting API Design - Best Practices Analysis

## 🤔 Question: Should Algorithm Name Be in the Endpoint?

**Short Answer: No, it's generally NOT best practice.**

---

## ❌ Problems with Algorithm in URL

### **1. Violates REST Principles**
REST APIs should be **resource-oriented**, not **implementation-oriented**.

```
❌ BAD:  /api/forecasting/xgboost/{drug_code}
✅ GOOD: /api/forecasting/{drug_code}
```

The **resource** is the forecast, not the algorithm. The algorithm is an **implementation detail**.

### **2. Exposes Implementation Details**
- Users shouldn't need to know about XGBoost, LSTM, ARIMA
- API should abstract away technical details
- Makes API harder to use for non-technical users

### **3. Inflexible**
What if you want to:
- Use **ensemble methods** (combining multiple algorithms)?
- **Auto-select** the best algorithm based on data?
- **Deprecate** an algorithm?
- **Change** the default algorithm?

With algorithm in URL, you're locked into that structure.

### **4. Not How Major APIs Do It**

**Google Cloud ML:**
```
POST /v1/projects/{project}/models/{model}/versions/{version}:predict
```
- Uses model versions, not algorithm names

**AWS SageMaker:**
```
POST /endpoints/{endpoint}/invocations
```
- Uses endpoints, not algorithm names

**OpenAI:**
```
POST /v1/chat/completions
```
- Model specified in request body, not URL

---

## ✅ Best Practice: Algorithm as Configuration

### **Option 1: Query Parameter (Recommended)**

```
GET /api/forecasting/{drug_code}?algorithm=xgboost
GET /api/forecasting/{drug_code}?algorithm=lstm
GET /api/forecasting/{drug_code}                    # Default
```

**Benefits:**
- ✅ Algorithm is configuration, not part of resource
- ✅ Easy to change default
- ✅ Can add auto-selection later
- ✅ Backward compatible
- ✅ Cleaner URL structure

### **Option 2: Request Body (For POST) or Headers**

```
POST /api/forecasting/{drug_code}
{
  "algorithm": "xgboost",
  "forecast_days": 30,
  ...
}
```

**Benefits:**
- ✅ Most flexible
- ✅ Can specify multiple parameters
- ✅ Standard REST pattern

### **Option 3: Model/Version Approach**

```
GET /api/forecasting/{drug_code}?model=v1
GET /api/forecasting/{drug_code}?model=xgboost-v2
GET /api/forecasting/{drug_code}?model=lstm-v1
```

**Benefits:**
- ✅ Abstracts algorithm behind model concept
- ✅ Can version algorithms
- ✅ More professional

---

## 🎯 Recommended Design

### **Primary Endpoint (Simple & Clean)**
```
GET /api/forecasting/{drug_code}
```
- Uses default algorithm (configurable)
- Most users don't need to specify algorithm

### **With Algorithm Override (Advanced Users)**
```
GET /api/forecasting/{drug_code}?algorithm=xgboost
GET /api/forecasting/{drug_code}?algorithm=lstm
```

### **Algorithm Discovery**
```
GET /api/forecasting/algorithms
```
Returns available algorithms and their capabilities.

---

## 📋 Implementation

### **Updated Routes**

```python
@forecasting_bp.route('/<drug_code>', methods=['GET'])
@handle_exceptions
def get_forecast(drug_code: str):
    """
    GET /api/forecasting/{drug_code}
    
    Generate demand forecast for a drug.
    
    Query params:
    - algorithm: str (optional, default: 'xgboost') - Algorithm to use
    - forecast_days: int (default: 30)
    - test_size: int (default: 30)
    - lookback_days: int (optional)
    - start_date: YYYY-MM-DD (optional)
    - end_date: YYYY-MM-DD (optional)
    - department: int (optional)
    """
    # Get algorithm from query param or use default
    algorithm = request.args.get('algorithm', 'xgboost')
    
    # Parse other parameters
    try:
        params = ForecastParams.from_request(request)
    except ValidationError as e:
        return format_success_response({'error': str(e)}, 400)
    
    try:
        forecaster = ForecastAlgorithmFactory.get_algorithm(algorithm)
        result = forecaster.forecast(
            drug_code=drug_code,
            forecast_days=params.forecast_days,
            test_size=params.test_size,
            lookback_days=params.lookback_days,
            start_date=params.start_date,
            end_date=params.end_date,
            department=params.department
        )
        return format_success_response(result)
    except ValueError as e:
        return format_success_response({'error': str(e)}, 400)
```

### **Updated Parser**

```python
@dataclass
class ForecastParams:
    forecast_days: int
    test_size: int
    algorithm: str = 'xgboost'  # Add algorithm parameter
    lookback_days: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    department: Optional[int] = None
    
    @classmethod
    def from_request(cls, request: Request, ...) -> 'ForecastParams':
        # ... existing parsing ...
        
        # Parse algorithm
        algorithm = request.args.get('algorithm', 'xgboost')
        if algorithm not in ForecastAlgorithmFactory.list_algorithms():
            raise ValidationError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Available: {', '.join(ForecastAlgorithmFactory.list_algorithms())}"
            )
        
        return cls(
            forecast_days=forecast_days,
            test_size=test_size,
            algorithm=algorithm,
            lookback_days=lookback_days,
            start_date=start_date,
            end_date=end_date,
            department=department
        )
```

---

## 📊 Comparison

| Aspect | Algorithm in URL | Algorithm as Query Param |
|--------|-----------------|-------------------------|
| **RESTful** | ❌ No (implementation detail) | ✅ Yes (configuration) |
| **Flexibility** | ❌ Low | ✅ High |
| **Abstraction** | ❌ Exposes details | ✅ Hides details |
| **Backward Compatible** | ⚠️ Harder | ✅ Easy |
| **User Experience** | ❌ Technical | ✅ Simple |
| **Future-Proof** | ❌ Limited | ✅ Flexible |

---

## 🎯 When Algorithm in URL Makes Sense

Algorithm in URL is acceptable when:

1. **Different algorithms = Different resources**
   - Example: `/api/reports/pdf` vs `/api/reports/excel`
   - These are fundamentally different outputs

2. **Algorithm is part of the domain model**
   - Example: `/api/analytics/real-time` vs `/api/analytics/batch`
   - These represent different business concepts

3. **You want explicit versioning**
   - Example: `/api/v1/forecasting/{drug_code}` vs `/api/v2/forecasting/{drug_code}`
   - Versioning is different from algorithm selection

---

## ✅ Final Recommendation

**Use query parameter approach:**

```
GET /api/forecasting/{drug_code}?algorithm=xgboost
```

**Why:**
1. ✅ Follows REST best practices
2. ✅ Abstracts implementation details
3. ✅ More flexible for future changes
4. ✅ Better user experience
5. ✅ Easier to add auto-selection later
6. ✅ Matches industry standards

**Default behavior:**
- If no algorithm specified → use default (configurable)
- Most users never need to specify algorithm
- Advanced users can override when needed

---

## 🚀 Example Usage

```bash
# Default algorithm (simplest)
curl "http://localhost:5000/api/forecasting/P182054?forecast_days=30"

# Specific algorithm (advanced)
curl "http://localhost:5000/api/forecasting/P182054?forecast_days=30&algorithm=xgboost"

# List available algorithms
curl "http://localhost:5000/api/forecasting/algorithms"
```

---

## 📚 References

- [REST API Design Best Practices](https://restfulapi.net/)
- [Google Cloud ML API Design](https://cloud.google.com/ai-platform/prediction/docs)
- [AWS SageMaker API Design](https://docs.aws.amazon.com/sagemaker/)
- [Microsoft Azure ML API Design](https://docs.microsoft.com/azure/machine-learning/)

---

**Conclusion**: Keep the endpoint clean and simple. Use query parameters for algorithm selection.

