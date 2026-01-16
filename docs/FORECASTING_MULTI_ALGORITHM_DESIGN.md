# Multi-Algorithm Forecasting Design

## 🎯 Problem Statement

Current implementation is tightly coupled to XGBoost. We need a scalable design that supports:
- XGBoost (current)
- LSTM (future)
- ARIMA (future)
- Prophet (future)
- Other algorithms

---

## ✅ Recommended Solution: Algorithm Sub-Routes

### **Design Pattern: Strategy Pattern + Factory**

**API Structure:**
```
GET /api/forecasting/{drug_code}                    # Default (XGBoost)
GET /api/forecasting/xgboost/{drug_code}            # Explicit XGBoost
GET /api/forecasting/lstm/{drug_code}               # LSTM
GET /api/forecasting/arima/{drug_code}              # ARIMA
GET /api/forecasting/prophet/{drug_code}            # Prophet
```

### **Benefits:**
- ✅ **RESTful**: Clear resource hierarchy
- ✅ **Explicit**: Algorithm is part of the URL
- ✅ **Scalable**: Easy to add new algorithms
- ✅ **Backward Compatible**: Default route maintains current behavior
- ✅ **Discoverable**: Users can see available algorithms

---

## 📋 Implementation Plan

### **1. Create Base Interface**

```python
# backend/app/modules/forecasting/base_forecaster.py

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import date

class BaseForecaster(ABC):
    """Base interface for all forecasting algorithms."""
    
    @abstractmethod
    def forecast(
        self,
        drug_code: str,
        forecast_days: int = 30,
        test_size: int = 30,
        lookback_days: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        department: Optional[int] = None
    ) -> Dict:
        """
        Generate forecast using the algorithm.
        
        Returns:
            Dictionary with forecast results in standard format:
            {
                'drug_code': str,
                'drug_name': str,
                'algorithm': str,
                'historical': [...],
                'forecast': [...],
                'test_predictions': [...],
                'metrics': {...},
                'feature_importance': {...},
                ...
            }
        """
        pass
    
    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Return the name of the algorithm."""
        pass
```

### **2. Refactor XGBoost Service**

```python
# backend/app/modules/forecasting/algorithms/xgboost_forecaster.py

from backend.app.modules.forecasting.base_forecaster import BaseForecaster
from backend.app.modules.forecasting.service_enhanced import ForecastService

class XGBoostForecaster(BaseForecaster):
    """XGBoost forecasting implementation."""
    
    def __init__(self):
        self._service = ForecastService()
    
    @property
    def algorithm_name(self) -> str:
        return 'xgboost'
    
    def forecast(self, **kwargs) -> Dict:
        result = self._service.forecast(**kwargs)
        result['algorithm'] = self.algorithm_name
        return result
```

### **3. Create Algorithm Factory**

```python
# backend/app/modules/forecasting/factory.py

from typing import Dict, Type
from backend.app.modules.forecasting.base_forecaster import BaseForecaster
from backend.app.modules.forecasting.algorithms.xgboost_forecaster import XGBoostForecaster

# Future implementations
# from backend.app.modules.forecasting.algorithms.lstm_forecaster import LSTMForecaster
# from backend.app.modules.forecasting.algorithms.arima_forecaster import ARIMAForecaster

class ForecastAlgorithmFactory:
    """Factory for creating forecast algorithm instances."""
    
    _algorithms: Dict[str, Type[BaseForecaster]] = {
        'xgboost': XGBoostForecaster,
        # 'lstm': LSTMForecaster,
        # 'arima': ARIMAForecaster,
        # 'prophet': ProphetForecaster,
    }
    
    @classmethod
    def get_algorithm(cls, algorithm: str = 'xgboost') -> BaseForecaster:
        """
        Get forecast algorithm instance.
        
        Args:
            algorithm: Algorithm name (default: 'xgboost')
            
        Returns:
            BaseForecaster instance
            
        Raises:
            ValueError: If algorithm is not supported
        """
        if algorithm not in cls._algorithms:
            available = ', '.join(cls._algorithms.keys())
            raise ValueError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Available algorithms: {available}"
            )
        
        return cls._algorithms[algorithm]()
    
    @classmethod
    def list_algorithms(cls) -> list:
        """List all available algorithms."""
        return list(cls._algorithms.keys())
```

### **4. Update Routes**

