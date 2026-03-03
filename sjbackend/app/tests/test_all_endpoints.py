# test_all_endpoints.py
import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:4000/api/v2"

# Color printing for better visibility
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️ {msg}{Colors.END}")

def test_health():
    """Test health endpoint"""
    print_info("Testing Health Endpoint...")
    response = requests.get("http://localhost:4000/health")
    if response.status_code == 200:
        print_success(f"Health check passed: {response.json()}")
    else:
        print_error(f"Health check failed: {response.status_code}")
    return response.status_code == 200

# Store tokens and IDs for later tests
test_data = {
    "worker_token": None,
    "employer_token": None,
    "worker_id": None,
    "employer_id": None,
    "job_id": None,
    "application_id": None
}

def test_register_worker():
    """Test worker registration"""
    print_info("\n1. Testing Worker Registration...")
    
    worker_data = {
        "name": "Test Worker",
        "email": "testworker@example.com",
        "password": "Test123!@#",
        "accountType": "worker",
        "phone": "08012345678",
        "location": "Lagos, Nigeria"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=worker_data)
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Worker registered: {data['data']['user']['email']}")
        return data['data']['accessToken'], data['data']['user']['id']
    elif response.status_code == 409:
        print_warning("Worker already exists, trying login instead...")
        return test_login_worker()
    else:
        print_error(f"Registration failed: {response.status_code} - {response.text}")
        return None, None

def test_register_employer():
    """Test employer registration"""
    print_info("\n2. Testing Employer Registration...")
    
    employer_data = {
        "name": "Test Employer",
        "email": "testemployer@example.com",
        "password": "Test123!@#",
        "accountType": "employer",
        "phone": "08087654321",
        "location": "Abuja, Nigeria"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=employer_data)
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Employer registered: {data['data']['user']['email']}")
        return data['data']['accessToken'], data['data']['user']['id']
    elif response.status_code == 409:
        print_warning("Employer already exists, trying login instead...")
        return test_login_employer()
    else:
        print_error(f"Registration failed: {response.status_code} - {response.text}")
        return None, None

