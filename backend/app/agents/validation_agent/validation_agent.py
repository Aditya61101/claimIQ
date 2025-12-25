from datetime import datetime, timezone
from sqlalchemy.orm import Session
# models
from app.models.documents import Document
from app.models.claims import Claim
# agent utilities
from app.agents.validation_agent.utils.requirements import get_required_fields
from app.agents.validation_agent.utils.helper import find_missing_fields
from app.agents.validation_agent.utils.llm_filler import llm_fill_missing_fields
# services
from app.services.claim_status import update_claim_processing_status


def validate_document(document:Document, db:Session):
    claim = db.query(Claim).get(document.claim_id)
    if not claim:
        return
    
    required_fields = get_required_fields(
        document_type=document.document_type,
        claim_type=claim.claim_type
    )

    extracted = document.extracted_data or {}

    missing = find_missing_fields(required=required_fields, extracted=extracted)

    if missing:
        # do LLM call to extract missing required fields
        llm_data = llm_fill_missing_fields(
            text=document.extracted_text,
            missing_fields=missing,
            document_type=document.document_type,
            claim_type=claim.claim_type
        )

        for key in missing:
            if llm_data.get(key):
                extracted[key]=llm_data[key]
        
        document.extracted = extracted
        db.commit()

    # final validation
    final_missing = find_missing_fields(required=required_fields, extracted=document.extracted_data)

    if final_missing:
        document.status="VALIDATION_FAILED"
        document.error_message = ("Missing required fields: "+ ", ".join(final_missing))

    document.processed_at = datetime.now(timezone.utc)
    db.commit()

    update_claim_processing_status(claim_id=document.claim_id, db=db)