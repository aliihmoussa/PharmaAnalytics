"""Data Access Layer for data upload feature."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.app.database.models import DataIngestionLog, DataIngestionError
from backend.app.database.session import get_db_session
import logging

logger = logging.getLogger(__name__)


class DataUploadDAL:
    """Data access layer for data upload operations using context manager pattern."""
    
    def __init__(self):
        """Initialize the DAL with a database session."""
        self._session: Optional[Session] = None
    
    def __enter__(self):
        """Context manager entry - get a database session."""
        self._session = get_db_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close the database session."""
        if self._session:
            self._session.close()
            self._session = None
    
    def _ensure_session(self):
        """Ensure database session is initialized."""
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with DataUploadDAL() as dal:'")
    
    def create_ingestion_log(
        self,
        file_name: str,
        file_year: Optional[int] = None,
        file_hash: Optional[str] = None,
        status: str = 'pending'
    ) -> DataIngestionLog:
        """Create a new ingestion log entry."""
        self._ensure_session()
        
        try:
            log_entry = DataIngestionLog(
                file_name=file_name,
                file_year=file_year,
                file_hash=file_hash,
                ingestion_status=status,
                started_at=datetime.now() if status == 'processing' else None
            )
            self._session.add(log_entry)
            self._session.commit()
            self._session.refresh(log_entry)
            return log_entry
        except Exception as e:
            self._session.rollback()
            logger.error(f"Error creating ingestion log: {e}")
            raise
    
    def get_ingestion_log(self, log_id: uuid.UUID) -> Optional[DataIngestionLog]:
        """Get ingestion log by ID."""
        self._ensure_session()
        return self._session.query(DataIngestionLog).filter(DataIngestionLog.id == log_id).first()
    
    def get_ingestion_log_by_filename(self, file_name: str) -> Optional[DataIngestionLog]:
        """Get ingestion log by file name."""
        self._ensure_session()
        return self._session.query(DataIngestionLog).filter(
                DataIngestionLog.file_name == file_name
            ).order_by(DataIngestionLog.created_at.desc()).first()
    
    def update_ingestion_log(
        self,
        log_id: uuid.UUID,
        status: Optional[str] = None,
        total_records: Optional[int] = None,
        successful_records: Optional[int] = None,
        failed_records: Optional[int] = None,
        error_message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ) -> bool:
        """Update ingestion log."""
        self._ensure_session()
        
        try:
            log_entry = self._session.query(DataIngestionLog).filter(DataIngestionLog.id == log_id).first()
            if not log_entry:
                return False
            
            if status:
                log_entry.ingestion_status = status
            if total_records is not None:
                log_entry.total_records = total_records
            if successful_records is not None:
                log_entry.successful_records = successful_records
            if failed_records is not None:
                log_entry.failed_records = failed_records
            if error_message is not None:
                log_entry.error_message = error_message
            if started_at:
                log_entry.started_at = started_at
            if completed_at:
                log_entry.completed_at = completed_at
            
            self._session.commit()
            return True
        except Exception as e:
            self._session.rollback()
            logger.error(f"Error updating ingestion log: {e}")
            raise
    
    def list_ingestion_logs(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DataIngestionLog]:
        """List ingestion logs with optional filtering."""
        self._ensure_session()
        
        query = self._session.query(DataIngestionLog)
        
        if status:
            query = query.filter(DataIngestionLog.ingestion_status == status)
        
        query = query.order_by(DataIngestionLog.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def log_ingestion_error(
        self,
        ingestion_log_id: uuid.UUID,
        error_type: str,
        error_message: str,
        row_number: Optional[int] = None,
        raw_data: Optional[str] = None
    ):
        """Log an ingestion error."""
        self._ensure_session()
        
        try:
            error_entry = DataIngestionError(
                ingestion_log_id=ingestion_log_id,
                row_number=row_number,
                raw_data=raw_data,
                error_type=error_type,
                error_message=error_message
            )
            self._session.add(error_entry)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            logger.error(f"Error logging ingestion error: {e}")
            raise

