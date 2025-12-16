"""Data cleaning and quality checks."""

import polars as pl
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
import logging
import re

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


def clean_excel_dataframe(df: pl.DataFrame) -> pl.DataFrame:
    """
    Apply Excel-specific cleaning operations.
    
    Args:
        df: Polars DataFrame from Excel file
    
    Returns:
        Cleaned DataFrame
    """
    cleaned_df = df.clone()
    original_rows = len(cleaned_df)
    
    # Remove rows where all values are null
    cleaned_df = cleaned_df.filter(
        pl.concat_list([pl.col(col).is_not_null() for col in cleaned_df.columns]).list.sum() > 0
    )
    
    # Strip whitespace from all string columns
    # Use try/except on each column to avoid pl.String attribute errors
    # Don't access schema directly as it may trigger internal pl.String access
    for col in cleaned_df.columns:
        try:
            # Try string strip operation - if it works, column is a string type
            cleaned_df = cleaned_df.with_columns([
                pl.col(col).str.strip().alias(col)
            ])
        except (AttributeError, TypeError, Exception) as e:
            # Column doesn't support string operations, skip it
            # This includes cases where Polars internally tries to access pl.String
            pass
    
    # Remove empty string values (convert to null)
    for col in cleaned_df.columns:
        try:
            # Try string operations - if it works, process the column
            cleaned_df = cleaned_df.with_columns([
                pl.when(pl.col(col).str.strip_chars() == "")
                .then(None)
                .otherwise(pl.col(col))
                .alias(col)
            ])
        except (AttributeError, TypeError, Exception):
            # Column doesn't support string operations, skip it
            pass
    
    rows_removed = original_rows - len(cleaned_df)
    if rows_removed > 0:
        logger.info(f"Excel cleaning: removed {rows_removed} empty rows")
    
    return cleaned_df


