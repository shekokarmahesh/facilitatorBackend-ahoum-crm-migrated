#!/usr/bin/env python3
"""Simple database connection test"""

import psycopg2
from config import Config

def test_connection():
    print("🔍 Testing database connection...")
    print(f"Database URL: {Config.POSTGRES_URL[:50]}...")
    
    try:
        # Test direct connection
        conn = psycopg2.connect(Config.POSTGRES_URL)
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Check if practitioners table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'practitioners'
            );
        """)
        practitioners_exists = cursor.fetchone()[0]
        print(f"practitioners table exists: {practitioners_exists}")
        
        if practitioners_exists:
            cursor.execute("SELECT COUNT(*) FROM practitioners")
            count = cursor.fetchone()[0]
            print(f"practitioners count: {count}")
            
            # Show first few practitioners
            cursor.execute("SELECT id, phone_number, name FROM practitioners LIMIT 3")
            practitioners = cursor.fetchall()
            print("Sample practitioners:")
            for p in practitioners:
                print(f"  ID: {p[0]}, Phone: {p[1]}, Name: {p[2]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection() 