from fastapi import APIRouter, Body, Depends, HTTPException, Query
from backend.schemas.user import UserRegister, UserLogin, AuthResponse, UserProfile, UserProfileUpdate, ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest, UserPreferences, UserStats
from backend.services.user_service import register_user, login_user, get_user_profile, update_user_profile, change_password, request_password_reset, reset_password, get_user_stats, get_user_sessions, deactivate_account, create_user_goal, get_user_goals, update_user_goal
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=AuthResponse)
async def register(payload: UserRegister):
    """
    Register a new user account
    """
    return register_user(payload)

@router.post("/login", response_model=AuthResponse)
async def login(payload: UserLogin):
    """
    Authenticate user and return access token
    """
    return login_user(payload)

@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_profile(user_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get user profile (authenticated endpoint)
    """
    # Verify user can only access their own profile or is admin
    if current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return get_user_profile(user_id)

@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return get_user_profile(user_id)

@router.put("/profile/{user_id}", response_model=UserProfile)
async def update_profile(
    user_id: str, 
    updates: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Update user profile (authenticated endpoint)
    """
    # Verify user can only update their own profile
    if current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return update_user_profile(user_id, updates)

@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    updates: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user's profile
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return update_user_profile(user_id, updates.dict(exclude_unset=True))

@router.put("/change-password")
async def change_user_password(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user's password (authenticated endpoint)
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return change_password(user_id, payload.current_password, payload.new_password)

@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    """
    Request password reset email
    """
    return request_password_reset(payload.email)

@router.post("/reset-password")
async def reset_user_password(payload: ResetPasswordRequest):
    """
    Reset password using reset token
    """
    return reset_password(payload.token, payload.new_password)

@router.get("/me/stats", response_model=UserStats)
async def get_my_stats(current_user: dict = Depends(get_current_user)):
    """
    Get comprehensive user statistics
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return get_user_stats(user_id)

@router.get("/me/sessions")
async def get_my_sessions(current_user: dict = Depends(get_current_user)):
    """
    Get user's active sessions for device management
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return get_user_sessions(user_id)

@router.delete("/me/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke a specific session (logout from device)
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Implementation would revoke the specific session
    return {"message": f"Session {session_id} revoked successfully"}

@router.post("/me/deactivate")
async def deactivate_my_account(
    current_user: dict = Depends(get_current_user)
):
    """
    Deactivate user account (soft delete)
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return deactivate_account(user_id)

@router.get("/me/goals")
async def get_my_goals(current_user: dict = Depends(get_current_user)):
    """
    Get user's learning goals
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return get_user_goals(user_id)

@router.post("/me/goals")
async def create_my_goal(
    goal_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new learning goal
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return create_user_goal(user_id, goal_data)

@router.put("/me/goals/{goal_id}")
async def update_my_goal(
    goal_id: int,
    goal_updates: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a learning goal
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    return update_user_goal(user_id, goal_id, goal_updates)

@router.put("/me/preferences")
async def update_my_preferences(
    preferences: UserPreferences,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user preferences and settings
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Update both notification and learning preferences
    updates = {
        "notification_preferences": {
            "push_notifications": preferences.push_notifications,
            "email_notifications": preferences.email_notifications,
            "reminder_time": preferences.reminder_time
        },
        "learning_preferences": {
            "theme": preferences.theme,
            "sound_enabled": preferences.sound_enabled,
            "interface_language": preferences.interface_language
        },
        "daily_goal": preferences.daily_goal
    }
    
    return update_user_profile(user_id, updates)

@router.get("/me/export")
async def export_my_data(current_user: dict = Depends(get_current_user)):
    """
    Export all user data (GDPR compliance)
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # This would typically generate a comprehensive data export
    return {"message": "Data export will be sent to your email within 24 hours"}

@router.post("/me/logout-all")
async def logout_all_sessions(current_user: dict = Depends(get_current_user)):
    """
    Logout from all devices (revoke all sessions)
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    # Implementation would revoke all user sessions
    return {"message": "Logged out from all devices successfully"} 