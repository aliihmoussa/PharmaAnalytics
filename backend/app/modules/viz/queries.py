"""Cost Analysis Data Access Layer - Database queries for cost visualization."""

from typing import Dict, List, Optional
from datetime import date
from sqlalchemy import func, case, and_, or_
from sqlalchemy.orm import Session
from backend.app.database.models import DrugTransaction
from backend.app.database.session import get_db_session


class CostAnalysisDAL:
    """Data access layer for cost analysis queries."""
    
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
    
    def _build_base_query(self, start_date: date, end_date: date, 
                         departments: Optional[List[int]] = None,
                         price_min: Optional[float] = None,
                         price_max: Optional[float] = None,
                         drug_categories: Optional[List[int]] = None):
        """Build base query with common filters."""
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with CostAnalysisDAL() as dal:'")
        
        query = self._session.query(DrugTransaction).filter(
            DrugTransaction.transaction_date.between(start_date, end_date),
            DrugTransaction.quantity < 0  # Only dispensed drugs (negative quantity)
        )
        
        # Apply filters
        if departments:
            query = query.filter(DrugTransaction.cr.in_(departments))
        
        if drug_categories:
            query = query.filter(DrugTransaction.cat.in_(drug_categories))
        
        if price_min is not None:
            query = query.filter(DrugTransaction.unit_price >= price_min)
        
        if price_max is not None:
            query = query.filter(DrugTransaction.unit_price <= price_max)
        
        return query
    
    def get_sunburst_data(self, start_date: date, end_date: date,
                          departments: Optional[List[int]] = None,
                          price_min: Optional[float] = None,
                          price_max: Optional[float] = None,
                          drug_categories: Optional[List[int]] = None) -> List[Dict]:
        """
        Get hierarchical data for sunburst chart: Department → Category → Drug.
        Returns data in format suitable for sunburst visualization.
        """
        base_query = self._build_base_query(
            start_date, end_date, departments, price_min, price_max, drug_categories
        )
        
        # Aggregate by department, category, and drug
        results = base_query.with_entities(
            func.coalesce(DrugTransaction.cr, 0).label('department_id'),
            func.coalesce(DrugTransaction.cat, 0).label('category_id'),
            DrugTransaction.drug_code,
            DrugTransaction.drug_name,
            func.sum(func.abs(DrugTransaction.quantity)).label('total_quantity'),
            func.sum(DrugTransaction.total_price).label('total_cost'),
            func.count().label('transaction_count')
        ).group_by(
            DrugTransaction.cr,
            DrugTransaction.cat,
            DrugTransaction.drug_code,
            DrugTransaction.drug_name
        ).all()
        
        # Transform to hierarchical structure
        dept_dict = {}
        for row in results:
            dept_id = row.department_id
            cat_id = row.category_id
            drug_code = row.drug_code
            drug_name = row.drug_name
            
            # Initialize department if not exists
            if dept_id not in dept_dict:
                dept_dict[dept_id] = {
                    'id': f'dept_{dept_id}',
                    'name': f'Department {dept_id}',
                    'value': 0.0,
                    'children': {}
                }
            
            # Initialize category if not exists
            if cat_id not in dept_dict[dept_id]['children']:
                dept_dict[dept_id]['children'][cat_id] = {
                    'id': f'dept_{dept_id}_cat_{cat_id}',
                    'name': f'Category {cat_id}',
                    'value': 0.0,
                    'children': []
                }
            
            # Add drug
            drug_value = float(row.total_cost) if row.total_cost else 0.0
            dept_dict[dept_id]['children'][cat_id]['children'].append({
                'id': f'dept_{dept_id}_cat_{cat_id}_drug_{drug_code}',
                'name': drug_name,
                'value': drug_value,
                'drug_code': drug_code,
                'quantity': float(row.total_quantity) if row.total_quantity else 0.0,
                'transaction_count': row.transaction_count
            })
            
            # Update category and department values
            dept_dict[dept_id]['children'][cat_id]['value'] += drug_value
            dept_dict[dept_id]['value'] += drug_value
        
        # Convert to list format
        return [dept_dict[dept_id] for dept_id in sorted(dept_dict.keys())]
    
    def get_top_cost_drivers(self, start_date: date, end_date: date,
                            departments: Optional[List[int]] = None,
                            price_min: Optional[float] = None,
                            price_max: Optional[float] = None,
                            drug_categories: Optional[List[int]] = None,
                            limit: int = 20) -> List[Dict]:
        """Get top 20 cost drivers (drugs with highest total cost)."""
        base_query = self._build_base_query(
            start_date, end_date, departments, price_min, price_max, drug_categories
        )
        
        results = base_query.with_entities(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name,
            func.coalesce(DrugTransaction.cr, 0).label('department_id'),
            func.coalesce(DrugTransaction.cat, 0).label('category_id'),
            func.sum(func.abs(DrugTransaction.quantity)).label('total_quantity'),
            func.sum(DrugTransaction.total_price).label('total_cost'),
            func.avg(DrugTransaction.unit_price).label('avg_unit_price'),
            func.count().label('transaction_count')
        ).group_by(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name,
            DrugTransaction.cr,
            DrugTransaction.cat
        ).order_by(
            func.sum(DrugTransaction.total_price).desc()
        ).limit(limit).all()
        
        return [
            {
                'drug_code': row.drug_code,
                'drug_name': row.drug_name,
                'department_id': row.department_id,
                'category_id': row.category_id,
                'total_cost': float(row.total_cost) if row.total_cost else 0.0,
                'total_quantity': float(row.total_quantity) if row.total_quantity else 0.0,
                'avg_unit_price': float(row.avg_unit_price) if row.avg_unit_price else 0.0,
                'transaction_count': row.transaction_count
            }
            for row in results
        ]
    
    def get_cost_trends(self, start_date: date, end_date: date,
                        granularity: str = 'daily',
                        departments: Optional[List[int]] = None,
                        price_min: Optional[float] = None,
                        price_max: Optional[float] = None,
                        drug_categories: Optional[List[int]] = None) -> List[Dict]:
        """
        Get cost trends over time (daily or monthly).
        granularity: 'daily' or 'monthly'
        """
        base_query = self._build_base_query(
            start_date, end_date, departments, price_min, price_max, drug_categories
        )
        
        trunc_unit = 'day' if granularity == 'daily' else 'month'
        
        results = base_query.with_entities(
            func.date_trunc(trunc_unit, DrugTransaction.transaction_date).label('date'),
            func.sum(DrugTransaction.total_price).label('total_cost'),
            func.sum(func.abs(DrugTransaction.quantity)).label('total_quantity'),
            func.count().label('transaction_count'),
            func.avg(DrugTransaction.unit_price).label('avg_unit_price')
        ).group_by(
            func.date_trunc(trunc_unit, DrugTransaction.transaction_date)
        ).order_by(
            func.date_trunc(trunc_unit, DrugTransaction.transaction_date)
        ).all()
        
        return [
            {
                'date': row.date.strftime('%Y-%m-%d') if granularity == 'daily' else row.date.strftime('%Y-%m'),
                'total_cost': float(row.total_cost) if row.total_cost else 0.0,
                'total_quantity': float(row.total_quantity) if row.total_quantity else 0.0,
                'transaction_count': row.transaction_count,
                'avg_unit_price': float(row.avg_unit_price) if row.avg_unit_price else 0.0
            }
            for row in results
        ]
    
    def get_bubble_chart_data(self, start_date: date, end_date: date,
                             departments: Optional[List[int]] = None,
                             price_min: Optional[float] = None,
                             price_max: Optional[float] = None,
                             drug_categories: Optional[List[int]] = None) -> List[Dict]:
        """
        Get data for bubble chart: Unit Price (x) vs Quantity (y) vs Frequency (size).
        Aggregated by drug.
        """
        base_query = self._build_base_query(
            start_date, end_date, departments, price_min, price_max, drug_categories
        )
        
        results = base_query.with_entities(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name,
            func.coalesce(DrugTransaction.cr, 0).label('department_id'),
            func.coalesce(DrugTransaction.cat, 0).label('category_id'),
            func.avg(DrugTransaction.unit_price).label('avg_unit_price'),
            func.sum(func.abs(DrugTransaction.quantity)).label('total_quantity'),
            func.count().label('frequency'),
            func.sum(DrugTransaction.total_price).label('total_cost')
        ).group_by(
            DrugTransaction.drug_code,
            DrugTransaction.drug_name,
            DrugTransaction.cr,
            DrugTransaction.cat
        ).all()
        
        return [
            {
                'drug_code': row.drug_code,
                'drug_name': row.drug_name,
                'department_id': row.department_id,
                'category_id': row.category_id,
                'unit_price': float(row.avg_unit_price) if row.avg_unit_price else 0.0,
                'quantity': float(row.total_quantity) if row.total_quantity else 0.0,
                'frequency': row.frequency,
                'total_cost': float(row.total_cost) if row.total_cost else 0.0
            }
            for row in results
        ]

