"""Data transformation and normalization functions."""

import polars as pl
from typing import Dict, Optional
from datetime import datetime, date
import logging
import re
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
    
    logger.info(f"transform_dataframe: Input columns: {transformed_df.columns}")
    
    # Map column names - handle variations like 'MOV#' vs 'MOV #'
    rename_dict = {}
    for old, new in FIELD_MAPPINGS.items():
        if old in transformed_df.columns:
            rename_dict[old] = new
            logger.debug(f"Mapping column: {old} -> {new}")
        # Also check for variations without spaces
        elif old.replace(' ', '') in transformed_df.columns:
            rename_dict[old.replace(' ', '')] = new
            logger.debug(f"Mapping column (no space): {old.replace(' ', '')} -> {new}")
        # Check case-insensitive match
        else:
            # Try case-insensitive match
            for col in transformed_df.columns:
                if col.upper().replace(' ', '') == old.upper().replace(' ', ''):
                    rename_dict[col] = new
                    logger.debug(f"Mapping column (case-insensitive): {col} -> {new}")
                    break
    
    if rename_dict:
        transformed_df = transformed_df.rename(rename_dict)
        logger.info(f"Mapped {len(rename_dict)} columns: {rename_dict}")
    else:
        logger.warning(f"No columns were mapped! Original columns: {transformed_df.columns}")
    
    logger.info(f"transform_dataframe: Output columns: {transformed_df.columns}")
    
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


def standardize_date(date_input) -> Optional[str]:
    """
    Standardize date input to YYYY-MM-DD format, handling various formats and invalid dates.
    
    Args:
        date_input: Date input (string, datetime, or None)
    
    Returns:
        Standardized date string in YYYY-MM-DD format, or None if invalid
    """
    # Handle None, empty strings, and pandas/polars null values
    if date_input is None or date_input == '' or str(date_input).strip() == '':
        return None
    
    # Handle datetime objects
    if isinstance(date_input, datetime):
        return date_input.strftime('%Y-%m-%d')
    
    if isinstance(date_input, date):
        return date_input.strftime('%Y-%m-%d')
    
    # Convert to string and strip whitespace
    date_string = str(date_input).strip()
    
    # Check for invalid date patterns
    invalid_patterns = ['00/00/00', '0000/00/00', '0000-00-00', '00-00-00']
    if any(invalid in date_string for invalid in invalid_patterns):
        return None
    
    # Check for invalid numeric-only dates
    if date_string in ['0', '00', '000', '0000', '00000', '000000']:
        return None
    
    # Pattern matching for various date formats
    patterns = [
        (r'^(\d{1,2})/(\d{1,2})/\s*(\d{2})$', 'dd/mm/yy'),  # 'dd/mm/ yy'
        (r'^(\d{1,2})/(\d{1,2})/(\d{2})$', 'dd/mm/yy'),      # 'dd/mm/yy'
        (r'^(\d{1,2})/(\d{1,2})/(\d{4})$', 'dd/mm/yyyy'),   # 'dd/mm/yyyy'
        (r'^(\d{4})-(\d{1,2})-(\d{1,2})$', 'yyyy-mm-dd'),   # 'yyyy-mm-dd'
        (r'^(\d{4})/(\d{1,2})/(\d{1,2})$', 'yyyy/mm/dd')    # 'yyyy/mm/dd'
    ]
    
    for pattern, format_type in patterns:
        match = re.match(pattern, date_string)
        if match:
            groups = match.groups()
            try:
                if format_type in ['yyyy-mm-dd', 'yyyy/mm/dd']:
                    # Year-first formats
                    year, month, day = groups
                    year = int(year)
                    month = int(month)
                    day = int(day)
                else:
                    # Day-first formats (dd/mm/yy or dd/mm/yyyy)
                    day, month, year_str = groups
                    day = int(day)
                    month = int(month)
                    
                    if len(year_str) == 2:
                        # Two-digit year: assume 00-69 = 2000-2069, 70-99 = 1970-1999
                        year = int(year_str)
                        if year <= 69:
                            year += 2000
                        else:
                            year += 1900
                    else:
                        year = int(year_str)
                
                # Validate month and day ranges
                if month == 0 or day == 0 or year == 0:
                    return None
                if month > 12 or day > 31:
                    return None
                
                # Create date object to validate (handles invalid dates like Feb 30)
                date_obj = datetime(year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            except (ValueError, TypeError) as e:
                logger.debug(f"Invalid date components: {date_string} - {e}")
                continue
    
    # Fallback: try standard date formats
    standard_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y']
    for fmt in standard_formats:
        try:
            date_obj = datetime.strptime(date_string, fmt)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    logger.debug(f"Could not standardize date: {date_string}")
    return None


def parse_date(date_str: str, format_hint: str = 'DD/MM/YY') -> Optional[datetime]:
    """
    Parse date string handling multiple formats.
    Uses standardize_date internally for robust parsing.
    
    Args:
        date_str: Date string to parse
        format_hint: Expected format (DD/MM/YY or YYYY-MM-DD) - kept for compatibility
    
    Returns:
        Parsed datetime or None if invalid
    """
    standardized = standardize_date(date_str)
    if standardized:
        try:
            return datetime.strptime(standardized, '%Y-%m-%d')
        except ValueError:
            return None
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
                return_dtype=pl.Utf8
            ).alias('drug_code')
        ])
    
    # Normalize drug names (trim)
    if 'drug_name' in normalized_df.columns:
        normalized_df = normalized_df.with_columns([
            pl.col('drug_name').str.strip().alias('drug_name')
        ])
    
    # Parse and standardize dates using the robust standardize_date function
    date_columns = ['transaction_date', 'admission_date', 'DATE', 'AD DATE']
    for col in date_columns:
        if col in normalized_df.columns:
            normalized_df = normalized_df.with_columns([
                pl.col(col).map_elements(
                    lambda x: parse_date(standardize_date(x)) if standardize_date(x) else None,
                    return_dtype=pl.Datetime
                ).alias(col)
            ])
    
    return normalized_df


