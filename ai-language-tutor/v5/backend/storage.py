import json
import os
import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from backend.constants import ContentStatus

# Import database functionality
try:
    from backend.database import database
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Database import failed: {e}")
    DATABASE_AVAILABLE = False
    database = None

class CurriculumStorage:
    def __init__(self, storage_dir: str = "data", use_database: bool = True, use_file_backup: bool = True):
        self.storage_dir = storage_dir
        self.curricula_dir = os.path.join(storage_dir, "curricula")
        self.use_database = use_database and DATABASE_AVAILABLE
        self.use_file_backup = use_file_backup
        self.ensure_directories()
        self._locks = {}

    def ensure_directories(self):
        """Ensure storage directories exist"""
        os.makedirs(self.curricula_dir, exist_ok=True)

    def get_lock(self, curriculum_id: str) -> asyncio.Lock:
        """Get or create a lock for a specific curriculum"""
        if curriculum_id not in self._locks:
            self._locks[curriculum_id] = asyncio.Lock()
        return self._locks[curriculum_id]

    async def store_curriculum(self, user_id: int, metadata: Dict[str, Any], curriculum_data: Dict[str, Any]) -> str:
        """Store curriculum and return curriculum ID"""
        self.ensure_directories()  # Ensure directories exist before writing
        curriculum_id = str(uuid.uuid4())
        
        # Store in database (primary storage)
        if self.use_database:
            try:
                db_curriculum_id = await database.store_curriculum(user_id, metadata, curriculum_data)
                curriculum_id = db_curriculum_id  # Use the database-generated ID
            except Exception as e:
                print(f"Database storage failed: {e}")
                if not self.use_file_backup:
                    raise e  # Re-raise if no backup is configured
        
        # Store in file as backup if enabled
        if self.use_file_backup:
            self.ensure_directories()  # Ensure directories exist before writing
            curriculum_record = {
                "id": curriculum_id,
                "user_id": user_id,
                "metadata": metadata,
                "curriculum": curriculum_data,
                "created_at": datetime.utcnow().isoformat(),
                "status": {
                    "curriculum": ContentStatus.COMPLETED if curriculum_data else ContentStatus.PENDING,
                    "flashcards": ContentStatus.PENDING,
                    "exercises": ContentStatus.PENDING,
                    "simulation": ContentStatus.PENDING
                },
                "content": {
                    "curriculum": curriculum_data,
                    "flashcards": None,
                    "exercises": None,
                    "simulation": None
                }
            }
            
            try:
                file_path = os.path.join(self.curricula_dir, f"{curriculum_id}.json")
                async with self.get_lock(curriculum_id):
                    with open(file_path, 'w') as f:
                        json.dump(curriculum_record, f, indent=2)
            except Exception as e:
                print(f"File backup storage failed: {e}")
                # Don't fail the operation if only backup fails
        
        return curriculum_id

    async def get_curriculum(self, curriculum_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve curriculum by ID"""
        self.ensure_directories()  # Ensure directories exist before reading
        
        # Try database first (primary storage)
        if self.use_database:
            try:
                curriculum = await database.get_curriculum(curriculum_id)
                if curriculum:
                    return curriculum
            except Exception as e:
                print(f"Database retrieval failed: {e}")
                if not self.use_file_backup:
                    return None
        
        # Fallback to file storage if backup is enabled
        if self.use_file_backup:
            self.ensure_directories()  # Ensure directories exist before reading
            file_path = os.path.join(self.curricula_dir, f"{curriculum_id}.json")
            if not os.path.exists(file_path):
                return None
            
            try:
                async with self.get_lock(curriculum_id):
                    with open(file_path, 'r') as f:
                        curriculum = json.load(f)
                        return curriculum
            except Exception as e:
                print(f"File storage retrieval failed: {e}")
                return None
        
        return None

    async def update_content_status(self, curriculum_id: str, content_type: str, status: ContentStatus):
        """Update the status of a specific content type"""
        self.ensure_directories()  # Ensure directories exist before writing
        # Update in database (primary storage)
        if self.use_database:
            try:
                db_result = await database.update_content_status(curriculum_id, content_type, status)
                if not db_result:
                    print(f"Database status update failed for {curriculum_id}")
                    if not self.use_file_backup:
                        return False
            except Exception as e:
                print(f"Database status update failed: {e}")
                if not self.use_file_backup:
                    return False
        
        # Update file backup if enabled
        if self.use_file_backup:
            self.ensure_directories()  # Ensure directories exist before writing
            try:
                curriculum = await self.get_curriculum(curriculum_id)
                if not curriculum:
                    return False
                
                curriculum["status"][content_type] = status
                curriculum["updated_at"] = datetime.utcnow().isoformat()
                
                file_path = os.path.join(self.curricula_dir, f"{curriculum_id}.json")
                async with self.get_lock(curriculum_id):
                    with open(file_path, 'w') as f:
                        json.dump(curriculum, f, indent=2)
            except Exception as e:
                print(f"File backup update failed: {e}")
                # Don't fail if only backup fails
        
        return True

    async def store_generated_content(self, curriculum_id: str, content_type: str, content_data: Dict[str, Any]):
        """Store generated content (flashcards, exercises, simulation)"""
        self.ensure_directories()  # Ensure directories exist before writing
        # Store in database (primary storage)
        if self.use_database:
            try:
                db_result = await database.store_generated_content(curriculum_id, content_type, content_data)
                if not db_result:
                    print(f"Database content storage failed for {curriculum_id}")
                    if not self.use_file_backup:
                        return False
            except Exception as e:
                print(f"Database content storage failed: {e}")
                if not self.use_file_backup:
                    return False
        
        # Update file backup if enabled
        if self.use_file_backup:
            self.ensure_directories()  # Ensure directories exist before writing
            try:
                curriculum = await self.get_curriculum(curriculum_id)
                if not curriculum:
                    return False
                
                curriculum["content"][content_type] = content_data
                curriculum["status"][content_type] = ContentStatus.COMPLETED
                curriculum["updated_at"] = datetime.utcnow().isoformat()
                
                file_path = os.path.join(self.curricula_dir, f"{curriculum_id}.json")
                async with self.get_lock(curriculum_id):
                    with open(file_path, 'w') as f:
                        json.dump(curriculum, f, indent=2)
            except Exception as e:
                print(f"File backup storage failed: {e}")
                # Don't fail if only backup fails
        
        return True

    async def get_user_curricula(self, user_id: int) -> list[Dict[str, Any]]:
        """Get all curricula for a user"""
        self.ensure_directories()  # Ensure directories exist before reading
        # Try database first (primary storage)
        if self.use_database:
            try:
                curricula = await database.get_user_curricula(user_id)
                return curricula  # Return even if empty list
            except Exception as e:
                print(f"Database user curricula retrieval failed: {e}")
                if not self.use_file_backup:
                    return []
        
        # Fallback to file storage if backup is enabled
        if self.use_file_backup:
            self.ensure_directories()  # Ensure directories exist before reading
            curricula = []
            
            if not os.path.exists(self.curricula_dir):
                return curricula
            
            try:
                for filename in os.listdir(self.curricula_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(self.curricula_dir, filename)
                        try:
                            with open(file_path, 'r') as f:
                                curriculum = json.load(f)
                                if curriculum.get("user_id") == user_id:
                                    curricula.append(curriculum)
                        except (json.JSONDecodeError, KeyError):
                            continue
                
                # Sort by creation date, newest first
                curricula.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                return curricula
            except Exception as e:
                print(f"File storage user curricula retrieval failed: {e}")
                return []
        
        return []

    async def create_curriculum_record(self, user_id: int, metadata: Dict[str, Any]) -> str:
        """Create curriculum record without content (for background generation)"""
        self.ensure_directories()  # Ensure directories exist before writing
        curriculum_id = str(uuid.uuid4())
        
        # Create in database (primary storage)
        if self.use_database:
            try:
                db_curriculum_id = await database.create_curriculum_record(user_id, metadata, curriculum_id)
                # The database should return the same curriculum_id we passed
                assert db_curriculum_id == curriculum_id, f"UUID mismatch: {curriculum_id} vs {db_curriculum_id}"
            except Exception as e:
                print(f"Database record creation failed: {e}")
                if not self.use_file_backup:
                    raise e
        
        # Create file backup if enabled
        if self.use_file_backup:
            curriculum_record = {
                "id": curriculum_id,
                "user_id": user_id,
                "metadata": metadata,
                "created_at": datetime.utcnow().isoformat(),
                "status": {
                    "curriculum": ContentStatus.PENDING,
                    "flashcards": ContentStatus.PENDING,
                    "exercises": ContentStatus.PENDING,
                    "simulation": ContentStatus.PENDING
                },
                "content": {
                    "curriculum": None,
                    "flashcards": None,
                    "exercises": None,
                    "simulation": None
                }
            }
            
            try:
                file_path = os.path.join(self.curricula_dir, f"{curriculum_id}.json")
                async with self.get_lock(curriculum_id):
                    with open(file_path, 'w') as f:
                        json.dump(curriculum_record, f, indent=2)
            except Exception as e:
                print(f"File backup creation failed: {e}")
                # Don't fail if only backup fails
        
        return curriculum_id

# Import configuration
try:
    from backend.config import USE_DATABASE_PRIMARY, USE_FILE_BACKUP
except ImportError:
    USE_DATABASE_PRIMARY = True
    USE_FILE_BACKUP = False

# Global storage instance - Database-first with file backup fallback
storage = CurriculumStorage(use_database=True, use_file_backup=True) 