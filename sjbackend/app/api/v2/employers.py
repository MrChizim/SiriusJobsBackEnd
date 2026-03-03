# app/api/v2/employers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, error_response
from app.models.user import User, AccountType
from app.models.employer import EmployerProfile
from app.schemas.employer import EmployerProfileUpdate, EmployerProfileResponse

router = APIRouter(prefix="/employers", tags=["employers"])

@router.get("/profile")
async def get_employer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current employer's profile
    """
    if current_user.account_type != AccountType.EMPLOYER:
        return error_response("Not an employer account", status_code=403)
    
    # Get or create employer profile
    profile = db.query(EmployerProfile).filter(
        EmployerProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create default profile
        profile = EmployerProfile(
            user_id=current_user.id,
            company_name=current_user.name,
            verified=False
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return success_response(data={
        "user_id": profile.user_id,
        "company_name": profile.company_name,
        "company_website": profile.company_website,
        "company_size": profile.company_size,
        "industry": profile.industry,
        "company_description": profile.company_description,
        "logo_url": profile.logo_url,
        "verified": profile.verified,
        "location": current_user.location,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
    })

@router.put("/profile")
async def update_employer_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update employer profile
    """
    if current_user.account_type != AccountType.EMPLOYER:
        return error_response("Not an employer account", status_code=403)
    
    profile = db.query(EmployerProfile).filter(
        EmployerProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        profile = EmployerProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update fields
    if "company_name" in profile_data:
        profile.company_name = profile_data["company_name"]
    if "company_website" in profile_data:
        profile.company_website = profile_data["company_website"]
    if "company_size" in profile_data:
        profile.company_size = profile_data["company_size"]
    if "industry" in profile_data:
        profile.industry = profile_data["industry"]
    if "company_description" in profile_data:
        profile.company_description = profile_data["company_description"]
    if "logo_url" in profile_data:
        profile.logo_url = profile_data["logo_url"]
    if "location" in profile_data:
        current_user.location = profile_data["location"]
    
    db.commit()
    
    return success_response(
        message="Profile updated successfully",
        data={
            "company_name": profile.company_name,
            "company_website": profile.company_website,
            "company_size": profile.company_size,
            "industry": profile.industry,
            "company_description": profile.company_description,
            "logo_url": profile.logo_url,
            "location": current_user.location
        }
    )

@router.get("/jobs")
async def get_employer_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get jobs posted by current employer"""
    from app.models.job import Job
    
    jobs = db.query(Job).filter(Job.employer_id == current_user.id).all()
    
    jobs_data = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "title": job.title,
            "description": job.description[:100] + "..." if job.description and len(job.description) > 100 else job.description,
            "category": job.category,
            "location": job.location,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None
        }
        
        # Add optional fields only if they exist
        if hasattr(job, 'job_type'):
            job_dict["job_type"] = job.job_type
        if hasattr(job, 'experience_level'):
            job_dict["experience_level"] = job.experience_level
        if hasattr(job, 'budget_min'):
            job_dict["budget_min"] = job.budget_min
        if hasattr(job, 'budget_max'):
            job_dict["budget_max"] = job.budget_max
        if hasattr(job, 'applications_count'):
            job_dict["applications_count"] = job.applications_count
        
        jobs_data.append(job_dict)
    
    return success_response(data=jobs_data)