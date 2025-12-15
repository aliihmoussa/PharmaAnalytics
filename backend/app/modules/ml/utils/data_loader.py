"""Data loader for ML training - loads data directly from PostgreSQL."""

from typing import Optional, List, Dict
from datetime import date, timedelta
import polars as pl
from backend.app.modules.dashboard.queries import AnalyticsDAL
import logging

logger = logging.getLogger(__name__)


class MLDataLoader:
    """
    Load ML training data directly from PostgreSQL.
    Reuses existing optimized queries from AnalyticsDAL.
    """
    
    def __init__(self):
        """Initialize data loader."""
        self.dal = AnalyticsDAL()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_drug_demand_data(
        self,
        drug_code: Optional[str] = None,
        department: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        training_months: int = 24,  # Limit to recent data for performance
        granularity: str = 'daily'  # 'daily', 'weekly', 'monthly'
    ) -> pl.DataFrame:
        """
        Load and aggregate transaction data for forecasting.
        
        Optimizations:
        - Uses existing indexed queries from AnalyticsDAL
        - Limits training window (default: 24 months)
        - Aggregates at database level
        
        Args:
            drug_code: Optional drug code filter
            department: Optional department filter
            start_date: Optional start date (defaults to training_months ago)
            end_date: Optional end date (defaults to today)
            training_months: Number of months of training data (default: 24)
            granularity: Time granularity ('daily', 'weekly', 'monthly')
        
        Returns:
            Polars DataFrame with columns: date, demand, drug_code (if not filtered)
        """
        # Set defaults
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=training_months * 30)
        
        self.logger.info(
            f"Loading demand data: drug_code={drug_code}, "
            f"start_date={start_date}, end_date={end_date}, granularity={granularity}"
        )
        
        try:
            with self.dal:
                # Use existing optimized query (already aggregates efficiently)
                raw_data = self.dal.get_drug_demand_time_series(
                    start_date=start_date,
                    end_date=end_date,
                    drug_code=drug_code,
                    granularity=granularity
                )
            
            if not raw_data:
                self.logger.warning(f"No data found for drug_code={drug_code}")
                return pl.DataFrame()
            
            # Convert to Polars DataFrame
            df = pl.DataFrame(raw_data)
            
            # Ensure date column is proper date type
            if 'date' in df.columns:
                # Handle different date formats
                if df['date'].dtype == pl.Utf8:
                    try:
                        df = df.with_columns(
                            pl.col('date').str.strptime(pl.Date, format="%Y-%m-%d")
                        )
                    except:
                        # Try alternative format
                        try:
                            df = df.with_columns(
                                pl.col('date').str.strptime(pl.Date, format="%Y-%m-%d %H:%M:%S")
                            )
                        except:
                            # If date is already a date object from DB, convert to string first
                            df = df.with_columns(
                                pl.col('date').cast(pl.Date)
                            )
                df = df.sort('date')
            
            # Rename columns for consistency
            if 'quantity' in df.columns:
                df = df.rename({'quantity': 'demand'})
            
            self.logger.info(f"Loaded {len(df)} records")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading demand data: {str(e)}", exc_info=True)
            raise
    
    def load_multiple_drugs(
        self,
        drug_codes: List[str],
        training_months: int = 24,
        granularity: str = 'daily'
    ) -> pl.DataFrame:
        """
        Load data for multiple drugs efficiently.
        
        Args:
            drug_codes: List of drug codes to load
            training_months: Number of months of training data
            granularity: Time granularity
        
        Returns:
            Combined DataFrame with drug_code column
        """
        all_data = []
        
        for drug_code in drug_codes:
            try:
                df = self.load_drug_demand_data(
                    drug_code=drug_code,
                    training_months=training_months,
                    granularity=granularity
                )
                if not df.is_empty():
                    df = df.with_columns(pl.lit(drug_code).alias('drug_code'))
                    all_data.append(df)
            except Exception as e:
                self.logger.warning(f"Failed to load data for {drug_code}: {str(e)}")
                continue
        
        if not all_data:
            return pl.DataFrame()
        
        return pl.concat(all_data)
    
    def get_historical_demand(
        self,
        drug_code: str,
        days_back: int = 90
    ) -> List[Dict]:
        """
        Get recent historical demand for visualization.
        
        Args:
            drug_code: Drug code
            days_back: Number of days to look back
        
        Returns:
            List of dictionaries with date and demand
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        with self.dal:
            raw_data = self.dal.get_drug_demand_time_series(
                start_date=start_date,
                end_date=end_date,
                drug_code=drug_code,
                granularity='daily'
            )
        
        # Format for frontend
        return [
            {
                'date': row['date'].isoformat() if isinstance(row['date'], date) else str(row['date']),
                'demand': int(row.get('quantity', 0))
            }
            for row in raw_data
        ]

