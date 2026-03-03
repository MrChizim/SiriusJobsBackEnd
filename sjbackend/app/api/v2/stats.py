# app/api/v2/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.response import success_response
from app.models.user import User, AccountType
from app.models.job import Job
from app.models.rating import Rating

router = APIRouter(prefix="/stats", tags=["statistics"])

@router.get("/platform")
async def get_platform_statistics(db: Session = Depends(get_db)):
    """Get real-time platform statistics"""
    
    # Total users
    total_users = db.query(User).filter(User.is_active == True).count()
    
    # Active workers (verified workers with profiles)
    active_workers = db.query(User).filter(
        User.account_type == AccountType.WORKER,
        User.is_active == True,
        User.is_verified == True,
        User.profile_image_url.isnot(None),
        User.location.isnot(None)
    ).count()
    
    # Jobs completed
    jobs_completed = db.query(Job).filter(Job.status == "completed").count()
    
    # Open jobs
    open_jobs = db.query(Job).filter(Job.status == "open").count()
    
    # Average rating
    from sqlalchemy import func
    avg_rating = db.query(func.avg(Rating.rating)).scalar()
    satisfaction_rate = round(float(avg_rating or 0) * 20, 1)
    
    # Total reviews
    total_reviews = db.query(Rating).count()
    
    return success_response(data={
        "total_users": total_users,
        "active_workers": active_workers,
        "jobs_completed": jobs_completed,
        "open_jobs": open_jobs,
        "satisfaction_rate": satisfaction_rate,
        "total_reviews": total_reviews,
        "last_updated": datetime.utcnow().isoformat()
    })