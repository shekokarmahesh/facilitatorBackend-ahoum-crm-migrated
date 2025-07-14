from flask import Blueprint, jsonify, g, render_template_string
from middleware.subdomain_middleware import require_valid_subdomain
from models.database import DatabaseManager, FacilitatorRepository
import logging

# Initialize database manager and repository
db_manager = DatabaseManager()
facilitator_repo = FacilitatorRepository(db_manager)

public_website_bp = Blueprint('public_website', __name__)

@public_website_bp.route('/', methods=['GET'])
@require_valid_subdomain()
def serve_public_website():
    """Serve public website for subdomain requests"""
    try:
        # Get practitioner data from subdomain context
        practitioner_data = g.subdomain_practitioner
        subdomain = g.subdomain
        
        if not practitioner_data:
            return jsonify({
                'error': 'Website not found',
                'message': 'This website is not published or does not exist'
            }), 404
        
        # Get complete profile data
        complete_profile = facilitator_repo.get_complete_facilitator_profile(practitioner_data['id'])
        
        if not complete_profile:
            return jsonify({
                'error': 'Profile not found',
                'message': 'Practitioner profile data not available'
            }), 404
        
        # Return the website data for frontend consumption
        return jsonify({
            'success': True,
            'subdomain': subdomain,
            'practitioner': complete_profile,
            'website_url': f"http://{subdomain}.localhost:3031"
        })
        
    except Exception as e:
        logging.error(f"Error serving public website for subdomain {g.subdomain}: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to load website'
        }), 500

@public_website_bp.route('/api/data', methods=['GET'])
@require_valid_subdomain()
def get_public_website_data():
    """API endpoint to get website data for subdomain"""
    try:
        practitioner_data = g.subdomain_practitioner
        subdomain = g.subdomain
        
        if not practitioner_data:
            return jsonify({
                'error': 'Website not found',
                'message': 'This website is not published or does not exist'
            }), 404
        
        # Get complete profile data
        complete_profile = facilitator_repo.get_complete_facilitator_profile(practitioner_data['id'])
        
        return jsonify({
            'success': True,
            'subdomain': subdomain,
            'practitioner': complete_profile,
            'is_public': True
        })
        
    except Exception as e:
        logging.error(f"Error getting public website data: {e}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to load website data'
        }), 500

# CORS OPTIONS handler
@public_website_bp.route('/', methods=['OPTIONS'])
@public_website_bp.route('/api/data', methods=['OPTIONS'])
def handle_options():
    """Handle CORS preflight requests"""
    return '', 204
