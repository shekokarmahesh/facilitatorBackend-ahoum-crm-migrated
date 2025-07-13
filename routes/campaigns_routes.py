from flask import Blueprint, request, jsonify
from models.database import DatabaseManager, CampaignRepository, StudentRepository
from middleware.auth_required import token_required
import logging
import requests
from config import Config

# Create blueprint
campaigns_bp = Blueprint('campaigns', __name__)

# Initialize database
db_manager = DatabaseManager()
campaign_repo = CampaignRepository(db_manager)
student_repo = StudentRepository(db_manager)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@campaigns_bp.route('/', methods=['GET'])
@token_required
def get_campaigns():
    """Get all campaigns for the current practitioner"""
    try:
        practitioner_id = request.facilitator_id
        campaigns = campaign_repo.get_campaigns(practitioner_id)
        
        return jsonify({
            "success": True,
            "campaigns": campaigns,
            "count": len(campaigns)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch campaigns"
        }), 500

@campaigns_bp.route('/', methods=['POST'])
@token_required
def create_campaign():
    """Create a new calling campaign"""
    try:
        practitioner_id = request.facilitator_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Request body is required"
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'campaign_type', 'message_template']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "error": f"Missing required field",
                    "message": f"Field '{field}' is required"
                }), 400
        
        campaign_id = campaign_repo.create_campaign(practitioner_id, data)
        
        if campaign_id:
            return jsonify({
                "success": True,
                "message": "Campaign created successfully",
                "campaign_id": campaign_id
            }), 201
        else:
            return jsonify({
                "error": "Creation failed",
                "message": "Failed to create campaign"
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to create campaign"
        }), 500

@campaigns_bp.route('/<int:campaign_id>/targets', methods=['GET'])
@token_required
def get_campaign_targets(campaign_id):
    """Get target students for a campaign"""
    try:
        targets = campaign_repo.get_campaign_targets(campaign_id)
        
        return jsonify({
            "success": True,
            "targets": targets,
            "count": len(targets)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching campaign targets: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch campaign targets"
        }), 500

@campaigns_bp.route('/<int:campaign_id>/launch', methods=['POST'])
@token_required
def launch_campaign(campaign_id):
    """Launch a campaign - start automated calling"""
    try:
        practitioner_id = request.facilitator_id
        
        # Get campaign targets
        targets = campaign_repo.get_campaign_targets(campaign_id)
        
        if not targets:
            return jsonify({
                "error": "No targets found",
                "message": "No students match the campaign criteria"
            }), 400
        
        # Update campaign status to active
        campaign_repo.update_campaign_status(campaign_id, 'active')
        
        return jsonify({
            "success": True,
            "message": "Campaign launched successfully",
            "targets_count": len(targets),
            "note": "Automated calling integration available"
        }), 200
        
    except Exception as e:
        logger.error(f"Error launching campaign: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to launch campaign"
        }), 500

@campaigns_bp.route('/templates', methods=['GET'])
@token_required
def get_campaign_templates():
    """Get pre-built campaign templates"""
    templates = {
        "workshop_promotion": {
            "name": "Workshop Promotion",
            "message_template": "Hi {student_name}! This is {caller_name} calling about {practitioner_name}'s upcoming workshop. We thought you'd be interested!",
            "target_audience": {
                "student_types": ["regular", "trial"],
                "statuses": ["active"]
            }
        },
        "class_reminder": {
            "name": "Class Reminder", 
            "message_template": "Hi {student_name}! Reminder about your class with {practitioner_name} tomorrow.",
            "target_audience": {
                "student_types": ["regular"],
                "statuses": ["active"]
            }
        }
    }
    
    return jsonify({
        "success": True,
        "templates": templates
    }), 200

# OPTIONS handlers for CORS
@campaigns_bp.route('/', methods=['OPTIONS'])
@campaigns_bp.route('/<int:campaign_id>/targets', methods=['OPTIONS'])  
@campaigns_bp.route('/<int:campaign_id>/launch', methods=['OPTIONS'])
@campaigns_bp.route('/templates', methods=['OPTIONS'])
def handle_options():
    """Handle OPTIONS requests for CORS"""
    return '', 200 