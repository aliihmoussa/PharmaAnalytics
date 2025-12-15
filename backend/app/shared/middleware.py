"""Middleware for error handling and request processing."""

import uuid
import logging
from functools import wraps
from flask import jsonify, request, g
from backend.app.shared.exceptions import AppException

logger = logging.getLogger(__name__)


def handle_exceptions(f):
    """Decorator to handle exceptions and return JSON responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Generate request ID
            g.request_id = str(uuid.uuid4())
            
            response = f(*args, **kwargs)
            return response
        except AppException as e:
            logger.error(f"Application error [{g.request_id}]: {e.message}", exc_info=True)
            return jsonify({
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": {}
                },
                "meta": {
                    "request_id": g.request_id,
                    "status": "error"
                }
            }), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error [{g.request_id}]: {str(e)}", exc_info=True)
            return jsonify({
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {}
                },
                "meta": {
                    "request_id": g.request_id,
                    "status": "error"
                }
            }), 500
    return decorated_function


def format_success_response(data: dict, status_code: int = 200) -> tuple:
    """Format successful API response."""
    return jsonify({
        "data": data,
        "meta": {
            "request_id": getattr(g, 'request_id', str(uuid.uuid4())),
            "status": "success"
        }
    }), status_code


def validate_request(model_class):
    """Decorator to validate request using Pydantic models."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip validation for OPTIONS requests (handled by CORS)
            if request.method == 'OPTIONS':
                return f(*args, **kwargs)
            
            try:
                if request.method == 'GET':
                    validated_data = model_class.from_query_params(request.args)
                else:
                    validated_data = model_class(**request.json or {})
                
                # Store validated data in request context
                g.validated_data = validated_data
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Validation error: {str(e)}", exc_info=True)
                return jsonify({
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(e),
                        "details": {}
                    },
                    "meta": {
                        "request_id": getattr(g, 'request_id', str(uuid.uuid4())),
                        "status": "error"
                    }
                }), 400
        return decorated_function
    return decorator

