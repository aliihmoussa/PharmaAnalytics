"""ML Service - Simple time-series forecasting (MVP)."""

from typing import Dict, List
from datetime import date, timedelta
from backend.app.shared.base_service import BaseService
from backend.app.modules.dashboard.queries import AnalyticsDAL
import logging

logger = logging.getLogger(__name__)


class MLService(BaseService):
    """Simple forecasting service - minimal implementation."""
    
    def __init__(self):
        """Initialize ML service."""
        super().__init__()
        self.dal = AnalyticsDAL()
        self.logger.info("MLService initialized")
    
    def simple_forecast(
        self,
        drug_code: str,
        forecast_days: int = 30,
        lookback_days: int = 90
    ) -> Dict:
        """
        Simple time-series forecast using moving average.
        
        This is a minimal implementation that demonstrates basic forecasting.
        Can be enhanced incrementally with ML models later.
        
        Args:
            drug_code: Drug code to forecast
            forecast_days: Number of days to forecast ahead
            lookback_days: Number of days of historical data to use
        
        Returns:
            Dictionary with forecast results
        """
        self.logger.info(f"Forecasting {drug_code} for {forecast_days} days")
        
        # Get historical data
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days)
        
        with self.dal:
            historical_data = self.dal.get_drug_demand_time_series(
                start_date=start_date,
                end_date=end_date,
                drug_code=drug_code,
                granularity='daily'
            )
        
        if not historical_data or len(historical_data) < 7:
            raise ValueError(
                f"Insufficient data for {drug_code}. Need at least 7 days, got {len(historical_data)}."
            )
        
        # Extract demand values
        demands = [abs(row.get('quantity', 0)) for row in historical_data]
        
        # Simple forecast: Use average of last 7 days
        recent_avg = sum(demands[-7:]) / min(7, len(demands))
        
        # Generate forecast dates
        last_date = historical_data[-1]['date']
        if isinstance(last_date, str):
            last_date = date.fromisoformat(last_date)
        
        forecast_dates = [
            (last_date + timedelta(days=i)).isoformat()
            for i in range(1, forecast_days + 1)
        ]
        
        # Simple forecast: constant value (can be enhanced with trend)
        forecast_values = [int(recent_avg)] * forecast_days
        
        # Format historical data
        historical = [
            {
                'date': row['date'].isoformat() if isinstance(row['date'], date) else str(row['date']),
                'demand': abs(row.get('quantity', 0))
            }
            for row in historical_data
        ]
        
        # Format forecast data
        forecast = [
            {
                'date': date_str,
                'demand': value
            }
            for date_str, value in zip(forecast_dates, forecast_values)
        ]
        
        return {
            'drug_code': drug_code,
            'historical': historical,
            'forecast': forecast,
            'method': 'moving_average',
            'lookback_days': lookback_days,
            'forecast_days': forecast_days
        }
