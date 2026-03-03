import requests
import json

BASE_URL = "http://localhost:4000/api/v2"

# Login first
login_data = {
    "email": "john@test.com",  # Use a worker account
    "password": "Test123!@#"
}

response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
token = response.json()["data"]["accessToken"]
headers = {"Authorization": f"Bearer {token}"}

# Test add guarantor
guarantor_data = {
    "guarantorName": "Jane Doe",
    "guarantorPhone": "08098765432",
    "guarantorEmail": "jane@example.com"
}
response = requests.post(f"{BASE_URL}/workers/guarantor", json=guarantor_data, headers=headers)
print(f"Add Guarantor: {response.status_code} - {response.json()}")

# Test check visibility
response = requests.get(f"{BASE_URL}/workers/can-appear-publicly", headers=headers)
print(f"Can Appear Publicly: {response.status_code} - {response.json()}")

# Test get analytics
response = requests.get(f"{BASE_URL}/workers/analytics", headers=headers)
print(f"Analytics: {response.status_code} - {response.json()}")

# Test track profile view (public endpoint - no auth needed)
response = requests.post(f"{BASE_URL}/workers/track-view/1")  # Replace 1 with actual worker ID
print(f"Track View: {response.status_code} - {response.json()}")