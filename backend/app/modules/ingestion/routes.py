"""Routes for ingestion module."""

import logging
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify

from backend.app.modules.ingestion.requests import IngestionStatusQuery
from backend.app.modules.ingestion.responses import (
    UploadResponse,
    IngestionStatusResponse,
    IngestionProgressResponse
)
from backend.app.modules.ingestion.services import IngestionService
from backend.app.shared.middleware import handle_exceptions, format_success_response

logger = logging.getLogger(__name__)

ingestion_bp = Blueprint('ingestion', __name__, url_prefix='/api/ingestion')


@ingestion_bp.route('/upload', methods=['POST'])
@handle_exceptions
def upload_file():
    """
    POST /api/ingestion/upload
    
    Upload a file for ingestion.
    
    Form data:
    - file: File to upload (multipart/form-data)
    - file_name: Original file name (optional, uses uploaded filename)
    - file_year: Year of the data (optional)
    
    Returns:
        Upload response with upload_id and status
    """
    upload_service = IngestionService()
    if 'file' not in request.files:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'No file provided'
            }
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Empty file name'
            }
        }), 400
    
    # Get optional parameters
    file_name = request.form.get('file_name') or file.filename
    file_year = request.form.get('file_year')
    file_year = int(file_year) if file_year and file_year.isdigit() else None
    
    try:
        result = upload_service.upload_file(file, file_name, file_year)
        response = UploadResponse(
            upload_id=result['upload_id'],
            ingestion_log_id=result['ingestion_log_id'],
            file_name=result['file_name'],
            status=result['status'],
            message=result['message']
        )
        return format_success_response(response.model_dump(), status_code=202)
    
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise


@ingestion_bp.route('/status/<uuid:ingestion_log_id>', methods=['GET'])
@handle_exceptions
def get_ingestion_status(ingestion_log_id: uuid.UUID):
    """
    GET /api/ingestion/status/<ingestion_log_id>
    
    Get ingestion status and progress.
    
    Returns:
        Ingestion status with progress information
    """
    upload_service = IngestionService()
    status = upload_service.get_ingestion_status(str(ingestion_log_id))
    
    # Determine response type
    if 'job_id' in status:
        response = IngestionProgressResponse(**status)
    else:
        response = IngestionStatusResponse(
            id=str(status['ingestion_log_id']),
            file_name=status.get('file_name', ''),
            file_year=status.get('file_year'),
            ingestion_status=status['status'],
            total_records=status.get('total_records', 0),
            successful_records=status.get('successful_records', 0),
            failed_records=status.get('failed_records', 0),
            error_message=status.get('error_message'),
            started_at=datetime.fromisoformat(status['started_at']) if status.get('started_at') else None,
            completed_at=datetime.fromisoformat(status['completed_at']) if status.get('completed_at') else None,
            created_at=datetime.fromisoformat(status['created_at']) if status.get('created_at') else datetime.now()
        )
    
    return format_success_response(response.model_dump())


@ingestion_bp.route('/history', methods=['GET'])
@handle_exceptions
def list_ingestion_history():
    """
    GET /api/ingestion/history
    
    List ingestion history.
    
    Query params:
    - status: Filter by status (optional)
    - limit: Maximum results (default: 50, max: 100)
    - offset: Offset for pagination (default: 0)
    
    Returns:
        List of ingestion logs
    """
    query = IngestionStatusQuery.from_query_params(request.args)
    upload_service = IngestionService()
    history = upload_service.list_ingestion_history(
        status=query.status,
        limit=query.limit,
        offset=query.offset
    )
    
    return format_success_response({
        'ingestions': history,
        'pagination': {
            'limit': query.limit,
            'offset': query.offset,
            'total': len(history)  # Note: actual total would require count query
        }
    })


@ingestion_bp.route('/ingest-path', methods=['POST'])
@handle_exceptions
def ingest_from_path():
    """
    POST /api/ingestion/ingest-path
    
    Ingest a file from a direct file path.
    
    JSON body:
    - file_path: Path to the file (required)
    - file_year: Year of the data (optional)
    
    Returns:
        Upload response with ingestion_log_id and status
    """
    data = request.get_json()
    upload_service = IngestionService()
    if not data or 'file_path' not in data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'file_path is required'
            }
        }), 400
    
    file_path = data.get('file_path')
    file_year = data.get('file_year')
    file_year = int(file_year) if file_year and str(file_year).isdigit() else None
    
    try:
        result = upload_service.ingest_file_from_path(file_path, file_year)
        response = UploadResponse(
            upload_id=result['upload_id'],
            ingestion_log_id=result['ingestion_log_id'],
            file_name=result['file_name'],
            status=result['status'],
            message=result['message']
        )
        return format_success_response(response.model_dump(), status_code=202)
    
    except Exception as e:
        logger.error(f"Ingest from path error: {e}", exc_info=True)
        raise


@ingestion_bp.route('/<uuid:ingestion_log_id>/cancel', methods=['DELETE'])
@handle_exceptions
def cancel_ingestion(ingestion_log_id: uuid.UUID):
    """
    DELETE /api/ingestion/<ingestion_log_id>/cancel
    
    Cancel a pending or processing ingestion.
    
    Returns:
        Success message
    """
    upload_service = IngestionService()
    cancelled = upload_service.cancel_ingestion(str(ingestion_log_id))
    
    if cancelled:
        return format_success_response({
            'message': f'Ingestion {ingestion_log_id} cancelled successfully'
        })
    else:
        return jsonify({
            'error': {
                'code': 'CANNOT_CANCEL',
                'message': 'Ingestion cannot be cancelled (already completed or failed)'
            }
        }), 400
