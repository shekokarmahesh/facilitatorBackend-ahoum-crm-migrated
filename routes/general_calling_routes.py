"""
General Calling Routes
API endpoints for general practitioner outreach and website promotion calls
"""

from flask import Blueprint, request, jsonify, current_app, g
import requests
import logging
import json
import subprocess
import os
from datetime import datetime
from models.database import DatabaseManager
from middleware.auth_required import token_required

general_calling_bp = Blueprint('general_calling', __name__, url_prefix='/api/general-calls')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@general_calling_bp.route('/test-livekit-config', methods=['GET'])
def test_general_livekit_config():
    """Test endpoint to check LiveKit configuration for general calls"""
    try:
        from dotenv import load_dotenv
        from config import Config
        
        load_dotenv()
        
        livekit_url = os.getenv("LIVEKIT_URL", Config.LIVEKIT_URL)
        livekit_api_key = os.getenv("LIVEKIT_API_KEY", Config.LIVEKIT_API_KEY)
        livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", Config.LIVEKIT_API_SECRET)
        
        return jsonify({
            'success': True,
            'config': {
                'url': livekit_url,
                'api_key': livekit_api_key[:8] + '...' if livekit_api_key else None,
                'api_secret': livekit_api_secret[:8] + '...' if livekit_api_secret else None,
                'has_credentials': bool(livekit_api_key and livekit_api_secret)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@general_calling_bp.route('/call-practitioner', methods=['POST'])
def initiate_general_call():
    """Initiate AI call for general practitioner outreach and website promotion"""
    try:
        data = request.get_json()
        logger.info(f"General call request data: {data}")
        
        # Validate input
        phone_number = data.get('phone_number')
        if not phone_number:
            return jsonify({'success': False, 'error': 'Phone number required'}), 400
        
        # Clean phone number
        phone_number = phone_number.strip()
        if not phone_number.startswith('+'):
            # Add default country code if not provided
            if phone_number.startswith('91'):
                phone_number = '+' + phone_number
            elif phone_number.startswith('1'):
                phone_number = '+' + phone_number
            else:
                # Default to Indian number if no country code
                phone_number = '+91' + phone_number
        
        # Get practitioner context (optional, for personalization)
        practitioner_context = data.get('practitioner_context', {})
        
        # Additional call context
        call_context = {
            'phone_number': phone_number,
            'call_type': 'general_outreach',
            'purpose': 'website_promotion',
            'practitioner_context': practitioner_context,
            'initiated_at': datetime.now().isoformat(),
            'source': 'api_request'
        }
        
        # Log call in database (optional)
        db_manager = DatabaseManager()
        try:
            # You can add a method to log general calls if needed
            logger.info(f"Initiating general call to {phone_number}")
        except Exception as db_error:
            logger.warning(f"Could not log call to database: {db_error}")
        finally:
            db_manager.close_connection()
        
        # Trigger LiveKit call
        success, room_name = trigger_livekit_general_call(phone_number, call_context)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'General outreach call initiated successfully',
                'phone_number': phone_number,
                'room_name': room_name,
                'call_type': 'general_outreach',
                'purpose': 'website_promotion'
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to initiate call'}), 500
            
    except Exception as e:
        logger.error(f"Error initiating general call: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def trigger_livekit_general_call(phone_number: str, call_context: dict) -> tuple[bool, str]:
    """Trigger LiveKit dispatch for general practitioner outreach calls"""
    try:
        from dotenv import load_dotenv
        from config import Config
        
        # Load environment variables
        load_dotenv()
        
        # Prepare metadata for LiveKit dispatch
        # For general calls, we use simpler metadata structure
        metadata = json.dumps({
            'phone_number': phone_number,
            'call_type': 'general',
            'context': call_context
        })
        
        # Generate unique room name
        room_name = f"general-call-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{phone_number.replace('+', '')}"
        
        # Get LiveKit credentials
        livekit_url = os.getenv("LIVEKIT_URL", Config.LIVEKIT_URL)
        livekit_api_key = os.getenv("LIVEKIT_API_KEY", Config.LIVEKIT_API_KEY)
        livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", Config.LIVEKIT_API_SECRET)
        
        # Check credentials
        if not livekit_api_key or not livekit_api_secret:
            logger.error("LiveKit credentials not configured")
            return False, None
        
        # Check LiveKit CLI
        try:
            lk_version = subprocess.run(['lk', '--version'], capture_output=True, text=True, timeout=5)
            if lk_version.returncode != 0:
                logger.error("LiveKit CLI (lk) not found or not working")
                return False, None
            else:
                logger.info(f"LiveKit CLI version: {lk_version.stdout.strip()}")
        except Exception as e:
            logger.error(f"Error checking LiveKit CLI: {e}")
            return False, None
        
        # Set working directory to calling agent folder
        calling_agent_dir = r"e:\Ahoum-CRM\calling agent livekit"
        
        # Prepare environment variables
        env = os.environ.copy()
        env.update({
            'LIVEKIT_URL': livekit_url,
            'LIVEKIT_API_KEY': livekit_api_key,
            'LIVEKIT_API_SECRET': livekit_api_secret
        })
        
        # Prepare LiveKit dispatch command for general calls
        dispatch_command = [
            'lk', 'dispatch', 'create',
            '--new-room',
            '--agent-name', 'outbound-caller',
            '--metadata', metadata
        ]
        
        logger.info(f"Triggering general LiveKit call: {' '.join(dispatch_command)}")
        logger.info(f"Working directory: {calling_agent_dir}")
        logger.info(f"Using LiveKit URL: {livekit_url}")
        
        # Execute LiveKit dispatch
        result = subprocess.run(
            dispatch_command,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=calling_agent_dir  # Set working directory
        )
        
        if result.returncode == 0:
            logger.info(f"General LiveKit call initiated successfully for {phone_number}")
            logger.info(f"LiveKit stdout: {result.stdout}")
            return True, room_name
        else:
            logger.error(f"LiveKit dispatch failed (return code: {result.returncode})")
            logger.error(f"LiveKit stderr: {result.stderr}")
            logger.error(f"LiveKit stdout: {result.stdout}")
            return False, None
        
    except subprocess.TimeoutExpired:
        logger.error("LiveKit dispatch timed out")
        return False, None
    except Exception as e:
        logger.error(f"Error triggering general LiveKit call: {e}")
        return False, None

@general_calling_bp.route('/call-practitioner-simple', methods=['POST'])
def initiate_simple_general_call():
    """Simplified endpoint that mimics the direct CLI command"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({'success': False, 'error': 'Phone number required'}), 400
        
        # Clean phone number
        phone_number = phone_number.strip()
        if not phone_number.startswith('+'):
            if phone_number.startswith('91'):
                phone_number = '+' + phone_number
            elif phone_number.startswith('1'):
                phone_number = '+' + phone_number
            else:
                phone_number = '+91' + phone_number
        
        # Use the exact same approach as your working CLI command
        success, room_name = trigger_simple_livekit_call(phone_number)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'General call initiated to {phone_number}',
                'phone_number': phone_number,
                'room_name': room_name
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to initiate call'}), 500
            
    except Exception as e:
        logger.error(f"Error in simple general call: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def trigger_simple_livekit_call(phone_number: str) -> tuple[bool, str]:
    """Trigger simple LiveKit call exactly like the CLI command that works"""
    try:
        from dotenv import load_dotenv
        from config import Config
        
        load_dotenv()
        
        # Get credentials
        livekit_url = os.getenv("LIVEKIT_URL", Config.LIVEKIT_URL)
        livekit_api_key = os.getenv("LIVEKIT_API_KEY", Config.LIVEKIT_API_KEY)
        livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", Config.LIVEKIT_API_SECRET)
        
        if not livekit_api_key or not livekit_api_secret:
            logger.error("LiveKit credentials not configured")
            return False, None
        
        # Set working directory
        calling_agent_dir = r"e:\Ahoum-CRM\calling agent livekit"
        
        # Prepare environment
        env = os.environ.copy()
        env.update({
            'LIVEKIT_URL': livekit_url,
            'LIVEKIT_API_KEY': livekit_api_key,
            'LIVEKIT_API_SECRET': livekit_api_secret
        })
        
        # Use the exact command structure that works
        dispatch_command = [
            'lk', 'dispatch', 'create',
            '--new-room',
            '--agent-name', 'outbound-caller',
            '--metadata', phone_number  # Simple metadata, just the phone number
        ]
        
        logger.info(f"Executing simple command: {' '.join(dispatch_command)}")
        
        result = subprocess.run(
            dispatch_command,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=calling_agent_dir
        )
        
        if result.returncode == 0:
            # Generate room name for response
            room_name = f"general-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            logger.info(f"Simple general call initiated successfully for {phone_number}")
            logger.info(f"Command output: {result.stdout}")
            return True, room_name
        else:
            logger.error(f"Command failed: {result.stderr}")
            return False, None
            
    except Exception as e:
        logger.error(f"Error in simple LiveKit call: {e}")
        return False, None

@general_calling_bp.route('/practitioners/search', methods=['GET'])
def search_practitioners():
    """Search for practitioners by phone, name, or practice type"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'}), 400
        
        db_manager = DatabaseManager()
        
        # Search in practitioners table
        practitioners = db_manager.search_practitioners(query)
        
        db_manager.close_connection()
        
        return jsonify({
            'success': True,
            'practitioners': practitioners,
            'count': len(practitioners)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching practitioners: {e}")
        return jsonify({'success': False, 'error': 'Search failed'}), 500

@general_calling_bp.route('/practitioners/<phone_number>/info', methods=['GET'])
def get_practitioner_info(phone_number):
    """Get detailed information about a specific practitioner"""
    try:
        # Clean phone number
        if not phone_number.startswith('+'):
            if phone_number.startswith('91'):
                phone_number = '+' + phone_number
            else:
                phone_number = '+91' + phone_number
        
        db_manager = DatabaseManager()
        
        # Get practitioner information
        practitioner = db_manager.get_practitioner_by_phone(phone_number)
        
        db_manager.close_connection()
        
        if practitioner:
            return jsonify({
                'success': True,
                'practitioner': practitioner
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Practitioner not found'
            }), 404
        
    except Exception as e:
        logger.error(f"Error getting practitioner info: {e}")
        return jsonify({'success': False, 'error': 'Failed to get practitioner info'}), 500

@general_calling_bp.route('/call-history', methods=['GET'])
def get_general_call_history():
    """Get history of general outreach calls"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        # This would require implementing call logging for general calls
        # For now, return a placeholder response
        
        return jsonify({
            'success': True,
            'message': 'General call history endpoint - implementation pending',
            'calls': [],
            'count': 0
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting call history: {e}")
        return jsonify({'success': False, 'error': 'Failed to get call history'}), 500

@general_calling_bp.route('/send-website-link', methods=['POST'])
def send_practitioner_website_link():
    """Send website link via WhatsApp to practitioner or course details to student"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data',
                'details': 'Request body must contain valid JSON'
            }), 400
            
        phone_number = data.get('phone_number')
        practitioner_info = data.get('practitioner_info', {})
        course_details = data.get('course_details')  # For course promotion calls
        specific_info = data.get('specific_info')    # For course promotion calls
        
        if not phone_number:
            return jsonify({'success': False, 'error': 'Phone number required'}), 400
        
        # Clean phone number for database lookup
        clean_phone = phone_number
        if not clean_phone.startswith('+'):
            if clean_phone.startswith('91'):
                clean_phone = '+' + clean_phone
            else:
                clean_phone = '+91' + clean_phone
        
        # Fetch actual practitioner details from database
        try:
            from models.database import DatabaseManager
            db_manager = DatabaseManager()
            
            # Get practitioner from database
            db_practitioner = db_manager.get_practitioner_by_phone(clean_phone)
            
            if db_practitioner:
                # Use database practitioner info
                name = db_practitioner.get('name', 'there')
                practice_type = db_practitioner.get('practice_type', 'spiritual practice')
                location = db_practitioner.get('location', '')
                about_us = db_practitioner.get('about_us', '')
                
                logger.info(f"Found practitioner in database: {name} - {practice_type}")
            else:
                # Fallback to request practitioner info if not in database
                name = practitioner_info.get('name', 'there')
                practice_type = practitioner_info.get('practice_type', 'spiritual practice')
                location = practitioner_info.get('location', '')
                about_us = practitioner_info.get('about_us', '')
                
                logger.info(f"Practitioner not found in database, using request info: {name} - {practice_type}")
            
            db_manager.close_connection()
            
        except Exception as db_error:
            logger.error(f"Database error fetching practitioner: {db_error}")
            # Fallback to request practitioner info
            name = practitioner_info.get('name', 'there')
            practice_type = practitioner_info.get('practice_type', 'spiritual practice')
            location = practitioner_info.get('location', '')
            about_us = practitioner_info.get('about_us', '')
        
        # Determine if this is a course promotion call or general website link
        is_course_promotion = course_details is not None
        
        if is_course_promotion:
            # This is a course promotion call - send course details
            logger.info(f"Sending course details to {phone_number} for course promotion")
            
            # Create course-specific message
            message = f"""🎯 Hi there!

{course_details}

📞 For registration and pricing details, please contact {name} directly.

🌟 Thank you for your interest!

- {name} & the Ahoum Team 🙏"""
            
            # For course promotion, we don't generate a website URL since it's about a specific course
            website_url = None
            
        else:
            # This is a general website promotion call
            logger.info(f"Sending website link to {phone_number} for general promotion")
            
            # Create personalized website message
            # Generate a clean URL-friendly name
            url_name = name.lower().replace(' ', '-').replace("'", "").replace('"', '')
            website_url = f"https://ahoum.com/practitioners/{url_name}"
            
            # Create location-specific greeting
            location_greeting = f" in {location}" if location else ""
            
            # Create personalized message based on available information
            if about_us:
                # If we have about_us, create a more personalized message
                message = f"""🌟 Hi {name}! 

I've created a beautiful website for your {practice_type} practice{location_greeting}! 

🌐 Your Website: {website_url}

✨ What's included:
• Professional responsive design
• Online booking & scheduling
• Student management system
• Secure payment processing
• SEO optimization for visibility
• Course & session management

🚀 Ready to go live! No technical skills needed - we handle everything.

💬 Questions? Reply here or call back anytime!

- Omee & the Ahoum Team 🙏

P.S. This is completely free to start - we only take a small commission on paid bookings!"""
            else:
                # Standard message
                message = f"""🌟 Hi {name}! 

I've created a beautiful website for your {practice_type} practice{location_greeting}! 

🌐 Your Website: {website_url}

✨ What's included:
• Professional responsive design
• Online booking & scheduling
• Student management system
• Secure payment processing
• SEO optimization for visibility
• Course & session management

🚀 Ready to go live! No technical skills needed - we handle everything.

💬 Questions? Reply here or call back anytime!

- Omee & the Ahoum Team 🙏

P.S. This is completely free to start - we only take a small commission on paid bookings!"""
        
        # Send via WhatsApp using your existing service
        try:
            from services.whatsapp_service import WhatsAppService
            whatsapp_service = WhatsAppService()
            
            logger.info(f"Attempting to send {'course details' if is_course_promotion else 'website link'} to {phone_number}")
            logger.info(f"Message preview: {message[:100]}...")
            result = whatsapp_service.send_text_message(phone_number, message)
            
            if result.get('success'):
                logger.info(f"Successfully sent {'course details' if is_course_promotion else 'website link'} to {phone_number}")
                return jsonify({
                    'success': True,
                    'message': f"{'Course details' if is_course_promotion else 'Website link'} sent successfully via WhatsApp",
                    'phone_number': phone_number,
                    'website_url': website_url,
                    'is_course_promotion': is_course_promotion,
                    'practitioner_name': name,
                    'practice_type': practice_type,
                    'whatsapp_result': result
                }), 200
            else:
                logger.error(f"WhatsApp service failed: {result}")
                return jsonify({
                    'success': False, 
                    'error': 'Failed to send WhatsApp message',
                    'details': result.get('error', 'Unknown WhatsApp error')
                }), 500
                
        except ImportError as e:
            logger.error(f"WhatsApp service import failed: {e}")
            return jsonify({
                'success': False,
                'error': 'WhatsApp service not available',
                'details': 'WhatsApp integration not configured'
            }), 503
            
    except Exception as e:
        logger.error(f"Error in send_practitioner_website_link: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@general_calling_bp.route('/send-website-link', methods=['OPTIONS'])
def send_website_link_options():
    """Handle preflight requests for website link sending"""
    return jsonify({'message': 'OK'}), 200

# Error handlers
@general_calling_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@general_calling_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
