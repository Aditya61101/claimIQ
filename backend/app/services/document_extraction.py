from datetime import datetime, timezone

from app.core.database import SessionLocal
# models
from app.models.documents import Document
from app.models.claims import Claim
# services
from app.services.claim_status import update_claim_processing_status
from app.extraction.structured.extract_router import extract_structured_data
from app.extraction.raw_unstructured.extract_router import extract_text

from app.orchestration.document_graph import document_graph

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

        document.processing_stage = "EXTRACTION"
        db.commit()

        text = extract_text(document.file_path)

        if not text:
            raise ValueError("No text could be extracted from the document.")

        structured = extract_structured_data(
            document_type=document.document_type,
            claim_type=claim.claim_type,
            text=text,
        )

        document.extracted_text = text
        document.extracted_data = structured
        document.status = "EXTRACTED"
        document.processed_at = datetime.now(timezone.utc)

        document.processing_stage = None
        db.commit()

        document_graph.invoke({
            "document_id": document.id,
            "claim_id": claim.id
        })

    except Exception as e:
        document.status = "EXTRACTION_FAILED"
        document.error_message = str(e)
        document.processing_stage = None
        document.processed_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        # updating claim processing
        update_claim_processing_status(document.claim_id, db)
        db.close()