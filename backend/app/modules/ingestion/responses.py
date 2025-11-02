"""Response models for data upload feature."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IngestionStatusResponse(BaseModel):
    """Ingestion status response."""
    
    id: str  # UUID as string
    file_name: str
    file_year: Optional[int]
    ingestion_status: str
    total_records: int
    successful_records: int
    failed_records: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    """Response for file upload."""
    
    upload_id: str
    ingestion_log_id: str  # UUID as string
    file_name: str
    status: str
    message: str
    estimated_completion_time: Optional[str] = None


class IngestionProgressResponse(BaseModel):
    """Ingestion progress response."""
    
    job_id: str
    ingestion_log_id: str  # UUID as string
    status: str
    progress: int  # 0-100
    progress_message: str
    total_records: int
    successful_records: int
    failed_records: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

