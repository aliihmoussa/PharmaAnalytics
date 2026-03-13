"""Routes for inventory (STORE file) upload."""

import logging
import os
import uuid
from pathlib import Path

from flask import Blueprint, request
from werkzeug.utils import secure_filename

from backend.app.modules.inventory.processor import process_store_file
from backend.app.shared.middleware import handle_exceptions, format_success_response

logger = logging.getLogger(__name__)

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

UPLOAD_DIR = Path('data/uploads/inventory')
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


@inventory_bp.route('/upload', methods=['POST'])
@handle_exceptions
def upload_store_file():
    """
    POST /api/inventory/upload

    Upload a STORE Excel file (e.g. STORE 2024.xlsx). Data must be in sheet 'rep25071808450909'.
    Processes synchronously and returns successful/failed record counts.

    Form data:
    - file: Excel file (required)

    Returns:
        { "successful_records": int, "failed_records": int, "message": str }
    """
    if 'file' not in request.files:
        return format_success_response({
            'error': 'No file provided',
            'successful_records': 0,
            'failed_records': 0,
        }, 400)

    file = request.files['file']
    if not file or file.filename == '':
        return format_success_response({
            'error': 'Empty file name',
            'successful_records': 0,
            'failed_records': 0,
        }, 400)

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return format_success_response({
            'error': f'Allowed extensions: {", ".join(ALLOWED_EXTENSIONS)}',
            'successful_records': 0,
            'failed_records': 0,
        }, 400)

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return format_success_response({
            'error': f'File too large (max {MAX_FILE_SIZE // (1024*1024)}MB)',
            'successful_records': 0,
            'failed_records': 0,
        }, 400)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = secure_filename(file.filename)
    path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_name}"
    try:
        file.save(str(path))
        successful, failed = process_store_file(path, file_name=safe_name)
        return format_success_response({
            'successful_records': successful,
            'failed_records': failed,
            'message': f'Ingested {successful} records, {failed} failed',
        })
    except Exception as e:
        logger.error(f"Inventory upload error: {e}", exc_info=True)
        return format_success_response({
            'error': str(e),
            'successful_records': 0,
            'failed_records': 0,
        }, 400)
    finally:
        if path.exists():
            try:
                path.unlink()
            except Exception:
                pass
