"""Store failed records during ingestion for review."""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .base import Base


class DataIngestionError(Base):
    """Store failed records during ingestion for review."""

    __tablename__ = 'data_ingestion_errors'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    ingestion_log_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    row_number = Column(Integer, nullable=True, comment='Original row number in file')
    raw_data = Column(Text, nullable=True, comment='JSON of raw row data')
    error_type = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
