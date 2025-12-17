"""Visualization routes - Cost analysis API endpoints."""

from flask import Blueprint, request, g
from backend.app.modules.viz.requests import CostAnalysisRequest, HospitalStayRequest
from backend.app.modules.viz.services import CostAnalysisService
from backend.app.shared.middleware import handle_exceptions, format_success_response, validate_request

viz_bp = Blueprint('viz', __name__, url_prefix='/api/viz')


@viz_bp.route('/cost-analysis', methods=['GET'])
@handle_exceptions
@validate_request(CostAnalysisRequest)
def get_cost_analysis():
    """
    GET /api/viz/cost-analysis
    
    Get comprehensive cost analysis data for visualization.
    
    Query params:
    - start_date: YYYY-MM-DD (required) - Start date for analysis
    - end_date: YYYY-MM-DD (required) - End date for analysis
    - departments: int[] (optional) - Filter by department IDs (comma-separated or multiple params)
    - price_min: float (optional) - Minimum unit price filter
    - price_max: float (optional) - Maximum unit price filter
    - drug_categories: int[] (optional) - Filter by drug category IDs (comma-separated or multiple params)
    
    Returns:
    - sunburst: Hierarchical data (Department → Category → Drug)
    - top_cost_drivers: Top 20 cost drivers (horizontal bar chart data)
    - cost_trends: Daily and monthly cost trends (line chart data)
    - bubble_chart: Unit price vs quantity vs frequency (bubble chart data)
    
    Example:
    GET /api/viz/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&departments=1,2,3&price_min=10.0&price_max=1000.0
    """
    filters = g.validated_data
    service = CostAnalysisService()
    result = service.get_cost_analysis(filters)
    return format_success_response(result)


@viz_bp.route('/hospital-stay-duration', methods=['GET'])
@handle_exceptions
@validate_request(HospitalStayRequest)
def get_hospital_stay_duration():
    """
    GET /api/viz/hospital-stay-duration
    
    Get comprehensive hospital stay duration analysis for visualization.
    
    Query params:
    - start_date: YYYY-MM-DD (required) - Start date for analysis
    - end_date: YYYY-MM-DD (required) - End date for analysis
    - departments: int[] (optional) - Filter by department IDs (comma-separated or multiple params)
    - min_stay_days: int (optional) - Minimum stay duration in days
    - max_stay_days: int (optional) - Maximum stay duration in days
    
    Returns:
    - statistics: Summary statistics (average, median, min, max, std dev)
    - distribution: Histogram data for stay duration distribution
    - by_department: Average stay duration grouped by department
    - trends: Monthly trends in stay duration
    - patient_stays: Top 100 individual patient stay records
    
    Example:
    GET /api/viz/hospital-stay-duration?start_date=2019-01-01&end_date=2019-12-31&departments=1,2,3&min_stay_days=1&max_stay_days=30
    """
    filters = g.validated_data
    service = CostAnalysisService()
    result = service.get_hospital_stay_analysis(filters)
    return format_success_response(result)

