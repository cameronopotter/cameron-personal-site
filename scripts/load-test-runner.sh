#!/bin/bash

# Digital Greenhouse Load Testing Runner
# Comprehensive load testing automation script

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOAD_TEST_DIR="$PROJECT_ROOT/load-testing"
RESULTS_DIR="$PROJECT_ROOT/load-test-results"
LOG_DIR="$RESULTS_DIR/logs"

# Default values
API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
WS_URL="ws://localhost:8000"
TEST_TYPE="baseline"
DURATION="10m"
USERS="50"
SPAWN_RATE="5"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Digital Greenhouse Load Testing Runner

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -t, --test-type TYPE        Test type: baseline|stress|spike|websocket|mobile|all (default: baseline)
    -u, --users USERS          Number of users (default: 50)
    -r, --spawn-rate RATE       User spawn rate per second (default: 5)
    -d, --duration DURATION     Test duration (default: 10m)
    --api-url URL              API base URL (default: http://localhost:8000)
    --frontend-url URL         Frontend URL (default: http://localhost:3000)
    --ws-url URL               WebSocket URL (default: ws://localhost:8000)
    --tool TOOL                Testing tool: locust|k6|both (default: both)
    --report-only              Generate reports from existing results
    --cleanup                   Clean up old test results
    -h, --help                 Show this help message

TEST TYPES:
    baseline     - Normal load testing with realistic user behavior
    stress       - High load testing to find breaking points
    spike        - Sudden traffic spikes testing
    websocket    - WebSocket connection testing
    mobile       - Mobile user simulation
    database     - Database-heavy operations testing
    all          - Run all test types sequentially

EXAMPLES:
    # Basic load test with 100 users
    $0 --test-type baseline --users 100 --duration 15m

    # Stress test with rapid user spawning
    $0 --test-type stress --users 500 --spawn-rate 50

    # WebSocket-specific testing
    $0 --test-type websocket --users 100

    # Run all tests
    $0 --test-type all

    # Generate reports only
    $0 --report-only

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--test-type)
                TEST_TYPE="$2"
                shift 2
                ;;
            -u|--users)
                USERS="$2"
                shift 2
                ;;
            -r|--spawn-rate)
                SPAWN_RATE="$2"
                shift 2
                ;;
            -d|--duration)
                DURATION="$2"
                shift 2
                ;;
            --api-url)
                API_URL="$2"
                shift 2
                ;;
            --frontend-url)
                FRONTEND_URL="$2"
                shift 2
                ;;
            --ws-url)
                WS_URL="$2"
                shift 2
                ;;
            --tool)
                TOOL="$2"
                shift 2
                ;;
            --report-only)
                REPORT_ONLY=true
                shift
                ;;
            --cleanup)
                CLEANUP=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Setup directories
setup_directories() {
    print_status "Setting up directories..."
    
    mkdir -p "$RESULTS_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$RESULTS_DIR/html"
    mkdir -p "$RESULTS_DIR/json"
    mkdir -p "$RESULTS_DIR/csv"
    
    print_success "Directories created"
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    local missing_deps=()
    
    # Check for required tools
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! python3 -c "import locust" &> /dev/null; then
        missing_deps+=("locust (pip install locust)")
    fi
    
    if ! command -v k6 &> /dev/null; then
        missing_deps+=("k6")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "Missing dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        echo
        echo "Installation commands:"
        echo "  brew install k6 jq"
        echo "  pip install locust"
        exit 1
    fi
    
    print_success "All dependencies found"
}

# Health check services
health_check() {
    print_status "Performing health checks..."
    
    # Check API health
    if ! curl -s "$API_URL/health" > /dev/null; then
        print_error "API is not accessible at $API_URL"
        print_warning "Make sure the backend server is running"
        exit 1
    fi
    
    # Check frontend
    if ! curl -s "$FRONTEND_URL" > /dev/null; then
        print_warning "Frontend is not accessible at $FRONTEND_URL"
        print_warning "Frontend tests will be skipped"
    fi
    
    print_success "Health checks passed"
}

