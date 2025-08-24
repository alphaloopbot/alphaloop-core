#!/bin/bash

# AlphaLoop Database and Service Testing
# This script tests database connectivity and service data storage
# Assumes database schemas are already set up

set -e

echo "🧪 AlphaLoop Database and Service Testing"
echo "========================================="
echo ""

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-didac}"
DB_PASSWORD="${DB_PASSWORD:-your_secure_password}"

echo "Starting database and service testing..."

# Test database connectivity
echo "Testing database connectivity..."
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d alphaloop_sys -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ Cannot connect to alphaloop_sys database"
    exit 1
fi
echo "✅ System metrics database connectivity OK"

if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d alphaloop_market -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ Cannot connect to alphaloop_market database"
    exit 1
fi
echo "✅ Market data database connectivity OK"

# Test service data storage
echo ""
echo "Testing service data storage..."

# Test System Metrics Service
echo "Testing System Metrics Service Storage"
docker run --rm --network host \
    -e DB_HOST=host.docker.internal \
    -e DB_PORT="$DB_PORT" \
    -e DB_USER="$DB_USER" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    -e DB_NAME=alphaloop_sys \
    test-system-metrics:latest \
    python -c "
from alphaloop_core.services.system_metrics import SystemMetricsService
import asyncio
import sys

try:
    service = SystemMetricsService()
    metrics = service.collect_metrics()
    if metrics:
        print(f'✅ Collected metrics: {len(metrics)} fields')
        result = asyncio.run(service.store_metrics_async(metrics))
        if result:
            print('✅ System metrics storage test passed')
            sys.exit(0)
        else:
            print('❌ System metrics storage test failed')
            sys.exit(1)
    else:
        print('❌ Failed to collect system metrics')
        sys.exit(1)
except Exception as e:
    print(f'❌ System metrics test error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ System metrics storage test passed"
else
    echo "❌ System metrics storage test failed"
    exit 1
fi

# Test Market Data Service
echo ""
echo "Testing Market Data Service Storage"
docker run --rm --network host \
    -e DB_HOST=host.docker.internal \
    -e DB_PORT="$DB_PORT" \
    -e DB_USER="$DB_USER" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    -e DB_NAME=alphaloop_market \
    test-market-data:latest \
    python -c "
from alphaloop_core.services.market_data import MarketDataService
import asyncio
import sys

try:
    service = MarketDataService()
    data = asyncio.run(service.get_mock_market_data())
    if data:
        print(f'✅ Generated market data: {len(data)} records')
        result = asyncio.run(service.store_market_data_async(data))
        if result:
            print('✅ Market data storage test passed')
            sys.exit(0)
        else:
            print('❌ Market data storage test failed')
            sys.exit(1)
    else:
        print('❌ Failed to generate market data')
        sys.exit(1)
except Exception as e:
    print(f'❌ Market data test error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Market data storage test passed"
else
    echo "❌ Market data storage test failed"
    exit 1
fi

echo ""
echo "✅ All database and service tests completed successfully!"
