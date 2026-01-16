"""Routes for forecasting module."""

from flask import Blueprint, request
from backend.app.modules.forecasting.factory import ForecastAlgorithmFactory
from backend.app.modules.forecasting.parsers import (
    ForecastParams,
    ValidationError
)
from backend.app.shared.middleware import handle_exceptions, format_success_response
import logging

logger = logging.getLogger(__name__)

forecasting_bp = Blueprint('forecasting', __name__, url_prefix='/api/forecasting')


@forecasting_bp.route('/<drug_code>', methods=['GET'])
@handle_exceptions
def get_forecast(drug_code: str):
    """
    GET /api/forecasting/{drug_code}
    
    Generate demand forecast for a drug using the specified algorithm (defaults to XGBoost).
    Supports domain-specific features (departments, categories, rooms).
    Returns frontend-ready format with historical and forecast data.
    
    Query params:
    - algorithm: str (optional, default: 'xgboost') - Algorithm to use for forecasting
    - forecast_days: int (default: 30) - Days to forecast ahead
    - test_size: int (default: 30) - Days to use for testing
    - lookback_days: int (optional) - Limit historical data
    - start_date: YYYY-MM-DD (optional) - Start date for historical data
    - end_date: YYYY-MM-DD (optional) - End date for historical data
    - department: int (optional) - Filter by consuming department (C.R)
    
    Returns:
        Frontend-ready forecast data with:
        - algorithm: str - Algorithm used for forecasting
        - historical: Array of {date, demand, type: 'actual'}
        - forecast: Array of {date, predicted, lower, upper, type: 'predicted'}
        - test_predictions: Array of {date, actual, predicted, error, type: 'test'}
        - metrics: {rmse, mae, mape, r2}
        - feature_importance: Object with feature importance scores
    """
    # Parse and validate query parameters
    try:
        params = ForecastParams.from_request(request, default_forecast_days=30, default_test_size=30)
    except ValidationError as e:
        return format_success_response({'error': str(e)}, 400)
    
    try:
        # Get algorithm instance from factory
        forecaster = ForecastAlgorithmFactory.get_algorithm(params.algorithm)
        
        # Generate forecast
        result = forecaster.forecast(
            drug_code=drug_code,
            forecast_days=params.forecast_days,
            test_size=params.test_size,
            lookback_days=params.lookback_days,
            start_date=params.start_date,
            end_date=params.end_date,
            department=params.department
        )
        return format_success_response(result)
    
    except ValueError as e:
        logger.error(f"Forecast error for {drug_code}: {str(e)}")
        return format_success_response(
            {'error': str(e)},
            400
        )
    except Exception as e:
        logger.error(f"Unexpected error in forecast for {drug_code}: {str(e)}", exc_info=True)
        return format_success_response(
            {'error': 'Internal server error during forecast'},
            500
        )


@forecasting_bp.route('/algorithms', methods=['GET'])
@handle_exceptions
def list_algorithms():
    """
    GET /api/forecasting/algorithms
    
    List all available forecasting algorithms.
    
    Returns:
        Dictionary with available algorithms and default algorithm
    """
    algorithms = ForecastAlgorithmFactory.list_algorithms()
    return format_success_response({
        'algorithms': algorithms,
        'default': ForecastAlgorithmFactory.DEFAULT_ALGORITHM
    })


@forecasting_bp.route('/health', methods=['GET'])
@handle_exceptions
def health_check():
    """Health check endpoint."""
    return format_success_response({
        'status': 'healthy',
        'module': 'forecasting',
        'endpoint': 'forecast',
        'available_algorithms': ForecastAlgorithmFactory.list_algorithms()
    })

