"""
Test Script for General Calling API Endpoints
Demonstrates how to use the new general calling functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
PHONE_NUMBER = "+918767763794"

def test_livekit_config():
    """Test LiveKit configuration"""
    print("🔧 Testing LiveKit Configuration...")
    
    response = requests.get(f"{BASE_URL}/api/general-calls/test-livekit-config")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ LiveKit Config Test:")
        print(f"   URL: {data['config']['url']}")
        print(f"   API Key: {data['config']['api_key']}")
        print(f"   Has Credentials: {data['config']['has_credentials']}")
    else:
        print(f"❌ Config test failed: {response.status_code}")
        print(response.text)

def test_simple_general_call():
    """Test the simple general call endpoint (recommended)"""
    print(f"\n📞 Testing Simple General Call to {PHONE_NUMBER}...")
    
    payload = {
        "phone_number": PHONE_NUMBER
    }
    
    response = requests.post(
        f"{BASE_URL}/api/general-calls/call-practitioner-simple",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Simple call initiated successfully!")
        print(f"   Phone: {data['phone_number']}")
        print(f"   Room: {data['room_name']}")
        print(f"   Message: {data['message']}")
    else:
        print(f"❌ Simple call failed: {response.status_code}")
        print(response.text)

def test_advanced_general_call():
    """Test the advanced general call endpoint with practitioner context"""
    print(f"\n📞 Testing Advanced General Call to {PHONE_NUMBER}...")
    
    payload = {
        "phone_number": PHONE_NUMBER,
        "practitioner_context": {
            "name": "Rajesh Kumar Sharma",
            "practice_type": "Meditation & Spiritual Guidance",
            "location": "Mumbai, Maharashtra, India",
            "website_interest": True,
            "lead_source": "api_test"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/general-calls/call-practitioner",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Advanced call initiated successfully!")
        print(f"   Phone: {data['phone_number']}")
        print(f"   Room: {data['room_name']}")
        print(f"   Purpose: {data['purpose']}")
        print(f"   Type: {data['call_type']}")
    else:
        print(f"❌ Advanced call failed: {response.status_code}")
        print(response.text)

def test_search_practitioners():
    """Test practitioner search functionality"""
    print(f"\n🔍 Testing Practitioner Search...")
    
    # Search by phone number
    response = requests.get(f"{BASE_URL}/api/general-calls/practitioners/search?q=8767763794")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Search results: {data['count']} practitioners found")
        for practitioner in data['practitioners']:
            print(f"   - {practitioner['name']} ({practitioner['phone_number']}) - {practitioner['practice_type']}")
    else:
        print(f"❌ Search failed: {response.status_code}")
        print(response.text)

def test_get_practitioner_info():
    """Test getting specific practitioner information"""
    print(f"\n👤 Testing Get Practitioner Info for {PHONE_NUMBER}...")
    
    # Clean phone number for URL
    phone_for_url = PHONE_NUMBER.replace('+', '%2B')
    
    response = requests.get(f"{BASE_URL}/api/general-calls/practitioners/{phone_for_url}/info")
    
    if response.status_code == 200:
        data = response.json()
        practitioner = data['practitioner']
        print("✅ Practitioner info retrieved:")
        print(f"   Name: {practitioner['name']}")
        print(f"   Practice: {practitioner['practice_type']}")
        print(f"   Location: {practitioner['location']}")
        print(f"   Contacted: {practitioner['is_contacted']}")
        print(f"   Status: {practitioner['contact_status']}")
    elif response.status_code == 404:
        print("⚠️  Practitioner not found in database")
    else:
        print(f"❌ Get info failed: {response.status_code}")
        print(response.text)

def test_call_history():
    """Test general call history endpoint"""
    print(f"\n📊 Testing Call History...")
    
    response = requests.get(f"{BASE_URL}/api/general-calls/call-history")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Call history: {data['count']} calls")
        print(f"   Message: {data['message']}")
    else:
        print(f"❌ Call history failed: {response.status_code}")
        print(response.text)

def main():
    """Run all tests"""
    print("🚀 Testing General Calling API Endpoints")
    print("=" * 50)
    
    try:
        # Test configuration first
        test_livekit_config()
        
        # Test search and info endpoints
        test_search_practitioners()
        test_get_practitioner_info()
        test_call_history()
        
        # Test calling endpoints
        print(f"\n📞 CALL TESTING")
        print("=" * 30)
        
        # Ask user which call method to test
        print("Choose a calling method to test:")
        print("1. Simple call (recommended - mimics CLI command)")
        print("2. Advanced call (with practitioner context)")
        print("3. Both")
        print("4. Skip calling tests")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            test_simple_general_call()
        elif choice == "2":
            test_advanced_general_call()
        elif choice == "3":
            test_simple_general_call()
            test_advanced_general_call()
        elif choice == "4":
            print("⏭️  Skipping call tests")
        else:
            print("Invalid choice, testing simple call...")
            test_simple_general_call()
        
        print(f"\n✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server.")
        print("   Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()
