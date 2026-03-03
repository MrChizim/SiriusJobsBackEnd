# app/models/job.py
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

# Job Categories Enum
JOB_CATEGORIES = [
    "electrician", "plumber", "cleaner", "carpenter", "painter",
    "ac_technician", "generator_technician", "personal_assistant",
    "chef_caterer", "security_guard", "driver", "event_planner",
    "it_support", "solar_installer", "healthcare_professional",
    "legal_consultant", "other"
]

# Job Types Enum
JOB_TYPES = ["full_time", "part_time", "contract", "project_based", "temporary"]

# Experience Levels
EXPERIENCE_LEVELS = ["entry_level", "1_3_years", "3_5_years", "5_plus_years"]

class Job(BaseModel):
    __tablename__ = "jobs"
    
    # Basic Info
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # From JOB_CATEGORIES
    job_type = Column(String(50), nullable=False)  # From JOB_TYPES
    experience_level = Column(String(50), nullable=False)  # From EXPERIENCE_LEVELS
    
    # Location
    location = Column(String(255), nullable=False)
    specific_address = Column(String(500), nullable=True)
    
    # Salary/Rate
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), default="NGN")
    salary_period = Column(String(20), default="monthly")  # hourly, daily, weekly, monthly, yearly
    
    # Contact Info
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    show_contact = Column(Boolean, default=True)
    
    # Requirements
    skills_required = Column(JSON, nullable=True)  # Store as JSON array
    responsibilities = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    
    # Schedule/Deadline
    application_deadline = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    duration = Column(String(100), nullable=True)
    
    # Status & Analytics
    status = Column(String(50), default="open")  # open, filled, closed, expired
    applications_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    save_count = Column(Integer, default=0)
    featured = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Ratings & Reviews
    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # Relationships
    employer = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="job", cascade="all, delete-orphan")