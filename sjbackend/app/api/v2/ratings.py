# app/api/v2/ratings.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, error_response
from app.models.user import User, AccountType
from app.models.rating import Rating
from app.models.job import Job

router = APIRouter(prefix="/ratings", tags=["ratings"])

@router.post("/jobs/{job_id}")
async def rate_job(
    job_id: int,
    rating_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a job (after completion)"""
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return error_response("Job not found", status_code=404)
    
    # Check if user is authorized to rate
    if current_user.account_type not in [AccountType.EMPLOYER, AccountType.WORKER]:
        return error_response("Not authorized to rate", status_code=403)
    
    # Check if already rated
    existing = db.query(Rating).filter(
        Rating.job_id == job_id,
        Rating.rater_id == current_user.id
    ).first()
    
    if existing:
        return error_response("Already rated this job", status_code=400)
    
    # Determine who is being rated
    rated_id = job.employer_id if current_user.id != job.employer_id else None
    
    # Create rating
    rating = Rating(
        rater_id=current_user.id,
        rated_id=rated_id,
        job_id=job_id,
        rating=rating_data.get("rating", 5),
        review=rating_data.get("review", "")
    )
    
    db.add(rating)
    
    # Update job's average rating
    ratings = db.query(Rating).filter(Rating.job_id == job_id).all()
    if ratings:
        job.average_rating = sum(r.rating for r in ratings) / len(ratings)
        job.review_count = len(ratings)
    
    db.commit()
    
    return success_response(message="Rating submitted successfully")

@router.get("/job/{job_id}")
async def get_job_ratings(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get all ratings for a job"""
    ratings = db.query(Rating).filter(Rating.job_id == job_id).all()
    
    ratings_data = []
    for r in ratings:
        rater = db.query(User).filter(User.id == r.rater_id).first()
        ratings_data.append({
            "id": r.id,
            "rater_name": rater.name if rater else "Unknown",
            "rating": r.rating,
            "review": r.review,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    
    return success_response(data=ratings_data)