"""
Secure Database Manager using SQLAlchemy ORM
Replaces raw SQL with secure, injection-proof operations
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ARRAY, JSON, ForeignKey, text, func, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import json
from config import Config
from typing import Optional, Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    
    # NEW: CRM Platform Onboarding Status
    crm_onboarding_completed = Column(Boolean, default=False, index=True)
    crm_first_login_date = Column(DateTime)
    crm_onboarding_completed_date = Column(DateTime)
    
    # Website Publishing (existing columns)
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
# CRM ONBOARDING TABLES (6-Step PROCESS)
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
# COURSE PROMOTION TABLES (For Calling CAMPAIGNS)
# =============================================================================

class CoursePromotionCall(Base):
    """Track course promotion calls"""
    __tablename__ = 'course_promotion_calls'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    call_status = Column(String(50), default='initiated', index=True)
    livekit_room_name = Column(String(255))
    call_start_time = Column(DateTime)
    call_end_time = Column(DateTime)
    call_duration = Column(Integer)  # in seconds
    student_name = Column(String(255))
    student_email = Column(String(255))
    call_outcome = Column(String(50))
    conversion_status = Column(String(50))
    follow_up_required = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    practitioner = relationship("Practitioner")
    course = relationship("Course")

class CoursePromotionLead(Base):
    """Store potential leads for course promotion"""
    __tablename__ = 'course_promotion_leads'
    
    id = Column(Integer, primary_key=True)
    practitioner_id = Column(Integer, ForeignKey('practitioners.id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    name = Column(String(255))
    phone_number = Column(String(20), nullable=False, index=True)
    email = Column(String(255))
    age_group = Column(String(50))
    experience_level = Column(String(50))
    location = Column(String(255))
    preferred_timing = Column(String(255))
    source = Column(String(100))  # how they found us
    interest_level = Column(Integer, default=5)  # 1-10 scale
    contact_status = Column(String(50), default='new', index=True)
    last_contacted = Column(DateTime)
    conversion_probability = Column(Integer, default=50)  # percentage
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    practitioner = relationship("Practitioner")
    course = relationship("Course")
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
# SECURE DATABASE MANAGER (Replacement for old DatabaseManager)
# =============================================================================

class DatabaseManager:
    """
    Secure database manager using SQLAlchemy ORM
    Drop-in replacement for the old raw SQL version
    """
    
    def __init__(self):
        self.db_session = DatabaseSession(Config.POSTGRES_URL)
        self._test_connection()
        logger.info("✅ Secure DatabaseManager initialized with SQLAlchemy ORM")
    
    def _test_connection(self):
        """Test database connectivity on initialization"""
        try:
            with self.db_session.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("✅ Database connection established successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session for manual operations"""
        return self.db_session.get_session()
    
    def close_connection(self):
        """Close database connections"""
        self.db_session.close()
    
    # Legacy method compatibility for existing code
    def execute_query(self, query, params=None):
        """Legacy compatibility - use ORM methods instead"""
        logger.warning("⚠️  execute_query is deprecated. Use ORM methods instead.")
        with self.get_session() as session:
            if params:
                return session.execute(query, params)
            else:
                return session.execute(query)
    
    # =============================================================================
    # GENERAL CALLING HELPER METHODS
    # =============================================================================
    
    def search_practitioners(self, query: str) -> List[Dict[str, Any]]:
        """Search practitioners by phone, name, or practice type"""
        try:
            with self.get_session() as session:
                practitioners = session.query(Practitioner).filter(
                    or_(
                        Practitioner.phone_number.ilike(f'%{query}%'),
                        Practitioner.name.ilike(f'%{query}%'),
                        Practitioner.practice_type.ilike(f'%{query}%'),
                        Practitioner.location.ilike(f'%{query}%')
                    )
                ).limit(20).all()
                
                return [
                    {
                        'id': p.id,
                        'name': p.name,
                        'phone_number': p.phone_number,
                        'email': p.email,
                        'practice_type': p.practice_type,
                        'location': p.location,
                        'is_contacted': p.is_contacted,
                        'contact_status': p.contact_status,
                        'last_contacted_date': p.last_contacted_date.isoformat() if p.last_contacted_date else None,
                        'onboarding_step': p.onboarding_step,
                        'website_published': p.website_published,
                        'subdomain': p.subdomain
                    }
                    for p in practitioners
                ]
        except Exception as e:
            logger.error(f"Error searching practitioners: {e}")
            return []
    
    def get_practitioner_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get detailed practitioner information by phone number"""
        try:
            with self.get_session() as session:
                practitioner = session.query(Practitioner).filter(
                    Practitioner.phone_number == phone_number
                ).first()
                
                if not practitioner:
                    return None
                
                return {
                    'id': practitioner.id,
                    'name': practitioner.name,
                    'phone_number': practitioner.phone_number,
                    'email': practitioner.email,
                    'practice_type': practitioner.practice_type,
                    'location': practitioner.location,
                    'about_us': practitioner.about_us,
                    'website_url': practitioner.website_url,
                    'social_media_links': practitioner.social_media_links,
                    'is_contacted': practitioner.is_contacted,
                    'last_contacted_date': practitioner.last_contacted_date.isoformat() if practitioner.last_contacted_date else None,
                    'contact_status': practitioner.contact_status,
                    'notes': practitioner.notes,
                    'onboarding_step': practitioner.onboarding_step,
                    'is_active': practitioner.is_active,
                    'subdomain': practitioner.subdomain,
                    'website_published': practitioner.website_published,
                    'website_published_at': practitioner.website_published_at.isoformat() if practitioner.website_published_at else None,
                    'website_status': practitioner.website_status,
                    'created_at': practitioner.created_at.isoformat() if practitioner.created_at else None,
                    'updated_at': practitioner.updated_at.isoformat() if practitioner.updated_at else None
                }
        except Exception as e:
            logger.error(f"Error getting practitioner by phone: {e}")
            return None
    
    def update_practitioner_contact_status(self, phone_number: str, status: str, notes: str = None) -> bool:
        """Update practitioner contact status after a general call"""
        try:
            with self.get_session() as session:
                practitioner = session.query(Practitioner).filter(
                    Practitioner.phone_number == phone_number
                ).first()
                
                if practitioner:
                    practitioner.is_contacted = True
                    practitioner.last_contacted_date = datetime.now()
                    practitioner.contact_status = status
                    if notes:
                        practitioner.notes = notes
                    
                    session.commit()
                    logger.info(f"Updated contact status for {phone_number}: {status}")
                    return True
                else:
                    logger.warning(f"Practitioner not found for phone: {phone_number}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating contact status: {e}")
            return False
    
    def create_or_update_practitioner(self, phone_number: str, practitioner_data: Dict[str, Any]) -> bool:
        """Create new practitioner or update existing one"""
        try:
            with self.get_session() as session:
                practitioner = session.query(Practitioner).filter(
                    Practitioner.phone_number == phone_number
                ).first()
                
                if practitioner:
                    # Update existing practitioner
                    for key, value in practitioner_data.items():
                        if hasattr(practitioner, key) and value is not None:
                            setattr(practitioner, key, value)
                    practitioner.updated_at = datetime.now()
                else:
                    # Create new practitioner
                    practitioner_data['phone_number'] = phone_number
                    practitioner = Practitioner(**practitioner_data)
                    session.add(practitioner)
                
                session.commit()
                logger.info(f"{'Updated' if practitioner.id else 'Created'} practitioner: {phone_number}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating/updating practitioner: {e}")
            return False
    
    def get_uncontacted_practitioners(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of practitioners who haven't been contacted yet"""
        try:
            with self.get_session() as session:
                practitioners = session.query(Practitioner).filter(
                    or_(
                        Practitioner.is_contacted == False,
                        Practitioner.is_contacted.is_(None)
                    )
                ).limit(limit).all()
                
                return [
                    {
                        'id': p.id,
                        'name': p.name,
                        'phone_number': p.phone_number,
                        'email': p.email,
                        'practice_type': p.practice_type,
                        'location': p.location,
                        'about_us': p.about_us[:200] + '...' if p.about_us and len(p.about_us) > 200 else p.about_us
                    }
                    for p in practitioners
                ]
        except Exception as e:
            logger.error(f"Error getting uncontacted practitioners: {e}")
            return []

