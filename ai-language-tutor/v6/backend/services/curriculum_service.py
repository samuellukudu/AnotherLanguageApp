from typing import Dict, List, Optional, Any
import logging
from backend.repositories.user_repository import UserRepository
from backend.core.exceptions import ResourceNotFoundException, ValidationException
from backend.services.base_service import BaseService
from backend.services.ai_service import ai_service
from backend.core.config import settings

logger = logging.getLogger(__name__)

class CurriculumService(BaseService):
    """Service for curriculum-related operations"""
    
    def __init__(self):
        self.repository = UserRepository()
        super().__init__(self.repository)
        logger.info("Curriculum Service initialized")
    
    async def generate_curriculum(self, user_id: int, query: str, metadata: Dict[str, str]) -> Dict[str, Any]:
        """Generate a curriculum for a user"""
        self.log_operation("generate_curriculum", user_id=user_id)
        
        # Check if user exists
        user = self.repository.find_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        
        # Format the curriculum instructions with metadata
        instructions = settings.curriculum_instructions.format(
            native_language=metadata.get("native_language", "unknown"),
            target_language=metadata.get("target_language", "unknown"),
            proficiency=metadata.get("proficiency", "unknown")
        )
        
        # Generate the curriculum using the AI service
        curriculum_content = await ai_service.get_completions(
            query,
            instructions,
            temperature=0.7,
            max_tokens=2048
        )
        
        # Store the curriculum in the database
        curriculum_data = {
            "user_id": user_id,
            "title": metadata.get("title", "Personalized Curriculum"),
            "description": metadata.get("description", "A personalized language learning curriculum"),
            "target_language": metadata.get("target_language", "unknown"),
            "native_language": metadata.get("native_language", "unknown"),
            "proficiency_level": metadata.get("proficiency", "unknown"),
            "content": curriculum_content
        }
        
        try:
            # Create a new curriculum record
            curriculum_record = self._create_curriculum(curriculum_data)
            
            return {
                "curriculum_id": curriculum_record.get("curriculum_id"),
                "title": curriculum_record.get("title"),
                "description": curriculum_record.get("description"),
                "content": curriculum_content,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error storing curriculum: {e}")
            # Return the generated content even if storage fails
            return {
                "curriculum_id": None,
                "title": metadata.get("title", "Personalized Curriculum"),
                "description": metadata.get("description", "A personalized language learning curriculum"),
                "content": curriculum_content,
                "metadata": metadata
            }
    
    def _create_curriculum(self, curriculum_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a curriculum record in the database"""
        try:
            # Insert into curriculums table
            query = """
            INSERT INTO curriculums 
            (user_id, title, description, target_language, native_language, proficiency_level, content) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
            RETURNING *
            """
            params = (
                curriculum_data["user_id"],
                curriculum_data["title"],
                curriculum_data["description"],
                curriculum_data["target_language"],
                curriculum_data["native_language"],
                curriculum_data["proficiency_level"],
                curriculum_data["content"]
            )
            
            return self.repository._execute_query(query, params)
        except Exception as e:
            logger.error(f"Database error creating curriculum: {e}")
            raise
    
    async def get_curriculum(self, curriculum_id: int) -> Dict[str, Any]:
        """Get a curriculum by ID"""
        self.log_operation("get_curriculum", curriculum_id=curriculum_id)
        
        query = "SELECT * FROM curriculums WHERE curriculum_id = %s"
        curriculum = self.repository._execute_query(query, (curriculum_id,))
        
        if not curriculum:
            raise ResourceNotFoundException("Curriculum", curriculum_id)
        
        return curriculum
    
    async def get_user_curriculums(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all curriculums for a user"""
        self.log_operation("get_user_curriculums", user_id=user_id)
        
        # Check if user exists
        user = self.repository.find_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        
        return self.repository.get_user_curriculum(user_id)

# Create a global service instance
curriculum_service = CurriculumService()