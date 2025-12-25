from typing import TypedDict, Optional

class DocumentState(TypedDict):
    document_id:int
    claim_id:int
    document_status:Optional[str]