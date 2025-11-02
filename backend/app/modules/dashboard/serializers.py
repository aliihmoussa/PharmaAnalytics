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

