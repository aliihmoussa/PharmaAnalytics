"""PostgreSQL connection pooling and management."""

import psycopg2
from psycopg2 import pool
from typing import Optional
from backend.app.config import config


class DatabaseConnection:
    """PostgreSQL connection pool manager."""
    
    _connection_pool: Optional[pool.ThreadedConnectionPool] = None
    
    @classmethod
    def initialize_pool(cls, min_conn: int = 1, max_conn: int = 20):
        """Initialize connection pool."""
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pool.ThreadedConnectionPool(
                    min_conn,
                    max_conn,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    host=config.DB_HOST,
                    port=config.DB_PORT,
                    database=config.DB_NAME
                )
            except Exception as e:
                raise ConnectionError(f"Failed to create connection pool: {e}")
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool."""
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Return a connection to the pool."""
        if cls._connection_pool:
            cls._connection_pool.putconn(conn)
    
    @classmethod
    def close_all(cls):
        """Close all connections in the pool."""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            cls._connection_pool = None


def get_db_connection():
    """Get database connection (helper function)."""
    return DatabaseConnection.get_connection()


def close_db_connection(conn):
    """Close database connection (helper function)."""
    DatabaseConnection.return_connection(conn)

