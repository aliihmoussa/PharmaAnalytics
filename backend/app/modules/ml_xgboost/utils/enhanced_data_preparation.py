"""Enhanced data preparation - load full transaction details with metadata for feature engineering."""

import pandas as pd
import numpy as np
from typing import Optional, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from backend.app.database.models import DrugTransaction
from backend.app.database.session import get_db_session
import logging

logger = logging.getLogger(__name__)


def load_enhanced_transaction_data(
    drug_code: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    lookback_days: Optional[int] = None
) -> pd.DataFrame:
    """
    Load full transaction data with all metadata for enhanced feature engineering.
    
    Args:
        drug_code: Drug code to load
        start_date: Optional start date
        end_date: Optional end date (defaults to today)
        lookback_days: Optional number of days to look back
    
    Returns:
        DataFrame with daily aggregated data including metadata
    """
    if end_date is None:
        end_date = date.today()
    
    if start_date is None:
        if lookback_days:
            start_date = end_date - timedelta(days=lookback_days)
        else:
            # Default: 2 years of data
            start_date = end_date - timedelta(days=730)
    
    logger.info(f"Loading enhanced transaction data for {drug_code} from {start_date} to {end_date}")
    
    session = get_db_session()
    try:
        # First, get basic daily aggregations
        query = session.query(
            func.date(DrugTransaction.transaction_date).label('date'),
            func.sum(func.abs(DrugTransaction.quantity)).filter(
                DrugTransaction.quantity < 0
            ).label('quantity'),
            func.sum(DrugTransaction.total_price).filter(
                DrugTransaction.quantity < 0
            ).label('total_value'),
            func.count().filter(DrugTransaction.quantity < 0).label('transaction_count'),
            func.count(func.distinct(DrugTransaction.cr)).label('unique_depts'),
            func.count(func.distinct(DrugTransaction.room_number)).label('unique_rooms'),
            func.count(func.distinct(DrugTransaction.bed_number)).label('unique_beds'),
            func.avg(DrugTransaction.unit_price).label('avg_unit_price'),
            func.stddev(DrugTransaction.unit_price).label('unit_price_std')
        ).filter(
            DrugTransaction.drug_code == drug_code,
            DrugTransaction.transaction_date >= start_date,
            DrugTransaction.transaction_date <= end_date,
            DrugTransaction.quantity < 0  # Only consumption
        ).group_by(
            func.date(DrugTransaction.transaction_date)
        ).order_by(
            func.date(DrugTransaction.transaction_date)
        )
        
        results = query.all()
        
        if not results:
            raise ValueError(
                f"No data found for drug_code={drug_code} "
                f"between {start_date} and {end_date}"
            )
        
        # Load all transaction details for mode calculations (more efficient)
        detail_query = session.query(
            func.date(DrugTransaction.transaction_date).label('date'),
            DrugTransaction.cr,
            DrugTransaction.cs,
            DrugTransaction.cat,
            DrugTransaction.ad_date
        ).filter(
            DrugTransaction.drug_code == drug_code,
            DrugTransaction.transaction_date >= start_date,
            DrugTransaction.transaction_date <= end_date,
            DrugTransaction.quantity < 0
        ).all()
        
        # Convert to DataFrame for efficient processing
        detail_df = pd.DataFrame([
            {
                'date': row.date,
                'cr': row.cr,
                'cs': row.cs,
                'cat': row.cat,
                'ad_date': row.ad_date
            }
            for row in detail_query
        ])
        
        # Calculate modes per day using pandas
        data_dicts = []
        for agg_row in results:
            date_val = agg_row.date
            
            # Filter transactions for this day
            day_details = detail_df[detail_df['date'] == date_val]
            
            # Calculate modes (most common values)
            top_cr = day_details['cr'].mode().iloc[0] if len(day_details['cr'].mode()) > 0 else None
            top_cs = day_details['cs'].mode().iloc[0] if len(day_details['cs'].mode()) > 0 else None
            top_cat = day_details['cat'].mode().iloc[0] if len(day_details['cat'].mode()) > 0 else None
            top_ad_date = day_details['ad_date'].mode().iloc[0] if len(day_details['ad_date'].mode()) > 0 else None
            
            # Calculate average admission lag
            if top_ad_date and day_details['ad_date'].notna().any():
                lags = (pd.to_datetime(date_val) - pd.to_datetime(day_details['ad_date'])).dt.days
                lags = lags[lags >= 0]  # Only positive lags
                avg_lag = float(lags.mean()) if len(lags) > 0 else 0.0
            else:
                avg_lag = 0.0
            
            data_dicts.append({
                'date': date_val,
                'QTY': float(agg_row.quantity) if agg_row.quantity else 0.0,
                'total_value': float(agg_row.total_value) if agg_row.total_value else 0.0,
                'transaction_count': agg_row.transaction_count or 0,
                'top_consuming_dept': int(top_cr) if top_cr is not None else None,
                'unique_depts': agg_row.unique_depts or 0,
                'top_supplying_dept': int(top_cs) if top_cs is not None else None,
                'top_category': int(top_cat) if top_cat is not None else None,
                'unique_rooms': agg_row.unique_rooms or 0,
                'unique_beds': agg_row.unique_beds or 0,
                'avg_unit_price': float(agg_row.avg_unit_price) if agg_row.avg_unit_price else 0.0,
                'unit_price_std': float(agg_row.unit_price_std) if agg_row.unit_price_std else 0.0,
                'avg_admission_lag': avg_lag,
                'ad_date': top_ad_date
            })
        
        df = pd.DataFrame(data_dicts)
        
        # Set date as index
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df.index.name = 'DATE'
        
        logger.info(f"Loaded {len(df)} days of enhanced transaction data")
        logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
        logger.info(f"Columns: {df.columns.tolist()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading enhanced transaction data: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()


def get_category_demand_data(
    category_id: int,
    start_date: date,
    end_date: date
) -> pd.Series:
    """
    Get category-level demand time series for category trend features.
    
    Args:
        category_id: Category ID
        start_date: Start date
        end_date: End date
    
    Returns:
        Series with daily category demand
    """
    session = get_db_session()
    try:
        query = session.query(
            func.date(DrugTransaction.transaction_date).label('date'),
            func.sum(func.abs(DrugTransaction.quantity)).filter(
                DrugTransaction.quantity < 0
            ).label('quantity')
        ).filter(
            DrugTransaction.cat == category_id,
            DrugTransaction.transaction_date >= start_date,
            DrugTransaction.transaction_date <= end_date,
            DrugTransaction.quantity < 0
        ).group_by(
            func.date(DrugTransaction.transaction_date)
        ).order_by(
            func.date(DrugTransaction.transaction_date)
        )
        
        results = query.all()
        
        if not results:
            return pd.Series(dtype=float)
        
        data_dict = {
            pd.to_datetime(row.date): float(row.quantity) if row.quantity else 0.0
            for row in results
        }
        
        return pd.Series(data_dict)
        
    except Exception as e:
        logger.error(f"Error loading category demand: {str(e)}", exc_info=True)
        return pd.Series(dtype=float)
    finally:
        session.close()


def get_department_demand_data(
    department_id: int,
    start_date: date,
    end_date: date
) -> pd.Series:
    """
    Get department-level demand time series for department features.
    
    Args:
        department_id: Department ID (C.R)
        start_date: Start date
        end_date: End date
    
    Returns:
        Series with daily department demand
    """
    session = get_db_session()
    try:
        query = session.query(
            func.date(DrugTransaction.transaction_date).label('date'),
            func.sum(func.abs(DrugTransaction.quantity)).filter(
                DrugTransaction.quantity < 0
            ).label('quantity')
        ).filter(
            DrugTransaction.cr == department_id,
            DrugTransaction.transaction_date >= start_date,
            DrugTransaction.transaction_date <= end_date,
            DrugTransaction.quantity < 0
        ).group_by(
            func.date(DrugTransaction.transaction_date)
        ).order_by(
            func.date(DrugTransaction.transaction_date)
        )
        
        results = query.all()
        
        if not results:
            return pd.Series(dtype=float)
        
        data_dict = {
            pd.to_datetime(row.date): float(row.quantity) if row.quantity else 0.0
            for row in results
        }
        
        return pd.Series(data_dict)
        
    except Exception as e:
        logger.error(f"Error loading department demand: {str(e)}", exc_info=True)
        return pd.Series(dtype=float)
    finally:
        session.close()


def enrich_with_aggregated_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Enrich daily data with aggregated features from category and department data.
    
    Args:
        df: DataFrame with daily drug data
    
    Returns:
        DataFrame enriched with category and department demand features
    """
    enriched_df = df.copy()
    
    # Add category demand if category available
    if 'top_category' in enriched_df.columns:
        categories = enriched_df['top_category'].dropna().unique()
        if len(categories) > 0:
            category_id = int(categories[0])  # Use most common category
            start_date = enriched_df.index.min().date()
            end_date = enriched_df.index.max().date()
            
            category_demand = get_category_demand_data(category_id, start_date, end_date)
            if len(category_demand) > 0:
                # Align with main dataframe index
                enriched_df['category_demand'] = enriched_df.index.map(
                    lambda x: category_demand.get(x, 0.0)
                )
            else:
                enriched_df['category_demand'] = 0.0
    
    # Add top department demand
    if 'top_consuming_dept' in enriched_df.columns:
        depts = enriched_df['top_consuming_dept'].dropna().unique()
        if len(depts) > 0:
            dept_id = int(depts[0])  # Use most common department
            start_date = enriched_df.index.min().date()
            end_date = enriched_df.index.max().date()
            
            dept_demand = get_department_demand_data(dept_id, start_date, end_date)
            if len(dept_demand) > 0:
                enriched_df['top_dept_demand'] = enriched_df.index.map(
                    lambda x: dept_demand.get(x, 0.0)
                )
            else:
                enriched_df['top_dept_demand'] = 0.0
    
    # Add top supplying department demand
    if 'top_supplying_dept' in enriched_df.columns:
        supply_depts = enriched_df['top_supplying_dept'].dropna().unique()
        if len(supply_depts) > 0:
            supply_dept_id = int(supply_depts[0])
            start_date = enriched_df.index.min().date()
            end_date = enriched_df.index.max().date()
            
            supply_dept_demand = get_department_demand_data(supply_dept_id, start_date, end_date)
            if len(supply_dept_demand) > 0:
                enriched_df['top_supply_dept_demand'] = enriched_df.index.map(
                    lambda x: supply_dept_demand.get(x, 0.0)
                )
            else:
                enriched_df['top_supply_dept_demand'] = 0.0
    
    return enriched_df


def resample_to_daily_enhanced(df: pd.DataFrame, target_col: str = 'QTY') -> pd.DataFrame:
    """
    Resample enhanced data to daily frequency, preserving metadata.
    
    Args:
        df: DataFrame with date index and metadata columns
        target_col: Name of target column
    
    Returns:
        Daily resampled DataFrame with metadata
    """
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found")
    
    logger.info(f"Before resampling: {len(df)} records")
    
    # Resample to daily frequency
    # For numeric columns, use sum or mean as appropriate
    resampled = df.resample('D').agg({
        target_col: 'sum',
        'total_value': 'sum',
        'transaction_count': 'sum',
        'unique_depts': 'max',  # Max unique departments
        'unique_rooms': 'max',
        'unique_beds': 'max',
        'avg_unit_price': 'mean',
        'unit_price_std': 'mean',
        'avg_admission_lag': 'mean',
        'top_consuming_dept': lambda x: x.mode()[0] if len(x.mode()) > 0 else None,
        'top_supplying_dept': lambda x: x.mode()[0] if len(x.mode()) > 0 else None,
        'top_category': lambda x: x.mode()[0] if len(x.mode()) > 0 else None,
        'ad_date': lambda x: x.mode()[0] if len(x.mode()) > 0 else None
    })
    
    logger.info(f"After resampling: {len(resampled)} records")
    
    return resampled

