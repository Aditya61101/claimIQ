from app.extraction.regex_utils import extract

def extract_prescription_data(text: str) -> dict:
    return {
        "patient_name": extract(r"Patient Name:\s*(.+)", text),
        "doctor_name": extract(r"Doctor:\s*(.+)", text),
        "diagnosis": extract(r"Diagnosis:\s*(.+)", text),
    }
