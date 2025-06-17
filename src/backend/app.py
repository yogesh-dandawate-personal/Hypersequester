"""
Flask Application Factory
"""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from .config import Config
from .routes import api_bp
from .models import db

def create_app(config_class=Config):
    """Create and configure Flask application"""
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'hypersequester'}
    
    # Root endpoint
    @app.route('/')
    def index():
        return {
            'message': 'Hypersequester API',
            'version': '1.0.0',
            'description': 'Hyperspectral Forest Carbon Assessment Platform'
        }
    
    return app
