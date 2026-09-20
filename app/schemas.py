from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    applied = "applied"
    interviewing = "interviewing"
    offered = "offered"
    rejected = "rejected"



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
    date:  Optional[datetime] = None
    applied_through_email: bool

class ApplicationResponse(BaseModel):
    application_id: int
    company_name: str
    role: str
    status: str
    applied_through_email: bool
    date: Optional[datetime] = None
    class Config:
        from_attributes= True

class ApplicationUpdate(BaseModel):
    status: StatusEnum
