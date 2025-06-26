from backend.utils.supabase_client import supabase
from backend.schemas.user import UserRegister, UserLogin, AuthResponse, UserProfile
from fastapi import HTTPException
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_user(payload: UserRegister) -> AuthResponse:
    """
    Register a new user with Supabase Auth and create user profile
    """
    try:
        # Register user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": payload.email, 
            "password": payload.password,
            "options": {
                "data": {
                    "username": payload.username,
                    "native_language": payload.native_language,
                    "target_languages": payload.target_languages
                }
            }
        })
        
        logger.info(f"Auth response: {auth_response}")
        
        # Check if registration was successful
        if hasattr(auth_response, 'user') and auth_response.user:
            user = auth_response.user
            
            # Create user profile in users table
            try:
                profile_data = {
                    "id": user.id,
                    "email": payload.email,
                    "username": payload.username or user.email.split('@')[0],
                    "native_language": payload.native_language,
                    "target_languages": payload.target_languages or [],
                    "timezone": payload.timezone,
                    "xp": 0,
                    "streak": 0,
                    "daily_goal": 50,
                    "notification_preferences": {
                        "push_notifications": True,
                        "email_notifications": True,
                        "reminder_time": "19:00"
                    },
                    "learning_preferences": {
                        "theme": "light",
                        "sound_enabled": True,
                        "interface_language": "en"
                    }
                }
                
                profile_response = supabase.table("users").insert(profile_data).execute()
                logger.info(f"Profile created: {profile_response}")
                
            except Exception as profile_error:
                logger.error(f"Profile creation error: {profile_error}")
                # Don't fail registration if profile creation fails
                pass
            
            # Check if we have a session (user might need email confirmation)
            if hasattr(auth_response, 'session') and auth_response.session:
                return AuthResponse(
                    access_token=auth_response.session.access_token,
                    user_id=user.id
                )
            else:
                # User registered but needs email confirmation
                raise HTTPException(
                    status_code=201,
                    detail="Registration successful! Please check your email to confirm your account before logging in."
                )
        else:
            # Registration failed
            error_message = "Registration failed"
            if hasattr(auth_response, 'error') and auth_response.error:
                error_message = auth_response.error.message
            
            raise HTTPException(status_code=400, detail=error_message)
            
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        logger.error(f"Registration exception: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

def login_user(payload: UserLogin) -> AuthResponse:
    """
    Authenticate user with Supabase Auth
    """
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })
        
        logger.info(f"Login response: {auth_response}")
        
        # Check if login was successful
        if (hasattr(auth_response, 'user') and auth_response.user and 
            hasattr(auth_response, 'session') and auth_response.session):
            
            # Update last_active timestamp and login count
            try:
                # First get current login count
                current_user = supabase.table("users").select("login_count").eq("id", auth_response.user.id).execute()
                current_login_count = current_user.data[0]["login_count"] if current_user.data else 0
                
                # Update with proper timestamp
                from datetime import datetime
                supabase.table("users").update({
                    "last_active": datetime.now().isoformat(),
                    "login_count": current_login_count + 1
                }).eq("id", auth_response.user.id).execute()
            except Exception as e:
                logger.warning(f"Could not update last_active/login_count: {e}")
            
            return AuthResponse(
                access_token=auth_response.session.access_token,
                user_id=auth_response.user.id
            )
        else:
            # Login failed
            error_message = "Invalid email or password"
            if hasattr(auth_response, 'error') and auth_response.error:
                error_message = auth_response.error.message
                
            raise HTTPException(status_code=401, detail=error_message)
            
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        logger.error(f"Login exception: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

def get_user_profile(user_id: str) -> UserProfile:
    """
    Get user profile from users table with graceful handling of missing fields
    """
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        profile_data = result.data[0]
        logger.info(f"Raw profile data: {profile_data}")
        
        # Handle missing fields gracefully
        normalized_profile = {
            "id": profile_data.get("id"),
            "email": profile_data.get("email"),
            "username": profile_data.get("username") or profile_data.get("email", "").split('@')[0],
            "display_name": profile_data.get("display_name"),
            "bio": profile_data.get("bio"),
            "native_language": profile_data.get("native_language"),
            "target_languages": profile_data.get("target_languages", []),
            "xp": profile_data.get("xp", 0),
            "streak": profile_data.get("streak", 0),
            "daily_goal": profile_data.get("daily_goal", 50),
            "timezone": profile_data.get("timezone"),
            "notification_preferences": profile_data.get("notification_preferences", {}),
            "learning_preferences": profile_data.get("learning_preferences", {}),
            "achievements": profile_data.get("achievements", []),
            "total_lessons_completed": profile_data.get("total_lessons_completed", 0),
            "total_time_spent": profile_data.get("total_time_spent", 0),
            "created_at": profile_data.get("created_at", ""),
            "updated_at": profile_data.get("updated_at", "")
        }
        
        # Add optional fields that might not exist in older databases
        if "last_active" in profile_data:
            normalized_profile["last_active"] = profile_data.get("last_active")
        if "longest_streak" in profile_data:
            normalized_profile["longest_streak"] = profile_data.get("longest_streak", profile_data.get("streak", 0))
        if "login_count" in profile_data:
            normalized_profile["login_count"] = profile_data.get("login_count", 0)
        
        return UserProfile(**normalized_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile exception: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")

def update_user_profile(user_id: str, updates: dict) -> UserProfile:
    """
    Update user profile in users table
    """
    try:
        # Remove any fields that shouldn't be updated
        allowed_fields = {
            "username", "display_name", "bio", "native_language", "target_languages",
            "daily_goal", "timezone", "notification_preferences", "learning_preferences",
            "xp", "streak"
        }
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if not filtered_updates:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        result = supabase.table("users").update(filtered_updates).eq("id", user_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="User not found or update failed")
        
        return get_user_profile(user_id)  # Use the normalized get function
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile exception: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")

def change_password(user_id: str, current_password: str, new_password: str):
    """
    Change user's password using Supabase Auth
    """
    try:
        # Supabase handles password changes through the auth API
        response = supabase.auth.update_user({
            "password": new_password
        })
        
        if hasattr(response, 'user') and response.user:
            return {"message": "Password updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to update password")
            
    except Exception as e:
        logger.error(f"Change password exception: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

def request_password_reset(email: str):
    """
    Request password reset email
    """
    try:
        response = supabase.auth.reset_password_email(email)
        return {"message": "If this email exists, a password reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Password reset request exception: {e}")
        # Don't reveal if email exists or not for security
        return {"message": "If this email exists, a password reset link has been sent"}

def reset_password(token: str, new_password: str):
    """
    Reset password using reset token
    """
    try:
        # This would typically be handled by Supabase's auth flow
        # The actual implementation depends on how you handle password reset tokens
        response = supabase.auth.update_user({
            "password": new_password
        })
        
        if hasattr(response, 'user') and response.user:
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
            
    except Exception as e:
        logger.error(f"Password reset exception: {e}")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

def get_user_stats(user_id: str):
    """
    Get comprehensive user statistics
    """
    try:
        # Get user profile
        profile = get_user_profile(user_id)
        
        # Calculate additional stats with safe field access
        stats = {
            "user_id": user_id,
            "total_xp": getattr(profile, 'xp', 0),
            "current_streak": getattr(profile, 'streak', 0),
            "longest_streak": getattr(profile, 'longest_streak', getattr(profile, 'streak', 0)),
            "total_lessons_completed": getattr(profile, 'total_lessons_completed', 0),
            "total_time_spent": getattr(profile, 'total_time_spent', 0),
            "achievements_count": len(getattr(profile, 'achievements', []) or []),
            "daily_goal": getattr(profile, 'daily_goal', 50),
            "join_date": getattr(profile, 'created_at', None),
            "last_active": getattr(profile, 'last_active', None),
            "favorite_language": (getattr(profile, 'target_languages', []) or [None])[0]
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Get user stats exception: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user statistics")

def get_user_sessions(user_id: str):
    """
    Get user's active sessions for device management
    """
    try:
        result = supabase.table("user_sessions").select("*").eq("user_id", user_id).eq("is_active", True).execute()
        
        sessions = []
        for session in result.data:
            sessions.append({
                "id": session["id"],
                "device_info": session.get("device_info", {}),
                "created_at": session["created_at"],
                "last_used": session.get("last_used"),
                "is_current": False  # You'd determine this based on current session
            })
        
        return {"sessions": sessions}
        
    except Exception as e:
        logger.error(f"Get user sessions exception: {e}")
        return {"sessions": []}

def deactivate_account(user_id: str):
    """
    Deactivate user account (soft delete)
    """
    try:
        result = supabase.table("users").update({
            "account_status": "deactivated"
        }).eq("id", user_id).execute()
        
        if result.data:
            return {"message": "Account deactivated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
        logger.error(f"Deactivate account exception: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate account")

def create_user_goal(user_id: str, goal_data: dict):
    """
    Create a new learning goal for user
    """
    try:
        goal_data["user_id"] = user_id
        result = supabase.table("user_goals").insert(goal_data).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=400, detail="Failed to create goal")
            
    except Exception as e:
        logger.error(f"Create user goal exception: {e}")
        raise HTTPException(status_code=500, detail="Failed to create goal")

def get_user_goals(user_id: str):
    """
    Get all user's learning goals
    """
    try:
        result = supabase.table("user_goals").select("*").eq("user_id", user_id).execute()
        return {"goals": result.data}
        
    except Exception as e:
        logger.error(f"Get user goals exception: {e}")
        return {"goals": []}

def update_user_goal(user_id: str, goal_id: int, updates: dict):
    """
    Update a user's learning goal
    """
    try:
        result = supabase.table("user_goals").update(updates).eq("id", goal_id).eq("user_id", user_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise HTTPException(status_code=404, detail="Goal not found")
            
    except Exception as e:
        logger.error(f"Update user goal exception: {e}")
        raise HTTPException(status_code=500, detail="Failed to update goal") 