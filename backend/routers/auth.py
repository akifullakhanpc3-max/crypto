from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from db import get_db, User
from utils.jwt_auth import create_access_token, verify_token
from utils.audit import log_audit

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # Truncate password to 72 bytes for bcrypt compatibility
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(db_user.id), "username": db_user.username, "role": db_user.role}
    )
    
    await log_audit(db, db_user.id, "signup", "user", str(db_user.id), "127.0.0.1", "success")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "username": db_user.username,
        "role": db_user.role
    }

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, user_credentials.username)
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        await log_audit(db, None, "login", "user", None, "127.0.0.1", "failure")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )
    
    await log_audit(db, user.id, "login", "user", str(user.id), "127.0.0.1", "success")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token_data = verify_token(credentials.credentials)
    user = db.query(User).filter(User.id == int(token_data.get("sub"))).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at
    }