# Run Locust tests
run_locust_tests() {
    local test_type="$1"
    local timestamp="$(date +%Y%m%d_%H%M%S)"
    local result_file="$RESULTS_DIR/locust_${test_type}_${timestamp}"
    
    print_status "Running Locust tests for $test_type..."
    
    # Locust command based on test type
    local locust_cmd="locust -f $LOAD_TEST_DIR/locust_tests.py --host=$API_URL --headless"
    
    case $test_type in
        baseline)
            locust_cmd="$locust_cmd --users=$USERS --spawn-rate=$SPAWN_RATE --run-time=$DURATION"
            ;;
        stress)
            locust_cmd="$locust_cmd --users=$((USERS * 4)) --spawn-rate=$((SPAWN_RATE * 5)) --run-time=$DURATION"
            ;;
        spike)
            locust_cmd="$locust_cmd --users=$((USERS * 10)) --spawn-rate=$((SPAWN_RATE * 20)) --run-time=5m"
            ;;
        mobile)
            # Focus on mobile user class
            locust_cmd="$locust_cmd --users=$USERS --spawn-rate=$SPAWN_RATE --run-time=$DURATION"
            ;;
        database)
            # Focus on database stress user class
            locust_cmd="$locust_cmd --users=$((USERS * 2)) --spawn-rate=$((SPAWN_RATE * 2)) --run-time=$DURATION"
            ;;
    esac
    
    # Add output options
    locust_cmd="$locust_cmd --csv=$result_file --html=$result_file.html --logfile=$LOG_DIR/locust_${test_type}_${timestamp}.log"
    
    print_status "Executing: $locust_cmd"
    
    # Run the test
    if eval "$locust_cmd"; then
        print_success "Locust $test_type test completed"
        
        # Move results to appropriate directories
        mv "${result_file}.html" "$RESULTS_DIR/html/"
        mv "${result_file}_stats.csv" "$RESULTS_DIR/csv/" 2>/dev/null || true
        mv "${result_file}_stats_history.csv" "$RESULTS_DIR/csv/" 2>/dev/null || true
        mv "${result_file}_failures.csv" "$RESULTS_DIR/csv/" 2>/dev/null || true
        
        return 0
    else
        print_error "Locust $test_type test failed"
        return 1
    fi
}

# Run K6 tests
run_k6_tests() {
    local test_type="$1"
    local timestamp="$(date +%Y%m%d_%H%M%S)"
    local result_file="$RESULTS_DIR/json/k6_${test_type}_${timestamp}.json"
    
    print_status "Running K6 tests for $test_type..."
    
    # K6 command based on test type
    local k6_cmd="k6 run $LOAD_TEST_DIR/k6_tests.js"
    
    # Set environment variables for K6
    export BASE_URL="$API_URL"
    export WS_URL="$WS_URL"
    export FRONTEND_URL="$FRONTEND_URL"
    
    case $test_type in
        baseline)
            k6_cmd="$k6_cmd --scenarios baseline_load"
            ;;
        stress)
            k6_cmd="$k6_cmd --scenarios stress_test"
            ;;
        spike)
            k6_cmd="$k6_cmd --scenarios spike_test"
            ;;
        websocket)
            k6_cmd="$k6_cmd --scenarios websocket_test"
            ;;
        mobile)
            k6_cmd="$k6_cmd --scenarios mobile_test"
            ;;
    esac
    
    # Add output options
    k6_cmd="$k6_cmd --out json=$result_file --summary-export=$RESULTS_DIR/k6_${test_type}_${timestamp}_summary.json"
    
    print_status "Executing: $k6_cmd"
    
    # Run the test
    if eval "$k6_cmd" 2>&1 | tee "$LOG_DIR/k6_${test_type}_${timestamp}.log"; then
        print_success "K6 $test_type test completed"
        return 0
    else
        print_error "K6 $test_type test failed"
        return 1
    fi
}

