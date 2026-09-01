"""
SQLAlchemy Contract model for storing analyzed Soroban contract metadata.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_address = Column(String(64), nullable=True, index=True)
    wasm_hash = Column(String(64), nullable=False, index=True)
    source_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    jobs = relationship("Job", back_populates="contract")
