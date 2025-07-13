"""
Course Calling Routes
API endpoints for course promotion calling functionality
"""

from flask import Blueprint, request, jsonify, current_app, g
import requests
import logging
import json
import subprocess
from datetime import datetime
from models.database import DatabaseManager, CourseCallingRepository
from middleware.auth_required import token_required

course_calling_bp = Blueprint('course_calling', __name__, url_prefix='/api/courses')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@course_calling_bp.route('/test-livekit-config', methods=['GET'])
def test_livekit_config():
    """Test endpoint to check LiveKit configuration"""
    try:
        import os
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

@course_calling_bp.route('/<int:course_id>/call-student', methods=['POST'])
@token_required
def initiate_course_promotion_call(course_id):
    """Initiate AI call to promote specific course"""
    try:
        practitioner_id = g.user.get('id')
        
        # Debug: Log raw request data
        logger.info(f"Raw request data: {request.data}")
        logger.info(f"Content-Type: {request.content_type}")
        
        data = request.get_json()
        logger.info(f"Parsed JSON data: {data}")
        
        # Validate input
        phone_number = data.get('phone_number')
        if not phone_number:
            return jsonify({'success': False, 'error': 'Phone number required'}), 400
        
        # Clean phone number
        phone_number = phone_number.strip()
        if not phone_number.startswith('+'):
            # Add default country code if not provided
            if phone_number.startswith('1'):
                phone_number = '+' + phone_number
            else:
                phone_number = '+1' + phone_number
        
        # Get course details and verify ownership
        db_manager = DatabaseManager()
        course_calling_repo = CourseCallingRepository(db_manager)
        
        course_data = course_calling_repo.get_course_with_practitioner(course_id, practitioner_id)
        
        if not course_data:
            return jsonify({'success': False, 'error': 'Course not found or access denied'}), 404
        
        course_dict = course_data['course']
        practitioner_dict = course_data['practitioner'] or {}
        
        # Log the call initiation
        call_id = course_calling_repo.log_course_promotion_call(practitioner_id, course_id, phone_number)
        
        if not call_id:
            return jsonify({'success': False, 'error': 'Failed to log call'}), 500
        
        # Prepare course context for calling agent
        course_context = {
            'course_id': course_id,
            'title': course_dict['title'],
            'timing': course_dict['timing'],
            'prerequisite': course_dict['prerequisite'] or 'Open to all levels',
            'description': course_dict['description'],
            'practitioner_id': practitioner_id,
            'practitioner_name': practitioner_dict.get('name', 'Your instructor'),
            'practitioner_phone': practitioner_dict.get('phone_number', ''),
            'call_id': call_id
        }
        
        # Trigger LiveKit call with course context
        success, room_name = trigger_livekit_course_call(phone_number, course_context, call_id)
        
        if success:
            # Update call status with room name
            if room_name:
                course_calling_repo.update_call_status(call_id, 'connecting', livekit_room_name=room_name)
            
            db_manager.close_connection()
            
            return jsonify({
                'success': True,
                'message': 'Course promotion call initiated successfully',
                'call_id': call_id,
                'course': course_dict,
                'phone_number': phone_number,
                'room_name': room_name
            }), 200
        else:
            # Update call status to failed
            course_calling_repo.update_call_status(call_id, 'failed')
            db_manager.close_connection()
            
            return jsonify({'success': False, 'error': 'Failed to initiate call'}), 500
            
    except Exception as e:
        logger.error(f"Error initiating course call: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

def trigger_livekit_course_call(phone_number: str, course_context: dict, call_id: int) -> tuple[bool, str]:
    """Trigger LiveKit dispatch with course promotion context"""
    try:
        # Import config and dotenv to get LiveKit credentials
        import os
        from dotenv import load_dotenv
        from config import Config
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Prepare metadata for LiveKit dispatch
        metadata = {
            'phone_number': phone_number,
            'call_type': 'course_promotion',
            'course_context': course_context,
            'call_id': call_id
        }
        
        # Generate unique room name
        room_name = f"course-call-{call_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Get fresh credentials from environment
        livekit_url = os.getenv("LIVEKIT_URL", Config.LIVEKIT_URL)
        livekit_api_key = os.getenv("LIVEKIT_API_KEY", Config.LIVEKIT_API_KEY)
        livekit_api_secret = os.getenv("LIVEKIT_API_SECRET", Config.LIVEKIT_API_SECRET)
        
        # Check if LiveKit credentials are configured
        if not livekit_api_key or not livekit_api_secret:
            logger.error("LiveKit credentials not configured. Please set LIVEKIT_API_KEY and LIVEKIT_API_SECRET")
            logger.error(f"Current values: URL={livekit_url}, API_KEY={'***' if livekit_api_key else 'None'}, SECRET={'***' if livekit_api_secret else 'None'}")
            return False, None
        
        # Check if lk CLI is available
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
        
        # Prepare environment variables for subprocess
        env = os.environ.copy()
        env.update({
            'LIVEKIT_URL': livekit_url,
            'LIVEKIT_API_KEY': livekit_api_key,
            'LIVEKIT_API_SECRET': livekit_api_secret
        })
        
        # Prepare LiveKit dispatch command
        dispatch_command = [
            'lk', 'dispatch', 'create',
            '--room', room_name,
            '--agent-name', 'outbound-caller',
            '--metadata', json.dumps(metadata)
        ]
        
        logger.info(f"Triggering LiveKit call: {' '.join(dispatch_command)}")
        logger.info(f"Using LiveKit URL: {livekit_url}")
        logger.info(f"Using API Key: {livekit_api_key[:8]}...")
        
        # Execute LiveKit dispatch with environment variables
        logger.info(f"Environment variables for LiveKit: URL={env.get('LIVEKIT_URL')}, API_KEY={env.get('LIVEKIT_API_KEY')[:8]}...")
        logger.info(f"Full command: {' '.join(dispatch_command)}")
        
        result = subprocess.run(
            dispatch_command, 
            capture_output=True, 
            text=True, 
            timeout=30,
            env=env,  # Pass environment variables to subprocess
            cwd=None  # Use current working directory
        )
        
        if result.returncode == 0:
            logger.info(f"LiveKit call initiated successfully for call ID {call_id}")
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
        logger.error(f"Error triggering LiveKit call: {e}")
        return False, None

@course_calling_bp.route('/<int:course_id>/call-history', methods=['GET'])
@token_required
def get_course_call_history(course_id):
    """Get call history for specific course"""
    try:
        practitioner_id = g.user.get('id')
        limit = request.args.get('limit', 50, type=int)
        
        # Verify course belongs to practitioner using secure ORM
        db_manager = DatabaseManager()
        course_calling_repo = CourseCallingRepository(db_manager)
        
        if not course_calling_repo.verify_course_ownership(course_id, practitioner_id):
            return jsonify({'success': False, 'error': 'Course not found'}), 404
        
        calls = course_calling_repo.get_course_promotion_calls(practitioner_id, limit)
        
        db_manager.close_connection()
        
        return jsonify({
            'success': True,
            'calls': calls,
            'count': len(calls)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching call history: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch call history'}), 500

@course_calling_bp.route('/<int:course_id>/call-analytics', methods=['GET'])
@token_required
def get_course_call_analytics(course_id):
    """Get call analytics for specific course"""
    try:
        practitioner_id = g.user.get('id')
        
        # Verify course belongs to practitioner using secure ORM
        db_manager = DatabaseManager()
        course_calling_repo = CourseCallingRepository(db_manager)
        
        course_data = course_calling_repo.get_course_with_practitioner(course_id, practitioner_id)
        if not course_data:
            return jsonify({'success': False, 'error': 'Course not found'}), 404
        
        course_dict = course_data['course']
        
        course_calling_repo = CourseCallingRepository(db_manager)
        analytics = course_calling_repo.get_call_analytics(course_id, practitioner_id)
        
        db_manager.close_connection()
        
        return jsonify({
            'success': True,
            'course': course_dict,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching call analytics: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch analytics'}), 500

@course_calling_bp.route('/call-history', methods=['GET'])
@token_required
def get_all_course_call_history():
    """Get all course promotion call history for practitioner"""
    try:
        practitioner_id = g.user.get('id')
        limit = request.args.get('limit', 100, type=int)
        
        db_manager = DatabaseManager()
        course_calling_repo = CourseCallingRepository(db_manager)
        calls = course_calling_repo.get_practitioner_call_history(practitioner_id, limit)
        
        db_manager.close_connection()
        
        return jsonify({
            'success': True,
            'calls': calls,
            'count': len(calls)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching practitioner call history: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch call history'}), 500

@course_calling_bp.route('/call/<int:call_id>/outcome', methods=['PUT'])
def update_call_outcome(call_id):
    """Update call outcome (typically called by calling agent)"""
    try:
        data = request.get_json()
        
        # Verify call belongs to practitioner using secure ORM
        db_manager = DatabaseManager()
        course_calling_repo = CourseCallingRepository(db_manager)
        
        practitioner_id = course_calling_repo.get_call_practitioner_id(call_id)
        if not practitioner_id:
            return jsonify({'success': False, 'error': 'Call not found'}), 404
        
        # Add practitioner_id to outcome data for stats update
        outcome_data = data.copy()
        outcome_data['practitioner_id'] = practitioner_id
        
        course_calling_repo = CourseCallingRepository(db_manager)
        success = course_calling_repo.update_call_outcome(call_id, outcome_data)
        
        db_manager.close_connection()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Call outcome updated successfully'
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to update call outcome'}), 500
        
    except Exception as e:
        logger.error(f"Error updating call outcome: {e}")
        return jsonify({'success': False, 'error': 'Failed to update call outcome'}), 500

@course_calling_bp.route('/call/<int:call_id>/status', methods=['PUT'])
def update_call_status(call_id):
    """Update call status (called by calling agent during call)"""
    try:
        data = request.get_json()
        status = data.get('status')
        room_name = data.get('room_name')
        
        if not status:
            return jsonify({'success': False, 'error': 'Status required'}), 400
        
        db_manager = DatabaseManager()
        course_calling_repo = CourseCallingRepository(db_manager)
        success = course_calling_repo.update_call_status(call_id, status, livekit_room_name=room_name)
        
        db_manager.close_connection()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Call status updated successfully'
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to update call status'}), 500
        
    except Exception as e:
        logger.error(f"Error updating call status: {e}")
        return jsonify({'success': False, 'error': 'Failed to update call status'}), 500

@course_calling_bp.route('/dashboard-stats', methods=['GET'])
@token_required
def get_calling_dashboard_stats():
    """Get overall calling statistics for practitioner dashboard"""
    try:
        practitioner_id = g.user.get('id')
        days = request.args.get('days', 30, type=int)
        
        db_manager = DatabaseManager()
        course_calling_repo = CourseCallingRepository(db_manager)
        
        # Get analytics using secure ORM method
        analytics = course_calling_repo.get_overall_analytics(practitioner_id)
        
        db_manager.close_connection()
        
        return jsonify({
            'success': True,
            'period_days': days,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch dashboard stats'}), 500

# Error handlers
@course_calling_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@course_calling_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500 