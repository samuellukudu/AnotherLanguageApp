from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from supabase import Client
from backend.db.supabase_client import get_supabase
from backend.auth import authenticate_user, create_access_token, get_password_hash
from backend.db.repositories import create_user, get_user_by_username, get_user_by_email, create_refresh_token, get_refresh_token, delete_refresh_token
from backend.schemas import Token, User as UserSchema, UserCreate
import uuid
import urllib.parse
import httpx
from fastapi.responses import RedirectResponse
import logging
from backend.settings import settings
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import Body

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Client = Depends(get_supabase)
):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(data={"sub": user.username})
    # issue refresh token
    refresh_token = uuid4().hex
    expires_at = (datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)).isoformat()
    await create_refresh_token(session, refresh_token, user.user_id, expires_at)
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.user_id, "refresh_token": refresh_token}

@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token_str: str = Body(...),
    session: Client = Depends(get_supabase)
):
    record = await get_refresh_token(session, refresh_token_str)
    if not record or record.get("expires_at") < datetime.utcnow().isoformat():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    user_id = record.get("user_id")
    access_token = await create_access_token(data={"sub": record.get("username") or record.get("user_id")})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user_id, "refresh_token": refresh_token_str}

@router.post("/token/revoke")
async def revoke_refresh_token(
    refresh_token_str: str = Body(...),
    session: Client = Depends(get_supabase)
):
    await delete_refresh_token(session, refresh_token_str)
    return {"status": "revoked"}

@router.post("/users", response_model=UserSchema)
async def signup_user(
    user_create: UserCreate,
    session: Client = Depends(get_supabase)
):
    # Prevent duplicate usernames
    existing = await get_user_by_username(session, user_create.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # Basic password strength check
    if len(user_create.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long"
        )
    hashed_password = get_password_hash(user_create.password)
    try:
        new_user = await create_user(session, user_create.username, user_create.email, hashed_password)
        return new_user
    except Exception as e:
        logging.exception(f"signup_user failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Google OAuth2 endpoints
@router.get("/auth/google/login")
def google_login():
    params = {
        "client_id": settings.google_client_id,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": settings.google_redirect_uri,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)

@router.get("/auth/google/callback", response_model=Token)
async def google_callback(code: str, session: Client = Depends(get_supabase)):
    # Exchange authorization code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    resp = httpx.post(token_url, data=data)
    resp.raise_for_status()
    tokens = resp.json()
    access_token = tokens.get("access_token")
    # Fetch userinfo
    userinfo = httpx.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()
    email = userinfo.get("email")
    # Find or create user by email
    user = await get_user_by_email(session, email)
    if not user:
        base_username = email.split("@")[0]
        # Ensure unique username
        if await get_user_by_username(session, base_username):
            base_username = f"{base_username}_{uuid.uuid4().hex[:6]}"
        # Create with random password
        pwd = uuid.uuid4().hex
        user = await create_user(session, base_username, email, get_password_hash(pwd))
    # Issue our JWT
    token = await create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "user_id": user.user_id}
