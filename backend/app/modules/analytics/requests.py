"""Analytics request models - Combined from dashboard and viz modules."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum
from backend.app.shared.validators import parse_date


# Enums
class GranularityEnum(str, Enum):
    """Time granularity for time-series queries."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class MetricTypeEnum(str, Enum):
    """Metric type for year comparison."""
    QUANTITY = "quantity"
    VALUE = "value"
    TRANSACTIONS = "transactions"


# Cost Analysis Requests (from viz module)
class CostAnalysisRequest(BaseModel):
    """Request model for cost analysis endpoint."""
    start_date: date
    end_date: date
    departments: Optional[List[int]] = None
    price_min: Optional[float] = Field(default=None, ge=0)
    price_max: Optional[float] = Field(default=None, ge=0)
    drug_categories: Optional[List[int]] = None
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Validate that end_date is after start_date."""
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v
    
    @field_validator('price_max')
    @classmethod
    def validate_price_range(cls, v, info):
        """Validate that price_max is greater than price_min if both are provided."""
        if v is not None and 'price_min' in info.data:
            price_min = info.data.get('price_min')
            if price_min is not None and v < price_min:
                raise ValueError('price_max must be greater than or equal to price_min')
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
        
        # Parse departments (can be comma-separated or multiple params)
        departments = None
        if params.get('departments'):
            if isinstance(params.get('departments'), str):
                departments = [int(d.strip()) for d in params.get('departments').split(',') if d.strip()]
            elif isinstance(params.get('departments'), list):
                departments = [int(d) for d in params.get('departments')]
        elif params.getlist('departments[]'):
            departments = [int(d) for d in params.getlist('departments[]')]
        
        # Parse drug_categories (can be comma-separated or multiple params)
        drug_categories = None
        if params.get('drug_categories'):
            if isinstance(params.get('drug_categories'), str):
                drug_categories = [int(c.strip()) for c in params.get('drug_categories').split(',') if c.strip()]
            elif isinstance(params.get('drug_categories'), list):
                drug_categories = [int(c) for c in params.get('drug_categories')]
        elif params.getlist('drug_categories[]'):
            drug_categories = [int(c) for c in params.getlist('drug_categories[]')]
        
        # Parse price filters
        price_min = None
        if params.get('price_min'):
            price_min = float(params.get('price_min'))
        
        price_max = None
        if params.get('price_max'):
            price_max = float(params.get('price_max'))
        
        return cls(
            start_date=parse_date(start_date_str),
            end_date=parse_date(end_date_str),
            departments=departments,
            price_min=price_min,
            price_max=price_max,
            drug_categories=drug_categories
        )


class HospitalStayRequest(BaseModel):
    """Request model for hospital stay duration analysis endpoint."""
    start_date: date
    end_date: date
    departments: Optional[List[int]] = None
    min_stay_days: Optional[int] = Field(default=None, ge=0)
    max_stay_days: Optional[int] = Field(default=None, ge=0)
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Validate that end_date is after start_date."""
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v
    
    @field_validator('max_stay_days')
    @classmethod
    def validate_stay_range(cls, v, info):
        """Validate that max_stay_days is greater than min_stay_days if both are provided."""
        if v is not None and 'min_stay_days' in info.data:
            min_stay = info.data.get('min_stay_days')
            if min_stay is not None and v < min_stay:
                raise ValueError('max_stay_days must be greater than or equal to min_stay_days')
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
        
        # Parse departments (can be comma-separated or multiple params)
        departments = None
        if params.get('departments'):
            if isinstance(params.get('departments'), str):
                departments = [int(d.strip()) for d in params.get('departments').split(',') if d.strip()]
            elif isinstance(params.get('departments'), list):
                departments = [int(d) for d in params.get('departments')]
        elif params.getlist('departments[]'):
            departments = [int(d) for d in params.getlist('departments[]')]
        
        # Parse stay duration filters
        min_stay_days = None
        if params.get('min_stay_days'):
            min_stay_days = int(params.get('min_stay_days'))
        
        max_stay_days = None
        if params.get('max_stay_days'):
            max_stay_days = int(params.get('max_stay_days'))
        
        return cls(
            start_date=parse_date(start_date_str),
            end_date=parse_date(end_date_str),
            departments=departments,
            min_stay_days=min_stay_days,
            max_stay_days=max_stay_days
        )


# Dashboard Analytics Requests (from dashboard module)
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

