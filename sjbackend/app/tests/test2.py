import requests
import json

BASE_URL = "http://localhost:4000/api/v2"

def test_worker_features(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get profile
    profile = requests.get(f"{BASE_URL}/workers/profile", headers=headers)
    print(f"Get Profile: {profile.status_code}")
    
    # Test update profile
    update_data = {
        "location": "Lagos, Nigeria",
        "bio": "Experienced carpenter with 5 years experience",
        "skills": ["carpentry", "furniture making", "cabinet installation"]
    }
    update = requests.put(f"{BASE_URL}/workers/profile", json=update_data, headers=headers)
    print(f"Update Profile: {update.status_code}")
    
    # Test check visibility
    visibility = requests.get(f"{BASE_URL}/workers/can-appear-publicly", headers=headers)
    print(f"Visibility: {visibility.status_code}")

def test_employer_features(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test create job
    job_data = {
        "title": "Need Experienced Carpenter",
        "description": "Looking for carpenter to build custom furniture",
        "category": "carpentry",
        "location": "Lagos",
        "budget_min": 50000,
        "budget_max": 100000,
        "experience_level": "intermediate"
    }
    job = requests.post(f"{BASE_URL}/jobs", json=job_data, headers=headers)
    print(f"Create Job: {job.status_code}")
    
    return job.json() if job.status_code == 200 else None

if __name__ == "__main__":
    # Login as worker
    worker_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "john@test.com",
        "password": "Test123!@#"
    })
    
    if worker_login.status_code == 200:
        worker_token = worker_login.json()["data"]["accessToken"]
        test_worker_features(worker_token)
    
    # Login as employer (create one first if needed)
    employer_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "employer@test.com",
        "password": "Test123!@#"
    })
    
    if employer_login.status_code == 200:
        employer_token = employer_login.json()["data"]["accessToken"]
        test_employer_features(employer_token)