def prepare_for_database(df: pl.DataFrame, source_file: Optional[str] = None) -> pl.DataFrame:
    """
    Prepare dataframe for database insertion.
    
    - Maps columns to database schema (if not already done)
    - Normalizes data
    - NOTE: Field validation is done in validate_data_integrity, not here
    
    Args:
        source_file: Optional source file name
        df: Raw DataFrame
    
    Returns:
        Prepared DataFrame ready for database insertion
    """
    # Transform column names (if not already transformed)
    logger.debug(f"prepare_for_database: Input columns: {df.columns}")
    if any(col in df.columns for col in ['DOC', 'CODE', 'ARTICLE']):  # Still has original column names
        logger.info(f"Transforming column names (found original columns)")
        df = transform_dataframe(df, source_file)
        logger.debug(f"After transform_dataframe: Columns: {df.columns}")
    
    # Normalize data
    df = normalize_dataframe(df)
    
    # Log field status for debugging (but don't filter here - validation does that)
    required_fields = ['doc_id', 'transaction_date', 'movement_number', 'drug_code', 'drug_name', 'quantity']
    original_count = len(df)
    logger.info(f"prepare_for_database: Starting with {original_count} records")
    
    # Check which required fields exist and log their null counts
    for field in required_fields:
        if field in df.columns:
            null_count = df[field].null_count()
            logger.info(f"prepare_for_database: Field {field} - {null_count} null values out of {original_count} records")
        else:
            logger.warning(f"prepare_for_database: Required field {field} not found in dataframe columns")
    
    # NOTE: Filtering is done in validate_data_integrity, not here to avoid duplication
    # Only filter zero quantities here (database constraint)
    if 'quantity' in df.columns:
        before_count = len(df)
        zero_qty_count = df.filter(pl.col('quantity') == 0).height
        if zero_qty_count > 0:
            logger.info(f"prepare_for_database: Found {zero_qty_count} records with zero quantity (will be filtered)")
            df = df.filter(pl.col('quantity') != 0)
    
    logger.info(f"Prepared {len(df)} records for database insertion (from {original_count} original)")
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

