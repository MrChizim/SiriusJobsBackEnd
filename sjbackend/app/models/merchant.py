# app/models/merchant.py
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class MerchantProfile(BaseModel):
    __tablename__ = "merchant_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(255), nullable=False)
    business_category = Column(String(100), nullable=False)  # electronics, fashion, food, etc.
    business_description = Column(Text, nullable=True)
    business_address = Column(String(500), nullable=True)
    business_phone = Column(String(50), nullable=True)
    business_email = Column(String(255), nullable=True)
    business_website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    
    # Social media links
    instagram = Column(String(255), nullable=True)
    facebook = Column(String(255), nullable=True)
    twitter = Column(String(255), nullable=True)
    whatsapp = Column(String(50), nullable=True)
    
    # Verification & Status
    verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    featured = Column(Boolean, default=False)
    
    # Analytics
    total_products = Column(Integer, default=0)
    total_sales = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # Subscription
    subscription_plan = Column(String(50), default="free")  # free, basic, premium
    subscription_expires = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="merchant_profile")
    products = relationship("Product", back_populates="merchant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="merchant")