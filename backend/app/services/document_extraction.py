import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.documents import Document

def extract_document(document_id:int, db:Session):
    """
        Background task:
        - Updates document status
        - Simulates extraction
    """
    
    # Dependency injection lifecycle ends after response
    # Session would be closed, so we give a real session.
    document = db.query(Document).filter(Document.id==document_id).first()

    if not document:
        return
    
    try:
        document.status = "PROCESSING"
        db.commit()

        # only for simulation
        time.sleep(3)

        # only for simulation
        document.extracted_text = f"Extracted text for document {document.file_name}"

        document.status = "EXTRACTED"
        document.processed_at = datetime.now(timezone.utc)

        db.commit()
    except Exception as e:
        document.status = "FAILED"
        document.error_message = str(e)
        document.processed_at = datetime.now(timezone.utc)
        db.commit()