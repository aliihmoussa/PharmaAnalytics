"""Data ingestion module using Polars for efficient file loading."""

import polars as pl
from pathlib import Path
from typing import List, Optional, Union, Iterator
import logging
import pandas as pd
import re
import io

logger = logging.getLogger(__name__)


class IngestionLoader:
    """Class for loading and processing data files."""
    
    def __init__(self):
        """Initialize the ingestion loader."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_file(self, file_path: Union[str, Path], separator: str = None) -> pl.DataFrame:
        """
        Load a data file using Polars.
        
        Args:
            file_path: Path to the data file
            separator: File separator (auto-detect if None)
        
        Returns:
            Polars DataFrame
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Try to auto-detect separator and read
            if separator:
                df = pl.read_csv(file_path, separator=separator, encoding='utf-8')
            else:
                # Try common separators
                for sep in ['\t', ';', ',', ' ']:
                    try:
                        df = pl.read_csv(file_path, separator=sep, encoding='utf-8')
                        if len(df.columns) > 1:
                            self.logger.info(f"Auto-detected separator: '{sep}'")
                            break
                    except:
                        continue
                else:
                    # Default to tab-separated (common for this dataset)
                    df = pl.read_csv(file_path, separator='\t', encoding='utf-8')
            
            self.logger.info(f"Loaded {len(df)} rows from {file_path.name}")
            return df
        
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            raise
    
    def load_multiple_files(self, file_paths: List[Union[str, Path]], separator: str = None) -> pl.DataFrame:
        """
        Load multiple files and concatenate them.
        
        Args:
            file_paths: List of file paths
            separator: File separator (auto-detect if None)
        
        Returns:
            Combined Polars DataFrame
        """
        dataframes = []
        
        for file_path in file_paths:
            df = self.load_file(file_path, separator)
            df = df.with_columns([
                pl.lit(str(file_path)).alias('source_file')
            ])
            dataframes.append(df)
        
        if not dataframes:
            raise ValueError("No files loaded")
        
        # Combine all dataframes
        combined_df = pl.concat(dataframes)
        self.logger.info(f"Combined {len(file_paths)} files into {len(combined_df)} total rows")
        
        return combined_df
    
    def get_file_info(self, df: pl.DataFrame) -> dict:
        """
        Get basic information about the loaded dataframe.
        
        Args:
            df: Polars DataFrame
        
        Returns:
            Dictionary with file information
        """
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': df.columns,
            'dtypes': {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)},
            'memory_usage': df.estimated_size() if hasattr(df, 'estimated_size') else None
        }
    
    def detect_file_type(self, file_path: Union[str, Path]) -> str:
        """
        Detect file type based on extension.
        
        Args:
            file_path: Path to the file
        
        Returns:
            File type: 'excel', 'csv', or 'unknown'
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension in ['.xlsx', '.xls']:
            return 'excel'
        elif extension in ['.csv', '.txt', '.tsv', '.dat']:
            return 'csv'
        else:
            return 'unknown'
    
    def load_excel_file(self, file_path: Union[str, Path], sheet_name: Optional[str] = None, header_row: int = 0) -> pl.DataFrame:
        """
        Load an Excel file using pandas and convert to Polars DataFrame.
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Name of sheet to read (None = first sheet)
            header_row: Row number to use as header (0-indexed)
        
        Returns:
            Polars DataFrame
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Determine engine based on file extension
            file_ext = file_path.suffix.lower()
            if file_ext == '.xlsx':
                engine = 'openpyxl'
            elif file_ext == '.xls':
                engine = 'xlrd'
            else:
                # Default to openpyxl for unknown extensions
                engine = 'openpyxl'
            
            # Read Excel file with pandas, force string dtype to avoid type inference
            # Explicitly specify engine to avoid auto-detection issues
            try:
                if sheet_name:
                    df_pandas = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, dtype=str, engine=engine)
                else:
                    # Read first sheet by default
                    df_pandas = pd.read_excel(file_path, header=header_row, dtype=str, engine=engine)
            except ImportError as e:
                if 'openpyxl' in str(e) or engine == 'openpyxl':
                    raise ImportError(
                        f"Missing required dependency 'openpyxl' for reading .xlsx files. "
                        f"Install it with: pip install openpyxl"
                    ) from e
                elif 'xlrd' in str(e) or engine == 'xlrd':
                    raise ImportError(
                        f"Missing required dependency 'xlrd' for reading .xls files. "
                        f"Install it with: pip install xlrd"
                    ) from e
                raise
            
            # Identify and log corrupted rows before processing
            corrupted_rows = self._identify_corrupted_rows(df_pandas)
            if len(corrupted_rows) > 0:
                self.logger.warning(
                    f"Identified {len(corrupted_rows)} corrupted rows, will skip them during processing"
                )
                # Remove corrupted rows
                df_pandas = df_pandas.drop(corrupted_rows)
            
            # Clean control characters and escape sequences BEFORE any type conversion
            df_pandas = self._clean_control_characters(df_pandas)
            
            # Replace 'nan' strings (from actual NaN values) with None for proper null handling
            df_pandas = df_pandas.replace('nan', None, regex=False)
            df_pandas = df_pandas.replace('NaN', None, regex=False)
            df_pandas = df_pandas.replace('None', None, regex=False)
            
            # Replace empty strings and whitespace-only strings with None
            df_pandas = df_pandas.replace(r'^\s*$', None, regex=True)
            
            # Ensure all columns are explicitly string type before conversion
            for col in df_pandas.columns:
                try:
                    df_pandas[col] = df_pandas[col].astype(str)
                    # Convert 'None' strings back to actual None
                    df_pandas.loc[df_pandas[col] == 'None', col] = None
                except Exception as e:
                    self.logger.warning(f"Error converting column {col} to string: {e}, setting to None")
                    df_pandas[col] = None
            
            # Convert to Polars DataFrame - force all columns to strings initially
            # to prevent type inference errors with mixed-type data
            schema_overrides = {col: pl.Utf8 for col in df_pandas.columns}
            
            try:
                df = pl.from_pandas(df_pandas, schema_overrides=schema_overrides)
            except Exception as e:
                # Fallback 1: Try CSV conversion
                try:
                    self.logger.warning(f"Direct pandas conversion failed, trying CSV fallback: {e}")
                    csv_buffer = io.StringIO()
                    df_pandas.to_csv(csv_buffer, index=False, sep='\t')
                    csv_buffer.seek(0)
                    df = pl.read_csv(csv_buffer, separator='\t', schema_overrides=schema_overrides)
                except Exception as e2:
                    # Fallback 2: Convert row by row, skipping problematic rows
                    self.logger.warning(
                        f"CSV conversion also failed, converting row-by-row and skipping errors: {e2}"
                    )
                    df = self._convert_pandas_to_polars_safe(df_pandas, schema_overrides)
            
            self.logger.info(f"Loaded {len(df)} rows from Excel file {file_path.name}")
            return df
        
        except Exception as e:
            self.logger.error(f"Error loading Excel file {file_path}: {e}")
            raise
    
    def _clean_control_characters(self, df_pandas: pd.DataFrame) -> pd.DataFrame:
        """
        Remove control characters and escape sequences from DataFrame.
        
        This prevents PyArrow from trying to convert corrupted string data to numeric types.
        
        Args:
            df_pandas: Pandas DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        df_cleaned = df_pandas.copy()
        
        # Pattern to match ANSI escape sequences and control characters
        # Matches: \x1B, \x00-\x1F (control chars), \x7F-\x9F (extended control chars),
        # and patterns like '_x001B_' or '\x1B'
        control_char_pattern = re.compile(r'[\x00-\x1F\x7F-\x9F]|_x[0-9A-Fa-f]{4}_|\\x[0-9A-Fa-f]{2}')
        
        for col in df_cleaned.columns:
            # Process all columns as strings (they should already be strings from dtype=str)
            # Replace control characters and escape sequences with empty string or None
            try:
                df_cleaned[col] = df_cleaned[col].astype(str).apply(
                    lambda x: None if pd.isna(x) or str(x) in ['nan', 'None', ''] 
                    else (re.sub(control_char_pattern, '', str(x)).strip() or None)
                )
            except Exception as e:
                self.logger.warning(f"Error cleaning column {col}, setting to None: {e}")
                df_cleaned[col] = None
        
        return df_cleaned
    
    def _identify_corrupted_rows(self, df_pandas: pd.DataFrame) -> pd.Index:
        """
        Identify rows that contain corrupted data that might cause conversion errors.
        
        Args:
            df_pandas: Pandas DataFrame
        
        Returns:
            Index of rows to skip
        """
        corrupted_rows = []
        
        # Pattern to detect problematic escape sequences and control characters
        problematic_pattern = re.compile(r'_x[0-9A-Fa-f]{4}_|\\x[0-9A-Fa-f]{2}.*\[.*~')
        
        for idx, row in df_pandas.iterrows():
            try:
                # Check each cell in the row for problematic patterns
                for col, value in row.items():
                    if pd.notna(value):
                        value_str = str(value)
                        # Check for problematic escape sequences that might cause conversion errors
                        if problematic_pattern.search(value_str):
                            corrupted_rows.append(idx)
                            self.logger.warning(
                                f"Row {idx} contains corrupted data in column {col}: "
                                f"{value_str[:50]}... (skipping row)"
                            )
                            break
            except Exception as e:
                # If we can't even check the row, mark it as corrupted
                corrupted_rows.append(idx)
                self.logger.warning(f"Error checking row {idx} for corruption: {e} (skipping row)")
        
        return pd.Index(corrupted_rows)
    
    def _convert_pandas_to_polars_safe(self, df_pandas: pd.DataFrame, schema_overrides: dict) -> pl.DataFrame:
        """
        Convert pandas DataFrame to Polars DataFrame row-by-row, skipping problematic rows.
        
        This is a fallback method when normal conversion fails due to corrupted data.
        
        Args:
            df_pandas: Pandas DataFrame
            schema_overrides: Schema overrides for Polars
        
        Returns:
            Polars DataFrame with problematic rows skipped
        """
        valid_rows = []
        skipped_count = 0
        
        for idx, row in df_pandas.iterrows():
            try:
                # Try to convert single row to dict
                row_dict = row.to_dict()
                # Validate row can be converted
                for key, value in row_dict.items():
                    # Check if value contains problematic patterns
                    if pd.notna(value):
                        value_str = str(value)
                        # Check for escape sequences that might cause issues
                        if re.search(r'_x[0-9A-Fa-f]{4}_|\\x[0-9A-Fa-f]{2}.*\[.*~', value_str):
                            raise ValueError(f"Corrupted data in row {idx}: {value_str[:50]}")
                valid_rows.append(row_dict)
            except Exception as e:
                skipped_count += 1
                self.logger.warning(f"Skipping row {idx} due to conversion error: {e}")
        
        if skipped_count > 0:
            self.logger.warning(f"Skipped {skipped_count} rows during safe conversion")
        
        if not valid_rows:
            self.logger.error("No valid rows remaining after safe conversion")
            return pl.DataFrame(schema=schema_overrides)
        
        # Convert list of dicts to Polars DataFrame
        try:
            df_polars = pl.DataFrame(valid_rows, schema_overrides=schema_overrides)
            return df_polars
        except Exception as e:
            self.logger.error(f"Failed to create Polars DataFrame from valid rows: {e}")
            # Last resort: return empty DataFrame with correct schema
            return pl.DataFrame(schema=schema_overrides)
    
    def load_excel_chunked(self, file_path: Union[str, Path], chunk_size: int = 10000, sheet_name: Optional[str] = None, header_row: int = 0) -> Iterator[pl.DataFrame]:
        """
        Load Excel file in chunks for memory-efficient processing.
        
        Note: Since pandas.read_excel doesn't support chunking natively,
        we read the entire file and split it into chunks. For very large files,
        consider using openpyxl directly for true streaming in future.
        
        Args:
            file_path: Path to the Excel file
            chunk_size: Number of rows per chunk (default: 10000)
            sheet_name: Name of sheet to read (None = first sheet)
            header_row: Row number to use as header (0-indexed)
        
        Yields:
            Polars DataFrame chunks
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Determine engine based on file extension
            file_ext = file_path.suffix.lower()
            if file_ext == '.xlsx':
                engine = 'openpyxl'
            elif file_ext == '.xls':
                engine = 'xlrd'
            else:
                # Default to openpyxl for unknown extensions
                engine = 'openpyxl'
            
            # Read entire Excel file (pandas doesn't support chunking for Excel)
            # For very large files, this might use significant memory
            # Consider using openpyxl directly for true streaming in future
            # Explicitly specify engine to avoid auto-detection issues
            try:
                if sheet_name:
                    df_pandas = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, dtype=str, engine=engine)
                else:
                    df_pandas = pd.read_excel(file_path, header=header_row, dtype=str, engine=engine)
            except ImportError as e:
                if 'openpyxl' in str(e) or engine == 'openpyxl':
                    raise ImportError(
                        f"Missing required dependency 'openpyxl' for reading .xlsx files. "
                        f"Install it with: pip install openpyxl"
                    ) from e
                elif 'xlrd' in str(e) or engine == 'xlrd':
                    raise ImportError(
                        f"Missing required dependency 'xlrd' for reading .xls files. "
                        f"Install it with: pip install xlrd"
                    ) from e
                raise
            
            # Identify and log corrupted rows before processing
            corrupted_rows = self._identify_corrupted_rows(df_pandas)
            if len(corrupted_rows) > 0:
                self.logger.warning(
                    f"Identified {len(corrupted_rows)} corrupted rows, will skip them during processing"
                )
                # Remove corrupted rows
                df_pandas = df_pandas.drop(corrupted_rows)
            
            # Clean control characters and escape sequences BEFORE any type conversion
            # This prevents PyArrow from trying to convert corrupted strings to numeric types
            df_pandas = self._clean_control_characters(df_pandas)
            
            # Replace 'nan' strings (from actual NaN values) with None for proper null handling
            df_pandas = df_pandas.replace('nan', None, regex=False)
            df_pandas = df_pandas.replace('NaN', None, regex=False)
            df_pandas = df_pandas.replace('None', None, regex=False)
            
            # Replace empty strings and whitespace-only strings with None
            df_pandas = df_pandas.replace(r'^\s*$', None, regex=True)
            
            # Ensure all columns are explicitly string type before conversion
            for col in df_pandas.columns:
                try:
                    df_pandas[col] = df_pandas[col].astype(str)
                    # Convert 'None' strings back to actual None
                    df_pandas.loc[df_pandas[col] == 'None', col] = None
                except Exception as e:
                    self.logger.warning(f"Error converting column {col} to string: {e}, setting to None")
                    df_pandas[col] = None
            
            # Convert to Polars DataFrame - force all columns to strings initially
            # to prevent type inference errors with mixed-type data
            # Use explicit schema to ensure PyArrow respects our string types
            schema_overrides = {col: pl.Utf8 for col in df_pandas.columns}
            
            # Convert via CSV string buffer to avoid PyArrow type inference issues
            # This is more reliable than direct from_pandas conversion
            # If conversion fails, try row-by-row conversion to skip problematic rows
            try:
                df_full = pl.from_pandas(df_pandas, schema_overrides=schema_overrides)
            except Exception as e:
                # Fallback 1: Try CSV conversion
                try:
                    self.logger.warning(f"Direct pandas conversion failed, trying CSV fallback: {e}")
                    csv_buffer = io.StringIO()
                    df_pandas.to_csv(csv_buffer, index=False, sep='\t')
                    csv_buffer.seek(0)
                    df_full = pl.read_csv(csv_buffer, separator='\t', schema_overrides=schema_overrides)
                except Exception as e2:
                    # Fallback 2: Convert row by row, skipping problematic rows
                    self.logger.warning(
                        f"CSV conversion also failed, converting row-by-row and skipping errors: {e2}"
                    )
                    df_full = self._convert_pandas_to_polars_safe(df_pandas, schema_overrides)
            
            total_rows = len(df_full)
            self.logger.info(f"Loaded {total_rows} rows from Excel file {file_path.name}, splitting into chunks")
            
            # Split into chunks
            for i in range(0, total_rows, chunk_size):
                chunk_df = df_full.slice(i, chunk_size)
                
                # Filter out completely empty rows (rows where all values are null)
                if len(chunk_df) > 0:
                    # Create a mask for rows with at least one non-null value
                    null_counts = chunk_df.null_count()
                    # Filter rows that have at least one non-null value
                    # We'll keep all rows for now and let the cleaning pipeline handle empty rows
                    # This is more efficient than checking each row individually
                    yield chunk_df
            
            self.logger.info(f"Finished processing Excel file {file_path.name} in chunks")
        
        except Exception as e:
            self.logger.error(f"Error loading Excel file {file_path}: {e}")
            raise


