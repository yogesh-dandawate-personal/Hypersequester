"""
Database Models
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid

db = SQLAlchemy()

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    properties = db.relationship('Property', backref='owner', lazy=True)
    assessments = db.relationship('CarbonAssessment', backref='user', lazy=True)

class Property(db.Model):
    """Property/Study Area model"""
    __tablename__ = 'properties'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Geographic information
    polygon_coordinates = db.Column(JSON)  # GeoJSON polygon
    area_hectares = db.Column(db.Float)
    centroid_lat = db.Column(db.Float)
    centroid_lon = db.Column(db.Float)
    country = db.Column(db.String(100))
    state_province = db.Column(db.String(100))
    
    # Ownership information
    owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    owner_type = db.Column(db.String(50))  # Private, Government, NGO, Corporate
    land_use_type = db.Column(db.String(100))
    management_notes = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessments = db.relationship('CarbonAssessment', backref='property', lazy=True)

class CarbonAssessment(db.Model):
    """Carbon Assessment model"""
    __tablename__ = 'carbon_assessments'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(UUID(as_uuid=True), db.ForeignKey('properties.id'), nullable=False)
    
    # Assessment metadata
    assessment_date = db.Column(db.DateTime, nullable=False)
    sensor_info = db.Column(db.String(200))
    flight_altitude = db.Column(db.Float)
    weather_conditions = db.Column(db.String(200))
    
    # Processing information
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    processing_started_at = db.Column(db.DateTime)
    processing_completed_at = db.Column(db.DateTime)
    processing_parameters = db.Column(JSON)
    
    # Results
    total_carbon_tonnes = db.Column(db.Float)
    total_co2_equivalent_tonnes = db.Column(db.Float)
    carbon_density_tonnes_per_hectare = db.Column(db.Float)
    forest_types_detected = db.Column(JSON)
    assessment_confidence = db.Column(db.Float)
    
    # File paths
    input_file_path = db.Column(db.String(500))
    results_file_path = db.Column(db.String(500))
    kml_file_path = db.Column(db.String(500))
    report_file_path = db.Column(db.String(500))
    
    # Quality metrics
    quality_flags = db.Column(JSON)
    uncertainty_metrics = db.Column(JSON)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProcessingJob(db.Model):
    """Processing Job model for tracking background tasks"""
    __tablename__ = 'processing_jobs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    celery_task_id = db.Column(db.String(255), unique=True, nullable=False)
    
    # References
    assessment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('carbon_assessments.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    # Job information
    job_type = db.Column(db.String(100), nullable=False)  # carbon_assessment, species_classification, etc.
    status = db.Column(db.String(50), default='pending')
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    # Timing
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    estimated_completion = db.Column(db.DateTime)
    
    # Results and errors
    result = db.Column(JSON)
    error_message = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
