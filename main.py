from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from middleware.subdomain_middleware import init_subdomain_middleware

from routes.phone_auth_routes import auth_bp
from routes.facilitator_routes import facilitator_bp
from routes.offerings_routes import offerings_bp
from routes.students_routes import students_bp
from routes.campaigns_routes import campaigns_bp
from routes.website_routes import website_bp
from routes.courses_routes import courses_bp
from routes.course_calling_routes import course_calling_bp
from routes.general_calling_routes import general_calling_bp
from routes.public_website_routes import public_website_bp

app = Flask(__name__)

# Initialize subdomain middleware
init_subdomain_middleware(app)

# CORS policy: allow all origins
CORS(app,
     origins="*",
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True,
     expose_headers=["Content-Type", "Authorization"])

# Additional CORS handling for subdomain patterns
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        # Allow localhost subdomains for development
        if origin.endswith('.localhost:8080') or origin.endswith('.localhost:3000') or origin.endswith('.localhost:3031') or origin.endswith('.localhost:5173'):
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Health check endpoint
@app.route('/ping', methods=['GET'])
def ping():
    """Simple health check endpoint"""
    return jsonify({
        "status": "success",
        "message": "Server is running",
        "timestamp": "2025-06-21"
    }), 200

# API info endpoint
@app.route('/api/info', methods=['GET'])
def api_info():
    """API information"""
    return jsonify({
        "name": "Facilitator Backend API",
        "version": "0.1.0",
        "authentication": "Token based",
        "status": "healthy"
    }), 200

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(facilitator_bp, url_prefix='/api/facilitator')
app.register_blueprint(offerings_bp, url_prefix='/api/offerings')
app.register_blueprint(students_bp, url_prefix='/api/students')
app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
app.register_blueprint(courses_bp)
app.register_blueprint(course_calling_bp)
app.register_blueprint(general_calling_bp)
app.register_blueprint(website_bp)
# Register public website blueprint without url_prefix to handle root and /api/data routes
app.register_blueprint(public_website_bp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


