"""
SQLAlchemy ORM Models for Ahoum CRM System
Replaces raw SQL with secure ORM patterns
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ARRAY, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional, Dict, Any
import os

Base = declarative_base()

# =============================================================================
# CORE MASTER TABLE
# =============================================================================

class Practitioner(Base):
    """Master table combining calling leads with CRM facilitators"""
    __tablename__ = 'practitioners'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core Identity (from calling system)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    
    # Practice Details (collected via calls)
    practice_type = Column(String(100), index=True)
    location = Column(String(255), index=True)
    about_us = Column(Text)
    website_url = Column(String(500))
    social_media_links = Column(JSON)
    
    # Calling System Tracking
    is_contacted = Column(Boolean, default=False, index=True)
    last_contacted_date = Column(DateTime)
    contact_status = Column(String(50), index=True)
    notes = Column(Text)
    
    # CRM Onboarding Integration
    onboarding_step = Column(Integer, default=0, index=True)
    is_active = Column(Boolean, default=True)
    
    # Enhanced Business Details
    student_count = Column(Integer)
    class_types = Column(ARRAY(String))
    current_challenges = Column(ARRAY(String))
    preferred_contact_method = Column(String(50))
    business_details = Column(JSON)
    
    # Website Publishing
    subdomain = Column(String(50), unique=True)
    website_published = Column(Boolean, default=False)
    website_published_at = Column(DateTime)
    website_status = Column(String(20), default='draft')
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    call_transcripts = relationship("CallTranscript", back_populates="practitioner", cascade="all, delete-orphan")
    call_outcomes = relationship("CallOutcome", back_populates="practitioner", cascade="all, delete-orphan")
    insights = relationship("PractitionerInsight", back_populates="practitioner", uselist=False, cascade="all, delete-orphan")
    basic_info = relationship("FacilitatorBasicInfo", back_populates="practitioner", uselist=False, cascade="all, delete-orphan")
    visual_profile = relationship("FacilitatorVisualProfile", back_populates="practitioner", uselist=False, cascade="all, delete-orphan")
    professional_details = relationship("FacilitatorProfessionalDetails", back_populates="practitioner", uselist=False, cascade="all, delete-orphan")
    bio_about = relationship("FacilitatorBioAbout", back_populates="practitioner", uselist=False, cascade="all, delete-orphan")
    work_experience = relationship("FacilitatorWorkExperience", back_populates="practitioner", cascade="all, delete-orphan")
    certifications = relationship("FacilitatorCertification", back_populates="practitioner", cascade="all, delete-orphan")
    offerings = relationship("Offering", back_populates="practitioner", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="practitioner", cascade="all, delete-orphan")
    phone_otps = relationship("PhoneOTP", back_populates="practitioner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Practitioner(id={self.id}, phone={self.phone_number}, name='{self.name}')>"

# =============================================================================
# CALLING SYSTEM TABLES
# =============================================================================

class CallTranscript(Base):
    """Store complete call recordings and transcripts"""
    __tablename__ = 'call_transcripts'
    
    id = Column(Integer, primary_key=True)
    room_name = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    phone_number = Column(String(20), ForeignKey('practitioners.phone_number'), nullable=False, index=True)
    timestamp = Column(DateTime, default=func.current_timestamp())
    call_date = Column(String(20))
    transcript_json = Column(JSON, nullable=False)
    conversation_summary = Column(Text)
    call_duration_seconds = Column(Integer)
    call_status = Column(String(50))
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="call_transcripts")

class CallOutcome(Base):
    """Track call results for AI learning"""
    __tablename__ = 'call_outcomes'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), ForeignKey('practitioners.phone_number'), nullable=False, index=True)
    call_outcome = Column(String(50), nullable=False)
    approach_used = Column(String(50))
    call_duration = Column(Integer)
    objection_type = Column(String(50))
    notes = Column(Text)
    call_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="call_outcomes")

class PractitionerInsight(Base):
    """AI-powered insights for personalized calling"""
    __tablename__ = 'practitioner_insights'
    
    phone_number = Column(String(20), ForeignKey('practitioners.phone_number'), primary_key=True)
    communication_style = Column(String(50))
    primary_objection = Column(String(50))
    successful_approaches = Column(ARRAY(String))
    failed_approaches = Column(ARRAY(String))
    conversion_probability = Column(Float, default=0.5)
    total_calls = Column(Integer, default=0)
    successful_calls = Column(Integer, default=0)
    best_contact_time = Column(String(20))
    avg_call_duration = Column(Integer)
    last_updated = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="insights")

# =============================================================================
# CRM ONBOARDING TABLES (6-Step Process)
# =============================================================================

class FacilitatorBasicInfo(Base):
    """Step 1: Basic facilitator information"""
    __tablename__ = 'facilitator_basic_info'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), unique=True, nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone_number = Column(String(20))
    location = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="basic_info")

class FacilitatorVisualProfile(Base):
    """Step 2: Visual profile"""
    __tablename__ = 'facilitator_visual_profile'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), unique=True, nullable=False)
    banner_urls = Column(ARRAY(String))
    profile_url = Column(String(500))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="visual_profile")

class FacilitatorProfessionalDetails(Base):
    """Step 3: Professional details"""
    __tablename__ = 'facilitator_professional_details'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), unique=True, nullable=False)
    languages = Column(ARRAY(String))
    teaching_styles = Column(ARRAY(String))
    specializations = Column(ARRAY(String))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="professional_details")

class FacilitatorBioAbout(Base):
    """Step 4: Bio and about"""
    __tablename__ = 'facilitator_bio_about'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), unique=True, nullable=False)
    short_bio = Column(Text)
    detailed_intro = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="bio_about")

class FacilitatorWorkExperience(Base):
    """Step 5: Work experience (multiple per practitioner)"""
    __tablename__ = 'facilitator_work_experience'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False)
    job_title = Column(String(255))
    company = Column(String(255))
    duration = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="work_experience")

class FacilitatorCertification(Base):
    """Step 6: Certifications (multiple per practitioner)"""
    __tablename__ = 'facilitator_certifications'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False)
    certificate_name = Column(String(255))
    issuing_organization = Column(String(255))
    date_received = Column(DateTime)
    credential_id = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="certifications")

# =============================================================================
# AUTHENTICATION TABLE
# =============================================================================

class PhoneOTP(Base):
    """Manage OTP-based phone authentication"""
    __tablename__ = 'phone_otps'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), ForeignKey('practitioners.phone_number'), nullable=False, index=True)
    otp = Column(String(10), nullable=False)
    otp_type = Column(String(50), default='verification')
    expires_at = Column(DateTime, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="phone_otps")

# =============================================================================
# SERVICE MANAGEMENT TABLES
# =============================================================================

class Offering(Base):
    """Store courses/services offered by practitioners"""
    __tablename__ = 'offerings'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    basic_info = Column(JSON)
    details = Column(JSON)
    price_schedule = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="offerings")

class Course(Base):
    """Specific courses for promotional calling campaigns"""
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    timing = Column(String(255), nullable=False)
    prerequisite = Column(Text)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="courses")

# =============================================================================
# DATABASE SESSION MANAGEMENT
# =============================================================================

class DatabaseSession:
    """Secure database session manager with connection pooling"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False  # Set to True for SQL debugging
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session with automatic cleanup"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables (for initial setup)"""
        Base.metadata.create_all(bind=self.engine)
    
    def close(self):
        """Close all connections"""
        self.engine.dispose()

