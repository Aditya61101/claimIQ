from app.extraction.regex_utils import extract
from app.utils.constants import ClaimTypes

def extract_bill_data(text:str, claim_type:str) -> dict:
    data = {
        "patient_name": extract(pattern=r"Patient Name:\s*(.+)", text=text),
        "total_bill_amount": extract(pattern=r"Bill amount:\s*(\d+)", text=text)
    }

    if claim_type == ClaimTypes.HOSPITALIZATION:
        data.update({
            "hospital_name": extract(pattern=r"Hospital:\s*(.+)", text=text),
            "admission_date": extract(pattern=r"Admission date:\s*([\d-]+)", text=text),
            "discharge_date": extract(pattern=r"Discharge date:\s*([\d-]+)", text=text)
        })

    elif claim_type == ClaimTypes.DOMICILIARY:
        data.update({
            "doctor_name": extract(pattern=r"Doctor:\s*(.+)", text=text),
            "treatment_date": extract(pattern=r"Treatment date:\s*([\d-]+)", text=text),
        })

    return data