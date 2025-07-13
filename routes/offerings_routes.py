from flask import Blueprint, request, jsonify
from models.database import DatabaseManager, FacilitatorRepository
from middleware.auth_required import token_required
import logging

# Create blueprint
offerings_bp = Blueprint('offerings', __name__)

# Initialize database
db_manager = DatabaseManager()
facilitator_repo = FacilitatorRepository(db_manager)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================================================================
# OFFERING MANAGEMENT ENDPOINTS (Alternative organization)
# ================================================================================

@offerings_bp.route('/', methods=['GET'])
@token_required
def list_offerings():
    """List all offerings for the current facilitator with optional filtering"""
    try:
        facilitator_id = request.facilitator_id
        
        # Get query parameters for filtering
        category = request.args.get('category')
        active_only = request.args.get('active', 'true').lower() == 'true'
        
        # Get all offerings for the facilitator
        offerings = facilitator_repo.get_facilitator_offerings(facilitator_id)
        
        # Apply filters
        if category:
            offerings = [o for o in offerings if o.get('category', '').lower() == category.lower()]
        
        if not active_only:
            # If active_only is False, we need to get inactive offerings too
            # For now, the repository only returns active offerings
            pass
        
        return jsonify({
            "success": True,
            "offerings": offerings,
            "count": len(offerings),
            "filters": {
                "category": category,
                "active_only": active_only
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing offerings: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to list offerings"
        }), 500

@offerings_bp.route('/', methods=['POST'])
@token_required
def create_new_offering():
    """Create a new offering for the current facilitator"""
    try:
        facilitator_id = request.facilitator_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Request body is required"
            }), 400
        
        # Validate required fields
        required_fields = ['title']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "message": f"Required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate data types and constraints
        if len(data.get('title', '')) > 255:
            return jsonify({
                "error": "Invalid data",
                "message": "Title cannot exceed 255 characters"
            }), 400
        
        # Prepare offering data
        offering_data = {
            "title": data.get("title").strip(),
            "description": data.get("description", "").strip(),
            "category": data.get("category", "").strip(),
            "basic_info": data.get("basic_info"),
            "details": data.get("details"),
            "price_schedule": data.get("price_schedule")
        }
        
        # Create the offering
        offering_id = facilitator_repo.create_offering(facilitator_id, offering_data)
        
        if not offering_id:
            return jsonify({
                "error": "Creation failed",
                "message": "Failed to create offering"
            }), 500
        
        # Get the created offering details
        offerings = facilitator_repo.get_facilitator_offerings(facilitator_id)
        created_offering = next((o for o in offerings if o['id'] == offering_id), None)
        
        return jsonify({
            "success": True,
            "message": "Offering created successfully",
            "offering": created_offering
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating offering: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to create offering"
        }), 500

@offerings_bp.route('/<int:offering_id>', methods=['GET'])
@token_required
def get_offering_by_id(offering_id):
    """Get a specific offering by ID (must belong to current facilitator)"""
    try:
        facilitator_id = request.facilitator_id
        
        # Verify ownership
        if not facilitator_repo.verify_offering_ownership(facilitator_id, offering_id):
            return jsonify({
                "error": "Access denied",
                "message": "You don't have permission to access this offering"
            }), 403
        
        # Get offering details
        offerings = facilitator_repo.get_facilitator_offerings(facilitator_id)
        offering = next((o for o in offerings if o['id'] == offering_id), None)
        
        if not offering:
            return jsonify({
                "error": "Offering not found",
                "message": "Offering not found or inactive"
            }), 404
        
        return jsonify({
            "success": True,
            "offering": offering
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching offering: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch offering"
        }), 500

@offerings_bp.route('/<int:offering_id>', methods=['PUT'])
@token_required
def update_offering_by_id(offering_id):
    """Update a specific offering by ID (must belong to current facilitator)"""
    try:
        facilitator_id = request.facilitator_id
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Request body is required"
            }), 400
        
        # Verify ownership
        if not facilitator_repo.verify_offering_ownership(facilitator_id, offering_id):
            return jsonify({
                "error": "Access denied",
                "message": "You don't have permission to update this offering"
            }), 403
        
        # Validate data constraints
        if data.get('title') and len(data.get('title', '')) > 255:
            return jsonify({
                "error": "Invalid data",
                "message": "Title cannot exceed 255 characters"
            }), 400
        
        # Prepare update data (only include fields that are provided)
        update_data = {}
        updatable_fields = ['title', 'description', 'category', 'basic_info', 'details', 'price_schedule']
        
        for field in updatable_fields:
            if field in data:
                if field in ['title', 'description', 'category'] and data[field] is not None:
                    update_data[field] = data[field].strip() if isinstance(data[field], str) else data[field]
                else:
                    update_data[field] = data[field]
        
        if not update_data:
            return jsonify({
                "error": "No valid fields to update",
                "message": "No updatable fields provided"
            }), 400
        
        # Update the offering
        facilitator_repo.update_offering(offering_id, facilitator_id, update_data)
        
        # Get updated offering
        offerings = facilitator_repo.get_facilitator_offerings(facilitator_id)
        updated_offering = next((o for o in offerings if o['id'] == offering_id), None)
        
        return jsonify({
            "success": True,
            "message": "Offering updated successfully",
            "offering": updated_offering
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating offering: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to update offering"
        }), 500

