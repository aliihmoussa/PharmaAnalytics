"""Seasonality detection with performance optimizations."""

import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class SeasonalityDetector:
    """Detect seasonality patterns in time series data."""
    
    def detect(self, series: pd.Series) -> Dict:
        """
        Detect seasonality patterns (weekly, monthly).
        
        Uses autocorrelation for fast detection.
        
        Args:
            series: Time series data
        
        Returns:
            Dictionary with seasonality detection results
        """
        if len(series) < 14:  # Need at least 2 weeks
            return {
                'seasonality_detected': False,
                'seasonal_periods': [],
                'seasonality_strength': {},
                'insufficient_data': True
            }
        
        results = {
            'seasonality_detected': False,
            'seasonal_periods': [],
            'seasonality_strength': {}
        }
        
        # Remove zeros for better seasonality detection
        non_zero_series = series[series > 0]
        if len(non_zero_series) < 14:
            return results
        
        # Weekly seasonality (lag 7)
        weekly_strength = self._detect_seasonal_strength(series, period=7)
        results['seasonality_strength']['weekly'] = weekly_strength
        
        # Monthly seasonality (lag 30)
        monthly_strength = 0.0
        if len(series) >= 60:  # Need at least 2 months
            monthly_strength = self._detect_seasonal_strength(series, period=30)
            results['seasonality_strength']['monthly'] = monthly_strength
        
        # Determine if seasonality is significant
        threshold = 0.3  # Correlation threshold
        
        if weekly_strength >= threshold:
            results['seasonality_detected'] = True
            results['seasonal_periods'].append('weekly')
        
        if monthly_strength >= threshold:
            results['seasonality_detected'] = True
            if 'monthly' not in results['seasonal_periods']:
                results['seasonal_periods'].append('monthly')
        
        # Dominant seasonality
        if results['seasonality_detected']:
            if weekly_strength > monthly_strength:
                results['dominant_seasonality'] = 'weekly'
            else:
                results['dominant_seasonality'] = 'monthly'
        else:
            results['dominant_seasonality'] = None
        
        return results
    
    def _detect_seasonal_strength(self, series: pd.Series, period: int) -> float:
        """
        Detect seasonal strength using autocorrelation.
        
        Args:
            series: Time series
            period: Seasonal period (7 for weekly, 30 for monthly)
        
        Returns:
            Seasonal strength score (0-1)
        """
        if len(series) < period * 2:
            return 0.0
        
        # Calculate autocorrelation at seasonal lag
        # Use vectorized operations for performance
        mean_val = series.mean()
        if mean_val == 0:
            return 0.0
        
        # Center the series
        centered = series - mean_val
        
        # Calculate autocorrelation at lag
        n = len(centered)
        if n <= period:
            return 0.0
        
        # Vectorized autocorrelation calculation
        lagged = centered.shift(period)
        valid_mask = ~(centered.isna() | lagged.isna())
        
        if valid_mask.sum() < period:
            return 0.0
        
        numerator = (centered[valid_mask] * lagged[valid_mask]).sum()
        denominator = (centered[valid_mask] ** 2).sum()
        
        if denominator == 0:
            return 0.0
        
        autocorr = numerator / denominator
        
        # Return absolute value as strength (0-1 range)
        return min(abs(autocorr), 1.0)