def test_login_worker():
    """Test worker login"""
    print_info("Testing Worker Login...")
    
    login_data = {
        "email": "testworker@example.com",
        "password": "Test123!@#"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Worker login successful")
        return data['data']['accessToken'], data['data']['user']['id']
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None, None

def test_login_employer():
    """Test employer login"""
    print_info("Testing Employer Login...")
    
    login_data = {
        "email": "testemployer@example.com",
        "password": "Test123!@#"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print_success("Employer login successful")
        return data['data']['accessToken'], data['data']['user']['id']
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None, None

def test_worker_profile(token):
    """Test worker profile endpoints"""
    print_info("\n3. Testing Worker Profile Endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get profile
    response = requests.get(f"{BASE_URL}/workers/profile", headers=headers)
    if response.status_code == 200:
        print_success("Got worker profile")
        profile = response.json()['data']
        print(f"   Name: {profile['name']}")
        print(f"   Location: {profile['location']}")
    else:
        print_error(f"Get profile failed: {response.status_code}")
    
    # Update profile
    update_data = {
        "bio": "Experienced professional with 5 years in the industry",
        "skills": ["carpentry", "plumbing", "electrical"],
        "location": "Port Harcourt, Nigeria"
    }
    response = requests.put(f"{BASE_URL}/workers/profile", json=update_data, headers=headers)
    if response.status_code == 200:
        print_success("Profile updated successfully")
    else:
        print_error(f"Profile update failed: {response.status_code}")
    
    # Check public visibility
    response = requests.get(f"{BASE_URL}/workers/can-appear-publicly", headers=headers)
    if response.status_code == 200:
        print_success(f"Visibility check: {response.json()['data']}")
    else:
        print_error(f"Visibility check failed: {response.status_code}")
    
    # Get analytics
    response = requests.get(f"{BASE_URL}/workers/analytics", headers=headers)
    if response.status_code == 200:
        print_success(f"Analytics: {response.json()['data']}")
    else:
        print_error(f"Analytics failed: {response.status_code}")

def test_employer_profile(token, employer_id):
    """Test employer profile endpoints"""
    print_info("\n4. Testing Employer Profile Endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get profile
    response = requests.get(f"{BASE_URL}/employers/profile", headers=headers)
    if response.status_code == 200:
        print_success("Got employer profile")
        profile = response.json()['data']
        print(f"   Company: {profile['company_name']}")
    else:
        print_error(f"Get profile failed: {response.status_code}")
    
    # Update profile
    update_data = {
        "company_name": "Test Enterprises Ltd",
        "company_website": "https://testenterprises.com",
        "company_size": "11-50",
        "industry": "Technology",
        "company_description": "Leading provider of tech solutions",
        "location": "Lagos, Nigeria"
    }
    response = requests.put(f"{BASE_URL}/employers/profile", json=update_data, headers=headers)
    if response.status_code == 200:
        print_success("Employer profile updated")
    else:
        print_error(f"Profile update failed: {response.status_code}")

def test_job_posting(token):
    """Test job posting endpoints"""
    print_info("\n5. Testing Job Posting Endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create job
    job_data = {
        "title": "Experienced Carpenter Needed",
        "description": "Looking for a skilled carpenter for furniture making and home renovations",
        "category": "carpentry",
        "location": "Lagos, Nigeria",
        "is_remote": False,
        "budget_min": 50000,
        "budget_max": 100000,
        "budget_type": "fixed",
        "experience_level": "intermediate",
        "skills_required": "carpentry,furniture making,wood finishing",
        "duration": "short-term"
    }
    
    response = requests.post(f"{BASE_URL}/jobs", json=job_data, headers=headers)
    if response.status_code == 201:
        data = response.json()
        test_data['job_id'] = data['data']['id']
        print_success(f"Job created with ID: {test_data['job_id']}")
    else:
        print_error(f"Job creation failed: {response.status_code} - {response.text}")
        return None
    
    # Get employer's jobs
    response = requests.get(f"{BASE_URL}/employers/jobs", headers=headers)
    if response.status_code == 200:
        jobs = response.json()['data']
        print_success(f"Retrieved {len(jobs)} jobs for employer")
    else:
        print_error(f"Get employer jobs failed: {response.status_code}")
    
    return test_data['job_id']

def test_public_jobs():
    """Test public job listing endpoints"""
    print_info("\n6. Testing Public Job Endpoints...")
    
    # Get all jobs
    response = requests.get(f"{BASE_URL}/jobs")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['data'])} jobs")
        if data['data']:
            test_data['job_id'] = data['data'][0]['id']
    else:
        print_error(f"Get jobs failed: {response.status_code}")
    
    # Get job by ID if available
    if test_data.get('job_id'):
        response = requests.get(f"{BASE_URL}/jobs/{test_data['job_id']}")
        if response.status_code == 200:
            print_success(f"Retrieved job details for ID: {test_data['job_id']}")
        else:
            print_error(f"Get job by ID failed: {response.status_code}")

def test_application(worker_token, job_id):
    """Test application endpoints"""
    print_info("\n7. Testing Application Endpoints...")
    headers = {"Authorization": f"Bearer {worker_token}"}
    
    # Apply to job
    application_data = {
        "job_id": job_id,
        "cover_letter": "I am very interested in this position. I have 5 years of experience.",
        "expected_pay": 75000,
        "proposed_timeline": "2 weeks"
    }
    
    response = requests.post(f"{BASE_URL}/applications", json=application_data, headers=headers)
    if response.status_code == 201:
        data = response.json()
        test_data['application_id'] = data['data']['application_id']
        print_success(f"Application submitted with ID: {test_data['application_id']}")
    else:
        print_error(f"Application failed: {response.status_code} - {response.text}")
    
    # Get worker's applications
    response = requests.get(f"{BASE_URL}/applications/my-applications", headers=headers)
    if response.status_code == 200:
        apps = response.json()['data']
        print_success(f"Retrieved {len(apps)} applications for worker")
    else:
        print_error(f"Get worker applications failed: {response.status_code}")

def test_employer_applications(employer_token, job_id):
    """Test employer viewing applications"""
    print_info("\n8. Testing Employer Application Views...")
    headers = {"Authorization": f"Bearer {employer_token}"}
    
    # Get job applications
    response = requests.get(f"{BASE_URL}/applications/job/{job_id}", headers=headers)
    if response.status_code == 200:
        apps = response.json()['data']
        print_success(f"Retrieved {len(apps)} applications for job")
        if apps:
            test_data['application_id'] = apps[0]['id']
    else:
        print_error(f"Get job applications failed: {response.status_code}")
    
    # Test shortlist if we have an application
    if test_data.get('application_id'):
        response = requests.put(
            f"{BASE_URL}/applications/{test_data['application_id']}/shortlist", 
            headers=headers
        )
        if response.status_code == 200:
            print_success("Application shortlisted")
        else:
            print_error(f"Shortlist failed: {response.status_code}")

def run_all_tests():
    """Run all tests in sequence"""
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}🚀 TESTING SIRIUSJOBS API V2{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    # Test health first
    if not test_health():
        print_error("Server not running. Start server first with 'python run.py'")
        return
    
    # Register/Login users
    worker_token, worker_id = test_register_worker()
    if worker_token:
        test_data['worker_token'] = worker_token
        test_data['worker_id'] = worker_id
    
    employer_token, employer_id = test_register_employer()
    if employer_token:
        test_data['employer_token'] = employer_token
        test_data['employer_id'] = employer_id
    
    # Test profiles
    if test_data['worker_token']:
        test_worker_profile(test_data['worker_token'])
    
    if test_data['employer_token']:
        test_employer_profile(test_data['employer_token'], test_data['employer_id'])
    
    # Test job posting (employer)
    if test_data['employer_token']:
        job_id = test_job_posting(test_data['employer_token'])
        if job_id:
            test_data['job_id'] = job_id
    
    # Test public job endpoints
    test_public_jobs()
    
    # Test applications (worker applies)
    if test_data['worker_token'] and test_data.get('job_id'):
        test_application(test_data['worker_token'], test_data['job_id'])
    
    # Test employer viewing applications
    if test_data['employer_token'] and test_data.get('job_id'):
        test_employer_applications(test_data['employer_token'], test_data['job_id'])
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}📊 TEST SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Worker Token: {'✅' if test_data['worker_token'] else '❌'}")
    print(f"Employer Token: {'✅' if test_data['employer_token'] else '❌'}")
    print(f"Job Created: {'✅' if test_data.get('job_id') else '❌'}")
    print(f"Application Submitted: {'✅' if test_data.get('application_id') else '❌'}")
    print(f"\n{Colors.GREEN}🎉 Testing complete!{Colors.END}")

if __name__ == "__main__":
    run_all_tests()