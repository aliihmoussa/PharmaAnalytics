"""ACF/PACF analysis with performance optimizations."""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class AutocorrelationAnalyzer:
    """Analyze autocorrelation and partial autocorrelation."""
    
    def analyze(self, series: pd.Series, max_lags: int = 30) -> Dict:
        """
        Analyze ACF and PACF for ARIMA order selection.
        
        Args:
            series: Time series data
            max_lags: Maximum number of lags to analyze
        
        Returns:
            Dictionary with ACF/PACF results and ARIMA suggestions
        """
        if len(series) < max_lags + 10:
            max_lags = min(max_lags, len(series) - 10)
        
        if max_lags < 5:
            return {'insufficient_data': True}
        
        # Remove zeros for better analysis
        non_zero_series = series[series > 0]
        if len(non_zero_series) < max_lags + 10:
            non_zero_series = series
        
        try:
            # Calculate ACF (vectorized)
            acf_values = self._calculate_acf(non_zero_series, max_lags)
            
            # Calculate PACF (simplified)
            pacf_values = self._calculate_pacf(non_zero_series, max_lags)
            
            # Find significant lags
            significant_lags = self._find_significant_lags(acf_values, threshold=0.2)
            seasonal_lags = self._find_seasonal_lags(acf_values)
            
            # Suggest ARIMA orders
            arima_suggestions = self._suggest_arima_orders(acf_values, pacf_values)
            
            return {
                'significant_lags': significant_lags,
                'seasonal_lags': seasonal_lags,
                'arima_suggested_orders': arima_suggestions,
                'acf_summary': {
                    'max_acf_lag': int(np.argmax(np.abs(acf_values[1:])) + 1) if len(acf_values) > 1 else None,
                    'max_acf_value': float(np.max(np.abs(acf_values[1:]))) if len(acf_values) > 1 else None
                }
            }
            
        except Exception as e:
            logger.warning(f"ACF/PACF analysis failed: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_acf(self, series: pd.Series, max_lags: int) -> np.ndarray:
        """Calculate autocorrelation function (vectorized)."""
        n = len(series)
        mean_val = series.mean()
        
        if mean_val == 0 or n == 0:
            return np.zeros(max_lags + 1)
        
        # Center the series
        centered = series - mean_val
        
        # Calculate variance
        variance = (centered ** 2).sum()
        
        if variance == 0:
            return np.zeros(max_lags + 1)
        
        # Calculate ACF for each lag
        acf = np.zeros(max_lags + 1)
        acf[0] = 1.0  # Lag 0 is always 1
        
        for lag in range(1, min(max_lags + 1, n)):
            if lag >= n:
                break
            
            # Vectorized autocorrelation
            lagged = centered.shift(lag)
            valid_mask = ~(centered.isna() | lagged.isna())
            
            if valid_mask.sum() > 0:
                numerator = (centered[valid_mask] * lagged[valid_mask]).sum()
                acf[lag] = numerator / variance
        
        return acf
    
    def _calculate_pacf(self, series: pd.Series, max_lags: int) -> np.ndarray:
        """Calculate partial autocorrelation (simplified Durbin-Levinson)."""
        # For performance, use simplified PACF calculation
        # Full PACF would use Durbin-Levinson recursion (more complex)
        n = len(series)
        pacf = np.zeros(max_lags + 1)
        pacf[0] = 1.0
        
        if n < 2:
            return pacf
        
        # Simplified: use correlation of residuals
        # This is an approximation but much faster
        mean_val = series.mean()
        centered = series - mean_val
        
        for lag in range(1, min(max_lags + 1, n // 2)):
            if lag >= n - 1:
                break
            
            # Simple PACF approximation
            # Remove linear trend from lagged series
            x = centered.iloc[lag:].values
            y = centered.iloc[:-lag].values if len(centered) > lag else centered.values
            
            if len(x) == len(y) and len(x) > 0:
                # Calculate correlation
                x_centered = x - x.mean()
                y_centered = y - y.mean()
                
                numerator = (x_centered * y_centered).sum()
                denominator = np.sqrt((x_centered ** 2).sum() * (y_centered ** 2).sum())
                
                if denominator > 0:
                    pacf[lag] = numerator / denominator
        
        return pacf
    
    def _find_significant_lags(self, acf: np.ndarray, threshold: float = 0.2) -> List[int]:
        """Find lags with significant autocorrelation."""
        significant = []
        for lag in range(1, len(acf)):
            if abs(acf[lag]) >= threshold:
                significant.append(lag)
        return significant[:10]  # Return top 10
    
    def _find_seasonal_lags(self, acf: np.ndarray) -> List[int]:
        """Find seasonal lags (7, 14, 30, etc.)."""
        seasonal_periods = [7, 14, 21, 28, 30]
        seasonal_lags = []
        
        for period in seasonal_periods:
            if period < len(acf) and abs(acf[period]) > 0.15:
                seasonal_lags.append(period)
        
        return seasonal_lags
    
    def _suggest_arima_orders(self, acf: np.ndarray, pacf: np.ndarray) -> Dict:
        """Suggest ARIMA(p,d,q) orders based on ACF/PACF."""
        # Simplified ARIMA order selection
        # Look for cut-off points in ACF and PACF
        
        # Find where PACF cuts off (suggests AR order)
        ar_order = 0
        for lag in range(1, min(5, len(pacf))):
            if abs(pacf[lag]) > 0.2:
                ar_order = lag
            elif ar_order > 0:
                break
        
        # Find where ACF cuts off (suggests MA order)
        ma_order = 0
        for lag in range(1, min(5, len(acf))):
            if abs(acf[lag]) > 0.2:
                ma_order = lag
            elif ma_order > 0:
                break
        
        # Seasonal components
        seasonal_ar = 0
        seasonal_ma = 0
        seasonal_period = 7  # Default weekly
        
        # Check for seasonal patterns
        if len(acf) > 7 and abs(acf[7]) > 0.2:
            seasonal_ar = 1
            seasonal_period = 7
        elif len(acf) > 14 and abs(acf[14]) > 0.2:
            seasonal_ar = 1
            seasonal_period = 14
        
        return {
            'ar': ar_order,
            'ma': ma_order,
            'd': 0,  # Assume stationary (can be improved with ADF test)
            'seasonal_ar': seasonal_ar,
            'seasonal_ma': seasonal_ma,
            'seasonal_period': seasonal_period
        }

