from datetime import timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user_model import User
from ..schemas.user_schema import Token, UserCreate, UserLogin, UserProfile
from ..utils.security_utils import create_access_token, hash_password, verify_password
from ..config import get_settings
from ..middleware.auth_middleware import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
logger = logging.getLogger("dristi-scan")


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=user_in.email, password_hash=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"user_id": user.id, "email": user.email})
    logger.info("User registered: %s", user.email)
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token({"user_id": user.id, "email": user.email}, expires_delta=access_token_expires)
    logger.info("User login: %s", user.email)
    return Token(access_token=access_token)


@router.get("/profile", response_model=UserProfile)
def profile(current_user: User = Depends(get_current_user)):
    return current_user