def coerce_data_types(df: pl.DataFrame) -> Tuple[pl.DataFrame, Dict]:
    """
    Coerce data types to expected formats.
    
    Args:
        df: Polars DataFrame
    
    Returns:
        Tuple of (cleaned DataFrame, conversion statistics)
    """
    from backend.app.modules.ingestion.transformation import standardize_date, parse_date
    
    cleaned_df = df.clone()
    conversion_stats = {'numeric_conversions': 0, 'date_conversions': 0, 'integer_validations': 0, 'errors': []}
    
    # Helper functions
    def clean_ad_date(value):
        """Clean corrupted AD DATE values."""
        if not value:
            return None
        value_str = str(value).strip()
        if re.match(r'^\d+\s+(00/00/00|0000/00/00|0000-00-00)$', value_str):
            return None
        return standardize_date(value_str)
    
    def normalize_doc_id(value):
        """Normalize doc_id to integer."""
        if not value:
            return None
        value_str = str(value).strip()
        try:
            return int(float(value_str))
        except (ValueError, TypeError):
            match = re.search(r'\d+', value_str)
            return int(match.group()) if match else abs(hash(value_str)) % (10**9)
    
    def normalize_bed_number(value):
        """Convert Arabic bed letters to English or preserve numbers."""
        if not value:
            return None
        value_str = str(value).strip()
        arabic_map = {'أ': 'A', 'ا': 'A', 'ب': 'B'}
        for arabic, english in arabic_map.items():
            if arabic in value_str:
                return english
        if value_str.upper() in ['A', 'B']:
            return value_str.upper()
        try:
            return str(int(float(value_str)))
        except (ValueError, TypeError):
            return value_str
    
    # Process date fields
    for col in ['AD DATE', 'admission_date']:
        if col in cleaned_df.columns:
            cleaned_df = cleaned_df.with_columns([
                pl.col(col).map_elements(clean_ad_date, return_dtype=pl.Utf8).alias(col)
            ]).with_columns([
                pl.col(col).map_elements(lambda x: parse_date(x) if x else None, return_dtype=pl.Datetime).alias(col)
            ])
            conversion_stats['date_conversions'] += 1
    
    for col in ['DATE', 'transaction_date']:
        if col in cleaned_df.columns:
            cleaned_df = cleaned_df.with_columns([
                pl.col(col).map_elements(standardize_date, return_dtype=pl.Utf8).alias(col)
            ]).with_columns([
                pl.col(col).map_elements(lambda x: parse_date(x) if x else None, return_dtype=pl.Datetime).alias(col)
            ])
            conversion_stats['date_conversions'] += 1
    
    # Process bed numbers
    for col in ['U', 'bed_number']:
        if col in cleaned_df.columns:
            cleaned_df = cleaned_df.with_columns([
                pl.col(col).map_elements(normalize_bed_number, return_dtype=pl.Utf8).alias(col)
            ])
            conversion_stats['integer_validations'] += 1
    
    # Process integer fields
    for col in ['LINE', 'CAT', 'C.R', 'MOV #', 'C.S', 'QTY', 'R']:
        if col in cleaned_df.columns:
            cleaned_df = cleaned_df.with_columns([
                pl.col(col).cast(pl.Int64, strict=False).alias(col)
            ])
            conversion_stats['integer_validations'] += 1
    
    # Process doc_id
    for col in ['DOC', 'doc_id']:
        if col in cleaned_df.columns:
            cleaned_df = cleaned_df.with_columns([
                pl.col(col).map_elements(normalize_doc_id, return_dtype=pl.Int64).alias(col)
            ])
            conversion_stats['integer_validations'] += 1
    
    # Process price fields
    for col in ['U.P', 'T.P', 'unit_price', 'total_price']:
        if col in cleaned_df.columns:
            try:
                cleaned_df = cleaned_df.with_columns([
                    pl.col(col).str.replace_all(r'[^\d.]', '').cast(pl.Float64, strict=False).alias(col)
                ])
            except (AttributeError, TypeError):
                cleaned_df = cleaned_df.with_columns([
                    pl.col(col).cast(pl.Float64, strict=False).alias(col)
                ])
            conversion_stats['numeric_conversions'] += 1
    
    return cleaned_df, conversion_stats


