from app.models.documents import Document
from app.agents.internal_verification_agent.utils.helpers import verify_bill, verify_prescription, verify_report
from app.utils.constants import DocumentTypes

def verify_document(document: Document, db):
    """
    Verifies internal consistency of a single document.
    Sets VERIFIED or VERIFICATION_FAILED.
    """

    data = document.extracted_data or {}

    try:
        if document.document_type == DocumentTypes.BILLS:
            verify_bill(data)

        elif document.document_type == DocumentTypes.REPORTS:
            verify_report(data)

        elif document.document_type == DocumentTypes.PRESCRIPTIONS:
            verify_prescription(data)

        else:
            raise ValueError("Unsupported document type")

        # If no exception → verified
        document.status = "VERIFIED"
        document.error_message = None

    except Exception as e:
        document.status = "VERIFICATION_FAILED"
        document.error_message = str(e)

    db.commit()