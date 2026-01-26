from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.security import hash_password, verify_password
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# --------------------
# TEMP IN-MEMORY USER STORE
# (DB integration next step)
# --------------------
fake_users_db = {}


class UserSignup(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserSignup):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    fake_users_db[user.username] = {
        "username": user.username,
        "password": hash_password(user.password),
    }

    return {"message": "User created successfully"}


@router.post("/login")
def login(user: UserLogin):
    db_user = fake_users_db.get(user.username)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token({"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer",
    }
