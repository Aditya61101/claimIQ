from pydantic import BaseModel

class GetHospitalResponse(BaseModel):
    id: int
    name:str
    city:str|None
    state:str|None

    class Config:
        from_attributes = True
