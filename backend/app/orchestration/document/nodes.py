from app.core.database import SessionLocal
from app.models.documents import Document
from app.agents.validation_agent.validation_agent import validate_document
from app.agents.internal_verification_agent.internal_verification_agent import verify_document

from .states import DocumentState

def document_validation_node(state:DocumentState) -> DocumentState:
    db = SessionLocal()

    try:
        document = db.get(Document, state['document_id'])
        
        if not document:
            return state
        
        document.processing_stage = "VALIDATION"
        db.commit()
        
        validate_document(document=document, db=db)

        db.refresh(document)
        state['document_status'] = document.status

        document.processing_stage = None
        db.commit()

        return state
    finally:
        db.close()

def document_verification_node(state:DocumentState) -> DocumentState:
    db = SessionLocal()

    try:
        document = db.get(Document, state['document_id'])
        
        if not document:
            return state
        
        document.processing_stage = "VERIFICATION"
        db.commit()
        
        verify_document(document=document, db=db)

        db.refresh(document)
        state['document_status'] = document.status

        document.processing_stage = None
        db.commit()

        return state
    finally:
        db.close()