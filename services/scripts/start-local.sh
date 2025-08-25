#!/bin/bash

# AlphaLoop Services - Local Development Startup Script

set -e

echo "🚀 Starting AlphaLoop Services (Local Development)"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ${ALPHALOOP_HOME:-/opt/alphaloop}/{postgres_db,logs,cache}

# Copy environment files if they don't exist
echo "⚙️ Setting up environment files..."

if [ ! -f "alphaloop-database/.env" ]; then
    cp alphaloop-database/env.example alphaloop-database/.env
    echo "✅ Created alphaloop-database/.env"
fi

if [ ! -f "alphaloop-system-metrics/.env" ]; then
    cp alphaloop-system-metrics/env.example alphaloop-system-metrics/.env
    echo "✅ Created alphaloop-system-metrics/.env"
fi

if [ ! -f "alphaloop-market-data/.env.local" ]; then
    cp alphaloop-market-data/env.example.local alphaloop-market-data/.env.local
    echo "✅ Created alphaloop-market-data/.env.local"
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

# Start system metrics
echo "📊 Starting system metrics..."
docker-compose up -d alphaloop-system-metrics

# Start market data (local)
echo "📈 Starting market data (local)..."
docker-compose up -d alphaloop-market-data-local

# Wait for all services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Show status
echo "📋 Service Status:"
docker-compose ps

echo ""
echo "🎉 AlphaLoop Services started successfully!"
echo ""
echo "📊 Service URLs:"
echo "   Database: localhost:5432"
echo "   Market Data API (Local): http://localhost:8001"
echo "   System Metrics: Running in background"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker-compose logs -f [service-name]"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
