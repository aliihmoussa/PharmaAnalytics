"""Evaluation utilities for XGBoost forecasting - matching Colab script."""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging

logger = logging.getLogger(__name__)


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate evaluation metrics matching Colab script.
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Dictionary with RMSE, MAE, MAPE, and R²
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    
    # MAPE calculation (handle division by zero)
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
    
    # R² (R-squared) calculation
    r2 = r2_score(y_true, y_pred)
    
    return {
        'rmse': float(rmse),
        'mae': float(mae),
        'mape': float(mape),
        'r2': float(r2)
    }


def create_results_dataframe(
    y_test: np.ndarray,
    y_pred: np.ndarray,
    dates: pd.DatetimeIndex
) -> pd.DataFrame:
    """
    Create results DataFrame matching Colab script format.
    
    Args:
        y_test: True test values
        y_pred: Predicted values
        dates: Date index
    
    Returns:
        DataFrame with Actual, Predicted, Error, Error_Pct columns
    """
    results_df = pd.DataFrame({
        'Actual': y_test,
        'Predicted': y_pred,
        'Date': dates
    }).set_index('Date')
    
    results_df['Error'] = results_df['Actual'] - results_df['Predicted']
    results_df['Error_Pct'] = (results_df['Error'] / results_df['Actual']) * 100
    
    return results_df


def calculate_confidence_intervals(
    errors: np.ndarray,
    predictions: np.ndarray,
    confidence_level: float = 0.95
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate confidence intervals for predictions.
    
    Uses standard deviation of errors from test set (matching Colab approach).
    
    Args:
        errors: Prediction errors from test set
        predictions: Future predictions
        confidence_level: Confidence level (0.95 for 95% CI)
    
    Returns:
        Tuple of (lower_bounds, upper_bounds)
    """
    forecast_std = np.std(errors)
    
    # Z-score for confidence level
    if confidence_level == 0.95:
        z_score = 1.96
    elif confidence_level == 0.80:
        z_score = 1.28
    else:
        # Approximate z-score
        z_score = 1.96
    
    lower_bounds = predictions - z_score * forecast_std
    upper_bounds = predictions + z_score * forecast_std
    
    # Ensure non-negative
    lower_bounds = np.maximum(lower_bounds, 0)
    
    return lower_bounds, upper_bounds

