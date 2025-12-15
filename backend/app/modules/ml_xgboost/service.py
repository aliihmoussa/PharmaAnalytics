"""XGBoost forecasting service - orchestrates complete pipeline."""

from typing import Dict, Optional
from datetime import date, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
import logging

from backend.app.modules.ml_xgboost.utils.data_preparation import (
    load_and_prepare_data,
    resample_to_daily,
    handle_missing_values,
    create_train_test_split
)
from backend.app.modules.ml_xgboost.features.xgboost_features import prepare_features
from backend.app.modules.ml_xgboost.models.xgboost_forecaster import XGBoostForecaster
from backend.app.modules.ml_xgboost.utils.evaluation import (
    calculate_metrics,
    create_results_dataframe,
    calculate_confidence_intervals
)
from backend.app.modules.ml_xgboost.utils.forecast_generator import create_future_features

logger = logging.getLogger(__name__)


class XGBoostForecastService:
    """Service for XGBoost time-series forecasting matching Colab script."""
    
    def __init__(self):
        """Initialize service."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def forecast(
        self,
        drug_code: str,
        forecast_days: int = 14,
        test_size: int = 30,
        lookback_days: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Complete XGBoost forecasting pipeline matching Colab script.
        
        Args:
            drug_code: Drug code to forecast
            forecast_days: Number of days to forecast ahead (default: 14)
            test_size: Number of days to use for testing (default: 30)
            lookback_days: Optional number of days to look back
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            Dictionary with forecast results
        """
        self.logger.info(f"Starting XGBoost forecast for {drug_code}")
        
        # Step 1: Load and prepare data
        self.logger.info("Step 1: Loading and preparing data")
        df = load_and_prepare_data(
            drug_code=drug_code,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days
        )
        
        # Step 2: Resample to daily and handle missing values
        self.logger.info("Step 2: Resampling to daily frequency")
        daily_data = resample_to_daily(df, target_col='QTY')
        
        self.logger.info(f"Daily data after resampling: {len(daily_data)} days")
        self.logger.info(f"Date range: {daily_data.index.min()} to {daily_data.index.max()}")
        
        daily_data = handle_missing_values(daily_data)
        
        self.logger.info(f"Daily data after handling missing values: {len(daily_data)} days")
        
        # Need sufficient data for training (at least test_size + enough for features)
        # Features require up to 30 days of lag, so we need at least test_size + 30
        min_required = test_size + 30
        if len(daily_data) < min_required:
            # Provide helpful error message
            date_range_info = ""
            if len(daily_data) > 0:
                date_range_info = f"Date range: {daily_data.index.min()} to {daily_data.index.max()}"
            
            raise ValueError(
                f"Insufficient data for drug_code '{drug_code}': "
                f"need at least {min_required} days, got {len(daily_data)}. "
                f"{date_range_info}. "
                f"Please try: "
                f"1) Increase lookback_days parameter, "
                f"2) Use a different date range with more data, "
                f"3) Check if this drug_code has sufficient historical transactions."
            )
        
        # Step 3: Feature engineering
        self.logger.info("Step 3: Creating features")
        features_df = prepare_features(daily_data, target_col='QTY')
        
        # Step 4: Train-test split
        self.logger.info("Step 4: Creating train-test split")
        train, test = create_train_test_split(features_df, test_size=test_size)
        
        # Prepare training data
        X_train = train.drop('QTY', axis=1)
        y_train = train['QTY']
        X_test = test.drop('QTY', axis=1)
        y_test = test['QTY']
        
        # Step 5: Train model
        self.logger.info("Step 5: Training XGBoost model")
        model = XGBoostForecaster()
        eval_results = model.train(
            X_train=X_train,
            y_train=y_train,
            X_val=X_test,
            y_val=y_test,
            verbose=False
        )
        
        # Step 6: Evaluate on test set
        self.logger.info("Step 6: Evaluating model")
        y_pred = model.predict(X_test)
        metrics = calculate_metrics(y_test.values, y_pred)
        
        # Create results DataFrame
        results_df = create_results_dataframe(
            y_test=y_test.values,
            y_pred=y_pred,
            dates=y_test.index
        )
        
        # Step 7: Generate future forecast
        self.logger.info(f"Step 7: Generating {forecast_days}-day forecast")
        last_training_date = features_df.index[-1]
        future_features = create_future_features(
            last_date=last_training_date,
            periods=forecast_days,
            feature_columns=X_train.columns.tolist()
        )
        
        future_predictions = model.predict(future_features)
        
        # Calculate confidence intervals
        errors = results_df['Error'].values
        lower_bounds, upper_bounds = calculate_confidence_intervals(
            errors=errors,
            predictions=future_predictions,
            confidence_level=0.95
        )
        
        # Step 8: Format results
        self.logger.info("Step 8: Formatting results")
        
        # Historical data (full dataset)
        # Helper function to safely convert to float
        def safe_float(val):
            if pd.isna(val):
                return 0.0
            if isinstance(val, (Decimal, np.integer, np.floating)):
                return float(val)
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        
        historical = [
            {
                'date': date_val.isoformat() if isinstance(date_val, pd.Timestamp) else str(date_val),
                'demand': safe_float(val)
            }
            for date_val, val in zip(daily_data.index, daily_data.values)
        ]
        
        # Test predictions
        test_predictions = [
            {
                'date': date_val.isoformat() if isinstance(date_val, pd.Timestamp) else str(date_val),
                'actual': safe_float(actual),
                'predicted': safe_float(predicted),
                'error': safe_float(error)
            }
            for date_val, actual, predicted, error in zip(
                results_df.index,
                results_df['Actual'].values,
                results_df['Predicted'].values,
                results_df['Error'].values
            )
        ]
        
        # Future forecast
        forecast = [
            {
                'date': date_val.isoformat() if isinstance(date_val, pd.Timestamp) else str(date_val),
                'predicted': safe_float(pred),
                'lower_bound': safe_float(lower),
                'upper_bound': safe_float(upper)
            }
            for date_val, pred, lower, upper in zip(
                future_features.index,
                future_predictions,
                lower_bounds,
                upper_bounds
            )
        ]
        
        # Feature importance
        feature_importance_df = model.get_feature_importance()
        feature_importance = {
            str(row['feature']): safe_float(row['importance'])
            for _, row in feature_importance_df.iterrows()
        }
        
        # Training history
        training_history = {}
        if eval_results:
            training_history = {
                'train_rmse': eval_results.get('validation_0', {}).get('rmse', []),
                'val_rmse': eval_results.get('validation_1', {}).get('rmse', [])
            }
        
        result = {
            'drug_code': drug_code,
            'historical': historical,
            'test_predictions': test_predictions,
            'forecast': forecast,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'training_history': training_history,
            'method': 'xgboost_colab',
            'forecast_days': forecast_days,
            'test_size': test_size
        }
        
        self.logger.info(f"Forecast completed. RMSE: {metrics['rmse']:.2f}")
        
        return result

