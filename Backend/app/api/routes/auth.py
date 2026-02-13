from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.seed import seed_default_roles
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.api.deps import get_current_user
from app.api.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    seed_default_roles(db)
    default_role = db.query(Role).filter(Role.name == "user").first()
    if not default_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default role not configured"
        )

    user = User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        is_active=True,
        role_id=default_role.id
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    access_token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
