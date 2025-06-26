import json
import os
import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ContentStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class CurriculumStorage:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.curricula_dir = os.path.join(storage_dir, "curricula")
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
        curriculum_id = str(uuid.uuid4())
        
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
        
        file_path = os.path.join(self.curricula_dir, f"{curriculum_id}.json")
        async with self.get_lock(curriculum_id):
            with open(file_path, 'w') as f:
                json.dump(curriculum_record, f, indent=2)
        
        return curriculum_id

    async def get_curriculum(self, curriculum_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve curriculum by ID"""
        file_path = os.path.join(self.curricula_dir, f"{curriculum_id}.json")
        if not os.path.exists(file_path):
            return None
        
        async with self.get_lock(curriculum_id):
            with open(file_path, 'r') as f:
                return json.load(f)

    async def update_content_status(self, curriculum_id: str, content_type: str, status: ContentStatus):
        """Update the status of a specific content type"""
        curriculum = await self.get_curriculum(curriculum_id)
        if not curriculum:
            return False
        
        curriculum["status"][content_type] = status
        curriculum["updated_at"] = datetime.utcnow().isoformat()
        
        file_path = os.path.join(self.curricula_dir, f"{curriculum_id}.json")
        async with self.get_lock(curriculum_id):
            with open(file_path, 'w') as f:
                json.dump(curriculum, f, indent=2)
        
        return True

    async def store_generated_content(self, curriculum_id: str, content_type: str, content_data: Dict[str, Any]):
        """Store generated content (flashcards, exercises, simulation)"""
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
        
        return True

    async def get_user_curricula(self, user_id: int) -> list[Dict[str, Any]]:
        """Get all curricula for a user"""
        curricula = []
        
        if not os.path.exists(self.curricula_dir):
            return curricula
        
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

    async def create_curriculum_record(self, user_id: int, metadata: Dict[str, Any]) -> str:
        """Create curriculum record without content (for background generation)"""
        curriculum_id = str(uuid.uuid4())
        
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
        
        file_path = os.path.join(self.curricula_dir, f"{curriculum_id}.json")
        async with self.get_lock(curriculum_id):
            with open(file_path, 'w') as f:
                json.dump(curriculum_record, f, indent=2)
        
        return curriculum_id

# Global storage instance
storage = CurriculumStorage() 