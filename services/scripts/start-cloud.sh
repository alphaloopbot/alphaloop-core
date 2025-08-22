#!/bin/bash

# AlphaLoop Services - Cloud Production Startup Script

set -e

echo "☁️ Starting AlphaLoop Services (Cloud Production)"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ${ALPHALOOP_HOME:-/opt/alphaloop}/{postgres_db,logs}

# Copy environment files if they don't exist
echo "⚙️ Setting up environment files..."

if [ ! -f "alphaloop-database/.env" ]; then
    cp alphaloop-database/env.example alphaloop-database/.env
    echo "✅ Created alphaloop-database/.env"
fi

if [ ! -f "alphaloop-market-data/.env.cloud" ]; then
    cp alphaloop-market-data/env.example.cloud alphaloop-market-data/.env.cloud
    echo "✅ Created alphaloop-market-data/.env.cloud"
fi

# Start services
echo "🐳 Starting services..."

# Start database first
echo "🗄️ Starting database..."
docker-compose up -d alphaloop-database

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until docker-compose exec -T alphaloop-database pg_isready -U postgres; do
    echo "   Waiting for database..."
    sleep 2
done
echo "✅ Database is ready!"

# Start market data (cloud)
echo "📈 Starting market data (cloud)..."
docker-compose up -d alphaloop-market-data-cloud

# Wait for all services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Show status
echo "📋 Service Status:"
docker-compose ps

echo ""
echo "☁️ AlphaLoop Cloud Services started successfully!"
echo ""
echo "📊 Service URLs:"
echo "   Database: localhost:5432"
echo "   Market Data API (Cloud): http://localhost:8000"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker-compose logs -f [service-name]"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
