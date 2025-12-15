"""ML routes - Simple forecasting endpoints."""

from flask import Blueprint, request
from backend.app.modules.ml.services import MLService
from backend.app.shared.middleware import handle_exceptions, format_success_response
import logging

logger = logging.getLogger(__name__)

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')


@ml_bp.route('/forecast/<drug_code>', methods=['GET'])
@handle_exceptions
def get_forecast(drug_code: str):
    """
    GET /api/ml/forecast/{drug_code}
    
    Simple time-series forecast using moving average.
    
    Query params:
    - forecast_days: int (default: 30) - Days to forecast ahead
    - lookback_days: int (default: 90) - Days of historical data to use
    
    Returns: Forecast data with historical context
    """
    forecast_days = int(request.args.get('forecast_days', 30))
    lookback_days = int(request.args.get('lookback_days', 90))
    
    # Basic validation
    if forecast_days < 1 or forecast_days > 365:
        return format_success_response(
            {'error': 'forecast_days must be between 1 and 365'},
            400
        )
    
    if lookback_days < 7:
        return format_success_response(
            {'error': 'lookback_days must be at least 7'},
            400
        )
    
    service = MLService()
    
    try:
        result = service.simple_forecast(
            drug_code=drug_code,
            forecast_days=forecast_days,
            lookback_days=lookback_days
        )
        return format_success_response(result)
    
    except ValueError as e:
        logger.error(f"Forecast error for {drug_code}: {str(e)}")
        return format_success_response(
            {'error': str(e)},
            400
        )
    except Exception as e:
        logger.error(f"Unexpected error forecasting {drug_code}: {str(e)}", exc_info=True)
        return format_success_response(
            {'error': 'Internal server error during forecast'},
            500
        )


@ml_bp.route('/health', methods=['GET'])
@handle_exceptions
def health_check():
    """Health check endpoint."""
    return format_success_response({
        'status': 'healthy',
        'module': 'ml',
        'method': 'simple_moving_average'
    })
