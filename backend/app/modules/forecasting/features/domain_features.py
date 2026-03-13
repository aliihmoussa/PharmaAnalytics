"""Domain-specific feature engineering for drug transaction data."""

import pandas as pd
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def create_department_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create department-related features.
    
    Args:
        df: DataFrame with daily aggregated data including 'cr', 'cs', 'QTY' columns
    
    Returns:
        DataFrame with added department features
    """
    features_df = df.copy()
    
    if 'cr' not in features_df.columns or 'QTY' not in features_df.columns:
        logger.warning("Missing 'cr' or 'QTY' columns for department features")
        return features_df
    
    # Department demand ratio: ratio of demand from top consuming department
    if 'top_dept_demand' in features_df.columns:
        total_demand = features_df['QTY'].abs()
        features_df['dept_demand_ratio'] = (
            features_df['top_dept_demand'] / total_demand.replace(0, np.nan)
        ).fillna(0)
    
    # Number of unique consuming departments per day
    if 'unique_depts' in features_df.columns:
        features_df['dept_diversity'] = features_df['unique_depts']
    
    # Supplying department features (if available)
    if 'cs' in features_df.columns:
        # Most common supplying department (mode)
        if 'top_supply_dept' in features_df.columns:
            features_df['supply_dept_ratio'] = (
                features_df['top_supply_dept_demand'] / total_demand.replace(0, np.nan)
            ).fillna(0) if 'top_supply_dept_demand' in features_df.columns else 0
    
    return features_df


def create_category_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create category-related features.
    
    Args:
        df: DataFrame with 'cat' and 'QTY' columns
    
    Returns:
        DataFrame with added category features
    """
    features_df = df.copy()
    
    if 'cat' not in features_df.columns or 'QTY' not in features_df.columns:
        logger.warning("Missing 'cat' or 'QTY' columns for category features")
        return features_df
    
    # Category trend: rolling mean of category demand
    if 'category_demand' in features_df.columns:
        features_df['category_trend'] = (
            features_df['category_demand'].rolling(window=7, min_periods=1).mean()
        )
        features_df['category_trend_30'] = (
            features_df['category_demand'].rolling(window=30, min_periods=1).mean()
        )
    
    # Category stability: coefficient of variation
    if 'category_demand' in features_df.columns:
        rolling_std = features_df['category_demand'].rolling(window=30, min_periods=1).std()
        rolling_mean = features_df['category_demand'].rolling(window=30, min_periods=1).mean()
        features_df['category_stability'] = (
            (rolling_std / rolling_mean.replace(0, np.nan)).fillna(0)
        )
    
    return features_df


def create_room_bed_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create room and bed-related features.
    
    Args:
        df: DataFrame with room/bed aggregations
    
    Returns:
        DataFrame with added room/bed features
    """
    features_df = df.copy()
    
    # Room diversity: number of unique rooms per day
    if 'unique_rooms' in features_df.columns:
        features_df['room_diversity'] = features_df['unique_rooms']
    else:
        features_df['room_diversity'] = 0
    
    # Bed diversity: number of unique beds per day
    if 'unique_beds' in features_df.columns:
        features_df['bed_diversity'] = features_df['unique_beds']
    else:
        features_df['bed_diversity'] = 0
    
    # Average demand per room
    if 'room_diversity' in features_df.columns and 'QTY' in features_df.columns:
        features_df['avg_demand_per_room'] = (
            features_df['QTY'].abs() / features_df['room_diversity'].replace(0, 1)
        )
    
    return features_df


def create_transaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create transaction pattern features.
    
    Args:
        df: DataFrame with transaction count and QTY
    
    Returns:
        DataFrame with added transaction features
    """
    features_df = df.copy()
    
    if 'QTY' not in features_df.columns:
        return features_df
    
    # Transaction count per day (if available)
    if 'transaction_count' in features_df.columns:
        features_df['txn_count'] = features_df['transaction_count']
    else:
        features_df['txn_count'] = 1  # Default if not available
    
    # Average transaction size
    if 'QTY' in features_df.columns and 'txn_count' in features_df.columns:
        features_df['avg_transaction_size'] = (
            features_df['QTY'].abs() / features_df['txn_count'].replace(0, 1)
        )
    
    # Transaction size variability (rolling std)
    if 'avg_transaction_size' in features_df.columns:
        features_df['txn_size_std_7'] = (
            features_df['avg_transaction_size'].rolling(window=7, min_periods=1).std()
        )
        features_df['txn_size_std_30'] = (
            features_df['avg_transaction_size'].rolling(window=30, min_periods=1).std()
        )
    
    return features_df


