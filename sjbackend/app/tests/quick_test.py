import requests
import json

BASE_URL = "http://localhost:4000/api/v2"

def test_api():
    # Test health
    health = requests.get("http://localhost:4000/health")
    print(f"Health: {health.json()}")
    
    # Register a worker
    register_data = {
        "name": "John Worker",
        "email": "john@test.com",
        "password": "Test123!@#",
        "accountType": "worker"
    }
    register = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Register: {register.status_code}")
    
    # Login
    login_data = {
        "email": "john@test.com",
        "password": "Test123!@#"
    }
    login = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login: {login.status_code}")
    
    if login.status_code == 200:
        token = login.json()["data"]["accessToken"]
        
        # Get workers
        workers = requests.get(f"{BASE_URL}/workers", headers={
            "Authorization": f"Bearer {token}"
        })
        print(f"Workers: {workers.status_code}")
        print(f"Response: {json.dumps(workers.json(), indent=2)}")

if __name__ == "__main__":
    test_api()