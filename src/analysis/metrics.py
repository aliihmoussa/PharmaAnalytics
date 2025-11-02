"""Business metrics calculations."""

import polars as pl
from typing import Dict, List, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


def top_drugs(df: pl.DataFrame, limit: int = 10, by: str = 'quantity') -> List[Dict]:
    """
    Get top dispensed drugs.
    
    Args:
        df: Polars DataFrame
        limit: Number of top drugs to return
        by: Sort by 'quantity' or 'value'
    
    Returns:
        List of top drugs with metrics
    """
    if 'ARTICLE' not in df.columns or 'QTY' not in df.columns:
        return []
    
    dispensed = df.filter(pl.col('QTY') < 0)
    
    if by == 'quantity':
        sort_col = 'total_dispensed'
        agg_col = pl.col('QTY').sum().abs()
    else:
        sort_col = 'total_value'
        agg_col = pl.col('T.P').sum().abs()
    
    top = dispensed.group_by(['CODE', 'ARTICLE']).agg([
        agg_col.alias('total_dispensed'),
        pl.col('T.P').sum().abs().alias('total_value'),
        pl.count().alias('transaction_count')
    ]).sort(sort_col, descending=True).head(limit)
    
    return top.to_dicts()


def department_performance(df: pl.DataFrame, limit: int = 10) -> List[Dict]:
    """
    Calculate department performance metrics.
    
    Args:
        df: Polars DataFrame
        limit: Number of top departments
    
    Returns:
        List of department metrics
    """
    if 'C.R' not in df.columns:
        return []
    
    performance = df.filter(pl.col('QTY') < 0).group_by('C.R').agg([
        pl.col('QTY').sum().abs().alias('total_dispensed'),
        pl.col('T.P').sum().abs().alias('total_value'),
        pl.count().alias('transaction_count'),
        pl.col('CODE').n_unique().alias('unique_drugs')
    ]).sort('total_dispensed', descending=True).head(limit)
    
    return performance.to_dicts()


def demand_trends(df: pl.DataFrame, date_column: str = 'DATE', granularity: str = 'daily') -> List[Dict]:
    """
    Calculate demand trends over time.
    
    Args:
        df: Polars DataFrame
        date_column: Name of date column
        granularity: 'daily', 'weekly', or 'monthly'
    
    Returns:
        List of time-series points
    """
    if date_column not in df.columns:
        return []
    
    # Parse date if needed
    if df[date_column].dtype == pl.Utf8:
        df = df.with_columns(pl.col(date_column).str.strptime(pl.Date, format="%d/%m/%y"))
    
    # Group by time period
    trunc = "1d" if granularity == 'daily' else ("1w" if granularity == 'weekly' else "1mo")
    
    trends = df.filter(pl.col('QTY') < 0).group_by(
        pl.col(date_column).dt.truncate(trunc)
    ).agg([
        pl.col('QTY').sum().abs().alias('quantity'),
        pl.col('T.P').sum().abs().alias('value'),
        pl.count().alias('transaction_count')
    ]).sort(date_column)
    
    return trends.to_dicts()

