"""Drug classification based on demand patterns."""

import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class DrugClassifier:
    """Classify drugs into categories based on demand patterns."""
    
    def classify(
        self,
        series: pd.Series,
        seasonality_results: Dict,
        volatility: float,
        zero_frequency: float
    ) -> Dict:
        """
        Classify drug into category.
        
        Categories:
        - fast_moving: High frequency, low intermittency
        - seasonal: Strong weekly/monthly patterns
        - intermittent: Sparse demand, many zeros
        - erratic: High volatility, unpredictable
        - slow_moving: Low frequency, stable
        
        Args:
            series: Time series data
            seasonality_results: Results from seasonality detection
            volatility: Coefficient of variation
            zero_frequency: Frequency of zero demand days
        
        Returns:
            Dictionary with classification results
        """
        # Calculate additional metrics
        mean_demand = series.mean()
        std_demand = series.std()
        non_zero_count = (series > 0).sum()
        total_days = len(series)
        demand_frequency = non_zero_count / total_days if total_days > 0 else 0.0
        
        # Check for seasonality
        has_seasonality = seasonality_results.get('seasonality_detected', False)
        seasonal_strength = max(
            seasonality_results.get('seasonality_strength', {}).values(),
            default=0.0
        )
        
        # Classification logic
        category = None
        confidence = 0.0
        characteristics = {
            'fast_moving': False,
            'seasonal': False,
            'intermittent': False,
            'erratic': False,
            'slow_moving': False
        }
        
        # Intermittent: High zero frequency
        if zero_frequency > 0.5:
            category = 'intermittent'
            confidence = min(zero_frequency, 0.95)
            characteristics['intermittent'] = True
        
        # Seasonal: Strong seasonality patterns
        elif has_seasonality and seasonal_strength > 0.4:
            category = 'seasonal'
            confidence = min(seasonal_strength, 0.95)
            characteristics['seasonal'] = True
        
        # Erratic: High volatility
        elif volatility > 0.6:
            category = 'erratic'
            confidence = min(volatility, 0.95)
            characteristics['erratic'] = True
        
        # Fast-moving: High frequency, low intermittency, low volatility
        elif demand_frequency > 0.8 and zero_frequency < 0.2 and volatility < 0.4:
            category = 'fast_moving'
            confidence = min(demand_frequency * (1 - volatility), 0.95)
            characteristics['fast_moving'] = True
        
        # Slow-moving: Low frequency, stable
        elif demand_frequency < 0.3 and volatility < 0.3:
            category = 'slow_moving'
            confidence = min((1 - demand_frequency) * (1 - volatility), 0.95)
            characteristics['slow_moving'] = True
        
        # Default: Unclassified or mixed
        else:
            category = 'mixed'
            confidence = 0.5
            # Mark multiple characteristics
            if demand_frequency > 0.6:
                characteristics['fast_moving'] = True
            if has_seasonality:
                characteristics['seasonal'] = True
            if volatility > 0.4:
                characteristics['erratic'] = True
        
        return {
            'category': category,
            'confidence': float(confidence),
            'characteristics': characteristics,
            'metrics': {
                'demand_frequency': float(demand_frequency),
                'zero_frequency': float(zero_frequency),
                'volatility': float(volatility),
                'mean_demand': float(mean_demand),
                'seasonal_strength': float(seasonal_strength)
            }
        }