# =============================================================================
# TEST FUNCTION
# =============================================================================

def test_orm_migration():
    """Test ORM models against existing database"""
    try:
        db_manager = DatabaseManager()
        
        # Test basic operations
        practitioners = []
        with db_manager.get_session() as session:
            practitioners = session.query(Practitioner).limit(3).all()
        
        print("✅ ORM Models Working Successfully!")
        print(f"✅ Found {len(practitioners)} practitioners in database")
        
        for p in practitioners:
            print(f"   - {p.name or 'Unknown'} ({p.phone_number})")
        
        db_manager.close_connection()
        return True
        
    except Exception as e:
        logger.error(f"Error updating facilitator profile: {e}")
        return False

# =============================================================================
# SECURE COURSE CALLING REPOSITORY
# =============================================================================

class CourseCallingRepository:
    """Secure course calling operations using ORM"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_course_with_practitioner(self, course_id: int, practitioner_id: int) -> Optional[Dict[str, Any]]:
        """Get course details with practitioner verification - SECURE"""
        with self.db_manager.get_session() as session:
            course = session.query(Course).filter(
                Course.id == course_id,
                Course.practitioner_id == practitioner_id,
                Course.is_active == True
            ).first()
            
            if not course:
                return None
            
            practitioner = session.query(Practitioner).filter(
                Practitioner.id == practitioner_id
            ).first()
            
            return {
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'timing': course.timing,
                    'prerequisite': course.prerequisite,
                    'description': course.description,
                    'practitioner_id': course.practitioner_id
                },
                'practitioner': {
                    'name': practitioner.name,
                    'phone_number': practitioner.phone_number,
                    'email': practitioner.email
                } if practitioner else None
            }
    
    def log_course_promotion_call(self, practitioner_id: int, course_id: int, phone_number: str) -> Optional[int]:
        """Log course promotion call - SECURE"""
        try:
            with self.db_manager.get_session() as session:
                call = CoursePromotionCall(
                    practitioner_id=practitioner_id,
                    course_id=course_id,
                    phone_number=phone_number,
                    call_status='initiated'
                )
                session.add(call)
                session.commit()
                session.refresh(call)
                return call.id
        except Exception as e:
            logger.error(f"Error logging course promotion call: {e}")
            return None
    
    def update_call_status(self, call_id: int, status: str, **additional_data) -> bool:
        """Update call status and additional data - SECURE"""
        try:
            with self.db_manager.get_session() as session:
                call = session.query(CoursePromotionCall).filter(
                    CoursePromotionCall.id == call_id
                ).first()
                
                if call:
                    call.call_status = status
                    for key, value in additional_data.items():
                        if hasattr(call, key):
                            setattr(call, key, value)
                    call.updated_at = func.now()
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating call status: {e}")
            return False
    
    def get_course_promotion_calls(self, practitioner_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get course promotion calls for practitioner - SECURE"""
        with self.db_manager.get_session() as session:
            calls = session.query(CoursePromotionCall).filter(
                CoursePromotionCall.practitioner_id == practitioner_id
            ).order_by(CoursePromotionCall.created_at.desc()).limit(limit).all()
            
            return [{
                'id': call.id,
                'course_id': call.course_id,
                'phone_number': call.phone_number,
                'call_status': call.call_status,
                'call_start_time': call.call_start_time.isoformat() if call.call_start_time else None,
                'call_end_time': call.call_end_time.isoformat() if call.call_end_time else None,
                'call_duration': call.call_duration,
                'student_name': call.student_name,
                'student_email': call.student_email,
                'call_outcome': call.call_outcome,
                'conversion_status': call.conversion_status,
                'follow_up_required': call.follow_up_required,
                'notes': call.notes,
                'created_at': call.created_at.isoformat() if call.created_at else None
            } for call in calls]
    
    def add_course_promotion_lead(self, practitioner_id: int, course_id: int, lead_data: Dict[str, Any]) -> Optional[int]:
        """Add new course promotion lead - SECURE"""
        try:
            with self.db_manager.get_session() as session:
                lead = CoursePromotionLead(
                    practitioner_id=practitioner_id,
                    course_id=course_id,
                    **lead_data
                )
                session.add(lead)
                session.commit()
                session.refresh(lead)
                return lead.id
        except Exception as e:
            logger.error(f"Error adding course promotion lead: {e}")
            return None
    
    def get_course_promotion_leads(self, practitioner_id: int, course_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get course promotion leads - SECURE"""
        with self.db_manager.get_session() as session:
            query = session.query(CoursePromotionLead).filter(
                CoursePromotionLead.practitioner_id == practitioner_id,
                CoursePromotionLead.is_active == True
            )
            
            if course_id:
                query = query.filter(CoursePromotionLead.course_id == course_id)
            
            leads = query.order_by(CoursePromotionLead.created_at.desc()).limit(limit).all()
            
            return [{
                'id': lead.id,
                'course_id': lead.course_id,
                'name': lead.name,
                'phone_number': lead.phone_number,
                'email': lead.email,
                'age_group': lead.age_group,
                'experience_level': lead.experience_level,
                'location': lead.location,
                'preferred_timing': lead.preferred_timing,
                'source': lead.source,
                'interest_level': lead.interest_level,
                'contact_status': lead.contact_status,
                'last_contacted': lead.last_contacted.isoformat() if lead.last_contacted else None,
                'conversion_probability': lead.conversion_probability,
                'notes': lead.notes,
                'created_at': lead.created_at.isoformat() if lead.created_at else None
            } for lead in leads]

    def verify_course_ownership(self, course_id: int, practitioner_id: int) -> bool:
        """Verify course belongs to practitioner - SECURE"""
        with self.db_manager.get_session() as session:
            course = session.query(Course).filter(
                Course.id == course_id,
                Course.practitioner_id == practitioner_id
            ).first()
            return course is not None
    
    def get_call_analytics(self, course_id: int, practitioner_id: int) -> Dict[str, Any]:
        """Get call analytics for course - SECURE"""
        with self.db_manager.get_session() as session:
            # Verify ownership first
            if not self.verify_course_ownership(course_id, practitioner_id):
                return None
            
            # Get basic call stats
            stats = session.query(
                func.count(CoursePromotionCall.id).label('total_calls'),
                func.count(case((CoursePromotionCall.call_outcome == 'successful', 1))).label('successful_calls'),
                func.count(case((CoursePromotionCall.conversion_status == 'converted', 1))).label('conversions'),
                func.avg(CoursePromotionCall.call_duration).label('avg_duration')
            ).filter(
                CoursePromotionCall.course_id == course_id,
                CoursePromotionCall.practitioner_id == practitioner_id
            ).first()
            
            total_calls = stats.total_calls or 0
            successful_calls = stats.successful_calls or 0
            conversions = stats.conversions or 0
            avg_duration = float(stats.avg_duration or 0)
            
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
            conversion_rate = (conversions / total_calls * 100) if total_calls > 0 else 0
            
            return {
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'conversions': conversions,
                'success_rate': round(success_rate, 2),
                'conversion_rate': round(conversion_rate, 2),
                'avg_call_duration': round(avg_duration, 2)
            }
    
    def get_overall_analytics(self, practitioner_id: int) -> Dict[str, Any]:
        """Get overall calling analytics for practitioner - SECURE"""
        with self.db_manager.get_session() as session:
            # Overall stats
            stats = session.query(
                func.count(CoursePromotionCall.id).label('total_calls'),
                func.count(case((CoursePromotionCall.call_outcome == 'successful', 1))).label('successful_calls'),
                func.count(case((CoursePromotionCall.conversion_status == 'converted', 1))).label('conversions'),
                func.avg(CoursePromotionCall.call_duration).label('avg_duration')
            ).filter(
                CoursePromotionCall.practitioner_id == practitioner_id
            ).first()
            
            total_calls = stats.total_calls or 0
            successful_calls = stats.successful_calls or 0
            conversions = stats.conversions or 0
            avg_duration = float(stats.avg_duration or 0)
            
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
            conversion_rate = (conversions / total_calls * 100) if total_calls > 0 else 0
            
            # Top performing courses
            top_courses = session.query(
                Course.id,
                Course.title,
                func.count(CoursePromotionCall.id).label('call_count'),
                func.count(case((CoursePromotionCall.conversion_status == 'converted', 1))).label('conversions')
            ).join(CoursePromotionCall).filter(
                CoursePromotionCall.practitioner_id == practitioner_id
            ).group_by(Course.id, Course.title).order_by(
                func.count(case((CoursePromotionCall.conversion_status == 'converted', 1))).desc()
            ).limit(5).all()
            
            return {
                'total_calls': total_calls,
                'successful_calls': successful_calls,
                'conversions': conversions,
                'success_rate': round(success_rate, 2),
                'conversion_rate': round(conversion_rate, 2),
                'avg_call_duration': round(avg_duration, 2),
                'top_courses': [{
                    'id': course.id,
                    'title': course.title,
                    'call_count': course.call_count,
                    'conversions': course.conversions
                } for course in top_courses]
            }

    def verify_call_ownership(self, call_id: int, practitioner_id: int) -> bool:
        """Verify call belongs to practitioner - SECURE"""
        with self.db_manager.get_session() as session:
            call = session.query(CoursePromotionCall).filter(
                CoursePromotionCall.id == call_id,
                CoursePromotionCall.practitioner_id == practitioner_id
            ).first()
            return call is not None
    
    def get_call_practitioner_id(self, call_id: int) -> Optional[int]:
        """Get practitioner ID for a call - SECURE"""
        with self.db_manager.get_session() as session:
            call = session.query(CoursePromotionCall).filter(
                CoursePromotionCall.id == call_id
            ).first()
            return call.practitioner_id if call else None

# =============================================================================
# FACILITATOR REPOSITORY CLASS - SECURE ORM VERSION
# =============================================================================

class FacilitatorRepository:
    """Secure ORM-based facilitator operations repository"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_facilitator_offerings(self, facilitator_id: int) -> List[Dict[str, Any]]:
        """Get all active offerings for a facilitator - SECURE"""
        with self.db_manager.get_session() as session:
            offerings = session.query(Offering).filter(
                Offering.practitioner_id == facilitator_id,
                Offering.is_active == True
            ).all()
            
            return [{
                'id': offering.id,
                'title': offering.title,
                'description': offering.description,
                'category': offering.category,
                'basic_info': offering.basic_info,
                'details': offering.details,
                'price_schedule': offering.price_schedule,
                'is_active': offering.is_active,
                'created_at': offering.created_at.isoformat() if offering.created_at else None,
                'updated_at': offering.updated_at.isoformat() if offering.updated_at else None
            } for offering in offerings]
    
    def create_offering(self, facilitator_id: int, offering_data: Dict[str, Any]) -> int:
        """Create new offering - SECURE"""
        with self.db_manager.get_session() as session:
            offering = Offering(
                practitioner_id=facilitator_id,
                title=offering_data.get('title'),
                description=offering_data.get('description'),
                category=offering_data.get('category'),
                basic_info=offering_data.get('basic_info'),
                details=offering_data.get('details'),
                price_schedule=offering_data.get('price_schedule'),
                is_active=True
            )
            
            session.add(offering)
            session.commit()
            session.refresh(offering)
            return offering.id
    
    def verify_offering_ownership(self, facilitator_id: int, offering_id: int) -> bool:
        """Verify offering belongs to facilitator - SECURE"""
        with self.db_manager.get_session() as session:
            offering = session.query(Offering).filter(
                Offering.id == offering_id,
                Offering.practitioner_id == facilitator_id
            ).first()
            return offering is not None
    
    def update_offering(self, offering_id: int, facilitator_id: int, update_data: Dict[str, Any]) -> bool:
        """Update offering - SECURE"""
        with self.db_manager.get_session() as session:
            offering = session.query(Offering).filter(
                Offering.id == offering_id,
                Offering.practitioner_id == facilitator_id
            ).first()
            if not offering:
                return False
            
            for key, value in update_data.items():
                if hasattr(offering, key):
                    setattr(offering, key, value)
            
            offering.updated_at = func.current_timestamp()
            session.commit()
            return True
    
    def get_offering_statistics(self, facilitator_id: int) -> Dict[str, Any]:
        """Get offering statistics - SECURE"""
        with self.db_manager.get_session() as session:
            # Get category statistics
            category_stats = session.query(
                Offering.category,
                func.count(Offering.id).label('count')
            ).filter(
                Offering.practitioner_id == facilitator_id
            ).group_by(Offering.category).all()
            
            # Get overall statistics
            overall = session.query(
                func.count(Offering.id).label('total'),
                func.count(case((Offering.is_active == True, 1))).label('active'),
                func.count(case((Offering.is_active == False, 1))).label('inactive'),
                func.count(func.distinct(Offering.category)).label('categories')
            ).filter(Offering.practitioner_id == facilitator_id).first()
            
            return {
                'overall': {
                    'total_offerings': overall.total or 0,
                    'active_offerings': overall.active or 0,
                    'inactive_offerings': overall.inactive or 0,
                    'unique_categories': overall.categories or 0
                },
                'categories': [
                    {'category': cat.category, 'count': cat.count}
                    for cat in category_stats if cat.category
                ]
            }
    
    def deactivate_offering(self, offering_id: int) -> bool:
        """Deactivate offering (soft delete) - SECURE"""
        with self.db_manager.get_session() as session:
            offering = session.query(Offering).filter(Offering.id == offering_id).first()
            if not offering:
                return False
            
            offering.is_active = False
            offering.updated_at = func.current_timestamp()
            session.commit()
            return True
    
    def activate_offering(self, offering_id: int) -> bool:
        """Activate offering - SECURE"""
        with self.db_manager.get_session() as session:
            offering = session.query(Offering).filter(Offering.id == offering_id).first()
            if not offering:
                return False
            
            offering.is_active = True
            offering.updated_at = func.current_timestamp()
            session.commit()
            return True
    
    def get_website_status(self, facilitator_id: int) -> Optional[Dict[str, Any]]:
        """Get website publishing status - SECURE"""
        with self.db_manager.get_session() as session:
            practitioner = session.query(Practitioner).filter(
                Practitioner.id == facilitator_id
            ).first()
            
            if not practitioner:
                return None
            
            return {
                'subdomain': practitioner.subdomain,
                'is_published': practitioner.website_published or False,
                'status': practitioner.website_status or 'draft',
                'published_at': practitioner.website_published_at.isoformat() if practitioner.website_published_at else None
            }
    
    def get_practitioner_by_subdomain(self, subdomain: str) -> Optional[Dict[str, Any]]:
        """Get practitioner by subdomain - SECURE"""
        with self.db_manager.get_session() as session:
            practitioner = session.query(Practitioner).filter(
                Practitioner.subdomain == subdomain,
                Practitioner.website_published == True,
                Practitioner.is_active == True
            ).first()
            
            if not practitioner:
                return None
            
            return {
                'id': practitioner.id,
                'name': practitioner.name,
                'email': practitioner.email,
                'subdomain': practitioner.subdomain,
                'website_published': practitioner.website_published,
                'is_active': practitioner.is_active
            }
    
    def check_subdomain_exists(self, subdomain: str) -> bool:
        """Check if subdomain already exists - SECURE"""
        with self.db_manager.get_session() as session:
            count = session.query(Practitioner).filter(
                func.lower(Practitioner.subdomain) == func.lower(subdomain)
            ).count()
            return count > 0
    
    def update_facilitator_website(self, website_data: Dict[str, Any]) -> bool:
        """Update facilitator website settings - SECURE"""
        with self.db_manager.get_session() as session:
            try:
                facilitator_id = website_data.get('facilitator_id')
                subdomain = website_data.get('subdomain')
                is_published = website_data.get('is_published', False)
                
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == facilitator_id
                ).first()
                
                if not practitioner:
                    raise ValueError(f"Practitioner {facilitator_id} not found")
                
                # Update website fields
                practitioner.subdomain = subdomain.lower() if subdomain else None
                practitioner.website_published = is_published
                practitioner.website_status = 'live' if is_published else 'draft'
                practitioner.website_published_at = func.current_timestamp() if is_published else None
                practitioner.updated_at = func.current_timestamp()
                
                session.commit()
                logger.info(f"✅ Updated website settings for facilitator {facilitator_id}")
                return True
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error updating website settings: {e}")
                raise
    
    # =============================================================================
    # OTP AUTHENTICATION METHODS
    # =============================================================================
    def create_otp(self, phone_number: str, otp: str) -> Optional[int]:
        """Create new OTP for phone authentication - SECURE"""
        try:
            from datetime import datetime, timedelta
            with self.db_manager.get_session() as session:
                # Mark existing OTPs as used
                session.query(PhoneOTP).filter(
                    PhoneOTP.phone_number == phone_number,
                    PhoneOTP.is_verified == False
                ).update({PhoneOTP.is_verified: True})
                # Add new OTP
                expires_at = datetime.now() + timedelta(minutes=10)
                new_otp = PhoneOTP(
                    phone_number=phone_number,
                    otp=otp,
                    otp_type='verification',
                    expires_at=expires_at,
                    is_verified=False
                )
                session.add(new_otp)
                session.commit()
                session.refresh(new_otp)
                return new_otp.id
        except Exception as e:
            logger.error(f"Error creating OTP: {e}")
            return None

    def verify_otp_and_get_user_status(self, phone_number: str, otp: str) -> Dict[str, Any]:
        """Verify OTP and determine if user needs onboarding - ENHANCED"""
        try:
            from datetime import datetime
            with self.db_manager.get_session() as session:
                otp_record = session.query(PhoneOTP).filter(
                    PhoneOTP.phone_number == phone_number,
                    PhoneOTP.otp == otp,
                    PhoneOTP.is_verified == False,
                    PhoneOTP.expires_at > datetime.now()
                ).first()
                if not otp_record:
                    return {"success": False, "error": "Invalid or expired OTP"}
                
                otp_record.is_verified = True
                practitioner = session.query(Practitioner).filter(
                    Practitioner.phone_number == phone_number
                ).first()
                
                if not practitioner:
                    # Truly new user - create account
                    practitioner = Practitioner(
                        phone_number=phone_number,
                        onboarding_step=0,
                        crm_onboarding_completed=False,
                        crm_first_login_date=func.now(),
                        is_active=True,
                        contact_status='new'
                    )
                    session.add(practitioner)
                    session.commit()
                    session.refresh(practitioner)
                    
                    return {
                        "success": True,
                        "is_new_user": True,
                        "needs_onboarding": True,
                        "practitioner_id": practitioner.id,
                        "onboarding_step": 0,
                        "crm_onboarding_completed": False
                    }
                else:
                    # Existing practitioner - check CRM onboarding status
                    needs_onboarding = not practitioner.crm_onboarding_completed
                    
                    # Update first login date if not set
                    if not practitioner.crm_first_login_date:
                        practitioner.crm_first_login_date = func.now()
                        session.commit()
                    
                    return {
                        "success": True,
                        "is_new_user": False,
                        "needs_onboarding": needs_onboarding,
                        "practitioner_id": practitioner.id,
                        "onboarding_step": practitioner.onboarding_step,
                        "crm_onboarding_completed": practitioner.crm_onboarding_completed,
                        "has_calling_data": practitioner.is_contacted,
                        "calling_data": {
                            "name": practitioner.name,
                            "email": practitioner.email,
                            "practice_type": practitioner.practice_type,
                            "location": practitioner.location,
                            "contact_status": practitioner.contact_status
                        } if practitioner.is_contacted else None
                    }
                    
        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return {"success": False, "error": "Failed to verify OTP"}

    def create_facilitator_account(self, phone_number: str, email: Optional[str] = None) -> Optional[int]:
        """Create new facilitator account - SECURE"""
        try:
            with self.db_manager.get_session() as session:
                existing = session.query(Practitioner).filter(
                    Practitioner.phone_number == phone_number
                ).first()
                if existing:
                    return existing.id
                practitioner = Practitioner(
                    phone_number=phone_number,
                    email=email,
                    onboarding_step=0,
                    is_active=True,
                    contact_status='new'
                )
                session.add(practitioner)
                session.commit()
                session.refresh(practitioner)
                return practitioner.id
        except Exception as e:
            logger.error(f"Error creating facilitator account: {e}")
            return None

    def get_facilitator_onboarding_status(self, practitioner_id: int) -> Dict[str, Any]:
        """Get facilitator onboarding status and data - SECURE"""
        try:
            with self.db_manager.get_session() as session:
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == practitioner_id
                ).first()
                
                if not practitioner:
                    return {"error": "Practitioner not found"}
                
                # Get completion status for each step
                basic_info = session.query(FacilitatorBasicInfo).filter(
                    FacilitatorBasicInfo.practitioner_id == practitioner_id
                ).first()
                
                visual_profile = session.query(FacilitatorVisualProfile).filter(
                    FacilitatorVisualProfile.practitioner_id == practitioner_id
                ).first()
                
                professional_details = session.query(FacilitatorProfessionalDetails).filter(
                    FacilitatorProfessionalDetails.practitioner_id == practitioner_id
                ).first()
                
                bio_about = session.query(FacilitatorBioAbout).filter(
                    FacilitatorBioAbout.practitioner_id == practitioner_id
                ).first()
                
                work_experience = session.query(FacilitatorWorkExperience).filter(
                    FacilitatorWorkExperience.practitioner_id == practitioner_id
                ).count()
                
                certifications = session.query(FacilitatorCertification).filter(
                    FacilitatorCertification.practitioner_id == practitioner_id
                ).count()
                
                return {
                    "current_step": practitioner.onboarding_step,
                    "completed_steps": {
                        "basic_info": basic_info is not None,
                        "visual_profile": visual_profile is not None,
                        "professional_details": professional_details is not None,
                        "bio_about": bio_about is not None,
                        "work_experience": work_experience > 0,
                        "certifications": certifications > 0
                    },
                    "practitioner": {
                        "id": practitioner.id,
                        "phone_number": practitioner.phone_number,
                        "email": practitioner.email,
                        "name": practitioner.name,
                        "onboarding_step": practitioner.onboarding_step
                    }
                }
        except Exception as e:
            logger.error(f"Error getting facilitator onboarding status: {e}")
            return {"error": "Failed to get onboarding status"}

    def save_basic_info(self, practitioner_id: int, basic_info_data: Dict[str, Any]) -> bool:
        """Save basic info for facilitator - ENHANCED with pre-fill support"""
        try:
            with self.db_manager.get_session() as session:
                # Check if basic info already exists
                existing = session.query(FacilitatorBasicInfo).filter(
                    FacilitatorBasicInfo.practitioner_id == practitioner_id
                ).first()
                
                if existing:
                    # Update existing
                    for key, value in basic_info_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = func.now()
                else:
                    # Create new
                    basic_info = FacilitatorBasicInfo(
                        practitioner_id=practitioner_id,
                        **basic_info_data
                    )
                    session.add(basic_info)
                
                # Update practitioner name and onboarding step
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == practitioner_id
                ).first()
                
                if practitioner:
                    # Update name if provided
                    if 'first_name' in basic_info_data and 'last_name' in basic_info_data:
                        practitioner.name = f"{basic_info_data['first_name']} {basic_info_data['last_name']}"
                    if 'email' in basic_info_data:
                        practitioner.email = basic_info_data['email']
                    if practitioner.onboarding_step < 1:
                        practitioner.onboarding_step = 1
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving basic info: {e}")
            return False

    def get_prefilled_basic_info(self, practitioner_id: int) -> Dict[str, Any]:
        """Get pre-filled basic info from calling system data - NEW"""
        try:
            with self.db_manager.get_session() as session:
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == practitioner_id
                ).first()
                
                if not practitioner:
                    return {}
                
                # Extract name parts if available
                first_name = ""
                last_name = ""
                if practitioner.name:
                    name_parts = practitioner.name.split(' ', 1)
                    first_name = name_parts[0] if len(name_parts) > 0 else ""
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                
                return {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": practitioner.email,
                    "location": practitioner.location,
                    "phone_number": practitioner.phone_number,
                    "has_calling_data": practitioner.is_contacted,
                    "practice_type": practitioner.practice_type
                }
                
        except Exception as e:
            logger.error(f"Error getting pre-filled basic info: {e}")
            return {}

    def save_visual_profile(self, practitioner_id: int, visual_data: Dict[str, Any]) -> bool:
        """Save visual profile for facilitator - SECURE"""
        try:
            with self.db_manager.get_session() as session:
                # Check if visual profile already exists
                existing = session.query(FacilitatorVisualProfile).filter(
                    FacilitatorVisualProfile.practitioner_id == practitioner_id
                ).first()
                
                if existing:
                    # Update existing
                    for key, value in visual_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = func.now()
                else:
                    # Create new
                    visual_profile = FacilitatorVisualProfile(
                        practitioner_id=practitioner_id,
                        **visual_data
                    )
                    session.add(visual_profile)
                
                # Update onboarding step
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == practitioner_id
                ).first()
                
                if practitioner and practitioner.onboarding_step < 2:
                    practitioner.onboarding_step = 2
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving visual profile: {e}")
            return False

    def save_professional_details(self, practitioner_id: int, professional_data: Dict[str, Any]) -> bool:
        """Save professional details for facilitator - SECURE"""
        try:
            with self.db_manager.get_session() as session:
                # Check if professional details already exist
                existing = session.query(FacilitatorProfessionalDetails).filter(
                    FacilitatorProfessionalDetails.practitioner_id == practitioner_id
                ).first()
                
                if existing:
                    # Update existing
                    for key, value in professional_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = func.now()
                else:
                    # Create new
                    professional_details = FacilitatorProfessionalDetails(
                        practitioner_id=practitioner_id,
                        **professional_data
                    )
                    session.add(professional_details)
                
                # Update onboarding step
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == practitioner_id
                ).first()
                
                if practitioner and practitioner.onboarding_step < 3:
                    practitioner.onboarding_step = 3
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving professional details: {e}")
            return False

    def save_bio_about(self, practitioner_id: int, bio_data: Dict[str, Any]) -> bool:
        """Save bio and about info for facilitator - SECURE"""
        try:
            with self.db_manager.get_session() as session:
                # Check if bio info already exists
                existing = session.query(FacilitatorBioAbout).filter(
                    FacilitatorBioAbout.practitioner_id == practitioner_id
                ).first()
                
                if existing:
                    # Update existing
                    for key, value in bio_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = func.now()
                else:
                    # Create new
                    bio_about = FacilitatorBioAbout(
                        practitioner_id=practitioner_id,
                        **bio_data
                    )
                    session.add(bio_about)
                
                # Update onboarding step
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == practitioner_id
                ).first()
                
                if practitioner and practitioner.onboarding_step < 4:
                    practitioner.onboarding_step = 4
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving bio about: {e}")
            return False

    def save_experience_certifications(self, practitioner_id: int, experience_data: List[Dict[str, Any]], certification_data: List[Dict[str, Any]]) -> bool:
        """Save experience and certifications - Complete onboarding - ENHANCED"""
        try:
            with self.db_manager.get_session() as session:
                # Clear existing records
                session.query(FacilitatorWorkExperience).filter(
                    FacilitatorWorkExperience.practitioner_id == practitioner_id
                ).delete()
                
                session.query(FacilitatorCertification).filter(
                    FacilitatorCertification.practitioner_id == practitioner_id
                ).delete()
                
                # Add work experiences
                for exp in experience_data:
                    work_exp = FacilitatorWorkExperience(
                        practitioner_id=practitioner_id,
                        job_title=exp.get('job_title'),
                        company=exp.get('company'),
                        duration=exp.get('duration'),
                        description=exp.get('description')
                    )
                    session.add(work_exp)
                
                # Add certifications
                for cert in certification_data:
                    certification = FacilitatorCertification(
                        practitioner_id=practitioner_id,
                        certificate_name=cert.get('certificate_name'),
                        issuing_organization=cert.get('issuing_organization'),
                        date_received=cert.get('date_received'),
                        credential_id=cert.get('credential_id')
                    )
                    session.add(certification)
                
                # Update practitioner onboarding step and mark CRM onboarding as completed
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == practitioner_id
                ).first()
                
                if practitioner:
                    practitioner.onboarding_step = 6  # Complete all steps
                    practitioner.crm_onboarding_completed = True  # NEW: Mark CRM onboarding complete
                    practitioner.crm_onboarding_completed_date = func.now()  # NEW: Set completion date
                    practitioner.updated_at = func.now()
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving experience and certifications: {e}")
            return False

    def get_complete_facilitator_profile(self, practitioner_id: int) -> Optional[Dict[str, Any]]:
        """Get complete facilitator profile data - SECURE"""
        try:
            with self.db_manager.get_session() as session:
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == practitioner_id
                ).first()
                
                if not practitioner:
                    return None
                
                # Get all related data
                basic_info = session.query(FacilitatorBasicInfo).filter(
                    FacilitatorBasicInfo.practitioner_id == practitioner_id
                ).first()
                
                visual_profile = session.query(FacilitatorVisualProfile).filter(
                    FacilitatorVisualProfile.practitioner_id == practitioner_id
                ).first()
                
                professional_details = session.query(FacilitatorProfessionalDetails).filter(
                    FacilitatorProfessionalDetails.practitioner_id == practitioner_id
                ).first()
                
                bio_about = session.query(FacilitatorBioAbout).filter(
                    FacilitatorBioAbout.practitioner_id == practitioner_id
                ).first()
                
                work_experience = session.query(FacilitatorWorkExperience).filter(
                    FacilitatorWorkExperience.practitioner_id == practitioner_id
                ).all()
                
                certifications = session.query(FacilitatorCertification).filter(
                    FacilitatorCertification.practitioner_id == practitioner_id
                ).all()
                
                return {
                    "practitioner": {
                        "id": practitioner.id,
                        "phone_number": practitioner.phone_number,
                        "email": practitioner.email,
                        "name": practitioner.name,
                        "subdomain": practitioner.subdomain,
                        "onboarding_step": practitioner.onboarding_step,
                        "website_published": practitioner.website_published
                    },
                    "basic_info": {
                        "first_name": basic_info.first_name,
                        "last_name": basic_info.last_name,
                        "phone_number": basic_info.phone_number,
                        "location": basic_info.location,
                        "email": basic_info.email
                    } if basic_info else None,
                    "visual_profile": {
                        "banner_urls": visual_profile.banner_urls,
                        "profile_url": visual_profile.profile_url
                    } if visual_profile else None,
                    "professional_details": {
                        "languages": professional_details.languages,
                        "teaching_styles": professional_details.teaching_styles,
                        "specializations": professional_details.specializations
                    } if professional_details else None,
                    "bio_about": {
                        "short_bio": bio_about.short_bio,
                        "detailed_intro": bio_about.detailed_intro
                    } if bio_about else None,
                    "work_experience": [{
                        "id": exp.id,
                        "job_title": exp.job_title,
                        "company": exp.company,
                        "duration": exp.duration,
                        "description": exp.description
                    } for exp in work_experience],
                    "certifications": [{
                        "id": cert.id,
                        "certificate_name": cert.certificate_name,
                        "issuing_organization": cert.issuing_organization,
                        "date_received": cert.date_received.isoformat() if cert.date_received else None,
                        "credential_id": cert.credential_id
                    } for cert in certifications]
                }
                
        except Exception as e:
            logger.error(f"Error getting complete facilitator profile: {e}")
            return None

