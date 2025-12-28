from pydantic import BaseModel
from datetime import datetime, date
from typing import  Optional

class GetPoliciesResponse(BaseModel):
    id:int
    owner_user_id:int

    policy_number:str
    plan_id:int

    total_sum_insured:float
    approved_claim_amount: Optional[float]

    policy_start_date: Optional[date]
    policy_end_date: Optional[date]

    issued_at: Optional[datetime]

    class Config:
        from_attributes = True