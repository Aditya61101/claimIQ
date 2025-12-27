from datetime import datetime, timezone
from app.core.database import Base

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Date
from sqlalchemy.orm import relationship

class Claim(Base):
    __tablename__ = 'claims'

    id = Column(Integer, primary_key=True, index=True)
    
    # claims are financial records and must not be deleted implicitly(ondelete='CASCADE') when related entities are removed.
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False)
    
    insured_person_id = Column(Integer, ForeignKey("insured_persons.id", ondelete="RESTRICT"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    claim_type = Column(String, nullable=False)
    diagnosis = Column(String, nullable=False)
    # status = Column(String, default='pending') # stale column
    
    claim_amount = Column(Float, nullable=False)
    approved_amount = Column(Float, nullable=True)

    treatment_date = Column(Date, nullable=True)
    # only for hospitalization
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    admission_date = Column(Date, nullable=True)
    discharge_date = Column(Date, nullable=True)

    # DRAFT, DOCUMENT_PENDING, DOCUMENT_PROCESSING, ACTION_REQUIRED, READY_FOR_EVALUATION, UNDER_REVIEW, COMPLETED
    processing_status = Column(
        String,
        nullable=False,
        default="DRAFT"
    )
    # PENDING, AI_APPROVED, AI_REJECTED, HUMAN_APPROVED, HUMAN_REJECTED
    decision_status = Column(
        String,
        nullable=False,
        default="PENDING"
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
        passive_deletes=True
        # cascade="all, delete-orphan"
    )