# app/schemas/worker.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class WorkerProfileBase(BaseModel):
    """Base worker profile schema"""
    skills: List[str] = []
    experience: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    hourlyRate: Optional[float] = None

class WorkerProfileUpdate(BaseModel):
    """Schema for updating worker profile"""
    skills: Optional[List[str]] = None
    experience: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    hourlyRate: Optional[float] = None
    profileImageUrl: Optional[str] = None

class GuarantorInfo(BaseModel):
    """Guarantor information"""
    guarantorName: str
    guarantorPhone: str
    guarantorEmail: Optional[str] = None

class SubscriptionInfo(BaseModel):
    """Subscription information"""
    status: str  # active, inactive, expired
    endDate: Optional[datetime] = None

class WorkerResponse(BaseModel):
    """Schema for worker data in responses"""
    userId: int
    name: str
    email: str
    phone: Optional[str] = None
    skills: List[str]
    experience: Optional[str]
    location: Optional[str]
    profilePhoto: Optional[str]
    bio: Optional[str]
    isVerified: bool
    govtIdVerified: bool = False
    hasGuarantor: bool = False
    subscription: SubscriptionInfo
    profileViews: int = 0
    rating: Optional[float] = None
    completedJobs: int = 0
    
    class Config:
        from_attributes = True

class WorkerProfileResponse(WorkerResponse):
    """Extended worker profile for authenticated user"""
    email: str
    phone: Optional[str]
    govtIdType: Optional[str]
    guarantorName: Optional[str]
    guarantorPhone: Optional[str]
    guarantorEmail: Optional[str]
    applicationCount: int = 0