"""Drug demand forecasting service using Gradient Boosting."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
import pickle
import json
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from backend.app.database.models import DrugTransaction
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
import holidays


class DrugDemandForecaster:
    """Drug demand forecasting service using Gradient Boosting."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.models: Dict[str, GradientBoostingRegressor] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: Dict[str, List[str]] = {}  # Store feature names for each drug
        self.holidays_calendar = holidays.CountryHoliday('SA')  # Saudi Arabia holidays

    def prepare_training_data(self, drug_code: str, lookback_days: int = 365) -> pd.DataFrame:
        """
        Prepare historical data for a specific drug.

        Args:
            drug_code: Drug code to forecast
            lookback_days: Number of days to look back for training

        Returns:
            DataFrame with features and target
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=lookback_days)

        # Fetch historical data
        query = self.db.query(
            DrugTransaction.transaction_date,
            DrugTransaction.quantity,
            DrugTransaction.cr,
            DrugTransaction.cat,
            DrugTransaction.unit_price,
            extract('dow', DrugTransaction.transaction_date).label('day_of_week'),
            extract('month', DrugTransaction.transaction_date).label('month'),
            extract('day', DrugTransaction.transaction_date).label('day_of_month'),
            extract('week', DrugTransaction.transaction_date).label('week_of_year'),
            extract('quarter', DrugTransaction.transaction_date).label('quarter')
        ).filter(
            DrugTransaction.drug_code == drug_code,
            DrugTransaction.transaction_date >= start_date,
            DrugTransaction.transaction_date <= end_date,
            DrugTransaction.quantity < 0  # Only consumption (negative quantities)
        ).order_by(DrugTransaction.transaction_date)

        # Convert to DataFrame
        df = pd.read_sql(query.statement, self.db.bind)

        if df.empty:
            return df

        # Aggregate daily consumption (sum negative quantities as positive demand)
        daily_demand = df.groupby('transaction_date').agg({
            'quantity': lambda x: abs(x.sum()),
            'cr': lambda x: x.mode()[0] if not x.empty else None,
            'cat': lambda x: x.mode()[0] if not x.empty else None,
            'unit_price': 'mean',
            'day_of_week': 'first',
            'month': 'first',
            'day_of_month': 'first',
            'week_of_year': 'first',
            'quarter': 'first'
        }).reset_index()

        # Add additional features
        daily_demand['is_weekend'] = daily_demand['day_of_week'].isin([5, 6]).astype(int)  # Fri=5, Sat=6
        daily_demand['is_holiday'] = daily_demand['transaction_date'].apply(
            lambda x: 1 if x in self.holidays_calendar else 0
        )
        daily_demand['day_of_year'] = daily_demand['transaction_date'].apply(
            lambda x: x.timetuple().tm_yday
        )

        # Create lag features
        for lag in [1, 7, 14, 30]:
            daily_demand[f'demand_lag_{lag}'] = daily_demand['quantity'].shift(lag)

        # Create rolling statistics
        daily_demand['demand_rolling_7_mean'] = daily_demand['quantity'].rolling(7, min_periods=1).mean()
        daily_demand['demand_rolling_30_mean'] = daily_demand['quantity'].rolling(30, min_periods=1).mean()
        daily_demand['demand_rolling_7_std'] = daily_demand['quantity'].rolling(7, min_periods=1).std()

        # Drop NaN values
        daily_demand = daily_demand.dropna()

        return daily_demand

    def train_model(self, drug_code: str, forecast_horizon: int = 30) -> Dict:
        """
        Train Gradient Boosting model for a specific drug.

        Args:
            drug_code: Drug code to forecast
            forecast_horizon: Number of days to forecast ahead

        Returns:
            Dictionary with training results and model info
        """
        # Prepare data
        data = self.prepare_training_data(drug_code)

        if len(data) < 30:  # Insufficient data
            return {
                'success': False,
                'message': f'Insufficient historical data for {drug_code}',
                'drug_code': drug_code
            }

        # Prepare features and target
        feature_columns = [
            'day_of_week', 'month', 'day_of_month', 'week_of_year', 'quarter',
            'is_weekend', 'is_holiday', 'day_of_year',
            'demand_lag_1', 'demand_lag_7', 'demand_lag_14', 'demand_lag_30',
            'demand_rolling_7_mean', 'demand_rolling_30_mean', 'demand_rolling_7_std'
        ]

        # Add categorical features if available
        categorical_cols = []
        if 'cr' in data.columns and data['cr'].notna().any():
            feature_columns.append('cr')
            categorical_cols.append('cr')

        if 'cat' in data.columns and data['cat'].notna().any():
            feature_columns.append('cat')
            categorical_cols.append('cat')

        X = data[feature_columns].copy()
        y = data['quantity'].values

        # Encode categorical features
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            X[col] = self.label_encoders[col].fit_transform(X[col].fillna(0))

        # Scale features
        if drug_code not in self.scalers:
            self.scalers[drug_code] = StandardScaler()

        X_scaled = self.scalers[drug_code].fit_transform(X)

        # Store feature names for this drug
        self.feature_names[drug_code] = feature_columns.copy()

        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        cv_scores = []

        for train_idx, val_idx in tscv.split(X_scaled):
            X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            # Initialize and train model
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
                n_iter_no_change=10,
                validation_fraction=0.1
            )

            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_val)
            mae = mean_absolute_error(y_val, y_pred)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            cv_scores.append({'mae': mae, 'rmse': rmse})

        # Train final model on all data
        final_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )

        final_model.fit(X_scaled, y)
        self.models[drug_code] = final_model

        # Get feature importance
        feature_importance = dict(zip(feature_columns, final_model.feature_importances_))

        return {
            'success': True,
            'drug_code': drug_code,
            'training_samples': len(data),
            'cv_scores': cv_scores,
            'feature_importance': feature_importance,
            'last_training_date': datetime.now().isoformat(),
            'forecast_horizon': forecast_horizon
        }

    def generate_forecast(self, drug_code: str, forecast_days: int = 30) -> Dict:
        """
        Generate forecast for a specific drug.

        Args:
            drug_code: Drug code to forecast
            forecast_days: Number of days to forecast

        Returns:
            Dictionary with forecast results
        """
        if drug_code not in self.models:
            # Train model if not already trained
            train_result = self.train_model(drug_code, forecast_days)
            if not train_result['success']:
                return train_result

        # Get last available data point
        latest_data = self.prepare_training_data(drug_code, lookback_days=60)

        if latest_data.empty:
            return {
                'success': False,
                'message': f'No recent data available for {drug_code}',
                'drug_code': drug_code
            }

        # Prepare base features for forecasting
        last_date = latest_data['transaction_date'].max()
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

        forecasts = []
        confidence_intervals = []

        # Get drug metadata
        drug_meta = self.db.query(
            DrugTransaction.drug_name,
            DrugTransaction.unit_price
        ).filter(
            DrugTransaction.drug_code == drug_code
        ).first()

        # Prepare initial feature vector
        current_features = latest_data.iloc[-1].copy()

        # Get feature names for this drug
        feature_columns = self.feature_names.get(drug_code, [])

        for forecast_date in forecast_dates:
            # Create feature vector for forecast date
            features = {
                'day_of_week': forecast_date.weekday(),
                'month': forecast_date.month,
                'day_of_month': forecast_date.day,
                'week_of_year': forecast_date.isocalendar()[1],
                'quarter': (forecast_date.month - 1) // 3 + 1,
                'is_weekend': 1 if forecast_date.weekday() in [5, 6] else 0,
                'is_holiday': 1 if forecast_date in self.holidays_calendar else 0,
                'day_of_year': forecast_date.timetuple().tm_yday
            }

            # Add lag features (using last known values)
            for lag in [1, 7, 14, 30]:
                lag_key = f'demand_lag_{lag}'
                if lag_key in current_features:
                    features[lag_key] = current_features[lag_key]
                else:
                    features[lag_key] = latest_data['quantity'].mean() if not latest_data.empty else 0

            # Add rolling statistics
            features['demand_rolling_7_mean'] = current_features.get(
                'demand_rolling_7_mean',
                latest_data['quantity'].tail(7).mean() if len(latest_data) >= 7 else latest_data['quantity'].mean()
            )
            features['demand_rolling_30_mean'] = current_features.get(
                'demand_rolling_30_mean',
                latest_data['quantity'].tail(30).mean() if len(latest_data) >= 30 else latest_data['quantity'].mean()
            )
            features['demand_rolling_7_std'] = current_features.get(
                'demand_rolling_7_std',
                latest_data['quantity'].tail(7).std() if len(latest_data) >= 7 else latest_data['quantity'].std()
            )

            # Add categorical features
            if 'cr' in latest_data.columns:
                features['cr'] = current_features.get('cr', latest_data['cr'].mode()[0] if not latest_data['cr'].mode().empty else 0)

            if 'cat' in latest_data.columns:
                features['cat'] = current_features.get('cat', latest_data['cat'].mode()[0] if not latest_data['cat'].mode().empty else 0)

            # Prepare feature vector for prediction
            feature_df = pd.DataFrame([features])

            # Encode categorical features
            for col in ['cr', 'cat']:
                if col in feature_df.columns and col in self.label_encoders:
                    feature_df[col] = self.label_encoders[col].transform(feature_df[col].fillna(0).astype(int))

            # Select only the features used during training (in correct order)
            if feature_columns:
                feature_df = feature_df.reindex(columns=feature_columns, fill_value=0)

            # Scale features
            X_scaled = self.scalers[drug_code].transform(feature_df)

            # Generate prediction
            prediction = self.models[drug_code].predict(X_scaled)[0]

            # Calculate confidence interval (using std of recent errors)
            if len(latest_data) >= 30:
                recent_data_features = latest_data[feature_columns].tail(30)
                recent_predictions = self.models[drug_code].predict(
                    self.scalers[drug_code].transform(recent_data_features)
                )
                error_std = np.std(recent_predictions - latest_data['quantity'].tail(30).values)
            else:
                error_std = latest_data['quantity'].std() if len(latest_data) > 1 else prediction * 0.1

            ci_lower = max(0, prediction - 1.96 * error_std)
            ci_upper = prediction + 1.96 * error_std

            forecasts.append({
                'date': forecast_date.isoformat(),
                'predicted_demand': float(prediction),
                'confidence_lower': float(ci_lower),
                'confidence_upper': float(ci_upper),
                'day_of_week': forecast_date.strftime('%A'),
                'is_weekend': features['is_weekend'] == 1,
                'is_holiday': features['is_holiday'] == 1
            })

            # Update current_features for next iteration (simplified)
            current_features['quantity'] = prediction
            current_features['demand_lag_1'] = prediction

        # Calculate summary statistics
        total_forecast = sum(f['predicted_demand'] for f in forecasts)
        avg_daily = total_forecast / forecast_days

        # Prepare historical data for comparison (last 90 days)
        historical_data = self.prepare_training_data(drug_code, lookback_days=90)
        historical_for_chart = []
        
        if not historical_data.empty:
            # Get last 90 days of actual demand
            for _, row in historical_data.tail(90).iterrows():
                historical_for_chart.append({
                    'date': row['transaction_date'].isoformat() if isinstance(row['transaction_date'], date) else str(row['transaction_date']),
                    'demand': float(row['quantity']),
                    'type': 'actual'
                })

        return {
            'success': True,
            'drug_code': drug_code,
            'drug_name': drug_meta.drug_name if drug_meta else 'Unknown',
            'unit_price': float(drug_meta.unit_price) if drug_meta else 0,
            'forecast_generated': datetime.now().isoformat(),
            'forecast_period': {
                'start_date': forecast_dates[0].isoformat(),
                'end_date': forecast_dates[-1].isoformat(),
                'days': forecast_days
            },
            'summary': {
                'total_predicted_demand': float(total_forecast),
                'average_daily_demand': float(avg_daily),
                'peak_demand_day': max(forecasts, key=lambda x: x['predicted_demand'])['date'],
                'peak_demand_value': max(f['predicted_demand'] for f in forecasts),
                'total_predicted_cost': float(total_forecast * (drug_meta.unit_price if drug_meta else 0))
            },
            # Chart-ready data
            'chart_data': {
                'historical': historical_for_chart,
                'forecast': [
                    {
                        'date': f['date'],
                        'demand': f['predicted_demand'],
                        'confidence_lower': f['confidence_lower'],
                        'confidence_upper': f['confidence_upper'],
                        'type': 'predicted'
                    }
                    for f in forecasts
                ]
            },
            # Detailed forecast data (for tables/details)
            'daily_forecasts': forecasts,
            'recommendations': self.generate_recommendations(forecasts, drug_meta),
            # Chart configuration for frontend
            'chart_config': {
                'type': 'line',
                'title': f'Demand Forecast: {drug_meta.drug_name if drug_meta else drug_code}',
                'x_axis': 'date',
                'y_axis': 'demand',
                'series': [
                    {
                        'name': 'Historical Demand',
                        'data_key': 'demand',
                        'color': '#3b82f6',  # Blue
                        'type': 'line',
                        'stroke_width': 2
                    },
                    {
                        'name': 'Predicted Demand',
                        'data_key': 'demand',
                        'color': '#f59e0b',  # Orange
                        'type': 'line',
                        'stroke_dasharray': '5 5',
                        'stroke_width': 2
                    },
                    {
                        'name': 'Confidence Interval',
                        'data_key': ['confidence_lower', 'confidence_upper'],
                        'color': '#f59e0b',
                        'type': 'area',
                        'opacity': 0.2,
                        'fill': True
                    }
                ]
            }
        }

    def generate_recommendations(self, forecasts: List[Dict], drug_meta) -> List[Dict]:
        """Generate inventory recommendations based on forecast."""
        recommendations = []

        if not forecasts:
            return recommendations

        # Calculate safety stock (95th percentile of demand)
        demands = [f['predicted_demand'] for f in forecasts]
        safety_stock = np.percentile(demands, 95)

        # Calculate reorder point
        lead_time_days = 7  # Assuming 7-day lead time
        avg_daily_demand = np.mean(demands)
        reorder_point = (avg_daily_demand * lead_time_days) + safety_stock

        # Calculate economic order quantity (simplified)
        annual_demand = avg_daily_demand * 365
        order_cost = 100  # Fixed cost per order
        holding_cost_rate = 0.25  # 25% of unit cost
        unit_cost = drug_meta.unit_price if drug_meta else 0

        if unit_cost > 0:
            eoq = np.sqrt((2 * annual_demand * order_cost) / (holding_cost_rate * unit_cost))
        else:
            eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost_rate)

        recommendations.append({
            'type': 'SAFETY_STOCK',
            'value': float(safety_stock),
            'description': f'Recommended safety stock to cover 95% of demand variability'
        })

        recommendations.append({
            'type': 'REORDER_POINT',
            'value': float(reorder_point),
            'description': f'Reorder when inventory falls below this level (based on {lead_time_days}-day lead time)'
        })

        recommendations.append({
            'type': 'ECONOMIC_ORDER_QUANTITY',
            'value': float(eoq),
            'description': f'Optimal order quantity to minimize total inventory costs'
        })

        # Check for upcoming high-demand periods
        high_demand_days = [f for f in forecasts if f['predicted_demand'] > safety_stock * 1.5]
        if high_demand_days:
            recommendations.append({
                'type': 'HIGH_DEMAND_ALERT',
                'dates': [f['date'] for f in high_demand_days[:3]],  # Top 3
                'description': 'Expected high demand days - consider additional stock'
            })

        return recommendations

    def batch_forecast_top_drugs(self, limit: int = 50, forecast_days: int = 30) -> Dict:
        """Generate forecasts for top N most consumed drugs."""

        # Get top drugs by consumption
        top_drugs_query = self.db.query(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name,
            func.sum(func.abs(DrugTransaction.quantity)).label('total_consumption'),
            func.count(DrugTransaction.id).label('transaction_count')
        ).filter(
            DrugTransaction.quantity < 0,
            DrugTransaction.transaction_date >= datetime.now().date() - timedelta(days=90)
        ).group_by(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name
        ).order_by(
            func.sum(func.abs(DrugTransaction.quantity)).desc()
        ).limit(limit)

        top_drugs = top_drugs_query.all()

        results = []
        for drug in top_drugs:
            try:
                forecast = self.generate_forecast(drug.drug_code, forecast_days)
                if forecast['success']:
                    results.append(forecast)
            except Exception as e:
                results.append({
                    'success': False,
                    'drug_code': drug.drug_code,
                    'drug_name': drug.drug_name,
                    'error': str(e)
                })

        return {
            'total_drugs_forecasted': len([r for r in results if r['success']]),
            'total_drugs_failed': len([r for r in results if not r['success']]),
            'forecast_date': datetime.now().isoformat(),
            'forecast_horizon_days': forecast_days,
            'results': results
        }

    def save_model(self, drug_code: str, filepath: str):
        """Save trained model to file."""
        if drug_code in self.models:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'model': self.models[drug_code],
                    'scaler': self.scalers[drug_code],
                    'label_encoders': self.label_encoders,
                    'feature_names': self.feature_names.get(drug_code, []),
                    'metadata': {
                        'drug_code': drug_code,
                        'saved_date': datetime.now().isoformat()
                    }
                }, f)

    def load_model(self, drug_code: str, filepath: str):
        """Load trained model from file."""
        with open(filepath, 'rb') as f:
            saved_data = pickle.load(f)
            self.models[drug_code] = saved_data['model']
            self.scalers[drug_code] = saved_data['scaler']
            self.label_encoders.update(saved_data.get('label_encoders', {}))
            if 'feature_names' in saved_data:
                self.feature_names[drug_code] = saved_data['feature_names']

