"""XGBoost forecaster matching Colab script configuration."""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple, List
import logging

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available. Install with: pip install xgboost")

logger = logging.getLogger(__name__)


class XGBoostForecaster:
    """
    XGBoost forecaster matching Colab script configuration.
    """
    
    def __init__(
        self,
        n_estimators: int = 1000,
        learning_rate: float = 0.01,
        max_depth: int = 7,
        min_child_weight: int = 1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
        n_jobs: int = -1,
        early_stopping_rounds: int = 50
    ):
        """
        Initialize XGBoost forecaster with Colab script parameters.
        
        Args:
            n_estimators: Number of boosting rounds
            learning_rate: Step size shrinkage
            max_depth: Maximum tree depth
            min_child_weight: Minimum sum of instance weight needed in a child
            subsample: Subsample ratio of training instances
            colsample_bytree: Subsample ratio of columns when constructing each tree
            random_state: Random seed
            n_jobs: Number of parallel threads
            early_stopping_rounds: Early stopping rounds
        """
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost not available. Install with: pip install xgboost")
        
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_child_weight = min_child_weight
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.early_stopping_rounds = early_stopping_rounds
        
        self.model = None
        self.feature_names = None
        self.is_trained = False
        self.eval_results = None
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        verbose: bool = False
    ) -> Dict[str, List[float]]:
        """
        Train XGBoost model matching Colab script.
        
        Args:
            X_train: Training features DataFrame
            y_train: Training target Series
            X_val: Validation features DataFrame (optional)
            y_val: Validation target Series (optional)
            verbose: Whether to print training progress
        
        Returns:
            Dictionary with evaluation results
        """
        # Store feature names
        self.feature_names = X_train.columns.tolist()
        
        # Create model with Colab script parameters
        self.model = xgb.XGBRegressor(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            min_child_weight=self.min_child_weight,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            random_state=self.random_state,
            n_jobs=self.n_jobs,
            eval_metric=['rmse', 'mae'],
            early_stopping_rounds=self.early_stopping_rounds
        )
        
        logger.info("Training XGBoost model...")
        
        # Prepare eval_set
        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))
        
        # Train model
        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            verbose=verbose
        )
        
        # Store evaluation results
        self.eval_results = self.model.evals_result()
        self.is_trained = True
        
        logger.info("Model training completed")
        
        return self.eval_results
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Generate predictions.
        
        Args:
            X: Features DataFrame
        
        Returns:
            Predictions array
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = self.model.predict(X)
        return predictions
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance matching Colab script format.
        
        Returns:
            DataFrame with feature names and importance scores
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model not trained")
        
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return feature_importance
    
    def get_eval_results(self) -> Optional[Dict]:
        """
        Get training history (RMSE over rounds).
        
        Returns:
            Dictionary with evaluation results or None
        """
        return self.eval_results

