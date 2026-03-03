# app/models/employer.py
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class EmployerProfile(BaseModel):
    __tablename__ = "employer_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=True)
    company_website = Column(String(255), nullable=True)
    company_size = Column(String(50), nullable=True)
    industry = Column(String(100), nullable=True)
    verified = Column(Boolean, default=False)
    verification_doc_url = Column(String(500), nullable=True)
    company_description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="employer_profile")
    
    def __repr__(self):
        return f"<EmployerProfile user_id={self.user_id} company={self.company_name}>"