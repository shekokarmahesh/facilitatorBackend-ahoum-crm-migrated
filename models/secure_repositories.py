"""
Secure Repository Implementations using SQLAlchemy ORM
Replaces raw SQL operations with secure ORM patterns
"""

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import json

from .sqlalchemy_models import (
    DatabaseEngine, SecureRepository,
    Practitioner, CallTranscript, CallOutcome, PractitionerInsight,
    FacilitatorBasicInfo, FacilitatorVisualProfile, FacilitatorProfessionalDetails,
    FacilitatorBioAbout, FacilitatorWorkExperience, FacilitatorCertification,
    PhoneOTP, Offering, Course
)

logger = logging.getLogger(__name__)

class SecureFacilitatorRepository(SecureRepository):
    """Secure CRUD operations for practitioners/facilitators using ORM"""
    
    def create_facilitator(self, phone_number: str, email: str = None, name: str = None) -> int:
        """
        Create new practitioner - SECURE VERSION
        
        OLD (VULNERABLE):
        cursor.execute(f"INSERT INTO practitioners (phone_number, email, name) VALUES ('{phone_number}', '{email}', '{name}')")
        
        NEW (SECURE):
        Uses ORM with automatic escaping and validation
        """
        with self.db_engine.get_db_session() as session:
            try:
                # Check if practitioner already exists
                existing = session.query(Practitioner).filter(
                    Practitioner.phone_number == phone_number
                ).first()
                
                if existing:
                    raise ValueError(f"Practitioner with phone {phone_number} already exists")
                
                # Create new practitioner with ORM (automatically secure)
                practitioner = Practitioner(
                    phone_number=phone_number,
                    email=email,
                    name=name,
                    is_active=True
                )
                
                session.add(practitioner)
                session.flush()  # Get ID without committing
                
                practitioner_id = practitioner.id
                logger.info(f"✅ Created practitioner {practitioner_id} for {phone_number}")
                return practitioner_id
                
            except IntegrityError as e:
                session.rollback()
                logger.error(f"❌ Integrity error creating practitioner: {e}")
                raise ValueError("Phone number already exists or constraint violation")
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error creating practitioner: {e}")
                raise

    def get_facilitator_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Get practitioner by phone - SECURE VERSION
        
        OLD (VULNERABLE):
        cursor.execute(f"SELECT * FROM practitioners WHERE phone_number = '{phone_number}'")
        
        NEW (SECURE):
        Uses ORM with parameter binding and relationship loading
        """
        with self.db_engine.get_db_session() as session:
            try:
                practitioner = session.query(Practitioner).filter(
                    Practitioner.phone_number == phone_number
                ).first()
                
                if not practitioner:
                    return None
                
                # Convert to dictionary with relationships
                return {
                    'id': practitioner.id,
                    'phone_number': practitioner.phone_number,
                    'name': practitioner.name,
                    'email': practitioner.email,
                    'practice_type': practitioner.practice_type,
                    'location': practitioner.location,
                    'about_us': practitioner.about_us,
                    'website_url': practitioner.website_url,
                    'social_media_links': practitioner.social_media_links,
                    'is_contacted': practitioner.is_contacted,
                    'contact_status': practitioner.contact_status,
                    'onboarding_step': practitioner.onboarding_step,
                    'is_active': practitioner.is_active,
                    'created_at': practitioner.created_at.isoformat() if practitioner.created_at else None,
                    'updated_at': practitioner.updated_at.isoformat() if practitioner.updated_at else None
                }
                
            except Exception as e:
                logger.error(f"❌ Error getting practitioner by phone {phone_number}: {e}")
                raise

    def get_facilitator_profile(self, facilitator_id: int) -> Optional[Dict[str, Any]]:
        """
        Get complete facilitator profile with all related data - SECURE VERSION
        
        OLD (VULNERABLE):
        Multiple raw SQL queries with string concatenation
        
        NEW (SECURE):
        Single ORM query with eager loading of relationships
        """
        with self.db_engine.get_db_session() as session:
            try:
                # Use eager loading to get all related data in one query
                practitioner = session.query(Practitioner).options(
                    joinedload(Practitioner.basic_info),
                    joinedload(Practitioner.visual_profile),
                    joinedload(Practitioner.professional_details),
                    joinedload(Practitioner.bio_about),
                    selectinload(Practitioner.work_experience),
                    selectinload(Practitioner.certifications),
                    joinedload(Practitioner.insights)
                ).filter(Practitioner.id == facilitator_id).first()
                
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
                    'about_us': practitioner.about_us,
                    'website_url': practitioner.website_url,
                    'social_media_links': practitioner.social_media_links,
                    'onboarding_step': practitioner.onboarding_step,
                    'is_active': practitioner.is_active,
                    'subdomain': practitioner.subdomain,
                    'website_published': practitioner.website_published,
                    'website_status': practitioner.website_status,
                    
                    # Related data
                    'basic_info': self._serialize_basic_info(practitioner.basic_info),
                    'visual_profile': self._serialize_visual_profile(practitioner.visual_profile),
                    'professional_details': self._serialize_professional_details(practitioner.professional_details),
                    'bio_about': self._serialize_bio_about(practitioner.bio_about),
                    'experience': [self._serialize_experience(exp) for exp in practitioner.work_experience],
                    'certifications': [self._serialize_certification(cert) for cert in practitioner.certifications],
                    'insights': self._serialize_insights(practitioner.insights)
                }
                
                return profile
                
            except Exception as e:
                logger.error(f"❌ Error getting facilitator profile {facilitator_id}: {e}")
                raise

    def update_facilitator_profile(self, facilitator_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update facilitator profile - SECURE VERSION
        
        OLD (VULNERABLE):
        Dynamic SQL string building with user input
        
        NEW (SECURE):
        ORM with automatic validation and type checking
        """
        with self.db_engine.get_db_session() as session:
            try:
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == facilitator_id
                ).first()
                
                if not practitioner:
                    raise ValueError(f"Practitioner {facilitator_id} not found")
                
                # Update main practitioner fields (if provided)
                if 'name' in update_data:
                    practitioner.name = update_data['name']
                if 'email' in update_data:
                    practitioner.email = update_data['email']
                
                # Update related tables using ORM relationships
                if 'basic_info' in update_data:
                    self._update_basic_info(session, practitioner, update_data['basic_info'])
                
                if 'visual_profile' in update_data:
                    self._update_visual_profile(session, practitioner, update_data['visual_profile'])
                
                if 'professional_details' in update_data:
                    self._update_professional_details(session, practitioner, update_data['professional_details'])
                
                if 'bio_about' in update_data:
                    self._update_bio_about(session, practitioner, update_data['bio_about'])
                
                if 'experience' in update_data:
                    self._update_experience(session, practitioner, update_data['experience'])
                
                if 'certifications' in update_data:
                    self._update_certifications(session, practitioner, update_data['certifications'])
                
                # Update timestamp
                practitioner.updated_at = datetime.utcnow()
                
                logger.info(f"✅ Updated facilitator profile {facilitator_id}")
                return True
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error updating facilitator profile {facilitator_id}: {e}")
                raise

    def create_offering(self, facilitator_id: int, offering_data: Dict[str, Any]) -> int:
        """
        Create new offering - SECURE VERSION
        
        OLD (VULNERABLE):
        String concatenation with JSON data
        
        NEW (SECURE):
        ORM with automatic JSON serialization and validation
        """
        with self.db_engine.get_db_session() as session:
            try:
                # Verify practitioner exists
                practitioner = session.query(Practitioner).filter(
                    Practitioner.id == facilitator_id
                ).first()
                
                if not practitioner:
                    raise ValueError(f"Practitioner {facilitator_id} not found")
                
                # Create offering with ORM (automatically secure)
                offering = Offering(
                    practitioner_id=facilitator_id,
                    title=offering_data.get('title'),
                    description=offering_data.get('description'),
                    category=offering_data.get('category'),
                    basic_info=offering_data.get('basic_info'),  # Automatically serialized as JSON
                    details=offering_data.get('details'),
                    price_schedule=offering_data.get('price_schedule'),
                    is_active=True
                )
                
                session.add(offering)
                session.flush()
                
                offering_id = offering.id
                logger.info(f"✅ Created offering {offering_id} for practitioner {facilitator_id}")
                return offering_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error creating offering: {e}")
                raise

    def search_facilitators(self, filters: Dict[str, Any] = None, page: int = 1, limit: int = 10) -> Tuple[List[Dict], int]:
        """
        Search facilitators with filters - SECURE VERSION
        
        OLD (VULNERABLE):
        Dynamic WHERE clause building with string concatenation
        
        NEW (SECURE):
        ORM query builder with automatic parameter binding
        """
        with self.db_engine.get_db_session() as session:
            try:
                # Start with base query
                query = session.query(Practitioner)
                
                # Apply filters using ORM (automatically secure)
                if filters:
                    if 'name' in filters and filters['name']:
                        query = query.filter(Practitioner.name.ilike(f"%{filters['name']}%"))
                    
                    if 'email' in filters and filters['email']:
                        query = query.filter(Practitioner.email.ilike(f"%{filters['email']}%"))
                    
                    if 'practice_type' in filters and filters['practice_type']:
                        query = query.filter(Practitioner.practice_type == filters['practice_type'])
                    
                    if 'location' in filters and filters['location']:
                        query = query.filter(Practitioner.location.ilike(f"%{filters['location']}%"))
                    
                    if 'is_active' in filters:
                        query = query.filter(Practitioner.is_active == filters['is_active'])
                
                # Get total count for pagination
                total_count = query.count()
                
                # Apply pagination
                offset = (page - 1) * limit
                facilitators = query.offset(offset).limit(limit).all()
                
                # Convert to dictionary format
                results = []
                for facilitator in facilitators:
                    results.append({
                        'id': facilitator.id,
                        'name': facilitator.name,
                        'phone_number': facilitator.phone_number,
                        'email': facilitator.email,
                        'practice_type': facilitator.practice_type,
                        'location': facilitator.location,
                        'is_active': facilitator.is_active,
                        'onboarding_step': facilitator.onboarding_step,
                        'created_at': facilitator.created_at.isoformat() if facilitator.created_at else None
                    })
                
                logger.info(f"✅ Search returned {len(results)} facilitators (page {page})")
                return results, total_count
                
            except Exception as e:
                logger.error(f"❌ Error searching facilitators: {e}")
                raise

    # Helper methods for relationship updates
    def _update_basic_info(self, session: Session, practitioner: Practitioner, basic_info_data: Dict):
        """Update basic info using ORM relationship"""
        if not practitioner.basic_info:
            basic_info = FacilitatorBasicInfo(practitioner_id=practitioner.id)
            session.add(basic_info)
            practitioner.basic_info = basic_info
        
        if 'first_name' in basic_info_data:
            practitioner.basic_info.first_name = basic_info_data['first_name']
        if 'last_name' in basic_info_data:
            practitioner.basic_info.last_name = basic_info_data['last_name']
        if 'location' in basic_info_data:
            practitioner.basic_info.location = basic_info_data['location']
        if 'email' in basic_info_data:
            practitioner.basic_info.email = basic_info_data['email']
        
        practitioner.basic_info.updated_at = datetime.utcnow()

    def _serialize_basic_info(self, basic_info: Optional[FacilitatorBasicInfo]) -> Optional[Dict]:
        """Convert basic info to dictionary"""
        if not basic_info:
            return None
        return {
            'first_name': basic_info.first_name,
            'last_name': basic_info.last_name,
            'phone_number': basic_info.phone_number,
            'location': basic_info.location,
            'email': basic_info.email
        }

    def _serialize_visual_profile(self, visual_profile: Optional[FacilitatorVisualProfile]) -> Optional[Dict]:
        """Convert visual profile to dictionary"""
        if not visual_profile:
            return None
        return {
            'banner_urls': visual_profile.banner_urls,
            'profile_url': visual_profile.profile_url
        }

    def _serialize_professional_details(self, professional_details: Optional[FacilitatorProfessionalDetails]) -> Optional[Dict]:
        """Convert professional details to dictionary"""
        if not professional_details:
            return None
        return {
            'languages': professional_details.languages,
            'teaching_styles': professional_details.teaching_styles,
            'specializations': professional_details.specializations
        }

    def _serialize_bio_about(self, bio_about: Optional[FacilitatorBioAbout]) -> Optional[Dict]:
        """Convert bio about to dictionary"""
        if not bio_about:
            return None
        return {
            'short_bio': bio_about.short_bio,
            'detailed_intro': bio_about.detailed_intro
        }

    def _serialize_experience(self, experience: FacilitatorWorkExperience) -> Dict:
        """Convert work experience to dictionary"""
        return {
            'id': experience.id,
            'job_title': experience.job_title,
            'company': experience.company,
            'duration': experience.duration,
            'description': experience.description
        }

    def _serialize_certification(self, certification: FacilitatorCertification) -> Dict:
        """Convert certification to dictionary"""
        return {
            'id': certification.id,
            'certificate_name': certification.certificate_name,
            'issuing_organization': certification.issuing_organization,
            'date_received': certification.date_received.isoformat() if certification.date_received else None,
            'credential_id': certification.credential_id
        }

    def _serialize_insights(self, insights: Optional[PractitionerInsight]) -> Optional[Dict]:
        """Convert insights to dictionary"""
        if not insights:
            return None
        return {
            'communication_style': insights.communication_style,
            'primary_objection': insights.primary_objection,
            'successful_approaches': insights.successful_approaches,
            'failed_approaches': insights.failed_approaches,
            'conversion_probability': insights.conversion_probability,
            'total_calls': insights.total_calls,
            'successful_calls': insights.successful_calls,
            'best_contact_time': insights.best_contact_time
        }

