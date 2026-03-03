# test_imports.py
print("Testing imports...")

try:
    from app.models import User
    print("✅ User model imported")
except Exception as e:
    print(f"❌ User import failed: {e}")

try:
    from app.models import MerchantProfile
    print("✅ MerchantProfile imported")
except Exception as e:
    print(f"❌ MerchantProfile import failed: {e}")

try:
    from app.models import Order
    print("✅ Order imported")
except Exception as e:
    print(f"❌ Order import failed: {e}")

try:
    from app.models import Product
    print("✅ Product imported")
except Exception as e:
    print(f"❌ Product import failed: {e}")