"""
SQLAlchemy Project model representing developer organizations / teams.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class AccessTier(str, enum.Enum):
    DEVELOPER = "DEVELOPER"
    BUILDER = "BUILDER"
    PROTOCOL = "PROTOCOL"
    ENTERPRISE = "ENTERPRISE"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    tier = Column(Enum(AccessTier), default=AccessTier.DEVELOPER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")
