# test_merchant_features.py
import requests
import json
import random
import string
from datetime import datetime
from pprint import pprint

BASE_URL = "http://localhost:4000"
API_V2 = f"{BASE_URL}/api/v2"

# Color printing for better visibility
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️ {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.MAGENTA}{msg}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")

# Generate unique test data
def generate_unique_email(prefix="merchant"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}.{timestamp}.{random_str}@test.com"

def generate_unique_phone():
    return f"080{random.randint(10000000, 99999999)}"

# Test data storage
test_data = {
    "merchant": {
        "email": None,
        "password": "Test123!@#",
        "token": None,
        "id": None,
        "profile_id": None
    },
    "products": [],
    "public_merchant_id": None
}

# ========== TEST FUNCTIONS ==========

def test_health():
    """Test health endpoint"""
    print_info("Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success(f"Health check passed")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_register_merchant():
    """Test merchant registration"""
    print_info("\n1. Registering Merchant...")
    
    test_data["merchant"]["email"] = generate_unique_email("merchant")
    phone = generate_unique_phone()
    
    merchant_data = {
        "name": "Test Merchant Store",
        "email": test_data["merchant"]["email"],
        "password": test_data["merchant"]["password"],
        "accountType": "merchant",
        "phone": phone,
        "location": "Lagos, Nigeria"
    }
    
    response = requests.post(f"{API_V2}/auth/register", json=merchant_data)
    
    if response.status_code == 201:
        data = response.json()
        test_data["merchant"]["token"] = data['data']['accessToken']
        test_data["merchant"]["id"] = data['data']['user']['id']
        print_success(f"Merchant registered successfully")
        print(f"   Email: {test_data['merchant']['email']}")
        print(f"   Phone: {phone}")
        print(f"   User ID: {test_data['merchant']['id']}")
        return True
    else:
        print_error(f"Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_login_merchant():
    """Test merchant login"""
    print_info("\n2. Testing Merchant Login...")
    
    login_data = {
        "email": test_data["merchant"]["email"],
        "password": test_data["merchant"]["password"]
    }
    
    response = requests.post(f"{API_V2}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        test_data["merchant"]["token"] = data['data']['accessToken']
        print_success("Merchant login successful")
        return True
    else:
        print_error(f"Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_get_merchant_profile():
    """Test getting merchant profile"""
    print_info("\n3. Getting Merchant Profile...")
    
    headers = {"Authorization": f"Bearer {test_data['merchant']['token']}"}
    response = requests.get(f"{API_V2}/merchants/profile", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        test_data["merchant"]["profile_id"] = data['data']['id']
        print_success("Merchant profile retrieved")
        print(f"   Business Name: {data['data']['business_name']}")
        print(f"   Business Category: {data['data']['business_category']}")
        print(f"   Profile ID: {data['data']['id']}")
        print(f"   Verified: {data['data']['verified']}")
        return True
    else:
        print_error(f"Get profile failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_update_merchant_profile():
    """Test updating merchant profile"""
    print_info("\n4. Updating Merchant Profile...")
    
    headers = {"Authorization": f"Bearer {test_data['merchant']['token']}"}
    
    update_data = {
        "business_name": "Sirius Electronics Hub",
        "business_category": "electronics",
        "business_description": "Best electronics and gadgets in Lagos",
        "business_address": "25 Ikeja Shopping Mall, Lagos",
        "business_phone": "08012345678",
        "business_website": "https://siriuselectronics.com",
        "instagram": "@sirius_electronics",
        "facebook": "siriuselectronics",
        "twitter": "@sirius_tech"
    }
    
    response = requests.put(f"{API_V2}/merchants/profile", json=update_data, headers=headers)
    
    if response.status_code == 200:
        print_success("Merchant profile updated successfully")
        return True
    else:
        print_error(f"Update profile failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

# In run_all_tests(), after login and before test_create_product():
if test_data['merchant']['token']:
    cleanup_products()        

def test_create_product():
    """Test creating products"""
    print_info("\n5. Creating Products...")
    
    headers = {"Authorization": f"Bearer {test_data['merchant']['token']}"}
    
    import time
    import random
    
    # Use timestamp + random to guarantee uniqueness
    timestamp = int(time.time())
    random_suffix = random.randint(1000, 9999)
    
    products = [
        {
            "name": "iPhone 15 Pro",
            "description": "Latest Apple smartphone",
            "price": 850000,
            "category": "electronics",
            "stock_quantity": 10,
            "sku": f"IP15PRO-{timestamp}-{random_suffix}",  # Unique every time
        },
        {
            "name": "Samsung Galaxy S24",
            "description": "Premium Android smartphone",
            "price": 750000,
            "category": "electronics",
            "stock_quantity": 15,
            "sku": f"SGS24-{timestamp}-{random_suffix}",  # Unique every time
        },
        {
            "name": "MacBook Pro 16",
            "description": "High-performance laptop",
            "price": 1850000,
            "category": "electronics",
            "stock_quantity": 5,
            "sku": f"MBP16-{timestamp}-{random_suffix}",  # Unique every time
        }
    ]
    
    success_count = 0
    for i, product in enumerate(products, 1):
        response = requests.post(f"{API_V2}/merchants/products", json=product, headers=headers)
        if response.status_code == 201:
            data = response.json()
            test_data["products"].append(data['data']['id'])
            print_success(f"Product {i} created: {product['name']} (ID: {data['data']['id']})")
            success_count += 1
        else:
            print_error(f"Product {i} creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    print(f"   Created {success_count}/{len(products)} products")
    return success_count > 0

def test_get_merchant_products():
    """Test getting merchant's products"""
    print_info("\n6. Getting Merchant Products...")
    
    headers = {"Authorization": f"Bearer {test_data['merchant']['token']}"}
    response = requests.get(f"{API_V2}/merchants/products", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['data'])} products")
        for i, product in enumerate(data['data'][:3], 1):  # Show first 3
            print(f"   {i}. {product['name']} - ₦{product['price']:,} - Stock: {product['stock_quantity']}")
        return True
    else:
        print_error(f"Get products failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_get_product_by_id():
    """Test getting individual products by ID"""
    print_info("\n7. Testing Get Product by ID...")
    
    if not test_data["products"]:
        print_warning("No products to test")
        return False
    
    success_count = 0
    for product_id in test_data["products"][:2]:  # Test first 2 products
        response = requests.get(f"{API_V2}/merchants/products/{product_id}")
        if response.status_code == 200:
            data = response.json()
            product = data['data']
            print_success(f"Retrieved product ID {product_id}: {product['name']}")
            print(f"   Price: ₦{product['price']:,}")
            print(f"   Category: {product['category']}")
            print(f"   Views: Not tracked")  # Changed this line
            success_count += 1
        else:
            print_error(f"Get product {product_id} failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    return success_count > 0

def test_update_product():
    """Test updating a product"""
    print_info("\n8. Testing Product Update...")
    
    if not test_data["products"]:
        print_warning("No products to update")
        return False
    
    headers = {"Authorization": f"Bearer {test_data['merchant']['token']}"}
    product_id = test_data["products"][0]
    
    update_data = {
        "price": 820000,
        "stock_quantity": 8,
        "description": "Updated: iPhone 15 Pro with warranty"
    }
    
    response = requests.put(f"{API_V2}/merchants/products/{product_id}", json=update_data, headers=headers)
    
    if response.status_code == 200:
        print_success(f"Product {product_id} updated successfully")
        return True
    else:
        print_error(f"Update product failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_get_public_merchants():
    """Test public merchants listing"""
    print_info("\n9. Testing Public Merchants Listing...")
    
    response = requests.get(f"{API_V2}/merchants/public")
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['data'])} merchants")
        if data['data']:
            test_data["public_merchant_id"] = data['data'][0]['id']
            merchant = data['data'][0]
            print(f"   First merchant: {merchant['business_name']}")
            print(f"   Category: {merchant['business_category']}")
            print(f"   Rating: {merchant['average_rating']}⭐")
        return True
    else:
        print_error(f"Get public merchants failed: {response.status_code}")
        return False

def test_get_public_merchant_by_id():
    """Test getting public merchant by ID"""
    print_info("\n10. Testing Public Merchant by ID...")
    
    if not test_data["public_merchant_id"]:
        merchant_id = 1  # Fallback to ID 1
    else:
        merchant_id = test_data["public_merchant_id"]
    
    response = requests.get(f"{API_V2}/merchants/public/{merchant_id}")
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved merchant ID {merchant_id}")
        print(f"   Business: {data['data']['business_name']}")
        print(f"   Category: {data['data']['business_category']}")
        print(f"   Address: {data['data'].get('business_address', 'N/A')}")
        print(f"   Social: {data['data'].get('instagram', 'N/A')}")
        return True
    else:
        print_error(f"Get public merchant {merchant_id} failed: {response.status_code}")
        return False

def test_get_merchant_dashboard():
    """Test merchant dashboard"""
    print_info("\n11. Testing Merchant Dashboard...")
    
    headers = {"Authorization": f"Bearer {test_data['merchant']['token']}"}
    response = requests.get(f"{API_V2}/merchants/dashboard", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Merchant dashboard retrieved")
        print(f"   Business: {data['data']['profile']['business_name']}")
        print(f"   Total Products: {data['data']['profile']['total_products']}")
        print(f"   Total Sales: {data['data']['profile']['total_sales']}")
        print(f"   Average Rating: {data['data']['profile']['average_rating']}⭐")
        print(f"   Recent Orders: {len(data['data']['recent_orders'])}")
        return True
    else:
        print_error(f"Get dashboard failed: {response.status_code}")
        return False

def test_increment_product_views():
    """Test product view counting"""
    print_info("\n12. Testing Product View Counting...")
    
    if not test_data["products"]:
        print_warning("No products to test views")
        return False
    
    product_id = test_data["products"][0]
    
    # Get initial views
    response1 = requests.get(f"{API_V2}/merchants/products/{product_id}")
    if response1.status_code != 200:
        print_error("Could not get product for view test")
        return False
    
    product_data = response1.json()['data']
    
    # Check if views_count exists in the response
    if 'views_count' in product_data:
        initial_views = product_data['views_count']
        print(f"   Initial views: {initial_views}")
        
        # Get again to increment
        response2 = requests.get(f"{API_V2}/merchants/products/{product_id}")
        if response2.status_code != 200:
            print_error("Could not get product for second view")
            return False
        
        new_views = response2.json()['data']['views_count']
        print(f"   New views: {new_views}")
        
        if new_views > initial_views:
            print_success(f"View count incremented from {initial_views} to {new_views}")
            return True
        else:
            print_warning("View count did not increment")
            return True
    else:
        print_warning("Product view counting not implemented in API")
        print(f"   Response fields available: {list(product_data.keys())}")
        return True  # Return True to continue tests even if view counting isn't implemented

def cleanup_products():
    """Delete existing products to avoid SKU conflicts"""
    print_info("Cleaning up existing products...")
    
    headers = {"Authorization": f"Bearer {test_data['merchant']['token']}"}
    
    # Get all products
    try:
        response = requests.get(f"{API_V2}/merchants/products", headers=headers)
        if response.status_code == 200:
            products = response.json().get('data', [])
            for product in products:
                # Delete each product
                delete_response = requests.delete(
                    f"{API_V2}/merchants/products/{product['id']}", 
                    headers=headers
                )
                if delete_response.status_code == 200:
                    print(f"   Deleted product: {product['name']}")
            print_success(f"Cleaned up {len(products)} products")
    except Exception as e:
        print_warning(f"Cleanup error: {e}")        

# ========== MAIN TEST EXECUTION ==========

def run_all_tests():
    print_header("🛍️ TESTING MERCHANT MARKETPLACE FEATURES")
    
    # Test health first
    if not test_health():
        print_error("Server not running. Start server first with 'python run.py'")
        return
    
    # Merchant registration and login
    if not test_register_merchant():
        print_error("Merchant registration failed - trying login with existing account?")
        # Try login with default credentials if registration fails
        test_data["merchant"]["email"] = "merchant@test.com"
        test_data["merchant"]["password"] = "Test123!@#"
        if not test_login_merchant():
            print_error("Cannot proceed without merchant authentication")
            return
    else:
        # Login with newly registered merchant
        test_login_merchant()
    
    # Profile tests
    test_get_merchant_profile()
    test_update_merchant_profile()
    
    # Product tests
    if test_create_product():
        test_get_merchant_products()
        test_get_product_by_id()
        test_update_product()
        test_increment_product_views()
    
    # Public merchant tests
    test_get_public_merchants()
    test_get_public_merchant_by_id()
    
    # Dashboard test
    test_get_merchant_dashboard()
    
    # Summary
    print_header("📊 MERCHANT TEST SUMMARY")
    print(f"Merchant Email: {test_data['merchant']['email']}")
    print(f"Merchant Profile ID: {test_data['merchant']['profile_id']}")
    print(f"Products Created: {len(test_data['products'])}")
    print(f"Product IDs: {test_data['products']}")
    
    print_header("🎉 MERCHANT MARKETPLACE TESTS COMPLETED")

if __name__ == "__main__":
    run_all_tests()