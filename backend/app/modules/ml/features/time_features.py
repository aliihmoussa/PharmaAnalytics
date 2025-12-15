"""Time-based feature engineering for demand forecasting."""

import polars as pl
from typing import List
import logging

logger = logging.getLogger(__name__)


def create_time_features(df: pl.DataFrame, date_col: str = 'date') -> pl.DataFrame:
    """
    Create time-based features for forecasting.
    
    Args:
        df: Polars DataFrame with date column
        date_col: Name of date column
    
    Returns:
        DataFrame with added time features
    """
    if date_col not in df.columns:
        raise ValueError(f"Date column '{date_col}' not found in DataFrame")
    
    df = df.with_columns([
        pl.col(date_col).dt.weekday().alias('day_of_week'),  # 1=Monday, 7=Sunday
        pl.col(date_col).dt.month().alias('month'),
        pl.col(date_col).dt.quarter().alias('quarter'),
        pl.col(date_col).dt.year().alias('year'),
        pl.col(date_col).dt.day().alias('day_of_month'),
        (pl.col(date_col).dt.weekday() >= 6).alias('is_weekend'),  # Saturday=6, Sunday=7
        (pl.col(date_col).dt.weekday() <= 5).alias('is_weekday'),
    ])
    
    return df


def create_lag_features(
    df: pl.DataFrame,
    value_col: str,
    date_col: str = 'date',
    lags: List[int] = [7, 14, 30, 90]
) -> pl.DataFrame:
    """
    Create lag features for time series.
    
    Args:
        df: Polars DataFrame
        value_col: Name of value column to lag
        date_col: Name of date column for sorting
        lags: List of lag periods (e.g., [7, 14, 30] for 7, 14, 30 days ago)
    
    Returns:
        DataFrame with added lag features
    """
    # Ensure sorted by date
    df = df.sort(date_col)
    
    for lag in lags:
        df = df.with_columns(
            pl.col(value_col).shift(lag).alias(f'{value_col}_lag_{lag}d')
        )
    
    return df


def create_rolling_features(
    df: pl.DataFrame,
    value_col: str,
    windows: List[int] = [7, 14, 30]
) -> pl.DataFrame:
    """
    Create rolling statistics features.
    
    Args:
        df: Polars DataFrame
        value_col: Name of value column
        windows: List of window sizes (e.g., [7, 14, 30] for 7, 14, 30 day windows)
    
    Returns:
        DataFrame with added rolling features
    """
    for window in windows:
        df = df.with_columns([
            pl.col(value_col).rolling_mean(window).alias(f'{value_col}_mean_{window}d'),
            pl.col(value_col).rolling_std(window).alias(f'{value_col}_std_{window}d'),
            pl.col(value_col).rolling_min(window).alias(f'{value_col}_min_{window}d'),
            pl.col(value_col).rolling_max(window).alias(f'{value_col}_max_{window}d'),
        ])
    
    return df


def create_seasonal_features(df: pl.DataFrame, date_col: str = 'date') -> pl.DataFrame:
    """
    Create seasonal features (cyclical encoding).
    
    Args:
        df: Polars DataFrame
        date_col: Name of date column
    
    Returns:
        DataFrame with added seasonal features
    """
    df = df.with_columns([
        # Cyclical encoding for day of week (0-1 range)
        (pl.col(date_col).dt.weekday() / 7.0).alias('day_of_week_cyclical'),
        # Cyclical encoding for month (0-1 range)
        (pl.col(date_col).dt.month() / 12.0).alias('month_cyclical'),
        # Day of year (1-365/366)
        pl.col(date_col).dt.ordinal_day().alias('day_of_year'),
    ])
    
    return df


def prepare_features_for_training(
    df: pl.DataFrame,
    target_col: str = 'demand',
    date_col: str = 'date',
    include_lags: bool = True,
    include_rolling: bool = True,
    include_seasonal: bool = True
) -> pl.DataFrame:
    """
    Prepare complete feature set for model training.
    
    Args:
        df: Polars DataFrame with date and target columns
        target_col: Name of target column
        date_col: Name of date column
        include_lags: Whether to include lag features
        include_rolling: Whether to include rolling statistics
        include_seasonal: Whether to include seasonal features
    
    Returns:
        DataFrame with all features prepared
    """
    # Ensure sorted by date
    df = df.sort(date_col)
    
    # Create time features
    df = create_time_features(df, date_col)
    
    # Create lag features
    if include_lags:
        df = create_lag_features(df, target_col, date_col, lags=[7, 14, 30, 90])
    
    # Create rolling features
    if include_rolling:
        df = create_rolling_features(df, target_col, windows=[7, 14, 30])
    
    # Create seasonal features
    if include_seasonal:
        df = create_seasonal_features(df, date_col)
    
    # Remove rows with NaN (from lag/rolling features)
    df = df.drop_nulls()
    
    return df

