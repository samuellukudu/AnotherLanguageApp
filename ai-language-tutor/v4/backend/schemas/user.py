from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    native_language: Optional[str] = None
    target_languages: Optional[List[str]] = None
    timezone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    native_language: Optional[str] = None
    target_languages: Optional[List[str]] = None
    xp: Optional[int] = 0
    streak: Optional[int] = 0
    daily_goal: Optional[int] = 50  # Daily XP goal
    timezone: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    learning_preferences: Optional[Dict[str, Any]] = None
    achievements: Optional[List[str]] = None
    total_lessons_completed: Optional[int] = 0
    total_time_spent: Optional[int] = 0  # in minutes
    created_at: str
    updated_at: str
    
    class Config:
        # Allow extra fields that might exist in the database
        extra = "ignore"

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    native_language: Optional[str] = None
    target_languages: Optional[List[str]] = None
    daily_goal: Optional[int] = None
    timezone: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    learning_preferences: Optional[Dict[str, Any]] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserPreferences(BaseModel):
    daily_goal: Optional[int] = 50
    reminder_time: Optional[str] = None  # e.g., "19:00"
    sound_enabled: Optional[bool] = True
    push_notifications: Optional[bool] = True
    email_notifications: Optional[bool] = True
    theme: Optional[str] = "light"  # light, dark
    interface_language: Optional[str] = "en"

class UserStats(BaseModel):
    user_id: str
    total_xp: int
    current_streak: int
    longest_streak: int
    total_lessons_completed: int
    total_time_spent: int  # in minutes
    achievements_count: int
    favorite_language: Optional[str] = None
    join_date: datetime
    last_active: Optional[datetime] = None 