# =============================================================================
# SECURE REPOSITORY PATTERN
# =============================================================================

class SecurePractitionerRepository:
    """Secure practitioner operations using ORM"""
    
    def __init__(self, db_session: DatabaseSession):
        self.db_session = db_session
    
    def get_by_phone(self, phone_number: str) -> Optional[Practitioner]:
        """Get practitioner by phone number (SQL injection safe)"""
        with self.db_session.get_session() as session:
            return session.query(Practitioner).filter(
                Practitioner.phone_number == phone_number
            ).first()
    
    def create_practitioner(self, phone_number: str, **kwargs) -> Practitioner:
        """Create new practitioner (SQL injection safe)"""
        with self.db_session.get_session() as session:
            practitioner = Practitioner(phone_number=phone_number, **kwargs)
            session.add(practitioner)
            session.commit()
            session.refresh(practitioner)
            return practitioner
    
    def update_practitioner(self, practitioner_id: int, **kwargs) -> Optional[Practitioner]:
        """Update practitioner (SQL injection safe)"""
        with self.db_session.get_session() as session:
            practitioner = session.query(Practitioner).filter(
                Practitioner.id == practitioner_id
            ).first()
            
            if practitioner:
                for key, value in kwargs.items():
                    if hasattr(practitioner, key):
                        setattr(practitioner, key, value)
                
                practitioner.updated_at = func.now()
                session.commit()
                session.refresh(practitioner)
            
            return practitioner
    
    def get_complete_profile(self, practitioner_id: int) -> Optional[Dict[str, Any]]:
        """Get complete practitioner profile with all related data"""
        with self.db_session.get_session() as session:
            practitioner = session.query(Practitioner).filter(
                Practitioner.id == practitioner_id
            ).first()
            
            if not practitioner:
                return None
            
            # Build complete profile dictionary
            profile = {
                'id': practitioner.id,
                'phone_number': practitioner.phone_number,
                'name': practitioner.name,
                'email': practitioner.email,
                'practice_type': practitioner.practice_type,
                'location': practitioner.location,
                'onboarding_step': practitioner.onboarding_step,
                'website_published': practitioner.website_published,
                'subdomain': practitioner.subdomain,
                'basic_info': practitioner.basic_info.__dict__ if practitioner.basic_info else None,
                'visual_profile': practitioner.visual_profile.__dict__ if practitioner.visual_profile else None,
                'professional_details': practitioner.professional_details.__dict__ if practitioner.professional_details else None,
                'bio_about': practitioner.bio_about.__dict__ if practitioner.bio_about else None,
                'work_experience': [exp.__dict__ for exp in practitioner.work_experience],
                'certifications': [cert.__dict__ for cert in practitioner.certifications],
                'offerings': [off.__dict__ for off in practitioner.offerings],
                'call_summary': {
                    'total_calls': len(practitioner.call_transcripts),
                    'insights': practitioner.insights.__dict__ if practitioner.insights else None
                }
            }
            
            return profile

