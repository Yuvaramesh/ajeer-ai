import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ajeer_dashboard')
    
    # Qdrant Vector DB Configuration
    QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
    QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', None)
    QDRANT_COLLECTION_NAME = 'faqs_collection'
    
    # Google API Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Currency Converter
    CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY', '')
    
    # Flask Configuration
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # RAG Configuration
    EMBEDDING_MODEL = 'models/embedding-001'
    LLM_MODEL = 'gemini-2.5-flash-lite'
    SIMILARITY_THRESHOLD = 0.7

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/ajeer_dashboard_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
