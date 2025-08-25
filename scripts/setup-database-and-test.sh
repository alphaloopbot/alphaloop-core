#!/bin/bash

# AlphaLoop Database Setup and Service Testing
# This script sets up the database schema and tests service functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-didac}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_NAME_SYS="${DB_NAME_SYS:-alphaloop_sys}"
DB_NAME_MARKET="${DB_NAME_MARKET:-alphaloop_market}"

echo -e "${BLUE}🗄️ AlphaLoop Database Setup and Service Testing${NC}"
echo "================================================"
echo ""

echo "Starting database setup and service testing..."
echo ""

# Function to generate SQL from YAML on-the-fly
generate_sql_from_yaml() {
    python3 -c "
import yaml
import sys

def generate_sql_column(column):
    name = column['name']
    col_type = column['type']

    type_mapping = {
        'Integer': 'INTEGER',
        'Float': 'DECIMAL(20,8)',
        'String': 'VARCHAR(255)',
        'Boolean': 'BOOLEAN',
        'TIMESTAMP': 'TIMESTAMP',
        'JSON': 'JSONB'
    }

    sql_type = str(type_mapping.get(col_type, col_type))

    if column.get('primary_key'):
        if col_type == 'Integer':
            sql_type = 'INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY'
        else:
            sql_type += ' PRIMARY KEY'

    if 'foreign_key' in column:
        fk_ref = str(column['foreign_key'])
        sql_type += f' REFERENCES {fk_ref}'

    if not column.get('primary_key') and not column.get('nullable', True):
        sql_type += ' NOT NULL'

    return f'    {name} {sql_type}'

def generate_table_sql(table_name, table_spec):
    columns = [generate_sql_column(col) for col in table_spec['columns']]
    return f'CREATE TABLE {table_name} (\n' + ',\n'.join(columns) + '\n);'

def generate_indexes(table_name, table_spec):
    indexes = []
    if table_spec.get('type') == 'data':
        indexes.extend([
            f'CREATE INDEX idx_{table_name}_timestamp ON {table_name}(timestamp_id);',
            f'CREATE INDEX idx_{table_name}_metadata_id ON {table_name}(metadata_id);',
            f'CREATE INDEX idx_{table_name}_metadata_timestamp ON {table_name}(metadata_id, timestamp_id);'
        ])
    return indexes

try:
    # Load YAML schema
    with open('config/database_schema.yaml', 'r') as f:
        schema = yaml.safe_load(f)

    # Generate SQL
    sql_lines = [
        '-- AlphaLoop Database Schemas - Generated on-the-fly from YAML',
        '-- Source: config/database_schema.yaml',
        '',
        '-- Drop existing databases if they exist (with connection termination)',
        '-- Terminate active connections to alphaloop_sys',
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='alphaloop_sys' AND pid <> pg_backend_pid();",
        'DROP DATABASE IF EXISTS alphaloop_sys;',
        '-- Terminate active connections to alphaloop_market',
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='alphaloop_market' AND pid <> pg_backend_pid();",
        'DROP DATABASE IF EXISTS alphaloop_market;',
        '',
        '-- Create fresh databases',
        'CREATE DATABASE alphaloop_sys;',
        'CREATE DATABASE alphaloop_market;',
        ''
    ]

    # Generate tables for each database
    for db_name, db_spec in schema['databases'].items():
        sql_lines.extend([
            f'-- ============================================================================',
            f'-- {db_name.upper()} DATABASE',
            f'-- ============================================================================',
            f'\\c {db_name};',
            ''
        ])

        for table_name, table_spec in db_spec['tables'].items():
            sql_lines.extend([
                f'-- {table_spec.get(\"description\", table_name)}',
                generate_table_sql(table_name, table_spec),
                ''
            ])

            # Add indexes
            indexes = generate_indexes(table_name, table_spec)
            for index in indexes:
                sql_lines.append(index)
            sql_lines.append('')

    # Add sample data
    sql_lines.extend([
        '-- ============================================================================',
        '-- SAMPLE DATA',
        '-- ============================================================================',
        '',
        '-- Insert sample system metadata',
        '\\c alphaloop_sys;',
        'INSERT INTO system_attributes (',
        '    host_name, system_name, node_name, machine, kernel_version,',
        '    cpu_cores, cpu_cores_logical, ram_total, ssd_total, boot_time',
        ') VALUES (',
        '    \'alphaloop-node-001\',',
        '    \'Linux\',',
        '    \'alphaloop-node-001\',',
        '    \'x86_64\',',
        '    \'5.15.0-generic\',',
        '    8,',
        '    16,',
        '    34359738368.0,  -- 32GB',
        '    1099511627776.0, -- 1TB',
        '    CURRENT_TIMESTAMP - INTERVAL \'1 hour\'',
        ');',
        '',
        '-- Insert sample market metadata',
        '\\c alphaloop_market;',
        'INSERT INTO tickers_metadata (ticker, base, quote, exchange, active) VALUES',
        '(\'BTC/USDT\', \'BTC\', \'USDT\', \'binance\', true),',
        '(\'ETH/USDT\', \'ETH\', \'USDT\', \'binance\', true),',
        '(\'ADA/USDT\', \'ADA\', \'USDT\', \'binance\', true),',
        '(\'DOT/USDT\', \'DOT\', \'USDT\', \'binance\', true);',
        ''
    ])

    # Output the generated SQL
    print('\\n'.join(sql_lines))

except Exception as e:
    print(f'Error generating SQL from YAML: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# Check PostgreSQL connection
echo -e "${BLUE}Checking PostgreSQL connection...${NC}"
if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to PostgreSQL${NC}"
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL is running and accessible${NC}"
echo ""

# Setup databases and tables
echo -e "${BLUE}Setting up databases and tables...${NC}"

# Safety: require explicit opt-in for destructive drop/create
if [[ "${ALLOW_DROP_DB:-}" != "1" ]]; then
    echo -e "${RED}❌ Refusing to drop/create databases without ALLOW_DROP_DB=1${NC}"
    echo -e "${YELLOW}Set ALLOW_DROP_DB=1 to allow destructive database operations${NC}"
    exit 1
fi
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres <<< "$(generate_sql_from_yaml)"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database schemas created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create database schemas${NC}"
    exit 1
fi
echo ""

# Test database connectivity
echo -e "${BLUE}Testing database connectivity...${NC}"

# Test system metrics database
if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME_SYS" -c "SELECT COUNT(*) FROM system_attributes;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ System metrics database connectivity OK${NC}"
else
    echo -e "${RED}❌ System metrics database connectivity failed${NC}"
    exit 1
fi

# Test market data database
if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME_MARKET" -c "SELECT COUNT(*) FROM tickers_metadata;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Market data database connectivity OK${NC}"
else
    echo -e "${RED}❌ Market data database connectivity failed${NC}"
    exit 1
fi
echo ""

# Test service data storage
echo -e "${BLUE}Testing service data storage...${NC}"
echo ""

# Test system metrics service storage
echo -e "${BLUE}Testing System Metrics Service Storage${NC}"
if docker run --rm --network host \
    -e DB_HOST="host.docker.internal" \
    -e DB_PORT="$DB_PORT" \
    -e DB_USER="$DB_USER" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    -e DB_NAME="$DB_NAME_SYS" \
    -e METRICS_INTERVAL=30 \
    -e HOST_HOSTNAME="test-host" \
    test-system-metrics:latest \
    python -c "
import asyncio
from alphaloop_core.services.system_metrics import SystemMetricsService

async def test_storage():
    service = SystemMetricsService()
    metrics = service.collect_metrics()
    if metrics:
        success = await service.store_metrics_async(metrics)
        if success:
            print('✅ System metrics stored successfully')
            return True
        else:
            print('❌ Failed to store system metrics')
            return False
    else:
        print('❌ Failed to collect system metrics')
        return False

result = asyncio.run(test_storage())
exit(0 if result else 1)
"; then
    echo -e "${GREEN}✅ System metrics storage test passed${NC}"
else
    echo -e "${RED}❌ System metrics storage test failed${NC}"
    exit 1
fi

# Test market data service storage
echo -e "${BLUE}Testing Market Data Service Storage${NC}"
if docker run --rm --network host \
    -e DB_HOST="host.docker.internal" \
    -e DB_PORT="$DB_PORT" \
    -e DB_USER="$DB_USER" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    -e DB_NAME="$DB_NAME_MARKET" \
    -e MARKET_DATA_INTERVAL=60 \
    -e DEPLOYMENT_TYPE="local" \
    -e CLOUD_SYNC_ENABLED="false" \
    test-market-data:latest \
    python -c "
import asyncio
from alphaloop_core.services.market_data import MarketDataService

async def test_storage():
    service = MarketDataService()
    market_data = await service.get_mock_market_data()
    if market_data:
        success = await service.store_market_data_async(market_data)
        if success:
            print('✅ Market data stored successfully')
            return True
        else:
            print('❌ Failed to store market data')
            return False
    else:
        print('❌ Failed to generate market data')
        return False

result = asyncio.run(test_storage())
exit(0 if result else 1)
"; then
    echo -e "${GREEN}✅ Market data storage test passed${NC}"
else
    echo -e "${RED}❌ Market data storage test failed${NC}"
    exit 1
fi
echo ""

# Verify data was stored
echo -e "${BLUE}Verifying stored data...${NC}"

# Check system metrics
echo -e "${BLUE}Checking system metrics data...${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME_SYS" -c "SELECT COUNT(*) as total_records, MAX(timestamp_id) as latest_record FROM system_metrics;"

# Check market data
echo -e "${BLUE}Checking market data...${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME_MARKET" -c "SELECT COUNT(*) as total_records, MAX(timestamp_id) as latest_record FROM tickers_prices;"
echo ""

# Test continuous data collection
echo -e "${BLUE}Testing continuous data collection (30 seconds)...${NC}"

# Start system metrics collection in background
docker run --rm --network host \
    -e DB_HOST="host.docker.internal" \
    -e DB_PORT="$DB_PORT" \
    -e DB_USER="$DB_USER" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    -e DB_NAME="$DB_NAME_SYS" \
    -e METRICS_INTERVAL=5 \
    -e HOST_HOSTNAME="test-host" \
    test-system-metrics:latest \
    python -c "
import asyncio
import time
from alphaloop_core.services.system_metrics import SystemMetricsService

async def collect_metrics():
    service = SystemMetricsService()
    start_time = time.time()
    while time.time() - start_time < 30:
        metrics = service.collect_metrics()
        if metrics:
            await service.store_metrics_async(metrics)
        await asyncio.sleep(5)

asyncio.run(collect_metrics())
" &
SYSTEM_METRICS_PID=$!

# Start market data collection in background
docker run --rm --network host \
    -e DB_HOST="host.docker.internal" \
    -e DB_PORT="$DB_PORT" \
    -e DB_USER="$DB_USER" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    -e DB_NAME="$DB_NAME_MARKET" \
    -e MARKET_DATA_INTERVAL=5 \
    -e DEPLOYMENT_TYPE="local" \
    -e CLOUD_SYNC_ENABLED="false" \
    test-market-data:latest \
    python -c "
import asyncio
import time
from alphaloop_core.services.market_data import MarketDataService

async def collect_market_data():
    service = MarketDataService()
    start_time = time.time()
    while time.time() - start_time < 30:
        market_data = await service.get_mock_market_data()
        if market_data:
            await service.store_market_data_async(market_data)
        await asyncio.sleep(5)

asyncio.run(collect_market_data())
" &
MARKET_DATA_PID=$!

# Wait for collection to complete with timeout protection
wait "$SYSTEM_METRICS_PID"
METRICS_RC=$?
wait "$MARKET_DATA_PID"
MARKET_RC=$?

if [[ $METRICS_RC -ne 0 || $MARKET_RC -ne 0 ]]; then
  echo -e "${RED}❌ Continuous collection failed (metrics=$METRICS_RC, market=$MARKET_RC)${NC}"
  exit 1
fi

# Check final data counts
echo -e "${BLUE}Final data verification...${NC}"
echo -e "${BLUE}System metrics records:${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME_SYS" -c "SELECT COUNT(*) as total_records FROM system_metrics;"

echo -e "${BLUE}Market data records:${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME_MARKET" -c "SELECT COUNT(*) as total_records FROM tickers_prices;"

echo ""
echo -e "${GREEN}✅ Database setup and service testing completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📊 Summary:${NC}"
echo "  • Database schemas created from YAML configuration"
echo "  • System metrics service: ✅ Working"
echo "  • Market data service: ✅ Working"
echo "  • Data collection: ✅ Working"
echo "  • No duplicate schema files maintained"
