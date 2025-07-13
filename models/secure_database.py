"""
Secure Database Manager using SQLAlchemy ORM
Replaces raw SQL with secure, injection-proof operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
from models.orm_models import (
    DatabaseSession, Practitioner, CallTranscript, CallOutcome, 
    PractitionerInsight, FacilitatorBasicInfo, FacilitatorVisualProfile,
    FacilitatorProfessionalDetails, FacilitatorBioAbout, 
    FacilitatorWorkExperience, FacilitatorCertification,
    Offering, Course, PhoneOTP
)
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureDatabaseManager:
    """
    Secure database manager replacing raw SQL with SQLAlchemy ORM
    Provides SQL injection protection and type safety
    """
    
    def __init__(self):
        self.db_session = DatabaseSession(Config.POSTGRES_URL)
        self._test_connection()
    
    def _test_connection(self):
        """Test database connectivity on initialization"""
        try:
            with self.db_session.get_session() as session:
                session.execute("SELECT 1")
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

# =============================================================================
# SECURE PRACTITIONER OPERATIONS
# =============================================================================

class SecureFacilitatorRepository:
    """Secure facilitator/practitioner operations using ORM"""
    
    def __init__(self, db_manager: SecureDatabaseManager):
        self.db_manager = db_manager
    
    # -------------------------------------------------------------------------
    # CORE PRACTITIONER OPERATIONS
    # -------------------------------------------------------------------------
    
    def get_practitioner_by_phone(self, phone_number: str) -> Optional[Practitioner]:
        """Get practitioner by phone number (SQL injection safe)"""
        with self.db_manager.get_session() as session:
            return session.query(Practitioner).filter(
                Practitioner.phone_number == phone_number
            ).first()
    
    def get_practitioner_by_id(self, practitioner_id: int) -> Optional[Practitioner]:
        """Get practitioner by ID (SQL injection safe)"""
        with self.db_manager.get_session() as session:
            return session.query(Practitioner).filter(
                Practitioner.id == practitioner_id
            ).first()
    
    def create_practitioner(self, phone_number: str, **kwargs) -> Practitioner:
        """Create new practitioner (SQL injection safe)"""
        with self.db_manager.get_session() as session:
            # Check if practitioner already exists
            existing = session.query(Practitioner).filter(
                Practitioner.phone_number == phone_number
            ).first()
            
            if existing:
                raise ValueError(f"Practitioner with phone {phone_number} already exists")
            
            practitioner = Practitioner(phone_number=phone_number, **kwargs)
            session.add(practitioner)
            session.commit()
            session.refresh(practitioner)
            return practitioner
    
    def update_practitioner(self, practitioner_id: int, **kwargs) -> Optional[Practitioner]:
        """Update practitioner (SQL injection safe)"""
        with self.db_manager.get_session() as session:
            practitioner = session.query(Practitioner).filter(
                Practitioner.id == practitioner_id
            ).first()
            
            if not practitioner:
                return None
            
            # Update allowed fields only
            allowed_fields = {
                'name', 'email', 'practice_type', 'location', 'about_us',
                'website_url', 'social_media_links', 'is_contacted',
                'last_contacted_date', 'contact_status', 'notes',
                'onboarding_step', 'is_active', 'student_count',
                'class_types', 'current_challenges', 'preferred_contact_method',
                'business_details', 'subdomain', 'website_published',
                'website_published_at', 'website_status'
            }
            
            for key, value in kwargs.items():
                if key in allowed_fields and hasattr(practitioner, key):
                    setattr(practitioner, key, value)
            
            practitioner.updated_at = func.now()
            session.commit()
            session.refresh(practitioner)
            return practitioner
    
    def get_facilitator_profile(self, practitioner_id: int) -> Optional[Dict[str, Any]]:
        """Get complete facilitator profile with all related data"""
        with self.db_manager.get_session() as session:
            practitioner = session.query(Practitioner).filter(
                Practitioner.id == practitioner_id
            ).first()
            
            if not practitioner:
                return None
            
            # Build complete profile
            profile = {
                'id': practitioner.id,
                'phone_number': practitioner.phone_number,
                'name': practitioner.name,
                'email': practitioner.email,
                'practice_type': practitioner.practice_type,
                'location': practitioner.location,
                'about_us': practitioner.about_us,
                'website_url': practitioner.website_url,
                'social_media_links': practitioner.social_media_links,
                'onboarding_step': practitioner.onboarding_step,
                'is_active': practitioner.is_active,
                'website_published': practitioner.website_published,
                'subdomain': practitioner.subdomain,
                'website_status': practitioner.website_status,
                'created_at': practitioner.created_at.isoformat() if practitioner.created_at else None,
                'updated_at': practitioner.updated_at.isoformat() if practitioner.updated_at else None,
            }
            
            # Add related data
            if practitioner.basic_info:
                profile['basic_info'] = {
                    'first_name': practitioner.basic_info.first_name,
                    'last_name': practitioner.basic_info.last_name,
                    'phone_number': practitioner.basic_info.phone_number,
                    'location': practitioner.basic_info.location,
                    'email': practitioner.basic_info.email
                }
            
            if practitioner.visual_profile:
                profile['visual_profile'] = {
                    'banner_urls': practitioner.visual_profile.banner_urls,
                    'profile_url': practitioner.visual_profile.profile_url
                }
            
            if practitioner.professional_details:
                profile['professional_details'] = {
                    'languages': practitioner.professional_details.languages,
                    'teaching_styles': practitioner.professional_details.teaching_styles,
                    'specializations': practitioner.professional_details.specializations
                }
            
            if practitioner.bio_about:
                profile['bio_about'] = {
                    'short_bio': practitioner.bio_about.short_bio,
                    'detailed_intro': practitioner.bio_about.detailed_intro
                }
            
            # Add experience and certifications
            profile['work_experience'] = []
            for exp in practitioner.work_experience:
                profile['work_experience'].append({
                    'id': exp.id,
                    'job_title': exp.job_title,
                    'company': exp.company,
                    'duration': exp.duration,
                    'description': exp.description
                })
            
            profile['certifications'] = []
            for cert in practitioner.certifications:
                profile['certifications'].append({
                    'id': cert.id,
                    'certificate_name': cert.certificate_name,
                    'issuing_organization': cert.issuing_organization,
                    'date_received': cert.date_received.isoformat() if cert.date_received else None,
                    'credential_id': cert.credential_id
                })
            
            return profile
    
    # -------------------------------------------------------------------------
    # ONBOARDING OPERATIONS
    # -------------------------------------------------------------------------
    
    def update_basic_info(self, practitioner_id: int, basic_info_data: Dict[str, Any]) -> bool:
        """Update or create basic info (Step 1)"""
        with self.db_manager.get_session() as session:
            # Check if basic info exists
            basic_info = session.query(FacilitatorBasicInfo).filter(
                FacilitatorBasicInfo.practitioner_id == practitioner_id
            ).first()
            
            if basic_info:
                # Update existing
                for key, value in basic_info_data.items():
                    if hasattr(basic_info, key):
                        setattr(basic_info, key, value)
                basic_info.updated_at = func.now()
            else:
                # Create new
                basic_info = FacilitatorBasicInfo(
                    practitioner_id=practitioner_id,
                    **basic_info_data
                )
                session.add(basic_info)
            
            session.commit()
            return True
    
    def update_visual_profile(self, practitioner_id: int, visual_data: Dict[str, Any]) -> bool:
        """Update or create visual profile (Step 2)"""
        with self.db_manager.get_session() as session:
            visual_profile = session.query(FacilitatorVisualProfile).filter(
                FacilitatorVisualProfile.practitioner_id == practitioner_id
            ).first()
            
            if visual_profile:
                for key, value in visual_data.items():
                    if hasattr(visual_profile, key):
                        setattr(visual_profile, key, value)
                visual_profile.updated_at = func.now()
            else:
                visual_profile = FacilitatorVisualProfile(
                    practitioner_id=practitioner_id,
                    **visual_data
                )
                session.add(visual_profile)
            
            session.commit()
            return True
    
    def update_professional_details(self, practitioner_id: int, professional_data: Dict[str, Any]) -> bool:
        """Update or create professional details (Step 3)"""
        with self.db_manager.get_session() as session:
            professional = session.query(FacilitatorProfessionalDetails).filter(
                FacilitatorProfessionalDetails.practitioner_id == practitioner_id
            ).first()
            
            if professional:
                for key, value in professional_data.items():
                    if hasattr(professional, key):
                        setattr(professional, key, value)
                professional.updated_at = func.now()
            else:
                professional = FacilitatorProfessionalDetails(
                    practitioner_id=practitioner_id,
                    **professional_data
                )
                session.add(professional)
            
            session.commit()
            return True
    
    def update_bio_about(self, practitioner_id: int, bio_data: Dict[str, Any]) -> bool:
        """Update or create bio and about (Step 4)"""
        with self.db_manager.get_session() as session:
            bio_about = session.query(FacilitatorBioAbout).filter(
                FacilitatorBioAbout.practitioner_id == practitioner_id
            ).first()
            
            if bio_about:
                for key, value in bio_data.items():
                    if hasattr(bio_about, key):
                        setattr(bio_about, key, value)
                bio_about.updated_at = func.now()
            else:
                bio_about = FacilitatorBioAbout(
                    practitioner_id=practitioner_id,
                    **bio_data
                )
                session.add(bio_about)
            
            session.commit()
            return True
    
    def add_work_experience(self, practitioner_id: int, experience_data: Dict[str, Any]) -> int:
        """Add work experience (Step 5)"""
        with self.db_manager.get_session() as session:
            experience = FacilitatorWorkExperience(
                practitioner_id=practitioner_id,
                **experience_data
            )
            session.add(experience)
            session.commit()
            session.refresh(experience)
            return experience.id
    
    def add_certification(self, practitioner_id: int, cert_data: Dict[str, Any]) -> int:
        """Add certification (Step 6)"""
        with self.db_manager.get_session() as session:
            certification = FacilitatorCertification(
                practitioner_id=practitioner_id,
                **cert_data
            )
            session.add(certification)
            session.commit()
            session.refresh(certification)
            return certification.id
    
    # -------------------------------------------------------------------------
    # LISTING AND SEARCH OPERATIONS
    # -------------------------------------------------------------------------
    
    def get_practitioners_by_filters(self, filters: Dict[str, Any], 
                                   page: int = 1, page_size: int = 20) -> Tuple[List[Practitioner], int]:
        """Get practitioners with filters and pagination"""
        with self.db_manager.get_session() as session:
            query = session.query(Practitioner)
            
            # Apply filters securely
            if filters.get('practice_type'):
                query = query.filter(Practitioner.practice_type == filters['practice_type'])
            
            if filters.get('location'):
                query = query.filter(Practitioner.location.ilike(f"%{filters['location']}%"))
            
            if filters.get('onboarding_step'):
                query = query.filter(Practitioner.onboarding_step == filters['onboarding_step'])
            
            if filters.get('is_contacted') is not None:
                query = query.filter(Practitioner.is_contacted == filters['is_contacted'])
            
            if filters.get('website_published') is not None:
                query = query.filter(Practitioner.website_published == filters['website_published'])
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            practitioners = query.offset(offset).limit(page_size).all()
            
            return practitioners, total_count

# =============================================================================
# SECURE CALLING OPERATIONS
# =============================================================================

class SecureCallRepository:
    """Secure call operations using ORM"""
    
    def __init__(self, db_manager: SecureDatabaseManager):
        self.db_manager = db_manager
    
    def store_call_transcript(self, phone_number: str, transcript_data: Dict[str, Any]) -> int:
        """Store call transcript securely"""
        with self.db_manager.get_session() as session:
            transcript = CallTranscript(
                phone_number=phone_number,
                room_name=transcript_data.get('room_name', ''),
                user_id=transcript_data.get('user_id', ''),
                call_date=transcript_data.get('call_date', ''),
                transcript_json=transcript_data.get('transcript_json', {}),
                conversation_summary=transcript_data.get('conversation_summary', ''),
                call_duration_seconds=transcript_data.get('call_duration_seconds', 0),
                call_status=transcript_data.get('call_status', 'completed')
            )
            session.add(transcript)
            session.commit()
            session.refresh(transcript)
            return transcript.id
    
    def store_call_outcome(self, phone_number: str, outcome_data: Dict[str, Any]) -> int:
        """Store call outcome securely"""
        with self.db_manager.get_session() as session:
            outcome = CallOutcome(
                phone_number=phone_number,
                call_outcome=outcome_data.get('call_outcome', ''),
                approach_used=outcome_data.get('approach_used', ''),
                call_duration=outcome_data.get('call_duration', 0),
                objection_type=outcome_data.get('objection_type', ''),
                notes=outcome_data.get('notes', '')
            )
            session.add(outcome)
            session.commit()
            session.refresh(outcome)
            return outcome.id
    
    def get_call_history(self, phone_number: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get call history for a phone number"""
        with self.db_manager.get_session() as session:
            transcripts = session.query(CallTranscript).filter(
                CallTranscript.phone_number == phone_number
            ).order_by(desc(CallTranscript.created_at)).limit(limit).all()
            
            history = []
            for transcript in transcripts:
                history.append({
                    'id': transcript.id,
                    'room_name': transcript.room_name,
                    'call_date': transcript.call_date,
                    'call_duration_seconds': transcript.call_duration_seconds,
                    'call_status': transcript.call_status,
                    'conversation_summary': transcript.conversation_summary,
                    'created_at': transcript.created_at.isoformat() if transcript.created_at else None
                })
            
            return history
    
    def update_practitioner_insights(self, phone_number: str, insights_data: Dict[str, Any]) -> bool:
        """Update AI insights for practitioner"""
        with self.db_manager.get_session() as session:
            insights = session.query(PractitionerInsight).filter(
                PractitionerInsight.phone_number == phone_number
            ).first()
            
            if insights:
                # Update existing insights
                for key, value in insights_data.items():
                    if hasattr(insights, key):
                        setattr(insights, key, value)
                insights.last_updated = func.now()
            else:
                # Create new insights
                insights = PractitionerInsight(
                    phone_number=phone_number,
                    **insights_data
                )
                session.add(insights)
            
            session.commit()
            return True

