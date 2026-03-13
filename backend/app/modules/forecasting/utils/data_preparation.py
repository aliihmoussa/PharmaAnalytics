"""Data preparation utilities - convert database data to pandas DataFrame format."""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from datetime import date, timedelta
from backend.app.modules.analytics.queries import AnalyticsDAL
import logging

logger = logging.getLogger(__name__)


def load_and_prepare_data(
    drug_code: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    lookback_days: Optional[int] = None
) -> pd.DataFrame:
    """
    Load data from database and convert to pandas DataFrame matching Colab format.
    
    Args:
        drug_code: Drug code to load
        start_date: Optional start date
        end_date: Optional end date (defaults to today)
        lookback_days: Optional number of days to look back (if start_date not provided)
    
    Returns:
        pandas DataFrame with 'DATE' index and 'QTY' column
    """
    if end_date is None:
        end_date = date.today()
    
    if start_date is None:
        if lookback_days:
            start_date = end_date - timedelta(days=lookback_days)
        else:
            # Default: 2 years of data
            start_date = end_date - timedelta(days=730)
    
    logger.info(f"Loading data for {drug_code} from {start_date} to {end_date}")
    
    dal = AnalyticsDAL()
    try:
        with dal:
            raw_data = dal.get_drug_demand_time_series(
                start_date=start_date,
                end_date=end_date,
                drug_code=drug_code,
                granularity='daily'
            )
        
        if not raw_data:
            raise ValueError(
                f"No data found for drug_code={drug_code} "
                f"between {start_date} and {end_date}. "
                f"Please check if the drug_code exists and has transactions in this date range."
            )
        
        if len(raw_data) == 1:
            logger.warning(
                f"Only 1 day of data found for drug_code={drug_code}. "
                f"This is insufficient for forecasting. "
                f"Date: {raw_data[0].get('date')}, Quantity: {raw_data[0].get('quantity')}"
            )
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(raw_data)
        
        logger.info(f"Raw data from DB: {len(df)} records")
        if len(df) > 0:
            logger.info(f"Sample data: {df.head()}")
            logger.info(f"Columns: {df.columns.tolist()}")
        
        # Rename columns to match Colab format
        if 'date' in df.columns:
            df = df.rename(columns={'date': 'DATE'})
        if 'quantity' in df.columns:
            df = df.rename(columns={'quantity': 'QTY'})
        
        # Convert QTY to numeric (handles Decimal, string, etc.)
        if 'QTY' in df.columns:
            # Convert to numeric, handling Decimal types from PostgreSQL
            df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')
        else:
            raise ValueError(f"No quantity column found in data. Available columns: {df.columns.tolist()}")
        
        # Ensure DATE is datetime
        df['DATE'] = pd.to_datetime(df['DATE'])
        
        # Set DATE as index
        df = df.set_index('DATE')
        df.index = pd.to_datetime(df.index)
        
        # Check for null/zero quantities
        null_count = df['QTY'].isna().sum()
        zero_count = (df['QTY'] == 0).sum()
        logger.info(f"Loaded {len(df)} records. Null QTY: {null_count}, Zero QTY: {zero_count}")
        logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
        logger.info(f"QTY dtype: {df['QTY'].dtype}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}", exc_info=True)
        raise


def resample_to_daily(df: pd.DataFrame, target_col: str = 'QTY') -> pd.Series:
    """
    Resample data to daily frequency matching Colab script.
    
    Note: Database already returns daily aggregated data, but we resample
    to ensure continuous daily series (filling gaps with 0).
    
    Args:
        df: DataFrame with date index
        target_col: Name of target column
    
    Returns:
        Daily resampled Series
    """
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found")
    
    logger.info(f"Before resampling: {len(df)} records")
    logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
    
    # Resample to daily frequency (sum for daily totals)
    # This will fill missing dates with 0
    daily_data = df[target_col].resample('D').sum()
    
    logger.info(f"After resampling: {len(daily_data)} records")
    logger.info(f"Date range: {daily_data.index.min()} to {daily_data.index.max()}")
    
    return daily_data


def handle_missing_values(daily_data: pd.Series) -> pd.Series:
    """
    Handle missing values matching Colab script logic.
    
    Colab: daily_data.replace(0, np.nan).ffill()
    
    Args:
        daily_data: Daily time series
    
    Returns:
        Series with missing values handled
    """
    # Replace zeros with NaN, then forward fill
    daily_data = daily_data.replace(0, np.nan).ffill()
    
    return daily_data


def create_train_test_split(
    features_df: pd.DataFrame,
    test_size: int = 30
) -> tuple:
    """
    Create time-aware train-test split matching Colab script.
    
    Uses last N days for testing (preserves temporal order).
    
    Args:
        features_df: DataFrame with features and target
        test_size: Number of days to use for testing
    
    Returns:
        Tuple of (train_df, test_df)
    """
    if len(features_df) < test_size:
        raise ValueError(
            f"Insufficient data: need at least {test_size} days, got {len(features_df)}"
        )
    
    train = features_df.iloc[:-test_size]
    test = features_df.iloc[-test_size:]
    
    logger.info(
        f"Train: {train.shape[0]} days ({train.index.min()} to {train.index.max()})"
    )
    logger.info(
        f"Test: {test.shape[0]} days ({test.index.min()} to {test.index.max()})"
    )
    
    return train, test

