from .bill_extractor import extract_bill_data
from .prescription_extractor import extract_prescription_data
from .report_extractor import extract_report_data

from app.utils.constants import DocumentTypes

def extract_structured_data(
    document_type: str,
    claim_type: str,
    text: str
) -> dict:

    if document_type == DocumentTypes.BILLS:
        return extract_bill_data(text, claim_type)

    if document_type == DocumentTypes.PRESCRIPTIONS:
        return extract_prescription_data(text)

    if document_type == DocumentTypes.REPORTS:
        return extract_report_data(text)

    return {}
