# test_all_endpoints_v2.py
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
def generate_unique_email(prefix="test"):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}.{timestamp}.{random_str}@test.com"

def generate_unique_phone():
    return f"080{random.randint(10000000, 99999999)}"

# Test data storage
test_data = {
    "worker": {
        "email": None,
        "password": "Test123!@#",
        "token": None,
        "id": None
    },
    "employer": {
        "email": None,
        "password": "Test123!@#",
        "token": None,
        "id": None
    },
    "professional": {
        "email": None,
        "password": "Test123!@#",
        "token": None,
        "id": None
    },
    "merchant": {
        "email": None,
        "password": "Test123!@#",
        "token": None,
        "id": None
    },
    "job_id": None,
    "application_id": None
}

# ========== TEST FUNCTIONS ==========

def test_health():
    """Test health endpoint"""
    print_info("Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success(f"Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_public_stats():
    """Test public stats endpoint"""
    print_info("Testing Public Stats Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/public/stats")
        if response.status_code == 200:
            print_success(f"Public stats retrieved")
            print(f"   Stats: {response.json()}")
            return True
        else:
            print_error(f"Public stats failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Public stats error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print_info("Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success(f"Root endpoint working")
            return True
        else:
            print_error(f"Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Root endpoint error: {e}")
        return False

def test_register_user(user_type, user_data):
    """Register a user of specified type"""
    print_info(f"Registering {user_type}...")
    
    response = requests.post(f"{API_V2}/auth/register", json=user_data)
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"{user_type.capitalize()} registered successfully")
        print(f"   Email: {user_data['email']}")
        print(f"   ID: {data['data']['user']['id']}")
        return {
            "success": True,
            "token": data['data']['accessToken'],
            "id": data['data']['user']['id']
        }
    else:
        print_error(f"Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return {"success": False}

def test_login(email, password, user_type):
    """Test login endpoint"""
    print_info(f"Logging in {user_type}...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{API_V2}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"{user_type.capitalize()} login successful")
        return {
            "success": True,
            "token": data['data']['accessToken'],
            "id": data['data']['user']['id']
        }
    else:
        print_error(f"Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return {"success": False}

def test_get_current_user(token, user_type):
    """Test get current user endpoint"""
    print_info(f"Getting current {user_type} user info...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_V2}/auth/me", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Got {user_type} user info")
        print(f"   Name: {data['data']['name']}")
        print(f"   Email: {data['data']['email']}")
        return True
    else:
        print_error(f"Get user failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_worker_profile(token):
    """Test worker profile endpoints"""
    print_info("Testing Worker Profile Endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get profile
    response = requests.get(f"{API_V2}/workers/profile", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print_success("Got worker profile")
        print(f"   Name: {data['data']['name']}")
        print(f"   Location: {data['data']['location']}")
    else:
        print_error(f"Get profile failed: {response.status_code}")
        return
    
    # Update profile
    update_data = {
        "bio": "Experienced professional with 5 years in the industry",
        "skills": ["carpentry", "plumbing", "electrical"],
        "location": "Port Harcourt, Nigeria"
    }
    response = requests.put(f"{API_V2}/workers/profile", json=update_data, headers=headers)
    if response.status_code == 200:
        print_success("Profile updated successfully")
    else:
        print_error(f"Profile update failed: {response.status_code}")
    
    # Check public visibility
    response = requests.get(f"{API_V2}/workers/can-appear-publicly", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print_success(f"Visibility check: {data['data']}")
    else:
        print_error(f"Visibility check failed: {response.status_code}")
    
    # Get analytics
    response = requests.get(f"{API_V2}/workers/analytics", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print_success(f"Analytics: {data['data']}")
    else:
        print_error(f"Analytics failed: {response.status_code}")

def test_employer_profile(token):
    """Test employer profile endpoints"""
    print_info("Testing Employer Profile Endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get profile
    response = requests.get(f"{API_V2}/employers/profile", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print_success("Got employer profile")
        print(f"   Company: {data['data'].get('company_name', 'N/A')}")
    else:
        print_error(f"Get profile failed: {response.status_code}")
        return
    
    # Update profile
    update_data = {
        "company_name": "Test Enterprises Ltd",
        "company_website": "https://testenterprises.com",
        "company_size": "11-50",
        "industry": "Technology",
        "company_description": "Leading provider of tech solutions",
        "location": "Lagos, Nigeria"
    }
    response = requests.put(f"{API_V2}/employers/profile", json=update_data, headers=headers)
    if response.status_code == 200:
        print_success("Employer profile updated")
    else:
        print_error(f"Profile update failed: {response.status_code}")

def test_job_categories():
    """Test job categories endpoint"""
    print_info("Testing Job Categories...")
    response = requests.get(f"{API_V2}/jobs/categories")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Got {len(data['data'])} job categories")
        print(f"   Categories: {data['data'][:5]}...")
        return True
    else:
        print_error(f"Job categories failed: {response.status_code}")
        return False

def test_job_types():
    """Test job types endpoint"""
    print_info("Testing Job Types...")
    response = requests.get(f"{API_V2}/jobs/types")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Got {len(data['data'])} job types")
        return True
    else:
        print_error(f"Job types failed: {response.status_code}")
        return False

def test_experience_levels():
    """Test experience levels endpoint"""
    print_info("Testing Experience Levels...")
    response = requests.get(f"{API_V2}/jobs/experience-levels")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Got {len(data['data'])} experience levels")
        return True
    else:
        print_error(f"Experience levels failed: {response.status_code}")
        return False

def test_create_job(token):
    """Test job creation"""
    print_info("Creating a job...")
    headers = {"Authorization": f"Bearer {token}"}
    
    job_data = {
        "title": "Experienced Carpenter Needed",
        "description": "Looking for a skilled carpenter for furniture making and home renovations",
        "category": "carpentry",
        "job_type": "full_time",
        "experience_level": "3_5_years",
        "location": "Lagos, Nigeria",
        "salary_min": 50000,
        "salary_max": 100000,
        "contact_name": "John Employer",
        "contact_email": "employer@test.com",
        "contact_phone": "08012345678"
    }
    
    response = requests.post(f"{API_V2}/jobs", json=job_data, headers=headers)
    if response.status_code == 201:
        data = response.json()
        test_data['job_id'] = data['data']['id']
        print_success(f"Job created with ID: {test_data['job_id']}")
        return True
    else:
        print_error(f"Job creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_get_jobs():
    """Test getting all jobs"""
    print_info("Getting all jobs...")
    response = requests.get(f"{API_V2}/jobs")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['data'])} jobs")
        return True
    else:
        print_error(f"Get jobs failed: {response.status_code}")
        return False

def test_search_jobs():
    """Test job search endpoint"""
    print_info("Testing job search...")
    params = {
        "category": "carpentry",
        "location": "Lagos",
        "sort_by": "newest"
    }
    response = requests.get(f"{API_V2}/jobs/search", params=params)
    if response.status_code == 200:
        data = response.json()
        print_success(f"Search returned {len(data['data'])} jobs")
        return True
    else:
        print_error(f"Job search failed: {response.status_code}")
        return False

def test_get_job_by_id(job_id):
    """Test getting job by ID"""
    print_info(f"Getting job with ID {job_id}...")
    response = requests.get(f"{API_V2}/jobs/{job_id}")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved job: {data['data']['title']}")
        return True
    else:
        print_error(f"Get job by ID failed: {response.status_code}")
        return False

def test_get_employer_jobs(token):
    """Test getting employer's jobs"""
    print_info("Getting employer's jobs...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_V2}/employers/jobs", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['data'])} jobs for employer")
        return True
    else:
        print_error(f"Get employer jobs failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_get_all_workers():
    """Test getting all workers"""
    print_info("Getting all workers...")
    response = requests.get(f"{API_V2}/workers")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['data'])} workers")
        return True
    else:
        print_error(f"Get workers failed: {response.status_code}")
        return False

def test_get_worker_by_id(worker_id):
    """Test getting worker by ID"""
    print_info(f"Getting worker with ID {worker_id}...")
    response = requests.get(f"{API_V2}/workers/{worker_id}")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved worker: {data['data']['name']}")
        return True
    else:
        print_error(f"Get worker by ID failed: {response.status_code}")
        return False

def test_create_application(token, job_id):
    """Test creating an application"""
    print_info("Creating job application...")
    headers = {"Authorization": f"Bearer {token}"}
    
    application_data = {
        "job_id": job_id,
        "cover_letter": "I am very interested in this position. I have 5 years of experience.",
        "expected_pay": 75000,
        "proposed_timeline": "2 weeks"
    }
    
    response = requests.post(f"{API_V2}/applications", json=application_data, headers=headers)
    if response.status_code == 201:
        data = response.json()
        test_data['application_id'] = data['data']['application_id']
        print_success(f"Application created with ID: {test_data['application_id']}")
        return True
    else:
        print_error(f"Application creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_get_worker_applications(token):
    """Test getting worker's applications"""
    print_info("Getting worker's applications...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_V2}/applications/my-applications", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['data'])} applications for worker")
        return True
    else:
        print_error(f"Get worker applications failed: {response.status_code}")
        return False

def test_get_job_applications(token, job_id):
    """Test getting applications for a job"""
    print_info(f"Getting applications for job {job_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_V2}/applications/job/{job_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {len(data['data'])} applications for job")
        return True
    else:
        print_error(f"Get job applications failed: {response.status_code}")
        return False

def test_shortlist_application(token, application_id):
    """Test shortlisting an application"""
    print_info(f"Shortlisting application {application_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{API_V2}/applications/{application_id}/shortlist", headers=headers)
    if response.status_code == 200:
        print_success("Application shortlisted")
        return True
    else:
        print_error(f"Shortlist failed: {response.status_code}")
        return False

def test_platform_stats():
    """Test platform statistics endpoint"""
    print_info("Testing platform statistics...")
    response = requests.get(f"{API_V2}/stats/platform")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Platform stats retrieved")
        print(f"   Total users: {data['data'].get('total_users', 0)}")
        print(f"   Active workers: {data['data'].get('active_workers', 0)}")
        print(f"   Jobs completed: {data['data'].get('jobs_completed', 0)}")
        return True
    else:
        print_error(f"Platform stats failed: {response.status_code}")
        return False

def test_track_profile_view(worker_id):
    """Test tracking profile view"""
    print_info(f"Tracking profile view for worker {worker_id}...")
    response = requests.post(f"{API_V2}/workers/track-view/{worker_id}")
    if response.status_code == 200:
        print_success("Profile view tracked")
        return True
    else:
        print_error(f"Track view failed: {response.status_code}")
        return False

# ========== MAIN TEST EXECUTION ==========

def run_all_tests():
    print_header("🚀 TESTING SIRIUSJOBS API V2 - COMPLETE SUITE")
    
    # Basic endpoints
    test_health()
    test_root()
    test_public_stats()
    
    # Generate unique test users
    test_data["worker"]["email"] = generate_unique_email("worker")
    test_data["employer"]["email"] = generate_unique_email("employer")
    test_data["professional"]["email"] = generate_unique_email("professional")
    test_data["merchant"]["email"] = generate_unique_email("merchant")
    
    print_header("📝 REGISTRATION TESTS")
    
    # Register users
    worker_reg = test_register_user("worker", {
        "name": "Test Worker",
        "email": test_data["worker"]["email"],
        "password": test_data["worker"]["password"],
        "accountType": "worker",
        "phone": generate_unique_phone(),
        "location": "Lagos, Nigeria"
    })
    if worker_reg["success"]:
        test_data["worker"]["token"] = worker_reg["token"]
        test_data["worker"]["id"] = worker_reg["id"]
    
    employer_reg = test_register_user("employer", {
        "name": "Test Employer",
        "email": test_data["employer"]["email"],
        "password": test_data["employer"]["password"],
        "accountType": "employer",
        "phone": generate_unique_phone(),
        "location": "Abuja, Nigeria"
    })
    if employer_reg["success"]:
        test_data["employer"]["token"] = employer_reg["token"]
        test_data["employer"]["id"] = employer_reg["id"]
    
    # Test professional registration (optional)
    professional_reg = test_register_user("professional", {
        "name": "Dr. Professional",
        "email": test_data["professional"]["email"],
        "password": test_data["professional"]["password"],
        "accountType": "professional",
        "phone": generate_unique_phone(),
        "location": "Port Harcourt, Nigeria"
    })
    if professional_reg["success"]:
        test_data["professional"]["token"] = professional_reg["token"]
        test_data["professional"]["id"] = professional_reg["id"]
    
    # Test merchant registration (optional)
    merchant_reg = test_register_user("merchant", {
        "name": "Merchant Store",
        "email": test_data["merchant"]["email"],
        "password": test_data["merchant"]["password"],
        "accountType": "merchant",
        "phone": generate_unique_phone(),
        "location": "Kano, Nigeria"
    })
    if merchant_reg["success"]:
        test_data["merchant"]["token"] = merchant_reg["token"]
        test_data["merchant"]["id"] = merchant_reg["id"]
    
    print_header("🔐 AUTHENTICATION TESTS")
    
    # Test login for each user type
    if test_data["worker"]["email"]:
        login_result = test_login(test_data["worker"]["email"], test_data["worker"]["password"], "worker")
        if login_result["success"]:
            test_data["worker"]["token"] = login_result["token"]
    
    if test_data["employer"]["email"]:
        login_result = test_login(test_data["employer"]["email"], test_data["employer"]["password"], "employer")
        if login_result["success"]:
            test_data["employer"]["token"] = login_result["token"]
    
    # Test get current user
    if test_data["worker"]["token"]:
        test_get_current_user(test_data["worker"]["token"], "worker")
    
    if test_data["employer"]["token"]:
        test_get_current_user(test_data["employer"]["token"], "employer")
    
    print_header("👤 WORKER ENDPOINTS")
    
    if test_data["worker"]["token"]:
        test_worker_profile(test_data["worker"]["token"])
        test_track_profile_view(test_data["worker"]["id"])
    
    print_header("🏢 EMPLOYER ENDPOINTS")
    
    if test_data["employer"]["token"]:
        test_employer_profile(test_data["employer"]["token"])
    
    print_header("📋 JOB ENDPOINTS")
    
    # Test job metadata endpoints
    test_job_categories()
    test_job_types()
    test_experience_levels()
    
    # Create a job (employer only)
    if test_data["employer"]["token"]:
        if test_create_job(test_data["employer"]["token"]):
            # Test job retrieval endpoints
            test_get_jobs()
            test_search_jobs()
            if test_data["job_id"]:
                test_get_job_by_id(test_data["job_id"])
            test_get_employer_jobs(test_data["employer"]["token"])
    
    print_header("👥 WORKER LISTING ENDPOINTS")
    
    test_get_all_workers()
    if test_data["worker"]["id"]:
        test_get_worker_by_id(test_data["worker"]["id"])
    
    print_header("📄 APPLICATION ENDPOINTS")
    
    # Worker applies to job
    if test_data["worker"]["token"] and test_data["job_id"]:
        if test_create_application(test_data["worker"]["token"], test_data["job_id"]):
            test_get_worker_applications(test_data["worker"]["token"])
    
    # Employer views and manages applications
    if test_data["employer"]["token"] and test_data["job_id"]:
        test_get_job_applications(test_data["employer"]["token"], test_data["job_id"])
        if test_data["application_id"]:
            test_shortlist_application(test_data["employer"]["token"], test_data["application_id"])
    
    print_header("📊 STATISTICS ENDPOINTS")
    
    test_platform_stats()
    
    print_header("📋 TEST SUMMARY")
    print(f"Worker Token: {'✅' if test_data['worker']['token'] else '❌'}")
    print(f"Employer Token: {'✅' if test_data['employer']['token'] else '❌'}")
    print(f"Professional Token: {'✅' if test_data['professional']['token'] else '❌'}")
    print(f"Merchant Token: {'✅' if test_data['merchant']['token'] else '❌'}")
    print(f"Job Created: {'✅' if test_data['job_id'] else '❌'}")
    print(f"Application Created: {'✅' if test_data['application_id'] else '❌'}")
    
    print_header("🎉 ALL TESTS COMPLETED")

if __name__ == "__main__":
    run_all_tests()