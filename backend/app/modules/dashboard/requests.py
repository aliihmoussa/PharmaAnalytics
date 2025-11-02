"""Analytics feature request models."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from enum import Enum
from backend.app.shared.validators import parse_date


class GranularityEnum(str, Enum):
    """Time granularity for time-series queries."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TopDrugsRequest(BaseModel):
    """Request model for top drugs endpoint."""
    start_date: date
    end_date: date
    limit: int = Field(default=10, ge=1, le=100)
    category_id: Optional[int] = None
    department_id: Optional[int] = None
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Validate that end_date is after start_date."""
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v
    
    @classmethod
    def from_query_params(cls, params):
        """Create instance from Flask query parameters."""
        return cls(
            start_date=parse_date(params.get('start_date')),
            end_date=parse_date(params.get('end_date')),
            limit=int(params.get('limit', 10)),
            category_id=int(params['category_id']) if params.get('category_id') else None,
            department_id=int(params['department_id']) if params.get('department_id') else None
        )


class DrugDemandRequest(BaseModel):
    """Request model for drug demand time-series."""
    start_date: date
    end_date: date
    drug_code: Optional[str] = None
    granularity: GranularityEnum = GranularityEnum.DAILY
    
    @classmethod
    def from_query_params(cls, params):
        """Create instance from Flask query parameters."""
        granularity_str = params.get('granularity', 'daily').lower()
        try:
            granularity = GranularityEnum(granularity_str)
        except ValueError:
            granularity = GranularityEnum.DAILY
        
        return cls(
            start_date=parse_date(params.get('start_date')),
            end_date=parse_date(params.get('end_date')),
            drug_code=params.get('drug_code'),
            granularity=granularity
        )


class SummaryStatsRequest(BaseModel):
    """Request model for summary statistics."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @classmethod
    def from_query_params(cls, params):
        """Create instance from Flask query parameters."""
        return cls(
            start_date=parse_date(params.get('start_date')) if params.get('start_date') else None,
            end_date=parse_date(params.get('end_date')) if params.get('end_date') else None
        )


class ChartDataRequest(BaseModel):
    """Request model for chart data."""
    start_date: date
    end_date: date
    chart_type: str
    filters: Optional[dict] = {}
    
    @classmethod
    def from_query_params(cls, params, chart_type: str):
        """Create instance from Flask query parameters."""
        return cls(
            start_date=parse_date(params.get('start_date')),
            end_date=parse_date(params.get('end_date')),
            chart_type=chart_type,
            filters={}
        )

