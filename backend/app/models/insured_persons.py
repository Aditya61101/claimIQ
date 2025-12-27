from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from datetime import datetime, timezone
from app.core.database import Base

class InsuredPerson(Base):

    __tablename__ = 'insured_persons'

    id = Column(Integer, primary_key=True, index=True)

    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)

    full_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )