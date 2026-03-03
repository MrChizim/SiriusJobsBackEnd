# app/api/v2/merchants.py
from fastapi import APIRouter, Depends, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, error_response, paginated_response
from app.models.user import User, AccountType
from app.models.merchant import MerchantProfile
from app.models.product import Product
from app.schemas.merchant import MerchantProfileUpdate, MerchantProfileResponse, MerchantPublicResponse

router = APIRouter(prefix="/merchants", tags=["merchants"])

# ========== PUBLIC MERCHANT ENDPOINTS ==========
# These must come BEFORE any parameterized routes

@router.get("/public", response_model=dict)
async def get_public_merchants(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by business category"),
    featured: Optional[bool] = Query(None, description="Filter featured merchants"),
    db: Session = Depends(get_db)
):
    """Get all merchants (public listing)"""
    query = db.query(MerchantProfile).filter(MerchantProfile.is_active == True)
    
    if category:
        query = query.filter(MerchantProfile.business_category == category)
    
    if featured is not None:
        query = query.filter(MerchantProfile.featured == featured)
    
    total = query.count()
    merchants = query.offset((page - 1) * limit).limit(limit).all()
    
    merchants_data = []
    for merchant in merchants:
        merchants_data.append({
            "id": merchant.id,
            "business_name": merchant.business_name,
            "business_category": merchant.business_category,
            "business_description": merchant.business_description[:200] + "..." if merchant.business_description and len(merchant.business_description) > 200 else merchant.business_description,
            "logo_url": merchant.logo_url,
            "banner_url": merchant.banner_url,
            "verified": merchant.verified,
            "featured": merchant.featured,
            "average_rating": merchant.average_rating,
            "review_count": merchant.review_count,
            "total_products": merchant.total_products
        })
    
    return paginated_response(
        items=merchants_data,
        total=total,
        page=page,
        limit=limit,
        message="Merchants retrieved successfully"
    )

