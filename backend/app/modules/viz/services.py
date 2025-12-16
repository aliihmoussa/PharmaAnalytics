"""Cost Analysis Service - Business logic for cost visualization."""

from typing import Dict
from backend.app.shared.base_service import BaseService
from backend.app.modules.viz.queries import CostAnalysisDAL
from backend.app.modules.viz.requests import CostAnalysisRequest
from backend.app.modules.dashboard.exceptions import NoDataFoundException


class CostAnalysisService(BaseService):
    """Service for cost analysis operations."""
    
    def __init__(self):
        """Initialize cost analysis service with dependencies."""
        super().__init__()
        self.dal = CostAnalysisDAL()
        self.logger.info("CostAnalysisService initialized")
    
    def get_cost_analysis(self, request: CostAnalysisRequest) -> Dict:
        """
        Get comprehensive cost analysis data for all chart types.
        
        Returns:
            Dictionary containing:
            - sunburst: Hierarchical data (Department → Category → Drug)
            - top_cost_drivers: Top 20 cost drivers
            - cost_trends: Daily/Monthly cost trends
            - bubble_chart: Unit price vs quantity vs frequency
        """
        with self.dal:
            # Get all chart data
            sunburst_data = self.dal.get_sunburst_data(
                start_date=request.start_date,
                end_date=request.end_date,
                departments=request.departments,
                price_min=request.price_min,
                price_max=request.price_max,
                drug_categories=request.drug_categories
            )
            
            top_drivers = self.dal.get_top_cost_drivers(
                start_date=request.start_date,
                end_date=request.end_date,
                departments=request.departments,
                price_min=request.price_min,
                price_max=request.price_max,
                drug_categories=request.drug_categories,
                limit=20
            )
            
            # Get both daily and monthly trends
            daily_trends = self.dal.get_cost_trends(
                start_date=request.start_date,
                end_date=request.end_date,
                granularity='daily',
                departments=request.departments,
                price_min=request.price_min,
                price_max=request.price_max,
                drug_categories=request.drug_categories
            )
            
            monthly_trends = self.dal.get_cost_trends(
                start_date=request.start_date,
                end_date=request.end_date,
                granularity='monthly',
                departments=request.departments,
                price_min=request.price_min,
                price_max=request.price_max,
                drug_categories=request.drug_categories
            )
            
            bubble_data = self.dal.get_bubble_chart_data(
                start_date=request.start_date,
                end_date=request.end_date,
                departments=request.departments,
                price_min=request.price_min,
                price_max=request.price_max,
                drug_categories=request.drug_categories
            )
        
        # Check if we have any data
        if not any([sunburst_data, top_drivers, daily_trends, monthly_trends, bubble_data]):
            raise NoDataFoundException("No cost data found for the specified filters")
        
        return {
            'sunburst': {
                'data': sunburst_data,
                'config': {
                    'type': 'sunburst',
                    'description': 'Hierarchical cost breakdown: Department → Category → Drug'
                }
            },
            'top_cost_drivers': {
                'data': top_drivers,
                'config': {
                    'type': 'horizontal_bar',
                    'description': 'Top 20 drugs by total cost',
                    'x_axis': 'total_cost',
                    'y_axis': 'drug_name'
                }
            },
            'cost_trends': {
                'daily': {
                    'data': daily_trends,
                    'config': {
                        'type': 'line',
                        'description': 'Daily cost trends',
                        'x_axis': 'date',
                        'y_axis': 'total_cost'
                    }
                },
                'monthly': {
                    'data': monthly_trends,
                    'config': {
                        'type': 'line',
                        'description': 'Monthly cost trends',
                        'x_axis': 'date',
                        'y_axis': 'total_cost'
                    }
                }
            },
            'bubble_chart': {
                'data': bubble_data,
                'config': {
                    'type': 'bubble',
                    'description': 'Unit Price vs Quantity vs Frequency',
                    'x_axis': 'unit_price',
                    'y_axis': 'quantity',
                    'size': 'frequency'
                }
            },
            'filters_applied': {
                'start_date': request.start_date.isoformat(),
                'end_date': request.end_date.isoformat(),
                'departments': request.departments,
                'price_min': request.price_min,
                'price_max': request.price_max,
                'drug_categories': request.drug_categories
            }
        }

