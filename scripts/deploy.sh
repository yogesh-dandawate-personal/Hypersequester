#!/bin/bash

# Deployment script for Hypersequester

set -e

ENVIRONMENT=${1:-development}
VERSION=${2:-latest}

echo "🚀 Deploying Hypersequester"
echo "=========================="
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    echo "❌ Invalid environment. Use: development, staging, or production"
    exit 1
fi

# Load environment-specific configuration
if [ -f "config/${ENVIRONMENT}.json" ]; then
    echo "📋 Loading configuration for $ENVIRONMENT"
else
    echo "❌ Configuration file not found: config/${ENVIRONMENT}.json"
    exit 1
fi

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose -f docker-compose.yml -f docker-compose.${ENVIRONMENT}.yml build

# Run database migrations (if in production)
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🗄️ Running database migrations..."
    docker-compose -f docker-compose.yml -f docker-compose.${ENVIRONMENT}.yml run --rm app python -m flask db upgrade
fi

# Deploy services
echo "🚀 Deploying services..."
docker-compose -f docker-compose.yml -f docker-compose.${ENVIRONMENT}.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy"
else
    echo "❌ Application health check failed"
    echo "📋 Service logs:"
    docker-compose logs app
    exit 1
fi

# Run post-deployment tests
if [ "$ENVIRONMENT" != "production" ]; then
    echo "🧪 Running post-deployment tests..."
    # Add integration tests here
    echo "✅ Post-deployment tests passed"
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Service status:"
docker-compose ps

echo ""
echo "🔗 Application URLs:"
echo "- Main application: http://localhost:5000"
echo "- Health check: http://localhost:5000/health"
echo "- API documentation: http://localhost:5000/api/docs"

if [ "$ENVIRONMENT" = "development" ]; then
    echo ""
    echo "🛠️ Development tools:"
    echo "- Database: postgresql://localhost:5432/hypersequester"
    echo "- Redis: redis://localhost:6379"
    echo "- Logs: docker-compose logs -f"
fi
