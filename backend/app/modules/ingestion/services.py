"""Service layer for data ingestion - Class-based service."""

import os
import uuid
from pathlib import Path
from typing import Optional, Union, Dict, Any
from datetime import datetime
import logging

from werkzeug.utils import secure_filename
from backend.app.shared.base_service import BaseService
from backend.app.modules.ingestion.dal import DataUploadDAL
from backend.app.modules.ingestion.processors import IngestionProcessor, calculate_file_hash
from backend.app.config import config
from backend.app.modules.ingestion.exceptions import (
    FileValidationError,
    UnsupportedFileTypeError,
    FileSizeLimitExceededError,
    DuplicateFileError,
    IngestionJobNotFoundError,
)
from backend.app.modules.ingestion.tasks import process_ingestion_task
from celery.result import AsyncResult

logger = logging.getLogger(__name__)


class IngestionService(BaseService):
    """Class-based service for handling data ingestion operations."""
    
    # Configuration constants
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS = {'csv', 'txt', 'tsv', 'dat', 'xlsx', 'xls'}
    UPLOAD_DIR = Path('data/uploads/temp')
    
    def __init__(self):
        """Initialize ingestion service with dependencies."""
        super().__init__()
        self.dal = DataUploadDAL()
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.logger.info("IngestionService initialized")
    
    def validate_file(self, file, file_name: str) -> tuple[Path, int]:
        """
        Validate uploaded file.
        
        Args:
            file: File object from request
            file_name: Original file name
        
        Returns:
            Tuple of (saved_file_path, file_size)
        
        Raises:
            FileValidationError: If validation fails
        """
        # Check file extension
        if not file_name or '.' not in file_name:
            raise UnsupportedFileTypeError("File must have an extension")
        
        extension = file_name.rsplit('.', 1)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"File type '{extension}' not allowed. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Read file to get size and save temporarily
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        # Check file size
        if file_size > self.MAX_FILE_SIZE:
            raise FileSizeLimitExceededError(
                f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({self.MAX_FILE_SIZE / 1024 / 1024:.2f}MB)"
            )
        
        if file_size == 0:
            raise FileValidationError("File is empty")
        
        # Save file temporarily
        secure_name = secure_filename(file_name)
        unique_id = str(uuid.uuid4())
        saved_path = self.UPLOAD_DIR / f"{unique_id}_{secure_name}"
        
        with open(saved_path, 'wb') as f:
            f.write(file.read())
        
        logger.info(f"Saved uploaded file: {saved_path} ({file_size} bytes)")
        return saved_path, file_size
    
    def upload_file(self, file, file_name: str, file_year: Optional[int] = None) -> dict:
        """
        Process file upload and initiate ingestion.
        
        Args:
            file: File object
            file_name: Original file name
            file_year: Optional year of the data
        
        Returns:
            Dictionary with upload_id, ingestion_log_id, status, etc.
        """
        # Validate and save file
        saved_path, file_size = self.validate_file(file, file_name)
        
        # Calculate file hash
        file_hash = calculate_file_hash(saved_path)
        
        # Check for duplicates (by hash or filename)
        existing_log = self.dal.get_ingestion_log_by_filename(file_name)
        if existing_log and existing_log.ingestion_status == 'completed':
            # Clean up temp file
            saved_path.unlink()
            raise DuplicateFileError(f"File '{file_name}' has already been ingested")
        
        # Create ingestion log
        ingestion_log = self.dal.create_ingestion_log(file_name=file_name, file_year=file_year, file_hash=file_hash)
        
        # Submit Celery task
        task = process_ingestion_task.delay(
            str(ingestion_log.id),
            str(saved_path),
            file_name
        )
        
        return {
            'upload_id': task.id,
            'ingestion_log_id': str(ingestion_log.id),  # Convert UUID to string
            'file_name': file_name,
            'status': 'pending',
            'message': 'File uploaded and queued for processing'
        }
    
    def get_ingestion_status(self, ingestion_log_id: Union[uuid.UUID, str]) -> dict:
        """Get ingestion status by log ID."""
        # Convert string UUID to UUID object if needed
        if isinstance(ingestion_log_id, str):
            ingestion_log_id = uuid.UUID(ingestion_log_id)
        
        log_entry = self.dal.get_ingestion_log(ingestion_log_id)
        if not log_entry:
            raise IngestionJobNotFoundError(f"Ingestion log {ingestion_log_id} not found")
        
        # Try to get Celery task status if still processing
        # We store the task_id in the ingestion log or search by ingestion_log_id
        # For now, check task status from database log entry
        
        # If status is still processing, check Celery task (task_id could be stored separately)
        # For MVP, we'll rely on database status updates from the task
        
        return {
            'ingestion_log_id': str(log_entry.id),  # Convert UUID to string
            'file_name': log_entry.file_name,
            'file_year': log_entry.file_year,
            'status': log_entry.ingestion_status,
            'total_records': log_entry.total_records,
            'successful_records': log_entry.successful_records,
            'failed_records': log_entry.failed_records,
            'error_message': log_entry.error_message,
            'started_at': log_entry.started_at.isoformat() if log_entry.started_at else None,
            'completed_at': log_entry.completed_at.isoformat() if log_entry.completed_at else None,
            'created_at': log_entry.created_at.isoformat() if log_entry.created_at else None,
        }
    
    def list_ingestion_history(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> list:
        """List ingestion history."""
        logs = self.dal.list_ingestion_logs(status=status, limit=limit, offset=offset)
        return [self._log_to_dict(log) for log in logs]
    
    def cancel_ingestion(self, ingestion_log_id: Union[uuid.UUID, str]) -> bool:
        """Cancel a pending ingestion."""
        # Convert string UUID to UUID object if needed
        if isinstance(ingestion_log_id, str):
            ingestion_log_id = uuid.UUID(ingestion_log_id)
        
        log_entry = self.dal.get_ingestion_log(ingestion_log_id)
        if not log_entry:
            raise IngestionJobNotFoundError(f"Ingestion log {ingestion_log_id} not found")
        
        if log_entry.ingestion_status not in ['pending', 'processing']:
            return False
        
        # Try to revoke Celery task if processing
        # Note: Celery task revocation requires task_id, which we'd need to store
        # For MVP, we'll just update the database status
        
        # Update log status
        if log_entry.ingestion_status in ['pending', 'processing']:
            self.dal.update_ingestion_log(
                ingestion_log_id,
                status='cancelled',
                completed_at=datetime.now()
            )
            return True
        
        return False
    
    def ingest_file_from_path(self, file_path: str, file_year: Optional[int] = None) -> dict:
        """
        Ingest a file from a direct file path.
        
        Args:
            file_path: Path to the file (absolute or relative)
            file_year: Optional year of the data
        
        Returns:
            Dictionary with ingestion_log_id, status, etc.
        
        Raises:
            FileValidationError: If file path is invalid or not accessible
        """
        from pathlib import Path
        
        # Resolve path
        file_path_obj = Path(file_path).resolve()
        
        # Security: Validate path is within allowed directories
        allowed_paths = [Path(p.strip()).resolve() for p in config.ALLOWED_INGESTION_PATHS.split(',')]
        if not any(str(file_path_obj).startswith(str(allowed_path)) for allowed_path in allowed_paths):
            raise FileValidationError(
                f"File path is not within allowed directories. Allowed: {config.ALLOWED_INGESTION_PATHS}",
                details={'file_path': str(file_path_obj)}
            )
        
        # Check if file exists
        if not file_path_obj.exists():
            raise FileValidationError(f"File not found: {file_path_obj}")
        
        # Check if file is readable
        if not file_path_obj.is_file():
            raise FileValidationError(f"Path is not a file: {file_path_obj}")
        
        if not os.access(file_path_obj, os.R_OK):
            raise FileValidationError(f"File is not readable: {file_path_obj}")
        
        # Validate file extension
        file_name = file_path_obj.name
        if not file_name or '.' not in file_name:
            raise UnsupportedFileTypeError("File must have an extension")
        
        extension = file_name.rsplit('.', 1)[1].lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"File type '{extension}' not allowed. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file_size = file_path_obj.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise FileSizeLimitExceededError(
                f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({self.MAX_FILE_SIZE / 1024 / 1024:.2f}MB)"
            )
        
        if file_size == 0:
            raise FileValidationError("File is empty")
        
        # Calculate file hash
        file_hash = calculate_file_hash(file_path_obj)
        
        # Check for duplicates
        existing_log = self.dal.get_ingestion_log_by_filename(file_name)
        if existing_log and existing_log.ingestion_status == 'completed':
            raise DuplicateFileError(f"File '{file_name}' has already been ingested")
        
        # Create ingestion log
        ingestion_log = self.dal.create_ingestion_log(file_name=file_name, file_year=file_year, file_hash=file_hash)
        
        # Submit Celery task
        task = process_ingestion_task.delay(
            str(ingestion_log.id),
            str(file_path_obj),
            file_name
        )
        
        return {
            'upload_id': task.id,
            'ingestion_log_id': str(ingestion_log.id),
            'file_name': file_name,
            'file_path': str(file_path_obj),
            'status': 'pending',
            'message': 'File queued for processing'
        }
    
    def _log_to_dict(self, log_entry) -> dict:
        """Convert log entry to dictionary."""
        return {
            'id': str(log_entry.id),  # Convert UUID to string
            'file_name': log_entry.file_name,
            'file_year': log_entry.file_year,
            'ingestion_status': log_entry.ingestion_status,
            'total_records': log_entry.total_records,
            'successful_records': log_entry.successful_records,
            'failed_records': log_entry.failed_records,
            'error_message': log_entry.error_message,
            'started_at': log_entry.started_at.isoformat() if log_entry.started_at else None,
            'completed_at': log_entry.completed_at.isoformat() if log_entry.completed_at else None,
            'created_at': log_entry.created_at.isoformat() if log_entry.created_at else None,
        }

