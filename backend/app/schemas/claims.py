from pydantic import BaseModel
from datetime import datetime

from app.schemas.documents import DocumentResponse

class ClaimCreate(BaseModel):
    policy_id:str
    claim_type:str
    amount:float

class ClaimResponse(ClaimCreate):
    id:int
    status:str
    created_at:datetime
    # SQLAlchemy ORM objects are not JSON serializable.
    # When using Pydantic response models, from_attributes = True allows Pydantic to read data from object attributes instead of expecting a dict, enabling safe serialization of ORM objects.
    class Config:
        from_attributes = True


class ClaimWithDocumentsResponse(ClaimResponse):
    documents: list[DocumentResponse]

    class Config:
        from_attributes = True