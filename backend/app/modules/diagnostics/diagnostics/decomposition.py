"""Time series decomposition with performance optimizations."""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TimeSeriesDecomposer:
    """Decompose time series into trend, seasonal, and residual components."""
    
    def decompose(
        self,
        series: pd.Series,
        model: str = 'additive',
        period: Optional[int] = None
    ) -> Dict:
        """
        Decompose time series.
        
        Args:
            series: Time series data
            model: 'additive' or 'multiplicative'
            period: Seasonal period (auto-detect if None)
        
        Returns:
            Dictionary with decomposition results
        """
        if len(series) < 30:
            return {'insufficient_data': True}
        
        # Auto-detect period (prefer weekly if available)
        if period is None:
            if len(series) >= 14:
                period = 7  # Weekly
            else:
                period = min(7, len(series) // 2)
        
        try:
            # Simple moving average decomposition (fast)
            trend = self._extract_trend(series, period)
            
            # Detrend
            if model == 'additive':
                detrended = series - trend
            else:
                detrended = series / (trend + 1e-8)  # Avoid division by zero
            
            # Extract seasonal component
            seasonal = self._extract_seasonal(detrended, period)
            
            # Residual
            if model == 'additive':
                residual = detrended - seasonal
            else:
                residual = detrended / (seasonal + 1e-8)
            
            # Calculate seasonal strength
            seasonal_strength = self._calculate_seasonal_strength(
                series, seasonal, model
            )
            
            return {
                'model': model,
                'period': period,
                'trend': {
                    'direction': self._get_trend_direction(trend),
                    'strength': float(abs(trend.iloc[-1] - trend.iloc[0]) / series.mean()) if series.mean() > 0 else 0.0
                },
                'seasonal_strength': float(seasonal_strength),
                'residual_variance': float(residual.var()),
                'decomposition_quality': 'good' if seasonal_strength > 0.3 else 'weak'
            }
            
        except Exception as e:
            logger.warning(f"Decomposition failed: {str(e)}")
            return {'error': str(e)}
    
    def _extract_trend(self, series: pd.Series, period: int) -> pd.Series:
        """Extract trend using moving average."""
        # Use centered moving average for better trend extraction
        window = min(period, len(series) // 4)
        if window < 3:
            window = 3
        
        # Vectorized rolling mean
        trend = series.rolling(window=window, center=True, min_periods=1).mean()
        
        # Fill edges
        if len(trend) > 0:
            trend.iloc[0] = series.iloc[0]
            trend.iloc[-1] = series.iloc[-1]
        
        return trend
    
    def _extract_seasonal(self, detrended: pd.Series, period: int) -> pd.Series:
        """Extract seasonal component."""
        if len(detrended) < period:
            return pd.Series(0.0, index=detrended.index)
        
        # Group by seasonal period and average
        seasonal_values = []
        for i in range(period):
            indices = [j for j in range(i, len(detrended), period)]
            if indices:
                seasonal_values.append(detrended.iloc[indices].mean())
            else:
                seasonal_values.append(0.0)
        
        # Repeat pattern
        seasonal = pd.Series(
            np.tile(seasonal_values, len(detrended) // period + 1)[:len(detrended)],
            index=detrended.index
        )
        
        # Center seasonal component (mean = 0 for additive)
        seasonal = seasonal - seasonal.mean()
        
        return seasonal
    
    def _calculate_seasonal_strength(
        self,
        original: pd.Series,
        seasonal: pd.Series,
        model: str
    ) -> float:
        """Calculate seasonal strength (0-1)."""
        if len(seasonal) == 0:
            return 0.0
        
        seasonal_var = seasonal.var()
        total_var = original.var()
        
        if total_var == 0:
            return 0.0
        
        strength = seasonal_var / total_var
        return min(max(strength, 0.0), 1.0)
    
    def _get_trend_direction(self, trend: pd.Series) -> str:
        """Determine trend direction."""
        if len(trend) < 2:
            return 'stable'
        
        first_half = trend.iloc[:len(trend)//2].mean()
        second_half = trend.iloc[len(trend)//2:].mean()
        
        diff = second_half - first_half
        threshold = trend.mean() * 0.05  # 5% threshold
        
        if diff > threshold:
            return 'increasing'
        elif diff < -threshold:
            return 'decreasing'
        else:
            return 'stable'

