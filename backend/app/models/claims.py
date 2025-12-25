from datetime import datetime, timezone
from app.core.database import Base

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship

class Claim(Base):
    __tablename__ = 'claims'

    id = Column(Integer, primary_key=True, index=True)
    
    policy_id = Column(String, nullable=False)
    claim_type = Column(String, nullable=False)
    status = Column(String, default='pending') # stale column
    amount = Column(Float, nullable=False)

    # DRAFT, DOCUMENT_PENDING, DOCUMENT_PROCESSING, ACTION_REQUIRED, READY_FOR_EVALUATION
    processing_status = Column(
        String,
        nullable=False,
        default="DRAFT"
    )

    decision_status = Column(
        String,
        nullable=False,
        default="NOT_DECIDED"
    )

    action_required = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    # for lazy loading, on demand document data fetching
    documents = relationship(
        "Document",
        backref="claim",
        cascade="all, delete-orphan"
    )