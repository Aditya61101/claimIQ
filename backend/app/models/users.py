from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    # POLICY_HOLDER, INSURER, HOSPITAL
    role = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )