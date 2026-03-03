# app/models/order.py
from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Order(BaseModel):
    __tablename__ = "orders"
    
    order_number = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchant_profiles.id"), nullable=False)
    
    # Order details
    status = Column(String(50), default="pending")  # pending, confirmed, processing, shipped, delivered, cancelled
    payment_status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    
    # Totals
    subtotal = Column(Float, default=0)
    shipping_cost = Column(Float, default=0)
    tax = Column(Float, default=0)
    discount = Column(Float, default=0)
    total = Column(Float, default=0)
    
    # Shipping
    shipping_address = Column(JSON, nullable=True)  # {"street": "...", "city": "...", "state": "...", "zip": "..."}
    shipping_method = Column(String(100), nullable=True)
    tracking_number = Column(String(255), nullable=True)
    
    # Customer notes
    customer_notes = Column(Text, nullable=True)
    merchant_notes = Column(Text, nullable=True)
    
    # Dates
    paid_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    merchant = relationship("MerchantProfile")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

# app/models/order.py - OrderItem class should NOT have a reviews relationship

class OrderItem(BaseModel):
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    # Product snapshot
    product_name = Column(String(255), nullable=False)
    product_sku = Column(String(100), nullable=True)
    product_image = Column(String(500), nullable=True)
    
    # Relationships - ONLY these two, NO reviews relationship
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")