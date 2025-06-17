"""
Application Configuration
"""

import os
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://localhost/hypersequester'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # Application settings
    ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'development'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5000)
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'data/uploads'
    RESULTS_FOLDER = os.environ.get('RESULTS_FOLDER') or 'data/results'
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
    # Processing settings
    PROCESSING_TIMEOUT = int(os.environ.get('PROCESSING_TIMEOUT') or 3600)  # 1 hour
    MAX_CONCURRENT_JOBS = int(os.environ.get('MAX_CONCURRENT_JOBS') or 4)
    
    # Spectral processing settings
    DEFAULT_PIXEL_SIZE = float(os.environ.get('DEFAULT_PIXEL_SIZE') or 1.0)
    SUPPORTED_FORMATS = ['AVIRIS', 'HySpex', 'PRISMA', 'EnMAP']
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create necessary directories
        Path(Config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(Config.RESULTS_FOLDER).mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENVIRONMENT = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENVIRONMENT = 'production'
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    ENVIRONMENT = 'testing'
    DATABASE_URL = 'sqlite:///:memory:'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
