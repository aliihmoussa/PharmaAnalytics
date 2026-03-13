"""API routes for Diagnostics module."""

from flask import Blueprint, request, jsonify
from backend.app.modules.diagnostics.services import FeatureService
from backend.app.shared.middleware import handle_exceptions
import logging

logger = logging.getLogger(__name__)

# Create blueprint
diagnostics_bp = Blueprint('diagnostics', __name__, url_prefix='/api/diagnostics')


@diagnostics_bp.route('/features/<drug_code>', methods=['GET'])
@handle_exceptions
def get_features(drug_code: str):
    """
    Get drug features and profiling data.
    
    Query parameters:
    - department: Optional department ID (cr)
    - start_date: Optional start date (YYYY-MM-DD)
    - end_date: Optional end date (YYYY-MM-DD)
    - use_cache: Whether to use cache (default: true)
    """
    try:
        # Parse query parameters
        department = request.args.get('department', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        use_cache = request.args.get('use_cache', 'true').lower() == 'true'
        
        from datetime import date
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = date.fromisoformat(start_date_str)
        if end_date_str:
            end_date = date.fromisoformat(end_date_str)
        
        # Get service
        service = FeatureService()
        result = service.get_features(
            drug_code=drug_code,
            department=department,
            start_date=start_date,
            end_date=end_date,
            use_cache=use_cache
        )
        
        return jsonify(result), result.get('meta', {}).get('status_code', 200)
        
    except ValueError as e:
        logger.warning(f"Invalid request parameters: {str(e)}")
        return jsonify({
            'success': False,
            'data': {'error': f'Invalid parameters: {str(e)}'}
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error in get_features: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'data': {'error': 'Internal server error'}
        }), 500
