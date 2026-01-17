from app.orchestration.document.document_graph import document_graph
from app.models.documents import Document
from app.services.claim_status import update_claim_processing_status
from app.core.database import SessionLocal

def invoke_document_graph(document_id:int, claim_id:int):
    db = SessionLocal()
    try:
        document:Document|None = db.query(Document).get(document_id)
        
        if not document:
            return

        # ---- Invoke document-level orchestration graph ----
        document_graph.invoke({
            "document_id": document.id,
            "claim_id": claim_id,
            "document_status": document.status
        })

        update_claim_processing_status(claim_id=claim_id, db=db)
    finally:
        db.close()