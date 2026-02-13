from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise credentials_exception
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


def require_role(required_roles: list[str]):
    """Return a dependency that ensures the current user has an allowed role."""
    def _role_guard(current_user: User = Depends(get_current_user)) -> User:
        role_name = getattr(current_user.role, "name", None)
        if role_name not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden"
            )
        return current_user

    return _role_guard


def ensure_owner_or_admin(owner_id: int, current_user: User) -> None:
    """Ensure the current user is the owner or has admin role."""
    role_name = getattr(current_user.role, "name", None)
    if role_name != "admin" and owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
