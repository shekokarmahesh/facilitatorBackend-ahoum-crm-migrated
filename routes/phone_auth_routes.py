from flask import Blueprint, jsonify, request
from models.database import DatabaseManager, FacilitatorRepository
from middleware.auth_required import (
    onboarding_token_required, 
    token_required, 
    generate_temp_token, 
    generate_auth_token,
    decode_token,
    get_token_from_request
)
import random
import re
from datetime import datetime
from config import Config
from twilio.rest import Client

auth_bp = Blueprint('auth', __name__)

# Initialize database components
db_manager = DatabaseManager()
facilitator_repo = FacilitatorRepository(db_manager)

def validate_phone_number(phone_number):
    """Validate phone number format"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone_number) is not None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_otp():
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_sms(phone_number, message):
    """
    Send SMS via Twilio
    """
    try:
        account_sid = Config.TWILIO_ACCOUNT_SID
        auth_token = Config.TWILIO_AUTH_TOKEN
        twilio_number = Config.TWILIO_PHONE_NUMBER

        if not all([account_sid, auth_token, twilio_number]):
            print("Twilio credentials are not set properly.")
            return False

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=twilio_number,
            to=phone_number
        )
        print(f"Twilio SMS sent to {phone_number}: SID {message.sid}")
        return True
    except Exception as e:
        print(f"Error sending SMS via Twilio: {e}")
        return False

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to phone number"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        # Validate input
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400
        
        if not validate_phone_number(phone_number):
            return jsonify({"error": "Invalid phone number format. Use international format (+1234567890)"}), 400
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in database
        otp_id = facilitator_repo.create_otp(phone_number, otp)
        
        if not otp_id:
            return jsonify({"error": "Failed to generate OTP. Please try again."}), 500
        
        # Send SMS
        sms_message = f"Your verification code is: {otp}. Valid for 10 minutes."
        if send_sms(phone_number, sms_message):
            return jsonify({
                "success": True,
                "message": "OTP sent successfully",
                "phone_number": phone_number
            }), 200
        else:
            return jsonify({"error": "Failed to send SMS. Please try again."}), 500
            
    except Exception as e:
        print(f"Error in send_otp: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and determine user flow - ENHANCED"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        
        # Validate input
        if not phone_number or not otp:
            return jsonify({"error": "Phone number and OTP are required"}), 400
        
        if not validate_phone_number(phone_number):
            return jsonify({"error": "Invalid phone number format"}), 400
        
        if len(otp) != 6 or not otp.isdigit():
            return jsonify({"error": "OTP must be 6 digits"}), 400
        
        # Verify OTP and get user status
        result = facilitator_repo.verify_otp_and_get_user_status(phone_number, otp)
        
        if result["success"]:
            if result["is_new_user"]:
                # Truly new user - create facilitator account and generate temporary token for onboarding
                facilitator_id = result["practitioner_id"]
                
                # Generate temporary token for onboarding
                temp_token = generate_temp_token(phone_number, facilitator_id)
                
                print(f"🔑 Generated onboarding token for new user:")
                print(f"   Phone: {phone_number}")
                print(f"   Facilitator ID: {facilitator_id}")
                print(f"   Token: {temp_token[:20]}...")
                
                return jsonify({
                    "success": True,
                    "is_new_user": True,
                    "needs_onboarding": True,
                    "redirect_to": "onboarding",
                    "message": "OTP verified. Please complete your profile.",
                    "current_step": 1,
                    "total_steps": 5,
                    "token": temp_token,
                    "token_type": "onboarding",
                    "prefilled_data": None
                }), 200
            else:
                # Existing practitioner - check if they need onboarding
                practitioner_id = result["practitioner_id"]
                needs_onboarding = result["needs_onboarding"]
                
                if needs_onboarding:
                    # Existing practitioner but needs CRM onboarding
                    temp_token = generate_temp_token(phone_number, practitioner_id)
                    
                    print(f"🔑 Generated onboarding token for existing user:")
                    print(f"   Phone: {phone_number}")
                    print(f"   Practitioner ID: {practitioner_id}")
                    print(f"   Token: {temp_token[:20]}...")
                    
                    # Get pre-filled data from calling system
                    prefilled_data = facilitator_repo.get_prefilled_basic_info(practitioner_id)
                    
                    return jsonify({
                        "success": True,
                        "is_new_user": False,
                        "needs_onboarding": True,
                        "redirect_to": "onboarding",
                        "message": "Welcome back! Please complete your CRM profile setup.",
                        "current_step": result.get("onboarding_step", 0) + 1,
                        "total_steps": 5,
                        "token": temp_token,
                        "token_type": "onboarding",
                        "prefilled_data": prefilled_data,
                        "has_calling_data": result.get("has_calling_data", False),
                        "calling_data": result.get("calling_data")
                    }), 200
                else:
                    # Fully onboarded practitioner - generate authentication token
                    auth_token = generate_auth_token(practitioner_id, phone_number)
                    
                    return jsonify({
                        "success": True,
                        "is_new_user": False,
                        "needs_onboarding": False,
                        "redirect_to": "dashboard",
                        "message": "Login successful",
                        "token": auth_token,
                        "token_type": "auth",
                        "facilitator": {
                            "id": practitioner_id,
                            "phone_number": phone_number,
                            "onboarding_step": result.get('onboarding_step', 0),
                            "crm_onboarding_completed": result.get('crm_onboarding_completed', True)
                        }
                    }), 200
        else:
            # Return the error from OTP verification
            return jsonify({"error": result.get("error", "OTP verification failed")}), 400
            
    except Exception as e:
        print(f"Error in verify_otp: {e}")
        return jsonify({"error": "Internal server error"}), 500

# 5-Step Onboarding Endpoints

@auth_bp.route('/onboarding/step1-basic-info', methods=['POST'])
@onboarding_token_required
def onboarding_step1_basic_info():
    """Step 1: Save basic information"""
    try:
        # Get facilitator_id from decorated request
        facilitator_id = request.temp_facilitator_id
        
        # Get data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'location']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Validate email format
        if not validate_email(data.get('email')):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Save basic info
        basic_info = {
            "first_name": data.get('first_name'),
            "last_name": data.get('last_name'),
            "email": data.get('email'),
            "location": data.get('location')
        }
        
        if facilitator_repo.save_basic_info(facilitator_id, basic_info):
            return jsonify({
                "success": True,
                "message": "Basic information saved successfully",
                "current_step": 1,
                "next_step": 2,
                "total_steps": 5
            }), 200
        else:
            return jsonify({"error": "Failed to save basic information"}), 500
            
    except Exception as e:
        print(f"Error in onboarding step 1: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/onboarding/step2-visual-profile', methods=['POST'])
@onboarding_token_required
def onboarding_step2_visual_profile():
    """Step 2: Save visual profile"""
    try:
        # Get facilitator_id from decorated request
        facilitator_id = request.temp_facilitator_id
        
        # Check if step 1 is completed
        onboarding_status = facilitator_repo.get_facilitator_onboarding_status(facilitator_id)
        if "error" in onboarding_status:
            return jsonify(onboarding_status), 400
            
        current_step = onboarding_status.get("current_step", 0)
        if current_step < 1:
            return jsonify({"error": "Please complete previous steps first"}), 400
        
        # Get data
        data = request.get_json()
        
        # Prepare visual profile data
        visual_data = {
            "banner_urls": data.get('banner_urls', []),
            "profile_url": data.get('profile_url')
        }
        
        if facilitator_repo.save_visual_profile(facilitator_id, visual_data):
            return jsonify({
                "success": True,
                "message": "Visual profile saved successfully",
                "current_step": 2,
                "next_step": 3,
                "total_steps": 5
            }), 200
        else:
            return jsonify({"error": "Failed to save visual profile"}), 500
            
    except Exception as e:
        print(f"Error in onboarding step 2: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/onboarding/step3-professional-details', methods=['POST'])
@onboarding_token_required
def onboarding_step3_professional_details():
    """Step 3: Save professional details"""
    try:
        # Get facilitator_id from decorated request
        facilitator_id = request.temp_facilitator_id
        
        # Check if step 2 is completed
        onboarding_status = facilitator_repo.get_facilitator_onboarding_status(facilitator_id)
        if "error" in onboarding_status:
            return jsonify(onboarding_status), 400
            
        current_step = onboarding_status.get("current_step", 0)
        if current_step < 2:
            return jsonify({"error": "Please complete previous steps first"}), 400
        
        # Get data
        data = request.get_json()
        
        # Prepare professional details
        professional_data = {
            "languages": data.get('languages', []),
            "teaching_styles": data.get('teaching_styles', []),
            "specializations": data.get('specializations', [])
        }
        
        if facilitator_repo.save_professional_details(facilitator_id, professional_data):
            return jsonify({
                "success": True,
                "message": "Professional details saved successfully",
                "current_step": 3,
                "next_step": 4,
                "total_steps": 5
            }), 200
        else:
            return jsonify({"error": "Failed to save professional details"}), 500
            
    except Exception as e:
        print(f"Error in onboarding step 3: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/onboarding/step4-bio-about', methods=['POST'])
@onboarding_token_required
def onboarding_step4_bio_about():
    """Step 4: Save bio and about information"""
    try:
        # Get facilitator_id from decorated request
        facilitator_id = request.temp_facilitator_id
        
        # Check if step 3 is completed
        onboarding_status = facilitator_repo.get_facilitator_onboarding_status(facilitator_id)
        if "error" in onboarding_status:
            return jsonify(onboarding_status), 400
            
        current_step = onboarding_status.get("current_step", 0)
        if current_step < 3:
            return jsonify({"error": "Please complete previous steps first"}), 400
        
        # Get data
        data = request.get_json()
        
        # Prepare bio and about data
        bio_data = {
            "short_bio": data.get('short_bio'),
            "detailed_intro": data.get('detailed_intro')
        }
        
        if facilitator_repo.save_bio_about(facilitator_id, bio_data):
            return jsonify({
                "success": True,
                "message": "Bio and about information saved successfully",
                "current_step": 4,
                "next_step": 5,
                "total_steps": 5
            }), 200
        else:
            return jsonify({"error": "Failed to save bio and about information"}), 500
            
    except Exception as e:
        print(f"Error in onboarding step 4: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/onboarding/step5-experience-certifications', methods=['POST'])
@onboarding_token_required
def onboarding_step5_experience_certifications():
    """Step 5: Save experience and certifications - Complete onboarding"""
    try:
        # Get info from decorated request
        facilitator_id = request.temp_facilitator_id
        phone_number = request.temp_phone_number
        
        # Check if step 4 is completed
        onboarding_status = facilitator_repo.get_facilitator_onboarding_status(facilitator_id)
        if "error" in onboarding_status:
            return jsonify(onboarding_status), 400
            
        current_step = onboarding_status.get("current_step", 0)
        if current_step < 4:
            return jsonify({"error": "Please complete previous steps first"}), 400
        
        # Get data
        data = request.get_json()
        
        # Prepare experience and certifications data - separate them properly
        experience_data = data.get('work_experiences', [])
        certification_data = data.get('certifications', [])
        
        if facilitator_repo.save_experience_certifications(facilitator_id, experience_data, certification_data):
            # Generate authentication token for completed onboarding
            auth_token = generate_auth_token(facilitator_id, phone_number)
            
            # Get complete profile for response
            complete_profile = facilitator_repo.get_complete_facilitator_profile(facilitator_id)
            
            return jsonify({
                "success": True,
                "message": "Onboarding completed successfully! Welcome aboard!",
                "current_step": 5,
                "total_steps": 5,
                "onboarding_complete": True,
                "token": auth_token,
                "token_type": "auth",
                "facilitator": {
                    "id": facilitator_id,
                    "phone_number": phone_number,
                    "name": f"{complete_profile['basic_info']['first_name']} {complete_profile['basic_info']['last_name']}" if complete_profile.get('basic_info') else None
                },
                "redirect_to": "dashboard"
            }), 200
        else:
            return jsonify({"error": "Failed to save experience and certifications"}), 500
            
    except Exception as e:
        print(f"Error in onboarding step 5: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/onboarding/status', methods=['GET'])
@onboarding_token_required
def get_onboarding_status():
    """Get current onboarding status"""
    try:
        # Get facilitator_id from decorated request
        facilitator_id = request.temp_facilitator_id
        
        # Get current onboarding status
        onboarding_status = facilitator_repo.get_facilitator_onboarding_status(facilitator_id)
        
        if "error" in onboarding_status:
            return jsonify(onboarding_status), 400
            
        current_step = onboarding_status.get("current_step", 0)
        
        return jsonify({
            "success": True,
            "facilitator_id": facilitator_id,
            "current_step": current_step,
            "total_steps": 5,
            "next_step": current_step + 1 if current_step < 5 else None,
            "is_complete": current_step >= 5,
            "detailed_status": onboarding_status
        }), 200
        
    except Exception as e:
        print(f"Error getting onboarding status: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user - with token-based auth, logout is handled client-side"""
    try:
        # In JWT-based authentication, logout is typically handled client-side
        # by removing the token from storage. Server-side logout can be implemented
        # with token blacklisting if needed.
        
        return jsonify({
            "success": True,
            "message": "Logged out successfully. Please remove the token from your storage."
        }), 200
        
    except Exception as e:
        print(f"Error in logout: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user information - standard /me endpoint"""
    try:
        token = get_token_from_request()
        
        if not token:
            return jsonify({
                "error": "No authentication token provided"
            }), 401
        
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                "error": "Invalid or expired token"
            }), 401
        
        if payload.get('type') == 'auth' and payload.get('is_authenticated'):
            # Fully authenticated user - get full profile
            facilitator_id = payload.get('facilitator_id')
            phone_number = payload.get('phone_number')
            
            # Get user details from database
            try:
                user_profile = facilitator_repo.get_complete_facilitator_profile(facilitator_id)
                
                if user_profile and user_profile.get('success'):
                    profile_data = user_profile.get('profile', {})
                    
                    return jsonify({
                        "id": facilitator_id,
                        "phone_number": phone_number,
                        "email": profile_data.get('basic_info', {}).get('email'),
                        "displayName": f"{profile_data.get('basic_info', {}).get('first_name', '')} {profile_data.get('basic_info', {}).get('last_name', '')}".strip(),
                        "firstName": profile_data.get('basic_info', {}).get('first_name'),
                        "lastName": profile_data.get('basic_info', {}).get('last_name'),
                        "photoURL": profile_data.get('visual_profile', {}).get('profile_url'),
                        "location": profile_data.get('basic_info', {}).get('location'),
                        "phoneNumber": phone_number,
                        "isAuthenticated": True,
                        "userType": "facilitator",
                        "onboardingComplete": profile_data.get('onboarding_complete', False)
                    }), 200
                else:
                    # Fallback for authenticated user without complete profile
                    return jsonify({
                        "id": facilitator_id,
                        "phone_number": phone_number,
                        "phoneNumber": phone_number,
                        "displayName": "Facilitator",
                        "isAuthenticated": True,
                        "userType": "facilitator",
                        "onboardingComplete": False
                    }), 200
                    
            except Exception as profile_error:
                print(f"Error getting user profile: {profile_error}")
                # Fallback response
                return jsonify({
                    "id": facilitator_id,
                    "phone_number": phone_number,
                    "phoneNumber": phone_number,
                    "displayName": "Facilitator",
                    "isAuthenticated": True,
                    "userType": "facilitator",
                    "onboardingComplete": False
                }), 200
                
        elif payload.get('type') == 'onboarding' and payload.get('otp_verified'):
            # User in onboarding process
            return jsonify({
                "id": payload.get('temp_facilitator_id'),
                "phone_number": payload.get('temp_phone_number'),
                "phoneNumber": payload.get('temp_phone_number'),
                "displayName": "New Facilitator",
                "isAuthenticated": False,
                "userType": "facilitator",
                "onboardingComplete": False,
                "onboardingInProgress": True
            }), 200
        else:
            return jsonify({
                "error": "Invalid token type"
            }), 401
            
    except Exception as e:
        print(f"Error in /me endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/auth-status', methods=['GET'])
@auth_bp.route('/status', methods=['GET'])  # Add an alias for the frontend
def auth_status():
    """Check current authentication status using token"""
    try:
        token = get_token_from_request()
        
        if not token:
            return jsonify({
                "authenticated": False,
                "status": "not_authenticated",
                "message": "No token provided"
            }), 200
        
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                "authenticated": False,
                "status": "not_authenticated",
                "message": "Invalid or expired token"
            }), 200
        
        if payload.get('type') == 'auth' and payload.get('is_authenticated'):
            # Fully authenticated user
            return jsonify({
                "authenticated": True,
                "facilitator_id": payload.get('facilitator_id'),
                "phone_number": payload.get('phone_number'),
                "status": "authenticated",
                "token_type": "auth"
            }), 200
        elif payload.get('type') == 'onboarding' and payload.get('otp_verified'):
            # User in onboarding process - get current step
            temp_facilitator_id = payload.get('temp_facilitator_id')
            onboarding_status = facilitator_repo.get_facilitator_onboarding_status(temp_facilitator_id)
            
            if "error" in onboarding_status:
                current_step = 0
            else:
                current_step = onboarding_status.get("current_step", 0)
                
            return jsonify({
                "authenticated": False,
                "temp_facilitator_id": temp_facilitator_id,
                "temp_phone_number": payload.get('temp_phone_number'),
                "status": "onboarding_pending",
                "current_step": current_step,
                "total_steps": 5,
                "next_step": current_step + 1 if current_step < 5 else None,
                "token_type": "onboarding"
            }), 200
        else:
            # Invalid token type
            return jsonify({
                "authenticated": False,
                "status": "not_authenticated",
                "message": "Invalid token type"
            }), 200
            
    except Exception as e:
        print(f"Error in session_status: {e}")
        return jsonify({"error": "Internal server error"}), 500

# CORS preflight handling
@auth_bp.route('/send-otp', methods=['OPTIONS'])
@auth_bp.route('/verify-otp', methods=['OPTIONS'])
@auth_bp.route('/onboarding/step1-basic-info', methods=['OPTIONS'])
@auth_bp.route('/onboarding/step2-visual-profile', methods=['OPTIONS'])
@auth_bp.route('/onboarding/step3-professional-details', methods=['OPTIONS'])
@auth_bp.route('/onboarding/step4-bio-about', methods=['OPTIONS'])
@auth_bp.route('/onboarding/step5-experience-certifications', methods=['OPTIONS'])
@auth_bp.route('/onboarding/status', methods=['OPTIONS'])
@auth_bp.route('/logout', methods=['OPTIONS'])
@auth_bp.route('/me', methods=['OPTIONS'])
@auth_bp.route('/status', methods=['OPTIONS'])
@auth_bp.route('/auth-status', methods=['OPTIONS'])
def handle_options():
    """Handle CORS preflight requests"""
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response, 200
