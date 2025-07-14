"""
Simple Migration: Add CRM Onboarding Fields to Practitioners Table
Uses existing database connection from models
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import DatabaseManager
from sqlalchemy import text

def add_crm_onboarding_fields():
    """Add CRM onboarding fields to practitioners table"""
    try:
        # Use existing database connection
        db = DatabaseManager()
        
        print("🔄 Adding CRM onboarding fields to practitioners table...")
        
        with db.get_session() as session:
            # Check if columns already exist
            result = session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'practitioners' 
                AND column_name IN ('crm_onboarding_completed', 'crm_first_login_date', 'crm_onboarding_completed_date')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            # Add columns if they don't exist
            if 'crm_onboarding_completed' not in existing_columns:
                session.execute(text("""
                    ALTER TABLE practitioners 
                    ADD COLUMN crm_onboarding_completed BOOLEAN DEFAULT FALSE
                """))
                print("✅ Added crm_onboarding_completed column")
            
            if 'crm_first_login_date' not in existing_columns:
                session.execute(text("""
                    ALTER TABLE practitioners 
                    ADD COLUMN crm_first_login_date TIMESTAMP
                """))
                print("✅ Added crm_first_login_date column")
            
            if 'crm_onboarding_completed_date' not in existing_columns:
                session.execute(text("""
                    ALTER TABLE practitioners 
                    ADD COLUMN crm_onboarding_completed_date TIMESTAMP
                """))
                print("✅ Added crm_onboarding_completed_date column")
            
            # Create indexes for performance
            try:
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_practitioners_crm_onboarding 
                    ON practitioners(crm_onboarding_completed)
                """))
                print("✅ Created index on crm_onboarding_completed")
            except Exception as e:
                print(f"⚠️ Index creation warning: {e}")
            
            try:
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_practitioners_crm_login_date 
                    ON practitioners(crm_first_login_date)
                """))
                print("✅ Created index on crm_first_login_date")
            except Exception as e:
                print(f"⚠️ Index creation warning: {e}")
            
            session.commit()
            print("🎉 Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    add_crm_onboarding_fields() 