from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email:EmailStr
    password:str

class CurrentUser(BaseModel):
    id:int
    email:EmailStr
    role:str

    class Config:
        from_attributes = True