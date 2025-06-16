from typing import Any, Dict, List, Optional, TypeVar, Generic, Type
import logging
from psycopg2 import sql, pool
from psycopg2.extras import RealDictCursor
from backend.core.config import settings

logger = logging.getLogger(__name__)

# Type variable for generic repository
T = TypeVar('T')

class DatabaseConnectionManager:
    """Manages database connections using a connection pool"""
    _connection_pool = None

    @classmethod
    def get_connection_pool(cls):
        """Get or create a connection pool"""
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dbname=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD,
                    host=settings.DB_HOST,
                    port=settings.DB_PORT
                )
                logger.info("Database connection pool created successfully")
            except Exception as e:
                logger.error(f"Error creating connection pool: {e}")
                raise
        return cls._connection_pool

    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        return cls.get_connection_pool().getconn()

    @classmethod
    def release_connection(cls, conn):
        """Release a connection back to the pool"""
        cls.get_connection_pool().putconn(conn)

    @classmethod
    def close_all_connections(cls):
        """Close all connections in the pool"""
        if cls._connection_pool is not None:
            cls._connection_pool.closeall()
            logger.info("All database connections closed")

class BaseRepository(Generic[T]):
    """Base repository class with common database operations"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def _execute_query(self, query, params=None, fetch=True, many=False):
        """Execute a database query with connection management"""
        conn = None
        try:
            conn = DatabaseConnectionManager.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                
                if fetch:
                    if many:
                        result = cursor.fetchall()
                    else:
                        result = cursor.fetchone()
                else:
                    result = None
                    
                conn.commit()
                return result
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                DatabaseConnectionManager.release_connection(conn)
    
    def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Find a record by its ID"""
        query = sql.SQL("SELECT * FROM {} WHERE id = %s").format(sql.Identifier(self.table_name))
        return self._execute_query(query, (id,))
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Find all records in the table"""
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(self.table_name))
        return self._execute_query(query, many=True)
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        columns = list(data.keys())
        values = list(data.values())
        
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
            sql.Identifier(self.table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )
        
        return self._execute_query(query, values)
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by its ID"""
        set_items = []
        values = []
        
        for key, value in data.items():
            set_items.append(sql.SQL("{} = %s").format(sql.Identifier(key)))
            values.append(value)
            
        values.append(id)  # Add ID for WHERE clause
        
        query = sql.SQL("UPDATE {} SET {} WHERE id = %s RETURNING *").format(
            sql.Identifier(self.table_name),
            sql.SQL(', ').join(set_items)
        )
        
        return self._execute_query(query, values)
    
    def delete(self, id: int) -> bool:
        """Delete a record by its ID"""
        query = sql.SQL("DELETE FROM {} WHERE id = %s").format(sql.Identifier(self.table_name))
        self._execute_query(query, (id,), fetch=False)
        return True