from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime

class Hospital(Base):
    __tablename__ = 'hospitals'

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, index=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)

    is_blacklisted = Column(Boolean, default=False, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

