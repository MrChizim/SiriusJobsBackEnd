# app/models/application.py
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Application(BaseModel):
    __tablename__ = "applications"
    
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Application details
    cover_letter = Column(Text, nullable=True)
    expected_pay = Column(Float, nullable=True)
    proposed_timeline = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, reviewed, shortlisted, rejected, hired, withdrawn
    employer_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    worker = relationship("User", back_populates="applications")
    
    def __repr__(self):
        return f"<Application job={self.job_id} worker={self.worker_id} status={self.status}>"