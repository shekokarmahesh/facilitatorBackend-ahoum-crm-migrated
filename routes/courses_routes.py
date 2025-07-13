from flask import Blueprint, request, jsonify, g
from middleware.auth_required import token_required
from models.database import DatabaseManager, FacilitatorRepository, StudentRepository, CourseRepository
from services.whatsapp_service import whatsapp_service
import logging
import re

# Create blueprint for course management routes
courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

# Initialize database components
db_manager = DatabaseManager()
facilitator_repo = FacilitatorRepository(db_manager)
student_repo = StudentRepository(db_manager)
course_repo = CourseRepository(db_manager)

# Configure logging
logger = logging.getLogger(__name__)

@courses_bp.route('/', methods=['GET'])
@token_required
def get_courses():
    """Get all courses for the authenticated facilitator"""
    try:
        facilitator_id = g.user.get('id')
        
        courses = course_repo.get_courses(facilitator_id)
        
        return jsonify({
            "success": True,
            "courses": courses,
            "count": len(courses)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch courses"
        }), 500

@courses_bp.route('/', methods=['POST'])
@token_required
def create_course():
    """Create a new course"""
    try:
        facilitator_id = g.user.get('id')
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'timing', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"{field} is required"
                }), 400
        
        # Create course data
        course_data = {
            'title': data.get('title').strip(),
            'timing': data.get('timing').strip(),
            'prerequisite': data.get('prerequisite', '').strip(),
            'description': data.get('description').strip()
        }
        
        # Create the course
        course_id = course_repo.create_course(facilitator_id, course_data)
        
        if course_id:
            # Get the created course
            course = course_repo.get_course(course_id, facilitator_id)
            
            return jsonify({
                "success": True,
                "message": "Course created successfully",
                "course": course
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Failed to create course"
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to create course"
        }), 500

@courses_bp.route('/<int:course_id>', methods=['GET'])
@token_required
def get_course(course_id):
    """Get a specific course"""
    try:
        facilitator_id = g.user.get('id')
        
        course = course_repo.get_course(course_id, facilitator_id)
        
        if course:
            return jsonify({
                "success": True,
                "course": course
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error fetching course: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch course"
        }), 500

@courses_bp.route('/<int:course_id>', methods=['PUT'])
@token_required
def update_course(course_id):
    """Update a course"""
    try:
        facilitator_id = g.user.get('id')
        data = request.get_json()
        
        # Check if course exists and belongs to facilitator
        existing_course = course_repo.get_course(course_id, facilitator_id)
        if not existing_course:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404
        
        # Validate required fields
        required_fields = ['title', 'timing', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"{field} is required"
                }), 400
        
        # Update course data
        update_data = {
            'title': data.get('title').strip(),
            'timing': data.get('timing').strip(),
            'prerequisite': data.get('prerequisite', '').strip(),
            'description': data.get('description').strip()
        }
        
        # Update the course
        success = course_repo.update_course(course_id, facilitator_id, update_data)
        
        if success:
            # Get the updated course
            updated_course = course_repo.get_course(course_id, facilitator_id)
            
            return jsonify({
                "success": True,
                "message": "Course updated successfully",
                "course": updated_course
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update course"
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating course: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to update course"
        }), 500

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@token_required
def delete_course(course_id):
    """Delete a course"""
    try:
        facilitator_id = g.user.get('id')
        
        # Check if course exists and belongs to facilitator
        existing_course = course_repo.get_course(course_id, facilitator_id)
        if not existing_course:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404
        
        # Delete the course
        success = course_repo.delete_course(course_id, facilitator_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Course deleted successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to delete course"
            }), 500
            
    except Exception as e:
        logger.error(f"Error deleting course: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to delete course"
        }), 500

@courses_bp.route('/<int:course_id>/send-whatsapp', methods=['POST'])
@token_required
def send_course_whatsapp(course_id):
    """Send course details via WhatsApp to selected students"""
    try:
        facilitator_id = g.user.get('id')
        data = request.get_json()
        
        # Check WhatsApp service availability
        if not whatsapp_service:
            return jsonify({
                "success": False,
                "error": "WhatsApp service is not available"
            }), 503
        
        # Get course details
        course = course_repo.get_course(course_id, facilitator_id)
        if not course:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404
        
        # Get recipient phone numbers
        phone_numbers = data.get('phone_numbers', [])
        student_ids = data.get('student_ids', [])
        
        # If student IDs provided, get their phone numbers
        if student_ids:
            students = student_repo.get_students(facilitator_id)
            for student in students:
                if student['id'] in student_ids and student.get('phone_number'):
                    phone_numbers.append(student['phone_number'])
        
        if not phone_numbers:
            return jsonify({
                "success": False,
                "error": "No phone numbers provided"
            }), 400
        
        # Send WhatsApp messages
        results = whatsapp_service.send_bulk_course_messages(phone_numbers, course)
        
        return jsonify({
            "success": True,
            "message": f"WhatsApp messages sent to {results['total_sent']} recipients",
            "results": results,
            "course_title": course['title']
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp messages: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to send WhatsApp messages"
        }), 500

