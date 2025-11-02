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
    """Data access layer for data upload operations."""
    
    def create_ingestion_log(
        self,
        file_name: str,
        file_year: Optional[int] = None,
        file_hash: Optional[str] = None,
        status: str = 'pending'
    ) -> DataIngestionLog:
        """Create a new ingestion log entry."""
        session = get_db_session()
        try:
            log_entry = DataIngestionLog(
                file_name=file_name,
                file_year=file_year,
                file_hash=file_hash,
                ingestion_status=status,
                started_at=datetime.now() if status == 'processing' else None
            )
            session.add(log_entry)
            session.commit()
            session.refresh(log_entry)
            return log_entry
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating ingestion log: {e}")
            raise
    
    def get_ingestion_log(self, log_id: uuid.UUID) -> Optional[DataIngestionLog]:
        """Get ingestion log by ID."""
        session = get_db_session()
        try:
            return session.query(DataIngestionLog).filter(DataIngestionLog.id == log_id).first()
        finally:
            session.close()
    
    def get_ingestion_log_by_filename(self, file_name: str) -> Optional[DataIngestionLog]:
        """Get ingestion log by file name."""
        session = get_db_session()
        try:
            return session.query(DataIngestionLog).filter(
                DataIngestionLog.file_name == file_name
            ).order_by(DataIngestionLog.created_at.desc()).first()
        finally:
            session.close()
    
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
        session = get_db_session()
        try:
            log_entry = session.query(DataIngestionLog).filter(DataIngestionLog.id == log_id).first()
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
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating ingestion log: {e}")
            raise
        finally:
            session.close()
    
    def list_ingestion_logs(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DataIngestionLog]:
        """List ingestion logs with optional filtering."""
        session = get_db_session()
        try:
            query = session.query(DataIngestionLog)
            
            if status:
                query = query.filter(DataIngestionLog.ingestion_status == status)
            
            query = query.order_by(DataIngestionLog.created_at.desc())
            query = query.limit(limit).offset(offset)
            
            return query.all()
        finally:
            session.close()
    
    def log_ingestion_error(
        self,
        ingestion_log_id: uuid.UUID,
        error_type: str,
        error_message: str,
        row_number: Optional[int] = None,
        raw_data: Optional[str] = None
    ):
        """Log an ingestion error."""
        session = get_db_session()
        try:
            error_entry = DataIngestionError(
                ingestion_log_id=ingestion_log_id,
                row_number=row_number,
                raw_data=raw_data,
                error_type=error_type,
                error_message=error_message
            )
            session.add(error_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging ingestion error: {e}")
        finally:
            session.close()

