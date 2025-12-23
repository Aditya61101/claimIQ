from sqlalchemy.orm import Session
from app.models.claims import Claim
from app.models.documents import Document


def derive_processing_status(claim_id: int, db: Session) -> str:
    """
    Pure function:
    Determines the correct processing_status for a claim.
    """

    documents = (
        db.query(Document)
        .filter(Document.claim_id == claim_id)
        .all()
    )

    # Rule 1: No documents uploaded
    if not documents:
        return "PENDING"

    statuses = {doc.status for doc in documents}

    # Rule 2: Any failure blocks the claim
    if "FAILED" in statuses:
        return "ACTION_REQUIRED"

    # Rule 3: Still processing or just uploaded
    if "UPLOADED" in statuses or "PROCESSING" in statuses:
        return "PROCESSING"

    # Rule 4: Everything extracted successfully
    if statuses == {"EXTRACTED"}:
        return "READY_FOR_REVIEW"

    # Safety fallback
    return "PENDING"


def update_claim_processing_status(claim_id: int, db: Session) -> None:
    """
    Applies derived status to the claim if it has changed.
    """

    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        return

    new_status = derive_processing_status(claim_id, db)

    if claim.processing_status != new_status:
        claim.processing_status = new_status
        db.commit()