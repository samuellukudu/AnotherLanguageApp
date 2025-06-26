from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
import os
from backend.utils.supabase_client import supabase

# Get Supabase JWT secret - this should be the JWT secret from your Supabase project settings
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

async def get_current_user(request: Request):
    """
    Extract and validate JWT token from Authorization header
    Returns the decoded user payload from Supabase
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    
    if not SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret not configured"
        )
    
    try:
        # Decode JWT token - Supabase uses HS256 for project JWTs
        # Set audience to "authenticated" which is what Supabase uses
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            audience="authenticated",  # Supabase's default audience
            options={"verify_aud": True}  # Explicitly verify audience
        )
        
        # Verify the token is still valid with Supabase
        try:
            user_response = supabase.auth.get_user(token)
            if not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed"
            )
        
        return payload  # Contains user info like user_id, email, etc.
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_dependency():
    """
    Dependency function to be used with FastAPI's Depends()
    """
    return Depends(get_current_user)

async def verify_curriculum_ownership(curriculum_id: int, user_id: str):
    """
    Verify that the user owns the specified curriculum
    """
    try:
        result = supabase.table("curriculums").select("user_id").eq("id", curriculum_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Curriculum not found")
        
        curriculum_user_id = result.data[0].get("user_id")
        if curriculum_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied: You don't own this curriculum")
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify curriculum ownership: {str(e)}") 