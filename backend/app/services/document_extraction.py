import time
from datetime import datetime, timezone

from app.core.database import SessionLocal

from app.models.documents import Document

from app.services.claim_status import update_claim_processing_status

def extract_document(document_id:int):
    """
        Background task:
        - Updates document status
        - Simulates extraction
    """
    # Dependency injection lifecycle ends after response
    # Session would be closed, so we give a real session.
    db = SessionLocal()
    try:

        document = db.query(Document).filter(Document.id==document_id).first()
        if not document:
            return

        document.status = "PROCESSING"
        db.commit()

        # TODO: extraction logic here

        document.status = "EXTRACTED"
        document.processed_at = datetime.now(timezone.utc)

        db.commit()
    except Exception as e:
        document.status = "FAILED"
        document.error_message = str(e)
        document.processed_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        # updating claim processing
        update_claim_processing_status(document.claim_id, db)
        db.close()