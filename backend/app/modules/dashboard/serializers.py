"""Analytics feature response models."""

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date


class DrugInfo(BaseModel):
    """Drug information model."""
    drug_code: str
    drug_name: str
    total_dispensed: int
    total_value: float
    transaction_count: int


class TopDrugsResponse(BaseModel):
    """Response model for top drugs endpoint."""
    drugs: List[DrugInfo]
    period: Dict[str, date]
    total_unique_drugs: int


class TimeSeriesPoint(BaseModel):
    """Time-series data point."""
    date: date
    quantity: int
    value: float
    transaction_count: int


class DrugDemandResponse(BaseModel):
    """Response model for drug demand endpoint."""
    data: List[TimeSeriesPoint]
    drug_code: Optional[str] = None
    granularity: str


class SummaryStatsResponse(BaseModel):
    """Response model for summary statistics."""
    total_dispensed: int
    total_value: float
    total_transactions: int
    unique_drugs: int
    unique_departments: int
    date_range: Optional[Dict[str, date]] = None
    avg_daily_dispensed: Optional[float] = None


class ChartDataResponse(BaseModel):
    """Response model for chart data."""
    chart_type: str
    data: Dict
    config: Optional[Dict] = None


class YearDataPoint(BaseModel):
    """Year comparison data point."""
    year: int
    metric_value: float


class YearComparisonResponse(BaseModel):
    """Response model for year-over-year comparison."""
    metric_type: str
    data: List[YearDataPoint]
    drug_code: Optional[str] = None
    years_compared: List[int]


class CategoryDataPoint(BaseModel):
    """Category analysis data point."""
    period: str
    category_id: int
    total_quantity: int
    total_value: float
    transaction_count: int
    unique_drugs: int


class CategoryAnalysisResponse(BaseModel):
    """Response model for category analysis."""
    data: List[CategoryDataPoint]
    granularity: str
    period: Dict[str, date]
    total_categories: int


class DemographicsDataPoint(BaseModel):
    """Patient demographics data point."""
    group: str
    transaction_count: int
    total_quantity: int
    total_value: float
    unique_drugs: Optional[int] = None


class PatientDemographicsResponse(BaseModel):
    """Response model for patient demographics."""
    data: List[DemographicsDataPoint]
    group_by: str
    period: Dict[str, date]
    total_groups: int

