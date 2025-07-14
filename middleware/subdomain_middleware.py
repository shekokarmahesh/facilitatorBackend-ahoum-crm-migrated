from flask import request, jsonify, g
from functools import wraps
from models.database import DatabaseManager, FacilitatorRepository
import logging

# Initialize database manager and repository
db_manager = DatabaseManager()
facilitator_repo = FacilitatorRepository(db_manager)

def get_subdomain_from_host(host):
    """Extract subdomain from host header"""
    try:
        # Remove port if present
        if ':' in host:
            host_without_port = host.split(':')[0]
        else:
            host_without_port = host
        
        # Check if it's a subdomain of ahoum.com (production)
        if host_without_port.endswith('.ahoum.com'):
            subdomain = host_without_port.replace('.ahoum.com', '')
            
            # Ignore www and other common subdomains for main site
            if subdomain and subdomain not in ['www', 'api', 'facilitatorCRM']:
                return subdomain
        
        # Check if it's a localhost subdomain (development)
        elif host_without_port.endswith('.localhost'):
            subdomain = host_without_port.replace('.localhost', '')
            
            # Ignore common reserved subdomains
            if subdomain and subdomain not in ['www', 'api', 'admin']:
                return subdomain
        
        return None
    except Exception:
        return None

def subdomain_context():
    """Middleware to add subdomain context to requests"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get subdomain from request
            host = request.headers.get('Host', '')
            subdomain = get_subdomain_from_host(host)
            
            # Add subdomain to request context
            g.subdomain = subdomain
            
            # If it's a subdomain request, get practitioner data
            if subdomain:
                try:
                    practitioner_data = facilitator_repo.get_practitioner_by_subdomain(subdomain)
                    g.subdomain_practitioner = practitioner_data
                except Exception as e:
                    logging.error(f"Error getting practitioner data for subdomain {subdomain}: {e}")
                    g.subdomain_practitioner = None
            else:
                g.subdomain_practitioner = None
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_valid_subdomain():
    """Decorator to require a valid published subdomain"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'subdomain') or not g.subdomain:
                return jsonify({
                    'error': 'Website not found',
                    'message': 'This website is not published or does not exist'
                }), 404
            
            if not hasattr(g, 'subdomain_practitioner') or not g.subdomain_practitioner:
                return jsonify({
                    'error': 'Website not found',
                    'message': 'This website is not published or does not exist'
                }), 404
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class SubdomainMiddleware:
    """WSGI middleware class for subdomain handling"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Add subdomain context to WSGI environ
        host = environ.get('HTTP_HOST', '')
        subdomain = get_subdomain_from_host(host)
        environ['subdomain'] = subdomain
        
        return self.app(environ, start_response)

def init_subdomain_middleware(app):
    """Initialize subdomain middleware with Flask app"""
    
    @app.before_request
    def before_request():
        """Add subdomain context before each request"""
        host = request.headers.get('Host', '')
        subdomain = get_subdomain_from_host(host)
        
        # Store in Flask's g object
        g.subdomain = subdomain
        g.subdomain_practitioner = None
        
        # Fetch practitioner data for ANY subdomain request (not just 'public' endpoints)
        if subdomain:
            try:
                practitioner_data = facilitator_repo.get_practitioner_by_subdomain(subdomain)
                g.subdomain_practitioner = practitioner_data
                logging.info(f"Subdomain middleware: Found practitioner data for {subdomain}: {practitioner_data is not None}")
            except Exception as e:
                logging.error(f"Error getting practitioner data for subdomain {subdomain}: {e}")
                g.subdomain_practitioner = None
    
    @app.context_processor
    def inject_subdomain():
        """Make subdomain available in templates"""
        return {
            'subdomain': getattr(g, 'subdomain', None),
            'subdomain_practitioner': getattr(g, 'subdomain_practitioner', None)
        } 