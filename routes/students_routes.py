from flask import Blueprint, request, jsonify
from models.database import DatabaseManager, StudentRepository
from middleware.auth_required import token_required
import csv
import io
import logging

# Create blueprint
students_bp = Blueprint('students', __name__)

# Initialize database
db_manager = DatabaseManager()
student_repo = StudentRepository(db_manager)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================================================================
# STUDENT MANAGEMENT ENDPOINTS
# ================================================================================

@students_bp.route('/', methods=['GET'])
@token_required
def get_students():
    """Get all students for the current practitioner"""
    try:
        practitioner_id = request.facilitator_id
        
        # Get filters from query params
        filters = {}
        if request.args.get('student_type'):
            filters['student_type'] = request.args.get('student_type')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        
        students = student_repo.get_students(practitioner_id, filters)
        
        return jsonify({
            "success": True,
            "students": students,
            "count": len(students)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch students"
        }), 500

@students_bp.route('/', methods=['POST'])
@token_required
def create_student():
    """Create a new student"""
    try:
        practitioner_id = request.facilitator_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Request body is required"
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'phone_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "error": f"Missing required field",
                    "message": f"Field '{field}' is required"
                }), 400
        
        student_id = student_repo.create_student(practitioner_id, data)
        
        if student_id:
            return jsonify({
                "success": True,
                "message": "Student created successfully",
                "student_id": student_id
            }), 201
        else:
            return jsonify({
                "error": "Creation failed",
                "message": "Failed to create student"
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to create student"
        }), 500

@students_bp.route('/<int:student_id>', methods=['PUT'])
@token_required
def update_student(student_id):
    """Update a student"""
    try:
        facilitator_id = request.facilitator_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Request body is required"
            }), 400
        
        success = student_repo.update_student(student_id, facilitator_id, data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Student updated successfully"
            }), 200
        else:
            return jsonify({
                "error": "Update failed",
                "message": "Failed to update student or student not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error updating student: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to update student"
        }), 500

@students_bp.route('/<int:student_id>', methods=['DELETE'])
@token_required
def delete_student(student_id):
    """Delete a student (soft delete)"""
    try:
        facilitator_id = request.facilitator_id
        
        success = student_repo.delete_student(student_id, facilitator_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Student deleted successfully"
            }), 200
        else:
            return jsonify({
                "error": "Delete failed",
                "message": "Failed to delete student or student not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error deleting student: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to delete student"
        }), 500

@students_bp.route('/import-csv', methods=['POST'])
@token_required
def import_students_csv():
    """Import students from CSV file"""
    try:
        practitioner_id = request.facilitator_id
        
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({
                "error": "No file provided",
                "message": "CSV file is required"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "error": "No file selected",
                "message": "Please select a CSV file"
            }), 400
        
        # Read CSV data
        try:
            csv_data = []
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            for row in csv_reader:
                csv_data.append(row)
            
            # Import students
            imported_count = student_repo.import_students_from_csv(practitioner_id, csv_data)
            
            return jsonify({
                "success": True,
                "message": f"Successfully imported {imported_count} students",
                "imported_count": imported_count,
                "total_rows": len(csv_data)
            }), 200
            
        except Exception as e:
            return jsonify({
                "error": "CSV parsing error",
                "message": f"Failed to parse CSV file: {str(e)}"
            }), 400
            
    except Exception as e:
        logger.error(f"Error importing students: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to import students"
        }), 500

@students_bp.route('/sample-csv', methods=['GET'])
def get_sample_csv():
    """Get sample CSV format for student import"""
    return jsonify({
        "success": True,
        "sample_format": {
            "headers": ["name", "phone_number", "email", "student_type", "status", "notes"],
            "example_row": {
                "name": "John Doe",
                "phone_number": "+1234567890",
                "email": "john@example.com",
                "student_type": "regular",
                "status": "active",
                "notes": "Prefers morning classes"
            }
        },
        "valid_student_types": ["regular", "trial", "former", "prospect"],
        "valid_statuses": ["active", "inactive", "paused"]
    }), 200

# ================================================================================
# OPTIONS HANDLERS FOR CORS
# ================================================================================

@students_bp.route('/', methods=['OPTIONS'])
@students_bp.route('/<int:student_id>', methods=['OPTIONS'])
@students_bp.route('/import-csv', methods=['OPTIONS'])
@students_bp.route('/sample-csv', methods=['OPTIONS'])
def handle_options():
    """Handle OPTIONS requests for CORS"""
    return '', 200 