def validate_data_integrity(df: pl.DataFrame) -> Tuple[pl.DataFrame, Dict]:
    """
    Validate data integrity and filter invalid records.
    
    Args:
        df: Polars DataFrame
    
    Returns:
        Tuple of (validated DataFrame, validation results)
    """
    validated_df = df.clone()
    original_rows = len(validated_df)
    validation_results = {'invalid_records': 0, 'invalid_reasons': {}, 'suspicious_patterns': []}
    
    # Generate doc_id if missing
    doc_cols = ['DOC', 'doc_id']
    doc_col = next((col for col in doc_cols if col in validated_df.columns), None)
    if doc_col and validated_df[doc_col].null_count() == original_rows:
        validated_df = validated_df.with_columns([(pl.int_range(pl.len()) + 1).alias(doc_col)])
    elif not doc_col:
        validated_df = validated_df.with_columns([(pl.int_range(pl.len()) + 1).alias('doc_id')])
    
    # Validate required fields
    required_fields = [
        (['DATE', 'transaction_date'], 'date'),
        (['MOV #', 'MOV#', 'movement_number'], 'mov'),
        (['CODE', 'drug_code'], 'code'),
        (['ARTICLE', 'drug_name'], 'article'),
        (['QTY', 'quantity'], 'qty')
    ]
    
    for field_group, field_key in required_fields:
        field = next((f for f in field_group if f in validated_df.columns), None)
        if not field:
            validation_results['invalid_reasons'][f'{field_key}_missing'] = original_rows
            continue
        
        before = len(validated_df)
        null_count = validated_df[field].null_count()
        
        if null_count == before:
            validation_results['invalid_reasons'][f'{field_key}_all_null'] = before
        else:
            validated_df = validated_df.filter(pl.col(field).is_not_null())
            removed = before - len(validated_df)
            if removed > 0:
                validation_results['invalid_records'] += removed
                validation_results['invalid_reasons'][f'{field_key}_null'] = removed
    
    # Validate date ranges
    for field in ['DATE', 'transaction_date']:
        if field in validated_df.columns and isinstance(validated_df[field].dtype, (pl.Datetime, pl.Date)):
            before = len(validated_df)
            validated_df = validated_df.filter(
                pl.col(field).is_null() |
                ((pl.col(field) >= pl.date(2010, 1, 1)) & (pl.col(field) <= pl.date(2030, 12, 31)))
            )
            removed = before - len(validated_df)
            if removed > 0:
                validation_results['invalid_records'] += removed
                validation_results['invalid_reasons'][f'{field}_out_of_range'] = removed
    
    # Set invalid optional dates to NULL
    for field in ['AD DATE', 'admission_date']:
        if field in validated_df.columns and isinstance(validated_df[field].dtype, (pl.Datetime, pl.Date)):
            validated_df = validated_df.with_columns([
                pl.when(
                    pl.col(field).is_not_null() &
                    ~((pl.col(field) >= pl.date(2010, 1, 1)) & (pl.col(field) <= pl.date(2030, 12, 31)))
                ).then(None).otherwise(pl.col(field)).alias(field)
            ])
    
    # Filter zero quantities
    qty_field = next((f for f in ['QTY', 'quantity'] if f in validated_df.columns), None)
    if qty_field:
        if not isinstance(validated_df[qty_field].dtype, (pl.Int64, pl.Int32, pl.Float64, pl.Float32)):
            validated_df = validated_df.with_columns([
                pl.col(qty_field).cast(pl.Float64, strict=False).alias(qty_field)
            ])
        
        before = len(validated_df)
        validated_df = validated_df.filter(pl.col(qty_field).is_null() | (pl.col(qty_field) != 0))
        removed = before - len(validated_df)
        if removed > 0:
            validation_results['invalid_records'] += removed
            validation_results['invalid_reasons'][f'{qty_field}_zero'] = removed
    
    # Check suspicious patterns
    if qty_field and isinstance(validated_df[qty_field].dtype, (pl.Int64, pl.Int32, pl.Float64, pl.Float32)):
        suspicious = validated_df.filter(pl.col(qty_field).abs() > 10000)
        if len(suspicious) > 0:
            validation_results['suspicious_patterns'].append({
                'type': 'high_quantity',
                'count': len(suspicious),
                'max_value': validated_df[qty_field].max()
            })
    
    price_field = next((f for f in ['T.P', 'total_price'] if f in validated_df.columns), None)
    if price_field and isinstance(validated_df[price_field].dtype, (pl.Int64, pl.Int32, pl.Float64, pl.Float32)):
        suspicious = validated_df.filter(pl.col(price_field) > 100000)
        if len(suspicious) > 0:
            validation_results['suspicious_patterns'].append({
                'type': 'high_price',
                'count': len(suspicious),
                'max_value': validated_df[price_field].max()
            })
    
    removed = original_rows - len(validated_df)
    if removed > 0:
        logger.info(f"Data validation: removed {removed} invalid records")
    
    return validated_df, validation_results


