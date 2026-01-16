"""Forecasting service for XGBoost with domain-specific features - frontend-ready format."""

from typing import Dict, Optional
from datetime import date, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
import logging

from backend.app.modules.forecasting.utils.enhanced_data_preparation import (
    load_enhanced_transaction_data,
    enrich_with_aggregated_features,
    resample_to_daily_enhanced
)
from backend.app.modules.forecasting.utils.data_preparation import (
    handle_missing_values,
    create_train_test_split
)
from backend.app.modules.forecasting.features.xgboost_features import prepare_features
from backend.app.modules.forecasting.models.xgboost_forecaster import XGBoostForecaster
from backend.app.modules.forecasting.utils.evaluation import (
    calculate_metrics,
    create_results_dataframe,
    calculate_confidence_intervals
)
from backend.app.modules.forecasting.utils.forecast_generator import create_future_features
from backend.app.database.models import DrugTransaction
from backend.app.database.session import get_db_session

logger = logging.getLogger(__name__)


class ForecastService:
    """Service for XGBoost forecasting with domain-specific features."""
    
    def __init__(self):
        """Initialize service."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def forecast(
        self,
        drug_code: str,
        forecast_days: int = 30,
        test_size: int = 30,
        lookback_days: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        department: Optional[int] = None
    ) -> Dict:
        """
        Complete XGBoost forecasting pipeline with domain-specific features.
        
        Returns frontend-ready format with historical and forecast data.
        
        Args:
            drug_code: Drug code to forecast
            forecast_days: Number of days to forecast ahead (default: 30)
            test_size: Number of days to use for testing (default: 30)
            lookback_days: Optional number of days to look back
            start_date: Optional start date
            end_date: Optional end date
            department: Optional consuming department ID (C.R) to filter by
        
        Returns:
            Dictionary with forecast results in frontend-ready format
        """
        if department:
            self.logger.info(f"Starting XGBoost forecast for {drug_code} (department: {department})")
        else:
            self.logger.info(f"Starting XGBoost forecast for {drug_code}")
        
        # Step 1: Load transaction data with metadata
        self.logger.info("Step 1: Loading transaction data with metadata")
        df = load_enhanced_transaction_data(
            drug_code=drug_code,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days,
            department=department
        )
        
        # Step 2: Enrich with aggregated features (category, department demand)
        self.logger.info("Step 2: Enriching with aggregated features")
        df = enrich_with_aggregated_features(df)
        
        # Step 3: Resample to daily and handle missing values
        self.logger.info("Step 3: Resampling to daily frequency")
        daily_data = resample_to_daily_enhanced(df, target_col='QTY')
        
        self.logger.info(f"Daily data: {len(daily_data)} days")
        self.logger.info(f"Date range: {daily_data.index.min()} to {daily_data.index.max()}")
        
        # Handle missing values in QTY
        daily_data['QTY'] = handle_missing_values(daily_data['QTY'])
        
        # Need sufficient data for training
        min_required = test_size + 30
        if len(daily_data) < min_required:
            date_range_info = ""
            if len(daily_data) > 0:
                date_range_info = f"Date range: {daily_data.index.min()} to {daily_data.index.max()}"
            
            raise ValueError(
                f"Insufficient data for drug_code '{drug_code}': "
                f"need at least {min_required} days, got {len(daily_data)}. "
                f"{date_range_info}"
            )
        
        # Step 4: Feature engineering with domain-specific features
        self.logger.info("Step 4: Creating features (including domain-specific features)")
        features_df = prepare_features(
            daily_data,
            target_col='QTY',
            use_domain_features=True
        )
        
        # Step 5: Train-test split
        self.logger.info("Step 5: Creating train-test split")
        train, test = create_train_test_split(features_df, test_size=test_size)
        
        # Prepare training data - ensure only numeric columns
        # Drop target column and any remaining non-numeric columns
        X_train = train.drop('QTY', axis=1)
        X_test = test.drop('QTY', axis=1)
        
        # Filter to only numeric columns (XGBoost requirement)
        numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
        X_train = X_train[numeric_cols]
        X_test = X_test[numeric_cols]
        
        y_train = train['QTY']
        y_test = test['QTY']
        
        self.logger.info(f"Training with {len(numeric_cols)} numeric features")
        
        # Step 6: Train model
        self.logger.info("Step 6: Training XGBoost model")
        model = XGBoostForecaster()
        eval_results = model.train(X_train=X_train, y_train=y_train, X_val=X_test, y_val=y_test)
        
        # Step 7: Evaluate on test set
        self.logger.info("Step 7: Evaluating model")
        y_pred = model.predict(X_test)
        metrics = calculate_metrics(y_test.values, y_pred)
        
        # Step 8: Generate future forecast
        self.logger.info(f"Step 8: Generating {forecast_days}-day forecast")
        last_training_date = features_df.index[-1]
        future_features = create_future_features(
            last_date=last_training_date,
            periods=forecast_days,
            feature_columns=X_train.columns.tolist()
        )
        
        future_predictions = model.predict(future_features)
        
        # Calculate confidence intervals
        results_df = create_results_dataframe(
            y_test=y_test.values,
            y_pred=y_pred,
            dates=y_test.index
        )
        errors = results_df['Error'].values
        lower_bounds, upper_bounds = calculate_confidence_intervals(errors=errors, predictions=future_predictions)
        
        # Step 9: Get drug metadata
        session = get_db_session()
        try:
            drug_meta = session.query(
                DrugTransaction.drug_name
            ).filter(
                DrugTransaction.drug_code == drug_code
            ).first()
            drug_name = drug_meta.drug_name if drug_meta else drug_code
        except:
            drug_name = drug_code
        finally:
            session.close()
        
        # Step 10: Format results for frontend
        self.logger.info("Step 10: Formatting results for frontend")
        
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
        
        # Historical data (full dataset)
        historical = [
            {
                'date': date_val.isoformat() if isinstance(date_val, pd.Timestamp) else str(date_val),
                'demand': safe_float(val),
                'type': 'actual'
            }
            for date_val, val in zip(daily_data.index, daily_data['QTY'].values)
        ]
        
        # Test predictions (for validation visualization)
        test_predictions = [
            {
                'date': date_val.isoformat() if isinstance(date_val, pd.Timestamp) else str(date_val),
                'actual': safe_float(actual),
                'predicted': safe_float(predicted),
                'error': safe_float(error),
                'type': 'test'
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
                'lower': safe_float(lower),
                'upper': safe_float(upper),
                'type': 'predicted'
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
        
        # Build frontend-ready response
        result = {
            'drug_code': drug_code,
            'drug_name': drug_name,
            'historical': historical,
            'test_predictions': test_predictions,
            'forecast': forecast,
            'metrics': {
                'rmse': safe_float(metrics.get('rmse', 0)),
                'mae': safe_float(metrics.get('mae', 0)),
                'mape': safe_float(metrics.get('mape', 0)),
                'r2': safe_float(metrics.get('r2', 0))
            },
            'feature_importance': feature_importance,
            'training_history': training_history,
            'forecast_days': forecast_days,
            'test_size': test_size,
            'data_info': {
                'total_days': len(daily_data),
                'train_days': len(train),
                'test_days': len(test),
                'date_range': {
                    'start': str(daily_data.index.min().date()),
                    'end': str(daily_data.index.max().date())
                }
            }
        }
        
        self.logger.info(f"Forecast completed. RMSE: {metrics['rmse']:.2f}")
        
        return result

