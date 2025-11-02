"""Exploratory data analysis functions."""

import polars as pl
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def data_profile(df: pl.DataFrame) -> Dict:
    """
    Generate comprehensive data profile.
    
    Args:
        df: Polars DataFrame
    
    Returns:
        Dictionary with data profile
    """
    profile = {
        'shape': {'rows': len(df), 'columns': len(df.columns)},
        'columns': df.columns,
        'dtypes': {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)},
        'memory_usage': df.estimated_size() if hasattr(df, 'estimated_size') else None
    }
    
    return profile


def detect_patterns(df: pl.DataFrame, date_column: str = 'DATE') -> Dict:
    """
    Detect patterns in the data.
    
    Args:
        df: Polars DataFrame
        date_column: Name of date column
    
    Returns:
        Dictionary with detected patterns
    """
    patterns = {}
    
    # Date range
    if date_column in df.columns:
        try:
            if df[date_column].dtype == pl.Utf8:
                dates = pl.col(date_column).str.strptime(pl.Date, format="%d/%m/%y")
            else:
                dates = pl.col(date_column)
            
            date_info = df.select([
                dates.min().alias('min_date'),
                dates.max().alias('max_date'),
                dates.count().alias('date_count')
            ])
            
            patterns['date_range'] = date_info.to_dicts()[0]
        except Exception as e:
            logger.warning(f"Could not analyze date patterns: {e}")
    
    return patterns


def calculate_key_metrics(df: pl.DataFrame) -> Dict:
    """
    Calculate key business metrics.
    
    Args:
        df: Polars DataFrame
    
    Returns:
        Dictionary with key metrics
    """
    metrics = {}
    
    # Top drugs (if ARTICLE column exists)
    if 'ARTICLE' in df.columns:
        top_drugs = df.filter(pl.col('QTY') < 0).group_by('ARTICLE').agg([
            pl.col('QTY').sum().abs().alias('total_dispensed'),
            pl.col('T.P').sum().abs().alias('total_value'),
            pl.count().alias('transaction_count')
        ]).sort('total_dispensed', descending=True).head(10)
        
        metrics['top_drugs'] = top_drugs.to_dicts()
    
    # Total dispensed quantity
    if 'QTY' in df.columns:
        total_dispensed = df.filter(pl.col('QTY') < 0).select(pl.col('QTY').sum().abs()).item()
        metrics['total_dispensed'] = total_dispensed
    
    # Total value
    if 'T.P' in df.columns:
        total_value = df.filter(pl.col('QTY') < 0).select(pl.col('T.P').sum().abs()).item()
        metrics['total_value'] = total_value
    
    # Unique drugs
    if 'CODE' in df.columns:
        unique_drugs = df.select(pl.col('CODE').n_unique()).item()
        metrics['unique_drugs'] = unique_drugs
    
    return metrics

