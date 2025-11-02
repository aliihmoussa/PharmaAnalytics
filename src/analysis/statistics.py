"""Statistical analysis functions."""

import polars as pl
from typing import Dict, List, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


def descriptive_stats(df: pl.DataFrame, column: Optional[str] = None) -> Dict:
    """
    Calculate descriptive statistics.
    
    Args:
        df: Polars DataFrame
        column: Specific column (all numeric columns if None)
    
    Returns:
        Dictionary with descriptive statistics
    """
    if column:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found")
        numeric_df = df.select(pl.col(column))
    else:
        # Select all numeric columns
        numeric_df = df.select([pl.col(col) for col in df.columns if df[col].dtype in [pl.Int64, pl.Float64]])
    
    stats = {}
    for col in numeric_df.columns:
        stats[col] = {
            'mean': numeric_df[col].mean(),
            'median': numeric_df[col].median(),
            'std': numeric_df[col].std(),
            'min': numeric_df[col].min(),
            'max': numeric_df[col].max(),
            'count': numeric_df[col].count(),
            'null_count': numeric_df[col].null_count()
        }
    
    return stats


def correlation_matrix(df: pl.DataFrame) -> Dict:
    """
    Calculate correlation matrix for numeric columns.
    
    Args:
        df: Polars DataFrame
    
    Returns:
        Dictionary with correlation matrix
    """
    numeric_cols = [col for col in df.columns if df[col].dtype in [pl.Int64, pl.Float64]]
    
    if len(numeric_cols) < 2:
        return {}
    
    correlations = {}
    for i, col1 in enumerate(numeric_cols):
        correlations[col1] = {}
        for col2 in numeric_cols[i:]:
            corr = df.select([pl.corr(col1, col2)]).item()
            correlations[col1][col2] = corr
            if col1 != col2:
                if col2 not in correlations:
                    correlations[col2] = {}
                correlations[col2][col1] = corr
    
    return correlations


def time_series_aggregation(
    df: pl.DataFrame,
    date_column: str,
    value_column: str,
    aggregation: str = 'daily'
) -> pl.DataFrame:
    """
    Aggregate time-series data by time period.
    
    Args:
        df: Polars DataFrame
        date_column: Name of date column
        value_column: Name of value column to aggregate
        aggregation: 'daily', 'weekly', or 'monthly'
    
    Returns:
        Aggregated DataFrame
    """
    if date_column not in df.columns:
        raise ValueError(f"Date column '{date_column}' not found")
    if value_column not in df.columns:
        raise ValueError(f"Value column '{value_column}' not found")
    
    # Parse date if string
    if df[date_column].dtype == pl.Utf8:
        df = df.with_columns(pl.col(date_column).str.strptime(pl.Date, format="%d/%m/%y"))
    
    # Group by time period
    if aggregation == 'daily':
        grouped = df.group_by(pl.col(date_column).dt.date())
    elif aggregation == 'weekly':
        grouped = df.group_by(pl.col(date_column).dt.truncate("1w"))
    elif aggregation == 'monthly':
        grouped = df.group_by(pl.col(date_column).dt.truncate("1mo"))
    else:
        raise ValueError(f"Invalid aggregation: {aggregation}")
    
    aggregated = grouped.agg([
        pl.col(value_column).sum().alias(f'total_{value_column}'),
        pl.col(value_column).mean().alias(f'avg_{value_column}'),
        pl.col(value_column).count().alias('count')
    ]).sort(date_column)
    
    return aggregated

