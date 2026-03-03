# app/api/v2/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token,
    verify_token, get_current_user
)
from app.core.response import success_response, error_response
from app.models.user import User, AccountType
from app.schemas.auth import (
    UserCreate, UserLogin, RefreshTokenRequest,
    AuthResponse, UserResponse, TokenResponse
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if user exists by email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        return error_response(
            "Email already registered",
            status_code=status.HTTP_409_CONFLICT
        )
    
    # Check if phone exists
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        return error_response(
            "Phone number already registered",
            status_code=status.HTTP_409_CONFLICT
        )
    
    # Create new user with location and profile image
    user = User(
        email=user_data.email,
        name=user_data.name,
        phone=user_data.phone,
        location=user_data.location,  # Save location
        profile_image_url=user_data.profileImageUrl,  # Save profile image URL
        password_hash=get_password_hash(user_data.password),
        account_type=AccountType(user_data.accountType),
        is_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Build user response
    user_response = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "accountType": user.account_type.value if hasattr(user.account_type, 'value') else user.account_type,
        "isVerified": user.is_verified,
        "profileImageUrl": user.profile_image_url,
        "location": user.location,
        "phone": user.phone
    }
    
    return success_response(
        data={
            "user": user_response,
            "accessToken": access_token,
            "refreshToken": refresh_token
        },
        message="Registration successful",
        status_code=status.HTTP_201_CREATED
    )
    
    # Check if user is active
    if not user.is_active:
        return error_response(
            "Account is inactive",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Build user response manually as a dictionary (NOT a Pydantic model)
    user_response = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "accountType": user.account_type.value if hasattr(user.account_type, 'value') else user.account_type,
        "isVerified": user.is_verified,
        "profileImageUrl": user.profile_image_url,
        "location": user.location,
        "phone": user.phone
    }
    
    return success_response(
        data={
            "user": user_response,  # This is a dict, not a Pydantic model
            "accessToken": access_token,
            "refreshToken": refresh_token
        },
        message="Login successful"
    )

@router.post("/refresh")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Get new access token using refresh token
    """
    # Verify refresh token
    payload = verify_token(refresh_data.refreshToken, "refresh")
    if not payload:
        return error_response(
            "Invalid refresh token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    user_id = payload.get("sub")
    if not user_id:
        return error_response(
            "Invalid token payload",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return error_response(
            "User not found or inactive",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Create new tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return success_response(
        data={
            "accessToken": access_token,
            "refreshToken": refresh_token
        },
        message="Token refreshed successfully"
    )

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's information
    """
    if not current_user:
        return error_response("User not found", status_code=404)
    
    user_data = {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "accountType": current_user.account_type.value if hasattr(current_user.account_type, 'value') else current_user.account_type,
        "isVerified": current_user.is_verified,
        "profileImageUrl": current_user.profile_image_url,
        "location": current_user.location,
        "phone": current_user.phone
    }
    
    return success_response(data=user_data)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (client should discard tokens)
    Note: For complete security, implement token blacklist with Redis
    """
    return success_response(
        message="Logout successful"
    )

@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    
    Returns access token and refresh token
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        return error_response(
            "Invalid credentials",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if user is active
    if not user.is_active:
        return error_response(
            "Account is inactive",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Build user response
    user_response = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "accountType": user.account_type.value if hasattr(user.account_type, 'value') else user.account_type,
        "isVerified": user.is_verified,
        "profileImageUrl": user.profile_image_url,
        "location": user.location,
        "phone": user.phone
    }
    
    return success_response(
        data={
            "user": user_response,
            "accessToken": access_token,
            "refreshToken": refresh_token
        },
        message="Login successful"
    )    