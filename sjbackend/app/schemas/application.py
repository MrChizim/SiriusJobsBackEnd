# app/schemas/application.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApplicationBase(BaseModel):
    cover_letter: Optional[str] = None
    expected_pay: Optional[float] = None
    proposed_timeline: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    job_id: int

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    employer_notes: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    id: int
    job_id: int
    worker_id: int
    worker_name: str
    job_title: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True