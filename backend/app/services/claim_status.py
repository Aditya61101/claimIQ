from sqlalchemy.orm import Session
from app.models.claims import Claim
from app.models.documents import Document

from app.orchestration.claim.claim_executor import invoke_claim_graph

BLOCKING_STATUS = {
    "EXTRACTION_FAILED",
    "VALIDATION_FAILED",
    "VERIFICATION_FAILED"
}

def build_action_required_payload(documents:list[Document]):
    blocking = []

    for doc in documents:
        if doc.status in BLOCKING_STATUS:
            blocking.append({
                "document_id": doc.id,
                "document_name": doc.original_file_name,
                "document_type": doc.document_type,
                "status": doc.status,
                "message": doc.error_message or "Document requires attention."
            })

    return {
        "summary": "Some documents require attention before processing can continue.",
        "blocking_documents": blocking,
        "next_steps": [
            "Re-upload the highlighted documents",
            "Ensure all required details are visible and correct"
        ]
    }

def derive_processing_status(claim:Claim, db: Session) -> str:
    """
    Pure function:
    Determines the correct processing_status for a claim.
    """

    documents = (
        db.query(Document)
        .filter(Document.claim_id == claim.id)
        .all()
    )

    # No documents uploaded
    if not documents:
        return "DRAFT", None

    statuses = {doc.status for doc in documents}

    # Any failure blocks the claim
    if statuses & BLOCKING_STATUS:
        return "ACTION_REQUIRED", build_action_required_payload(documents)

    # Every document verified successfully, so we moved to claim level agents
    if statuses == {"VERIFIED"}:
        return "READY_FOR_EVALUATION", None

    # Still processing
    return "DOCUMENT_PROCESSING", None

def update_claim_processing_status(claim_id: int, db: Session) -> None:
    """
    Applies derived processing_status and action_required to the claim.
    """

    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        return

    new_status, action_required = derive_processing_status(claim, db)

    if claim.processing_status != new_status or claim.action_required != action_required:
        claim.processing_status = new_status
        claim.action_required = action_required
        db.commit()

    # claim graph is invoked here
    if new_status == 'READY_FOR_EVALUATION':
        invoke_claim_graph(claim.id)