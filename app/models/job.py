"""
SQLAlchemy Job model for analysis runs (Contract, Behavioral, Resilience).
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, JSON, Enum
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class JobType(str, enum.Enum):
    CONTRACT_RISK = "CONTRACT_RISK"
    BEHAVIORAL_ANOMALY = "BEHAVIORAL_ANOMALY"
    QUANTUM_RESILIENCE = "QUANTUM_RESILIENCE"


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    contract_id = Column(String(36), ForeignKey("contracts.id"), nullable=True)
    target_address = Column(String(64), nullable=True)
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.COMPLETED, nullable=False)
    
    # Risk & Benchmark metrics
    classical_score = Column(Float, nullable=True)
    hybrid_score = Column(Float, nullable=True)
    delta_score = Column(Float, nullable=True)
    
    classical_latency_ms = Column(Float, nullable=True)
    hybrid_latency_ms = Column(Float, nullable=True)
    
    model_version = Column(String(64), default="qi-guard-stellar-0.1.0")
    quantum_config = Column(JSON, nullable=True)
    raw_response = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="jobs")
    contract = relationship("Contract", back_populates="jobs")
    findings = relationship("Finding", back_populates="job", cascade="all, delete-orphan")
