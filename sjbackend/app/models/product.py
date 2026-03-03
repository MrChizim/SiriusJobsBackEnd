# app/models/product.py
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = "products"
    
    merchant_id = Column(Integer, ForeignKey("merchant_profiles.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    
    # Pricing
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float, nullable=True)  # Original price for "sale" display
    cost_per_item = Column(Float, nullable=True)  # For profit tracking
    profit_margin = Column(Float, nullable=True)
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    sku = Column(String(100), unique=True, nullable=True)  # Stock keeping unit
    barcode = Column(String(100), nullable=True)
    track_inventory = Column(Boolean, default=True)
    allow_backorders = Column(Boolean, default=False)
    
    # Media
    images = Column(JSON, default=list)  # Array of image URLs
    videos = Column(JSON, default=list)  # Array of video URLs
    thumbnail = Column(String(500), nullable=True)
    
    # Product details
    weight = Column(Float, nullable=True)
    dimensions = Column(JSON, nullable=True)  # {"length": 10, "width": 5, "height": 2, "unit": "cm"}
    materials = Column(JSON, default=list)  # Array of materials
    tags = Column(JSON, default=list)  # Array of tags
    variants = Column(JSON, nullable=True)  # For products with options (size, color)
    
    # Status
    status = Column(String(50), default="draft")  # draft, published, archived
    featured = Column(Boolean, default=False)
    views_count = Column(Integer, default=0)
    sold_count = Column(Integer, default=0)
    
    # Ratings
    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # Relationships
    merchant = relationship("MerchantProfile", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product", cascade="all, delete-orphan")