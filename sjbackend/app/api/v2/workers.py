from fastapi import APIRouter, Depends, Query, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, error_response, paginated_response
from app.models.user import User, AccountType

router = APIRouter(prefix="/workers", tags=["workers"])

# ========== PUBLIC ENDPOINTS ==========
@router.get("")
async def get_workers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    location: Optional[str] = Query(None, description="Location filter"),
    db: Session = Depends(get_db)
):
    """
    Get all workers with pagination and filtering
    """
    # Base query for active workers
    query = db.query(User).filter(
        User.account_type == AccountType.WORKER,
        User.is_active == True
    )
    
    # Apply location filter
    if location:
        query = query.filter(User.location.ilike(f"%{location}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    workers = query.offset((page - 1) * limit).limit(limit).all()
    
    # Format response with all fields
    workers_data = []
    for worker in workers:
        # Parse skills from comma-separated string
        skills_list = worker.skills.split(",") if worker.skills else []
        
        workers_data.append({
            "userId": worker.id,
            "name": worker.name,
            "skills": skills_list,
            "experience": worker.bio,
            "location": worker.location,
            "profilePhoto": worker.profile_image_url,
            "bio": worker.bio or "",
            "isVerified": worker.is_verified,
            "govtIdVerified": worker.govt_id_url is not None,
            "hasGuarantor": worker.guarantor_name is not None,
            "subscription": {
                "status": worker.subscription_status or "inactive",
                "endDate": worker.subscription_end_date.isoformat() if worker.subscription_end_date else None
            },
            "profileViews": worker.profile_views or 0,
            "rating": None,
            "completedJobs": 0
        })
    
    return paginated_response(
        items=workers_data,
        total=total,
        page=page,
        limit=limit,
        message="Workers retrieved successfully"
    )

# ========== PROTECTED ENDPOINTS (NO PARAMETERS - MUST COME BEFORE PARAMETERIZED ROUTES) ==========
@router.get("/profile")
async def get_worker_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current worker's complete profile (authenticated endpoint)
    """
    if current_user.account_type != AccountType.WORKER:
        return error_response(
            "Not a worker account",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    # Parse skills
    skills_list = current_user.skills.split(",") if current_user.skills else []
    
    profile = {
        "userId": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "skills": skills_list,
        "experience": current_user.bio,
        "location": current_user.location,
        "profilePhoto": current_user.profile_image_url,
        "bio": current_user.bio or "",
        "isVerified": current_user.is_verified,
        "govtIdVerified": current_user.govt_id_url is not None,
        "govtIdType": current_user.govt_id_type,
        "guarantorName": current_user.guarantor_name,
        "guarantorPhone": current_user.guarantor_phone,
        "guarantorEmail": current_user.guarantor_email,
        "subscription": {
            "status": current_user.subscription_status or "inactive",
            "endDate": current_user.subscription_end_date.isoformat() if current_user.subscription_end_date else None
        },
        "profileViews": current_user.profile_views or 0,
        "applicationCount": 0,
        "rating": None,
        "completedJobs": 0
    }
    
    return success_response(
        data=profile,
        message="Profile retrieved successfully"
    )

@router.put("/profile")
async def update_worker_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update worker profile (location, bio, skills, profile photo)
    """
    if current_user.account_type != AccountType.WORKER:
        return error_response(
            "Not a worker account",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    # Update fields if provided
    if "location" in profile_data:
        current_user.location = profile_data["location"]
    
    if "bio" in profile_data:
        current_user.bio = profile_data["bio"]
    
    if "profileImageUrl" in profile_data:
        current_user.profile_image_url = profile_data["profileImageUrl"]
    
    if "skills" in profile_data and isinstance(profile_data["skills"], list):
        # Store skills as comma-separated string
        current_user.skills = ",".join(profile_data["skills"])
    
    db.commit()
    db.refresh(current_user)
    
    # Parse skills back to list
    skills_list = current_user.skills.split(",") if current_user.skills else []
    
    return success_response(
        data={
            "userId": current_user.id,
            "name": current_user.name,
            "location": current_user.location,
            "profilePhoto": current_user.profile_image_url,
            "bio": current_user.bio or "",
            "skills": skills_list
        },
        message="Profile updated successfully"
    )

@router.post("/guarantor")
async def add_guarantor(
    guarantor_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add guarantor information
    """
    if current_user.account_type != AccountType.WORKER:
        return error_response("Not a worker account", status_code=403)
    
    # Update guarantor fields
    if "guarantorName" in guarantor_data:
        current_user.guarantor_name = guarantor_data["guarantorName"]
    if "guarantorPhone" in guarantor_data:
        current_user.guarantor_phone = guarantor_data["guarantorPhone"]
    if "guarantorEmail" in guarantor_data:
        current_user.guarantor_email = guarantor_data["guarantorEmail"]
    
    db.commit()
    
    return success_response(
        message="Guarantor information added successfully"
    )

@router.get("/can-appear-publicly")
async def check_public_visibility(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if worker can appear in public listings
    """
    if current_user.account_type != AccountType.WORKER:
        return error_response("Not a worker account", status_code=403)
    
    can_appear = (
        current_user.is_verified and
        current_user.profile_image_url is not None and
        current_user.location is not None and
        current_user.bio is not None and
        current_user.skills is not None
    )
    
    return success_response(data={
        "canAppearPublicly": can_appear,
        "hasActiveSubscription": current_user.subscription_status == "active",
        "hasGovernmentId": current_user.govt_id_url is not None,
        "hasGuarantor": current_user.guarantor_name is not None
    })

@router.get("/analytics")
async def get_worker_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get worker analytics (profile views, applications, hires)
    """
    if current_user.account_type != AccountType.WORKER:
        return error_response("Not a worker account", status_code=403)
    
    return success_response(data={
        "profileViews": current_user.profile_views or 0,
        "jobApplications": 0,
        "hiresReceived": 0,
        "lastUpdated": str(datetime.utcnow())
    })

@router.post("/upload-photo")
async def upload_worker_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload worker profile photo
    """
    if current_user.account_type != AccountType.WORKER:
        return error_response("Not a worker account", status_code=403)
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        return error_response("Only image files are allowed", status_code=400)
    
    try:
        # Placeholder for file upload
        file_url = f"/uploads/{current_user.id}/profile_{datetime.utcnow().timestamp()}.jpg"
        
        # Save the URL to the user's profile
        current_user.profile_image_url = file_url
        db.commit()
        
        return success_response(
            data={"photoUrl": file_url},
            message="Profile photo uploaded successfully"
        )
    except Exception as e:
        return error_response(f"Upload failed: {str(e)}", status_code=400)

@router.post("/upload-id")
async def upload_worker_id(
    file: UploadFile = File(...),
    id_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload government ID for verification
    """
    if current_user.account_type != AccountType.WORKER:
        return error_response("Not a worker account", status_code=403)
    
    # Validate ID type
    valid_id_types = ["nin", "voters_card", "drivers_license", "international_passport"]
    if id_type not in valid_id_types:
        return error_response(f"Invalid ID type. Must be one of: {', '.join(valid_id_types)}", status_code=400)
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        return error_response("File must be an image or PDF", status_code=400)
    
    try:
        # Placeholder for file upload
        file_url = f"/uploads/{current_user.id}/ids/{id_type}_{datetime.utcnow().timestamp()}.pdf"
        
        current_user.govt_id_url = file_url
        current_user.govt_id_type = id_type
        db.commit()
        
        return success_response(
            data={"documentUrl": file_url, "type": id_type},
            message="ID uploaded successfully"
        )
    except Exception as e:
        return error_response(f"Upload failed: {str(e)}", status_code=400)

# ========== PARAMETERIZED ROUTES (MUST COME LAST) ==========
@router.get("/{worker_id}")
async def get_worker_by_id(
    worker_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific worker by ID (public endpoint)
    """
    worker = db.query(User).filter(
        User.id == worker_id,
        User.account_type == AccountType.WORKER,
        User.is_active == True
    ).first()
    
    if not worker:
        return error_response(
            "Worker not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Parse skills
    skills_list = worker.skills.split(",") if worker.skills else []
    
    response = {
        "userId": worker.id,
        "name": worker.name,
        "skills": skills_list,
        "experience": worker.bio,
        "location": worker.location,
        "profilePhoto": worker.profile_image_url,
        "bio": worker.bio or "",
        "isVerified": worker.is_verified,
        "govtIdVerified": worker.govt_id_url is not None,
        "hasGuarantor": worker.guarantor_name is not None,
        "subscription": {
            "status": worker.subscription_status or "inactive",
            "endDate": worker.subscription_end_date.isoformat() if worker.subscription_end_date else None
        },
        "profileViews": worker.profile_views or 0,
        "rating": None,
        "completedJobs": 0
    }
    
    # Track profile view (increment counter)
    worker.profile_views = (worker.profile_views or 0) + 1
    db.commit()
    
    return success_response(
        data=response,
        message="Worker retrieved successfully"
    )

@router.post("/track-view/{worker_id}")
async def track_profile_view(
    worker_id: int,
    db: Session = Depends(get_db)
):
    """
    Track when someone views a worker's profile (public endpoint)
    """
    worker = db.query(User).filter(
        User.id == worker_id,
        User.account_type == AccountType.WORKER
    ).first()
    
    if not worker:
        return error_response("Worker not found", status_code=404)
    
    worker.profile_views = (worker.profile_views or 0) + 1
    db.commit()
    
    return success_response(message="Profile view tracked")