@courses_bp.route('/<int:course_id>/send-to-all-students', methods=['POST'])
@token_required
def send_course_to_all_students(course_id):
    """Send course details via WhatsApp to all active students"""
    try:
        facilitator_id = g.user.get('id')
        
        # Check WhatsApp service availability
        if not whatsapp_service:
            return jsonify({
                "success": False,
                "error": "WhatsApp service is not available"
            }), 503
        
        # Get course details
        course = course_repo.get_course(course_id, facilitator_id)
        if not course:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404
        
        # Get all active students
        students = student_repo.get_students(facilitator_id, filters={'status': 'active'})
        
        # Extract phone numbers
        phone_numbers = []
        for student in students:
            if student.get('phone_number'):
                phone_numbers.append(student['phone_number'])
        
        if not phone_numbers:
            return jsonify({
                "success": False,
                "error": "No active students with phone numbers found"
            }), 400
        
        # Send WhatsApp messages
        results = whatsapp_service.send_bulk_course_messages(phone_numbers, course)
        
        return jsonify({
            "success": True,
            "message": f"WhatsApp messages sent to {results['total_sent']} students",
            "results": results,
            "course_title": course['title'],
            "total_students": len(students)
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp messages to all students: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to send WhatsApp messages"
        }), 500

@courses_bp.route('/test-whatsapp', methods=['POST'])
@token_required
def test_whatsapp():
    """Test WhatsApp service with a simple message"""
    try:
        facilitator_id = g.user.get('id')
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({
                "success": False,
                "error": "Phone number is required"
            }), 400
        
        # Check WhatsApp service availability
        if not whatsapp_service:
            return jsonify({
                "success": False,
                "error": "WhatsApp service is not available"
            }), 503
        
        # Test message
        test_message = "Hello! This is a test message from Ahoum CRM. Your WhatsApp integration is working correctly! ✅"
        
        # Send test message
        result = whatsapp_service.send_text_message(phone_number, test_message)
        
        return jsonify({
            "success": True,
            "message": "Test message sent",
            "result": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing WhatsApp: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to test WhatsApp service"
        }), 500

@courses_bp.route('/whatsapp-status', methods=['GET'])
@token_required
def whatsapp_status():
    """Check WhatsApp service status"""
    try:
        facilitator_id = g.user.get('id')
        if not whatsapp_service:
            return jsonify({
                "success": False,
                "status": "unavailable",
                "message": "WhatsApp service is not initialized"
            }), 503
        
        # Test connection
        status = whatsapp_service.test_connection()
        
        return jsonify({
            "success": True,
            "status": status
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking WhatsApp status: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to check WhatsApp status"
        }), 500

# Add new routes for website publishing
@courses_bp.route('/api/facilitator/check-subdomain/<subdomain>', methods=['GET'])
@token_required
def check_subdomain(subdomain):
    """Check if a subdomain is available"""
    try:
        # Validate subdomain format
        if not re.match(r'^[a-z0-9-]{3,}$', subdomain):
            return jsonify({
                'available': False,
                'message': 'Invalid subdomain format. Use only lowercase letters, numbers, and hyphens.'
            }), 400

        # Check if subdomain exists
        exists = facilitator_repo.check_subdomain_exists(subdomain)
        
        return jsonify({
            'available': not exists,
            'message': 'Subdomain is available' if not exists else 'Subdomain is already taken'
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to check subdomain availability',
            'message': str(e)
        }), 500

@courses_bp.route('/api/facilitator/publish-website', methods=['POST'])
@token_required
def publish_website():
    """Publish facilitator's website with chosen subdomain"""
    try:
        facilitator_id = g.user.get('id')
        data = request.get_json()
        subdomain = data.get('subdomain')

        # Validate subdomain
        if not subdomain or not re.match(r'^[a-z0-9-]{3,}$', subdomain):
            return jsonify({
                'error': 'Invalid subdomain',
                'message': 'Invalid subdomain format. Use only lowercase letters, numbers, and hyphens.'
            }), 400

        # Check if subdomain is taken
        if facilitator_repo.check_subdomain_exists(subdomain):
            return jsonify({
                'error': 'Subdomain taken',
                'message': 'This subdomain is already taken. Please choose another one.'
            }), 400

        # Update facilitator's subdomain and publish status
        facilitator_repo.update_facilitator_website({
            'facilitator_id': facilitator_id,
            'subdomain': subdomain,
            'is_published': True
        })

        return jsonify({
            'success': True,
            'message': 'Website published successfully',
            'subdomain': subdomain
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to publish website',
            'message': str(e)
        }), 500

# CORS OPTIONS handlers
@courses_bp.route('/', methods=['OPTIONS'])
@courses_bp.route('/<int:course_id>', methods=['OPTIONS'])
@courses_bp.route('/<int:course_id>/send-whatsapp', methods=['OPTIONS'])
@courses_bp.route('/<int:course_id>/send-to-all-students', methods=['OPTIONS'])
@courses_bp.route('/test-whatsapp', methods=['OPTIONS'])
@courses_bp.route('/whatsapp-status', methods=['OPTIONS'])
@courses_bp.route('/api/facilitator/check-subdomain/<subdomain>', methods=['OPTIONS'])
@courses_bp.route('/api/facilitator/publish-website', methods=['OPTIONS'])
def handle_options():
    """Handle CORS preflight requests"""
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response, 200 