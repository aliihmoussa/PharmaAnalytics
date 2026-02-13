"""Analytics Data Access Layer - Database queries using SQLAlchemy ORM."""

from typing import Dict, List, Optional
from datetime import date, datetime
from sqlalchemy import func, extract, case, String
from sqlalchemy.orm import Session
from backend.app.database.models import DrugTransaction
from backend.app.database.session import get_db_session


class AnalyticsDAL:
    """Data access layer for analytics queries using SQLAlchemy ORM."""
    
    def __init__(self):
        """Initialize the DAL with a database session."""
        self._session: Optional[Session] = None
    
    def __enter__(self):
        """Context manager entry - get a database session."""
        self._session = get_db_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close the database session."""
        if self._session:
            self._session.close()
            self._session = None
    
    def get_top_drugs(
        self,
        start_date: date,
        end_date: date,
        limit: int,
        category_id: Optional[int] = None,
        department_id: Optional[int] = None
    ) -> List[Dict]:
        """Get top dispensed drugs from database."""
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        query = self._session.query(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name,
            func.sum(func.abs(DrugTransaction.quantity)).label('total_qty'),
            func.sum(DrugTransaction.total_price).label('total_value'),
            func.count().label('transaction_count')
        ).filter(
            DrugTransaction.transaction_date.between(start_date, end_date),
            DrugTransaction.quantity < 0
        )
        
        if category_id:
            query = query.filter(DrugTransaction.cat == category_id)
        
        if department_id:
            query = query.filter(DrugTransaction.cr == department_id)
        
        results = query.group_by(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name
        ).order_by(
            func.sum(func.abs(DrugTransaction.quantity)).desc()
        ).limit(limit).all()
        
        return [
            {
                'drug_code': row.drug_code,
                'drug_name': row.drug_name,
                'total_qty': float(row.total_qty) if row.total_qty else 0.0,
                'total_value': float(row.total_value) if row.total_value else 0.0,
                'transaction_count': row.transaction_count
            }
            for row in results
        ]
    
    def get_drug_demand_time_series(
        self,
        start_date: date,
        end_date: date,
        drug_code: Optional[str] = None,
        granularity: str = 'daily'
    ) -> List[Dict]:
        """Get time-series demand data."""
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        # Map granularity to SQLAlchemy date_trunc format
        trunc_mapping = {
            'daily': 'day',
            'weekly': 'week',
            'monthly': 'month'
        }
        trunc_unit = trunc_mapping.get(granularity, 'day')
        
        query = self._session.query(
            func.date_trunc(trunc_unit, DrugTransaction.transaction_date).label('date'),
            func.sum(
                func.abs(DrugTransaction.quantity)
            ).filter(DrugTransaction.quantity < 0).label('quantity'),
            func.sum(
                DrugTransaction.total_price
            ).filter(DrugTransaction.quantity < 0).label('value'),
            func.count().filter(DrugTransaction.quantity < 0).label('transaction_count')
        ).filter(
            DrugTransaction.transaction_date.between(start_date, end_date)
        )
        
        if drug_code:
            query = query.filter(DrugTransaction.drug_code == drug_code)
        
        results = query.group_by(
            func.date_trunc(trunc_unit, DrugTransaction.transaction_date)
        ).order_by(
            func.date_trunc(trunc_unit, DrugTransaction.transaction_date)
        ).all()
        
        return [
            {
                'date': row.date,
                'quantity': float(row.quantity) if row.quantity else 0.0,
                'value': float(row.value) if row.value else 0.0,
                'transaction_count': row.transaction_count or 0
            }
            for row in results
        ]
    
    def get_summary_stats(self, start_date: Optional[date], end_date: Optional[date]) -> Dict:
        """Get overall statistics."""
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        query = self._session.query(
            func.count().filter(DrugTransaction.quantity < 0).label('total_dispensed'),
            func.sum(DrugTransaction.total_price).filter(DrugTransaction.quantity < 0).label('total_value'),
            func.count().label('total_transactions'),
            func.count(func.distinct(DrugTransaction.drug_code)).label('unique_drugs'),
            func.count(func.distinct(DrugTransaction.cr)).label('unique_departments')
        )
        
        if start_date and end_date:
            query = query.filter(
                DrugTransaction.transaction_date.between(start_date, end_date)
            )
        
        result = query.first()
        
        if result:
            return {
                'total_dispensed': result.total_dispensed or 0,
                'total_value': float(result.total_value) if result.total_value else 0.0,
                'total_transactions': result.total_transactions or 0,
                'unique_drugs': result.unique_drugs or 0,
                'unique_departments': result.unique_departments or 0
            }
        
        return {
            'total_dispensed': 0,
            'total_value': 0.0,
            'total_transactions': 0,
            'unique_drugs': 0,
            'unique_departments': 0
        }
    
    def get_seasonal_patterns(
        self,
        start_date: date,
        end_date: date,
        drug_code: Optional[str] = None
    ) -> List[Dict]:
        """Get seasonal patterns (monthly aggregations)."""
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        query = self._session.query(
            extract('month', DrugTransaction.transaction_date).label('month'),
            extract('year', DrugTransaction.transaction_date).label('year'),
            func.sum(
                func.abs(DrugTransaction.quantity)
            ).filter(DrugTransaction.quantity < 0).label('quantity'),
            func.sum(
                DrugTransaction.total_price
            ).filter(DrugTransaction.quantity < 0).label('value')
        ).filter(
            DrugTransaction.transaction_date.between(start_date, end_date)
        )
        
        if drug_code:
            query = query.filter(DrugTransaction.drug_code == drug_code)
        
        results = query.group_by(
            extract('month', DrugTransaction.transaction_date),
            extract('year', DrugTransaction.transaction_date)
        ).order_by(
            extract('year', DrugTransaction.transaction_date),
            extract('month', DrugTransaction.transaction_date)
        ).all()
        
        return [
            {
                'month': int(row.month),
                'year': int(row.year),
                'quantity': float(row.quantity) if row.quantity else 0.0,
                'value': float(row.value) if row.value else 0.0
            }
            for row in results
        ]
    
    def get_department_performance(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[Dict]:
        """Get department performance metrics."""
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        # Filter base query first, then aggregate (correct approach)
        # Only count consumption transactions (quantity < 0)
        results = self._session.query(
            DrugTransaction.cr.label('department_id'),
            func.count().label('transaction_count'),
            func.sum(func.abs(DrugTransaction.quantity)).label('total_dispensed'),
            func.sum(DrugTransaction.total_price).label('total_value'),
            func.count(func.distinct(DrugTransaction.drug_code)).label('unique_drugs')
        ).filter(
            DrugTransaction.transaction_date.between(start_date, end_date),
            DrugTransaction.quantity < 0  # Filter consumption transactions only
        ).group_by(
            DrugTransaction.cr
        ).order_by(
            func.sum(func.abs(DrugTransaction.quantity)).desc()
        ).limit(limit).all()
        
        return [
            {
                'department_id': row.department_id,
                'transaction_count': row.transaction_count,
                'total_dispensed': float(row.total_dispensed) if row.total_dispensed else 0.0,
                'total_value': float(row.total_value) if row.total_value else 0.0,
                'unique_drugs': row.unique_drugs
            }
            for row in results
        ]
    
    def get_year_comparison(
        self,
        metric_type: str = 'quantity',
        drug_code: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Dict]:
        """
        Get year-over-year comparison metrics.
        
        Args:
            metric_type: 'quantity', 'value', or 'transactions'
            drug_code: Optional drug code filter
            start_year: Optional start year (default: 2019)
            end_year: Optional end year (default: 2022)
        """
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        # Build metric selection based on type
        # Apply quantity < 0 filter at base query level (not on aggregation)
        if metric_type == 'quantity':
            metric_expr = func.sum(func.abs(DrugTransaction.quantity))
        elif metric_type == 'value':
            metric_expr = func.sum(DrugTransaction.total_price)
        else:  # transactions
            metric_expr = func.count()
        
        query = self._session.query(
            extract('year', DrugTransaction.transaction_date).label('year'),
            metric_expr.label('metric_value')
        ).filter(
            DrugTransaction.quantity < 0  # Filter consumption transactions only
        )
        
        if start_year:
            query = query.filter(
                extract('year', DrugTransaction.transaction_date) >= start_year
            )
        
        if end_year:
            query = query.filter(
                extract('year', DrugTransaction.transaction_date) <= end_year
            )
        
        if drug_code:
            query = query.filter(DrugTransaction.drug_code == drug_code)
        
        results = query.group_by(
            extract('year', DrugTransaction.transaction_date)
        ).order_by(
            extract('year', DrugTransaction.transaction_date)
        ).all()
        
        return [
            {
                'year': int(row.year),
                'metric_value': float(row.metric_value) if row.metric_value else 0.0
            }
            for row in results
        ]
    
    def get_category_analysis(
        self,
        start_date: date,
        end_date: date,
        granularity: str = 'monthly',
        limit: int = None
    ) -> List[Dict]:
        """
        Get drug category analysis over time.
        
        Args:
            start_date: Start date
            end_date: End date
            granularity: 'monthly' or 'quarterly'
            limit: Optional limit for top N categories (by total value)
        """
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        trunc_unit = 'quarter' if granularity == 'quarterly' else 'month'
        
        # If limit is specified, first get top categories by total value
        top_category_ids = None
        if limit and limit > 0:
            # Get top N categories by total value across all periods
            category_totals = self._session.query(
                DrugTransaction.cat.label('category_id'),
                func.sum(DrugTransaction.total_price).filter(
                    DrugTransaction.quantity < 0
                ).label('total_value')
            ).filter(
                DrugTransaction.transaction_date.between(start_date, end_date),
                DrugTransaction.cat.isnot(None)
            ).group_by(
                DrugTransaction.cat
            ).order_by(
                func.sum(DrugTransaction.total_price).filter(
                    DrugTransaction.quantity < 0
                ).desc()
            ).limit(limit).all()
            
            top_category_ids = [row.category_id for row in category_totals]
        
        # Main query for category analysis
        query = self._session.query(
            func.date_trunc(trunc_unit, DrugTransaction.transaction_date).label('period'),
            DrugTransaction.cat.label('category_id'),
            func.sum(
                func.abs(DrugTransaction.quantity)
            ).filter(DrugTransaction.quantity < 0).label('total_quantity'),
            func.sum(
                DrugTransaction.total_price
            ).filter(DrugTransaction.quantity < 0).label('total_value'),
            func.count().filter(DrugTransaction.quantity < 0).label('transaction_count'),
            func.count(func.distinct(DrugTransaction.drug_code)).label('unique_drugs')
        ).filter(
            DrugTransaction.transaction_date.between(start_date, end_date),
            DrugTransaction.cat.isnot(None)
        )
        
        # Filter by top categories if limit is specified
        if top_category_ids:
            query = query.filter(DrugTransaction.cat.in_(top_category_ids))
        
        results = query.group_by(
            func.date_trunc(trunc_unit, DrugTransaction.transaction_date),
            DrugTransaction.cat
        ).order_by(
            func.date_trunc(trunc_unit, DrugTransaction.transaction_date),
            DrugTransaction.cat
        ).all()
        
        return [
            {
                'period': row.period,
                'category_id': row.category_id,
                'total_quantity': float(row.total_quantity) if row.total_quantity else 0.0,
                'total_value': float(row.total_value) if row.total_value else 0.0,
                'transaction_count': row.transaction_count or 0,
                'unique_drugs': row.unique_drugs
            }
            for row in results
        ]
    
    def get_patient_demographics(
        self,
        start_date: date,
        end_date: date,
        group_by: str = 'age'
    ) -> List[Dict]:
        """
        Get patient demographics analysis.
        
        Args:
            start_date: Start date
            end_date: End date
            group_by: 'age', 'room', or 'bed'
        """
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        if group_by == 'age':
            # Calculate age from date_of_birth at the time of transaction
            # Use PostgreSQL's AGE function and extract years
            age_expr = extract(
                'year',
                func.age(DrugTransaction.transaction_date, DrugTransaction.date_of_birth)
            )
            
            age_group_expr = case(
                (age_expr < 18, '0-17'),
                (age_expr < 30, '18-29'),
                (age_expr < 50, '30-49'),
                (age_expr < 70, '50-69'),
                else_='70+'
            ).label('age_group')
            
            results = self._session.query(
                age_group_expr,
                func.count().label('transaction_count'),
                func.sum(
                    func.abs(DrugTransaction.quantity)
                ).filter(DrugTransaction.quantity < 0).label('total_quantity'),
                func.sum(
                    DrugTransaction.total_price
                ).filter(DrugTransaction.quantity < 0).label('total_value')
            ).filter(
                DrugTransaction.transaction_date.between(start_date, end_date),
                DrugTransaction.date_of_birth.isnot(None)
            ).group_by(
                age_group_expr
            ).all()
            
            # Sort results in Python by age group order
            age_group_order = {'0-17': 1, '18-29': 2, '30-49': 3, '50-69': 4, '70+': 5}
            sorted_results = sorted(
                results,
                key=lambda row: age_group_order.get(row.age_group, 99)
            )
            
            return [
                {
                    'age_group': row.age_group,
                    'transaction_count': row.transaction_count,
                    'total_quantity': float(row.total_quantity) if row.total_quantity else 0.0,
                    'total_value': float(row.total_value) if row.total_value else 0.0
                }
                for row in sorted_results
            ]
        
        elif group_by == 'room':
            results = self._session.query(
                DrugTransaction.room_number,
                func.count().label('transaction_count'),
                func.sum(
                    func.abs(DrugTransaction.quantity)
                ).filter(DrugTransaction.quantity < 0).label('total_quantity'),
                func.sum(
                    DrugTransaction.total_price
                ).filter(DrugTransaction.quantity < 0).label('total_value'),
                func.count(func.distinct(DrugTransaction.drug_code)).label('unique_drugs')
            ).filter(
                DrugTransaction.transaction_date.between(start_date, end_date),
                DrugTransaction.room_number.isnot(None)
            ).group_by(
                DrugTransaction.room_number
            ).order_by(
                func.sum(func.abs(DrugTransaction.quantity)).filter(DrugTransaction.quantity < 0).desc()
            ).limit(50).all()
            
            return [
                {
                    'room_number': row.room_number,
                    'transaction_count': row.transaction_count,
                    'total_quantity': float(row.total_quantity) if row.total_quantity else 0.0,
                    'total_value': float(row.total_value) if row.total_value else 0.0,
                    'unique_drugs': row.unique_drugs
                }
                for row in results
            ]
        
        else:  # bed
            results = self._session.query(
                DrugTransaction.bed_number,
                func.count().label('transaction_count'),
                func.sum(
                    func.abs(DrugTransaction.quantity)
                ).filter(DrugTransaction.quantity < 0).label('total_quantity'),
                func.sum(
                    DrugTransaction.total_price
                ).filter(DrugTransaction.quantity < 0).label('total_value'),
                func.count(func.distinct(DrugTransaction.drug_code)).label('unique_drugs')
            ).filter(
                DrugTransaction.transaction_date.between(start_date, end_date),
                DrugTransaction.bed_number.isnot(None)
            ).group_by(
                DrugTransaction.bed_number
            ).order_by(
                func.sum(func.abs(DrugTransaction.quantity)).filter(DrugTransaction.quantity < 0).desc()
            ).limit(50).all()
            
            return [
                {
                    'bed_number': row.bed_number,
                    'transaction_count': row.transaction_count,
                    'total_quantity': float(row.total_quantity) if row.total_quantity else 0.0,
                    'total_value': float(row.total_value) if row.total_value else 0.0,
                    'unique_drugs': row.unique_drugs
                }
                for row in results
            ]

    def search_drugs(self, query: str, limit: int = 3) -> List[Dict]:
        """Search for drugs by code or name with case-insensitive matching.
        
        Args:
            query: Search query (minimum 3 characters)
            limit: Maximum number of results to return (default: 3)
            
        Returns:
            List of drug matches with id, drug_code, and name
        """
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        # Get distinct drugs where code or name starts with query
        # Filter for active drugs (quantity < 0 indicates dispensed/available)
        results = self._session.query(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name
        ).filter(
            (func.lower(DrugTransaction.drug_code).startswith(func.lower(query))) |
            (func.lower(DrugTransaction.drug_name).startswith(func.lower(query))),
            DrugTransaction.quantity < 0  # Active/dispensed drugs
        ).distinct(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name
        ).order_by(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name
        ).limit(limit).all()
        
        return [
            {
                'id': row.drug_code,
                'drug_code': row.drug_code,
                'name': row.drug_name
            }
            for row in results
        ]

    def search_departments(self, query: str, limit: int = 3) -> List[Dict]:
        """Search for departments by ID or name with case-insensitive matching.
        
        Args:
            query: Search query
            limit: Maximum number of results to return (default: 3)
            
        Returns:
            List of department matches with id and department_name
        """
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with AnalyticsDAL() as dal:'")
        
        # Search for distinct departments by code (cr - consuming department)
        # Try to match as integer first, then as string prefix
        search_results = []
        
        try:
            # Try parsing as integer first
            dept_id = int(query)
            search_results = self._session.query(
                DrugTransaction.cr.label('dept_id')
            ).filter(
                DrugTransaction.cr == dept_id,
                DrugTransaction.cr.isnot(None)
            ).distinct(
                DrugTransaction.cr
            ).limit(limit).all()
        except (ValueError, TypeError):
            pass
        
        # If no results from integer search, try string matching
        if not search_results:
            search_results = self._session.query(
                DrugTransaction.cr.label('dept_id')
            ).filter(
                DrugTransaction.cr.isnot(None),
                func.lower(func.cast(DrugTransaction.cr, String)).like(func.lower(query) + '%')
            ).distinct(
                DrugTransaction.cr
            ).limit(limit).all()
        
        return [
            {
                'id': row.dept_id,
                'department_name': f'Department {row.dept_id}'
            }
            for row in search_results
        ]
