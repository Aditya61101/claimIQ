from datetime import datetime
from app.models.documents import Document

def verify_bill(data: dict, document: Document):
    total = data.get("total_bill_amount")
    patient = data.get("patient_name")

    if not patient or not patient.strip():
        raise ValueError("Patient name missing or invalid")

    if total is None or float(total) <= 0:
        raise ValueError("Total bill amount must be greater than zero")

    # Hospitalization bill
    if document.claim_type == "hospitalization":
        admission = data.get("admission_date")
        discharge = data.get("discharge_date")

        _validate_date(admission)
        _validate_date(discharge)

        if _parse_date(admission) > _parse_date(discharge):
            raise ValueError("Admission date cannot be after discharge date")

    # Domiciliary bill
    else:
        treatment = data.get("treatment_date")
        _validate_date(treatment)


def verify_report(data: dict):
    patient = data.get("patient_name")
    diagnosis = data.get("diagnosis")
    report_date = data.get("report_date")

    if not patient or not patient.strip():
        raise ValueError("Patient name missing")

    if not diagnosis or not diagnosis.strip():
        raise ValueError("Diagnosis missing")

    _validate_date(report_date)

    if _parse_date(report_date) > datetime.utcnow():
        raise ValueError("Report date cannot be in the future")


def verify_prescription(data: dict):
    patient = data.get("patient_name")
    doctor = data.get("doctor_name")
    diagnosis = data.get("diagnosis")

    if not patient or not patient.strip():
        raise ValueError("Patient name missing")

    if not doctor or not doctor.strip():
        raise ValueError("Doctor name missing")

    if not diagnosis or not diagnosis.strip():
        raise ValueError("Diagnosis missing")


def _validate_date(value: str):
    if not value:
        raise ValueError("Date missing")
    _parse_date(value)


def _parse_date(value: str):
    try:
        return datetime.fromisoformat(value)
    except Exception:
        raise ValueError(f"Invalid date format: {value}")
