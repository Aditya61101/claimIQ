from app.orchestration.states import DocumentState

def document_router(state:DocumentState):
    """
    Running logic after validation
    """
    
    status = state.get("document_status")

    if status in ("EXTRACTION_FAILED", "VALIDATION_FAILED", "VERIFICATION_FAILED"):
        return "end"
    
    return "verify"