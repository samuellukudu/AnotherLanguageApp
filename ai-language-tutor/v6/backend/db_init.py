"""
Database Initialization Module
Handles database creation, schema setup, and health checks
"""

import os
import aiosqlite
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Handles database initialization and health checks"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", "./ai_tutor.db")
        self.schema_path = self._find_schema_file()
    
    def _find_schema_file(self) -> str:
        """Return the path to the schema.sql file.

        The schema.sql file is expected to be in the same directory as this script.
        """
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"schema.sql not found at {schema_path}")
        return schema_path
    
    async def check_database_exists(self) -> bool:
        """Check if database file exists"""
        return os.path.exists(self.db_path)
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Comprehensive database health check"""
        health_status = {
            "database_exists": False,
            "database_accessible": False,
            "schema_loaded": False,
            "tables_exist": False,
            "views_exist": False,
            "can_write": False,
            "record_count": {},
            "errors": []
        }
        
        try:
            # Check if database file exists
            health_status["database_exists"] = await self.check_database_exists()
            
            if not health_status["database_exists"]:
                health_status["errors"].append("Database file does not exist")
                return health_status
            
            # Try to connect to database
            async with aiosqlite.connect(self.db_path) as db:
                health_status["database_accessible"] = True
                
                # Check if required tables exist
                required_tables = ['metadata_extractions', 'curricula', 'learning_content', 'api_cache']
                existing_tables = await self._get_existing_tables(db)
                
                missing_tables = [table for table in required_tables if table not in existing_tables]
                if missing_tables:
                    health_status["errors"].append(f"Missing tables: {missing_tables}")
                else:
                    health_status["tables_exist"] = True
                
                # Check if views exist
                required_views = ['user_learning_journeys', 'curriculum_content_status']
                existing_views = await self._get_existing_views(db)
                
                missing_views = [view for view in required_views if view not in existing_views]
                if missing_views:
                    health_status["errors"].append(f"Missing views: {missing_views}")
                else:
                    health_status["views_exist"] = True
                
                # Test write capability
                try:
                    await db.execute("CREATE TEMPORARY TABLE test_write (id INTEGER)")
                    await db.execute("DROP TABLE test_write")
                    health_status["can_write"] = True
                except Exception as e:
                    health_status["errors"].append(f"Cannot write to database: {str(e)}")
                
                # Get record counts
                if health_status["tables_exist"]:
                    for table in required_tables:
                        try:
                            async with db.execute(f"SELECT COUNT(*) FROM {table}") as cursor:
                                count = await cursor.fetchone()
                                health_status["record_count"][table] = count[0] if count else 0
                        except Exception as e:
                            health_status["record_count"][table] = f"Error: {str(e)}"
                
                health_status["schema_loaded"] = (
                    health_status["tables_exist"] and 
                    health_status["views_exist"]
                )
                
        except Exception as e:
            health_status["errors"].append(f"Database connection error: {str(e)}")
        
        return health_status
    
    async def _get_existing_tables(self, db: aiosqlite.Connection) -> List[str]:
        """Get list of existing tables"""
        async with db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def _get_existing_views(self, db: aiosqlite.Connection) -> List[str]:
        """Get list of existing views"""
        async with db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
        """) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def create_database(self) -> bool:
        """Create database file and initialize with schema"""
        try:
            logger.info(f"Creating database at: {self.db_path}")
            
            # Ensure directory exists
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created directory: {db_dir}")
            
            # Create database and load schema
            async with aiosqlite.connect(self.db_path) as db:
                # Read schema file
                with open(self.schema_path, 'r') as f:
                    schema = f.read()
                
                # Execute schema
                await db.executescript(schema)
                await db.commit()
                
                logger.info("Database created and schema loaded successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            return False
    
    async def initialize_database(self, force_recreate: bool = False) -> Dict[str, Any]:
        """Initialize database with comprehensive checks and creation"""
        result = {
            "success": False,
            "action_taken": "none",
            "health_check": {},
            "errors": []
        }
        
        try:
            # Check current database health
            health_check = await self.check_database_health()
            result["health_check"] = health_check
            
            # Determine if we need to create/recreate database
            needs_creation = (
                not health_check["database_exists"] or
                not health_check["schema_loaded"] or
                force_recreate
            )
            
            if needs_creation:
                if health_check["database_exists"] and force_recreate:
                    # Backup existing database
                    backup_path = f"{self.db_path}.backup"
                    if os.path.exists(self.db_path):
                        os.rename(self.db_path, backup_path)
                        logger.info(f"Backed up existing database to: {backup_path}")
                        result["action_taken"] = "recreated_with_backup"
                    else:
                        result["action_taken"] = "force_recreated"
                else:
                    result["action_taken"] = "created"
                
                # Create database
                creation_success = await self.create_database()
                if not creation_success:
                    result["errors"].append("Failed to create database")
                    return result
                
                # Verify creation
                final_health = await self.check_database_health()
                result["health_check"] = final_health
                
                if final_health["schema_loaded"] and final_health["can_write"]:
                    result["success"] = True
                    logger.info("Database initialization completed successfully")
                else:
                    result["errors"].append("Database created but health check failed")
            
            else:
                # Database exists and is healthy
                result["success"] = True
                result["action_taken"] = "already_exists"
                logger.info("Database already exists and is healthy")
            
        except Exception as e:
            error_msg = f"Database initialization error: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        return result
    
    async def repair_database(self) -> Dict[str, Any]:
        """Attempt to repair database issues"""
        result = {
            "success": False,
            "repairs_attempted": [],
            "errors": []
        }
        
        try:
            health_check = await self.check_database_health()
            
            if not health_check["database_exists"]:
                # Database doesn't exist - create it
                creation_result = await self.initialize_database()
                result["repairs_attempted"].append("created_missing_database")
                result["success"] = creation_result["success"]
                result["errors"].extend(creation_result.get("errors", []))
                return result
            
            # Database exists but has issues
            async with aiosqlite.connect(self.db_path) as db:
                # Check and repair missing tables
                if not health_check["tables_exist"]:
                    with open(self.schema_path, 'r') as f:
                        schema = f.read()
                    await db.executescript(schema)
                    await db.commit()
                    result["repairs_attempted"].append("recreated_schema")
                
                # Verify repair
                final_health = await self.check_database_health()
                result["success"] = final_health["schema_loaded"]
                
        except Exception as e:
            error_msg = f"Database repair error: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        return result


# Global instance
db_initializer = DatabaseInitializer()