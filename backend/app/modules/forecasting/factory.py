"""Factory for creating forecast algorithm instances."""

from typing import Dict, Type
from backend.app.modules.forecasting.base_forecaster import BaseForecaster
from backend.app.modules.forecasting.algorithms.xgboost_algorithm import XGBoostForecaster

# Future implementations can be imported here:
# from backend.app.modules.forecasting.algorithms.lstm_forecaster import LSTMForecaster
# from backend.app.modules.forecasting.algorithms.arima_forecaster import ARIMAForecaster
# from backend.app.modules.forecasting.algorithms.prophet_forecaster import ProphetForecaster

import logging

logger = logging.getLogger(__name__)


class ForecastAlgorithmFactory:
    """Factory for creating forecast algorithm instances."""
    
    # Registry of available algorithms
    _algorithms: Dict[str, Type[BaseForecaster]] = {
        'xgboost': XGBoostForecaster,
        # Future algorithms can be added here:
        # 'lstm': LSTMForecaster,
        # 'arima': ARIMAForecaster,
        # 'prophet': ProphetForecaster,
    }
    
    # Default algorithm
    DEFAULT_ALGORITHM = 'xgboost'
    
    @classmethod
    def get_algorithm(cls, algorithm: str = None) -> BaseForecaster:
        """
        Get forecast algorithm instance.
        
        Args:
            algorithm: Algorithm name (defaults to DEFAULT_ALGORITHM)
            
        Returns:
            BaseForecaster instance
            
        Raises:
            ValueError: If algorithm is not supported
        """
        if algorithm is None:
            algorithm = cls.DEFAULT_ALGORITHM
        
        algorithm = algorithm.lower().strip()
        
        if algorithm not in cls._algorithms:
            available = ', '.join(sorted(cls._algorithms.keys()))
            raise ValueError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Available algorithms: {available}"
            )
        
        logger.info(f"Creating {algorithm} forecaster instance")
        return cls._algorithms[algorithm]()
    
    @classmethod
    def list_algorithms(cls) -> list:
        """
        List all available algorithms.
        
        Returns:
            List of available algorithm names
        """
        return sorted(list(cls._algorithms.keys()))
    
    @classmethod
    def is_algorithm_supported(cls, algorithm: str) -> bool:
        """
        Check if an algorithm is supported.
        
        Args:
            algorithm: Algorithm name to check
            
        Returns:
            True if algorithm is supported, False otherwise
        """
        return algorithm.lower().strip() in cls._algorithms