def verify_data_consistency(df: pl.DataFrame) -> Tuple[pl.DataFrame, Dict]:
    """
    Verify data consistency and auto-correct where possible.
    
    Args:
        df: Polars DataFrame
    
    Returns:
        Tuple of (corrected DataFrame, consistency check results)
    """
    corrected_df = df.clone()
    consistency_results = {
        'price_mismatches_corrected': 0,
        'age_normalizations': 0,
        'date_inconsistencies': 0,
        'errors': []
    }
    
    # Verify total_price matches unit_price × quantity (with tolerance)
    price_fields = {
        'unit': ['U.P', 'unit_price'],
        'total': ['T.P', 'total_price'],
        'qty': ['QTY', 'quantity']
    }
    
    unit_price_col = None
    total_price_col = None
    qty_col = None
    
    for col in corrected_df.columns:
        if col in price_fields['unit']:
            unit_price_col = col
        elif col in price_fields['total']:
            total_price_col = col
        elif col in price_fields['qty']:
            qty_col = col
    
    if unit_price_col and total_price_col and qty_col:
        try:
            # Calculate expected total price
            expected_total = pl.col(unit_price_col) * pl.col(qty_col).abs()
            actual_total = pl.col(total_price_col)
            
            # Find mismatches (tolerance: ±0.01)
            mismatch_mask = (actual_total - expected_total).abs() > 0.01
            
            if mismatch_mask.sum() > 0:
                # Recalculate total_price from unit_price × quantity
                corrected_df = corrected_df.with_columns([
                    pl.when(mismatch_mask)
                    .then(expected_total)
                    .otherwise(actual_total)
                    .alias(total_price_col)
                ])
                consistency_results['price_mismatches_corrected'] = mismatch_mask.sum()
                logger.info(f"Corrected {mismatch_mask.sum()} price mismatches")
        except Exception as e:
            consistency_results['errors'].append(f"Error correcting prices: {e}")
    
    # Normalize date_of_birth - parse dates and standardize format (store as date, not age)
    birth_date_fields = ['AGE', 'date_of_birth']
    for birth_field in birth_date_fields:
        if birth_field in corrected_df.columns:
            try:
                # Log sample values before normalization
                sample_values = corrected_df[birth_field].head(10).to_list()
                null_count_before = corrected_df[birth_field].null_count()
                logger.info(f"Normalizing {birth_field} (date of birth): {null_count_before} null values, sample values: {sample_values}")
                
                # Use standardize_date from transformation module for date standardization
                from backend.app.modules.ingestion.transformation import standardize_date
                
                def normalize_birth_date(date_str):
                    """Parse and standardize birth date from various formats."""
                    if date_str is None:
                        return None
                    date_str = str(date_str).strip()
                    if not date_str:
                        return None
                    
                    # Handle corrupted formats like "ب 0000/00/00" - Arabic letter + invalid date
                    arabic_letter_match = re.match(r'^([أاببتثجحخدذرزسشصضطظعغفقكلمنهوي])\s*(0000/00/00|00/00/00|0000-00-00)', date_str)
                    if arabic_letter_match:
                        logger.debug(f"Found corrupted birth date with Arabic letter: {date_str}")
                        return None
                    
                    # Use standardize_date to parse the date
                    standardized = standardize_date(date_str)
                    if standardized:
                        return standardized
                    
                    # If standardize_date failed, try to extract numeric age and convert to approximate birth year
                    # This handles cases like "25 سنة" (25 years old)
                    arabic_patterns = [
                        r'سنة', r'عام', r'عمر', r'س',  # Arabic words for year/age
                        r'year', r'years', r'yr', r'yrs',  # English words
                        r'age', r'aged'
                    ]
                    cleaned_str = date_str
                    for pattern in arabic_patterns:
                        cleaned_str = re.sub(pattern, '', cleaned_str, flags=re.IGNORECASE)
                    
                    # Remove invalid date patterns
                    cleaned_str = re.sub(r'\s*(0000/00/00|00/00/00|0000-00-00)', '', cleaned_str)
                    
                    # Extract numeric age if present
                    match = re.search(r'\d+', cleaned_str)
                    if match:
                        age = int(match.group())
                        if 0 <= age <= 150:
                            # Convert age to approximate birth year (using 2019 as reference)
                            # Store as January 1st of birth year
                            birth_year = 2019 - age
                            return f"{birth_year}-01-01"
                    
                    return None
                
                # Standardize dates to YYYY-MM-DD format
                corrected_df = corrected_df.with_columns([
                    pl.col(birth_field).map_elements(
                        normalize_birth_date,
                        return_dtype=pl.Utf8
                    ).alias(birth_field)
                ])
                
                # Convert standardized date strings to date objects
                # First, check how many non-null values we have before conversion
                non_null_before = corrected_df[birth_field].is_not_null().sum()
                logger.info(f"Before date conversion: {non_null_before} non-null {birth_field} values")
                
                # Convert to date objects - use strict=False to handle invalid dates gracefully
                corrected_df = corrected_df.with_columns([
                    pl.col(birth_field).str.strptime(pl.Date, format='%Y-%m-%d', strict=False).alias(birth_field)
                ])
                
                # Check how many non-null values we have after conversion
                non_null_after = corrected_df[birth_field].is_not_null().sum()
                logger.info(f"After date conversion: {non_null_after} non-null {birth_field} values")
                
                # Log sample values to see what we have
                sample_dates = corrected_df[birth_field].filter(pl.col(birth_field).is_not_null()).head(5).to_list()
                if sample_dates:
                    logger.info(f"Sample {birth_field} date objects: {sample_dates}")
                
                # Log results after normalization
                null_count_after = corrected_df[birth_field].null_count()
                non_null_count = corrected_df[birth_field].is_not_null().sum()  # Fixed: use is_not_null() not not_null()
                sample_values_after = corrected_df.filter(pl.col(birth_field).is_not_null())[birth_field].head(10).to_list()
                logger.info(f"After normalizing {birth_field}: {null_count_after} null values, {non_null_count} non-null values")
                if sample_values_after:
                    logger.info(f"Sample normalized birth dates: {sample_values_after}")
                
                consistency_results['age_normalizations'] = non_null_count  # Keep same key for compatibility
            except Exception as e:
                consistency_results['errors'].append(f"Error normalizing birth date: {e}")
                logger.error(f"Error normalizing birth date: {e}", exc_info=True)
    
    # Check for logical inconsistencies (admission_date after transaction_date)
    date_pairs = [
        ('AD DATE', 'DATE'),
        ('admission_date', 'transaction_date')
    ]
    
    for ad_field, tx_field in date_pairs:
        if ad_field in corrected_df.columns and tx_field in corrected_df.columns:
            try:
                inconsistencies = corrected_df.filter(
                    pl.col(ad_field) > pl.col(tx_field)
                )
                if len(inconsistencies) > 0:
                    consistency_results['date_inconsistencies'] = len(inconsistencies)
                    logger.warning(f"Found {len(inconsistencies)} date inconsistencies "
                                 f"({ad_field} after {tx_field})")
            except Exception as e:
                consistency_results['errors'].append(f"Error checking date consistency: {e}")
    
    return corrected_df, consistency_results


def generate_quality_report(df: pl.DataFrame, cleaning_stats: Optional[Dict] = None, 
                           validation_results: Optional[Dict] = None,
                           consistency_results: Optional[Dict] = None) -> Dict:
    """
    Generate comprehensive data quality report.
    
    Args:
        df: Polars DataFrame
        cleaning_stats: Optional cleaning statistics
        validation_results: Optional validation results
        consistency_results: Optional consistency check results
    
    Returns:
        Dictionary with quality report
    """
    report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': check_missing_values(df),
        'duplicates': check_duplicates(df),
        'column_info': {},
        'cleaning_stats': cleaning_stats or {},
        'validation_results': validation_results or {},
        'consistency_results': consistency_results or {}
    }
    
    for col in df.columns:
        col_info = {
            'dtype': str(df[col].dtype),
            'null_count': df[col].null_count(),
            'null_percentage': (df[col].null_count() / len(df)) * 100 if len(df) > 0 else 0
        }
        
        if df[col].dtype in [pl.Int64, pl.Float64]:
            col_info['min'] = df[col].min()
            col_info['max'] = df[col].max()
            col_info['mean'] = df[col].mean()
        
        report['column_info'][col] = col_info
    
    return report

