from pydantic import BaseModel
from datetime import datetime, date

class InsuredPersonResponse(BaseModel):
    id:int
    policy_id:int

    full_name:str
    date_of_birth:date
    gender:str