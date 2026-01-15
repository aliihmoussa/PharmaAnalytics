"""Routes for XGBoost forecasting module."""

from flask import Blueprint, request
from backend.app.modules.ml_xgboost.service import XGBoostForecastService
from backend.app.modules.ml_xgboost.service_enhanced import EnhancedXGBoostForecastService
from backend.app.shared.middleware import handle_exceptions, format_success_response
from datetime import datetime, date, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

ml_xgboost_bp = Blueprint('ml_xgboost', __name__, url_prefix='/api/ml-xgboost')


@ml_xgboost_bp.route('/forecast/<drug_code>', methods=['GET'])
@handle_exceptions
def get_xgboost_forecast(drug_code: str):
    """
    GET /api/ml-xgboost/forecast/{drug_code}
    
    XGBoost time-series forecast matching Colab script implementation.
    
    Query params:
    - forecast_days: int (default: 14) - Days to forecast ahead
    - test_size: int (default: 30) - Days to use for testing
    - lookback_days: int (optional) - Limit historical data
    - start_date: YYYY-MM-DD (optional) - Start date for historical data
    - end_date: YYYY-MM-DD (optional) - End date for historical data
    
    Returns:
        Forecast data with historical context, test predictions, and future forecast
    """
    # Parse query parameters
    forecast_days = int(request.args.get('forecast_days', 14))
    test_size = int(request.args.get('test_size', 30))
    lookback_days = request.args.get('lookback_days')
    lookback_days = int(lookback_days) if lookback_days else None
    
    start_date = request.args.get('start_date')
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return format_success_response(
                {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                400
            )
    
    end_date = request.args.get('end_date')
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return format_success_response(
                {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                400
            )
    
    # Validation
    if forecast_days < 1 or forecast_days > 365:
        return format_success_response(
            {'error': 'forecast_days must be between 1 and 365'},
            400
        )
    
    if test_size < 7:
        return format_success_response(
            {'error': 'test_size must be at least 7'},
            400
        )
    
    service = XGBoostForecastService()
    
    try:
        result = service.forecast(
            drug_code=drug_code,
            forecast_days=forecast_days,
            test_size=test_size,
            lookback_days=lookback_days,
            start_date=start_date,
            end_date=end_date
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


@ml_xgboost_bp.route('/forecast-enhanced/<drug_code>', methods=['GET'])
@handle_exceptions
def get_enhanced_forecast(drug_code: str):
    """
    GET /api/ml-xgboost/forecast-enhanced/{drug_code}
    
    Enhanced XGBoost forecast with domain-specific features (departments, categories, rooms).
    Returns frontend-ready format with historical and forecast data.
    
    Query params:
    - forecast_days: int (default: 30) - Days to forecast ahead
    - test_size: int (default: 30) - Days to use for testing
    - lookback_days: int (optional) - Limit historical data
    - start_date: YYYY-MM-DD (optional) - Start date for historical data
    - end_date: YYYY-MM-DD (optional) - End date for historical data
    - department: int (optional) - Filter by consuming department (C.R)
    
    Returns:
        Frontend-ready forecast data with:
        - historical: Array of {date, demand, type: 'actual'}
        - forecast: Array of {date, predicted, lower, upper, type: 'predicted'}
        - test_predictions: Array of {date, actual, predicted, error, type: 'test'}
        - metrics: {rmse, mae, mape, r2}
        - feature_importance: Object with feature importance scores
    """
    # Parse query parameters
    forecast_days = int(request.args.get('forecast_days', 30))
    test_size = int(request.args.get('test_size', 30))
    lookback_days = request.args.get('lookback_days')
    lookback_days = int(lookback_days) if lookback_days else None
    
    # Parse department parameter
    department = request.args.get('department')
    department = int(department) if department else None
    
    start_date = request.args.get('start_date')
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return format_success_response(
                {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                400
            )
    
    end_date = request.args.get('end_date')
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return format_success_response(
                {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                400
            )
    
    # Validation
    if forecast_days < 1 or forecast_days > 365:
        return format_success_response(
            {'error': 'forecast_days must be between 1 and 365'},
            400
        )
    
    if test_size < 7:
        return format_success_response(
            {'error': 'test_size must be at least 7'},
            400
        )
    
    service = EnhancedXGBoostForecastService()
    
    try:
        result = service.forecast(
            drug_code=drug_code,
            forecast_days=forecast_days,
            test_size=test_size,
            lookback_days=lookback_days,
            start_date=start_date,
            end_date=end_date
        )
        return format_success_response(result)
    
    except ValueError as e:
        logger.error(f"Enhanced forecast error for {drug_code}: {str(e)}")
        return format_success_response(
            {'error': str(e)},
            400
        )
    except Exception as e:
        logger.error(f"Unexpected error in enhanced forecast for {drug_code}: {str(e)}", exc_info=True)
        return format_success_response(
            {'error': 'Internal server error during forecast'},
            500
        )


@ml_xgboost_bp.route('/data-check/<drug_code>', methods=['GET'])
@handle_exceptions
def check_data_availability(drug_code: str):
    """
    GET /api/ml-xgboost/data-check/<drug_code>
    
    Check data availability for a drug code.
    
    Query params:
    - lookback_days: int (optional, default: 730) - Days to look back
    - start_date: YYYY-MM-DD (optional)
    - end_date: YYYY-MM-DD (optional)
    
    Returns:
        Data availability information
    """
    from backend.app.modules.ml_xgboost.utils.data_preparation import load_and_prepare_data
    
    end_date = date.today()
    lookback_days = request.args.get('lookback_days')
    lookback_days = int(lookback_days) if lookback_days else 730
    
    start_date = request.args.get('start_date')
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return format_success_response(
                {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                400
            )
    else:
        start_date = end_date - timedelta(days=lookback_days)
    
    end_date_param = request.args.get('end_date')
    if end_date_param:
        try:
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
        except ValueError:
            return format_success_response(
                {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                400
            )
    
    try:
        df = load_and_prepare_data(
            drug_code=drug_code,
            start_date=start_date,
            end_date=end_date
        )
        
        return format_success_response({
            'drug_code': drug_code,
            'date_range': {
                'start': str(df.index.min().date()) if len(df) > 0 else None,
                'end': str(df.index.max().date()) if len(df) > 0 else None
            },
            'total_days': len(df),
            'total_quantity': float(df['QTY'].sum()) if len(df) > 0 else 0.0,
            'avg_daily_quantity': float(df['QTY'].mean()) if len(df) > 0 else 0.0,
            'min_required': 60,  # test_size (30) + feature lag (30)
            'sufficient': len(df) >= 60,
            'sample_dates': [
                {'date': str(idx.date()), 'quantity': float(val) if not pd.isna(val) else 0.0}
                for idx, val in df.head(10).iterrows()
            ] if len(df) > 0 else []
        })
    except Exception as e:
        logger.error(f"Data check error for {drug_code}: {str(e)}", exc_info=True)
        return format_success_response(
            {'error': str(e), 'drug_code': drug_code},
            400
        )


@ml_xgboost_bp.route('/health', methods=['GET'])
@handle_exceptions
def health_check():
    """Health check endpoint."""
    return format_success_response({
        'status': 'healthy',
        'module': 'ml_xgboost',
        'method': 'xgboost_colab'
    })

