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
    
    def get_hospital_stay_duration(self, start_date: date, end_date: date,
                                   departments: Optional[List[int]] = None,
                                   min_stay_days: Optional[int] = None,
                                   max_stay_days: Optional[int] = None) -> List[Dict]:
        """
        Get hospital stay duration for patients.
        Groups by doc_id and calculates stay duration from admission date to last transaction.
        """
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with CostAnalysisDAL() as dal:'")
        
        # Base query - filter by date range and get patient stays
        query = self._session.query(
            DrugTransaction.doc_id,
            func.min(DrugTransaction.ad_date).label('admission_date'),
            func.max(DrugTransaction.transaction_date).label('last_transaction_date'),
            func.coalesce(func.max(DrugTransaction.cr), 0).label('department_id'),
            func.count().label('transaction_count')
        ).filter(
            DrugTransaction.transaction_date.between(start_date, end_date)
        )
        
        # Filter by departments if provided
        if departments:
            query = query.filter(DrugTransaction.cr.in_(departments))
        
        # Group by doc_id to get unique patient stays
        query = query.group_by(DrugTransaction.doc_id)
        
        # Execute query
        results = query.all()
        
        # Calculate stay duration and filter
        stays = []
        for row in results:
            admission_date = row.admission_date
            last_transaction = row.last_transaction_date
            
            # Skip if no admission date
            if not admission_date:
                continue
            
            # Calculate stay duration in days
            stay_days = (last_transaction - admission_date).days
            
            # Skip negative or zero stays (data quality issue)
            if stay_days < 0:
                continue
            
            # Apply stay duration filters
            if min_stay_days is not None and stay_days < min_stay_days:
                continue
            if max_stay_days is not None and stay_days > max_stay_days:
                continue
            
            stays.append({
                'doc_id': row.doc_id,
                'admission_date': admission_date.isoformat(),
                'last_transaction_date': last_transaction.isoformat(),
                'stay_days': stay_days,
                'department_id': row.department_id,
                'transaction_count': row.transaction_count
            })
        
        return stays
    
    def get_stay_duration_statistics(self, start_date: date, end_date: date,
                                    departments: Optional[List[int]] = None,
                                    min_stay_days: Optional[int] = None,
                                    max_stay_days: Optional[int] = None) -> Dict:
        """Get statistical summary of hospital stay durations."""
        stays = self.get_hospital_stay_duration(
            start_date, end_date, departments, min_stay_days, max_stay_days
        )
        
        if not stays:
            return {
                'total_patients': 0,
                'average_stay_days': 0.0,
                'median_stay_days': 0.0,
                'min_stay_days': 0,
                'max_stay_days': 0,
                'std_dev_stay_days': 0.0
            }
        
        stay_days_list = [stay['stay_days'] for stay in stays]
        stay_days_list.sort()
        
        total_patients = len(stay_days_list)
        average = sum(stay_days_list) / total_patients
        
        # Calculate median
        if total_patients % 2 == 0:
            median = (stay_days_list[total_patients // 2 - 1] + stay_days_list[total_patients // 2]) / 2
        else:
            median = stay_days_list[total_patients // 2]
        
        # Calculate standard deviation
        variance = sum((x - average) ** 2 for x in stay_days_list) / total_patients
        std_dev = variance ** 0.5
        
        return {
            'total_patients': total_patients,
            'average_stay_days': round(average, 2),
            'median_stay_days': round(median, 2),
            'min_stay_days': min(stay_days_list),
            'max_stay_days': max(stay_days_list),
            'std_dev_stay_days': round(std_dev, 2)
        }
    
    def get_stay_duration_distribution(self, start_date: date, end_date: date,
                                      departments: Optional[List[int]] = None,
                                      min_stay_days: Optional[int] = None,
                                      max_stay_days: Optional[int] = None,
                                      bins: int = 20) -> List[Dict]:
        """Get distribution of stay durations for histogram."""
        stays = self.get_hospital_stay_duration(
            start_date, end_date, departments, min_stay_days, max_stay_days
        )
        
        if not stays:
            return []
        
        stay_days_list = [stay['stay_days'] for stay in stays]
        min_days = min(stay_days_list)
        max_days = max(stay_days_list)
        
        # Create bins
        bin_width = (max_days - min_days) / bins if max_days > min_days else 1
        if bin_width == 0:
            bin_width = 1
        
        # Initialize bins
        bin_counts = {}
        for i in range(bins):
            bin_start = min_days + i * bin_width
            bin_end = min_days + (i + 1) * bin_width
            bin_key = f"{int(bin_start)}-{int(bin_end)}"
            bin_counts[bin_key] = {
                'range': f"{int(bin_start)}-{int(bin_end)} days",
                'start': int(bin_start),
                'end': int(bin_end),
                'count': 0
            }
        
        # Count stays in each bin
        for stay_days in stay_days_list:
            bin_index = int((stay_days - min_days) / bin_width) if bin_width > 0 else 0
            bin_index = min(bin_index, bins - 1)  # Ensure we don't go out of bounds
            
            bin_start = min_days + bin_index * bin_width
            bin_end = min_days + (bin_index + 1) * bin_width
            bin_key = f"{int(bin_start)}-{int(bin_end)}"
            
            if bin_key in bin_counts:
                bin_counts[bin_key]['count'] += 1
        
        return list(bin_counts.values())
    
    def get_stay_duration_by_department(self, start_date: date, end_date: date,
                                       departments: Optional[List[int]] = None,
                                       min_stay_days: Optional[int] = None,
                                       max_stay_days: Optional[int] = None) -> List[Dict]:
        """Get average stay duration grouped by department."""
        stays = self.get_hospital_stay_duration(
            start_date, end_date, departments, min_stay_days, max_stay_days
        )
        
        if not stays:
            return []
        
        # Group by department
        dept_stays = {}
        for stay in stays:
            dept_id = stay['department_id']
            if dept_id not in dept_stays:
                dept_stays[dept_id] = []
            dept_stays[dept_id].append(stay['stay_days'])
        
        # Calculate averages
        result = []
        for dept_id, stay_days_list in dept_stays.items():
            avg_stay = sum(stay_days_list) / len(stay_days_list)
            result.append({
                'department_id': dept_id,
                'patient_count': len(stay_days_list),
                'average_stay_days': round(avg_stay, 2),
                'min_stay_days': min(stay_days_list),
                'max_stay_days': max(stay_days_list)
            })
        
        # Sort by average stay days descending
        result.sort(key=lambda x: x['average_stay_days'], reverse=True)
        return result
    
    def get_stay_duration_trends(self, start_date: date, end_date: date,
                                 departments: Optional[List[int]] = None,
                                 min_stay_days: Optional[int] = None,
                                 max_stay_days: Optional[int] = None,
                                 granularity: str = 'monthly') -> List[Dict]:
        """Get stay duration trends over time."""
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with CostAnalysisDAL() as dal:'")
        
        # Get all stays first
        all_stays = self.get_hospital_stay_duration(
            start_date, end_date, departments, min_stay_days, max_stay_days
        )
        
        if not all_stays:
            return []
        
        # Group by time period
        trunc_unit = 'month' if granularity == 'monthly' else 'day'
        trends = {}
        
        for stay in all_stays:
            # Use admission date for grouping
            admission_date = date.fromisoformat(stay['admission_date'])
            
            if trunc_unit == 'month':
                period_key = admission_date.strftime('%Y-%m')
            else:
                period_key = admission_date.isoformat()
            
            if period_key not in trends:
                trends[period_key] = []
            trends[period_key].append(stay['stay_days'])
        
        # Calculate averages per period
        result = []
        for period, stay_days_list in sorted(trends.items()):
            avg_stay = sum(stay_days_list) / len(stay_days_list)
            result.append({
                'period': period,
                'average_stay_days': round(avg_stay, 2),
                'patient_count': len(stay_days_list),
                'min_stay_days': min(stay_days_list),
                'max_stay_days': max(stay_days_list)
            })
        
        return result

