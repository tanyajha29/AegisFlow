from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from ..database import Base


class Scan(Base):
    __tablename__ = "scans"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name: str = Column(String(255), nullable=False)
    scan_date: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    risk_score: float = Column(Float, nullable=False, default=0.0)
    security_score: float = Column(Float, nullable=False, default=100.0)
    total_findings: int = Column(Integer, nullable=False, default=0)
    critical_count: int = Column(Integer, nullable=False, default=0)
    high_count: int = Column(Integer, nullable=False, default=0)
    medium_count: int = Column(Integer, nullable=False, default=0)
    low_count: int = Column(Integer, nullable=False, default=0)
    total_issues: int = Column(Integer, nullable=False, default=0)
    vulnerability_snapshot = Column(JSON, nullable=False, default=list)

    user = relationship("User", back_populates="scans")
    vulnerabilities = relationship(
        "Vulnerability", back_populates="scan", cascade="all, delete-orphan", passive_deletes=True
    )