# Generate performance report
generate_report() {
    local timestamp="$(date +%Y%m%d_%H%M%S)"
    local report_file="$RESULTS_DIR/performance_report_${timestamp}.html"
    
    print_status "Generating performance report..."
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Digital Greenhouse Load Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2196F3; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .success { background: #d4edda; border-color: #c3e6cb; }
        .warning { background: #fff3cd; border-color: #ffeeba; }
        .error { background: #f8d7da; border-color: #f5c6cb; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 3px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌱 Digital Greenhouse Load Test Report</h1>
        <p>Generated on: $(date)</p>
        <p>Test Configuration: $TEST_TYPE | Users: $USERS | Duration: $DURATION</p>
    </div>

    <div class="section">
        <h2>📊 Test Summary</h2>
        <div class="metric">
            <strong>Test Type:</strong> $TEST_TYPE
        </div>
        <div class="metric">
            <strong>Max Users:</strong> $USERS
        </div>
        <div class="metric">
            <strong>Duration:</strong> $DURATION
        </div>
        <div class="metric">
            <strong>Target:</strong> $API_URL
        </div>
    </div>

    <div class="section">
        <h2>📈 Key Metrics</h2>
        <p>Detailed metrics can be found in the individual test result files:</p>
        <ul>
EOF

    # Add links to result files
    for html_file in "$RESULTS_DIR/html"/*.html; do
        if [[ -f "$html_file" ]]; then
            local filename=$(basename "$html_file")
            echo "            <li><a href=\"html/$filename\">$filename</a></li>" >> "$report_file"
        fi
    done

    cat >> "$report_file" << EOF
        </ul>
    </div>

    <div class="section">
        <h2>🔍 Analysis</h2>
        <p>This report provides an overview of the load testing results. Check individual test reports for detailed metrics.</p>
        
        <h3>Performance Recommendations:</h3>
        <ul>
            <li>Monitor response times during peak load</li>
            <li>Check error rates and investigate failures</li>
            <li>Review database performance metrics</li>
            <li>Analyze WebSocket connection stability</li>
            <li>Verify mobile performance optimization</li>
        </ul>
    </div>

    <div class="section">
        <h2>📁 Files Generated</h2>
        <table>
            <tr><th>Type</th><th>Location</th><th>Description</th></tr>
            <tr><td>HTML Reports</td><td>html/</td><td>Visual test reports</td></tr>
            <tr><td>JSON Data</td><td>json/</td><td>Raw test data</td></tr>
            <tr><td>CSV Data</td><td>csv/</td><td>Metrics in CSV format</td></tr>
            <tr><td>Logs</td><td>logs/</td><td>Detailed test logs</td></tr>
        </table>
    </div>

    <footer style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
        <p><em>Generated by Digital Greenhouse Load Testing Suite</em></p>
    </footer>
</body>
</html>
EOF

    print_success "Performance report generated: $report_file"
}

# Run all tests
run_all_tests() {
    print_status "Running all test types..."
    
    local test_types=("baseline" "stress" "websocket" "mobile")
    local failed_tests=()
    
    for test_type in "${test_types[@]}"; do
        print_status "Starting $test_type test..."
        
        if [[ "$TOOL" == "locust" ]] || [[ "$TOOL" == "both" ]]; then
            if ! run_locust_tests "$test_type"; then
                failed_tests+=("locust:$test_type")
            fi
        fi
        
        if [[ "$TOOL" == "k6" ]] || [[ "$TOOL" == "both" ]]; then
            if ! run_k6_tests "$test_type"; then
                failed_tests+=("k6:$test_type")
            fi
        fi
        
        # Brief pause between tests
        sleep 30
    done
    
    if [[ ${#failed_tests[@]} -gt 0 ]]; then
        print_warning "Some tests failed:"
        for failed_test in "${failed_tests[@]}"; do
            echo "  - $failed_test"
        done
    else
        print_success "All tests completed successfully!"
    fi
}

# Cleanup old results
cleanup_results() {
    print_status "Cleaning up old test results..."
    
    # Remove files older than 7 days
    find "$RESULTS_DIR" -name "*.html" -mtime +7 -delete 2>/dev/null || true
    find "$RESULTS_DIR" -name "*.json" -mtime +7 -delete 2>/dev/null || true
    find "$RESULTS_DIR" -name "*.csv" -mtime +7 -delete 2>/dev/null || true
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Main function
main() {
    # Parse arguments
    parse_args "$@"
    
    # Handle cleanup
    if [[ "$CLEANUP" == "true" ]]; then
        cleanup_results
        exit 0
    fi
    
    # Setup
    setup_directories
    
    # Only check dependencies and health if not report-only
    if [[ "$REPORT_ONLY" != "true" ]]; then
        check_dependencies
        health_check
    fi
    
    # Set default tool if not specified
    if [[ -z "$TOOL" ]]; then
        TOOL="both"
    fi
    
    # Handle report-only mode
    if [[ "$REPORT_ONLY" == "true" ]]; then
        generate_report
        exit 0
    fi
    
    print_status "Starting Digital Greenhouse Load Tests"
    print_status "Configuration: Test Type=$TEST_TYPE, Users=$USERS, Duration=$DURATION"
    print_status "Target URLs: API=$API_URL, WebSocket=$WS_URL"
    
    # Run tests based on type
    case $TEST_TYPE in
        all)
            run_all_tests
            ;;
        baseline|stress|spike|websocket|mobile|database)
            if [[ "$TOOL" == "locust" ]] || [[ "$TOOL" == "both" ]]; then
                run_locust_tests "$TEST_TYPE"
            fi
            
            if [[ "$TOOL" == "k6" ]] || [[ "$TOOL" == "both" ]]; then
                run_k6_tests "$TEST_TYPE"
            fi
            ;;
        *)
            print_error "Unknown test type: $TEST_TYPE"
            show_help
            exit 1
            ;;
    esac
    
    # Generate report
    generate_report
    
    print_success "Load testing completed! Check results in: $RESULTS_DIR"
}

# Run main function
main "$@"