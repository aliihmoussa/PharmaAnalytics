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
        start_date_str = params.get('start_date')
        end_date_str = params.get('end_date')
        
        if not start_date_str:
            raise ValueError("start_date is required")
        if not end_date_str:
            raise ValueError("end_date is required")
        
        return cls(
            start_date=parse_date(start_date_str),
            end_date=parse_date(end_date_str),
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
        start_date_str = params.get('start_date')
        end_date_str = params.get('end_date')
        
        if not start_date_str:
            raise ValueError("start_date is required")
        if not end_date_str:
            raise ValueError("end_date is required")
        
        granularity_str = params.get('granularity', 'daily').lower()
        try:
            granularity = GranularityEnum(granularity_str)
        except ValueError:
            granularity = GranularityEnum.DAILY
        
        return cls(
            start_date=parse_date(start_date_str),
            end_date=parse_date(end_date_str),
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
        start_date_str = params.get('start_date')
        end_date_str = params.get('end_date')
        
        if not start_date_str:
            raise ValueError("start_date is required")
        if not end_date_str:
            raise ValueError("end_date is required")
        
        return cls(
            start_date=parse_date(start_date_str),
            end_date=parse_date(end_date_str),
            chart_type=chart_type,
            filters={}
        )


class MetricTypeEnum(str, Enum):
    """Metric type for year comparison."""
    QUANTITY = "quantity"
    VALUE = "value"
    TRANSACTIONS = "transactions"


class YearComparisonRequest(BaseModel):
    """Request model for year-over-year comparison."""
    metric_type: MetricTypeEnum = MetricTypeEnum.QUANTITY
    drug_code: Optional[str] = None
    start_year: Optional[int] = Field(default=2019, ge=2010, le=2030)
    end_year: Optional[int] = Field(default=2022, ge=2010, le=2030)
    
    @field_validator('end_year')
    @classmethod
    def validate_year_range(cls, v, info):
        """Validate that end_year is after or equal to start_year."""
        if 'start_year' in info.data and v < info.data['start_year']:
            raise ValueError('end_year must be after or equal to start_year')
        return v
    
    @classmethod
    def from_query_params(cls, params):
        """Create instance from Flask query parameters."""
        metric_str = params.get('metric_type', 'quantity').lower()
        try:
            metric_type = MetricTypeEnum(metric_str)
        except ValueError:
            metric_type = MetricTypeEnum.QUANTITY
        
        return cls(
            metric_type=metric_type,
            drug_code=params.get('drug_code'),
            start_year=int(params['start_year']) if params.get('start_year') else 2019,
            end_year=int(params['end_year']) if params.get('end_year') else 2022
        )


class CategoryAnalysisRequest(BaseModel):
    """Request model for category analysis."""
    start_date: date
    end_date: date
    granularity: str = Field(default='monthly', pattern='^(monthly|quarterly)$')
    limit: int = Field(default=10, ge=1, le=15, description='Limit number of top categories to return')
    
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
        start_date_str = params.get('start_date')
        end_date_str = params.get('end_date')
        
        if not start_date_str:
            raise ValueError("start_date is required")
        if not end_date_str:
            raise ValueError("end_date is required")
        
        # Parse limit parameter
        limit = 10  # default
        if 'limit' in params:
            try:
                limit = int(params.get('limit'))
                if limit < 1:
                    limit = 10
                elif limit > 15:
                    limit = 15
            except (ValueError, TypeError):
                limit = 10
        
        return cls(
            start_date=parse_date(start_date_str),
            end_date=parse_date(end_date_str),
            granularity=params.get('granularity', 'monthly'),
            limit=limit
        )


class PatientDemographicsRequest(BaseModel):
    """Request model for patient demographics."""
    start_date: date
    end_date: date
    group_by: str = Field(default='age', pattern='^(age|room|bed)$')
    
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
        start_date_str = params.get('start_date')
        end_date_str = params.get('end_date')
        
        if not start_date_str:
            raise ValueError("start_date is required")
        if not end_date_str:
            raise ValueError("end_date is required")
        
        return cls(
            start_date=parse_date(start_date_str),
            end_date=parse_date(end_date_str),
            group_by=params.get('group_by', 'age')
        )

