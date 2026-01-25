"""Data transformation and normalization functions."""

from turtle import pd
import polars as pl
from typing import Dict, Optional
from datetime import datetime
import logging
from backend.app.modules.ingestion.schema import FIELD_MAPPINGS

logger = logging.getLogger(__name__)


def transform_dataframe(df: pl.DataFrame, source_file: Optional[str] = None) -> pl.DataFrame:
    """
    Transform raw dataframe to match database schema.
    
    Args:
        df: Raw Polars DataFrame with original column names
        source_file: Optional source file name for tracking
    
    Returns:
        Transformed DataFrame with mapped column names and normalized data
    """
    transformed_df = df.clone()
    
    # Map column names
    rename_dict = {old: new for old, new in FIELD_MAPPINGS.items() if old in transformed_df.columns}
    if rename_dict:
        transformed_df = transformed_df.rename(rename_dict)
        logger.debug(f"Mapped {len(rename_dict)} columns")
    
    # Add source_file column if provided
    if source_file:
        transformed_df = transformed_df.with_columns([
            pl.lit(source_file).alias('source_file')
        ])
    
    return transformed_df


def normalize_drug_code(code: str) -> str:
    """
    Normalize drug code (uppercase, trim whitespace).
    
    Args:
        code: Raw drug code string
    
    Returns:
        Normalized drug code
    """
    if code is None:
        return None
    return str(code).strip().upper()


