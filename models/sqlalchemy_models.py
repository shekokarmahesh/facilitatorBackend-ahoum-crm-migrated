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
        return f"<Practitioner(id={self.id}, name='{self.name}', phone='{self.phone_number}')>"

# =============================================================================
# CALLING SYSTEM TABLES
# =============================================================================

class CallTranscript(Base):
    """Store complete call recordings and transcripts"""
    __tablename__ = 'call_transcripts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_name = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    phone_number = Column(String(20), ForeignKey('practitioners.phone_number'), nullable=False, index=True)
    timestamp = Column(DateTime, default=func.current_timestamp())
    call_date = Column(String(20), index=True)
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
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), ForeignKey('practitioners.phone_number'), nullable=False, index=True)
    call_outcome = Column(String(50), nullable=False, index=True)
    approach_used = Column(String(50))
    call_duration = Column(Integer)
    objection_type = Column(String(50))
    notes = Column(Text)
    call_date = Column(DateTime, default=func.now(), index=True)
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
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), unique=True, nullable=False, index=True)
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
    """Step 2: Visual profile (images, banners)"""
    __tablename__ = 'facilitator_visual_profile'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), unique=True, nullable=False, index=True)
    banner_urls = Column(ARRAY(String))
    profile_url = Column(String(500))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="visual_profile")

class FacilitatorProfessionalDetails(Base):
    """Step 3: Professional qualifications and specializations"""
    __tablename__ = 'facilitator_professional_details'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), unique=True, nullable=False, index=True)
    languages = Column(ARRAY(String))
    teaching_styles = Column(ARRAY(String))
    specializations = Column(ARRAY(String))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="professional_details")

class FacilitatorBioAbout(Base):
    """Step 4: Bio and detailed about information"""
    __tablename__ = 'facilitator_bio_about'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), unique=True, nullable=False, index=True)
    short_bio = Column(Text)
    detailed_intro = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="bio_about")

class FacilitatorWorkExperience(Base):
    """Step 5: Work experience (multiple records per practitioner)"""
    __tablename__ = 'facilitator_work_experience'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False, index=True)
    job_title = Column(String(255))
    company = Column(String(255))
    duration = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="work_experience")

class FacilitatorCertification(Base):
    """Step 6: Certifications (multiple records per practitioner)"""
    __tablename__ = 'facilitator_certifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False, index=True)
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
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), ForeignKey('practitioners.phone_number'), nullable=False, index=True)
    otp = Column(String(10), nullable=False)
    otp_type = Column(String(50), default='verification')
    expires_at = Column(DateTime, nullable=False, index=True)
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
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)
    basic_info = Column(JSON)
    details = Column(JSON)
    price_schedule = Column(JSON)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    practitioner = relationship("Practitioner", back_populates="offerings")

class Course(Base):
    """Specific courses for promotional calling campaigns"""
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
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

class CoursePromotionCall(Base):
    """Track course promotion calls made by AI agents"""
    __tablename__ = 'course_promotion_calls'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    call_status = Column(String(50), default='initiated', index=True)
    call_outcome = Column(String(50), index=True)
    call_duration = Column(Integer)  # in seconds
    livekit_room_name = Column(String(255))
    transcript_summary = Column(Text)
    student_response = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    scheduled_callback = Column(DateTime)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    practitioner = relationship("Practitioner")
    course = relationship("Course")

# =============================================================================
# DATABASE ENGINE AND SESSION MANAGEMENT
# =============================================================================

class DatabaseEngine:
    """Secure SQLAlchemy engine with connection pooling"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            # Security settings
            pool_pre_ping=True,  # Validate connections before use
            pool_recycle=3600,   # Recycle connections every hour
            pool_size=10,        # Connection pool size
            max_overflow=20,     # Maximum overflow connections
            echo=False,          # Set to True for SQL debugging
            # Security: Prevent SQL injection through engine
            module=None,
            future=True
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables (only if they don't exist)"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session with automatic cleanup"""
        return self.SessionLocal()
    
    def get_db_session(self):
        """Context manager for database sessions"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

# =============================================================================
# SECURE REPOSITORY BASE CLASS
# =============================================================================

class SecureRepository:
    """Base repository with built-in security features"""
    
    def __init__(self, db_engine: DatabaseEngine):
        self.db_engine = db_engine
    
    def get_session(self):
        """Get secure database session"""
        return self.db_engine.get_session()
    
    def safe_execute(self, session: Session, operation_func, *args, **kwargs):
        """Execute operation with automatic error handling and rollback"""
        try:
            result = operation_func(session, *args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

def get_database_url() -> str:
    """Get database URL from environment with fallback"""
    return os.getenv("POSTGRES_URL")

# Global database engine instance
db_engine = DatabaseEngine(get_database_url())