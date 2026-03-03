# app/services/stats_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User, AccountType
from app.models.job import Job
from app.models.rating import Rating
from app.models.analytics import PlatformStats
from datetime import datetime

def update_platform_stats(db: Session):
    """Update all platform statistics"""
    
    stats = db.query(PlatformStats).first()
    if not stats:
        stats = PlatformStats()
        db.add(stats)
    
    # Total users
    stats.total_users = db.query(User).filter(User.is_active == True).count()
    
    # Active workers (verified workers with complete profiles)
    stats.active_workers = db.query(User).filter(
        User.account_type == AccountType.WORKER,
        User.is_active == True,
        User.is_verified == True,
        User.profile_image_url.isnot(None),
        User.location.isnot(None)
    ).count()
    
    # Jobs completed
    stats.jobs_completed = db.query(Job).filter(Job.status == "completed").count()
    
    # Open jobs
    stats.open_jobs = db.query(Job).filter(Job.status == "open").count()
    
    # Average rating
    avg_rating = db.query(func.avg(Rating.rating)).scalar()
    stats.satisfaction_rate = round(float(avg_rating or 0) * 20, 1)  # Convert to percentage
    
    # Total reviews
    stats.total_reviews = db.query(Rating).count()
    
    stats.last_updated = datetime.utcnow()
    db.commit()
    
    return stats

def get_platform_stats(db: Session):
    """Get current platform statistics"""
    stats = db.query(PlatformStats).first()
    if not stats:
        stats = update_platform_stats(db)
    
    return {
        "total_users": stats.total_users,
        "active_workers": stats.active_workers,
        "jobs_completed": stats.jobs_completed,
        "open_jobs": stats.open_jobs,
        "satisfaction_rate": stats.satisfaction_rate,
        "total_reviews": stats.total_reviews,
        "last_updated": stats.last_updated.isoformat() if stats.last_updated else None
    }