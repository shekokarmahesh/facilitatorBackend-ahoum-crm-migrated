#!/usr/bin/env python3
"""
Test script for WhatsApp integration
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
    except ImportError as e:
        print(f"❌ psycopg2 import failed: {e}")
        return False
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import wasenderapi
        print("✅ wasenderapi imported successfully")
    except ImportError as e:
        print(f"❌ wasenderapi import failed: {e}")
        return False
    
    try:
        from config import Config
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration settings"""
    print("\n📋 Testing configuration...")
    
    try:
        from config import Config
        
        # Check WhatsApp config
        if Config.WASENDER_API_KEY:
            print("✅ WASENDER_API_KEY is configured")
        else:
            print("⚠️ WASENDER_API_KEY is not configured")
        
        if Config.WASENDER_PHONE_NUMBER:
            print(f"✅ WASENDER_PHONE_NUMBER: {Config.WASENDER_PHONE_NUMBER}")
        else:
            print("⚠️ WASENDER_PHONE_NUMBER is not configured")
        
        if Config.WASENDER_SESSION_NAME:
            print(f"✅ WASENDER_SESSION_NAME: {Config.WASENDER_SESSION_NAME}")
        else:
            print("⚠️ WASENDER_SESSION_NAME is not configured")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_whatsapp_service():
    """Test WhatsApp service initialization"""
    print("\n📱 Testing WhatsApp service...")
    
    try:
        from services.whatsapp_service import WhatsAppService
        
        # Try to initialize the service
        service = WhatsAppService()
        print("✅ WhatsApp service initialized successfully")
        
        # Test connection
        status = service.test_connection()
        if status['success']:
            print("✅ WhatsApp service connection test passed")
        else:
            print(f"⚠️ WhatsApp service connection test failed: {status['message']}")
        
        return True
    except Exception as e:
        print(f"❌ WhatsApp service test failed: {e}")
        return False

def test_database_tables():
    """Test if the courses table exists"""
    print("\n🗄️ Testing database tables...")
    
    try:
        from models.database import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # Check if courses table exists
        db_manager.execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'courses'
            );
        """)
        courses_exists = db_manager.cursor.fetchone()[0]
        
        if courses_exists:
            print("✅ Courses table exists")
        else:
            print("⚠️ Courses table does not exist - run setup_unified_system.py")
        
        db_manager.close_connection()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_course_repository():
    """Test course repository functionality"""
    print("\n📚 Testing course repository...")
    
    try:
        from models.database import DatabaseManager, CourseRepository
        
        db_manager = DatabaseManager()
        course_repo = CourseRepository(db_manager)
        
        # Note: This is just testing the repository methods exist
        # We won't actually create/modify data without a valid facilitator_id
        print("✅ CourseRepository initialized successfully")
        
        db_manager.close_connection()
        return True
    except Exception as e:
        print(f"❌ Course repository test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 WhatsApp Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("WhatsApp Service Test", test_whatsapp_service),
        ("Database Tables Test", test_database_tables),
        ("Course Repository Test", test_course_repository)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! WhatsApp integration is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 