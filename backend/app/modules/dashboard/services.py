"""Dashboard analytics service - Class-based service."""

from typing import Dict, List, Optional
from datetime import date
from backend.app.shared.base_service import BaseService
from backend.app.modules.dashboard.queries import AnalyticsDAL
from backend.app.modules.dashboard.requests import (
    TopDrugsRequest,
    DrugDemandRequest,
    ChartDataRequest,
    GranularityEnum
)
from backend.app.modules.dashboard.serializers import (
    DrugInfo,
    TimeSeriesPoint
)
from backend.app.modules.dashboard.exceptions import NoDataFoundException, InvalidChartTypeException


class DashboardService(BaseService):
    """Class-based service for dashboard analytics operations."""
    
    def __init__(self):
        """Initialize dashboard service with dependencies."""
        super().__init__()
        self.dal = AnalyticsDAL()
        self.logger.info("DashboardService initialized")
    
    def get_top_drugs(self, filters: TopDrugsRequest) -> Dict:
        """Get top dispensed drugs with business logic."""
        with self.dal:
            raw_data = self.dal.get_top_drugs(
                start_date=filters.start_date,
                end_date=filters.end_date,
                limit=filters.limit,
                category_id=filters.category_id,
                department_id=filters.department_id
            )
        
        if not raw_data:
            raise NoDataFoundException("No data found for specified filters")
        
        # Transform to response format
        drugs = [
            DrugInfo(
                drug_code=row['drug_code'],
                drug_name=row['drug_name'],
                total_dispensed=abs(row['total_qty']),
                total_value=abs(row['total_value']),
                transaction_count=row['transaction_count']
            )
            for row in raw_data
        ]
        
        return {
            'drugs': [drug.model_dump() for drug in drugs],
            'period': {
                'start': filters.start_date.isoformat(),
                'end': filters.end_date.isoformat()
            },
            'total_unique_drugs': len(drugs)
        }
    
    def get_drug_demand(self, filters: DrugDemandRequest) -> Dict:
        """Get time-series demand data."""
        with self.dal:
            raw_data = self.dal.get_drug_demand_time_series(
                start_date=filters.start_date,
                end_date=filters.end_date,
                drug_code=filters.drug_code,
                granularity=filters.granularity.value
            )
        
        if not raw_data:
            raise NoDataFoundException("No data found for specified filters")
        
        data_points = [
            TimeSeriesPoint(
                date=row['date'],
                quantity=int(row['quantity']) if row['quantity'] else 0,
                value=float(row['value']) if row['value'] else 0.0,
                transaction_count=int(row['transaction_count']) if row['transaction_count'] else 0
            )
            for row in raw_data
        ]
        
        return {
            'data': [point.model_dump() for point in data_points],
            'drug_code': filters.drug_code,
            'granularity': filters.granularity.value
        }
    
    def get_summary_statistics(self, start_date: Optional[date], end_date: Optional[date]) -> Dict:
        """Get overall dashboard statistics."""
        with self.dal:
            stats = self.dal.get_summary_stats(start_date, end_date)
        
        # Calculate average daily dispensed if date range provided
        avg_daily_dispensed = None
        date_range_dict = None
        
        if start_date and end_date:
            days_diff = (end_date - start_date).days + 1
            if days_diff > 0:
                avg_daily_dispensed = stats.get('total_dispensed', 0) / days_diff
            date_range_dict = {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        
        return {
            'total_dispensed': int(stats.get('total_dispensed', 0)),
            'total_value': float(stats.get('total_value', 0.0)),
            'total_transactions': int(stats.get('total_transactions', 0)),
            'unique_drugs': int(stats.get('unique_drugs', 0)),
            'unique_departments': int(stats.get('unique_departments', 0)),
            'date_range': date_range_dict,
            'avg_daily_dispensed': round(avg_daily_dispensed, 2) if avg_daily_dispensed else None
        }
    
    def get_chart_data(self, chart_type: str, request_data: ChartDataRequest) -> Dict:
        """Get pre-formatted chart data for frontend."""
        chart_processors = {
            'trends': self._process_trends_chart,
            'seasonal': self._process_seasonal_chart,
            'department': self._process_department_chart
        }
        
        processor = chart_processors.get(chart_type)
        if not processor:
            raise InvalidChartTypeException(chart_type)
        
        return processor(request_data)
    
    def _process_trends_chart(self, request_data: ChartDataRequest) -> Dict:
        """Format data for time-series trend chart."""
        demand_filters = DrugDemandRequest(
            start_date=request_data.start_date,
            end_date=request_data.end_date,
            granularity=GranularityEnum.DAILY
        )
        result = self.get_drug_demand(demand_filters)
        
        return {
            'chart_type': 'trends',
            'data': result,
            'config': {
                'type': 'line',
                'x_axis': 'date',
                'y_axis': 'quantity'
            }
        }
    
    def _process_seasonal_chart(self, request_data: ChartDataRequest) -> Dict:
        """Format data for seasonal patterns heatmap."""
        with self.dal:
            raw_data = self.dal.get_seasonal_patterns(
                start_date=request_data.start_date,
                end_date=request_data.end_date
            )
        
        if not raw_data:
            raise NoDataFoundException("No seasonal data found")
        
        return {
            'chart_type': 'seasonal',
            'data': {
                'patterns': raw_data
            },
            'config': {
                'type': 'heatmap',
                'x_axis': 'month',
                'y_axis': 'year'
            }
        }
    
    def _process_department_chart(self, request_data: ChartDataRequest) -> Dict:
        """Format data for department performance chart."""
        with self.dal:
            raw_data = self.dal.get_department_performance(
                start_date=request_data.start_date,
                end_date=request_data.end_date
            )
        
        if not raw_data:
            raise NoDataFoundException("No department data found")
        
        return {
            'chart_type': 'department',
            'data': {
                'departments': raw_data
            },
            'config': {
                'type': 'bar',
                'x_axis': 'department_id',
                'y_axis': 'total_dispensed'
            }
        }

