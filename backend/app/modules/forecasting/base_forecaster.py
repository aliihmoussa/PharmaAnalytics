"""Base interface for all forecasting algorithms."""

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
        
        Args:
            drug_code: Drug code to forecast
            forecast_days: Number of days to forecast ahead
            test_size: Number of days to use for testing
            lookback_days: Optional number of days to look back
            start_date: Optional start date
            end_date: Optional end date
            department: Optional consuming department ID
        
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

