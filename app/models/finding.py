"""
SQLAlchemy Finding model for individual security vulnerability records.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Enum, Text
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    finding_code = Column(String(64), nullable=False)  # e.g., QIG-SCF-0041
    finding_type = Column(String(64), nullable=False)  # e.g., ACCESS_CONTROL
    component = Column(String(255), nullable=True)     # e.g., transfer_admin()
    severity = Column(Enum(Severity), nullable=False)
    evidence = Column(JSON, nullable=True)             # Array of string evidence statements
    remediation = Column(Text, nullable=True)
    quantum_contribution = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="findings")
