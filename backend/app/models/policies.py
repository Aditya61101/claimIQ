from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Date
from datetime import datetime, timezone
from app.core.database import Base


class Policy(Base):

    __tablename__ = 'policies'

    id = Column(Integer, primary_key=True, index=True)

    policy_number = Column(String, unique=True, nullable=False, index=True)

    plan_id = Column(Integer, ForeignKey("policy_plans.id", ondelete="RESTRICT"), nullable=False)

    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    total_sum_insured = Column(Float, nullable=False)
    approved_claim_amount = Column(Float, nullable=False, default=0.0) 

    policy_start_date = Column(Date, nullable=True)
    policy_end_date = Column(Date, nullable=True)

    issued_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )