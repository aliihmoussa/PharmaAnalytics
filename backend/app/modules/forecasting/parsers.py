"""Query parameter parsers and validators for forecasting endpoints."""

from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime
from flask import Request


class ValidationError(Exception):
    """Raised when query parameter validation fails."""
    pass


@dataclass
class ForecastParams:
    """Parsed and validated parameters for forecast endpoint."""
    forecast_days: int
    test_size: int
    algorithm: str = 'xgboost'
    lookback_days: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    department: Optional[int] = None
    
    @classmethod
    def from_request(cls, request: Request, default_forecast_days: int = 30, default_test_size: int = 30) -> 'ForecastParams':
        """
        Parse and validate forecast parameters from Flask request.
        
        Args:
            request: Flask request object
            default_forecast_days: Default value for forecast_days
            default_test_size: Default value for test_size
            
        Returns:
            EnhancedForecastParams instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Parse forecast_days - match original: int(request.args.get('forecast_days', 30))
        # Handle empty strings: if key exists but is empty, use default
        forecast_days_val = request.args.get('forecast_days', default_forecast_days)
        if forecast_days_val == '':
            forecast_days_val = default_forecast_days
        try:
            forecast_days = int(forecast_days_val)
        except (ValueError, TypeError):
            raise ValidationError('forecast_days must be an integer')
        
        # Parse test_size - match original: int(request.args.get('test_size', 30))
        # Handle empty strings: if key exists but is empty, use default
        test_size_val = request.args.get('test_size', default_test_size)
        if test_size_val == '':
            test_size_val = default_test_size
        try:
            test_size = int(test_size_val)
        except (ValueError, TypeError):
            raise ValidationError('test_size must be an integer')
        
        # Parse lookback_days - match original: int(lookback_days) if lookback_days else None
        lookback_days = None
        lookback_days_str = request.args.get('lookback_days')
        if lookback_days_str:
            try:
                lookback_days = int(lookback_days_str)
            except ValueError:
                raise ValidationError('lookback_days must be an integer')
        
        # Parse department - match original exactly: int(department) if department else None
        # Original: department = int(department) if department else None
        # This will raise ValueError if department is invalid (non-integer string), matching original behavior
        department_str = request.args.get('department')
        department = int(department_str) if department_str else None
        
        # Parse start_date
        start_date = None
        start_date_str = request.args.get('start_date')
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError('Invalid start_date format. Use YYYY-MM-DD')
        
        # Parse end_date
        end_date = None
        end_date_str = request.args.get('end_date')
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError('Invalid end_date format. Use YYYY-MM-DD')
        
        # Validate forecast_days
        if forecast_days < 1 or forecast_days > 365:
            raise ValidationError('forecast_days must be between 1 and 365')
        
        # Validate test_size
        if test_size < 7:
            raise ValidationError('test_size must be at least 7')
        
        # Parse algorithm (optional, defaults to xgboost)
        algorithm = request.args.get('algorithm', 'xgboost').lower().strip()
        
        # Validate algorithm (import here to avoid circular dependency)
        try:
            from backend.app.modules.forecasting.factory import ForecastAlgorithmFactory
            if not ForecastAlgorithmFactory.is_algorithm_supported(algorithm):
                available = ', '.join(ForecastAlgorithmFactory.list_algorithms())
                raise ValidationError(
                    f"Unsupported algorithm '{algorithm}'. "
                    f"Available algorithms: {available}"
                )
        except ImportError:
            # If factory not available, just use the algorithm as-is
            # This allows the parser to work independently
            pass
        
        return cls(
            forecast_days=forecast_days,
            test_size=test_size,
            algorithm=algorithm,
            lookback_days=lookback_days,
            start_date=start_date,
            end_date=end_date,
            department=department
        )

