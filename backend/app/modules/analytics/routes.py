"""Analytics routes - Combined API endpoints from dashboard and viz modules."""

import uuid
from flask import Blueprint, request, g, jsonify

from backend.app.modules.analytics.requests import (
    # Cost analysis requests (from viz)
    CostAnalysisRequest,
    HospitalStayRequest,
    # Dashboard analytics requests
    TopDrugsRequest,
    DrugDemandRequest,
    SummaryStatsRequest,
    ChartDataRequest,
    YearComparisonRequest,
    CategoryAnalysisRequest,
    PatientDemographicsRequest
)
from backend.app.modules.analytics.services import DashboardService
from backend.app.modules.analytics.cost_services import CostAnalysisService
from backend.app.modules.analytics.exceptions import NoDataFoundException
from backend.app.shared.middleware import handle_exceptions, format_success_response, validate_request

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


# ============================================================================
# Cost Analysis Routes (from viz module)
# ============================================================================

@analytics_bp.route('/cost-analysis', methods=['GET'])
@handle_exceptions
@validate_request(CostAnalysisRequest)
def get_cost_analysis():
    """
    GET /api/analytics/cost-analysis
    
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
    GET /api/analytics/cost-analysis?start_date=2019-01-01&end_date=2019-12-31&departments=1,2,3&price_min=10.0&price_max=1000.0
    """
    filters = g.validated_data
    service = CostAnalysisService()
    result = service.get_cost_analysis(filters)
    return format_success_response(result)


@analytics_bp.route('/hospital-stay-duration', methods=['GET'])
@handle_exceptions
@validate_request(HospitalStayRequest)
def get_hospital_stay_duration():
    """
    GET /api/analytics/hospital-stay-duration
    
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
    GET /api/analytics/hospital-stay-duration?start_date=2019-01-01&end_date=2019-12-31&departments=1,2,3&min_stay_days=1&max_stay_days=30
    """
    filters = g.validated_data
    service = CostAnalysisService()
    result = service.get_hospital_stay_analysis(filters)
    return format_success_response(result)


# ============================================================================
# Dashboard Analytics Routes (from dashboard module)
# ============================================================================

@analytics_bp.route('/top-drugs', methods=['GET'])
@handle_exceptions
@validate_request(TopDrugsRequest)
def get_top_drugs():
    """
    GET /api/analytics/top-drugs
    
    Get top dispensed drugs by quantity.
    
    Query params:
    - start_date: YYYY-MM-DD (required)
    - end_date: YYYY-MM-DD (required)
    - limit: int (default: 10, max: 100)
    - category_id: int (optional)
    - department_id: int (optional)
    
    Returns: Top dispensed drugs with quantities and values
    """
    filters = g.validated_data
    analytics_service = DashboardService()
    result = analytics_service.get_top_drugs(filters)
    return format_success_response(result)


@analytics_bp.route('/drug-demand', methods=['GET'])
@handle_exceptions
@validate_request(DrugDemandRequest)
def get_drug_demand():
    """
    GET /api/analytics/drug-demand
    
    Get drug demand trends over time.
    
    Query params:
    - start_date: YYYY-MM-DD (required)
    - end_date: YYYY-MM-DD (required)
    - drug_code: str (optional, specific drug)
    - granularity: 'daily'|'weekly'|'monthly' (default: 'daily')
    
    Returns: Time-series demand data
    """
    filters = g.validated_data
    analytics_service = DashboardService()
    result = analytics_service.get_drug_demand(filters)
    return format_success_response(result)


@analytics_bp.route('/summary-stats', methods=['GET'])
@handle_exceptions
def get_summary_stats():
    """
    GET /api/analytics/summary-stats
    
    Get overall statistics for dashboard cards.
    
    Query params:
    - start_date: YYYY-MM-DD (optional)
    - end_date: YYYY-MM-DD (optional)
    
    Returns: Summary statistics (total dispensed, value, transactions, etc.)
    """
    date_range = SummaryStatsRequest.from_query_params(request.args)
    analytics_service = DashboardService()
    result = analytics_service.get_summary_statistics(
        date_range.start_date,
        date_range.end_date
    )
    return format_success_response(result)


