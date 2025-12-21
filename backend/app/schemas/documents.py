from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    claim_id: int
    document_type: str
    file_name: str
    original_file_name: str
    file_path: str
    content_type: str
    uploaded_at: datetime
    source: str
    status: str

    class Config:
        from_attributes = True
