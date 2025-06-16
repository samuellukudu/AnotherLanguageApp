from typing import Dict, List, Optional, Any
import logging
from psycopg2 import sql
from backend.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository):
    """Repository for user-related database operations"""
    
    def __init__(self):
        super().__init__("users")
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find a user by username"""
        query = sql.SQL("SELECT * FROM {} WHERE username = %s").format(sql.Identifier(self.table_name))
        return self._execute_query(query, (username,))
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email"""
        query = sql.SQL("SELECT * FROM {} WHERE email = %s").format(sql.Identifier(self.table_name))
        return self._execute_query(query, (email,))
    
    def get_user_progress(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all progress records for a user"""
        query = """
        SELECT p.*, a.activity_name, a.activity_type 
        FROM user_activity_progress p
        JOIN activities a ON p.activity_id = a.activity_id
        WHERE p.user_id = %s
        ORDER BY p.last_accessed DESC
        """
        return self._execute_query(query, (user_id,), many=True)
    
    def get_user_curriculum(self, user_id: int) -> List[Dict[str, Any]]:
        """Get curriculum data for a user"""
        query = """
        SELECT c.*, w.* 
        FROM curriculums c
        LEFT JOIN weekly_modules w ON c.curriculum_id = w.curriculum_id
        WHERE c.user_id = %s
        ORDER BY w.week_number
        """
        return self._execute_query(query, (user_id,), many=True)
    
    def get_user_flashcards(self, user_id: int) -> List[Dict[str, Any]]:
        """Get flashcard sets for a user"""
        query = """
        SELECT fs.*, f.* 
        FROM flashcard_sets fs
        LEFT JOIN generated_flashcards f ON fs.set_id = f.set_id
        WHERE fs.user_id = %s
        ORDER BY fs.created_at DESC
        """
        return self._execute_query(query, (user_id,), many=True)
    
    def get_user_exercises(self, user_id: int) -> List[Dict[str, Any]]:
        """Get exercise sets for a user"""
        query = """
        SELECT es.*, e.* 
        FROM exercise_sets es
        LEFT JOIN generated_exercises e ON es.set_id = e.set_id
        WHERE es.user_id = %s
        ORDER BY es.created_at DESC
        """
        return self._execute_query(query, (user_id,), many=True)
    
    def get_user_simulations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get simulation records for a user"""
        query = """
        SELECT * FROM simulations
        WHERE user_id = %s
        ORDER BY created_at DESC
        """
        return self._execute_query(query, (user_id,), many=True)
    
    def update_user_progress(self, user_id: int, activity_id: int, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update or create a user's progress for an activity"""
        # Check if progress record exists
        check_query = """
        SELECT * FROM user_activity_progress 
        WHERE user_id = %s AND activity_id = %s
        """
        existing = self._execute_query(check_query, (user_id, activity_id))
        
        if existing:
            # Update existing record
            set_items = []
            values = []
            
            for key, value in progress_data.items():
                set_items.append(sql.SQL("{} = %s").format(sql.Identifier(key)))
                values.append(value)
                
            values.extend([user_id, activity_id])  # Add for WHERE clause
            
            query = sql.SQL("""
            UPDATE user_activity_progress 
            SET {}, last_accessed = CURRENT_TIMESTAMP 
            WHERE user_id = %s AND activity_id = %s
            RETURNING *
            """).format(sql.SQL(', ').join(set_items))
            
            return self._execute_query(query, values)
        else:
            # Create new record
            data = {**progress_data, "user_id": user_id, "activity_id": activity_id}
            columns = list(data.keys())
            values = list(data.values())
            
            query = sql.SQL("""
            INSERT INTO user_activity_progress ({}) 
            VALUES ({}) 
            RETURNING *
            """).format(
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )
            
            return self._execute_query(query, values)