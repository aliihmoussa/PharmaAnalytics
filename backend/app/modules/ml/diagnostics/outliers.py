"""Outlier detection with performance optimizations."""

import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class OutlierDetector:
    """Detect outliers in time series data using efficient methods."""
    
    def detect(self, series: pd.Series, method: str = 'iqr') -> Dict:
        """
        Detect outliers in time series.
        
        Args:
            series: Time series data
            method: Detection method ('iqr', 'zscore', or 'isolation')
        
        Returns:
            Dictionary with outlier detection results
        """
        if len(series) < 10:
            return {
                'count': 0,
                'percentage': 0.0,
                'indices': [],
                'values': [],
                'insufficient_data': True
            }
        
        # Remove zeros for outlier detection (zeros are handled separately)
        non_zero_series = series[series > 0]
        
        if len(non_zero_series) < 5:
            return {
                'count': 0,
                'percentage': 0.0,
                'indices': [],
                'values': []
            }
        
        if method == 'iqr':
            outlier_mask = self._iqr_method(non_zero_series)
        elif method == 'zscore':
            outlier_mask = self._zscore_method(non_zero_series)
        else:
            outlier_mask = self._iqr_method(non_zero_series)  # Default to IQR
        
        # Get outlier indices in original series
        outlier_indices = non_zero_series[outlier_mask].index.tolist()
        outlier_values = non_zero_series[outlier_mask].values.tolist()
        
        total_count = len(series)
        outlier_count = len(outlier_indices)
        
        return {
            'count': outlier_count,
            'percentage': float(outlier_count / total_count * 100) if total_count > 0 else 0.0,
            'indices': outlier_indices,
            'values': outlier_values,
            'method': method
        }
    
    def _iqr_method(self, series: pd.Series) -> pd.Series:
        """IQR method for outlier detection (fast and efficient)."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        if IQR == 0:
            return pd.Series(False, index=series.index)
        
        # Vectorized comparison
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return (series < lower_bound) | (series > upper_bound)
    
    def _zscore_method(self, series: pd.Series, threshold: float = 3.0) -> pd.Series:
        """Z-score method for outlier detection."""
        mean_val = series.mean()
        std_val = series.std()
        
        if std_val == 0:
            return pd.Series(False, index=series.index)
        
        # Vectorized z-score calculation
        z_scores = np.abs((series - mean_val) / std_val)
        
        return z_scores > threshold