@offerings_bp.route('/<int:offering_id>', methods=['DELETE'])
@token_required
def delete_offering_by_id(offering_id):
    """Soft delete a specific offering by ID (must belong to current facilitator)"""
    try:
        facilitator_id = request.facilitator_id
        
        # Verify ownership
        if not facilitator_repo.verify_offering_ownership(facilitator_id, offering_id):
            return jsonify({
                "error": "Access denied",
                "message": "You don't have permission to delete this offering"
            }), 403
        
        # Check if offering exists and is active
        offerings = facilitator_repo.get_facilitator_offerings(facilitator_id)
        offering = next((o for o in offerings if o['id'] == offering_id), None)
        
        if not offering:
            return jsonify({
                "error": "Offering not found",
                "message": "Offering not found or already inactive"
            }), 404
        
        # Soft delete by setting is_active to False
        # Note: We need to add this method to the repository or use a workaround
        try:
            # Prepare update data to deactivate
            update_data = {"is_active": False}
            facilitator_repo.update_offering(offering_id, facilitator_id, update_data)
            
            return jsonify({
                "success": True,
                "message": "Offering deleted successfully"
            }), 200
            
        except Exception:
            # Fallback: Use ORM method to deactivate offering
            facilitator_repo.deactivate_offering(offering_id)
            
            return jsonify({
                "success": True,
                "message": "Offering deleted successfully"
            }), 200
        
    except Exception as e:
        logger.error(f"Error deleting offering: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to delete offering"
        }), 500

@offerings_bp.route('/<int:offering_id>/activate', methods=['PUT'])
@token_required
def activate_offering(offering_id):
    """Reactivate a previously deactivated offering"""
    try:
        facilitator_id = request.facilitator_id
        
        # Verify ownership (need to check even inactive offerings)
        if not facilitator_repo.verify_offering_ownership(facilitator_id, offering_id):
            return jsonify({
                "error": "Access denied",
                "message": "You don't have permission to access this offering"
            }), 403
        
        # Reactivate the offering
        if not facilitator_repo.activate_offering(offering_id):
            return jsonify({
                "error": "Activation failed",
                "message": "Failed to activate offering"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Offering activated successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error activating offering: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to activate offering"
        }), 500

# ================================================================================
# OFFERING STATISTICS AND ANALYTICS
# ================================================================================

@offerings_bp.route('/stats', methods=['GET'])
@token_required
def get_offering_statistics():
    """Get statistics about the facilitator's offerings"""
    try:
        facilitator_id = request.facilitator_id
        
        # Get statistics using ORM method
        stats = facilitator_repo.get_offering_statistics(facilitator_id)
        
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching offering statistics: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch offering statistics"
        }), 500

# ================================================================================
# BULK OPERATIONS
# ================================================================================

@offerings_bp.route('/bulk/update', methods=['PUT'])
@token_required
def bulk_update_offerings():
    """Update multiple offerings at once"""
    try:
        facilitator_id = request.facilitator_id
        data = request.get_json()
        
        if not data or 'offerings' not in data:
            return jsonify({
                "error": "Invalid data",
                "message": "Array of offerings with IDs is required"
            }), 400
        
        offerings_to_update = data['offerings']
        
        if not isinstance(offerings_to_update, list):
            return jsonify({
                "error": "Invalid data",
                "message": "Offerings must be an array"
            }), 400
        
        updated_count = 0
        errors = []
        
        for offering_data in offerings_to_update:
            if 'id' not in offering_data:
                errors.append("Missing ID for offering")
                continue
            
            offering_id = offering_data['id']
            
            # Verify ownership
            if not facilitator_repo.verify_offering_ownership(facilitator_id, offering_id):
                errors.append(f"Access denied for offering ID {offering_id}")
                continue
            
            # Prepare update data
            update_data = {}
            updatable_fields = ['title', 'description', 'category', 'basic_info', 'details', 'price_schedule']
            
            for field in updatable_fields:
                if field in offering_data:
                    update_data[field] = offering_data[field]
            
            if update_data:
                try:
                    facilitator_repo.update_offering(offering_id, facilitator_id, update_data)
                    updated_count += 1
                except Exception as e:
                    errors.append(f"Failed to update offering ID {offering_id}: {str(e)}")
        
        return jsonify({
            "success": True,
            "message": f"Bulk update completed. Updated {updated_count} offerings.",
            "updated_count": updated_count,
            "errors": errors
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to perform bulk update"
        }), 500

@offerings_bp.route('/bulk/delete', methods=['DELETE'])
@token_required
def bulk_delete_offerings():
    """Soft delete multiple offerings at once"""
    try:
        facilitator_id = request.facilitator_id
        data = request.get_json()
        
        if not data or 'offering_ids' not in data:
            return jsonify({
                "error": "Invalid data",
                "message": "Array of offering IDs is required"
            }), 400
        
        offering_ids = data['offering_ids']
        
        if not isinstance(offering_ids, list):
            return jsonify({
                "error": "Invalid data",
                "message": "offering_ids must be an array"
            }), 400
        
        deleted_count = 0
        errors = []
        
        for offering_id in offering_ids:
            # Verify ownership
            if not facilitator_repo.verify_offering_ownership(facilitator_id, offering_id):
                errors.append(f"Access denied for offering ID {offering_id}")
                continue
            
            try:
                # Soft delete using ORM method
                if facilitator_repo.deactivate_offering(offering_id):
                    deleted_count += 1
                else:
                    errors.append(f"Failed to delete offering ID {offering_id}")
            except Exception as e:
                errors.append(f"Failed to delete offering ID {offering_id}: {str(e)}")
        
        return jsonify({
            "success": True,
            "message": f"Bulk delete completed. Deleted {deleted_count} offerings.",
            "deleted_count": deleted_count,
            "errors": errors
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to perform bulk delete"
        }), 500
