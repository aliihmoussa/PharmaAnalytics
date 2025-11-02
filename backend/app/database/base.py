"""Base repository pattern for Data Access Layer."""

from typing import Generic, TypeVar, List, Dict, Any
from backend.app.database.connection import get_db_connection, close_db_connection

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository class for database operations."""
    
    def __init__(self):
        self._conn = None
    
    def __enter__(self):
        self._conn = get_db_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            close_db_connection(self._conn)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts."""
        if self._conn is None:
            self._conn = get_db_connection()
        
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                return []
        except Exception as e:
            self._conn.rollback()
            raise
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows."""
        if self._conn is None:
            self._conn = get_db_connection()
        
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(query, params)
                self._conn.commit()
                return cursor.rowcount
        except Exception as e:
            self._conn.rollback()
            raise

