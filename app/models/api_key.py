"""
SQLAlchemy APIKey model representing project access keys (qig_live_, qig_test_, qig_ci_).
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class KeyType(str, enum.Enum):
    LIVE = "LIVE"
    TEST = "TEST"
    CI = "CI"


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    key_prefix = Column(String(16), nullable=False, index=True)  # e.g., qig_live_abc1
    hashed_key = Column(String(255), nullable=False, unique=True, index=True)
    key_type = Column(Enum(KeyType), default=KeyType.LIVE, nullable=False)
    name = Column(String(100), default="Default Key")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="api_keys")
