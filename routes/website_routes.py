from flask import Blueprint, request, jsonify, g
from middleware.auth_required import token_required
from models.database import DatabaseManager, FacilitatorRepository
import re

# Initialize database manager and repository
db_manager = DatabaseManager()
facilitator_repo = FacilitatorRepository(db_manager)

website_bp = Blueprint('website', __name__)

@website_bp.route('/api/facilitator/check-subdomain/<subdomain>', methods=['GET'])
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

@website_bp.route('/api/facilitator/publish-website', methods=['POST'])
@token_required
def publish_website():
    """Publish facilitator's website with chosen subdomain"""
    try:
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

<<<<<<< HEAD
@website_bp.route('/status', methods=['GET'])
@token_required
def get_website_status():
    """Get current website publishing status"""
    try:
        facilitator_id = request.facilitator_id
        
        # Get practitioner data including website status
        website_data = facilitator_repo.get_website_status(facilitator_id)
        
        if website_data:
            # Add website URL to the data
            website_data['website_url'] = f"https://{website_data.get('subdomain')}.ahoum.com" if website_data.get('subdomain') else None
            
            return jsonify({
                'success': True,
                'website': website_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Practitioner not found'
            }), 404
        
    except Exception as e:
        logging.error(f"Error getting website status: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
=======
        # Get current facilitator's ID from session
        facilitator_id = g.user.get('id')
>>>>>>> 6ae75d5c634c76742ccbd961df2fc535fb69032a

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
@website_bp.route('/api/facilitator/check-subdomain/<subdomain>', methods=['OPTIONS'])
@website_bp.route('/api/facilitator/publish-website', methods=['OPTIONS'])
def handle_options():
    """Handle CORS preflight requests"""
    return '', 204 