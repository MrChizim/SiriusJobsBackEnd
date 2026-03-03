# app/models/user.py
from sqlalchemy import Column, String, Boolean, Enum, DateTime, Integer, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import BaseModel

class AccountType(str, enum.Enum):
    """User account types"""
    WORKER = "worker"
    EMPLOYER = "employer"
    PROFESSIONAL = "professional"
    MERCHANT = "merchant"
    ADMIN = "admin"

class User(BaseModel):
    __tablename__ = "users"
    
    # Core fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    
    # Status flags
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Profile fields
    profile_image_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(String(500), nullable=True)
    
    # Government ID fields
    govt_id_url = Column(String(500), nullable=True)
    govt_id_type = Column(String(50), nullable=True)
    id_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Guarantor fields
    guarantor_name = Column(String(255), nullable=True)
    guarantor_phone = Column(String(50), nullable=True)
    guarantor_email = Column(String(255), nullable=True)
    
    # Analytics fields
    profile_views = Column(Integer, default=0)
    
    # Subscription fields
    subscription_status = Column(String(50), default="inactive")
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Verification timestamps
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    phone_verified_at = Column(DateTime(timezone=True), nullable=True)
    identity_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # ========== RELATIONSHIPS ==========
    # Employer profile (one-to-one)
    employer_profile = relationship("EmployerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Jobs posted by employer
    jobs = relationship("Job", back_populates="employer", foreign_keys="Job.employer_id", cascade="all, delete-orphan")
    
    # Add this to the relationships section in User class
    merchant_profile = relationship("MerchantProfile", back_populates="user", uselist=False)

    # Applications submitted by worker
    applications = relationship("Application", back_populates="worker", foreign_keys="Application.worker_id", cascade="all, delete-orphan")
    
    # Ratings given and received
    ratings_given = relationship("Rating", foreign_keys="Rating.rater_id", back_populates="rater", cascade="all, delete-orphan")
    ratings_received = relationship("Rating", foreign_keys="Rating.rated_id", back_populates="rated", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email} ({self.account_type.value})>"