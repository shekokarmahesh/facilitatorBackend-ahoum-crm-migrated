import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Database Configuration - Use same database as calling system
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_EXPIRATION_DELTA = 24 * 60 * 60  # 24 hours in seconds
    
    # OTP Configuration
    OTP_EXPIRATION_MINUTES = 10
    OTP_LENGTH = 6
    
    # SMS Configuration (Twilio)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    # WhatsApp Configuration (WasenderAPI)
    WASENDER_API_KEY = os.getenv("WASENDER_API_KEY")
    WASENDER_PHONE_NUMBER = os.getenv("WASENDER_PHONE_NUMBER")
    WASENDER_SESSION_NAME = os.getenv("WASENDER_SESSION_NAME")
    
    # Application Settings
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS Settings
    ALLOWED_ORIGINS = [
        "https://preview--ahoum-crm.lovable.app",
        "http://localhost:8080",
        "http://127.0.0.1:8080", 
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # Allow subdomain patterns for local development
        "http://*.localhost:8080",
        "http://*.localhost:3000",
        "http://*.localhost:5173"
    ]
    
    # Calling System Integration
    INTELLIGENCE_API_URL = os.getenv("INTELLIGENCE_API_URL", "http://localhost:5000")
    LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Must be set in production

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 