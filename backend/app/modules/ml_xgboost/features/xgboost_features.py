"""Feature engineering matching Colab script exactly."""

import pandas as pd
import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-based features matching Colab script.
    
    Args:
        df: DataFrame with DatetimeIndex
    
    Returns:
        DataFrame with added time features
    """
    features_df = df.copy()
    
    # Time-based features
    features_df['hour'] = features_df.index.hour
    features_df['dayofweek'] = features_df.index.dayofweek
    features_df['quarter'] = features_df.index.quarter
    features_df['month'] = features_df.index.month
    features_df['year'] = features_df.index.year
    features_df['dayofyear'] = features_df.index.dayofyear
    features_df['dayofmonth'] = features_df.index.day
    features_df['weekofyear'] = features_df.index.isocalendar().week
    
    return features_df


def create_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create cyclical encoding for periodic features matching Colab script.
    
    Args:
        df: DataFrame with dayofweek, month, dayofyear columns
    
    Returns:
        DataFrame with added cyclical features
    """
    features_df = df.copy()
    
    # Cyclical encoding
    features_df['dayofweek_sin'] = np.sin(2 * np.pi * features_df['dayofweek'] / 7)
    features_df['dayofweek_cos'] = np.cos(2 * np.pi * features_df['dayofweek'] / 7)
    features_df['month_sin'] = np.sin(2 * np.pi * features_df['month'] / 12)
    features_df['month_cos'] = np.cos(2 * np.pi * features_df['month'] / 12)
    features_df['dayofyear_sin'] = np.sin(2 * np.pi * features_df['dayofyear'] / 365)
    features_df['dayofyear_cos'] = np.cos(2 * np.pi * features_df['dayofyear'] / 365)
    
    return features_df


def create_lag_features(
    df: pd.DataFrame,
    target_col: str = 'QTY',
    lags: List[int] = [1, 2, 3, 7, 14, 21, 30]
) -> pd.DataFrame:
    """
    Create lag features matching Colab script.
    
    Args:
        df: DataFrame with target column
        target_col: Name of target column
        lags: List of lag periods
    
    Returns:
        DataFrame with added lag features
    """
    features_df = df.copy()
    
    for lag in lags:
        features_df[f'lag_{lag}'] = features_df[target_col].shift(lag)
    
    return features_df


def create_rolling_features(
    df: pd.DataFrame,
    target_col: str = 'QTY',
    windows: List[int] = [7, 14, 30]
) -> pd.DataFrame:
    """
    Create rolling statistics matching Colab script.
    
    Args:
        df: DataFrame with target column
        target_col: Name of target column
        windows: List of window sizes
    
    Returns:
        DataFrame with added rolling features
    """
    features_df = df.copy()
    
    for window in windows:
        features_df[f'rolling_mean_{window}'] = (
            features_df[target_col].rolling(window=window).mean().shift(1)
        )
        features_df[f'rolling_std_{window}'] = (
            features_df[target_col].rolling(window=window).std().shift(1)
        )
        features_df[f'rolling_min_{window}'] = (
            features_df[target_col].rolling(window=window).min().shift(1)
        )
        features_df[f'rolling_max_{window}'] = (
            features_df[target_col].rolling(window=window).max().shift(1)
        )
    
    return features_df


def create_difference_features(
    df: pd.DataFrame,
    target_col: str = 'QTY'
) -> pd.DataFrame:
    """
    Create difference features matching Colab script.
    
    Args:
        df: DataFrame with target column
        target_col: Name of target column
    
    Returns:
        DataFrame with added difference features
    """
    features_df = df.copy()
    
    features_df['diff_1'] = features_df[target_col].diff(1)
    features_df['diff_7'] = features_df[target_col].diff(7)
    
    return features_df


def create_binary_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create binary features matching Colab script.
    
    Args:
        df: DataFrame with dayofweek column
    
    Returns:
        DataFrame with added binary features
    """
    features_df = df.copy()
    
    features_df['is_weekend'] = features_df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)
    features_df['is_month_start'] = features_df.index.is_month_start.astype(int)
    features_df['is_month_end'] = features_df.index.is_month_end.astype(int)
    features_df['is_quarter_start'] = features_df.index.is_quarter_start.astype(int)
    features_df['is_quarter_end'] = features_df.index.is_quarter_end.astype(int)
    
    return features_df


def prepare_features(
    daily_data: pd.Series,
    target_col: str = 'QTY',
    use_enhanced_features: bool = False
) -> pd.DataFrame:
    """
    Master function: combine all feature engineering steps matching Colab script.
    
    Args:
        daily_data: Daily time series (can be Series or DataFrame)
        target_col: Name of target column
        use_enhanced_features: Whether to include domain-specific enhanced features
    
    Returns:
        DataFrame with all features prepared
    """
    # Create feature DataFrame
    if isinstance(daily_data, pd.Series):
        features_df = pd.DataFrame(index=daily_data.index)
        features_df[target_col] = daily_data
    else:
        features_df = daily_data.copy()
    
    logger.info("Creating time-based features...")
    features_df = create_time_features(features_df)
    
    logger.info("Creating cyclical features...")
    features_df = create_cyclical_features(features_df)
    
    logger.info("Creating lag features...")
    features_df = create_lag_features(features_df, target_col=target_col)
    
    logger.info("Creating rolling statistics...")
    features_df = create_rolling_features(features_df, target_col=target_col)
    
    logger.info("Creating difference features...")
    features_df = create_difference_features(features_df, target_col=target_col)
    
    logger.info("Creating binary features...")
    features_df = create_binary_features(features_df)
    
    # Add enhanced domain-specific features if requested
    if use_enhanced_features:
        try:
            from backend.app.modules.ml_xgboost.features.enhanced_features import create_enhanced_features
            logger.info("Creating enhanced domain-specific features...")
            features_df = create_enhanced_features(features_df, target_col=target_col)
        except Exception as e:
            logger.warning(f"Could not create enhanced features: {str(e)}")
    
    # Remove rows with NaN values (from lag/rolling features)
    features_df = features_df.dropna()
    
    logger.info(f"Final feature DataFrame shape: {features_df.shape}")
    logger.info(f"Number of features created: {len(features_df.columns) - 1}")  # Excluding target
    
    return features_df

