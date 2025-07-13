from functools import wraps
from flask import jsonify, request
import jwt
import os

def token_required(f):
    """
    Decorator to require valid JWT token authentication
    Replaces session-based authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    "error": "Invalid token format",
                    "message": "Token should be provided as 'Bearer <token>'"
                }), 401
        
        if not token:
            return jsonify({
                "error": "Authentication required",
                "message": "Token is missing"
            }), 401
        
        try:
            # Decode the JWT token
            secret_key = os.getenv('JWT_SECRET', 'your-jwt-secret-key-change-in-production')
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            facilitator_id = data['facilitator_id']
            phone_number = data['phone_number']
            
            # Add to request for easy access in routes
            request.facilitator_id = facilitator_id
            request.phone_number = phone_number
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token expired",
                "message": "Please login again"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid token",
                "message": "Please login again"
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def onboarding_token_required(f):
    """
    Decorator to require valid onboarding token
    Used for routes that should only be accessible during onboarding
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({
                    "error": "Invalid token format",
                    "message": "Token should be provided as 'Bearer <token>'"
                }), 401
        
        if not token:
            return jsonify({
                "error": "Authentication required",
                "message": "Onboarding token is missing"
            }), 401
        
        try:
            # Decode the JWT token
            secret_key = os.getenv('JWT_SECRET', 'your-jwt-secret-key-change-in-production')
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Verify this is an onboarding token
            if data.get('token_type') != 'onboarding':
                return jsonify({
                    "error": "Invalid token type",
                    "message": "This endpoint requires onboarding token"
                }), 401
            
            facilitator_id = data['facilitator_id']
            phone_number = data['phone_number']
            
            # Add to request for easy access in routes
            request.temp_facilitator_id = facilitator_id
            request.temp_phone_number = phone_number
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token expired",
                "message": "Please verify OTP again"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid token",
                "message": "Please verify OTP again"
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_token(f):
    """
    Decorator that provides token info if available but doesn't require it
    Useful for public endpoints that can benefit from user context
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
                
                # Try to decode the token
                secret_key = os.getenv('JWT_SECRET', 'your-jwt-secret-key-change-in-production')
                data = jwt.decode(token, secret_key, algorithms=['HS256'])
                
                # Add to request if valid
                request.facilitator_id = data.get('facilitator_id')
                request.phone_number = data.get('phone_number')
                request.is_authenticated = True
                
            except (IndexError, jwt.InvalidTokenError, jwt.ExpiredSignatureError):
                # Token is invalid or expired, but that's okay for optional auth
                request.facilitator_id = None
                request.phone_number = None
                request.is_authenticated = False
        else:
            # No token provided, but that's okay for optional auth
            request.facilitator_id = None
            request.phone_number = None
            request.is_authenticated = False
        
        return f(*args, **kwargs)
    
    return decorated_function
