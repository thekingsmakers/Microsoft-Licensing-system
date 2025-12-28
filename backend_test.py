import requests
import sys
import json
from datetime import datetime, timedelta

class ServiceRenewalAPITester:
    def __init__(self, base_url="https://renewal-hub-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                details = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    details += f" - {error_detail}"
                except:
                    details += f" - {response.text[:200]}"
                self.log_test(name, False, details)
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Request failed: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n" + "="*50)
        print("TESTING HEALTH ENDPOINTS")
        print("="*50)
        
        self.run_test("API Root", "GET", "", 200)
        self.run_test("Health Check", "GET", "health", 200)

    def test_categories(self):
        """Test categories endpoint (no auth required)"""
        print("\n" + "="*50)
        print("TESTING CATEGORIES")
        print("="*50)
        
        success, response = self.run_test("Get Categories", "GET", "categories", 200)
        if success and 'categories' in response:
            print(f"   Categories found: {len(response['categories'])}")
            return response['categories']
        return []

    def test_auth_flow(self):
        """Test complete authentication flow"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION")
        print("="*50)
        
        # Generate unique test user
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"test_user_{timestamp}@example.com"
        test_password = "TestPass123!"
        test_name = f"Test User {timestamp}"

        # Test registration
        register_data = {
            "name": test_name,
            "email": test_email,
            "password": test_password
        }
        
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, register_data)
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Registered user: {response['user']['email']}")
        else:
            print("❌ Registration failed - cannot continue with auth tests")
            return False

        # Test login with same credentials
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        success, response = self.run_test("User Login", "POST", "auth/login", 200, login_data)
        
        if success and 'token' in response:
            # Update token from login
            self.token = response['token']
            print(f"   Logged in user: {response['user']['email']}")
        
        # Test get current user
        self.run_test("Get Current User", "GET", "auth/me", 200)
        
        # Test invalid login
        invalid_login = {
            "email": test_email,
            "password": "wrongpassword"
        }
        self.run_test("Invalid Login", "POST", "auth/login", 401, invalid_login)
        
        return True

    def test_services_crud(self):
        """Test complete CRUD operations for services"""
        print("\n" + "="*50)
        print("TESTING SERVICES CRUD")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token - skipping service tests")
            return None

        # Test get empty services list
        success, response = self.run_test("Get Services (Empty)", "GET", "services", 200)
        
        # Test create service
        future_date = (datetime.now() + timedelta(days=45)).isoformat()
        service_data = {
            "name": "Test Adobe Creative Cloud",
            "provider": "Adobe Inc.",
            "category": "Software License",
            "expiry_date": future_date,
            "contact_email": "admin@testcompany.com",
            "notes": "Test service for API testing",
            "cost": 599.99
        }
        
        success, response = self.run_test("Create Service", "POST", "services", 200, service_data)
        
        if not success:
            print("❌ Service creation failed - skipping remaining CRUD tests")
            return None
            
        service_id = response.get('id')
        if not service_id:
            print("❌ No service ID returned - skipping remaining CRUD tests")
            return None
            
        print(f"   Created service ID: {service_id}")

        # Test get services list (should have 1 service)
        success, response = self.run_test("Get Services (With Data)", "GET", "services", 200)
        if success:
            print(f"   Services count: {len(response)}")

        # Test get specific service
        self.run_test("Get Specific Service", "GET", f"services/{service_id}", 200)

        # Test update service
        update_data = {
            "name": "Updated Adobe Creative Cloud",
            "cost": 699.99,
            "notes": "Updated test service"
        }
        self.run_test("Update Service", "PUT", f"services/{service_id}", 200, update_data)

        # Test send reminder
        self.run_test("Send Manual Reminder", "POST", f"services/{service_id}/send-reminder", 200)

        # Test delete service
        self.run_test("Delete Service", "DELETE", f"services/{service_id}", 200)

        # Test get non-existent service
        self.run_test("Get Deleted Service", "GET", f"services/{service_id}", 404)
        
        return service_id

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        print("\n" + "="*50)
        print("TESTING DASHBOARD STATS")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token - skipping dashboard tests")
            return

        success, response = self.run_test("Get Dashboard Stats", "GET", "dashboard/stats", 200)
        
        if success:
            expected_keys = ['total', 'expiring_soon', 'expired', 'safe', 'categories', 'total_cost']
            for key in expected_keys:
                if key in response:
                    print(f"   {key}: {response[key]}")

    def test_email_logs(self):
        """Test email logs endpoint"""
        print("\n" + "="*50)
        print("TESTING EMAIL LOGS")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token - skipping email logs tests")
            return

        self.run_test("Get Email Logs", "GET", "email-logs", 200)

    def test_expiry_check(self):
        """Test expiry check trigger"""
        print("\n" + "="*50)
        print("TESTING EXPIRY CHECK")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token - skipping expiry check tests")
            return

        self.run_test("Trigger Expiry Check", "POST", "check-expiring", 200)

    def test_protected_routes_without_auth(self):
        """Test that protected routes require authentication"""
        print("\n" + "="*50)
        print("TESTING PROTECTED ROUTES (NO AUTH)")
        print("="*50)
        
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        # These should all return 401/403
        protected_endpoints = [
            ("GET", "auth/me"),
            ("GET", "services"),
            ("POST", "services"),
            ("GET", "dashboard/stats"),
            ("GET", "email-logs"),
            ("POST", "check-expiring")
        ]
        
        for method, endpoint in protected_endpoints:
            self.run_test(f"Protected {method} {endpoint}", method, endpoint, 401)
        
        # Restore token
        self.token = original_token

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Service Renewal Hub API Tests")
        print(f"Testing against: {self.base_url}")
        
        # Test basic connectivity
        self.test_health_check()
        
        # Test public endpoints
        categories = self.test_categories()
        
        # Test authentication
        auth_success = self.test_auth_flow()
        
        if auth_success:
            # Test protected endpoints
            self.test_services_crud()
            self.test_dashboard_stats()
            self.test_email_logs()
            self.test_expiry_check()
        
        # Test security
        self.test_protected_routes_without_auth()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL TEST RESULTS")
        print("="*60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return 0
        else:
            print("❌ SOME TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
            return 1

def main():
    tester = ServiceRenewalAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())