class SecureCallRepository:
    """Secure call operations using ORM"""
    
    def __init__(self, db_session: DatabaseSession):
        self.db_session = db_session
    
    def store_transcript(self, phone_number: str, transcript_data: Dict[str, Any]) -> CallTranscript:
        """Store call transcript (SQL injection safe)"""
        with self.db_session.get_session() as session:
            transcript = CallTranscript(
                phone_number=phone_number,
                room_name=transcript_data.get('room_name', ''),
                user_id=transcript_data.get('user_id', ''),
                transcript_json=transcript_data.get('transcript_json', {}),
                conversation_summary=transcript_data.get('summary', ''),
                call_duration_seconds=transcript_data.get('duration', 0),
                call_status=transcript_data.get('status', 'completed')
            )
            session.add(transcript)
            session.commit()
            session.refresh(transcript)
            return transcript
    
    def store_outcome(self, phone_number: str, outcome_data: Dict[str, Any]) -> CallOutcome:
        """Store call outcome (SQL injection safe)"""
        with self.db_session.get_session() as session:
            outcome = CallOutcome(
                phone_number=phone_number,
                call_outcome=outcome_data.get('outcome'),
                approach_used=outcome_data.get('approach'),
                call_duration=outcome_data.get('duration'),
                objection_type=outcome_data.get('objection'),
                notes=outcome_data.get('notes', '')
            )
            session.add(outcome)
            session.commit()
            session.refresh(outcome)
            return outcome
    
    def get_call_history(self, phone_number: str, limit: int = 10) -> List[CallTranscript]:
        """Get recent call history (SQL injection safe)"""
        with self.db_session.get_session() as session:
            return session.query(CallTranscript).filter(
                CallTranscript.phone_number == phone_number
            ).order_by(CallTranscript.created_at.desc()).limit(limit).all()

# =============================================================================
# MIGRATION UTILITIES
# =============================================================================

def migrate_from_raw_sql(database_url: str):
    """Utility to verify ORM models match existing database schema"""
    db_session = DatabaseSession(database_url)
    
    try:
        # Test basic connectivity
        with db_session.get_session() as session:
            # Test query to ensure ORM models work with existing data
            practitioners = session.query(Practitioner).limit(5).all()
            print(f"✅ Successfully connected to existing database")
            print(f"✅ Found {len(practitioners)} practitioners in database")
            
            for p in practitioners:
                print(f"   - {p.name} ({p.phone_number})")
        
        return True
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        return False
    finally:
        db_session.close()

if __name__ == "__main__":
    # Test migration with your database
    from config import Config
    success = migrate_from_raw_sql(Config.POSTGRES_URL)
    if success:
        print("🎉 ORM migration is ready to proceed!")
    else:
        print("⚠️  Please check database connectivity")
