from datetime import datetime, timezone

from app.core.database import SessionLocal
# models
from app.models.documents import Document
from app.models.claims import Claim
# services
from app.services.claim_status import update_claim_processing_status
from app.extraction.extract_router import extract_structured_data

def extract_document(document_id:int):
    """
        Background task:
        - Updates document status
        - Simulates extraction
    """
    # Dependency injection lifecycle ends after response is sent
    # Session would be closed, so we make a new session.
    db = SessionLocal()
    try:

        document = db.query(Document).filter(Document.id==document_id).first()
        if not document:
            return
        
        claim = db.query(Claim).get(document.claim_id)
        if not claim:
            return

        document.status = "PROCESSING"
        db.commit()

        # TODO: extraction logic here


        if not document.extracted_text:
            raise ValueError("No OCR text available")

        structured = extract_structured_data(
            document_type=document.document_type,
            claim_type=claim.claim_type,
            text=document.extracted_text,
        )

        document.extracted_data = structured
        document.status = "EXTRACTED"
        document.processed_at = datetime.now(timezone.utc)
        db.commit()

        ## TODO: INVOKE Langgraph

    except Exception as e:
        document.status = "FAILED"
        document.error_message = str(e)
        document.processed_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        # updating claim processing
        update_claim_processing_status(document.claim_id, db)
        db.close()