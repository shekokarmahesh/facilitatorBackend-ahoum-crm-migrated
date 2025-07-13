#!/usr/bin/env python3
"""
Migration: Add Course Promotion Calling Tables
Creates tables and indexes needed for course promotion AI calling feature
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run the course promotion tables migration"""
    
    print("🚀 Starting Course Promotion Tables Migration")
    print("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        
        # 1. Create course_promotion_calls table
        print("📋 Creating course_promotion_calls table...")
        db_manager.cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_promotion_calls (
                id SERIAL PRIMARY KEY,
                practitioner_id INTEGER NOT NULL REFERENCES practitioners(id) ON DELETE CASCADE,
                course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
                phone_number VARCHAR(20) NOT NULL,
                call_status VARCHAR(50) DEFAULT 'initiated', 
                call_outcome VARCHAR(50), 
                call_duration INTEGER, 
                livekit_room_name VARCHAR(255),
                transcript_summary TEXT,
                student_response TEXT,
                follow_up_required BOOLEAN DEFAULT FALSE,
                scheduled_callback TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ course_promotion_calls table created")
        
        # 2. Create indexes for performance
        print("📋 Creating indexes...")
        db_manager.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_promotion_calls_practitioner 
            ON course_promotion_calls(practitioner_id);
        """)
        
        db_manager.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_promotion_calls_course 
            ON course_promotion_calls(course_id);
        """)
        
        db_manager.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_promotion_calls_phone 
            ON course_promotion_calls(phone_number);
        """)
        
        db_manager.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_promotion_calls_status 
            ON course_promotion_calls(call_status);
        """)
        
        db_manager.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_promotion_calls_created 
            ON course_promotion_calls(created_at);
        """)
        print("✅ Indexes created")
        
        # 3. Add course promotion tracking to existing call_transcripts table
        print("📋 Adding course promotion fields to call_transcripts...")
        try:
            db_manager.cursor.execute("""
                ALTER TABLE call_transcripts 
                ADD COLUMN IF NOT EXISTS course_id INTEGER REFERENCES courses(id) ON DELETE SET NULL;
            """)
            
            db_manager.cursor.execute("""
                ALTER TABLE call_transcripts 
                ADD COLUMN IF NOT EXISTS call_type VARCHAR(50) DEFAULT 'general';
            """)
            print("✅ call_transcripts table updated")
        except Exception as e:
            print(f"⚠️  call_transcripts columns may already exist: {e}")
        
        # 4. Add course promotion insights to practitioner_insights table
        print("📋 Adding course promotion insights...")
        try:
            db_manager.cursor.execute("""
                ALTER TABLE practitioner_insights 
                ADD COLUMN IF NOT EXISTS course_promotion_calls INTEGER DEFAULT 0;
            """)
            
            db_manager.cursor.execute("""
                ALTER TABLE practitioner_insights 
                ADD COLUMN IF NOT EXISTS course_promotion_success INTEGER DEFAULT 0;
            """)
            print("✅ practitioner_insights table updated")
        except Exception as e:
            print(f"⚠️  practitioner_insights columns may already exist: {e}")
        
        # 5. Create a view for course promotion analytics
        print("📋 Creating course promotion analytics view...")
        db_manager.cursor.execute("""
            CREATE OR REPLACE VIEW course_promotion_analytics AS
            SELECT 
                c.id as course_id,
                c.title as course_title,
                c.practitioner_id,
                COUNT(cpc.id) as total_calls,
                COUNT(CASE WHEN cpc.call_outcome = 'interested' THEN 1 END) as interested_calls,
                COUNT(CASE WHEN cpc.call_outcome = 'very_interested' THEN 1 END) as very_interested_calls,
                COUNT(CASE WHEN cpc.call_outcome = 'registered' THEN 1 END) as registered_calls,
                AVG(cpc.call_duration) as avg_call_duration,
                MAX(cpc.created_at) as last_call_date
            FROM courses c
            LEFT JOIN course_promotion_calls cpc ON c.id = cpc.course_id
            WHERE c.is_active = TRUE
            GROUP BY c.id, c.title, c.practitioner_id;
        """)
        print("✅ course_promotion_analytics view created")
        
        # 6. Commit all changes
        db_manager.connection.commit()
        
        # 7. Verify tables exist
        print("\n📋 Verifying migration...")
        db_manager.cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'course_promotion_calls'
            );
        """)
        table_exists = db_manager.cursor.fetchone()[0]
        
        if table_exists:
            db_manager.cursor.execute("SELECT COUNT(*) FROM course_promotion_calls")
            count = db_manager.cursor.fetchone()[0]
            print(f"✅ course_promotion_calls table verified (current records: {count})")
        
        db_manager.close_connection()
        
        print("\n🎉 Course Promotion Tables Migration Completed Successfully!")
        print("\nTables Added:")
        print("  📋 course_promotion_calls - Main call tracking table")
        print("  📊 course_promotion_analytics - Analytics view")
        print("\nColumns Added:")
        print("  📞 call_transcripts.course_id - Links transcripts to courses")
        print("  📞 call_transcripts.call_type - Distinguishes call types")
        print("  📈 practitioner_insights.course_promotion_* - Promotion stats")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        logger.error(f"Migration error: {e}")
        return False

def rollback_migration():
    """Rollback the migration (for testing purposes)"""
    print("🔄 Rolling back Course Promotion Tables Migration...")
    
    try:
        db_manager = DatabaseManager()
        
        # Drop view
        db_manager.cursor.execute("DROP VIEW IF EXISTS course_promotion_analytics CASCADE;")
        
        # Drop table
        db_manager.cursor.execute("DROP TABLE IF EXISTS course_promotion_calls CASCADE;")
        
        # Remove added columns (optional - commented out to preserve data)
        # db_manager.cursor.execute("ALTER TABLE call_transcripts DROP COLUMN IF EXISTS course_id;")
        # db_manager.cursor.execute("ALTER TABLE call_transcripts DROP COLUMN IF EXISTS call_type;")
        # db_manager.cursor.execute("ALTER TABLE practitioner_insights DROP COLUMN IF EXISTS course_promotion_calls;")
        # db_manager.cursor.execute("ALTER TABLE practitioner_insights DROP COLUMN IF EXISTS course_promotion_success;")
        
        db_manager.connection.commit()
        db_manager.close_connection()
        
        print("✅ Migration rolled back successfully")
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Course Promotion Tables Migration")
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_migration()
    else:
        success = run_migration()
    
    sys.exit(0 if success else 1) 