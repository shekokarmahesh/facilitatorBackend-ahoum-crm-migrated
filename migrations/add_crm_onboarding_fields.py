"""
Migration: Add CRM Onboarding Fields to Practitioners Table
Adds fields to track CRM platform onboarding completion status
"""

import asyncio
import asyncpg
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

async def add_crm_onboarding_fields():
    """Add CRM onboarding fields to practitioners table"""
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("🔄 Adding CRM onboarding fields to practitioners table...")
        
        # Add new columns
        await conn.execute("""
            ALTER TABLE practitioners 
            ADD COLUMN IF NOT EXISTS crm_onboarding_completed BOOLEAN DEFAULT FALSE;
        """)
        
        await conn.execute("""
            ALTER TABLE practitioners 
            ADD COLUMN IF NOT EXISTS crm_first_login_date TIMESTAMP;
        """)
        
        await conn.execute("""
            ALTER TABLE practitioners 
            ADD COLUMN IF NOT EXISTS crm_onboarding_completed_date TIMESTAMP;
        """)
        
        # Create indexes for performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_practitioners_crm_onboarding 
            ON practitioners(crm_onboarding_completed);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_practitioners_crm_first_login 
            ON practitioners(crm_first_login_date);
        """)
        
        # Update existing practitioners who have completed onboarding
        # Mark them as CRM onboarding completed if they have all onboarding data
        await conn.execute("""
            UPDATE practitioners 
            SET crm_onboarding_completed = TRUE,
                crm_onboarding_completed_date = updated_at
            WHERE id IN (
                SELECT DISTINCT p.id 
                FROM practitioners p
                INNER JOIN facilitator_basic_info bi ON p.id = bi.practitioner_id
                INNER JOIN facilitator_visual_profile vp ON p.id = vp.practitioner_id
                INNER JOIN facilitator_professional_details pd ON p.id = pd.practitioner_id
                INNER JOIN facilitator_bio_about ba ON p.id = ba.practitioner_id
                WHERE p.onboarding_step >= 5
            );
        """)
        
        # Get statistics
        total_practitioners = await conn.fetchval("SELECT COUNT(*) FROM practitioners")
        crm_completed = await conn.fetchval("SELECT COUNT(*) FROM practitioners WHERE crm_onboarding_completed = TRUE")
        calling_data = await conn.fetchval("SELECT COUNT(*) FROM practitioners WHERE is_contacted = TRUE")
        
        print(f"✅ Migration completed successfully!")
        print(f"📊 Statistics:")
        print(f"   - Total practitioners: {total_practitioners}")
        print(f"   - CRM onboarding completed: {crm_completed}")
        print(f"   - Have calling data: {calling_data}")
        print(f"   - Need CRM onboarding: {total_practitioners - crm_completed}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            await conn.close()

async def rollback_migration():
    """Rollback the migration if needed"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("🔄 Rolling back CRM onboarding fields...")
        
        # Remove indexes
        await conn.execute("DROP INDEX IF EXISTS idx_practitioners_crm_onboarding;")
        await conn.execute("DROP INDEX IF EXISTS idx_practitioners_crm_first_login;")
        
        # Remove columns
        await conn.execute("ALTER TABLE practitioners DROP COLUMN IF EXISTS crm_onboarding_completed;")
        await conn.execute("ALTER TABLE practitioners DROP COLUMN IF EXISTS crm_first_login_date;")
        await conn.execute("ALTER TABLE practitioners DROP COLUMN IF EXISTS crm_onboarding_completed_date;")
        
        print("✅ Rollback completed successfully!")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        if conn:
            await conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback_migration())
    else:
        asyncio.run(add_crm_onboarding_fields()) 