def create_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create price-related features.
    
    Args:
        df: DataFrame with 'unit_price' or 'avg_unit_price' column
    
    Returns:
        DataFrame with added price features
    """
    features_df = df.copy()
    
    # Average unit price
    price_col = None
    if 'avg_unit_price' in features_df.columns:
        price_col = 'avg_unit_price'
    elif 'unit_price' in features_df.columns:
        price_col = 'unit_price'
    
    if price_col:
        features_df['unit_price'] = features_df[price_col]
        
        # Price stability: coefficient of variation
        rolling_mean = features_df['unit_price'].rolling(window=30, min_periods=1).mean()
        rolling_std = features_df['unit_price'].rolling(window=30, min_periods=1).std()
        features_df['price_stability'] = (
            (rolling_std / rolling_mean.replace(0, np.nan)).fillna(0)
        )
        
        # Price trend
        features_df['price_trend_7'] = (
            features_df['unit_price'].rolling(window=7, min_periods=1).mean()
        )
        features_df['price_trend_30'] = (
            features_df['unit_price'].rolling(window=30, min_periods=1).mean()
        )
    else:
        # Default values if price not available
        features_df['unit_price'] = 0
        features_df['price_stability'] = 0
        features_df['price_trend_7'] = 0
        features_df['price_trend_30'] = 0
    
    return features_df


def create_admission_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create admission date-related features.
    
    Args:
        df: DataFrame with 'ad_date' and transaction date index
    
    Returns:
        DataFrame with added admission features
    """
    features_df = df.copy()
    
    if 'ad_date' not in features_df.columns or features_df.index.dtype != 'datetime64[ns]':
        # Default values if admission date not available
        features_df['admission_lag'] = 0
        features_df['has_admission_date'] = 0
        return features_df
    
    # Days between admission and transaction
    transaction_dates = pd.to_datetime(features_df.index)
    admission_dates = pd.to_datetime(features_df['ad_date'], errors='coerce')
    
    features_df['admission_lag'] = (
        (transaction_dates - admission_dates).dt.days.fillna(0)
    )
    features_df['has_admission_date'] = (
        features_df['ad_date'].notna().astype(int)
    )
    
    # Admission lag statistics (rolling)
    features_df['admission_lag_mean_7'] = (
        features_df['admission_lag'].rolling(window=7, min_periods=1).mean()
    )
    features_df['admission_lag_mean_30'] = (
        features_df['admission_lag'].rolling(window=30, min_periods=1).mean()
    )
    
    # Drop the original ad_date column (object type) - we've extracted all numeric features from it
    if 'ad_date' in features_df.columns:
        features_df = features_df.drop(columns=['ad_date'])
    
    return features_df


def create_domain_features(
    daily_data: pd.DataFrame,
    target_col: str = 'QTY'
) -> pd.DataFrame:
    """
    Master function: create all domain-specific features for drug transactions.
    
    Creates features related to departments, categories, rooms, prices, and admissions.
    
    Args:
        daily_data: DataFrame with daily aggregated data including metadata
        target_col: Name of target column (default: 'QTY')
    
    Returns:
        DataFrame with all domain-specific features added
    """
    features_df = daily_data.copy()
    
    logger.info("Creating department features...")
    features_df = create_department_features(features_df)
    
    logger.info("Creating category features...")
    features_df = create_category_features(features_df)
    
    logger.info("Creating room/bed features...")
    features_df = create_room_bed_features(features_df)
    
    logger.info("Creating transaction features...")
    features_df = create_transaction_features(features_df)
    
    logger.info("Creating price features...")
    features_df = create_price_features(features_df)
    
    logger.info("Creating admission features...")
    features_df = create_admission_features(features_df)
    
    # Drop any remaining non-numeric columns (object types) that XGBoost can't handle
    # Keep only numeric types: int, float, bool
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns.tolist()
    if target_col in features_df.columns:
        numeric_cols.append(target_col)  # Keep target column even if it's not numeric
    
    # Drop non-numeric columns
    cols_to_drop = [col for col in features_df.columns if col not in numeric_cols]
    if cols_to_drop:
        logger.info(f"Dropping non-numeric columns: {cols_to_drop}")
        features_df = features_df.drop(columns=cols_to_drop)
    
    # Fill any remaining NaN values with 0
    features_df = features_df.fillna(0)
    
    logger.info(f"Domain features created. Total columns: {len(features_df.columns)}")
    
    return features_df