# =============================================================================
# SECURE AUTHENTICATION OPERATIONS
# =============================================================================

class SecureAuthRepository:
    """Secure authentication operations using ORM"""
    
    def __init__(self, db_manager: SecureDatabaseManager):
        self.db_manager = db_manager
    
    def store_otp(self, phone_number: str, otp: str, expires_at: datetime) -> int:
        """Store OTP securely"""
        with self.db_manager.get_session() as session:
            # Remove any existing OTPs for this phone number
            session.query(PhoneOTP).filter(
                PhoneOTP.phone_number == phone_number
            ).delete()
            
            # Create new OTP
            phone_otp = PhoneOTP(
                phone_number=phone_number,
                otp=otp,
                expires_at=expires_at
            )
            session.add(phone_otp)
            session.commit()
            session.refresh(phone_otp)
            return phone_otp.id
    
    def verify_otp(self, phone_number: str, otp: str) -> bool:
        """Verify OTP securely"""
        with self.db_manager.get_session() as session:
            phone_otp = session.query(PhoneOTP).filter(
                and_(
                    PhoneOTP.phone_number == phone_number,
                    PhoneOTP.otp == otp,
                    PhoneOTP.expires_at > func.now(),
                    PhoneOTP.is_verified == False
                )
            ).first()
            
            if phone_otp:
                phone_otp.is_verified = True
                session.commit()
                return True
            
            return False

# =============================================================================
# MIGRATION HELPER
# =============================================================================

def test_orm_migration():
    """Test ORM models against existing database"""
    try:
        db_manager = SecureDatabaseManager()
        facilitator_repo = SecureFacilitatorRepository(db_manager)
        
        # Test basic operations
        practitioners = []
        with db_manager.get_session() as session:
            practitioners = session.query(Practitioner).limit(3).all()
        
        print("✅ ORM Models Working Successfully!")
        print(f"✅ Found {len(practitioners)} practitioners in database")
        
        for p in practitioners:
            print(f"   - {p.name or 'Unknown'} ({p.phone_number})")
        
        # Test repository operations
        if practitioners:
            first_practitioner = practitioners[0]
            profile = facilitator_repo.get_facilitator_profile(first_practitioner.id)
            print(f"✅ Successfully retrieved profile for practitioner {first_practitioner.id}")
        
        db_manager.close_connection()
        return True
        
    except Exception as e:
        print(f"❌ ORM migration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_orm_migration()
    if success:
        print("\n🎉 ORM Migration Ready!")
        print("Your data is safe and ORM models are working correctly.")
    else:
        print("\n⚠️  Please check the error above before proceeding.")
