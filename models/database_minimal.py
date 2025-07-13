"""
Minimal ORM Model for Migration Testing
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ARRAY, JSON, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Practitioner(Base):
    """Minimal practitioner model matching existing schema"""
    __tablename__ = 'practitioners'
    
    # Core fields that likely exist
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    practice_type = Column(String(100))
    location = Column(String(255))
    about_us = Column(Text)
    website_url = Column(String(500))
    is_contacted = Column(Boolean, default=False)
    contact_status = Column(String(50))
    notes = Column(Text)
    onboarding_step = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    subdomain = Column(String(50))
    website_published = Column(Boolean, default=False)
    website_status = Column(String(20), default='draft')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class DatabaseManager:
    """Minimal database manager for testing"""
    
    def __init__(self):
        self.engine = create_engine(Config.POSTGRES_URL, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._test_connection()
        logger.info("✅ Minimal DatabaseManager initialized")
    
    def _test_connection(self):
        """Test database connectivity"""
        try:
            with self.SessionLocal() as session:
                session.execute(text("SELECT 1"))
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def close_connection(self):
        """Close database connections"""
        self.engine.dispose()

def test_minimal_orm():
    """Test minimal ORM setup"""
    try:
        db_manager = DatabaseManager()
        
        with db_manager.get_session() as session:
            # Try to query with basic fields only
            practitioners = session.query(Practitioner.id, Practitioner.phone_number, Practitioner.name).limit(3).all()
        
        print("✅ Minimal ORM Test Successful!")
        print(f"✅ Found {len(practitioners)} practitioners:")
        
        for p in practitioners:
            print(f"   - ID: {p.id}, Phone: {p.phone_number}, Name: {p.name or 'Unknown'}")
        
        db_manager.close_connection()
        return True
        
    except Exception as e:
        print(f"❌ Minimal ORM test failed: {e}")
        return False

if __name__ == "__main__":
    test_minimal_orm()
