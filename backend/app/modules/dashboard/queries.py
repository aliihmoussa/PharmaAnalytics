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
        
        query += f"""
            GROUP BY DATE_TRUNC('{trunc_unit}', transaction_date)
            ORDER BY date
        """
        
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
                COALESCE(COUNT(*) FILTER (WHERE quantity < 0), 0) as total_dispensed,
                COALESCE(SUM(total_price) FILTER (WHERE quantity < 0), 0.0) as total_value,
                COALESCE(COUNT(*), 0) as total_transactions,
                COALESCE(COUNT(DISTINCT drug_code), 0) as unique_drugs,
                COALESCE(COUNT(DISTINCT cr), 0) as unique_departments
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
        # Build metric selection based on type
        if metric_type == 'quantity':
            metric_select = "SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as metric_value"
        elif metric_type == 'value':
            metric_select = "SUM(total_price) FILTER (WHERE quantity < 0) as metric_value"
        else:  # transactions
            metric_select = "COUNT(*) FILTER (WHERE quantity < 0) as metric_value"
        
        query = f"""
            SELECT 
                EXTRACT(YEAR FROM transaction_date) as year,
                {metric_select}
            FROM drug_transactions
            WHERE 1=1
        """
        params = []
        
        if start_year:
            query += " AND EXTRACT(YEAR FROM transaction_date) >= %s"
            params.append(start_year)
        
        if end_year:
            query += " AND EXTRACT(YEAR FROM transaction_date) <= %s"
            params.append(end_year)
        
        if drug_code:
            query += " AND drug_code = %s"
            params.append(drug_code)
        
        query += """
            GROUP BY EXTRACT(YEAR FROM transaction_date)
            ORDER BY year
        """
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_category_analysis(
        self,
        start_date: date,
        end_date: date,
        granularity: str = 'monthly'
    ) -> List[Dict]:
        """
        Get drug category analysis over time.
        
        Args:
            start_date: Start date
            end_date: End date
            granularity: 'monthly' or 'quarterly'
        """
        if granularity == 'quarterly':
            date_trunc = "DATE_TRUNC('quarter', transaction_date)"
        else:  # monthly
            date_trunc = "DATE_TRUNC('month', transaction_date)"
        
        query = f"""
            SELECT 
                {date_trunc} as period,
                cat as category_id,
                SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as total_quantity,
                SUM(total_price) FILTER (WHERE quantity < 0) as total_value,
                COUNT(*) FILTER (WHERE quantity < 0) as transaction_count,
                COUNT(DISTINCT drug_code) as unique_drugs
            FROM drug_transactions
            WHERE transaction_date BETWEEN %s AND %s
                AND cat IS NOT NULL
            GROUP BY {date_trunc}, cat
            ORDER BY period, cat
        """
        
        return self.execute_query(query, (start_date, end_date))
    
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
        if group_by == 'age':
            # Group by age ranges
            query = """
                SELECT 
                    CASE 
                        WHEN patient_age::integer < 18 THEN '0-17'
                        WHEN patient_age::integer < 30 THEN '18-29'
                        WHEN patient_age::integer < 50 THEN '30-49'
                        WHEN patient_age::integer < 70 THEN '50-69'
                        ELSE '70+'
                    END as age_group,
                    COUNT(*) as transaction_count,
                    SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as total_quantity,
                    SUM(total_price) FILTER (WHERE quantity < 0) as total_value
                FROM drug_transactions
                WHERE transaction_date BETWEEN %s AND %s
                    AND patient_age IS NOT NULL
                    AND patient_age ~ '^[0-9]+$'
                GROUP BY age_group
                ORDER BY 
                    CASE age_group
                        WHEN '0-17' THEN 1
                        WHEN '18-29' THEN 2
                        WHEN '30-49' THEN 3
                        WHEN '50-69' THEN 4
                        ELSE 5
                    END
            """
        elif group_by == 'room':
            query = """
                SELECT 
                    room_number,
                    COUNT(*) as transaction_count,
                    SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as total_quantity,
                    SUM(total_price) FILTER (WHERE quantity < 0) as total_value,
                    COUNT(DISTINCT drug_code) as unique_drugs
                FROM drug_transactions
                WHERE transaction_date BETWEEN %s AND %s
                    AND room_number IS NOT NULL
                GROUP BY room_number
                ORDER BY total_quantity DESC
                LIMIT 50
            """
        else:  # bed
            query = """
                SELECT 
                    bed_number,
                    COUNT(*) as transaction_count,
                    SUM(ABS(quantity)) FILTER (WHERE quantity < 0) as total_quantity,
                    SUM(total_price) FILTER (WHERE quantity < 0) as total_value,
                    COUNT(DISTINCT drug_code) as unique_drugs
                FROM drug_transactions
                WHERE transaction_date BETWEEN %s AND %s
                    AND bed_number IS NOT NULL
                GROUP BY bed_number
                ORDER BY total_quantity DESC
                LIMIT 50
            """
        
        return self.execute_query(query, (start_date, end_date))

