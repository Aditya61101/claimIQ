from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from datetime import datetime, timezone
from app.core.database import Base


class PolicyPlan(Base):

    __tablename__ = 'policy_plans'

    id = Column(Integer, primary_key=True)

    plan_code = Column(String, unique=True, nullable=False, index=True)
    plan_name = Column(String, nullable=False)

    default_sum_insured = Column(Float, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )