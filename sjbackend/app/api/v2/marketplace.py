# app/api/v2/marketplace.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import Optional
from app.core.database import get_db
from app.core.response import success_response, paginated_response
from app.models.product import Product
from app.models.merchant import MerchantProfile

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

@router.get("/products")
async def search_products(
    query: Optional[str] = Query(None, description="Search in product name and description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    merchant_id: Optional[int] = Query(None, description="Filter by merchant"),
    sort_by: str = Query("newest", description="Sort by: newest, price_low, price_high, popular"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search products with filters"""
    
    query_builder = db.query(Product).filter(Product.status == "published")
    
    # Text search
    if query:
        query_builder = query_builder.filter(
            or_(
                Product.name.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%")
            )
        )
    
    # Category filter
    if category:
        query_builder = query_builder.filter(Product.category == category)
    
    # Price filter
    if min_price is not None:
        query_builder = query_builder.filter(Product.price >= min_price)
    if max_price is not None:
        query_builder = query_builder.filter(Product.price <= max_price)
    
    # Merchant filter
    if merchant_id:
        query_builder = query_builder.filter(Product.merchant_id == merchant_id)
    
    # Sorting
    if sort_by == "newest":
        query_builder = query_builder.order_by(desc(Product.created_at))
    elif sort_by == "price_low":
        query_builder = query_builder.order_by(Product.price)
    elif sort_by == "price_high":
        query_builder = query_builder.order_by(desc(Product.price))
    elif sort_by == "popular":
        query_builder = query_builder.order_by(desc(Product.sold_count))
    
    total = query_builder.count()
    products = query_builder.offset((page - 1) * limit).limit(limit).all()
    
    products_data = []
    for product in products:
        merchant = db.query(MerchantProfile).filter(
            MerchantProfile.id == product.merchant_id
        ).first()
        
        products_data.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "compare_at_price": product.compare_at_price,
            "thumbnail": product.thumbnail,
            "category": product.category,
            "average_rating": product.average_rating,
            "review_count": product.review_count,
            "merchant": {
                "id": merchant.id if merchant else None,
                "business_name": merchant.business_name if merchant else "Unknown",
                "verified": merchant.verified if merchant else False
            }
        })
    
    return paginated_response(
        items=products_data,
        total=total,
        page=page,
        limit=limit,
        message="Products retrieved successfully"
    )

@router.get("/categories")
async def get_product_categories(db: Session = Depends(get_db)):
    """Get all product categories with counts"""
    from sqlalchemy import func
    
    categories = db.query(
        Product.category,
        func.count(Product.id).label("product_count")
    ).filter(Product.status == "published").group_by(Product.category).all()
    
    return success_response(data=[{
        "category": cat[0],
        "count": cat[1]
    } for cat in categories])