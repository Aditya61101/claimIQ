from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.documents import Document
from app.models.claims import Claim
from app.services.claim_status import update_claim_processing_status

from app.extraction.raw_unstructured.extract_router import extract_text
from app.extraction.structured.extract_router import extract_structured_data

from app.orchestration.document.document_graph import document_graph


def extract_document(document_id: int):
    """
    Background task:
    - Performs raw text extraction
    - Performs structured extraction
    - Updates document status deterministically
    - Triggers document-level LangGraph
    - Updates claim processing status safely
    """
    # Dependency injection lifecycle ends after response is sent
    # Session would be closed, so we make a new session.
    db = SessionLocal()
    try:
        # ---- Fetch document ----
        document: Document | None = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )
        if not document:
            return

        claim: Claim | None = db.query(Claim).get(document.claim_id)
        if not claim:
            return

        # ---- Mark extraction started (AUTHORITATIVE) ----
        document.status = "EXTRACTION_IN_PROGRESS"
        document.processing_stage = "EXTRACTION"
        db.commit()

        # ---- Raw text extraction (OCR / PDF / Image) ----
        text = extract_text(document.file_path)

        if not text or not text.strip():
            raise ValueError("No text could be extracted from the document.")

        # ---- Structured extraction (regex / rules) ----
        structured_data = extract_structured_data(
            document_type=document.document_type,
            claim_type=claim.claim_type,
            text=text,
        )

        # ---- Persist extraction result ----
        document.extracted_text = text
        document.extracted_data = structured_data
        document.status = "EXTRACTED"
        document.processing_stage = None
        document.processed_at = datetime.now(timezone.utc)

        db.commit()

        # ---- Invoke document-level orchestration graph ----
        document_graph.invoke({
            "document_id": document.id,
            "claim_id": claim.id,
            "document_status": document.status
        })

    except Exception as e:
        # ---- Extraction failure ----
        document.status = "EXTRACTION_FAILED"
        document.error_message = str(e)
        document.processing_stage = None
        document.processed_at = datetime.now(timezone.utc)

        db.commit()

    finally:
        # ---- Always re-derive claim processing status ----
        update_claim_processing_status(document.claim_id, db)
        db.close()