```python
# backend/app/modules/forecasting/routes.py

from flask import Blueprint, request
from backend.app.modules.forecasting.factory import ForecastAlgorithmFactory
from backend.app.modules.forecasting.parsers import ForecastParams, ValidationError
from backend.app.shared.middleware import handle_exceptions, format_success_response
import logging

logger = logging.getLogger(__name__)

forecasting_bp = Blueprint('forecasting', __name__, url_prefix='/api/forecasting')


@forecasting_bp.route('/<drug_code>', methods=['GET'])
@forecasting_bp.route('/xgboost/<drug_code>', methods=['GET'])
@handle_exceptions
def get_forecast(drug_code: str, algorithm: str = 'xgboost'):
    """
    GET /api/forecasting/{drug_code}
    GET /api/forecasting/xgboost/{drug_code}
    
    Generate demand forecast for a drug. Defaults to XGBoost algorithm.
    
    Query params:
    - forecast_days: int (default: 30)
    - test_size: int (default: 30)
    - lookback_days: int (optional)
    - start_date: YYYY-MM-DD (optional)
    - end_date: YYYY-MM-DD (optional)
    - department: int (optional)
    """
    # Parse parameters
    try:
        params = ForecastParams.from_request(request, default_forecast_days=30, default_test_size=30)
    except ValidationError as e:
        return format_success_response({'error': str(e)}, 400)
    
    # Get algorithm from route or default to xgboost
    algorithm = request.view_args.get('algorithm', 'xgboost') if request.view_args else 'xgboost'
    
    try:
        # Get algorithm instance
        forecaster = ForecastAlgorithmFactory.get_algorithm(algorithm)
        
        # Generate forecast
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
        logger.error(f"Forecast error for {drug_code}: {str(e)}")
        return format_success_response({'error': str(e)}, 400)
    except Exception as e:
        logger.error(f"Unexpected error in forecast for {drug_code}: {str(e)}", exc_info=True)
        return format_success_response(
            {'error': 'Internal server error during forecast'},
            500
        )


@forecasting_bp.route('/lstm/<drug_code>', methods=['GET'])
@handle_exceptions
def get_lstm_forecast(drug_code: str):
    """GET /api/forecasting/lstm/{drug_code} - LSTM forecast."""
    return get_forecast(drug_code, algorithm='lstm')


@forecasting_bp.route('/arima/<drug_code>', methods=['GET'])
@handle_exceptions
def get_arima_forecast(drug_code: str):
    """GET /api/forecasting/arima/{drug_code} - ARIMA forecast."""
    return get_forecast(drug_code, algorithm='arima')


@forecasting_bp.route('/algorithms', methods=['GET'])
@handle_exceptions
def list_algorithms():
    """GET /api/forecasting/algorithms - List available algorithms."""
    algorithms = ForecastAlgorithmFactory.list_algorithms()
    return format_success_response({
        'algorithms': algorithms,
        'default': 'xgboost'
    })
```

---

## 🔄 Alternative: Query Parameter Approach

### **Simpler but less RESTful:**

```python
# Query parameter approach
GET /api/forecasting/{drug_code}?algorithm=xgboost  # Default
GET /api/forecasting/{drug_code}?algorithm=lstm
GET /api/forecasting/{drug_code}?algorithm=arima
```

**Pros:**
- ✅ Simpler implementation
- ✅ Backward compatible (defaults to xgboost)
- ✅ Single route handler

**Cons:**
- ❌ Less RESTful (algorithm not in URL)
- ❌ Less discoverable
- ❌ Harder to document different algorithms

---

## 📊 Comparison

| Aspect | Sub-Routes | Query Parameter |
|--------|-----------|----------------|
| **RESTful** | ✅ Excellent | ⚠️ Good |
| **Discoverability** | ✅ High | ⚠️ Medium |
| **Documentation** | ✅ Easy | ⚠️ Harder |
| **Implementation** | ⚠️ More code | ✅ Simpler |
| **Scalability** | ✅ Excellent | ✅ Good |
| **Backward Compatible** | ✅ Yes | ✅ Yes |

---

## 🎯 Recommendation

**Use Sub-Routes Approach** for:
- Better REST API design
- Clearer separation of algorithms
- Easier documentation
- More professional API

**Use Query Parameter** if:
- You want minimal code changes
- Algorithms are very similar
- You prefer simplicity

---

## 📋 Migration Path

### **Phase 1: Refactor Current Code (No Breaking Changes)**
1. Create `BaseForecaster` interface
2. Wrap current `ForecastService` in `XGBoostForecaster`
3. Create factory
4. Update routes to use factory (defaults to xgboost)
5. Test - should work exactly as before

### **Phase 2: Add New Algorithm**
1. Implement `LSTMForecaster(BaseForecaster)`
2. Register in factory
3. Add route `/api/forecasting/lstm/{drug_code}`
4. Test new algorithm

### **Phase 3: Documentation**
1. Update API docs with all algorithms
2. Add algorithm comparison guide
3. Update frontend integration docs

---

## ✅ Benefits of This Design

1. **Scalable**: Easy to add new algorithms
2. **Maintainable**: Clear separation of concerns
3. **Testable**: Each algorithm can be tested independently
4. **Flexible**: Can switch algorithms without changing API
5. **Professional**: Follows design patterns and best practices

---

## 🚀 Example Usage

```bash
# Default (XGBoost)
curl "http://localhost:5000/api/forecasting/P182054?forecast_days=30"

# Explicit XGBoost
curl "http://localhost:5000/api/forecasting/xgboost/P182054?forecast_days=30"

# LSTM (when implemented)
curl "http://localhost:5000/api/forecasting/lstm/P182054?forecast_days=30"

# ARIMA (when implemented)
curl "http://localhost:5000/api/forecasting/arima/P182054?forecast_days=30"

# List available algorithms
curl "http://localhost:5000/api/forecasting/algorithms"
```

---

**Status**: Design ready for implementation

