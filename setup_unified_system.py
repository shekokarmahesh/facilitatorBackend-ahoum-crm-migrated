#!/usr/bin/env python3
"""
Unified Ecosystem Setup Script
Sets up the complete database schema and connections for the unified calling + CRM system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from models.database import DatabaseManager, FacilitatorRepository
from config import Config

async def setup_unified_system():
    """Setup the complete unified system"""
    
    print("🚀 Setting up Unified Calling + CRM Ecosystem")
    print("=" * 60)
    print()
    
    try:
        # Initialize database manager
        print("📊 Initializing database connection...")
        db_manager = DatabaseManager()
        
        print("✅ Connected to unified database!")
        print(f"   Database: {Config.POSTGRES_URL.split('@')[1] if '@' in Config.POSTGRES_URL else 'localhost'}")
        print()
        
        # Verify unified tables exist
        print("🔍 Verifying unified database schema...")
        
        # Check if practitioners table exists
        db_manager.execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'practitioners'
            );
        """)
        practitioners_exists = db_manager.cursor.fetchone()[0]
        
        if practitioners_exists:
            print("✅ Practitioners table (unified schema) found")
        else:
            print("❌ Practitioners table not found - running unified schema creation...")
            return False
        
        # Check student management tables
        db_manager.execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'students'
            );
        """)
        students_exists = db_manager.cursor.fetchone()[0]
        
        if students_exists:
            print("✅ Students table found")
        else:
            print("⚠️  Students table not found - will be created")
        
        # Check campaign tables
        db_manager.execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'calling_campaigns'
            );
        """)
        campaigns_exists = db_manager.cursor.fetchone()[0]
        
        if campaigns_exists:
            print("✅ Calling campaigns table found")
        else:
            print("⚠️  Campaigns table not found - will be created")
        
        # Get table counts
        print()
        print("📈 Database Statistics:")
        
        # Practitioners count
        db_manager.execute_query("SELECT COUNT(*) FROM practitioners")
        practitioners_count = db_manager.cursor.fetchone()[0]
        print(f"   👥 Practitioners: {practitioners_count}")
        
        # Students count (if table exists)
        if students_exists:
            db_manager.execute_query("SELECT COUNT(*) FROM students")
            students_count = db_manager.cursor.fetchone()[0]
            print(f"   🎓 Students: {students_count}")
        
        # Campaigns count (if table exists)
        if campaigns_exists:
            db_manager.execute_query("SELECT COUNT(*) FROM calling_campaigns")
            campaigns_count = db_manager.cursor.fetchone()[0]
            print(f"   📞 Campaigns: {campaigns_count}")
        
        # Offerings count
        try:
            db_manager.execute_query("SELECT COUNT(*) FROM offerings")
            offerings_count = db_manager.cursor.fetchone()[0]
            print(f"   📋 Offerings: {offerings_count}")
        except:
            print(f"   📋 Offerings: table not found")
        
        print()
        
        # Test API endpoints setup
        print("🔧 API Endpoints Available:")
        print("   📱 Authentication: /api/auth/*")
        print("   👤 Facilitators: /api/facilitator/*")
        print("   📋 Offerings: /api/offerings/*")
        print("   🎓 Students: /api/students/*")
        print("   📞 Campaigns: /api/campaigns/*")
        print()
        
        # Create sample data (optional)
        response = input("📝 Would you like to create sample data for testing? (y/N): ")
        if response.lower() in ['y', 'yes']:
            await create_sample_data(db_manager)
        
        db_manager.close_connection()
        
        print()
        print("🎉 Unified system setup completed successfully!")
        print()
        print("📋 Next Steps:")
        print("  1. Start the backend server: python main.py")
        print("  2. Test authentication: curl -X POST http://localhost:5000/api/auth/send-otp")
        print("  3. Access frontend: http://localhost:5173")
        print("  4. Test student management and campaigns")
        print()
        print("🔗 Integration with Calling System:")
        print("  • Practitioners data is shared between calling and CRM")
        print("  • Call outcomes feed into student insights")
        print("  • Campaigns use LiveKit for automated calling")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

async def create_sample_data(db_manager):
    """Create sample data for testing"""
    try:
        print("\n📝 Creating sample data...")
        
        facilitator_repo = FacilitatorRepository(db_manager)
        
        # Create sample practitioner
        sample_phone = "+1234567890"
        
        # Check if sample practitioner exists
        db_manager.execute_query(
            "SELECT id FROM practitioners WHERE phone_number = %s",
            (sample_phone,)
        )
        existing = db_manager.cursor.fetchone()
        
        if not existing:
            facilitator_id = facilitator_repo.create_facilitator(
                phone_number=sample_phone,
                email="sample@example.com",
                name="Sample Yoga Teacher"
            )
            
            if facilitator_id:
                # Update with additional details
                db_manager.execute_query("""
                    UPDATE practitioners 
                    SET practice_type = %s, location = %s, onboarding_step = %s,
                        student_count = %s, class_types = %s
                    WHERE id = %s
                """, (
                    "Yoga Therapy",
                    "San Francisco, CA", 
                    6,
                    15,
                    ["Hatha Yoga", "Vinyasa", "Private Sessions"],
                    facilitator_id
                ))
                
                print(f"✅ Created sample practitioner (ID: {facilitator_id})")
                
                # Create sample students
                sample_students = [
                    {"name": "Emma Thompson", "phone_number": "+1555111001", "email": "emma@email.com", "student_type": "regular"},
                    {"name": "Mike Rodriguez", "phone_number": "+1555111002", "email": "mike@email.com", "student_type": "trial"},
                    {"name": "Lisa Chen", "phone_number": "+1555111003", "email": "lisa@email.com", "student_type": "regular"},
                    {"name": "David Wilson", "phone_number": "+1555111004", "email": "david@email.com", "student_type": "former"},
                    {"name": "Sarah Johnson", "phone_number": "+1555111005", "email": "sarah@email.com", "student_type": "prospect"}
                ]
                
                for student in sample_students:
                    db_manager.execute_query("""
                        INSERT INTO students (practitioner_id, name, phone_number, email, student_type, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (practitioner_id, phone_number) DO NOTHING
                    """, (
                        facilitator_id,
                        student['name'],
                        student['phone_number'],
                        student['email'],
                        student['student_type'],
                        'active'
                    ))
                
                print(f"✅ Created {len(sample_students)} sample students")
                
                # Create sample campaign
                db_manager.execute_query("""
                    INSERT INTO calling_campaigns (practitioner_id, name, description, campaign_type, 
                                                 message_template, status, target_audience)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    facilitator_id,
                    "Workshop Promotion - Breathwork",
                    "Promote upcoming advanced breathwork workshop",
                    "workshop_promotion",
                    "Hi {student_name}! This is Alex calling about Sarah's upcoming Advanced Breathwork Workshop on Saturday. Given your practice, we thought you'd love this deep dive into pranayama techniques.",
                    "draft",
                    '{"student_types": ["regular", "trial"], "statuses": ["active"]}'
                ))
                
                print("✅ Created sample campaign")
                
                db_manager.commit()
                
                print()
                print("📊 Sample Data Created:")
                print(f"   👤 Practitioner: {sample_phone}")
                print(f"   🎓 Students: {len(sample_students)}")
                print(f"   📞 Campaigns: 1")
        else:
            print("ℹ️  Sample data already exists")
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    print("Starting unified system setup...")
    success = asyncio.run(setup_unified_system())
    
    if success:
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check your database configuration.")
        sys.exit(1) 