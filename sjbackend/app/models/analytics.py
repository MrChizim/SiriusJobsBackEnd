# app/models/analytics.py
from sqlalchemy import Column, Integer, Float, DateTime, String, JSON
from app.models.base import BaseModel

class PlatformStats(BaseModel):
    __tablename__ = "platform_stats"
    
    total_users = Column(Integer, default=0)
    active_workers = Column(Integer, default=0)
    jobs_completed = Column(Integer, default=0)
    open_jobs = Column(Integer, default=0)
    satisfaction_rate = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    last_updated = Column(DateTime, nullable=True)
    
class Rating(BaseModel):
    __tablename__ = "ratings"
    
    rater_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rated_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    rating = Column(Float, nullable=False)  # 1-5
    review = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)