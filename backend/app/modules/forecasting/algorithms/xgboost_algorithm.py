"""XGBoost forecasting algorithm implementation."""

from typing import Dict, Optional
from datetime import date
from backend.app.modules.forecasting.base_forecaster import BaseForecaster
from backend.app.modules.forecasting.forecast_service import ForecastService
import logging

logger = logging.getLogger(__name__)


class XGBoostForecaster(BaseForecaster):
    """XGBoost forecasting implementation."""
    
    def __init__(self):
        """Initialize XGBoost forecaster."""
        self._service = ForecastService()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def algorithm_name(self) -> str:
        """Return the name of the algorithm."""
        return 'xgboost'
    
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
        Generate forecast using XGBoost algorithm.
        
        Args:
            drug_code: Drug code to forecast
            forecast_days: Number of days to forecast ahead
            test_size: Number of days to use for testing
            lookback_days: Optional number of days to look back
            start_date: Optional start date
            end_date: Optional end date
            department: Optional consuming department ID
        
        Returns:
            Dictionary with forecast results including algorithm name
        """
        self.logger.info(f"Generating XGBoost forecast for {drug_code}")
        
        # Use the existing service to generate forecast
        result = self._service.forecast(
            drug_code=drug_code,
            forecast_days=forecast_days,
            test_size=test_size,
            lookback_days=lookback_days,
            start_date=start_date,
            end_date=end_date,
            department=department
        )
        
        # Add algorithm name to result
        result['algorithm'] = self.algorithm_name
        
        return result

