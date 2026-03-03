# app/models/product_review.py
from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON
from app.models.base import BaseModel

class ProductReview(BaseModel):
    __tablename__ = "product_reviews"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(255), nullable=True)
    review = Column(Text, nullable=True)
    
    # Media
    images = Column(JSON, default=list)  # Review images
    videos = Column(JSON, default=list)  # Review videos
    
    # Verified purchase
    verified_purchase = Column(Boolean, default=False)
    
    # Helpfulness
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="published")  # published, pending, hidden
    
    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User")
    order = relationship("Order")
    