import requests
import sys
import json
from datetime import datetime

class BrandingThemeAPITester:
    def __init__(self, base_url="https://renewal-hub-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
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
        """Login as admin user"""
        print("\n" + "="*50)
        print("TESTING ADMIN LOGIN")
        print("="*50)
        
        login_data = {
            "email": "admin@company.com",
            "password": "admin123"
        }
        
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, login_data)
        
        if success and 'token' in response:
            self.token = response['token']
            print(f"   Logged in as: {response['user']['email']}")
            print(f"   User role: {response['user'].get('role', 'user')}")
            return True
        else:
            print("❌ Admin login failed - cannot continue with settings tests")
            return False

    def test_public_settings_api(self):
        """Test public settings endpoint (no auth required)"""
        print("\n" + "="*50)
        print("TESTING PUBLIC SETTINGS API")
        print("="*50)
        
        success, response = self.run_test("Get Public Settings", "GET", "settings/public", 200)
        
        if success:
            print("   Public settings response:")
            for key, value in response.items():
                print(f"     {key}: {value}")
            
            # Check required branding fields
            required_fields = ['company_name', 'company_tagline', 'primary_color', 'theme_mode']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                self.log_test("Public Settings Fields", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Public Settings Fields", True)
                
            return response
        return {}

    def test_admin_settings_api(self):
        """Test admin settings endpoints"""
        print("\n" + "="*50)
        print("TESTING ADMIN SETTINGS API")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token - skipping admin settings tests")
            return {}

        # Test get all settings
        success, response = self.run_test("Get All Settings", "GET", "settings", 200)
        
        if success:
            print("   Admin settings response:")
            for key, value in response.items():
                if 'password' in key.lower() or 'key' in key.lower():
                    print(f"     {key}: [HIDDEN]")
                else:
                    print(f"     {key}: {value}")
            return response
        return {}

    def test_branding_update(self):
        """Test updating branding settings"""
        print("\n" + "="*50)
        print("TESTING BRANDING UPDATE")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token - skipping branding update tests")
            return False

        # Test branding update
        branding_data = {
            "company_name": "Test Organization Inc",
            "company_tagline": "Testing Theme System",
            "logo_url": "https://via.placeholder.com/128x128/84cc16/ffffff?text=TEST",
            "primary_color": "#84cc16",
            "theme_mode": "light",
            "accent_color": "#84cc16"
        }
        
        success, response = self.run_test("Update Branding Settings", "PUT", "settings/update", 200, branding_data)
        
        if success:
            print("   Branding settings updated successfully")
            
            # Verify the update by checking public settings
            success2, public_response = self.run_test("Verify Public Settings Update", "GET", "settings/public", 200)
            
            if success2:
                # Check if the updates are reflected
                for key, expected_value in branding_data.items():
                    if key in public_response:
                        actual_value = public_response[key]
                        if actual_value == expected_value:
                            print(f"   ✅ {key}: {actual_value}")
                        else:
                            print(f"   ❌ {key}: Expected {expected_value}, got {actual_value}")
                            self.log_test(f"Verify {key} Update", False, f"Expected {expected_value}, got {actual_value}")
                    else:
                        print(f"   ❌ {key}: Missing from public response")
                        self.log_test(f"Verify {key} Present", False, "Field missing from public response")
            
            return True
        return False

    def test_theme_mode_changes(self):
        """Test different theme mode changes"""
        print("\n" + "="*50)
        print("TESTING THEME MODE CHANGES")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token - skipping theme mode tests")
            return False

        theme_modes = ["dark", "light", "system"]
        
        for theme_mode in theme_modes:
            theme_data = {
                "theme_mode": theme_mode
            }
            
            success, response = self.run_test(f"Set Theme Mode to {theme_mode}", "PUT", "settings/update", 200, theme_data)
            
            if success:
                # Verify the theme mode was set
                success2, public_response = self.run_test(f"Verify Theme Mode {theme_mode}", "GET", "settings/public", 200)
                
                if success2 and public_response.get('theme_mode') == theme_mode:
                    print(f"   ✅ Theme mode successfully set to {theme_mode}")
                else:
                    self.log_test(f"Verify Theme Mode {theme_mode}", False, f"Theme mode not updated correctly")

    def test_accent_color_changes(self):
        """Test different accent color changes"""
        print("\n" + "="*50)
        print("TESTING ACCENT COLOR CHANGES")
        print("="*50)
        
        if not self.token:
            print("❌ No auth token - skipping accent color tests")
            return False

        test_colors = ["#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]
        
        for color in test_colors:
            color_data = {
                "primary_color": color,
                "accent_color": color
            }
            
            success, response = self.run_test(f"Set Accent Color to {color}", "PUT", "settings/update", 200, color_data)
            
            if success:
                # Verify the color was set
                success2, public_response = self.run_test(f"Verify Accent Color {color}", "GET", "settings/public", 200)
                
                if success2 and public_response.get('primary_color') == color:
                    print(f"   ✅ Accent color successfully set to {color}")
                else:
                    self.log_test(f"Verify Accent Color {color}", False, f"Accent color not updated correctly")

    def run_all_tests(self):
        """Run complete branding and theme test suite"""
        print("🚀 Starting Branding & Theme API Tests")
        print(f"Testing against: {self.base_url}")
        
        # Test public settings (no auth required)
        public_settings = self.test_public_settings_api()
        
        # Test admin login
        admin_success = self.test_admin_login()
        
        if admin_success:
            # Test admin settings
            admin_settings = self.test_admin_settings_api()
            
            # Test branding updates
            self.test_branding_update()
            
            # Test theme mode changes
            self.test_theme_mode_changes()
            
            # Test accent color changes
            self.test_accent_color_changes()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL BRANDING & THEME TEST RESULTS")
        print("="*60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL BRANDING & THEME TESTS PASSED!")
            return 0
        else:
            print("❌ SOME BRANDING & THEME TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
            return 1

def main():
    tester = BrandingThemeAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())