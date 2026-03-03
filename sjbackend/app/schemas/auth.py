# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class UserCreate(BaseModel):
    """Schema for user registration"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    accountType: str = Field(..., pattern="^(worker|employer|professional|merchant)$")
    phone: str = Field(..., pattern="^[0-9]{11}$")
    location: Optional[str] = Field(None, max_length=255)  # Add location field
    profileImageUrl: Optional[str] = Field(None)  # Add profile image field
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refreshToken: str

class UserResponse(BaseModel):
    """Schema for user data in responses"""
    id: int
    name: str
    email: EmailStr
    accountType: str
    isVerified: bool
    profileImageUrl: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True
        # Explicitly map database fields to schema fields
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "accountType": "worker",
                "isVerified": False
            }
        }
    
    @classmethod
    def from_orm(cls, user):
        """Custom method to map database fields to schema fields"""
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            accountType=user.account_type.value if hasattr(user.account_type, 'value') else user.account_type,
            isVerified=user.is_verified,
            profileImageUrl=user.profile_image_url,
            location=user.location,
            phone=user.phone
        )

class TokenResponse(BaseModel):
    """Schema for token responses"""
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"
    expiresIn: int = 900

class AuthResponse(BaseModel):
    """Schema for authentication responses"""
    user: UserResponse
    accessToken: str
    refreshToken: str