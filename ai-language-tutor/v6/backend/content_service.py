import json
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from backend.database import AsyncSessionLocal, SavedContent, UserMetadata, generate_content_id
import logging

logger = logging.getLogger(__name__)


class ContentService:
    """Service for saving and retrieving AI-generated content"""
    
    async def save_metadata(
        self, 
        query: str, 
        metadata: Dict[str, Any], 
        user_id: Optional[int] = None
    ) -> str:
        """
        Save extracted metadata to database
        
        Args:
            query: Original user query
            metadata: Extracted metadata dict
            user_id: Optional user ID
            
        Returns:
            content_id: Unique identifier for the saved content
        """
        async with AsyncSessionLocal() as session:
            # Save to user_metadata table
            user_metadata = UserMetadata(
                user_id=user_id,
                query=query,
                native_language=metadata.get("native_language"),
                target_language=metadata.get("target_language"),
                proficiency=metadata.get("proficiency"),
                title=metadata.get("title"),
                description=metadata.get("description")
            )
            session.add(user_metadata)
            
            # Also save to general saved_content table
            content_id = generate_content_id(query, "metadata", user_id)
            saved_content = SavedContent(
                content_id=content_id,
                content_type="metadata",
                user_id=user_id,
                query=query,
                generated_content=json.dumps(metadata),
                native_language=metadata.get("native_language"),
                target_language=metadata.get("target_language"),
                proficiency=metadata.get("proficiency")
            )
            
            try:
                session.add(saved_content)
                await session.commit()
                logger.info(f"Saved metadata for query: {query[:50]}...")
                return content_id
            except IntegrityError:
                # Content already exists, return existing ID
                await session.rollback()
                return content_id
    
    async def save_content(
        self,
        query: str,
        content: str,
        content_type: str,
        user_id: Optional[int] = None,
        native_language: Optional[str] = None,
        target_language: Optional[str] = None,
        proficiency: Optional[str] = None
    ) -> str:
        """
        Save generated content to database
        
        Args:
            query: Original user query
            content: Generated content (JSON string)
            content_type: Type of content (curriculum, flashcards, etc.)
            user_id: Optional user ID
            native_language: User's native language
            target_language: Language being learned
            proficiency: User's proficiency level
            
        Returns:
            content_id: Unique identifier for the saved content
        """
        content_id = generate_content_id(query, content_type, user_id)
        
        async with AsyncSessionLocal() as session:
            saved_content = SavedContent(
                content_id=content_id,
                content_type=content_type,
                user_id=user_id,
                query=query,
                generated_content=content,
                native_language=native_language,
                target_language=target_language,
                proficiency=proficiency
            )
            
            try:
                session.add(saved_content)
                await session.commit()
                logger.info(f"Saved {content_type} content for query: {query[:50]}...")
                return content_id
            except IntegrityError:
                # Content already exists, return existing ID
                await session.rollback()
                return content_id
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get saved content by content ID"""
        async with AsyncSessionLocal() as session:
            stmt = select(SavedContent).where(SavedContent.content_id == content_id)
            result = await session.execute(stmt)
            content = result.scalar_one_or_none()
            
            if content:
                return {
                    "content_id": content.content_id,
                    "content_type": content.content_type,
                    "query": content.query,
                    "content": content.generated_content,
                    "native_language": content.native_language,
                    "target_language": content.target_language,
                    "proficiency": content.proficiency,
                    "created_at": content.created_at.isoformat(),
                    "updated_at": content.updated_at.isoformat()
                }
            return None
    
    async def get_user_metadata_history(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's metadata extraction history"""
        async with AsyncSessionLocal() as session:
            stmt = select(UserMetadata).where(
                UserMetadata.user_id == user_id
            ).order_by(UserMetadata.created_at.desc()).limit(limit)
            
            result = await session.execute(stmt)
            metadata_list = result.scalars().all()
            
            return [
                {
                    "id": meta.id,
                    "query": meta.query,
                    "native_language": meta.native_language,
                    "target_language": meta.target_language,
                    "proficiency": meta.proficiency,
                    "title": meta.title,
                    "description": meta.description,
                    "created_at": meta.created_at.isoformat()
                }
                for meta in metadata_list
            ]
    
    async def get_user_content(
        self, 
        user_id: int, 
        content_type: Optional[str] = None, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's saved content"""
        async with AsyncSessionLocal() as session:
            stmt = select(SavedContent).where(SavedContent.user_id == user_id)
            
            if content_type:
                stmt = stmt.where(SavedContent.content_type == content_type)
            
            stmt = stmt.order_by(SavedContent.created_at.desc()).limit(limit)
            
            result = await session.execute(stmt)
            content_list = result.scalars().all()
            
            return [
                {
                    "content_id": content.content_id,
                    "content_type": content.content_type,
                    "query": content.query,
                    "content": content.generated_content,
                    "native_language": content.native_language,
                    "target_language": content.target_language,
                    "proficiency": content.proficiency,
                    "created_at": content.created_at.isoformat()
                }
                for content in content_list
            ]
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete saved content by ID"""
        async with AsyncSessionLocal() as session:
            stmt = select(SavedContent).where(SavedContent.content_id == content_id)
            result = await session.execute(stmt)
            content = result.scalar_one_or_none()
            
            if content:
                await session.delete(content)
                await session.commit()
                return True
            return False


# Initialize the content service
content_service = ContentService() 