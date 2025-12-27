from pydantic import BaseModel, Field, model_validator
from datetime import datetime, date
from typing import Literal, Optional
from app.utils.constants import ClaimTypes
from app.schemas.documents import DocumentResponse

class InsuredPersonInput(BaseModel):
    full_name:str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None

class ClaimCreate(BaseModel):
    policy_id:int = Field(..., description="Primary key of policy table")
    insured_person_id:int = Field(..., description="selected insured person under the policy")
    # insured_person: InsuredPersonInput
    claim_type: Literal['hospitalization', 'domiciliary']
    diagnosis: str
    
    claim_amount:float = Field(..., gt=0)

    # for domiciliary
    treatment_date: Optional[date] = None
    # for hospitalization
    hospital_id: Optional[int] = Field(None, description="Required for hospitalization claims")
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None

    @model_validator(mode='after')
    def validate_date(self):
        if self.claim_type == ClaimTypes.DOMICILIARY:
            if not self.treatment_date:
                raise ValueError("Treatment date is required for domiciliary claims")
        elif self.claim_type == ClaimTypes.HOSPITALIZATION:
            if not self.hospital_id:
                raise ValueError("hospital id is required for hospitalization claims")
            if not self.admission_date or not self.discharge_date:
                raise ValueError("Admission date and Discharge date are required for hospitalization claims")
        return self


class ClaimResponse(ClaimCreate):
    id:int
    processing_status:str
    decision_status:str
    created_at:datetime
    # SQLAlchemy ORM objects are not JSON serializable.
    # When using Pydantic response models, from_attributes = True allows Pydantic to read data from object attributes instead of expecting a dict, enabling safe serialization of ORM objects.
    class Config:
        from_attributes = True


class ClaimWithDocumentsResponse(ClaimResponse):
    documents: list[DocumentResponse]

    class Config:
        from_attributes = True