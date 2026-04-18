from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, index=True, nullable=False)
    password_hash: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    # is_active=False until MFA setup is verified during registration
    is_active: bool = Column(Boolean, default=True, nullable=False)
    mfa_enabled: bool = Column(Boolean, default=False, nullable=False)
    mfa_secret_encrypted: str | None = Column(Text, nullable=True)
    backup_codes: str | None = Column(Text, nullable=True)

    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")
