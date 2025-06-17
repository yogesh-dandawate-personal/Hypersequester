#!/usr/bin/env python3
"""
Hypersequester Main Application Entry Point
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from backend.app import create_app
from backend.config import Config

def main():
    """Main application entry point"""
    
    # Create Flask application
    app = create_app()
    
    # Get configuration
    config = Config()
    
    print("🌲 Hypersequester - Hyperspectral Forest Carbon Assessment Platform")
    print("=" * 70)
    print(f"Environment: {config.ENVIRONMENT}")
    print(f"Debug Mode: {config.DEBUG}")
    print(f"Database: {config.DATABASE_URL}")
    print(f"Host: {config.HOST}")
    print(f"Port: {config.PORT}")
    print("=" * 70)
    
    # Run the application
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )

if __name__ == "__main__":
    main()
