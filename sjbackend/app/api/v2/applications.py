# app/api/v2/applications.py
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import Body

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, error_response, paginated_response
from app.models.user import User, AccountType
from app.models.job import Job
from app.models.application import Application

router = APIRouter(prefix="/applications", tags=["applications"])

# ========== PYDANTIC MODELS ==========

class ApplicationCreate(BaseModel):
    """Schema for creating a job application"""
    job_id: int = Field(..., description="ID of the job to apply for")
    cover_letter: Optional[str] = Field(None, description="Cover letter or message to employer")
    expected_pay: Optional[float] = Field(None, description="Expected pay for the job")
    proposed_timeline: Optional[str] = Field(None, description="Proposed timeline for completion")

class ApplicationReject(BaseModel):
    """Schema for rejecting an application"""
    reason: Optional[str] = Field(None, description="Reason for rejection")

class ApplicationResponse(BaseModel):
    """Schema for application data in responses"""
    id: int
    job_id: int
    worker_id: int
    worker_name: Optional[str] = None
    job_title: Optional[str] = None
    status: str
    expected_pay: Optional[float] = None
    proposed_timeline: Optional[str] = None
    cover_letter: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class WorkerApplicationResponse(BaseModel):
    """Schema for worker's own applications"""
    id: int
    job_id: int
    job_title: Optional[str] = None
    status: str
    expected_pay: Optional[float] = None
    cover_letter_preview: Optional[str] = None
    created_at: Optional[str] = None

# ========== WORKER APPLICATION ENDPOINTS ==========
@router.post("", response_model=dict, status_code=201)
async def create_application(
    application_data: dict,  # Temporarily use dict for debugging
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply to a job"""
    if current_user.account_type != AccountType.WORKER:
        return error_response("Only workers can apply to jobs", status_code=403)
    
    job_id = application_data.get("job_id")
    if not job_id:
        return error_response("Missing job_id", status_code=400)
    
    # Check if job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return error_response("Job not found", status_code=404)
    
    # Create application
    from app.models.application import Application
    application = Application(
        job_id=job_id,
        worker_id=current_user.id,
        cover_letter=application_data.get("cover_letter"),
        expected_pay=application_data.get("expected_pay"),
        status="pending"
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return success_response(
        data={"application_id": application.id},
        message="Application submitted successfully",
        status_code=201
    )
    
@router.post("", response_model=dict, status_code=201)
async def apply_to_job(
    application_data: ApplicationCreate = Body(...),  # Now using Pydantic model
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply to a job (workers only)
    
    - **job_id**: ID of the job to apply for
    - **cover_letter**: Optional message to the employer
    - **expected_pay**: Optional expected payment
    - **proposed_timeline**: Optional timeline for completion
    """
    if current_user.account_type != AccountType.WORKER:
        return error_response("Only workers can apply to jobs", status_code=403)
    
    job_id = application_data.job_id
    
    # Check if job exists and is open
    job = db.query(Job).filter(Job.id == job_id, Job.status == "open").first()
    if not job:
        return error_response("Job not found or no longer open", status_code=404)
    
    # Check if already applied
    existing = db.query(Application).filter(
        Application.job_id == job_id,
        Application.worker_id == current_user.id
    ).first()
    
    if existing:
        return error_response("You have already applied to this job", status_code=400)
    
    # Create application
    application = Application(
        job_id=job_id,
        worker_id=current_user.id,
        cover_letter=application_data.cover_letter,
        expected_pay=application_data.expected_pay,
        proposed_timeline=application_data.proposed_timeline,
        status="pending"
    )
    
    db.add(application)
    
    # Increment applications count on job
    job.applications_count = (job.applications_count or 0) + 1
    
    db.commit()
    db.refresh(application)
    
    return success_response(
        data={"application_id": application.id},
        message="Application submitted successfully",
        status_code=201
    )

@router.get("/my-applications", response_model=dict)
async def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all applications by current worker
    """
    if current_user.account_type != AccountType.WORKER:
        return error_response("Only workers can view their applications", status_code=403)
    
    applications = db.query(Application).filter(
        Application.worker_id == current_user.id
    ).order_by(Application.created_at.desc()).all()
    
    apps_data = []
    for app in applications:
        # Fixed: Added missing closing parenthesis
        job = db.query(Job).filter(Job.id == app.job_id).first()
        job_title = job.title if job else "unknown job"
        cover_letter_preview = app.cover_letter[:100] + "..." if app.cover_letter and len(app.cover_letter) > 100 else app.cover_letter
        
        apps_data.append(WorkerApplicationResponse(
            id=app.id,
            job_id=app.job_id,
            job_title=job_title,
            status=app.status,
            expected_pay=app.expected_pay,
            cover_letter_preview=cover_letter_preview,
            created_at=app.created_at.isoformat() if app.created_at else None
        ))
    
    return success_response(data=apps_data)
# ========== EMPLOYER APPLICATION MANAGEMENT ENDPOINTS ==========

@router.get("/job/{job_id}", response_model=dict)
async def get_job_applications(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all applications for a specific job (employers only)
    """
    # Check if job exists and belongs to current user
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        return error_response("Job not found", status_code=404)
    
    if job.employer_id != current_user.id:
        return error_response("Not authorized to view these applications", status_code=403)
    
    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).order_by(Application.created_at.desc()).all()
    
    apps_data = []
    for app in applications:
        worker = db.query(User).filter(User.id == app.worker_id).first()
        apps_data.append(ApplicationResponse(
            id=app.id,
            job_id=app.job_id,
            worker_id=app.worker_id,
            worker_name=worker.name if worker else "Unknown",
            job_title=job.title,
            status=app.status,
            expected_pay=app.expected_pay,
            proposed_timeline=app.proposed_timeline,
            cover_letter=app.cover_letter,
            created_at=app.created_at.isoformat() if app.created_at else None
        ))
    
    return success_response(data=apps_data)

@router.put("/{application_id}/shortlist", response_model=dict)
async def shortlist_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Shortlist an applicant (employers only)
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        return error_response("Application not found", status_code=404)
    
    # Check job ownership
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if job.employer_id != current_user.id:
        return error_response("Not authorized", status_code=403)
    
    application.status = "shortlisted"
    db.commit()
    
    return success_response(message="Applicant shortlisted successfully")

@router.put("/{application_id}/reject", response_model=dict)
async def reject_application(
    application_id: int,
    reject_data: ApplicationReject,  # Using Pydantic model
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject an applicant (employers only)
    
    - **reason**: Optional reason for rejection
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        return error_response("Application not found", status_code=404)
    
    # Check job ownership
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if job.employer_id != current_user.id:
        return error_response("Not authorized", status_code=403)
    
    application.status = "rejected"
    application.rejection_reason = reject_data.reason
    db.commit()
    
    return success_response(message="Applicant rejected")

@router.put("/{application_id}/hire", response_model=dict)
async def hire_applicant(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hire an applicant (employers only)
    """
    application = db.query(Application).filter(Application.id == application_id).first()
    
    if not application:
        return error_response("Application not found", status_code=404)
    
    # Check job ownership
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if job.employer_id != current_user.id:
        return error_response("Not authorized", status_code=403)
    
    # Update application status
    application.status = "hired"
    
    # Update job status to filled
    job.status = "filled"
    
    db.commit()
    
    return success_response(message="Applicant hired successfully")