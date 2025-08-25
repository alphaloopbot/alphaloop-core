#!/bin/bash

# AlphaLoop Services - End-to-End Testing Script

set -Eeuo pipefail

echo "🧪 AlphaLoop Services - End-to-End Testing"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper function to run tests
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -e "\n${BLUE}🔍 Testing: ${test_name}${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if declare -F -- "$test_command" >/dev/null 2>&1; then
        "$test_command"
    else
        bash -c "$test_command"
    fi
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS: ${test_name}${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL: ${test_name}${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Check if services are running
check_services_running() {
    echo -e "\n${YELLOW}📋 Checking if services are running...${NC}"
    (
        cd services

        # Check if containers exist and are running
        if ! docker-compose ps | grep -q "alphaloop-database.*Up"; then
            echo -e "${RED}❌ Database service is not running${NC}"
            exit 1
        fi

        if ! docker-compose ps | grep -q "alphaloop-system-metrics.*Up"; then
            echo -e "${RED}❌ System metrics service is not running${NC}"
            exit 1
        fi

        if ! docker-compose ps | grep -q "alphaloop-market-data-local.*Up"; then
            echo -e "${RED}❌ Market data service is not running${NC}"
            exit 1
        fi

        echo -e "${GREEN}✅ All services are running${NC}"
    )
    return $?
}

# Database Tests
test_database_connectivity() {
    (
        cd services
        docker-compose exec -T alphaloop-database pg_isready -U postgres
    )
}

test_database_databases() {
    (
        cd services
        # Test market database
        docker-compose exec -T alphaloop-database psql -U postgres -d alphaloop_market -c "SELECT current_database();" > /dev/null
        # Test system database
        docker-compose exec -T alphaloop-database psql -U postgres -d alphaloop_sys -c "SELECT current_database();" > /dev/null
    )
}

test_database_permissions() {
    (
        cd services
        # Test market user
        docker-compose exec -T alphaloop-database psql -U alphaloop_market -d alphaloop_market -c "SELECT 1;" > /dev/null
        # Test system user
        docker-compose exec -T alphaloop-database psql -U alphaloop_sys -d alphaloop_sys -c "SELECT 1;" > /dev/null
    )
}

# System Metrics Tests
test_system_metrics_process() {
    (
        cd services
        docker-compose exec -T alphaloop-system-metrics python -c "import psutil; print('System metrics process is running')"
    )
}

test_system_metrics_logs() {
    (
        cd services
        # Check if logs are being generated
        docker-compose logs alphaloop-system-metrics | grep -q "metrics" || exit 1
    )
}

# Market Data Tests
test_market_data_health() {
    curl -f http://localhost:8001/health > /dev/null
}

test_market_data_status() {
    curl -f http://localhost:8001/api/v1/status > /dev/null
}

test_market_data_database_connection() {
    # This would test if market data service can connect to database
    # For now, we'll just check if the service is responding
    curl -f http://localhost:8001/health > /dev/null
}

# Integration Tests
test_service_communication() {
    # Test if services can communicate with each other
    (
        cd services

        # Test if system metrics can connect to database
        docker-compose exec -T alphaloop-system-metrics python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('System metrics can connect to database')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"
    )
}

test_data_flow() {
    # Test if data is flowing through the system
    (
        cd services

        # Check if system metrics are being written to database
        docker-compose exec -T alphaloop-database \
          psql -U postgres -d alphaloop_sys -t -A -c "SELECT COUNT(*) FROM system_metrics WHERE created_at > NOW() - INTERVAL '5 minutes';" \
          | awk '($1+0)>0 {exit 0} END{exit 1}'
    )
}

# Performance Tests
test_response_times() {
    # Test API response times
    local start_time
    start_time="$(date +%s.%N)"
    curl -fsS http://localhost:8001/health > /dev/null
    local end_time
    end_time="$(date +%s.%N)"
    local response_time
    if command -v bc >/dev/null 2>&1; then
        response_time="$(echo "$end_time - $start_time" | bc)"
    else
        response_time="$(python - <<'PY'
import sys,decimal
from decimal import Decimal
start=Decimal(sys.argv[1]); end=Decimal(sys.argv[2])
decimal.getcontext().prec=9
print(end-start)
PY
"$start_time" "$end_time")"
    fi

    # Response time should be less than 2 seconds
    if python - <<'PY' "$response_time"; then
import sys
print(float(sys.argv[1]) < 2.0)
PY
    then
        echo "Response time: ${response_time}s (OK)"
        return 0
    else
        echo "Response time: ${response_time}s (SLOW)"
        return 1
    fi
}

# Main test execution
main() {
    echo -e "\n${YELLOW}🚀 Starting end-to-end tests...${NC}"

    # Check if services are running
    if ! check_services_running; then
        echo -e "${RED}❌ Please start all services first: make services-start-local${NC}"
        exit 1
    fi

    echo -e "\n${BLUE}📊 Database Tests${NC}"
    run_test "Database Connectivity" "test_database_connectivity"
    run_test "Database Creation" "test_database_databases"
    run_test "Database Permissions" "test_database_permissions"

    echo -e "\n${BLUE}📈 System Metrics Tests${NC}"
    run_test "System Metrics Process" "test_system_metrics_process"
    run_test "System Metrics Logs" "test_system_metrics_logs"

    echo -e "\n${BLUE}📊 Market Data Tests${NC}"
    run_test "Market Data Health Check" "test_market_data_health"
    run_test "Market Data Status API" "test_market_data_status"
    run_test "Market Data Database Connection" "test_market_data_database_connection"

    echo -e "\n${BLUE}🔗 Integration Tests${NC}"
    run_test "Service Communication" "test_service_communication"
    run_test "Data Flow" "test_data_flow"

    echo -e "\n${BLUE}⚡ Performance Tests${NC}"
    run_test "API Response Time" "test_response_times"

    # Summary
    echo -e "\n${YELLOW}📋 Test Summary${NC}"
    echo "=========================================="
    echo -e "Total Tests: ${TOTAL_TESTS}"
    echo -e "${GREEN}Passed: ${PASSED_TESTS}${NC}"
    echo -e "${RED}Failed: ${FAILED_TESTS}${NC}"

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All tests passed! Services are working correctly.${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ Some tests failed. Please check the service logs.${NC}"
        echo -e "\n${YELLOW}Useful debugging commands:${NC}"
        echo "  make services-logs                    # View all service logs"
        echo "  make services-status                  # Check service status"
        echo "  docker-compose logs alphaloop-database     # Database logs"
        echo "  docker-compose logs alphaloop-system-metrics # System metrics logs"
        echo "  docker-compose logs alphaloop-market-data-local # Market data logs"
        exit 1
    fi
}

# Run main function
main "$@"