@router.get("/public/{merchant_id}", response_model=dict)
async def get_public_merchant(
    merchant_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific merchant by ID (public)"""
    merchant = db.query(MerchantProfile).filter(
        MerchantProfile.id == merchant_id,
        MerchantProfile.is_active == True
    ).first()
    
    if not merchant:
        return error_response("Merchant not found", status_code=404)
    
    return success_response(data={
        "id": merchant.id,
        "business_name": merchant.business_name,
        "business_category": merchant.business_category,
        "business_description": merchant.business_description,
        "business_address": merchant.business_address,
        "business_phone": merchant.business_phone,
        "business_email": merchant.business_email,
        "business_website": merchant.business_website,
        "logo_url": merchant.logo_url,
        "banner_url": merchant.banner_url,
        "social": {
            "instagram": merchant.instagram,
            "facebook": merchant.facebook,
            "twitter": merchant.twitter,
            "whatsapp": merchant.whatsapp
        },
        "verified": merchant.verified,
        "featured": merchant.featured,
        "average_rating": merchant.average_rating,
        "review_count": merchant.review_count,
        "total_products": merchant.total_products
    })

# ========== MERCHANT PROFILE ENDPOINTS ==========

@router.get("/profile")
async def get_merchant_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current merchant's profile"""
    if current_user.account_type != AccountType.MERCHANT:
        return error_response("Not a merchant account", status_code=403)
    
    profile = db.query(MerchantProfile).filter(
        MerchantProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create default profile
        profile = MerchantProfile(
            user_id=current_user.id,
            business_name=current_user.name,
            business_category="general"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return success_response(data={
        "id": profile.id,
        "business_name": profile.business_name,
        "business_category": profile.business_category,
        "business_description": profile.business_description,
        "business_address": profile.business_address,
        "business_phone": profile.business_phone,
        "business_email": profile.business_email,
        "business_website": profile.business_website,
        "logo_url": profile.logo_url,
        "banner_url": profile.banner_url,
        "social": {
            "instagram": profile.instagram,
            "facebook": profile.facebook,
            "twitter": profile.twitter,
            "whatsapp": profile.whatsapp
        },
        "verified": profile.verified,
        "featured": profile.featured,
        "total_products": profile.total_products,
        "total_sales": profile.total_sales,
        "average_rating": profile.average_rating,
        "review_count": profile.review_count,
        "subscription_plan": profile.subscription_plan
    })

@router.put("/profile")
async def update_merchant_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update merchant profile"""
    if current_user.account_type != AccountType.MERCHANT:
        return error_response("Not a merchant account", status_code=403)
    
    profile = db.query(MerchantProfile).filter(
        MerchantProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        profile = MerchantProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update fields
    updatable_fields = [
        "business_name", "business_category", "business_description",
        "business_address", "business_phone", "business_email",
        "business_website", "logo_url", "banner_url",
        "instagram", "facebook", "twitter", "whatsapp"
    ]
    
    for field in updatable_fields:
        if field in profile_data:
            setattr(profile, field, profile_data[field])
    
    db.commit()
    
    return success_response(message="Profile updated successfully")

    # ========== PRODUCT ENDPOINTS ==========

@router.post("/products")
async def create_product(
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product"""
    if current_user.account_type != AccountType.MERCHANT:
        return error_response("Not a merchant account", status_code=403)
    
    profile = db.query(MerchantProfile).filter(
        MerchantProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        return error_response("Merchant profile not found", status_code=404)
    
    # Validate required fields
    required_fields = ["name", "price", "category"]
    for field in required_fields:
        if field not in product_data:
            return error_response(f"Missing required field: {field}", status_code=400)
    
    product = Product(
        merchant_id=profile.id,
        name=product_data["name"],
        description=product_data.get("description"),
        category=product_data["category"],
        price=product_data["price"],
        stock_quantity=product_data.get("stock_quantity", 0),
        sku=product_data.get("sku"),
        images=product_data.get("images", []),
        thumbnail=product_data.get("thumbnail"),
        status="draft"
    )
    
    db.add(product)
    
    # Update merchant product count
    profile.total_products = (profile.total_products or 0) + 1
    
    db.commit()
    db.refresh(product)
    
    return success_response(
        data={"id": product.id, "name": product.name},
        message="Product created successfully",
        status_code=201
    )
    
@router.get("/products")
async def get_merchant_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products for current merchant"""
    if current_user.account_type != AccountType.MERCHANT:
        return error_response("Not a merchant account", status_code=403)
    
    profile = db.query(MerchantProfile).filter(
        MerchantProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        return error_response("Merchant profile not found", status_code=404)
    
    products = db.query(Product).filter(
        Product.merchant_id == profile.id
    ).order_by(Product.created_at.desc()).all()
    
    products_data = [{
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "compare_at_price": p.compare_at_price,
        "stock_quantity": p.stock_quantity,
        "status": p.status,
        "thumbnail": p.thumbnail,
        "views_count": p.views_count,
        "sold_count": p.sold_count,
        "created_at": p.created_at.isoformat() if p.created_at else None
    } for p in products]
    
    return success_response(data=products_data)

@router.get("/products/{product_id}")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get product by ID (public)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        return error_response("Product not found", status_code=404)
    
    # Increment view count
    product.views_count = (product.views_count or 0) + 1
    db.commit()
    
    # Get merchant info
    merchant = db.query(MerchantProfile).filter(
        MerchantProfile.id == product.merchant_id
    ).first()
    
    return success_response(data={
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "compare_at_price": product.compare_at_price,
        "category": product.category,
        "subcategory": product.subcategory,
        "images": product.images,
        "thumbnail": product.thumbnail,
        "stock_quantity": product.stock_quantity,
        "tags": product.tags,
        "average_rating": product.average_rating,
        "review_count": product.review_count,
        "merchant": {
            "id": merchant.id,
            "business_name": merchant.business_name,
            "verified": merchant.verified,
            "average_rating": merchant.average_rating
        }
    })

@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product"""
    if current_user.account_type != AccountType.MERCHANT:
        return error_response("Not a merchant account", status_code=403)
    
    profile = db.query(MerchantProfile).filter(
        MerchantProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        return error_response("Merchant profile not found", status_code=404)
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.merchant_id == profile.id
    ).first()
    
    if not product:
        return error_response("Product not found", status_code=404)
    
    # Update fields
    updatable_fields = [
        "name", "description", "price", "compare_at_price", "cost_per_item",
        "stock_quantity", "sku", "category", "subcategory", "images",
        "thumbnail", "tags", "status"
    ]
    
    for field in updatable_fields:
        if field in product_data:
            setattr(product, field, product_data[field])
    
    db.commit()
    
    return success_response(message="Product updated successfully")

@router.get("/dashboard", response_model=dict)
async def get_merchant_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get merchant dashboard statistics"""
    if current_user.account_type != AccountType.MERCHANT:
        return error_response("Not a merchant account", status_code=403)
    
    profile = db.query(MerchantProfile).filter(
        MerchantProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        return error_response("Merchant profile not found", status_code=404)
    
    # Get total products
    total_products = profile.total_products
    
    # Get recent orders (if orders table exists)
    from app.models.order import Order
    recent_orders = db.query(Order).filter(
        Order.merchant_id == profile.id
    ).order_by(Order.created_at.desc()).limit(5).all()
    
    orders_data = [{
        "id": o.id,
        "order_number": o.order_number,
        "total": o.total,
        "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None
    } for o in recent_orders]
    
    return success_response(data={
        "profile": {
            "business_name": profile.business_name,
            "verified": profile.verified,
            "total_products": total_products,
            "total_sales": profile.total_sales or 0,
            "average_rating": profile.average_rating or 0.0
        },
        "recent_orders": orders_data,
        "quick_stats": {
            "products": total_products,
            "orders_today": 0,
            "revenue_month": 0,
            "customers": 0
        }
    })
   