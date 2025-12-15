"""Dashboard routes - API endpoints."""

from flask import Blueprint, request, g

from backend.app.modules.dashboard.requests import (
    TopDrugsRequest,
    DrugDemandRequest,
    SummaryStatsRequest,
    ChartDataRequest,
    YearComparisonRequest,
    CategoryAnalysisRequest,
    PatientDemographicsRequest
)
from backend.app.modules.dashboard.serializers import (
    TopDrugsResponse,
    DrugDemandResponse,
    SummaryStatsResponse,
    ChartDataResponse,
    YearComparisonResponse,
    CategoryAnalysisResponse,
    PatientDemographicsResponse
)
from backend.app.modules.dashboard.services import DashboardService
from backend.app.shared.middleware import handle_exceptions, format_success_response, validate_request

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


# Initialize service instance


@dashboard_bp.route('/top-drugs', methods=['GET'])
@handle_exceptions
@validate_request(TopDrugsRequest)
def get_top_drugs():
    """
    GET /api/dashboard/top-drugs
    
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


@dashboard_bp.route('/drug-demand', methods=['GET'])
@handle_exceptions
@validate_request(DrugDemandRequest)
def get_drug_demand():
    """
    GET /api/dashboard/drug-demand
    
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


@dashboard_bp.route('/summary-stats', methods=['GET'])
@handle_exceptions
def get_summary_stats():
    """
    GET /api/dashboard/summary-stats
    
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


@dashboard_bp.route('/chart-data/<chart_type>', methods=['GET'])
@handle_exceptions
def get_chart_data(chart_type: str):
    """
    GET /api/dashboard/chart-data/{chart_type}
    
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


@dashboard_bp.route('/department-performance', methods=['GET'])
@handle_exceptions
def get_department_performance():
    """
    GET /api/dashboard/department-performance
    
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
        from backend.app.modules.dashboard.exceptions import NoDataFoundException
        raise NoDataFoundException("No department data found")
    
    return format_success_response({'departments': result})


@dashboard_bp.route('/year-comparison', methods=['GET'])
@handle_exceptions
@validate_request(YearComparisonRequest)
def get_year_comparison():
    """
    GET /api/dashboard/year-comparison
    
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
    return format_success_response(result)


@dashboard_bp.route('/category-analysis', methods=['GET'])
@handle_exceptions
@validate_request(CategoryAnalysisRequest)
def get_category_analysis():
    """
    GET /api/dashboard/category-analysis
    
    Get drug category analysis over time.
    
    Query params:
    - start_date: YYYY-MM-DD (required)
    - end_date: YYYY-MM-DD (required)
    - granularity: 'monthly'|'quarterly' (default: 'monthly')
    
    Returns: Category analysis data
    """
    analytics_service = DashboardService()
    filters = g.validated_data
    result = analytics_service.get_category_analysis(filters)
    return format_success_response(result)


@dashboard_bp.route('/patient-demographics', methods=['GET'])
@handle_exceptions
@validate_request(PatientDemographicsRequest)
def get_patient_demographics():
    """
    GET /api/dashboard/patient-demographics
    
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
