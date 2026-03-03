# app/models/rating.py
from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Rating(BaseModel):
    __tablename__ = "ratings"
    
    rater_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rated_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    rating = Column(Float, nullable=False)
    review = Column(Text, nullable=True)
    
    # Relationships
    rater = relationship("User", foreign_keys=[rater_id])
    rated = relationship("User", foreign_keys=[rated_id])
    job = relationship("Job", back_populates="ratings")