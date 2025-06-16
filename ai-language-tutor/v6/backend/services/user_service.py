from typing import Dict, List, Optional, Any
import logging
from backend.repositories.user_repository import UserRepository
from backend.core.exceptions import ResourceNotFoundException, ValidationException
from backend.services.base_service import BaseService

logger = logging.getLogger(__name__)

class UserService(BaseService):
    """Service for user-related operations"""
    
    def __init__(self):
        self.repository = UserRepository()
        super().__init__(self.repository)
        logger.info("User Service initialized")
    
    async def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get a user by ID"""
        self.log_operation("get_user_by_id", user_id=user_id)
        
        user = self.repository.find_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        return user
    
    async def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Get a user by username"""
        self.log_operation("get_user_by_username", username=username)
        
        user = self.repository.find_by_username(username)
        if not user:
            raise ResourceNotFoundException("User", username)
        return user
    
    async def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get a user by email"""
        self.log_operation("get_user_by_email", email=email)
        
        user = self.repository.find_by_email(email)
        if not user:
            raise ResourceNotFoundException("User", email)
        return user
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        self.log_operation("create_user")
        
        # Check if username or email already exists
        existing_username = self.repository.find_by_username(user_data.get("username"))
        if existing_username:
            raise ValidationException(
                message="Username already exists",
                details={"field": "username"}
            )
        
        existing_email = self.repository.find_by_email(user_data.get("email"))
        if existing_email:
            raise ValidationException(
                message="Email already exists",
                details={"field": "email"}
            )
        
        # Create the user
        return self.repository.create(user_data)
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user"""
        self.log_operation("update_user", user_id=user_id)
        
        # Check if user exists
        existing_user = self.repository.find_by_id(user_id)
        if not existing_user:
            raise ResourceNotFoundException("User", user_id)
        
        # Check if username is being changed and if it already exists
        if "username" in user_data and user_data["username"] != existing_user["username"]:
            existing_username = self.repository.find_by_username(user_data["username"])
            if existing_username:
                raise ValidationException(
                    message="Username already exists",
                    details={"field": "username"}
                )
        
        # Check if email is being changed and if it already exists
        if "email" in user_data and user_data["email"] != existing_user["email"]:
            existing_email = self.repository.find_by_email(user_data["email"])
            if existing_email:
                raise ValidationException(
                    message="Email already exists",
                    details={"field": "email"}
                )
        
        # Update the user
        return self.repository.update(user_id, user_data)
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        self.log_operation("delete_user", user_id=user_id)
        
        # Check if user exists
        existing_user = self.repository.find_by_id(user_id)
        if not existing_user:
            raise ResourceNotFoundException("User", user_id)
        
        # Delete the user
        return self.repository.delete(user_id)
    
    async def get_user_progress(self, user_id: int) -> List[Dict[str, Any]]:
        """Get a user's progress"""
        self.log_operation("get_user_progress", user_id=user_id)
        
        # Check if user exists
        existing_user = self.repository.find_by_id(user_id)
        if not existing_user:
            raise ResourceNotFoundException("User", user_id)
        
        return self.repository.get_user_progress(user_id)
    
    async def update_user_progress(self, user_id: int, activity_id: int, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user's progress for an activity"""
        self.log_operation("update_user_progress", user_id=user_id, activity_id=activity_id)
        
        # Check if user exists
        existing_user = self.repository.find_by_id(user_id)
        if not existing_user:
            raise ResourceNotFoundException("User", user_id)
        
        return self.repository.update_user_progress(user_id, activity_id, progress_data)

# Create a global service instance
user_service = UserService()