# Create a default instance for backward compatibility
_default_loader = IngestionLoader()

# Expose functions for backward compatibility
def load_file(file_path: Union[str, Path], separator: str = None) -> pl.DataFrame:
    """Load a data file using Polars (backward compatibility wrapper)."""
    return _default_loader.load_file(file_path, separator)

def load_multiple_files(file_paths: List[Union[str, Path]], separator: str = None) -> pl.DataFrame:
    """Load multiple files and concatenate them (backward compatibility wrapper)."""
    return _default_loader.load_multiple_files(file_paths, separator)

def get_file_info(df: pl.DataFrame) -> dict:
    """Get basic information about the loaded dataframe (backward compatibility wrapper)."""
    return _default_loader.get_file_info(df)

def detect_file_type(file_path: Union[str, Path]) -> str:
    """Detect file type based on extension (backward compatibility wrapper)."""
    return _default_loader.detect_file_type(file_path)

def load_excel_file(file_path: Union[str, Path], sheet_name: Optional[str] = None, header_row: int = 0) -> pl.DataFrame:
    """Load an Excel file (backward compatibility wrapper)."""
    return _default_loader.load_excel_file(file_path, sheet_name, header_row)

def load_excel_chunked(file_path: Union[str, Path], chunk_size: int = 10000, sheet_name: Optional[str] = None, header_row: int = 0) -> Iterator[pl.DataFrame]:
    """Load Excel file in chunks (backward compatibility wrapper)."""
    return _default_loader.load_excel_chunked(file_path, chunk_size, sheet_name, header_row)

