from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    class Config:
        from_attributes= True

class UserLogin(BaseModel):
    email: str
    password: str

class ApplicationCreate(BaseModel):
    company_name: str
    role: str
    status: str
    date: datetime
    applied_through_email: bool

class ApplicationResponse(BaseModel):
    application_id: int
    company_name: str
    role: str
    status: str
    applied_through_email: bool
    class Config:
        from_attributes= True

class ApplicationUpdate(BaseModel):
    status: str
