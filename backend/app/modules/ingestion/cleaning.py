"""Data cleaning and quality checks."""

import polars as pl
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def check_missing_values(df: pl.DataFrame) -> Dict:
    """
    Check for missing values in the dataframe.
    
    Returns:
        Dictionary with missing value counts per column
    """
    missing_counts = {}
    for col in df.columns:
        null_count = df[col].null_count()
        if null_count > 0:
            missing_counts[col] = {
                'count': null_count,
                'percentage': (null_count / len(df)) * 100
            }
    return missing_counts


def check_duplicates(df: pl.DataFrame, subset: Optional[List[str]] = None) -> Dict:
    """
    Check for duplicate rows.
    
    Args:
        df: Polars DataFrame
        subset: Columns to consider for duplicates (all columns if None)
    
    Returns:
        Dictionary with duplicate information
    """
    if subset:
        duplicate_count = df.select(pl.col(subset)).is_duplicated().sum()
    else:
        duplicate_count = df.is_duplicated().sum()
    
    return {
        'duplicate_rows': duplicate_count,
        'percentage': (duplicate_count / len(df)) * 100 if len(df) > 0 else 0
    }


def detect_outliers(df: pl.DataFrame, column: str, method: str = 'iqr') -> List[int]:
    """
    Detect outliers using IQR or Z-score method.
    
    Args:
        df: Polars DataFrame
        column: Column name to check
        method: 'iqr' or 'zscore'
    
    Returns:
        List of row indices with outliers
    """
    if column not in df.columns:
        return []
    
    col_data = df[column]
    
    if method == 'iqr':
        q1 = col_data.quantile(0.25)
        q3 = col_data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outlier_mask = (col_data < lower_bound) | (col_data > upper_bound)
        outlier_indices = df.filter(outlier_mask).select(pl.first().row_nr()).to_series().to_list()
    
    elif method == 'zscore':
        mean = col_data.mean()
        std = col_data.std()
        z_scores = (col_data - mean) / std
        outlier_mask = (z_scores.abs() > 3)
        outlier_indices = df.filter(outlier_mask).select(pl.first().row_nr()).to_series().to_list()
    
    else:
        return []
    
    return outlier_indices


def validate_data_types(df: pl.DataFrame, schema: Dict[str, str]) -> Dict:
    """
    Validate data types against expected schema.
    
    Args:
        df: Polars DataFrame
        schema: Dictionary mapping column names to expected types
    
    Returns:
        Dictionary with validation results
    """
    validation_results = {}
    
    for col, expected_type in schema.items():
        if col not in df.columns:
            validation_results[col] = {'status': 'missing', 'message': 'Column not found'}
            continue
        
        actual_type = str(df[col].dtype)
        if actual_type == expected_type or _type_compatible(actual_type, expected_type):
            validation_results[col] = {'status': 'valid', 'actual': actual_type}
        else:
            validation_results[col] = {
                'status': 'invalid',
                'expected': expected_type,
                'actual': actual_type
            }
    
    return validation_results


def _type_compatible(actual: str, expected: str) -> bool:
    """Check if types are compatible."""
    type_mapping = {
        'int32': ['int64', 'float64'],
        'int64': ['float64'],
        'float64': []
    }
    return expected in type_mapping.get(actual, [])


def generate_quality_report(df: pl.DataFrame) -> Dict:
    """
    Generate comprehensive data quality report.
    
    Args:
        df: Polars DataFrame
    
    Returns:
        Dictionary with quality report
    """
    report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': check_missing_values(df),
        'duplicates': check_duplicates(df),
        'column_info': {}
    }
    
    for col in df.columns:
        col_info = {
            'dtype': str(df[col].dtype),
            'null_count': df[col].null_count(),
            'null_percentage': (df[col].null_count() / len(df)) * 100
        }
        
        if df[col].dtype in [pl.Int64, pl.Float64]:
            col_info['min'] = df[col].min()
            col_info['max'] = df[col].max()
            col_info['mean'] = df[col].mean()
        
        report['column_info'][col] = col_info
    
    return report


def clean_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    """
    Apply basic cleaning operations.
    
    Args:
        df: Polars DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    cleaned_df = df.clone()
    
    # Remove completely duplicate rows
    cleaned_df = cleaned_df.unique()
    
    logger.info(f"Cleaned dataframe: {len(cleaned_df)} rows (removed {len(df) - len(cleaned_df)} duplicates)")
    
    return cleaned_df

