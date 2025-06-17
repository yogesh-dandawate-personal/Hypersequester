#!/bin/bash

# Hypersequester Setup Script
# This script sets up the development environment

set -e

echo "🌲 Setting up Hypersequester Development Environment"
echo "=================================================="

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

node_version=$(node --version)
echo "✅ Node.js version check passed: $node_version"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/{uploads,results}
mkdir -p logs
mkdir -p config

# Set up environment variables
echo "⚙️ Setting up environment variables..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Hypersequester Environment Variables
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://localhost/hypersequester_dev
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
UPLOAD_FOLDER=data/uploads
RESULTS_FOLDER=data/results
EOF
    echo "✅ Created .env file with default values"
else
    echo "✅ .env file already exists"
fi

# Initialize database (if PostgreSQL is running)
echo "🗄️ Checking database connection..."
if command -v psql &> /dev/null; then
    if psql -h localhost -U postgres -c '\q' 2>/dev/null; then
        echo "✅ PostgreSQL is running"
        
        # Create database if it doesn't exist
        createdb hypersequester_dev 2>/dev/null || echo "Database already exists"
        
        # Run migrations (when implemented)
        # python src/manage.py db upgrade
    else
        echo "⚠️ PostgreSQL is not running. Please start PostgreSQL and run database migrations manually."
    fi
else
    echo "⚠️ PostgreSQL client not found. Please install PostgreSQL."
fi

# Check Redis connection
echo "🔄 Checking Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️ Redis is not running. Please start Redis for background task processing."
    fi
else
    echo "⚠️ Redis client not found. Please install Redis."
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the development server: python src/main.py"
echo "3. Open your browser to: http://localhost:5000"
echo ""
echo "For Docker deployment:"
echo "docker-compose up --build"
