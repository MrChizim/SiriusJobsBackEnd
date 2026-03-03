# quick_test.py
import requests

BASE_URL = "http://localhost:4000"

def test_basic():
    print("Testing basic endpoints...")
    
    # Test health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health failed: {e}")
    
    # Test root
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Root failed: {e}")
    
    # Test API v2 root
    try:
        response = requests.get(f"{BASE_URL}/api/v2")
        print(f"API v2: {response.status_code}")
    except Exception as e:
        print(f"API v2 failed: {e}")

if __name__ == "__main__":
    test_basic()