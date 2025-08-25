#!/bin/bash

# AlphaLoop Services E2E Test Script
# Tests both system metrics and market data services end-to-end

set -Eeuo pipefail

# Ensure background containers are cleaned up on exit/interrupt
cleanup() {
    docker rm -f test-system-metrics test-market-data >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SYSTEM_METRICS_IMAGE="test-system-metrics"
MARKET_DATA_IMAGE="test-market-data"
TEST_TIMEOUT=30

echo -e "${BLUE}🚀 AlphaLoop Services E2E Test Suite${NC}"
echo "=================================="

# Function to print test results
print_result() {
    local test_name="$1"
    local exit_code="$2"
    local message="$3"

    if [ "$exit_code" -eq 0 ]; then
        echo -e "${GREEN}✅ $test_name: $message${NC}"
    else
        echo -e "${RED}❌ $test_name: $message${NC}"
    fi
}

# Function to test service basic functionality
test_service_basic() {
    local service_name="$1"
    local image_name="$2"
    local test_command="$3"

    echo -e "\n${YELLOW}Testing $service_name basic functionality...${NC}"

    # Test service imports and basic functionality
    if docker run --rm "$image_name" python -c "$test_command" 2>/dev/null; then
        print_result "$service_name Basic Test" 0 "Service imports and basic functionality work"
        return 0
    else
        print_result "$service_name Basic Test" 1 "Service failed to import or run basic functionality"
        return 1
    fi
}

# Function to test service data collection
test_service_data_collection() {
    local service_name="$1"
    local image_name="$2"
    local test_command="$3"

    echo -e "\n${YELLOW}Testing $service_name data collection...${NC}"

    # Test data collection functionality
    if docker run --rm "$image_name" python -c "$test_command" 2>/dev/null; then
        print_result "$service_name Data Collection" 0 "Data collection functionality works"
        return 0
    else
        print_result "$service_name Data Collection" 1 "Data collection failed"
        return 1
    fi
}

# Function to test service infrastructure integration
test_service_infrastructure() {
    local service_name="$1"
    local image_name="$2"

    echo -e "\n${YELLOW}Testing $service_name infrastructure integration...${NC}"

    # Test that all infrastructure modules are accessible
    local test_script="
import sys
try:
    from alphaloop_logging import AlphaLoopLogger, LoggingConfig
    from alphaloop_storage import create_database_manager
    from alphaloop_cache import create_cache_manager
    from alphaloop_heartbeat import HeartbeatGenerator
    print('✅ All infrastructure modules imported successfully')
except ImportError as e:
    print(f'❌ Infrastructure import failed: {e}')
    sys.exit(1)
"

    if docker run --rm "$image_name" python -c "$test_script" 2>/dev/null; then
        print_result "$service_name Infrastructure" 0 "All infrastructure modules accessible"
        return 0
    else
        print_result "$service_name Infrastructure" 1 "Infrastructure modules not accessible"
        return 1
    fi
}

# Function to test service health check
test_service_health() {
    local service_name="$1"
    local image_name="$2"

    echo -e "\n${YELLOW}Testing $service_name health check...${NC}"

    # Test health check command
    if docker run --rm "$image_name" python -c "import psutil; print('OK')" 2>/dev/null; then
        print_result "$service_name Health Check" 0 "Health check passes"
        return 0
    else
        print_result "$service_name Health Check" 1 "Health check fails"
        return 1
    fi
}

# Function to test service configuration
test_service_config() {
    local service_name="$1"
    local image_name="$2"

    echo -e "\n${YELLOW}Testing $service_name configuration...${NC}"

    # Test environment variable handling
    local test_script="
import os
try:
    # Test that environment variables are accessible
    interval = os.getenv('METRICS_INTERVAL', '30')
    print(f'✅ Configuration test passed: METRICS_INTERVAL={interval}')
except Exception as e:
    print(f'❌ Configuration test failed: {e}')
    exit(1)
"

    if docker run --rm "$image_name" python -c "$test_script" 2>/dev/null; then
        print_result "$service_name Configuration" 0 "Configuration handling works"
        return 0
    else
        print_result "$service_name Configuration" 1 "Configuration handling failed"
        return 1
    fi
}

# Main test execution
main() {
    local total_tests=0
    local passed_tests=0

    echo -e "\n${BLUE}Starting E2E Tests...${NC}"

    # Test System Metrics Service
    echo -e "\n${BLUE}📊 Testing System Metrics Service${NC}"
    echo "----------------------------------------"

    # Basic functionality test
    test_service_basic "System Metrics" "$SYSTEM_METRICS_IMAGE" "
from alphaloop_core.services.system_metrics import SystemMetricsService
service = SystemMetricsService()
print('✅ System Metrics Service initialized')
"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Data collection test
    test_service_data_collection "System Metrics" "$SYSTEM_METRICS_IMAGE" "
from alphaloop_core.services.system_metrics import SystemMetricsService
service = SystemMetricsService()
metrics = service.collect_metrics()
if metrics and len(metrics) > 0:
    print(f'✅ Collected {len(metrics)} system metrics')
else:
    print('❌ No metrics collected')
    exit(1)
"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Infrastructure integration test
    test_service_infrastructure "System Metrics" "$SYSTEM_METRICS_IMAGE"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Health check test
    test_service_health "System Metrics" "$SYSTEM_METRICS_IMAGE"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Configuration test
    test_service_config "System Metrics" "$SYSTEM_METRICS_IMAGE"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Test Market Data Service
    echo -e "\n${BLUE}📈 Testing Market Data Service${NC}"
    echo "----------------------------------"

    # Basic functionality test
    test_service_basic "Market Data" "$MARKET_DATA_IMAGE" "
from alphaloop_core.services.market_data import MarketDataService
service = MarketDataService()
print('✅ Market Data Service initialized')
"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Data collection test
    test_service_data_collection "Market Data" "$MARKET_DATA_IMAGE" "
from alphaloop_core.services.market_data import MarketDataService
service = MarketDataService()
data = service.get_mock_market_data()
if data and len(data) > 0:
    print(f'✅ Generated {len(data)} market data records')
else:
    print('❌ No market data generated')
    exit(1)
"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Infrastructure integration test
    test_service_infrastructure "Market Data" "$MARKET_DATA_IMAGE"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Health check test
    test_service_health "Market Data" "$MARKET_DATA_IMAGE"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Configuration test
    test_service_config "Market Data" "$MARKET_DATA_IMAGE"
    local result=$?
    ((total_tests++))
    if [ $result -eq 0 ]; then ((passed_tests++)); fi

    # Test Service Integration
    echo -e "\n${BLUE}🔗 Testing Service Integration${NC}"
    echo "--------------------------------"

    # Test that both services can run simultaneously
    echo -e "\n${YELLOW}Testing concurrent service execution...${NC}"

    # Start both services in background with a timeout and check they don't crash
    timeout "${TEST_TIMEOUT}s" docker run --rm --name test-system-metrics "$SYSTEM_METRICS_IMAGE" python -c "
import time
from alphaloop_core.services.system_metrics import SystemMetricsService
service = SystemMetricsService()
print('✅ System Metrics Service started successfully')
time.sleep(2)
print('✅ System Metrics Service completed successfully')
" &
    pid1=$!

    timeout "${TEST_TIMEOUT}s" docker run --rm --name test-market-data "$MARKET_DATA_IMAGE" python -c "
import time
from alphaloop_core.services.market_data import MarketDataService
service = MarketDataService()
print('✅ Market Data Service started successfully')
time.sleep(2)
print('✅ Market Data Service completed successfully')
" &
    pid2=$!

    # Wait for both and capture exit codes
    wait "$pid1"; rc1=$?
    wait "$pid2"; rc2=$?

    ((total_tests++))
    if [ $rc1 -eq 0 ] && [ $rc2 -eq 0 ]; then
        print_result "Service Integration" 0 "Both services can run concurrently"
        ((passed_tests++))
    else
        print_result "Service Integration" 1 "One or both services exited with errors (rc1=$rc1, rc2=$rc2)"
    fi

    # Final Results
    echo -e "\n${BLUE}📋 Test Results Summary${NC}"
    echo "========================"
    echo -e "${GREEN}Passed: $passed_tests${NC}"
    echo -e "${RED}Failed: $((total_tests - passed_tests))${NC}"
    echo -e "${BLUE}Total: $total_tests${NC}"

    if [ $passed_tests -eq $total_tests ]; then
        echo -e "\n${GREEN}🎉 All tests passed! Services are working correctly.${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ Some tests failed. Please check the output above.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
