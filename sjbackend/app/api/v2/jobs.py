# app/api/v2/jobs.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, error_response, paginated_response
from app.models.user import User, AccountType
from app.models.job import Job, JOB_CATEGORIES, JOB_TYPES, EXPERIENCE_LEVELS

router = APIRouter(prefix="/jobs", tags=["jobs"])

# ========== PUBLIC ENDPOINTS ==========

@router.get("/categories")
async def get_job_categories():
    """Get all available job categories"""
    return success_response(data=JOB_CATEGORIES)

@router.get("/types")
async def get_job_types():
    """Get all available job types"""
    return success_response(data=JOB_TYPES)

@router.get("/experience-levels")
async def get_experience_levels():
    """Get all available experience levels"""
    return success_response(data=EXPERIENCE_LEVELS)

@router.get("/search")
async def search_jobs(
    query: Optional[str] = Query(None, description="Search in title and description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level"),
    min_salary: Optional[float] = Query(None, description="Minimum salary"),
    max_salary: Optional[float] = Query(None, description="Maximum salary"),
    sort_by: str = Query("newest", description="Sort by: newest, oldest, salary_high, salary_low"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search jobs with advanced filtering"""
    
    # Base query for open jobs
    query_builder = db.query(Job).filter(Job.status == "open")
    
    # Text search
    if query:
        query_builder = query_builder.filter(
            or_(
                Job.title.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%")
            )
        )
    
    # Category filter
    if category:
        query_builder = query_builder.filter(Job.category == category)
    
    # Location filter
    if location:
        query_builder = query_builder.filter(Job.location.ilike(f"%{location}%"))
    
    # Job type filter
    if job_type:
        query_builder = query_builder.filter(Job.job_type == job_type)
    
    # Experience level filter
    if experience_level:
        query_builder = query_builder.filter(Job.experience_level == experience_level)
    
    # Salary range filter
    if min_salary:
        query_builder = query_builder.filter(Job.salary_max >= min_salary)
    if max_salary:
        query_builder = query_builder.filter(Job.salary_min <= max_salary)
    
    # Sorting
    if sort_by == "newest":
        query_builder = query_builder.order_by(desc(Job.created_at))
    elif sort_by == "oldest":
        query_builder = query_builder.order_by(Job.created_at)
    elif sort_by == "salary_high":
        query_builder = query_builder.order_by(desc(Job.salary_max))
    elif sort_by == "salary_low":
        query_builder = query_builder.order_by(Job.salary_min)
    
    total = query_builder.count()
    jobs = query_builder.offset((page - 1) * limit).limit(limit).all()
    
    jobs_data = []
    for job in jobs:
        employer = db.query(User).filter(User.id == job.employer_id).first()
        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
            "category": job.category,
            "job_type": job.job_type,
            "experience_level": job.experience_level,
            "location": job.location,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "salary_period": job.salary_period,
            "employer_id": job.employer_id,
            "employer_name": employer.name if employer else "Unknown",
            "applications_count": job.applications_count,
            "views_count": job.views_count,
            "created_at": job.created_at.isoformat() if job.created_at else None
        })
    
    return paginated_response(
        items=jobs_data,
        total=total,
        page=page,
        limit=limit,
        message="Jobs retrieved successfully"
    )

@router.get("")
async def get_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all jobs with basic filtering"""
    query = db.query(Job).filter(Job.status == "open")
    
    if category:
        query = query.filter(Job.category == category)
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    total = query.count()
    jobs = query.offset((page - 1) * limit).limit(limit).all()
    
    jobs_data = []
    for job in jobs:
        employer = db.query(User).filter(User.id == job.employer_id).first()
        jobs_data.append({
            "id": job.id,
            "title": job.title,
            "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
            "category": job.category,
            "location": job.location,
            "job_type": job.job_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "employer_name": employer.name if employer else "Unknown",
            "created_at": job.created_at.isoformat() if job.created_at else None
        })
    
    return paginated_response(items=jobs_data, total=total, page=page, limit=limit)

@router.get("/{job_id}")
async def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return error_response("Job not found", status_code=404)
    
    job.views_count = (job.views_count or 0) + 1
    db.commit()
    
    employer = db.query(User).filter(User.id == job.employer_id).first()
    
    return success_response(data={
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "category": job.category,
        "job_type": job.job_type,
        "experience_level": job.experience_level,
        "location": job.location,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency,
        "salary_period": job.salary_period,
        "contact_name": job.contact_name,
        "contact_email": job.contact_email,
        "contact_phone": job.contact_phone,
        "show_contact": job.show_contact,
        "employer": {
            "id": employer.id,
            "name": employer.name
        },
        "applications_count": job.applications_count,
        "views_count": job.views_count,
        "created_at": job.created_at.isoformat() if job.created_at else None
    })

# ========== PROTECTED ENDPOINTS ==========

@router.post("")
async def create_job(
    job_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting (employers only)"""
    if current_user.account_type != AccountType.EMPLOYER:
        return error_response("Only employers can post jobs", status_code=403)
    
    required_fields = ["title", "description", "category", "job_type", "experience_level", "location"]
    for field in required_fields:
        if field not in job_data:
            return error_response(f"Missing required field: {field}", status_code=400)
    
    job = Job(
        employer_id=current_user.id,
        title=job_data["title"],
        description=job_data["description"],
        category=job_data["category"],
        job_type=job_data.get("job_type", "full_time"),
        experience_level=job_data.get("experience_level", "entry_level"),
        location=job_data["location"],
        salary_min=job_data.get("salary_min"),
        salary_max=job_data.get("salary_max"),
        salary_currency=job_data.get("salary_currency", "NGN"),
        salary_period=job_data.get("salary_period", "monthly"),
        contact_name=job_data.get("contact_name", current_user.name),
        contact_email=job_data.get("contact_email", current_user.email),
        contact_phone=job_data.get("contact_phone", current_user.phone),
        status="open",
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return success_response(data={"id": job.id}, message="Job posted successfully", status_code=201)

@router.put("/{job_id}")
async def update_job(
    job_id: int,
    job_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a job posting"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return error_response("Job not found", status_code=404)
    
    if job.employer_id != current_user.id:
        return error_response("Not authorized", status_code=403)
    
    for field in ["title", "description", "category", "job_type", "experience_level", 
                  "location", "salary_min", "salary_max", "status"]:
        if field in job_data:
            setattr(job, field, job_data[field])
    
    db.commit()
    return success_response(message="Job updated successfully")

@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job posting"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return error_response("Job not found", status_code=404)
    
    if job.employer_id != current_user.id:
        return error_response("Not authorized", status_code=403)
    
    db.delete(job)
    db.commit()
    return success_response(message="Job deleted successfully")

@router.post("/{job_id}/close")
async def close_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close a job posting"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return error_response("Job not found", status_code=404)
    
    if job.employer_id != current_user.id:
        return error_response("Not authorized", status_code=403)
    
    job.status = "closed"
    db.commit()
    return success_response(message="Job closed successfully")