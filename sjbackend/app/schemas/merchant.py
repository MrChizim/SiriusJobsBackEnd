# app/schemas/merchant.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base schema
class MerchantProfileBase(BaseModel):
    business_name: str
    business_category: str
    business_description: Optional[str] = None
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None
    business_website: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    whatsapp: Optional[str] = None

# For creating a new merchant profile
class MerchantProfileCreate(MerchantProfileBase):
    pass

# For updating a merchant profile
class MerchantProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    business_category: Optional[str] = None
    business_description: Optional[str] = None
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None
    business_website: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    whatsapp: Optional[str] = None

# For merchant's own profile (full details)
class MerchantProfileResponse(MerchantProfileBase):
    id: int
    user_id: int
    verified: bool
    is_active: bool
    featured: bool
    total_products: int
    total_sales: int
    average_rating: float
    review_count: int
    subscription_plan: str
    subscription_expires: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# For public merchant listing (limited info)
class MerchantPublicResponse(BaseModel):
    id: int
    business_name: str
    business_category: str
    business_description: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    verified: bool
    featured: bool
    average_rating: float
    review_count: int
    total_products: int
    
    class Config:
        from_attributes = True

# For dashboard stats
class MerchantDashboardResponse(BaseModel):
    profile: Dict[str, Any]
    recent_orders: List[Dict[str, Any]]
    quick_stats: Dict[str, int]