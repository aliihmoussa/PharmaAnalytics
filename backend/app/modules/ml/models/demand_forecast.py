"""Drug demand forecasting model implementation."""

from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import numpy (required for ML operations)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("numpy not available. Install with: pip install numpy")
    # Create a dummy np module to prevent errors
    class DummyNP:
        def __getattr__(self, name):
            raise ImportError("numpy is required. Install with: pip install numpy")
    np = DummyNP()

# Try to import joblib (required for model persistence)
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    logger.warning("joblib not available. Install with: pip install joblib")

# Try to import ML libraries (will fail gracefully if not installed)
try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost not available. Install with: pip install xgboost")

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Install with: pip install scikit-learn")


class DrugDemandForecaster:
    """
    Forecast drug demand using machine learning.
    
    Supports XGBoost and Random Forest models.
    """
    
    def __init__(self, model_type: str = 'xgboost'):
        """
        Initialize forecaster.
        
        Args:
            model_type: 'xgboost' or 'random_forest'
        """
        if model_type == 'xgboost' and not XGBOOST_AVAILABLE:
            logger.warning("XGBoost not available, falling back to Random Forest")
            model_type = 'random_forest'
        
        if model_type == 'random_forest' and not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for Random Forest model")
        
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        self.is_trained = False
        
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        **kwargs
    ) -> Dict[str, float]:
        """
        Train the forecasting model.
        
        Args:
            X_train: Training features (n_samples, n_features)
            y_train: Training targets (n_samples,)
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
            **kwargs: Additional model parameters
        
        Returns:
            Dictionary with training metrics
        """
        if self.model_type == 'xgboost':
            if not XGBOOST_AVAILABLE:
                raise ImportError("XGBoost not available")
            
            self.model = XGBRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 6),
                learning_rate=kwargs.get('learning_rate', 0.1),
                random_state=kwargs.get('random_state', 42),
                n_jobs=kwargs.get('n_jobs', -1)
            )
            
            # Use validation set if provided
            if X_val is not None and y_val is not None:
                self.model.fit(
                    X_train, y_train,
                    eval_set=[(X_val, y_val)],
                    verbose=kwargs.get('verbose', False)
                )
            else:
                self.model.fit(X_train, y_train)
                
        elif self.model_type == 'random_forest':
            if not SKLEARN_AVAILABLE:
                raise ImportError("scikit-learn not available")
            
            self.model = RandomForestRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 10),
                random_state=kwargs.get('random_state', 42),
                n_jobs=kwargs.get('n_jobs', -1)
            )
            
            self.model.fit(X_train, y_train)
        
        self.is_trained = True
        
        # Calculate metrics
        metrics = {}
        train_pred = self.model.predict(X_train)
        metrics['train_mae'] = float(mean_absolute_error(y_train, train_pred))
        metrics['train_rmse'] = float(np.sqrt(mean_squared_error(y_train, train_pred)))
        metrics['train_r2'] = float(r2_score(y_train, train_pred))
        
        if X_val is not None and y_val is not None:
            val_pred = self.model.predict(X_val)
            metrics['val_mae'] = float(mean_absolute_error(y_val, val_pred))
            metrics['val_rmse'] = float(np.sqrt(mean_squared_error(y_val, val_pred)))
            metrics['val_r2'] = float(r2_score(y_val, val_pred))
            
            # Calculate MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((y_val - val_pred) / (y_val + 1e-8))) * 100
            metrics['val_mape'] = float(mape)
        
        logger.info(f"Model trained. Metrics: {metrics}")
        return metrics
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Generate demand predictions.
        
        Args:
            X: Features (n_samples, n_features)
        
        Returns:
            Predictions (n_samples,)
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = self.model.predict(X)
        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)
        
        return predictions
    
    def predict_with_confidence(
        self,
        X: np.ndarray,
        confidence_level: float = 0.8
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate predictions with confidence intervals.
        
        Note: This is a simplified implementation. For proper confidence intervals,
        consider using quantile regression or ensemble methods.
        
        Args:
            X: Features
            confidence_level: Confidence level (default: 0.8 for 80% interval)
        
        Returns:
            Tuple of (predictions, lower_bounds, upper_bounds)
        """
        predictions = self.predict(X)
        
        # Simple confidence interval based on model's feature importance
        # In production, use proper uncertainty quantification
        std_estimate = np.std(predictions) * 0.15  # Rough estimate
        
        z_score = 1.28 if confidence_level == 0.8 else 1.96  # 80% or 95%
        
        lower_bounds = predictions - z_score * std_estimate
        upper_bounds = predictions + z_score * std_estimate
        
        # Ensure non-negative
        lower_bounds = np.maximum(lower_bounds, 0)
        
        return predictions, lower_bounds, upper_bounds
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model not trained")
        
        if self.model_type == 'xgboost':
            importances = self.model.feature_importances_
        elif self.model_type == 'random_forest':
            importances = self.model.feature_importances_
        else:
            return {}
        
        if self.feature_names and len(self.feature_names) == len(importances):
            return dict(zip(self.feature_names, importances.tolist()))
        else:
            return {f'feature_{i}': float(imp) for i, imp in enumerate(importances)}
    
    def save(self, filepath: str):
        """
        Save model to disk.
        
        Args:
            filepath: Path to save model
        """
        if not JOBLIB_AVAILABLE:
            raise ImportError("joblib is required for model persistence. Install with: pip install joblib")
        
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """
        Load model from disk.
        
        Args:
            filepath: Path to saved model
        
        Returns:
            Loaded DrugDemandForecaster instance
        """
        if not JOBLIB_AVAILABLE:
            raise ImportError("joblib is required for model loading. Install with: pip install joblib")
        
        model_data = joblib.load(filepath)
        
        forecaster = cls(model_type=model_data['model_type'])
        forecaster.model = model_data['model']
        forecaster.feature_names = model_data.get('feature_names')
        forecaster.is_trained = model_data.get('is_trained', True)
        
        logger.info(f"Model loaded from {filepath}")
        return forecaster

