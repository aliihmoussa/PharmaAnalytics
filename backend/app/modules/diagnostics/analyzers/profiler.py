"""Main profiling engine for drug demand data - optimized for performance."""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from backend.app.database.models import DrugTransaction
from backend.app.database.session import get_db_session
from .seasonality import SeasonalityDetector
from .outliers import OutlierDetector
from .decomposition import TimeSeriesDecomposer
from .autocorrelation import AutocorrelationAnalyzer
from .classifier import DrugClassifier
import logging

logger = logging.getLogger(__name__)


class DrugProfiler:
    """High-performance drug demand profiler with caching support."""
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize profiler.
        
        Args:
            use_cache: Whether to use caching (default: True)
        """
        self.use_cache = use_cache
        self.seasonality_detector = SeasonalityDetector()
        self.outlier_detector = OutlierDetector()
        self.decomposer = TimeSeriesDecomposer()
        self.autocorr_analyzer = AutocorrelationAnalyzer()
        self.classifier = DrugClassifier()
    
    def load_daily_demand(
        self,
        drug_code: str,
        department: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.Series:
        """
        Load daily demand data with optimized query.
        
        Args:
            drug_code: Drug code
            department: Optional department filter (cr)
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            Series with date index and demand values
        """
        if end_date is None:
            end_date = date.today()
        
        if start_date is None:
            # Default: 2 years
            start_date = end_date - timedelta(days=730)
        
        session = get_db_session()
        try:
            # Optimized query: single aggregation with date filter
            query = session.query(
                func.date(DrugTransaction.transaction_date).label('date'),
                func.sum(func.abs(DrugTransaction.quantity)).label('demand')
            ).filter(
                DrugTransaction.drug_code == drug_code,
                DrugTransaction.transaction_date >= start_date,
                DrugTransaction.transaction_date <= end_date,
                DrugTransaction.quantity < 0  # Only consumption
            )
            
            if department is not None:
                query = query.filter(DrugTransaction.cr == department)
            
            query = query.group_by(
                func.date(DrugTransaction.transaction_date)
            ).order_by(
                func.date(DrugTransaction.transaction_date)
            )
            
            results = query.all()
            
            if not results:
                return pd.Series(dtype=float)
            
            # Convert to Series with date index (vectorized)
            data_dict = {
                pd.to_datetime(row.date): float(row.demand) if row.demand else 0.0
                for row in results
            }
            
            series = pd.Series(data_dict)
            series.name = 'demand'
            
            # Fill missing dates with 0 and ensure continuous index
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            series = series.reindex(date_range, fill_value=0.0)
            
            return series
            
        except Exception as e:
            logger.error(f"Error loading daily demand for {drug_code}: {str(e)}", exc_info=True)
            raise
        finally:
            session.close()
    
    def profile(
        self,
        drug_code: str,
        department: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Complete profiling of drug demand data.
        
        Args:
            drug_code: Drug code to profile
            department: Optional department filter
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            Dictionary with complete profiling results
        """
        logger.info(f"Profiling drug_code={drug_code}, department={department}")
        
        # Load data (optimized query)
        demand_series = self.load_daily_demand(
            drug_code=drug_code,
            department=department,
            start_date=start_date,
            end_date=end_date
        )
        
        if len(demand_series) == 0:
            raise ValueError(f"No data found for drug_code={drug_code}")
        
        # Basic statistics (vectorized operations)
        total_days = len(demand_series)
        missing_days = demand_series.isna().sum()
        zero_demand_days = (demand_series == 0).sum()
        zero_frequency = zero_demand_days / total_days if total_days > 0 else 0.0
        
        # Data health metrics
        data_health = {
            'history_length_days': total_days,
            'missing_days': int(missing_days),
            'missing_percentage': float(missing_days / total_days * 100) if total_days > 0 else 0.0,
            'zero_demand_frequency': float(zero_frequency),
            'zero_demand_count': int(zero_demand_days),
            'data_completeness_score': float(1.0 - (missing_days / total_days)) if total_days > 0 else 0.0,
            'date_range': {
                'start': demand_series.index.min().isoformat(),
                'end': demand_series.index.max().isoformat()
            }
        }
        
        # Outlier detection (optimized)
        outlier_results = self.outlier_detector.detect(demand_series)
        data_health['outlier_count'] = outlier_results['count']
        data_health['outlier_percentage'] = outlier_results['percentage']
        
        # Time-series characteristics (vectorized)
        mean_demand = demand_series.mean()
        std_demand = demand_series.std()
        volatility = float(std_demand / mean_demand) if mean_demand > 0 else 0.0
        
        # Trend analysis (simple linear trend)
        if len(demand_series) > 1:
            x = np.arange(len(demand_series))
            y = demand_series.values
            trend_coef = np.polyfit(x, y, 1)[0]
            trend = 'increasing' if trend_coef > 0.01 else ('decreasing' if trend_coef < -0.01 else 'stable')
        else:
            trend = 'stable'
        
        time_series_chars = {
            'mean_demand': float(mean_demand),
            'std_demand': float(std_demand),
            'volatility': volatility,
            'trend': trend,
            'min_demand': float(demand_series.min()),
            'max_demand': float(demand_series.max()),
            'median_demand': float(demand_series.median())
        }
        
        # Stationarity test (simplified ADF test)
        # For performance, use simple variance ratio test
        if len(demand_series) > 30:
            first_half = demand_series[:len(demand_series)//2].var()
            second_half = demand_series[len(demand_series)//2:].var()
            variance_ratio = second_half / first_half if first_half > 0 else 1.0
            # Simple heuristic: if variance ratio is close to 1, likely stationary
            is_stationary = 0.8 < variance_ratio < 1.2
            time_series_chars['stationarity'] = 'stationary' if is_stationary else 'non-stationary'
        else:
            time_series_chars['stationarity'] = 'unknown'
        
        # Seasonality detection (optimized)
        seasonality_results = self.seasonality_detector.detect(demand_series)
        time_series_chars.update(seasonality_results)
        
        # Decomposition (only if sufficient data)
        decomposition_results = {}
        if len(demand_series) > 60:  # Need at least 2 months
            try:
                decomposition_results = self.decomposer.decompose(demand_series)
            except Exception as e:
                logger.warning(f"Decomposition failed: {str(e)}")
                decomposition_results = {'error': str(e)}
        else:
            decomposition_results = {'insufficient_data': True}
        
        # ACF/PACF analysis (only if sufficient data)
        acf_pacf_results = {}
        if len(demand_series) > 30:
            try:
                acf_pacf_results = self.autocorr_analyzer.analyze(demand_series)
            except Exception as e:
                logger.warning(f"ACF/PACF analysis failed: {str(e)}")
                acf_pacf_results = {'error': str(e)}
        else:
            acf_pacf_results = {'insufficient_data': True}
        
        # Drug classification
        classification = self.classifier.classify(
            demand_series,
            seasonality_results,
            volatility,
            zero_frequency
        )
        
        # Risk assessment
        risks = self._assess_risks(
            data_health,
            time_series_chars,
            classification,
            total_days
        )
        
        # Compile results
        result = {
            'drug_code': drug_code,
            'department': department,
            'data_health': data_health,
            'time_series_characteristics': time_series_chars,
            'outliers': outlier_results,
            'decomposition': decomposition_results,
            'acf_pacf': acf_pacf_results,
            'classification': classification,
            'risks': risks,
            'profiled_at': pd.Timestamp.now().isoformat()
        }
        
        return result
    
    def _assess_risks(
        self,
        data_health: Dict,
        time_series_chars: Dict,
        classification: Dict,
        total_days: int
    ) -> Dict:
        """Assess risks and data quality issues."""
        risks = {
            'data_quality_issues': [],
            'forecast_reliability': 'high',
            'recommendations': []
        }
        
        # Check data completeness
        if data_health['missing_percentage'] > 10:
            risks['data_quality_issues'].append(
                f"High missing data: {data_health['missing_percentage']:.1f}%"
            )
            risks['forecast_reliability'] = 'medium'
        
        if data_health['outlier_percentage'] > 5:
            risks['data_quality_issues'].append(
                f"High outlier rate: {data_health['outlier_percentage']:.1f}%"
            )
        
        # Check history length
        if total_days < 60:
            risks['data_quality_issues'].append(
                f"Insufficient history: {total_days} days (minimum 60 recommended)"
            )
            risks['forecast_reliability'] = 'low'
            risks['recommendations'].append("Collect more historical data")
        elif total_days < 180:
            risks['recommendations'].append("More data would improve forecast accuracy")
        
        # Check for high volatility
        if time_series_chars.get('volatility', 0) > 0.5:
            risks['data_quality_issues'].append("High volatility detected")
            risks['recommendations'].append("Consider using robust forecasting methods")
        
        # Check for intermittency
        if classification.get('category') == 'intermittent':
            risks['recommendations'].append("Use intermittent demand forecasting methods")
        
        # Positive recommendations
        if time_series_chars.get('seasonality_detected'):
            risks['recommendations'].append("Strong seasonality detected - use seasonal models")
        
        if risks['forecast_reliability'] == 'high' and total_days >= 180:
            risks['recommendations'].append("Data quality is good for accurate forecasting")
        
        return risks

