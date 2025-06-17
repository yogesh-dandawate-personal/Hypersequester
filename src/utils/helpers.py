"""
Utility helper functions
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('hypersequester.log')
        ]
    )
    
    return logging.getLogger(__name__)

def ensure_directory(path: str) -> Path:
    """Ensure directory exists, create if it doesn't"""
    
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def load_json_config(config_path: str) -> Dict[str, Any]:
    """Load JSON configuration file"""
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in config file {config_path}: {e}")
        return {}

def save_json_config(config: Dict[str, Any], config_path: str) -> bool:
    """Save configuration to JSON file"""
    
    try:
        ensure_directory(os.path.dirname(config_path))
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2, default=str)
        return True
    except Exception as e:
        logging.error(f"Error saving config to {config_path}: {e}")
        return False

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def validate_coordinates(coordinates: list) -> bool:
    """Validate geographic coordinates"""
    
    if not isinstance(coordinates, list) or len(coordinates) < 3:
        return False
    
    for coord in coordinates:
        if not isinstance(coord, list) or len(coord) != 2:
            return False
        
        lon, lat = coord
        if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
            return False
    
    return True

def generate_unique_filename(base_name: str, extension: str, directory: str = "") -> str:
    """Generate unique filename with timestamp"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.{extension}"
    
    if directory:
        return os.path.join(directory, filename)
    
    return filename

def calculate_carbon_metrics(carbon_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate derived carbon metrics"""
    
    total_carbon_kg = carbon_data.get('total_carbon_kg', 0)
    area_hectares = carbon_data.get('area_hectares', 1)
    
    # Convert to tonnes
    total_carbon_tonnes = total_carbon_kg / 1000
    
    # Calculate CO2 equivalent (carbon * 3.67)
    co2_equivalent_tonnes = total_carbon_tonnes * 3.67
    
    # Calculate density per hectare
    carbon_density = co2_equivalent_tonnes / area_hectares if area_hectares > 0 else 0
    
    return {
        'total_carbon_tonnes': total_carbon_tonnes,
        'co2_equivalent_tonnes': co2_equivalent_tonnes,
        'carbon_density_tonnes_per_hectare': carbon_density
    }
