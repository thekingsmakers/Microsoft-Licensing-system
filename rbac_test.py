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

    def clear_database(self):
        """Clear users to ensure clean test state"""
        print("\n" + "="*50)
        print("CLEARING DATABASE FOR CLEAN TEST")
        print("="*50)
        
        # Try to get existing users and delete them (this might fail if no admin exists)
        try:
            # First try to create a temporary admin to clean up
            temp_admin_data = {
                "name": "Temp Admin",
                "email": "temp_admin@test.com",
                "password": "TempPass123!"
            }
            
            response = requests.post(f"{self.api_url}/auth/register", json=temp_admin_data, timeout=10)
            if response.status_code == 200:
                temp_token = response.json().get('token')
                if temp_token:
                    # Get all users
                    users_response = requests.get(f"{self.api_url}/users", 
                                                headers={'Authorization': f'Bearer {temp_token}'}, timeout=10)
                    if users_response.status_code == 200:
                        users = users_response.json()
                        temp_admin_id = response.json().get('user', {}).get('id')
                        
                        # Delete all users except the temp admin
                        for user in users:
                            if user['id'] != temp_admin_id:
                                requests.delete(f"{self.api_url}/users/{user['id']}", 
                                              headers={'Authorization': f'Bearer {temp_token}'}, timeout=10)
                        
                        # Finally delete temp admin (this might fail as it's the last admin)
                        print("Database cleared successfully")
        except Exception as e:
            print(f"Database clear attempt completed (some operations may have failed): {e}")

    def test_first_user_admin_role(self):
        """Test that first registered user gets admin role"""
        print("\n" + "="*50)
        print("TESTING FIRST USER ADMIN ROLE")
        print("="*50)
        
        # Clear database first
        self.clear_database()
        
        # Register first user
        timestamp = datetime.now().strftime('%H%M%S%f')
        admin_data = {
            "name": "Admin User",
            "email": f"admin_{timestamp}@test.com",
            "password": "AdminPass123!"
        }
        
        success, response = self.run_test("Register First User (Should be Admin)", "POST", "auth/register", 200, admin_data)
        
        if success and 'user' in response:
            user_role = response['user'].get('role')
            if user_role == 'admin':
                self.log_test("First User Gets Admin Role", True)
                self.admin_token = response['token']
                self.admin_user = response['user']
                print(f"   Admin user created: {self.admin_user['email']}")
                return True
            else:
                self.log_test("First User Gets Admin Role", False, f"Expected 'admin', got '{user_role}'")
                return False
        else:
            self.log_test("First User Gets Admin Role", False, "Registration failed")
            return False

    def test_subsequent_user_role(self):
        """Test that subsequent users get user role"""
        print("\n" + "="*50)
        print("TESTING SUBSEQUENT USER ROLE")
        print("="*50)
        
        if not self.admin_token:
            print("❌ No admin token - skipping subsequent user test")
            return False
        
        # Register second user
        timestamp = datetime.now().strftime('%H%M%S%f')
        user_data = {
            "name": "Regular User",
            "email": f"user_{timestamp}@test.com",
            "password": "UserPass123!"
        }
        
        success, response = self.run_test("Register Second User (Should be User)", "POST", "auth/register", 200, user_data)
        
        if success and 'user' in response:
            user_role = response['user'].get('role')
            if user_role == 'user':
                self.log_test("Subsequent User Gets User Role", True)
                self.user_token = response['token']
                self.regular_user = response['user']
                print(f"   Regular user created: {self.regular_user['email']}")
                return True
            else:
                self.log_test("Subsequent User Gets User Role", False, f"Expected 'user', got '{user_role}'")
                return False
        else:
            self.log_test("Subsequent User Gets User Role", False, "Registration failed")
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
            expected_keys = ['resend_api_key_masked', 'sender_email', 'company_name', 'notification_thresholds']
            for key in expected_keys:
                if key in response:
                    print(f"   {key}: {response[key]}")
        
        # Test admin can update settings
        settings_update = {
            "company_name": "Test Company RBAC",
            "sender_email": "test@testcompany.com",
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
            role_update = {"role": "admin"}
            success, response = self.run_test("Admin Update User Role", "PUT", f"users/{self.regular_user['id']}", 200, role_update, self.admin_token)
            
            # Change back to user
            role_update = {"role": "user"}
            self.run_test("Admin Change Role Back", "PUT", f"users/{self.regular_user['id']}", 200, role_update, self.admin_token)

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
        
        # Test cannot demote last admin (first create scenario where admin is the only admin)
        # Get current users to check admin count
        success, users = self.run_test("Get Users for Admin Count", "GET", "users", 200, token=self.admin_token)
        
        if success:
            admin_count = sum(1 for user in users if user.get('role') == 'admin')
            print(f"   Current admin count: {admin_count}")
            
            if admin_count == 1:
                # Try to demote the only admin (should fail)
                role_update = {"role": "user"}
                self.run_test("Cannot Demote Last Admin", "PUT", f"users/{self.admin_user['id']}", 400, role_update, self.admin_token)

    def run_all_rbac_tests(self):
        """Run complete RBAC test suite"""
        print("🚀 Starting RBAC Tests for Service Renewal Hub")
        print(f"Testing against: {self.base_url}")
        
        # Test user role assignment
        admin_created = self.test_first_user_admin_role()
        if admin_created:
            user_created = self.test_subsequent_user_role()
            
            # Test admin access
            self.test_admin_settings_access()
            self.test_admin_user_management()
            
            # Test user access restrictions
            if user_created:
                self.test_user_settings_access_denied()
                self.test_user_management_access_denied()
            
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