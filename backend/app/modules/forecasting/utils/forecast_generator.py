"""Forecast generator for future dates - matching Colab script."""

import pandas as pd
import numpy as np
from datetime import timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)


def create_future_features(
    last_date: pd.Timestamp,
    periods: int = 14,
    feature_columns: List[str] = None
) -> pd.DataFrame:
    """
    Create features for future dates matching Colab script approach.
    
    Note: Lag and rolling features are set to 0 for future dates
    (Colab script doesn't create them for future dates).
    
    Args:
        last_date: Last date in training data
        periods: Number of future periods to create
        feature_columns: List of feature column names from training data
    
    Returns:
        DataFrame with features for future dates
    """
    # Generate future dates
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=periods,
        freq='D'
    )
    
    future_df = pd.DataFrame(index=future_dates)
    
    # Time-based features
    future_df['hour'] = future_df.index.hour
    future_df['dayofweek'] = future_df.index.dayofweek
    future_df['quarter'] = future_df.index.quarter
    future_df['month'] = future_df.index.month
    future_df['year'] = future_df.index.year
    future_df['dayofyear'] = future_df.index.dayofyear
    future_df['dayofmonth'] = future_df.index.day
    future_df['weekofyear'] = future_df.index.isocalendar().week
    
    # Cyclical features
    future_df['dayofweek_sin'] = np.sin(2 * np.pi * future_df['dayofweek'] / 7)
    future_df['dayofweek_cos'] = np.cos(2 * np.pi * future_df['dayofweek'] / 7)
    future_df['month_sin'] = np.sin(2 * np.pi * future_df['month'] / 12)
    future_df['month_cos'] = np.cos(2 * np.pi * future_df['month'] / 12)
    future_df['dayofyear_sin'] = np.sin(2 * np.pi * future_df['dayofyear'] / 365)
    future_df['dayofyear_cos'] = np.cos(2 * np.pi * future_df['dayofyear'] / 365)
    
    # Binary features
    future_df['is_weekend'] = future_df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)
    future_df['is_month_start'] = future_df.index.is_month_start.astype(int)
    future_df['is_month_end'] = future_df.index.is_month_end.astype(int)
    future_df['is_quarter_start'] = future_df.index.is_quarter_start.astype(int)
    future_df['is_quarter_end'] = future_df.index.is_quarter_end.astype(int)
    
    # Lag and rolling features - set to 0 for future dates (matching Colab)
    # We need to add missing columns that exist in training data
    if feature_columns:
        for col in feature_columns:
            if col not in future_df.columns:
                future_df[col] = 0
        
        # Ensure column order matches training data
        # Only include columns that exist in both
        available_cols = [col for col in feature_columns if col in future_df.columns]
        future_df = future_df[available_cols]
    
    return future_df

