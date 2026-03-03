# app/api/v2/orders.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.response import success_response, error_response
from app.models.user import User, AccountType
from app.models.merchant import MerchantProfile
from app.models.product import Product
from app.models.order import Order, OrderItem
import uuid
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/cart/checkout")
async def checkout(
    cart_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create order from cart items"""
    items = cart_data.get("items", [])
    shipping_address = cart_data.get("shipping_address")
    
    if not items:
        return error_response("Cart is empty", status_code=400)
    
    if not shipping_address:
        return error_response("Shipping address required", status_code=400)
    
    # Group items by merchant
    merchant_items = {}
    for item in items:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product:
            return error_response(f"Product {item['product_id']} not found", status_code=404)
        
        merchant_id = product.merchant_id
        if merchant_id not in merchant_items:
            merchant_items[merchant_id] = []
        
        merchant_items[merchant_id].append({
            "product": product,
            "quantity": item["quantity"],
            "price": product.price
        })
    
    # Create separate order for each merchant
    orders = []
    for merchant_id, mitems in merchant_items.items():
        order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        subtotal = sum(item["price"] * item["quantity"] for item in mitems)
        total = subtotal  # Add shipping/tax later
        
        order = Order(
            order_number=order_number,
            user_id=current_user.id,
            merchant_id=merchant_id,
            subtotal=subtotal,
            total=total,
            shipping_address=shipping_address,
            status="pending",
            payment_status="pending"
        )
        
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order items
        for mitem in mitems:
            product = mitem["product"]
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=mitem["quantity"],
                price=product.price,
                total=product.price * mitem["quantity"],
                product_name=product.name,
                product_sku=product.sku,
                product_image=product.thumbnail
            )
            db.add(order_item)
            
            # Update product sold count
            product.sold_count = (product.sold_count or 0) + mitem["quantity"]
            if product.track_inventory:
                product.stock_quantity -= mitem["quantity"]
        
        orders.append(order)
    
    db.commit()
    
    return success_response(
        data={"order_ids": [o.id for o in orders]},
        message="Order created successfully"
    )

@router.get("/my-orders")
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's orders"""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    orders_data = []
    for order in orders:
        merchant = db.query(MerchantProfile).filter(
            MerchantProfile.id == order.merchant_id
        ).first()
        
        orders_data.append({
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "payment_status": order.payment_status,
            "total": order.total,
            "merchant_name": merchant.business_name if merchant else "Unknown",
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "item_count": len(order.items)
        })
    
    return success_response(data=orders_data)

@router.get("/merchant/orders")
async def get_merchant_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get orders for current merchant"""
    if current_user.account_type != AccountType.MERCHANT:
        return error_response("Not a merchant account", status_code=403)
    
    profile = db.query(MerchantProfile).filter(
        MerchantProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        return error_response("Merchant profile not found", status_code=404)
    
    orders = db.query(Order).filter(
        Order.merchant_id == profile.id
    ).order_by(Order.created_at.desc()).all()
    
    orders_data = []
    for order in orders:
        customer = db.query(User).filter(User.id == order.user_id).first()
        
        orders_data.append({
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "payment_status": order.payment_status,
            "total": order.total,
            "customer_name": customer.name if customer else "Unknown",
            "customer_email": customer.email if customer else "Unknown",
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items": [{
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": item.price,
                "total": item.total
            } for item in order.items]
        })
    
    return success_response(data=orders_data)