#!/usr/bin/env python3
"""
Migration: Fix Course Promotion Calls Schema
Adds missing columns to course_promotion_calls table to match ORM model
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.database import DatabaseManager
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the course promotion calls schema fix migration"""
    
    print("🚀 Starting Course Promotion Calls Schema Fix Migration")
    print("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        
        # Check if columns exist and add them if missing
        missing_columns = [
            ("call_start_time", "TIMESTAMP"),
            ("call_end_time", "TIMESTAMP"),
            ("student_name", "VARCHAR(255)"),
            ("student_email", "VARCHAR(255)"),
            ("conversion_status", "VARCHAR(50)"),
            ("notes", "TEXT"),
            ("livekit_room_name", "VARCHAR(255)")
        ]
        
        with db_manager.get_session() as session:
            for column_name, column_type in missing_columns:
                print(f"📋 Checking column {column_name}...")
                
                # Check if column exists
                result = session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='course_promotion_calls' 
                    AND column_name=:column_name
                """), {"column_name": column_name})
                
                exists = result.fetchone()
                
                if not exists:
                    print(f"➕ Adding missing column {column_name}...")
                    session.execute(text(f"""
                        ALTER TABLE course_promotion_calls 
                        ADD COLUMN {column_name} {column_type}
                    """))
                    print(f"✅ Column {column_name} added successfully")
                else:
                    print(f"✅ Column {column_name} already exists")
            
            # Add indexes for new columns if they don't exist
            print("📋 Adding indexes...")
            
            try:
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_course_promotion_calls_practitioner_id 
                    ON course_promotion_calls(practitioner_id)
                """))
                print("✅ Practitioner ID index ensured")
                
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_course_promotion_calls_course_id 
                    ON course_promotion_calls(course_id)
                """))
                print("✅ Course ID index ensured")
                
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_course_promotion_calls_phone_number 
                    ON course_promotion_calls(phone_number)
                """))
                print("✅ Phone number index ensured")
                
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_course_promotion_calls_call_status 
                    ON course_promotion_calls(call_status)
                """))
                print("✅ Call status index ensured")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not create some indexes: {e}")
            
            # Commit the changes
            session.commit()
            print("\n✅ Migration completed successfully!")
            print("=" * 60)
        
        # Close connection
        db_manager.close_connection()
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
        if 'db_manager' in locals():
            db_manager.close_connection()
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("🎉 Course promotion calls schema fix migration completed!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)