def parse_date(date_str: str, format_hint: str = 'DD/MM/YY') -> Optional[datetime]:
    """
    Parse date string handling multiple formats.
    
    Args:
        date_str: Date string to parse
        format_hint: Expected format (DD/MM/YY or YYYY-MM-DD)
    
    Returns:
        Parsed datetime or None if invalid
    """
    if date_str is None or date_str == '':
        return None
    
    # Try common formats
    formats = [
        '%d/%m/%y',  # DD/MM/YY
        '%d/%m/%Y',  # DD/MM/YYYY
        '%Y-%m-%d',  # ISO format
        '%d-%m-%Y',  # DD-MM-YYYY
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except (ValueError, AttributeError):
            continue
    
    logger.warning(f"Could not parse date: {date_str}")
    return None


def normalize_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    """
    Apply normalization to dataframe columns.
    
    Args:
        df: DataFrame to normalize
    
    Returns:
        Normalized DataFrame
    """
    normalized_df = df.clone()
    
    # Normalize drug codes
    if 'drug_code' in normalized_df.columns:
        normalized_df = normalized_df.with_columns([
            pl.col('drug_code').map_elements(
                lambda x: normalize_drug_code(x) if x is not None else None,
                return_dtype=pl.String
            ).alias('drug_code')
        ])
    
    # Normalize drug names (trim)
    if 'drug_name' in normalized_df.columns:
        normalized_df = normalized_df.with_columns([
            pl.col('drug_name').str.strip().alias('drug_name')
        ])
    
    # Parse dates
    date_columns = ['transaction_date', 'admission_date']
    for col in date_columns:
        if col in normalized_df.columns:
            normalized_df = normalized_df.with_columns([
                pl.col(col).map_elements(
                    lambda x: parse_date(x),
                    return_dtype=pl.Datetime
                ).alias(col)
            ])
    
    return normalized_df


def prepare_for_database(df: pl.DataFrame, source_file: Optional[str] = None) -> pl.DataFrame:
    """
    Prepare dataframe for database insertion.
    
    - Maps columns to database schema
    - Normalizes data
    - Validates required fields
    - Filters invalid records
    
    Args:
        df: Raw DataFrame
    
    Returns:
        Prepared DataFrame ready for database insertion
    """
    # Transform column names (if not already transformed)
    if any(col in df.columns for col in ['DOC', 'CODE', 'ARTICLE']):  # Still has original column names
        df = transform_dataframe(df, source_file)
    
    # Normalize data
    df = normalize_dataframe(df)
    
    # Filter out records with missing required fields
    required_fields = ['doc_id', 'transaction_date', 'movement_number', 'drug_code', 'drug_name', 'quantity']
    for field in required_fields:
        if field in df.columns:
            df = df.filter(pl.col(field).is_not_null())
    
    # Filter out zero quantities (enforced by database constraint)
    if 'quantity' in df.columns:
        df = df.filter(pl.col('quantity') != 0)
    
    logger.info(f"Prepared {len(df)} valid records for database insertion")
    return df


def calculate_derived_fields(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate derived fields if not present.
    
    Args:
        df: DataFrame to process
    
    Returns:
        DataFrame with derived fields
    """
    df = df.clone()
    
    # Calculate total_price if missing
    if 'total_price' not in df.columns or df['total_price'].null_count() > 0:
        if 'unit_price' in df.columns and 'quantity' in df.columns:
            df = df.with_columns([
                (pl.col('unit_price') * pl.col('quantity')).alias('total_price')
            ])
    
    return df

def create_derived_features(df: pl.DataFrame) -> pl.DataFrame:
    """Create additional derived features"""

    # Cost categories
    try:
        df['cost_category'] = pd.qcut(df['total_price'], q=4,
                                      labels=['Low', 'Medium', 'High', 'Very High'],
                                      duplicates='drop')
    except ValueError:
        # Fallback to cut if qcut fails
        df['cost_category'] = pd.cut(df['total_price'], bins=4,
                                     labels=['Low', 'Medium', 'High', 'Very High'])

    # Quantity categories
    try:
        df['quantity_category'] = pd.qcut(df['quantity'], q=4,
                                          labels=['Low', 'Medium', 'High', 'Very High'],
                                          duplicates='drop')
    except ValueError:
        # Fallback to cut if qcut fails
        df['quantity_category'] = pd.cut(df['quantity'], bins=4,
                                         labels=['Low', 'Medium', 'High', 'Very High'])

    # Transaction flags
    # A new column where a 1 indicates the record is among the most expensive 25% of all entries (based on total_price)
    df['is_high_cost'] = (df['total_price'] > df['total_price'].quantile(0.75)).astype(int)
    # A new column where a 1 indicates the record has a volume/quantity in the top 25% (based on quantity)
    df['is_high_quantity'] = (df['quantity'] >
                              df['quantity'].quantile(0.75)).astype(int)
    
    return df

def extract_time_features(df: pl.DataFrame) -> pl.DataFrame:
    """Extract time-based features"""

    # Time components
    df['year'] = df['transaction_date'].dt.year
    df['month'] = df['transaction_date'].dt.month
    df['month_name'] = df['transaction_date'].dt.month_name()
    df['quarter'] = df['transaction_date'].dt.quarter
    df['day_of_week'] = df['transaction_date'].dt.dayofweek
    df['day_name'] = df['transaction_date'].dt.day_name()
    df['is_weekend'] = df['transaction_date'].isin([5, 6]).astype(int)

    return df

def calculate_age_features(df: pl.DataFrame) -> pl.DataFrame:
    """Calculate age-related features"""
    
    MAX_AGE = 120

    # Calculate age at admission
    df['patient_age_at_admission'] = (
        df['admission_date'] - df['patient_dob']
    ).dt.days / 365.25

    # Clip age to reasonable bounds
    df['patient_age_at_admission'] = df['patient_age_at_admission'].clip(0, MAX_AGE)

    # Create age groups
    age_bins = [0, 18, 30, 40, 50, 60, 70, 80, 90, MAX_AGE]
    age_labels = ['0-18', '19-30', '31-40', '41-50', '51-60',
                  '61-70', '71-80', '81-90', '90+']
    df['age_group'] = pd.cut(df['patient_age_at_admission'],
                             bins=age_bins, labels=age_labels, right=False)

    return df