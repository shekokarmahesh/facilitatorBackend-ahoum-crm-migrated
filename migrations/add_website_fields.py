"""Add website fields to facilitators table

This migration adds the necessary fields to support website publishing functionality:
- subdomain: unique subdomain for the facilitator's website
- is_published: whether the website is published and accessible
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import DatabaseManager

def up():
    """Apply the migration"""
    db = DatabaseManager()
    
    try:
        # Add new columns
        db.execute("""
            ALTER TABLE facilitators
            ADD COLUMN IF NOT EXISTS subdomain VARCHAR(255) UNIQUE,
            ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT FALSE
        """)
        
        # Create index on subdomain for faster lookups
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_facilitators_subdomain 
            ON facilitators(subdomain) 
            WHERE is_active = true AND is_published = true
        """)
        
        print("✅ Successfully added website fields to facilitators table")
    except Exception as e:
        print(f"❌ Error adding website fields: {e}")
        raise

def down():
    """Revert the migration"""
    db = DatabaseManager()
    
    try:
        # Drop index first
        db.execute("""
            DROP INDEX IF EXISTS idx_facilitators_subdomain
        """)
        
        # Drop columns
        db.execute("""
            ALTER TABLE facilitators
            DROP COLUMN IF EXISTS subdomain,
            DROP COLUMN IF EXISTS is_published
        """)
        
        print("✅ Successfully removed website fields from facilitators table")
    except Exception as e:
        print(f"❌ Error removing website fields: {e}")
        raise

if __name__ == "__main__":
    up() 