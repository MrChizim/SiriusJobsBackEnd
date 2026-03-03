# app/schemas/employer.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class EmployerProfileBase(BaseModel):
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    company_description: Optional[str] = None
    location: Optional[str] = None
    logo_url: Optional[str] = None

class EmployerProfileCreate(EmployerProfileBase):
    pass

class EmployerProfileUpdate(EmployerProfileBase):
    pass

class EmployerProfileResponse(EmployerProfileBase):
    user_id: int
    verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True