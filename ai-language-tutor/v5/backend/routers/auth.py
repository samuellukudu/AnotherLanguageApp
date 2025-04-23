from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from supabase import Client
from backend.db.supabase_client import get_supabase
from backend.auth import authenticate_user, create_access_token, get_password_hash
from backend.db.repositories import create_user, get_user_by_username, get_user_by_email
from backend.schemas import Token, User as UserSchema, UserCreate
import uuid
import urllib.parse
import httpx
from fastapi.responses import RedirectResponse
import logging
from backend.settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

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
    return {"access_token": access_token, "token_type": "bearer"}

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
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": GOOGLE_REDIRECT_URI,
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
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
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
    return {"access_token": token, "token_type": "bearer"}
