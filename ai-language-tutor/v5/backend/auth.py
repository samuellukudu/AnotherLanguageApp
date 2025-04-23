from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from supabase import Client
from backend.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.db.repositories import get_user, get_user_by_username, create_user
from backend.db.supabase_client import get_supabase
from backend.schemas import Token, TokenData, User as UserModel, UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def authenticate_user(session: Client, username: str, password: str) -> Optional[UserModel]:
    user_data = await get_user_by_username(session, username)
    if not user_data:
        return None
    # Verify against raw password_hash; UserModel excludes it
    pwd_hash = user_data.get("password_hash")
    if not pwd_hash or not verify_password(password, pwd_hash):
        return None
    # Return sanitized UserModel (password_hash dropped)
    return UserModel(**user_data)

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), session: Client = Depends(get_supabase)) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user_data = await get_user_by_username(session, username)
    if user_data is None:
        raise credentials_exception
    return UserModel(**user_data)

async def get_current_active_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    # extend with is_active checks as needed
    return current_user

def require_roles(*roles: str):
    """Dependency to enforce user has one of the given roles."""
    async def role_checker(current_user: UserModel = Depends(get_current_active_user)) -> UserModel:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges"
            )
        return current_user
    return Depends(role_checker)
