"""Visualization request models."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from backend.app.shared.validators import parse_date


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

