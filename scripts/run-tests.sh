#!/bin/bash

# Test runner script for Hypersequester

set -e

echo "🧪 Running Hypersequester Test Suite"
echo "===================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest is not installed. Installing..."
    pip install pytest pytest-cov
fi

# Set environment variables for testing
export ENVIRONMENT=testing
export DATABASE_URL=sqlite:///:memory:
export CELERY_ALWAYS_EAGER=true

echo "🔬 Running Python tests..."
echo "-------------------------"

# Run Python tests with coverage
pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

# Check if Node.js tests exist and run them
if [ -f "package.json" ] && [ -d "src/frontend" ]; then
    echo ""
    echo "⚛️ Running Frontend tests..."
    echo "----------------------------"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing Node.js dependencies..."
        npm install
    fi
    
    # Run frontend tests
    npm test -- --coverage --watchAll=false
fi

echo ""
echo "✅ All tests completed!"
echo ""
echo "📊 Coverage reports:"
echo "- Python: htmlcov/index.html"
echo "- Frontend: coverage/lcov-report/index.html"
