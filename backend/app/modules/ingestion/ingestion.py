"""Data ingestion module using Polars for efficient file loading."""

import polars as pl
from pathlib import Path
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)


def load_file(file_path: Union[str, Path], separator: str = None) -> pl.DataFrame:
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
                        logger.info(f"Auto-detected separator: '{sep}'")
                        break
                except:
                    continue
            else:
                # Default to tab-separated (common for this dataset)
                df = pl.read_csv(file_path, separator='\t', encoding='utf-8')
        
        logger.info(f"Loaded {len(df)} rows from {file_path.name}")
        return df
    
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        raise


def load_multiple_files(file_paths: List[Union[str, Path]], separator: str = None) -> pl.DataFrame:
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
        df = load_file(file_path, separator)
        df = df.with_columns([
            pl.lit(str(file_path)).alias('source_file')
        ])
        dataframes.append(df)
    
    if not dataframes:
        raise ValueError("No files loaded")
    
    # Combine all dataframes
    combined_df = pl.concat(dataframes)
    logger.info(f"Combined {len(file_paths)} files into {len(combined_df)} total rows")
    
    return combined_df


def get_file_info(df: pl.DataFrame) -> dict:
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