# =============================================================================
# STUDENT REPOSITORY CLASS - SECURE ORM VERSION
# =============================================================================

class StudentRepository:
    """Secure ORM-based student operations repository"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_students(self, facilitator_id: int) -> List[Dict[str, Any]]:
        """Get all students for a facilitator - SECURE"""
        with self.db_manager.get_session() as session:
            # For now, return students from course promotion leads
            leads = session.query(CoursePromotionLead).filter(
                CoursePromotionLead.practitioner_id == facilitator_id,
                CoursePromotionLead.is_active == True
            ).all()
            
            return [{
                'id': lead.id,
                'name': lead.name,
                'phone_number': lead.phone_number,
                'email': lead.email,
                'age_group': lead.age_group,
                'experience_level': lead.experience_level,
                'location': lead.location,
                'preferred_timing': lead.preferred_timing,
                'source': lead.source,
                'interest_level': lead.interest_level,
                'contact_status': lead.contact_status,
                'last_contacted': lead.last_contacted.isoformat() if lead.last_contacted else None,
                'conversion_probability': lead.conversion_probability,
                'notes': lead.notes,
                'created_at': lead.created_at.isoformat() if lead.created_at else None,
                'updated_at': lead.updated_at.isoformat() if lead.updated_at else None
            } for lead in leads]
    
    def create_student(self, facilitator_id: int, student_data: Dict[str, Any]) -> int:
        """Create new student/lead - SECURE"""
        with self.db_manager.get_session() as session:
            student = CoursePromotionLead(
                practitioner_id=facilitator_id,
                name=student_data.get('name'),
                phone_number=student_data.get('phone_number'),
                email=student_data.get('email'),
                age_group=student_data.get('age_group'),
                experience_level=student_data.get('experience_level'),
                location=student_data.get('location'),
                preferred_timing=student_data.get('preferred_timing'),
                source=student_data.get('source', 'manual'),
                interest_level=student_data.get('interest_level', 5),
                contact_status=student_data.get('contact_status', 'new'),
                conversion_probability=student_data.get('conversion_probability', 50),
                notes=student_data.get('notes'),
                is_active=True
            )
            
            session.add(student)
            session.commit()
            session.refresh(student)
            return student.id
    
    def update_student(self, student_id: int, facilitator_id: int, update_data: Dict[str, Any]) -> bool:
        """Update student - SECURE"""
        with self.db_manager.get_session() as session:
            student = session.query(CoursePromotionLead).filter(
                CoursePromotionLead.id == student_id,
                CoursePromotionLead.practitioner_id == facilitator_id
            ).first()
            
            if not student:
                return False
            
            for key, value in update_data.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            
            student.updated_at = func.current_timestamp()
            session.commit()
            return True
    
    def delete_student(self, student_id: int, facilitator_id: int) -> bool:
        """Soft delete student - SECURE"""
        with self.db_manager.get_session() as session:
            student = session.query(CoursePromotionLead).filter(
                CoursePromotionLead.id == student_id,
                CoursePromotionLead.practitioner_id == facilitator_id
            ).first()
            
            if not student:
                return False
            
            student.is_active = False
            student.updated_at = func.current_timestamp()
            session.commit()
            return True
    
    def verify_student_ownership(self, facilitator_id: int, student_id: int) -> bool:
        """Verify student belongs to facilitator - SECURE"""
        with self.db_manager.get_session() as session:
            student = session.query(CoursePromotionLead).filter(
                CoursePromotionLead.id == student_id,
                CoursePromotionLead.practitioner_id == facilitator_id
            ).first()
            return student is not None

# =============================================================================
# COURSE REPOSITORY CLASS - SECURE ORM VERSION
# =============================================================================

class CourseRepository:
    """Secure ORM-based course operations repository"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_courses(self, facilitator_id: int) -> List[Dict[str, Any]]:
        """Get all courses for a facilitator - SECURE"""
        with self.db_manager.get_session() as session:
            courses = session.query(Course).filter(
                Course.practitioner_id == facilitator_id,
                Course.is_active == True
            ).all()
            
            return [{
                'id': course.id,
                'title': course.title,
                'timing': course.timing,
                'prerequisite': course.prerequisite,
                'description': course.description,
                'is_active': course.is_active,
                'created_at': course.created_at.isoformat() if course.created_at else None,
                'updated_at': course.updated_at.isoformat() if course.updated_at else None
            } for course in courses]
    
    def get_course(self, course_id: int, facilitator_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific course for a facilitator - SECURE"""
        with self.db_manager.get_session() as session:
            course = session.query(Course).filter(
                Course.id == course_id,
                Course.practitioner_id == facilitator_id,
                Course.is_active == True
            ).first()
            
            if not course:
                return None
            
            return {
                'id': course.id,
                'title': course.title,
                'timing': course.timing,
                'prerequisite': course.prerequisite,
                'description': course.description,
                'is_active': course.is_active,
                'created_at': course.created_at.isoformat() if course.created_at else None,
                'updated_at': course.updated_at.isoformat() if course.updated_at else None
            }
    
    def create_course(self, facilitator_id: int, course_data: Dict[str, Any]) -> int:
        """Create new course - SECURE"""
        with self.db_manager.get_session() as session:
            course = Course(
                practitioner_id=facilitator_id,
                title=course_data.get('title'),
                timing=course_data.get('timing'),
                prerequisite=course_data.get('prerequisite'),
                description=course_data.get('description'),
                is_active=True
            )
            
            session.add(course)
            session.commit()
            session.refresh(course)
            return course.id
    
    def update_course(self, course_id: int, facilitator_id: int, update_data: Dict[str, Any]) -> bool:
        """Update course - SECURE"""
        with self.db_manager.get_session() as session:
            course = session.query(Course).filter(
                Course.id == course_id,
                Course.practitioner_id == facilitator_id,
                Course.is_active == True
            ).first()
            if not course:
                return False
            
            for key, value in update_data.items():
                if hasattr(course, key):
                    setattr(course, key, value)
            
            course.updated_at = func.current_timestamp()
            session.commit()
            return True
    
    def delete_course(self, course_id: int, facilitator_id: int) -> bool:
        """Soft delete course - SECURE"""
        with self.db_manager.get_session() as session:
            course = session.query(Course).filter(
                Course.id == course_id,
                Course.practitioner_id == facilitator_id,
                Course.is_active == True
            ).first()
            if not course:
                return False
            
            course.is_active = False
            course.updated_at = func.current_timestamp()
            session.commit()
            return True
    
    def verify_course_ownership(self, facilitator_id: int, course_id: int) -> bool:
        """Verify course belongs to facilitator - SECURE"""
        with self.db_manager.get_session() as session:
            course = session.query(Course).filter(
                Course.id == course_id,
                Course.practitioner_id == facilitator_id
            ).first()
            return course is not None

# =============================================================================
# CAMPAIGN REPOSITORY CLASS - SECURE ORM VERSION
# =============================================================================

class CampaignRepository:
    """Secure ORM-based campaign operations repository"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_campaigns(self, facilitator_id: int) -> List[Dict[str, Any]]:
        """Get all campaigns for a facilitator - SECURE"""
        with self.db_manager.get_session() as session:
            # For now, return course promotion calls as campaigns
            campaigns = session.query(CoursePromotionCall).filter(
                CoursePromotionCall.practitioner_id == facilitator_id
            ).all()
            
            return [{
                'id': campaign.id,
                'course_id': campaign.course_id,
                'phone_number': campaign.phone_number,
                'call_status': campaign.call_status,
                'call_start_time': campaign.call_start_time.isoformat() if campaign.call_start_time else None,
                'call_end_time': campaign.call_end_time.isoformat() if campaign.call_end_time else None,
                'call_duration': campaign.call_duration,
                'student_name': campaign.student_name,
                'student_email': campaign.student_email,
                'call_outcome': campaign.call_outcome,
                'conversion_status': campaign.conversion_status,
                'follow_up_required': campaign.follow_up_required,
                'notes': campaign.notes,
                'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
                'updated_at': campaign.updated_at.isoformat() if campaign.updated_at else None
            } for campaign in campaigns]
    
    def create_campaign(self, facilitator_id: int, campaign_data: Dict[str, Any]) -> int:
        """Create new campaign - SECURE"""
        with self.db_manager.get_session() as session:
            campaign = CoursePromotionCall(
                practitioner_id=facilitator_id,
                course_id=campaign_data.get('course_id'),
                phone_number=campaign_data.get('phone_number'),
                call_status=campaign_data.get('call_status', 'initiated'),
                student_name=campaign_data.get('student_name'),
                student_email=campaign_data.get('student_email'),
                call_outcome=campaign_data.get('call_outcome'),
                conversion_status=campaign_data.get('conversion_status'),
                follow_up_required=campaign_data.get('follow_up_required', False),
                notes=campaign_data.get('notes')
            )
            
            session.add(campaign)
            session.flush()
            return campaign.id
    
    def update_campaign(self, campaign_id: int, facilitator_id: int, update_data: Dict[str, Any]) -> bool:
        """Update campaign - SECURE"""
        with self.db_manager.get_session() as session:
            campaign = session.query(CoursePromotionCall).filter(
                CoursePromotionCall.id == campaign_id,
                CoursePromotionCall.practitioner_id == facilitator_id
            ).first()
            
            if not campaign:
                return False
            
            for key, value in update_data.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)
            
            campaign.updated_at = func.current_timestamp()
            session.commit()
            return True
    
    def delete_campaign(self, campaign_id: int, facilitator_id: int) -> bool:
        """Delete campaign - SECURE"""
        with self.db_manager.get_session() as session:
            campaign = session.query(CoursePromotionCall).filter(
                CoursePromotionCall.id == campaign_id,
                CoursePromotionCall.practitioner_id == facilitator_id
            ).first()
            
            if not campaign:
                return False
            
            session.delete(campaign)
            session.commit()
            return True
    
    def update_campaign_status(self, campaign_id: int, status: str) -> bool:
        """Update campaign status - SECURE"""
        with self.db_manager.get_session() as session:
            campaign = session.query(CoursePromotionCall).filter(
                CoursePromotionCall.id == campaign_id
            ).first()
            
            if not campaign:
                return False
            
            campaign.call_status = status
            campaign.updated_at = func.current_timestamp()
            session.commit()
            return True
    
    def get_campaign_targets(self, campaign_id: int) -> List[Dict[str, Any]]:
        """Get target students for a campaign - SECURE"""
        with self.db_manager.get_session() as session:
            # Get active students as potential targets
            targets = session.query(CoursePromotionLead).filter(
                CoursePromotionLead.is_active == True
            ).all()
            
            return [{
                'id': target.id,
                'name': target.name,
                'phone_number': target.phone_number,
                'email': target.email,
                'student_type': target.student_type,
                'status': target.status,
                'created_at': target.created_at.isoformat() if target.created_at else None
            } for target in targets]
