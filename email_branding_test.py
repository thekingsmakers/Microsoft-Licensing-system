import requests
import sys
import json
from datetime import datetime

class EmailBrandingAPITester:
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

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            details = ""
            
            if not success:
                details = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        details += f" - {error_data['detail']}"
                except:
                    details += f" - {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            return success, response.json() if success and response.content else {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@company.com", "password": "admin123"}
        )
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            print(f"   Admin logged in: {response['user']['name']} ({response['user']['role']})")
            return True
        return False

    def test_public_settings_endpoint(self):
        """Test public settings endpoint (no auth required)"""
        # Test without authentication
        success, response = self.run_test(
            "Public Settings Endpoint (No Auth)",
            "GET",
            "settings/public",
            200
        )
        
        if success:
            required_fields = ['company_name', 'company_tagline', 'logo_url', 'primary_color', 'theme_mode', 'accent_color']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                self.log_test("Public Settings Fields Check", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Public Settings Fields Check", True, "All required branding fields present")
                print(f"   Company: {response.get('company_name')}")
                print(f"   Tagline: {response.get('company_tagline')}")
                print(f"   Theme: {response.get('theme_mode')}")
                print(f"   Color: {response.get('primary_color')}")
        
        return success

    def test_get_admin_settings(self):
        """Test getting admin settings"""
        success, response = self.run_test(
            "Get Admin Settings",
            "GET",
            "settings",
            200
        )
        
        if success:
            # Check for email provider fields
            email_fields = ['email_provider', 'sender_email', 'sender_name']
            smtp_fields = ['smtp_host', 'smtp_port', 'smtp_username', 'smtp_use_tls']
            branding_fields = ['company_name', 'company_tagline', 'logo_url', 'primary_color', 'theme_mode', 'accent_color']
            
            all_fields = email_fields + smtp_fields + branding_fields
            missing_fields = [field for field in all_fields if field not in response]
            
            if missing_fields:
                self.log_test("Settings Fields Check", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Settings Fields Check", True, "All email and branding fields present")
                print(f"   Email Provider: {response.get('email_provider')}")
                print(f"   Company Name: {response.get('company_name')}")
                print(f"   Theme Mode: {response.get('theme_mode')}")
        
        return success

    def test_update_email_provider_resend(self):
        """Test updating email provider to Resend"""
        update_data = {
            "email_provider": "resend",
            "sender_email": "test@example.com",
            "sender_name": "Test Service Hub",
            "resend_api_key": "re_test_key_12345"
        }
        
        success, response = self.run_test(
            "Update Email Provider (Resend)",
            "PUT",
            "settings/update",
            200,
            data=update_data
        )
        return success

    def test_update_email_provider_smtp(self):
        """Test updating email provider to SMTP"""
        update_data = {
            "email_provider": "smtp",
            "sender_email": "smtp@example.com",
            "sender_name": "SMTP Service Hub",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "smtp_user",
            "smtp_password": "smtp_pass",
            "smtp_use_tls": True
        }
        
        success, response = self.run_test(
            "Update Email Provider (SMTP)",
            "PUT",
            "settings/update",
            200,
            data=update_data
        )
        return success

    def test_update_email_provider_gmail(self):
        """Test updating email provider to Gmail"""
        update_data = {
            "email_provider": "gmail",
            "sender_email": "test@gmail.com",
            "sender_name": "Gmail Service Hub",
            "smtp_username": "test@gmail.com",
            "smtp_password": "app_password_123"
        }
        
        success, response = self.run_test(
            "Update Email Provider (Gmail)",
            "PUT",
            "settings/update",
            200,
            data=update_data
        )
        return success

    def test_update_email_provider_outlook(self):
        """Test updating email provider to Outlook"""
        update_data = {
            "email_provider": "outlook",
            "sender_email": "test@outlook.com",
            "sender_name": "Outlook Service Hub",
            "smtp_username": "test@outlook.com",
            "smtp_password": "outlook_password"
        }
        
        success, response = self.run_test(
            "Update Email Provider (Outlook)",
            "PUT",
            "settings/update",
            200,
            data=update_data
        )
        return success

    def test_update_branding_settings(self):
        """Test updating branding settings"""
        update_data = {
            "company_name": "Test Organization Inc",
            "company_tagline": "Advanced Service Management",
            "logo_url": "https://example.com/logo.png",
            "primary_color": "#8b5cf6",
            "theme_mode": "light",
            "accent_color": "#8b5cf6"
        }
        
        success, response = self.run_test(
            "Update Branding Settings",
            "PUT",
            "settings/update",
            200,
            data=update_data
        )
        return success

    def test_update_theme_settings(self):
        """Test updating theme settings"""
        # Test dark theme
        success1, _ = self.run_test(
            "Update Theme (Dark)",
            "PUT",
            "settings/update",
            200,
            data={"theme_mode": "dark", "accent_color": "#06b6d4"}
        )
        
        # Test light theme
        success2, _ = self.run_test(
            "Update Theme (Light)",
            "PUT",
            "settings/update",
            200,
            data={"theme_mode": "light", "accent_color": "#10b981"}
        )
        
        # Test system theme
        success3, _ = self.run_test(
            "Update Theme (System)",
            "PUT",
            "settings/update",
            200,
            data={"theme_mode": "system", "accent_color": "#f59e0b"}
        )
        
        return success1 and success2 and success3

    def test_update_notification_thresholds(self):
        """Test updating notification thresholds"""
        update_data = {
            "notification_thresholds": [60, 30, 7, 1]
        }
        
        success, response = self.run_test(
            "Update Notification Thresholds",
            "PUT",
            "settings/update",
            200,
            data=update_data
        )
        return success

    def test_email_test_functionality(self):
        """Test email test functionality"""
        success, response = self.run_test(
            "Send Test Email",
            "POST",
            "settings/test-email",
            200
        )
        
        if success and 'message' in response:
            print(f"   Test email response: {response['message']}")
        
        return success

    def test_verify_public_settings_updated(self):
        """Verify public settings reflect the updates"""
        success, response = self.run_test(
            "Verify Public Settings Updated",
            "GET",
            "settings/public",
            200
        )
        
        if success:
            # Check if our branding updates are reflected
            expected_values = {
                'company_name': 'Test Organization Inc',
                'company_tagline': 'Advanced Service Management',
                'logo_url': 'https://example.com/logo.png',
                'primary_color': '#8b5cf6'
            }
            
            mismatches = []
            for key, expected in expected_values.items():
                actual = response.get(key)
                if actual != expected:
                    mismatches.append(f"{key}: expected '{expected}', got '{actual}'")
            
            if mismatches:
                self.log_test("Public Settings Values Check", False, f"Mismatches: {mismatches}")
            else:
                self.log_test("Public Settings Values Check", True, "All branding values updated correctly")
        
        return success

    def test_invalid_email_provider(self):
        """Test invalid email provider"""
        update_data = {
            "email_provider": "invalid_provider"
        }
        
        # This should either succeed (if validation is lenient) or fail gracefully
        success, response = self.run_test(
            "Invalid Email Provider",
            "PUT",
            "settings/update",
            200,  # Assuming it accepts any string
            data=update_data
        )
        return success

    def test_unauthorized_access(self):
        """Test unauthorized access to settings"""
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Unauthorized Settings Access",
            "GET",
            "settings",
            401  # Should be unauthorized
        )
        
        # Restore token
        self.token = original_token
        return success

    def run_all_tests(self):
        """Run all email and branding tests"""
        print("🚀 Starting Email & Branding API Tests...")
        print("=" * 60)
        
        # Authentication
        if not self.test_admin_login():
            print("❌ Cannot proceed without admin login")
            return False
        
        # Public settings (no auth required)
        self.test_public_settings_endpoint()
        
        # Admin settings access
        self.test_get_admin_settings()
        
        # Email provider tests
        self.test_update_email_provider_resend()
        self.test_update_email_provider_smtp()
        self.test_update_email_provider_gmail()
        self.test_update_email_provider_outlook()
        
        # Branding tests
        self.test_update_branding_settings()
        self.test_update_theme_settings()
        self.test_update_notification_thresholds()
        
        # Email functionality
        self.test_email_test_functionality()
        
        # Verification
        self.test_verify_public_settings_updated()
        
        # Security tests
        self.test_invalid_email_provider()
        self.test_unauthorized_access()
        
        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check details above.")
            return False

def main():
    tester = EmailBrandingAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())