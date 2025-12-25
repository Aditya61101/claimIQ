from app.extraction.structured.contracts import (
    COMMON_BILL_FIELDS, HOSPITALIZATION_BILL_FIELDS, DOMICILIARY_BILL_FIELDS, PRESCRIPTION_FIELDS, REPORT_FIELDS
)
from app.utils.constants import DocumentTypes, ClaimTypes

def get_required_fields(document_type:str, claim_type:str) -> list[str]:
    
    if document_type == DocumentTypes.REPORTS:
        return REPORT_FIELDS
    
    if document_type == DocumentTypes.PRESCRIPTIONS:
        return PRESCRIPTION_FIELDS
    
    if claim_type == ClaimTypes.DOMICILIARY:
        return COMMON_BILL_FIELDS + DOMICILIARY_BILL_FIELDS
    
    if claim_type == ClaimTypes.HOSPITALIZATION:
        return COMMON_BILL_FIELDS + HOSPITALIZATION_BILL_FIELDS