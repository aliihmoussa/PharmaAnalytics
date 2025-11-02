"""Request models for data upload feature."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


class UploadFileRequest(BaseModel):
    """Request model for file upload."""
    
    file_name: str = Field(..., description="Original file name")
    file_year: Optional[int] = Field(None, description="Year of the data file")
    
    @field_validator('file_name')
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("File name cannot be empty")
        return v.strip()


class IngestionStatusQuery(BaseModel):
    """Query parameters for ingestion status."""
    
    status: Optional[str] = Field(None, description="Filter by status")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    
    @classmethod
    def from_query_params(cls, args):
        """Create from Flask request args."""
        return cls(
            status=args.get('status'),
            limit=int(args.get('limit', 50)),
            offset=int(args.get('offset', 0))
        )