class SecureCallingRepository(SecureRepository):
    """Secure operations for calling system using ORM"""
    
    def store_call_transcript(self, transcript_data: Dict[str, Any], phone_number: str = None, 
                            call_duration: int = None, call_status: str = None) -> int:
        """
        Store call transcript - SECURE VERSION
        
        OLD (VULNERABLE):
        JSON string manipulation with potential injection
        
        NEW (SECURE):
        ORM with automatic JSON handling and foreign key validation
        """
        with self.db_engine.get_db_session() as session:
            try:
                # Create transcript with ORM (automatically secure)
                transcript = CallTranscript(
                    room_name=transcript_data.get("room_name"),
                    user_id=transcript_data.get("user_id"),
                    phone_number=phone_number,
                    call_date=transcript_data.get("timestamp"),
                    transcript_json=transcript_data.get("transcript"),  # Automatically serialized
                    conversation_summary=self._extract_conversation_summary(transcript_data),
                    call_duration_seconds=call_duration,
                    call_status=call_status
                )
                
                session.add(transcript)
                session.flush()
                
                transcript_id = transcript.id
                logger.info(f"✅ Stored call transcript {transcript_id} for {phone_number}")
                return transcript_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error storing call transcript: {e}")
                raise

    def store_call_outcome(self, phone_number: str, outcome: str, approach_used: str = None,
                          duration: int = None, objection_type: str = None, notes: str = None) -> bool:
        """
        Store call outcome - SECURE VERSION
        
        OLD (VULNERABLE):
        Raw SQL with parameter concatenation
        
        NEW (SECURE):
        ORM with automatic validation and foreign key checking
        """
        with self.db_engine.get_db_session() as session:
            try:
                # Create call outcome with ORM
                outcome_record = CallOutcome(
                    phone_number=phone_number,
                    call_outcome=outcome,
                    approach_used=approach_used,
                    call_duration=duration,
                    objection_type=objection_type,
                    notes=notes
                )
                
                session.add(outcome_record)
                
                # Update practitioner insights
                self._update_practitioner_insights(session, phone_number, outcome, approach_used, objection_type)
                
                logger.info(f"✅ Stored call outcome {outcome} for {phone_number}")
                return True
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error storing call outcome: {e}")
                raise

    def get_practitioner_context(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Get practitioner context for intelligent calling - SECURE VERSION
        
        OLD (VULNERABLE):
        Complex raw SQL with multiple joins and string building
        
        NEW (SECURE):
        Single ORM query with eager loading and automatic parameter binding
        """
        with self.db_engine.get_db_session() as session:
            try:
                # Get practitioner with all related data in one secure query
                practitioner = session.query(Practitioner).options(
                    joinedload(Practitioner.insights),
                    selectinload(Practitioner.call_transcripts).options(
                        joinedload(CallTranscript.practitioner)
                    ),
                    selectinload(Practitioner.call_outcomes)
                ).filter(Practitioner.phone_number == phone_number).first()
                
                if not practitioner:
                    return None
                
                # Build context using ORM relationships
                context = {
                    'practitioner': {
                        'name': practitioner.name,
                        'phone_number': practitioner.phone_number,
                        'practice_type': practitioner.practice_type,
                        'location': practitioner.location,
                        'about_us': practitioner.about_us,
                        'is_contacted': practitioner.is_contacted,
                        'contact_status': practitioner.contact_status
                    },
                    'insights': self._serialize_insights(practitioner.insights),
                    'call_history': [
                        {
                            'date': transcript.created_at.isoformat(),
                            'duration': transcript.call_duration_seconds,
                            'status': transcript.call_status,
                            'summary': transcript.conversation_summary
                        }
                        for transcript in practitioner.call_transcripts[-5:]  # Last 5 calls
                    ],
                    'call_outcomes': [
                        {
                            'outcome': outcome.call_outcome,
                            'approach': outcome.approach_used,
                            'objection': outcome.objection_type,
                            'date': outcome.call_date.isoformat()
                        }
                        for outcome in practitioner.call_outcomes[-5:]  # Last 5 outcomes
                    ]
                }
                
                return context
                
            except Exception as e:
                logger.error(f"❌ Error getting practitioner context for {phone_number}: {e}")
                raise

    def _extract_conversation_summary(self, transcript_data: Dict) -> str:
        """Extract human-readable summary from transcript JSON"""
        try:
            items = transcript_data.get("transcript", {}).get("items", [])
            summary_parts = []
            
            for item in items:
                if item.get("type") == "message":
                    role = "AI" if item.get("role") == "assistant" else "User"
                    content = " ".join(item.get("content", []))
                    summary_parts.append(f"{role}: {content}")
            
            return "\n".join(summary_parts)
        except Exception:
            return "Summary extraction failed"

    def _update_practitioner_insights(self, session: Session, phone_number: str, 
                                    outcome: str, approach_used: str, objection_type: str):
        """Update practitioner insights based on call outcome"""
        # Get or create insights record
        insights = session.query(PractitionerInsight).filter(
            PractitionerInsight.phone_number == phone_number
        ).first()
        
        if not insights:
            insights = PractitionerInsight(phone_number=phone_number)
            session.add(insights)
        
        # Update call statistics
        insights.total_calls = (insights.total_calls or 0) + 1
        
        if outcome == 'success':
            insights.successful_calls = (insights.successful_calls or 0) + 1
        
        # Update conversion probability
        if insights.total_calls > 0:
            insights.conversion_probability = insights.successful_calls / insights.total_calls
        
        # Update approaches and objections
        if approach_used:
            if outcome == 'success':
                if not insights.successful_approaches:
                    insights.successful_approaches = []
                if approach_used not in insights.successful_approaches:
                    insights.successful_approaches.append(approach_used)
            else:
                if not insights.failed_approaches:
                    insights.failed_approaches = []
                if approach_used not in insights.failed_approaches:
                    insights.failed_approaches.append(approach_used)
        
        if objection_type and not insights.primary_objection:
            insights.primary_objection = objection_type
        
        insights.last_updated = datetime.utcnow()

class SecureOTPRepository(SecureRepository):
    """Secure OTP operations using ORM"""
    
    def create_otp(self, phone_number: str, otp: str, expires_in_minutes: int = 10) -> bool:
        """
        Create OTP - SECURE VERSION
        
        OLD (VULNERABLE):
        Direct SQL insertion with string formatting
        
        NEW (SECURE):
        ORM with automatic datetime handling and validation
        """
        with self.db_engine.get_db_session() as session:
            try:
                # Clean up expired OTPs first
                self._cleanup_expired_otps(session, phone_number)
                
                # Create new OTP with ORM
                expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
                
                otp_record = PhoneOTP(
                    phone_number=phone_number,
                    otp=otp,
                    expires_at=expires_at,
                    is_verified=False
                )
                
                session.add(otp_record)
                
                logger.info(f"✅ Created OTP for {phone_number}")
                return True
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error creating OTP: {e}")
                raise

    def verify_otp(self, phone_number: str, otp: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify OTP and get user status - SECURE VERSION
        
        OLD (VULNERABLE):
        Multiple raw SQL queries with potential race conditions
        
        NEW (SECURE):
        Single transaction with ORM and automatic cleanup
        """
        with self.db_engine.get_db_session() as session:
            try:
                # Find valid OTP using ORM (automatically secure)
                otp_record = session.query(PhoneOTP).filter(
                    and_(
                        PhoneOTP.phone_number == phone_number,
                        PhoneOTP.otp == otp,
                        PhoneOTP.expires_at > datetime.utcnow(),
                        PhoneOTP.is_verified == False
                    )
                ).first()
                
                if not otp_record:
                    return False, None
                
                # Mark as verified
                otp_record.is_verified = True
                
                # Get practitioner status
                practitioner = session.query(Practitioner).filter(
                    Practitioner.phone_number == phone_number
                ).first()
                
                user_status = {
                    'is_new_user': practitioner is None,
                    'phone_number': phone_number,
                    'practitioner_id': practitioner.id if practitioner else None,
                    'onboarding_step': practitioner.onboarding_step if practitioner else 0
                }
                
                logger.info(f"✅ Verified OTP for {phone_number}")
                return True, user_status
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error verifying OTP: {e}")
                raise

    def _cleanup_expired_otps(self, session: Session, phone_number: str):
        """Clean up expired OTPs for phone number"""
        session.query(PhoneOTP).filter(
            and_(
                PhoneOTP.phone_number == phone_number,
                PhoneOTP.expires_at <= datetime.utcnow()
            )
        ).delete() 