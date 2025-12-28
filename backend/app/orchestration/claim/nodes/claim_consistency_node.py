from typing import List, Set
from app.orchestration.claim.state import ClaimGraphState, AgentIssue
from app.utils.constants import ClaimTypes


def claim_consistency_node(state: ClaimGraphState) -> ClaimGraphState:
    """
    Ensures consistency between:
    - claim form
    - insured person (ground truth)
    - extracted document data (verified docs only)

    Produces HIGH severity issues if claim story is incoherent.
    """

    issues: List[AgentIssue] = []

    claim = state["claim_data"]
    insured = state["insured_person"]
    documents = state["documents"]

    # --------------------------------------------------
    # 1. Patient name consistency
    # --------------------------------------------------
    insured_name = insured.get("full_name")

    doc_patient_names: Set[str] = {
        doc["extracted_data"].get("patient_name")
        for doc in documents
        if doc.get("extracted_data", {}).get("patient_name")
    }

    if len(doc_patient_names) > 1:
        issues.append({
            "code": "PATIENT_NAME_MISMATCH_ACROSS_DOCUMENTS",
            "message": "Patient name differs across submitted documents",
            "severity": "HIGH",
            "evidence": {
                "document_patient_names": list(doc_patient_names)
            }
        })

    if insured_name and doc_patient_names and insured_name not in doc_patient_names:
        issues.append({
            "code": "INSURED_PERSON_MISMATCH",
            "message": "Document patient name does not match insured person",
            "severity": "HIGH",
            "evidence": {
                "insured_person": insured_name,
                "document_patient_names": list(doc_patient_names)
            }
        })

    # --------------------------------------------------
    # 2. Diagnosis consistency
    # --------------------------------------------------
    claim_diagnosis = claim.get("diagnosis")

    doc_diagnoses: Set[str] = {
        doc["extracted_data"].get("diagnosis")
        for doc in documents
        if doc.get("extracted_data", {}).get("diagnosis")
    }

    if len(doc_diagnoses) > 1:
        issues.append({
            "code": "DIAGNOSIS_MISMATCH_ACROSS_DOCUMENTS",
            "message": "Diagnosis differs across submitted documents",
            "severity": "HIGH",
            "evidence": {
                "document_diagnoses": list(doc_diagnoses)
            }
        })

    if claim_diagnosis and doc_diagnoses and claim_diagnosis not in doc_diagnoses:
        issues.append({
            "code": "CLAIM_DIAGNOSIS_MISMATCH",
            "message": "Claim diagnosis does not match document diagnosis",
            "severity": "HIGH",
            "evidence": {
                "claim_diagnosis": claim_diagnosis,
                "document_diagnoses": list(doc_diagnoses)
            }
        })

    # --------------------------------------------------
    # 3. Claim amount vs bills
    # --------------------------------------------------
    claim_amount = claim.get("claim_amount", 0.0)

    bill_totals = [
        float(doc["extracted_data"].get("total_bill_amount", 0))
        for doc in documents
        if doc.get("document_type") == "bills"
    ]

    if bill_totals:
        total_billed = sum(bill_totals)

        if total_billed <= 0:
            issues.append({
                "code": "INVALID_BILL_AMOUNT",
                "message": "Total bill amount extracted is invalid",
                "severity": "HIGH",
                "evidence": {
                    "bill_amounts": bill_totals
                }
            })

        if total_billed > claim_amount:
            issues.append({
                "code": "CLAIM_AMOUNT_INCONSISTENT",
                "message": "Total bill amount exceeds claimed amount",
                "severity": "HIGH",
                "evidence": {
                    "claim_amount": claim_amount,
                    "total_billed": total_billed
                }
            })

    # --------------------------------------------------
    # 4. Claim type vs evidence consistency
    # --------------------------------------------------
    claim_type = claim.get("claim_type")

    if claim_type == ClaimTypes.HOSPITALIZATION:
        missing_dates = any(
            not doc["extracted_data"].get("admission_date") or
            not doc["extracted_data"].get("discharge_date")
            for doc in documents
            if doc.get("document_type") == "bills"
        )

        if missing_dates:
            issues.append({
                "code": "HOSPITALIZATION_DATES_MISSING",
                "message": "Hospitalization claim requires admission and discharge dates",
                "severity": "HIGH",
                "evidence": None
            })

    if claim_type == ClaimTypes.DOMICILIARY:
        missing_treatment = any(
            not doc["extracted_data"].get("treatment_date")
            for doc in documents
            if doc.get("document_type") == "bills"
        )

        if missing_treatment:
            issues.append({
                "code": "DOMICILIARY_TREATMENT_DATE_MISSING",
                "message": "Domiciliary claim requires treatment date in bill",
                "severity": "HIGH",
                "evidence": None
            })

    # --------------------------------------------------
    # Finalize state
    # --------------------------------------------------
    state["consistency_issues"] = issues or None
    return state