@analytics_bp.route('/chart-data/<chart_type>', methods=['GET'])
@handle_exceptions
def get_chart_data(chart_type: str):
    """
    GET /api/analytics/chart-data/{chart_type}
    
    Get pre-formatted chart data for frontend visualization.
    
    Chart types:
    - 'trends': Time-series trend chart
    - 'seasonal': Seasonal patterns heatmap
    - 'department': Department performance chart
    
    Query params:
    - start_date: YYYY-MM-DD (required)
    - end_date: YYYY-MM-DD (required)
    
    Returns: Chart data formatted for frontend charting library
    """
    request_data = ChartDataRequest.from_query_params(request.args, chart_type)
    analytics_service = DashboardService()
    result = analytics_service.get_chart_data(chart_type, request_data)
    return format_success_response(result)


@analytics_bp.route('/department-performance', methods=['GET'])
@handle_exceptions
def get_department_performance():
    """
    GET /api/analytics/department-performance
    
    Get department-level performance metrics.
    
    Query params:
    - start_date: YYYY-MM-DD (required)
    - end_date: YYYY-MM-DD (required)
    - limit: int (default: 10)
    
    Returns: Department performance comparison
    """
    # Use drug demand request for date validation
    date_filters = DrugDemandRequest.from_query_params(request.args)
    limit = int(request.args.get('limit', 10))
    analytics_service = DashboardService()
    with analytics_service.dal:
        result = analytics_service.dal.get_department_performance(
            start_date=date_filters.start_date,
            end_date=date_filters.end_date,
            limit=limit
        )
    
    if not result:
        raise NoDataFoundException("No department data found")
    
    return format_success_response({'departments': result})


@analytics_bp.route('/year-comparison', methods=['GET'])
@handle_exceptions
@validate_request(YearComparisonRequest)
def get_year_comparison():
    """
    GET /api/analytics/year-comparison
    
    Get year-over-year comparison metrics.
    
    Query params:
    - metric_type: 'quantity'|'value'|'transactions' (default: 'quantity')
    - drug_code: str (optional, specific drug)
    - start_year: int (optional, default: 2019)
    - end_year: int (optional, default: 2022)
    
    Returns: Year-over-year comparison data
    """
    filters = g.validated_data
    analytics_service = DashboardService()
    result = analytics_service.get_year_comparison(filters)
    
    # Restructure to avoid nested data.data
    # Put data points directly in data key, with metadata at root level
    return jsonify({
        'data': result.get('values', []),
        'drug_code': result.get('drug_code'),
        'metric_type': result.get('metric_type'),
        'years_compared': result.get('years_compared', []),
        'meta': {
            'request_id': getattr(g, 'request_id', str(uuid.uuid4())),
            'status': 'success'
        }
    }), 200


@analytics_bp.route('/category-analysis', methods=['GET'])
@handle_exceptions
@validate_request(CategoryAnalysisRequest)
def get_category_analysis():
    """
    GET /api/analytics/category-analysis
    
    Get drug category analysis over time.
    
    Query params:
    - start_date: YYYY-MM-DD (required)
    - end_date: YYYY-MM-DD (required)
    - granularity: 'monthly'|'quarterly' (default: 'monthly')
    - limit: int (optional, default: 10, max: 15) - Limit number of top categories to return
    
    Returns: Category analysis data
    """
    analytics_service = DashboardService()
    filters = g.validated_data
    result = analytics_service.get_category_analysis(filters)
    return format_success_response(result)


@analytics_bp.route('/patient-demographics', methods=['GET'])
@handle_exceptions
@validate_request(PatientDemographicsRequest)
def get_patient_demographics():
    """
    GET /api/analytics/patient-demographics
    
    Get patient demographics analysis.
    
    Query params:
    - start_date: YYYY-MM-DD (required)
    - end_date: YYYY-MM-DD (required)
    - group_by: 'age'|'room'|'bed' (default: 'age')
    
    Returns: Patient demographics data
    """
    analytics_service = DashboardService()
    filters = g.validated_data
    result = analytics_service.get_patient_demographics(filters)
    return format_success_response(result)

