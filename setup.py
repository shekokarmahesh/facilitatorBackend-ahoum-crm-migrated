#!/usr/bin/env python3
"""Setup script for the unified calling + CRM ecosystem"""

import sys
from models.database import DatabaseManager

def setup_system():
    print("🚀 Setting up Unified Ecosystem...")
    
    try:
        db_manager = DatabaseManager()
        print("✅ Database connected successfully!")
        print("✅ Tables created successfully!")
        
        # Test connection
        db_manager.execute_query("SELECT COUNT(*) FROM practitioners")
        count = db_manager.cursor.fetchone()[0]
        print(f"📊 Practitioners table: {count} records")
        
        db_manager.close_connection()
        
        print("\n🎉 Setup completed!")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Test API at: http://localhost:5000")
        
        return True
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_system() 