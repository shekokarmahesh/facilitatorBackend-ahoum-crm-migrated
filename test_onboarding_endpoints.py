"""
Test script for onboarding endpoints to debug the step2 visual profile error
"""

import json
import sys
import urllib.request
import urllib.parse
import urllib.error

# API Configuration
BASE_URL = "http://localhost:5000"

class OnboardingTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.facilitator_id = None
        
    def register_facilitator(self, phone_number="9876543210"):
        """Register a new facilitator for testing"""
        url = f"{self.base_url}/api/auth/register"
        data = {
            "phone_number": phone_number,
            "verification_code": "123456"  # Mock code for testing
        }
        
        try:
            response = requests.post(url, json=data)
            print(f"📱 Register Response ({response.status_code}): {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get('token')
                print(f"✅ Registration successful! Token: {self.auth_token[:20]}...")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def step1_basic_info(self):
        """Test Step 1: Basic Info"""
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        url = f"{self.base_url}/api/auth/onboarding/step1-basic-info"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        data = {
            "first_name": "Test",
            "last_name": "Facilitator", 
            "email": "test@example.com",
            "location": "Test City",
            "date_of_birth": "1990-01-01"
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            print(f"📝 Step 1 Response ({response.status_code}): {response.text}")
            
            if response.status_code == 200:
                print("✅ Step 1 completed successfully!")
                return True
            else:
                print(f"❌ Step 1 failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Step 1 error: {e}")
            return False
    
    def step2_visual_profile(self):
        """Test Step 2: Visual Profile - This is where the error occurs"""
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        url = f"{self.base_url}/api/auth/onboarding/step2-visual-profile"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        data = {
            "profile_url": "https://example.com/profile.jpg",
            "banner_urls": [
                "https://example.com/banner1.jpg",
                "https://example.com/banner2.jpg"
            ]
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            print(f"🖼️ Step 2 Response ({response.status_code}): {response.text}")
            
            if response.status_code == 200:
                print("✅ Step 2 completed successfully!")
                return True
            else:
                print(f"❌ Step 2 failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Step 2 error: {e}")
            return False

    def test_get_onboarding_status(self):
        """Test the GET endpoint to check onboarding status"""
        if not self.auth_token:
            print("❌ No auth token available")
            return False
            
        url = f"{self.base_url}/api/facilitator/onboarding/all-steps"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            print(f"📊 Onboarding Status Response ({response.status_code}): {response.text}")
            
            if response.status_code == 200:
                print("✅ Onboarding status retrieved successfully!")
                return True
            else:
                print(f"❌ Onboarding status failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Onboarding status error: {e}")
            return False

    def run_test_sequence(self):
        """Run the complete test sequence"""
        print("🚀 Starting Onboarding Test Sequence...")
        print("=" * 50)
        
        # Step 1: Register facilitator
        if not self.register_facilitator():
            print("❌ Test sequence failed at registration")
            return False
        
        print("\n" + "-" * 30)
        
        # Step 2: Complete basic info 
        if not self.step1_basic_info():
            print("❌ Test sequence failed at step 1")
            return False
            
        print("\n" + "-" * 30)
        
        # Step 3: Test onboarding status
        self.test_get_onboarding_status()
        
        print("\n" + "-" * 30)
        
        # Step 4: Try visual profile (this should reproduce the error)
        if not self.step2_visual_profile():
            print("❌ Test sequence failed at step 2 (expected - this is the bug we're fixing)")
            return False
            
        print("\n🎉 All tests completed successfully!")
        return True

if __name__ == "__main__":
    print("🧪 Onboarding Endpoints Test")
    print("This script will test the onboarding flow and reproduce the step2 error")
    print("=" * 60)
    
    tester = OnboardingTester()
    tester.run_test_sequence()
