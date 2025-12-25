from app.extraction.regex_utils import extract

def extract_report_data(text: str) -> dict:
    return {
        "patient_name": extract(r"Patient Name:\s*(.+)", text),
        "diagnosis": extract(r"Diagnosis:\s*(.+)", text),
        "report_date": extract(r"Report Date:\s*([\d-]+)", text),
    }
