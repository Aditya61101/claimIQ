from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from datetime import datetime, timezone

from app.core.database import Base

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)

    claim_id = Column(
        Integer,
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    file_name = Column(String, nullable=False)
    original_file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    # bills, prescriptions, reports
    document_type = Column(String, nullable=False)
    content_type = Column(String, nullable=False)

    source = Column(String, nullable=False, default='USER_UPLOAD')
    # UPLOADED, EXTRACTED, EXTRACTION_FAILED VALIDATION_FAILED, VERIFICATION_FAILED, VERIFIED
    status = Column(String, nullable=False, default='UPLOADED')
    processing_stage = Column(String, nullable=True)
    
    extracted_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    
    error_message = Column(Text, nullable=True)
    
    uploaded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    processed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )