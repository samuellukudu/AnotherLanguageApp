from typing import Dict, Any, Optional
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from backend.core.config import settings
from backend.core.exceptions import DatabaseException, ConfigurationException
from backend.services.base_service import BaseService
from backend.repositories.base_repository import DatabaseConnectionManager

logger = logging.getLogger(__name__)

class DatabaseService(BaseService):
    """Service for database operations and initialization"""
    
    def __init__(self):
        super().__init__()
        logger.info("Database Service initialized")
    
    async def initialize_database(self):
        """Initialize the database schema"""
        self.log_operation("initialize_database")
        
        try:
            # Get the schema SQL from the database module
            from backend.infrastructure.database import SCHEMA_SQL
            
            if not SCHEMA_SQL:
                raise ConfigurationException("Database schema SQL is not defined")
            
            # Execute the schema SQL
            conn = None
            try:
                conn = DatabaseConnectionManager.get_connection()
                with conn.cursor() as cursor:
                    cursor.execute(SCHEMA_SQL)
                conn.commit()
                logger.info("Database schema initialized successfully")
            except Exception as e:
                if conn:
                    conn.rollback()
                raise DatabaseException(
                    message="Failed to initialize database schema",
                    details={"error": str(e)}
                )
            finally:
                if conn:
                    DatabaseConnectionManager.release_connection(conn)
                    
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            if isinstance(e, (DatabaseException, ConfigurationException)):
                raise
            raise DatabaseException(
                message="Failed to initialize database",
                details={"error": str(e)}
            )
    
    async def check_database_connection(self) -> bool:
        """Check if the database connection is working"""
        self.log_operation("check_database_connection")
        
        conn = None
        try:
            conn = DatabaseConnectionManager.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
        finally:
            if conn:
                DatabaseConnectionManager.release_connection(conn)
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database"""
        self.log_operation("get_database_info")
        
        conn = None
        try:
            conn = DatabaseConnectionManager.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get PostgreSQL version
                cursor.execute("SELECT version()")
                version = cursor.fetchone()["version"]
                
                # Get database size
                cursor.execute(
                    "SELECT pg_size_pretty(pg_database_size(%s)) as size",
                    (settings.DB_NAME,)
                )
                size = cursor.fetchone()["size"]
                
                # Get table count
                cursor.execute(
                    """SELECT count(*) as table_count 
                       FROM information_schema.tables 
                       WHERE table_schema = 'public'"""
                )
                table_count = cursor.fetchone()["table_count"]
                
                return {
                    "version": version,
                    "size": size,
                    "table_count": table_count,
                    "name": settings.DB_NAME,
                    "host": settings.DB_HOST,
                    "port": settings.DB_PORT
                }
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            raise DatabaseException(
                message="Failed to get database information",
                details={"error": str(e)}
            )
        finally:
            if conn:
                DatabaseConnectionManager.release_connection(conn)

# Create a global service instance
database_service = DatabaseService()