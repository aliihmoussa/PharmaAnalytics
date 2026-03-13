"""Data ingestion log model for tracking file uploads."""

from sqlalchemy import Column, Integer, String, DateTime, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .base import Base


class DataIngestionLog(Base):
    """Data ingestion log model for tracking file uploads."""

    __tablename__ = 'data_ingestion_log'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    file_name = Column(String(255), nullable=False, index=True)
    file_year = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True, comment='SHA256 hash of original file')
    total_records = Column(Integer, nullable=False, default=0)
    successful_records = Column(Integer, nullable=False, default=0)
    failed_records = Column(Integer, nullable=False, default=0)
    ingestion_status = Column(
        String(50),
        nullable=False,
        default='pending',
        index=True,
        comment='pending, processing, completed, failed, cancelled'
    )
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "ingestion_status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')",
            name='chk_ingestion_status'
        ),
    )
