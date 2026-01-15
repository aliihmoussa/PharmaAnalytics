"""Cost Analysis Service - Business logic for cost visualization."""

from typing import Dict
from backend.app.shared.base_service import BaseService
from backend.app.modules.viz.queries import CostAnalysisDAL
from backend.app.modules.viz.requests import CostAnalysisRequest, HospitalStayRequest
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
                drug_categories=request.drug_categories,
                max_items=200  # Limit to 200 items for better performance and readability
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
                    'description': 'Unit Price vs Quantity vs Frequency (Top 200 drugs, outliers filtered)',
                    'x_axis': 'unit_price',
                    'y_axis': 'quantity',
                    'size': 'frequency',
                    'note': 'Shows top 200 drugs by frequency. Zero-priced items and extreme outliers filtered for better readability.'
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
    
    def get_hospital_stay_analysis(self, request: HospitalStayRequest) -> Dict:
        """
        Get comprehensive hospital stay duration analysis.
        
        Returns:
            Dictionary containing:
            - statistics: Summary statistics (avg, median, min, max, std dev)
            - distribution: Histogram data for stay duration distribution
            - by_department: Average stay duration by department
            - trends: Stay duration trends over time (monthly)
            - patient_stays: Individual patient stay records (limited to top 100)
        """
        with self.dal:
            # Get all stay data
            statistics = self.dal.get_stay_duration_statistics(
                start_date=request.start_date,
                end_date=request.end_date,
                departments=request.departments,
                min_stay_days=request.min_stay_days,
                max_stay_days=request.max_stay_days
            )
            
            distribution = self.dal.get_stay_duration_distribution(
                start_date=request.start_date,
                end_date=request.end_date,
                departments=request.departments,
                min_stay_days=request.min_stay_days,
                max_stay_days=request.max_stay_days
            )
            
            by_department = self.dal.get_stay_duration_by_department(
                start_date=request.start_date,
                end_date=request.end_date,
                departments=request.departments,
                min_stay_days=request.min_stay_days,
                max_stay_days=request.max_stay_days
            )
            
            monthly_trends = self.dal.get_stay_duration_trends(
                start_date=request.start_date,
                end_date=request.end_date,
                departments=request.departments,
                min_stay_days=request.min_stay_days,
                max_stay_days=request.max_stay_days,
                granularity='monthly'
            )
            
            # Get individual patient stays (limited for performance)
            all_stays = self.dal.get_hospital_stay_duration(
                start_date=request.start_date,
                end_date=request.end_date,
                departments=request.departments,
                min_stay_days=request.min_stay_days,
                max_stay_days=request.max_stay_days
            )
            # Sort by stay duration descending and limit to top 100
            patient_stays = sorted(all_stays, key=lambda x: x['stay_days'], reverse=True)[:100]
        
        # Check if we have any data
        if statistics['total_patients'] == 0:
            raise NoDataFoundException("No hospital stay data found for the specified filters")
        
        return {
            'statistics': {
                'data': statistics,
                'config': {
                    'type': 'summary',
                    'description': 'Hospital stay duration statistics'
                }
            },
            'distribution': {
                'data': distribution,
                'config': {
                    'type': 'histogram',
                    'description': 'Distribution of hospital stay durations',
                    'x_axis': 'stay_duration_range',
                    'y_axis': 'patient_count'
                }
            },
            'by_department': {
                'data': by_department,
                'config': {
                    'type': 'bar',
                    'description': 'Average stay duration by department',
                    'x_axis': 'department_id',
                    'y_axis': 'average_stay_days'
                }
            },
            'trends': {
                'monthly': {
                    'data': monthly_trends,
                    'config': {
                        'type': 'line',
                        'description': 'Monthly trends in hospital stay duration',
                        'x_axis': 'period',
                        'y_axis': 'average_stay_days'
                    }
                }
            },
            'patient_stays': {
                'data': patient_stays,
                'config': {
                    'type': 'table',
                    'description': 'Top 100 patient stays by duration',
                    'total_count': len(all_stays),
                    'displayed_count': len(patient_stays)
                }
            },
            'filters_applied': {
                'start_date': request.start_date.isoformat(),
                'end_date': request.end_date.isoformat(),
                'departments': request.departments,
                'min_stay_days': request.min_stay_days,
                'max_stay_days': request.max_stay_days
            }
        }

