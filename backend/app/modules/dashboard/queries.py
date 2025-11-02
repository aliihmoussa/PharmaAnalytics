"""Analytics Data Access Layer - Database queries."""

from typing import Dict, List, Optional
from datetime import date
from backend.app.database.connection import get_db_connection, close_db_connection
from backend.app.database.base import BaseRepository


class AnalyticsDAL(BaseRepository):
    """Data access layer for analytics queries."""
    
    def get_top_drugs(
        self,
        start_date: date,
        end_date: date,
        limit: int,
        category_id: Optional[int] = None,
        department_id: Optional[int] = None
    ) -> List[Dict]:
        """Get top dispensed drugs from database."""
        query = """
            SELECT 
                drug_code,
                drug_name,
                SUM(ABS(quantity)) as total_qty,
                SUM(total_price) as total_value,
                COUNT(*) as transaction_count
            FROM drug_transactions
            WHERE transaction_date BETWEEN %s AND %s
                AND quantity < 0
        """
        params = [start_date, end_date]
        
        if category_id:
            query += " AND cat = %s"
            params.append(category_id)
        
        if department_id:
            query += " AND cr = %s"
            params.append(department_id)
        
        query += """
            GROUP BY drug_code, drug_name
            ORDER BY total_qty DESC
            LIMIT %s
        """
        params.append(limit)
        
        return self.execute_query(query, tuple(params))
    
    def get_drug_demand_time_series(
        self,
        start_date: date,
        end_date: date,
        drug_code: Optional[str] = None,
        granularity: str = 'daily'
    ) -> List[Dict]:
        """Get time-series demand data."""
        # Map granularity to PostgreSQL date_trunc format
        trunc_mapping = {
            'daily': 'day',
            'weekly': 'week',
            'monthly': 'month'
        }
        trunc_unit = trunc_mapping.get(granularity, 'day')
        
        query = f"""
            SELECT 
                DATE_TRUNC('{trunc_unit}', transaction_date) as date,
                SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as quantity,
                SUM(total_price) FILTER (WHERE quantity < 0) as value,
                COUNT(*) FILTER (WHERE quantity < 0) as transaction_count
            FROM drug_transactions
            WHERE transaction_date BETWEEN %s AND %s
        """
        params = [start_date, end_date]
        
        if drug_code:
            query += " AND drug_code = %s"
            params.append(drug_code)
        
        query += """
            GROUP BY DATE_TRUNC('{trunc_unit}', transaction_date)
            ORDER BY date
        """.format(trunc_unit=trunc_unit)
        
        return self.execute_query(query, tuple(params))
    
    def get_summary_stats(self, start_date: Optional[date], end_date: Optional[date]) -> Dict:
        """Get overall statistics."""
        if start_date and end_date:
            where_clause = "WHERE transaction_date BETWEEN %s AND %s"
            params = (start_date, end_date)
        else:
            where_clause = ""
            params = None
        
        query = f"""
            SELECT 
                COUNT(*) FILTER (WHERE quantity < 0) as total_dispensed,
                SUM(total_price) FILTER (WHERE quantity < 0) as total_value,
                COUNT(*) as total_transactions,
                COUNT(DISTINCT drug_code) as unique_drugs,
                COUNT(DISTINCT cr) as unique_departments
            FROM drug_transactions
            {where_clause}
        """
        
        results = self.execute_query(query, params)
        if results:
            return results[0]
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
        query = """
            SELECT 
                EXTRACT(MONTH FROM transaction_date) as month,
                EXTRACT(YEAR FROM transaction_date) as year,
                SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as quantity,
                SUM(total_price) FILTER (WHERE quantity < 0) as value
            FROM drug_transactions
            WHERE transaction_date BETWEEN %s AND %s
        """
        params = [start_date, end_date]
        
        if drug_code:
            query += " AND drug_code = %s"
            params.append(drug_code)
        
        query += """
            GROUP BY EXTRACT(MONTH FROM transaction_date), EXTRACT(YEAR FROM transaction_date)
            ORDER BY year, month
        """
        
        return self.execute_query(query, tuple(params))
    
    def get_department_performance(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[Dict]:
        """Get department performance metrics."""
        query = """
            SELECT 
                cr as department_id,
                COUNT(*) as transaction_count,
                SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as total_dispensed,
                SUM(total_price) FILTER (WHERE quantity < 0) as total_value,
                COUNT(DISTINCT drug_code) as unique_drugs
            FROM drug_transactions
            WHERE transaction_date BETWEEN %s AND %s
            GROUP BY cr
            ORDER BY total_dispensed DESC
            LIMIT %s
        """
        
        return self.execute_query(query, (start_date, end_date, limit))

