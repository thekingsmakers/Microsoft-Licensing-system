import requests
import sys
import json
from datetime import datetime

class RBACTester:
    def __init__(self, base_url="https://renewal-hub-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.regular_user = None
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

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'

        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

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

    def test_admin_login(self):
        """Test admin login with provided credentials"""
        print("\n" + "="*50)
        print("TESTING ADMIN LOGIN")
        print("="*50)
        
        admin_credentials = {
            "email": "admin@company.com",
            "password": "admin123"
        }
        
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, admin_credentials)
        
        if success and 'user' in response:
            user_role = response['user'].get('role')
            if user_role == 'admin':
                self.log_test("Admin Has Admin Role", True)
                self.admin_token = response['token']
                self.admin_user = response['user']
                print(f"   Admin user: {self.admin_user['email']} - Role: {self.admin_user['role']}")
                return True
            else:
                self.log_test("Admin Has Admin Role", False, f"Expected 'admin', got '{user_role}'")
                return False
        else:
            self.log_test("Admin Has Admin Role", False, "Login failed")
            return False

    def test_new_user_gets_user_role(self):
        """Test that new users get user role"""
        print("\n" + "="*50)
        print("TESTING NEW USER GETS USER ROLE")
        print("="*50)
        
        # Register new user
        timestamp = datetime.now().strftime('%H%M%S%f')
        user_data = {
            "name": "Test User",
            "email": f"testuser_{timestamp}@test.com",
            "password": "UserPass123!"
        }
        
        success, response = self.run_test("Register New User", "POST", "auth/register", 200, user_data)
        
        if success and 'user' in response:
            user_role = response['user'].get('role')
            if user_role == 'user':
                self.log_test("New User Gets User Role", True)
                self.user_token = response['token']
                self.regular_user = response['user']
                print(f"   New user: {self.regular_user['email']} - Role: {self.regular_user['role']}")
                return True
            else:
                self.log_test("New User Gets User Role", False, f"Expected 'user', got '{user_role}'")
                return False
        else:
            self.log_test("New User Gets User Role", False, "Registration failed")
            return False

    def test_admin_settings_access(self):
        """Test admin can access settings"""
        print("\n" + "="*50)
        print("TESTING ADMIN SETTINGS ACCESS")
        print("="*50)
        
        if not self.admin_token:
            print("❌ No admin token - skipping admin settings tests")
            return
        
        # Test admin can get settings
        success, response = self.run_test("Admin Get Settings", "GET", "settings", 200, token=self.admin_token)
        
        if success:
            expected_keys = ['sender_email', 'company_name', 'notification_thresholds']
            for key in expected_keys:
                if key in response:
                    print(f"   {key}: {response[key]}")
        
        # Test admin can update settings
        settings_update = {
            "company_name": "Test Company RBAC Updated",
            "sender_email": "rbac-test@testcompany.com",
            "notification_thresholds": [45, 14, 3]
        }
        
        self.run_test("Admin Update Settings", "PUT", "settings/update", 200, settings_update, self.admin_token)

    def test_user_settings_access_denied(self):
        """Test regular user cannot access settings"""
        print("\n" + "="*50)
        print("TESTING USER SETTINGS ACCESS DENIED")
        print("="*50)
        
        if not self.user_token:
            print("❌ No user token - skipping user settings tests")
            return
        
        # Test user cannot get settings (should return 403)
        self.run_test("User Get Settings (Should Fail)", "GET", "settings", 403, token=self.user_token)
        
        # Test user cannot update settings (should return 403)
        settings_update = {
            "company_name": "Unauthorized Update"
        }
        self.run_test("User Update Settings (Should Fail)", "PUT", "settings/update", 403, settings_update, self.user_token)

    def test_admin_user_management(self):
        """Test admin can manage users"""
        print("\n" + "="*50)
        print("TESTING ADMIN USER MANAGEMENT")
        print("="*50)
        
        if not self.admin_token:
            print("❌ No admin token - skipping user management tests")
            return
        
        # Test admin can get users list
        success, response = self.run_test("Admin Get Users", "GET", "users", 200, token=self.admin_token)
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} users")
            for user in response:
                print(f"   - {user.get('name')} ({user.get('email')}) - Role: {user.get('role')}")
        
        # Test admin can update user role (if we have a regular user)
        if self.regular_user:
            # First promote to admin
            role_update = {"role": "admin"}
            success, response = self.run_test("Admin Promote User to Admin", "PUT", f"users/{self.regular_user['id']}", 200, role_update, self.admin_token)
            
            # Then demote back to user
            role_update = {"role": "user"}
            self.run_test("Admin Demote User Back", "PUT", f"users/{self.regular_user['id']}", 200, role_update, self.admin_token)

    def test_user_management_access_denied(self):
        """Test regular user cannot access user management"""
        print("\n" + "="*50)
        print("TESTING USER MANAGEMENT ACCESS DENIED")
        print("="*50)
        
        if not self.user_token:
            print("❌ No user token - skipping user management access tests")
            return
        
        # Test user cannot get users list (should return 403)
        self.run_test("User Get Users (Should Fail)", "GET", "users", 403, token=self.user_token)
        
        # Test user cannot update other users (should return 403)
        if self.admin_user:
            role_update = {"role": "user"}
            self.run_test("User Update Other User (Should Fail)", "PUT", f"users/{self.admin_user['id']}", 403, role_update, self.user_token)

    def test_admin_protection_rules(self):
        """Test admin protection rules"""
        print("\n" + "="*50)
        print("TESTING ADMIN PROTECTION RULES")
        print("="*50)
        
        if not self.admin_token or not self.admin_user:
            print("❌ No admin token/user - skipping admin protection tests")
            return
        
        # Test admin cannot delete themselves
        self.run_test("Admin Cannot Delete Self", "DELETE", f"users/{self.admin_user['id']}", 400, token=self.admin_token)
        
        # Test cannot demote last admin
        # First get current users to check admin count
        success, users = self.run_test("Get Users for Admin Count", "GET", "users", 200, token=self.admin_token)
        
        if success:
            admin_count = sum(1 for user in users if user.get('role') == 'admin')
            print(f"   Current admin count: {admin_count}")
            
            if admin_count == 1:
                # Try to demote the only admin (should fail)
                role_update = {"role": "user"}
                self.run_test("Cannot Demote Last Admin", "PUT", f"users/{self.admin_user['id']}", 400, role_update, self.admin_token)
            else:
                print(f"   Multiple admins exist ({admin_count}), skipping last admin test")

    def test_user_can_access_services(self):
        """Test that regular users can still access services"""
        print("\n" + "="*50)
        print("TESTING USER CAN ACCESS SERVICES")
        print("="*50)
        
        if not self.user_token:
            print("❌ No user token - skipping user services access tests")
            return
        
        # Test user can access services
        self.run_test("User Get Services", "GET", "services", 200, token=self.user_token)
        
        # Test user can access dashboard stats
        self.run_test("User Get Dashboard Stats", "GET", "dashboard/stats", 200, token=self.user_token)

    def run_all_rbac_tests(self):
        """Run complete RBAC test suite"""
        print("🚀 Starting RBAC Tests for Service Renewal Hub")
        print(f"Testing against: {self.base_url}")
        
        # Test admin login
        admin_logged_in = self.test_admin_login()
        
        if admin_logged_in:
            # Test new user role assignment
            user_created = self.test_new_user_gets_user_role()
            
            # Test admin access
            self.test_admin_settings_access()
            self.test_admin_user_management()
            
            # Test user access restrictions
            if user_created:
                self.test_user_settings_access_denied()
                self.test_user_management_access_denied()
                self.test_user_can_access_services()
            
            # Test admin protection rules
            self.test_admin_protection_rules()
        
        # Print final results
        print("\n" + "="*60)
        print("RBAC TEST RESULTS")
        print("="*60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL RBAC TESTS PASSED!")
            return 0
        else:
            print("❌ SOME RBAC TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
            return 1

def main():
    tester = RBACTester()
    return tester.run_all_rbac_tests()

if __name__ == "__main__":
    sys.exit(main())