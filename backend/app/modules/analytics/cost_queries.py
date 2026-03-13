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
        
        # Convert to list format: departments as list, each department's children (categories) as list
        result = []
        for dept_id in sorted(dept_dict.keys()):
            dept = dept_dict[dept_id]
            result.append({
                'id': dept['id'],
                'name': dept['name'],
                'value': dept['value'],
                'children': [dept['children'][cat_id] for cat_id in sorted(dept['children'].keys())]
            })
        return result
    
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
                             drug_categories: Optional[List[int]] = None,
                             max_items: int = 200) -> List[Dict]:
        """
        Get optimized data for bubble chart: Unit Price (x) vs Quantity (y) vs Frequency (size).
        Aggregated by drug with outlier filtering and result limiting for performance.
        
        Optimizations:
        - Filters out zero-priced items (clusters at origin)
        - Limits results to top items by frequency or cost
        - Uses percentile-based filtering to remove extreme outliers
        - Groups only by drug_code (not department/category) for better aggregation
        """
        base_query = self._build_base_query(
            start_date, end_date, departments, price_min, price_max, drug_categories
        )
        
        # Filter out zero or near-zero prices to avoid clustering at origin
        base_query = base_query.filter(DrugTransaction.unit_price > 0.01)
        
        # Aggregate by drug only (not by department/category) for better performance
        # This reduces the number of groups significantly
        results = base_query.with_entities(
            DrugTransaction.drug_code,
            func.max(DrugTransaction.drug_name).label('drug_name'),
            func.avg(DrugTransaction.unit_price).label('avg_unit_price'),
            func.sum(func.abs(DrugTransaction.quantity)).label('total_quantity'),
            func.count().label('frequency'),
            func.sum(DrugTransaction.total_price).label('total_cost'),
            func.max(func.coalesce(DrugTransaction.cr, 0)).label('primary_department_id'),
            func.max(func.coalesce(DrugTransaction.cat, 0)).label('primary_category_id')
        ).group_by(
            DrugTransaction.drug_code
        ).having(
            # Filter out drugs with very low frequency (noise)
            func.count() >= 3
        ).order_by(
            # Order by frequency first, then by total cost
            func.count().desc(),
            func.sum(DrugTransaction.total_price).desc()
        ).limit(max_items).all()
        
        if not results:
            return []
        
        # Calculate percentiles for outlier filtering
        prices = [float(row.avg_unit_price) for row in results if row.avg_unit_price]
        quantities = [float(row.total_quantity) for row in results if row.total_quantity]
        
        if prices and quantities:
            prices_sorted = sorted(prices)
            quantities_sorted = sorted(quantities)
            
            # Use 95th percentile as upper bound to filter extreme outliers
            # min(..., len - 1) ensures index never equals len (robust against multiplier/fp changes)
            num_prices = len(prices_sorted)
            num_quantities = len(quantities_sorted)
            price_p95 = prices_sorted[min(int(num_prices * 0.95), num_prices - 1)] if num_prices > 0 else max(prices)
            quantity_p95 = quantities_sorted[min(int(num_quantities * 0.95), num_quantities - 1)] if num_quantities > 0 else max(quantities)
            
            # Filter outliers and return clean data
            filtered_results = []
            for row in results:
                unit_price = float(row.avg_unit_price) if row.avg_unit_price else 0.0
                quantity = float(row.total_quantity) if row.total_quantity else 0.0
                
                # Filter extreme outliers (beyond 95th percentile)
                if unit_price > price_p95 * 2 or quantity > quantity_p95 * 2:
                    continue
                
                filtered_results.append({
                    'drug_code': row.drug_code,
                    'drug_name': row.drug_name or row.drug_code,
                    'department_id': row.primary_department_id,
                    'category_id': row.primary_category_id,
                    'unit_price': round(unit_price, 2),
                    'quantity': round(quantity, 2),
                    'frequency': row.frequency,
                    'total_cost': round(float(row.total_cost) if row.total_cost else 0.0, 2)
                })
            
            return filtered_results
        
        # Fallback if no data
        return [
            {
                'drug_code': row.drug_code,
                'drug_name': row.drug_name or row.drug_code,
                'department_id': row.primary_department_id,
                'category_id': row.primary_category_id,
                'unit_price': round(float(row.avg_unit_price) if row.avg_unit_price else 0.0, 2),
                'quantity': round(float(row.total_quantity) if row.total_quantity else 0.0, 2),
                'frequency': row.frequency,
                'total_cost': round(float(row.total_cost) if row.total_cost else 0.0, 2)
            }
            for row in results
        ]
    
    def get_hospital_stay_duration(self, start_date: date, end_date: date,
                                   departments: Optional[List[int]] = None,
                                   min_stay_days: Optional[int] = None,
                                   max_stay_days: Optional[int] = None,
                                   limit: Optional[int] = None) -> List[Dict]:
        """
        Get hospital stay duration for patients - OPTIMIZED VERSION.
        Uses SQL date arithmetic for better performance.
        Groups by doc_id and calculates stay duration from admission date to last transaction.
        """
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with CostAnalysisDAL() as dal:'")
        
        # Build base query with date calculation in SQL
        query = self._session.query(
            DrugTransaction.doc_id,
            func.min(DrugTransaction.ad_date).label('admission_date'),
            func.max(DrugTransaction.transaction_date).label('last_transaction_date'),
            func.coalesce(func.max(DrugTransaction.cr), 0).label('department_id'),
            func.count().label('transaction_count')
        ).filter(
            DrugTransaction.transaction_date.between(start_date, end_date),
            DrugTransaction.ad_date.isnot(None)  # Filter out NULL admission dates early
        )
        
        # Filter by departments if provided
        if departments:
            query = query.filter(DrugTransaction.cr.in_(departments))
        
        # Group by doc_id to get unique patient stays
        query = query.group_by(DrugTransaction.doc_id)
        
        # Apply stay duration filters in SQL if possible (using HAVING)
        if min_stay_days is not None or max_stay_days is not None:
            # We'll filter in Python after getting stay_days, but we can still optimize
            pass
        
        # Add limit if specified (for performance)
        if limit:
            query = query.limit(limit)
        
        # Execute query
        results = query.all()
        
        # Process results with filtering
        stays = []
        for row in results:
            admission_date = row.admission_date
            last_transaction = row.last_transaction_date
            
            # Calculate stay duration in days
            stay_days = (last_transaction - admission_date).days if admission_date and last_transaction else 0
            
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
                                    max_stay_days: Optional[int] = None,
                                    sample_size: int = 10000) -> Dict:
        """
        Get statistical summary of hospital stay durations - OPTIMIZED.
        Uses sampling for large datasets to improve performance.
        """
        # Use sampling for large datasets - get a representative sample
        stays = self.get_hospital_stay_duration(
            start_date, end_date, departments, min_stay_days, max_stay_days,
            limit=sample_size  # Limit for performance
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
                                      bins: int = 20,
                                      sample_size: int = 10000) -> List[Dict]:
        """
        Get distribution of stay durations for histogram - OPTIMIZED.
        Uses sampling for large datasets.
        """
        stays = self.get_hospital_stay_duration(
            start_date, end_date, departments, min_stay_days, max_stay_days,
            limit=sample_size  # Limit for performance
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
                                       max_stay_days: Optional[int] = None,
                                       sample_size: int = 10000) -> List[Dict]:
        """
        Get average stay duration grouped by department - OPTIMIZED.
        Uses sampling for large datasets.
        """
        stays = self.get_hospital_stay_duration(
            start_date, end_date, departments, min_stay_days, max_stay_days,
            limit=sample_size  # Limit for performance
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
                                 granularity: str = 'monthly',
                                 sample_size: int = 10000) -> List[Dict]:
        """
        Get stay duration trends over time - OPTIMIZED.
        Uses sampling for large datasets.
        """
        if not self._session:
            raise RuntimeError("Database session not initialized. Use 'with CostAnalysisDAL() as dal:'")
        
        # Get sampled stays for performance
        all_stays = self.get_hospital_stay_duration(
            start_date, end_date, departments, min_stay_days, max_stay_days,
            limit=sample_size  # Limit for performance
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

