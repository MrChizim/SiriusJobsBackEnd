import os
import uuid
from fastapi import UploadFile, HTTPException
import cloudinary
import cloudinary.uploader
from app.core.config import settings

# Configure Cloudinary (you'll need to add these to .env)
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
ALLOWED_DOC_TYPES = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def upload_to_cloudinary(file: UploadFile, folder: str = "profiles"):
    """Upload file to Cloudinary"""
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1]
    public_id = f"{folder}/{uuid.uuid4()}"
    
    # Upload to Cloudinary
    result = cloudinary.uploader.upload(
        file.file,
        public_id=public_id,
        resource_type="auto"
    )
    
    return result["secure_url"]

async def upload_profile_photo(file: UploadFile, user_id: int):
    """Upload profile photo"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image type")
    
    return await upload_to_cloudinary(file, f"users/{user_id}/profile")

async def upload_govt_id(file: UploadFile, user_id: int, id_type: str):
    """Upload government ID"""
    if file.content_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(status_code=400, detail="Invalid document type")
    
    return await upload_to_cloudinary(file, f"users/{user_id}/ids/{id_type}")