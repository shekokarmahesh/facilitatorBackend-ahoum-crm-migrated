from functools import wraps
from flask import jsonify, request, g
import jwt
import os
from datetime import datetime, timedelta

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-jwt-secret-change-in-production')
JWT_ALGORITHM = 'HS256'

def generate_temp_token(phone_number: str, facilitator_id: int):
    """Generate temporary token for onboarding process"""
    payload = {
        'temp_phone_number': phone_number,
        'temp_facilitator_id': facilitator_id,
        'otp_verified': True,
        'type': 'onboarding',
        'exp': datetime.utcnow() + timedelta(hours=2),  # 2 hour expiry
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_auth_token(facilitator_id: int, phone_number: str):
    """Generate authentication token for logged in users"""
    payload = {
        'facilitator_id': facilitator_id,
        'phone_number': phone_number,
        'is_authenticated': True,
        'type': 'auth',
        'exp': datetime.utcnow() + timedelta(days=7),  # 7 day expiry
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_request():
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None

def token_required(f):
    """
    Decorator to require valid authentication token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({
                "error": "Authentication required",
                "message": "Please provide a valid token"
            }), 401
        
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                "error": "Invalid token",
                "message": "Please login again"
            }), 401
        
        # Check if it's an auth token
        if payload.get('type') != 'auth' or not payload.get('is_authenticated'):
            return jsonify({
                "error": "Invalid token type",
                "message": "Please login again"
            }), 401
        
        # Set user info in Flask's g object and request object
        g.user = {
            'id': payload.get('facilitator_id'),
            'phone_number': payload.get('phone_number'),
            'is_authenticated': True
        }
        
        # Also set attributes on request object for easy access
        request.facilitator_id = payload.get('facilitator_id')
        request.phone_number = payload.get('phone_number')
        request.is_authenticated = True
        
        return f(*args, **kwargs)
    
    return decorated_function

def onboarding_token_required(f):
    """
    Decorator to require valid onboarding token
    Used for routes that should only be accessible during onboarding
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({
                "error": "Authentication required",
                "message": "Please verify OTP first"
            }), 401
        
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                "error": "Invalid token",
                "message": "Please verify OTP again"
            }), 401
        
        # Check if it's an onboarding token
        if payload.get('type') != 'onboarding' or not payload.get('otp_verified'):
            return jsonify({
                "error": "Invalid token type",
                "message": "Please verify OTP first"
            }), 401
        
        # Add temp info to request
        request.temp_phone_number = payload.get('temp_phone_number')
        request.temp_facilitator_id = payload.get('temp_facilitator_id')
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_token(f):
    """
    Decorator that provides token info if available but doesn't require it
    Useful for public endpoints that can benefit from user context
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if token:
            payload = decode_token(token)
            if payload:
                request.facilitator_id = payload.get('facilitator_id')
                request.phone_number = payload.get('phone_number')
                request.is_authenticated = payload.get('is_authenticated', False)
            else:
                request.facilitator_id = None
                request.phone_number = None
                request.is_authenticated = False
        else:
            request.facilitator_id = None
            request.phone_number = None
            request.is_authenticated = False
        
        return f(*args, **kwargs)
    
    return decorated_function
