# app/schemas/job.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Enums matching the models
JOB_CATEGORIES = [
    "electrician", "plumber", "cleaner", "carpenter", "painter",
    "ac_technician", "generator_technician", "personal_assistant",
    "chef_caterer", "security_guard", "driver", "event_planner",
    "it_support", "solar_installer", "healthcare_professional",
    "legal_consultant", "other"
]

JOB_TYPES = ["full_time", "part_time", "contract", "project_based", "temporary"]
EXPERIENCE_LEVELS = ["entry_level", "1_3_years", "3_5_years", "5_plus_years"]
SORT_OPTIONS = ["relevance", "rating", "reviews", "newest", "oldest"]

class JobCreate(BaseModel):
    title: str
    description: str
    category: str = Field(..., description=f"Must be one of: {', '.join(JOB_CATEGORIES)}")
    job_type: str = Field(..., description=f"Must be one of: {', '.join(JOB_TYPES)}")
    experience_level: str = Field(..., description=f"Must be one of: {', '.join(EXPERIENCE_LEVELS)}")
    
    location: str
    specific_address: Optional[str] = None
    
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "NGN"
    salary_period: str = "monthly"
    
    contact_name: str
    contact_email: EmailStr
    contact_phone: str
    show_contact: bool = True
    
    skills_required: Optional[List[str]] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    
    application_deadline: Optional[datetime] = None
    start_date: Optional[datetime] = None
    duration: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    employer_id: int
    employer_name: str
    employer_rating: Optional[float] = None
    
    title: str
    description: str
    category: str
    job_type: str
    experience_level: str
    
    location: str
    specific_address: Optional[str]
    
    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: str
    salary_period: str
    
    contact_name: str
    contact_email: EmailStr
    contact_phone: str
    show_contact: bool
    
    skills_required: List[str]
    responsibilities: Optional[str]
    benefits: Optional[str]
    
    status: str
    applications_count: int
    views_count: int
    save_count: int
    featured: bool
    
    average_rating: float
    review_count: int
    
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class JobSearchParams(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    sort_by: str = "relevance"  # relevance, rating, reviews, newest, oldest
    page: int = 1
    limit: int = 20