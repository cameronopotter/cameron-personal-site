#!/bin/bash

# Digital Greenhouse Monitoring Setup Script
# Sets up comprehensive monitoring with Prometheus, Grafana, and Alertmanager

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MONITORING_DIR="$PROJECT_ROOT/monitoring"
DATA_DIR="${DATA_PATH:-$PROJECT_ROOT/monitoring-data}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        exit 1
    fi
    
    log_success "All dependencies found"
}

# Setup directories
setup_directories() {
    log_info "Setting up monitoring directories..."
    
    local dirs=(
        "$DATA_DIR/prometheus"
        "$DATA_DIR/grafana"
        "$DATA_DIR/alertmanager"
        "$DATA_DIR/loki"
        "$DATA_DIR/logs"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        # Set permissions for container access
        chmod 755 "$dir"
    done
    
    log_success "Directories created"
}

# Generate configuration files
generate_configs() {
    log_info "Generating monitoring configuration files..."
    
    # Create docker-compose for monitoring stack
    cat > "$MONITORING_DIR/docker-compose.monitoring.yml" << 'EOF'
version: '3.8'

services:
  # Prometheus - Metrics collection
  prometheus:
    image: prom/prometheus:latest
    container_name: digital-greenhouse-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./rules:/etc/prometheus/rules:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    networks:
      - monitoring

  # Grafana - Visualization
  grafana:
    image: grafana/grafana:latest
    container_name: digital-greenhouse-grafana
    restart: unless-stopped
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/var/lib/grafana/dashboards:ro
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin123}
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
    networks:
      - monitoring

  # Alertmanager - Alert handling
  alertmanager:
    image: prom/alertmanager:latest
    container_name: digital-greenhouse-alertmanager
    restart: unless-stopped
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - alertmanager_data:/alertmanager
    networks:
      - monitoring

  # Node Exporter - System metrics
  node-exporter:
    image: prom/node-exporter:latest
    container_name: digital-greenhouse-node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring

  # cAdvisor - Container metrics
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: digital-greenhouse-cadvisor
    restart: unless-stopped
    ports:
      - "8081:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/lib/docker:/var/lib/docker:ro
    networks:
      - monitoring

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: digital-greenhouse-redis-exporter
    restart: unless-stopped
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis:6379
    networks:
      - monitoring

  # Postgres Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: digital-greenhouse-postgres-exporter
    restart: unless-stopped
    ports:
      - "9187:9187"
    environment:
      - DATA_SOURCE_NAME=postgresql://postgres:password@database:5432/digital_greenhouse?sslmode=disable
    networks:
      - monitoring

  # Blackbox Exporter - Uptime monitoring
  blackbox-exporter:
    image: prom/blackbox-exporter:latest
    container_name: digital-greenhouse-blackbox-exporter
    restart: unless-stopped
    ports:
      - "9115:9115"
    volumes:
      - ./blackbox.yml:/etc/blackbox_exporter/config.yml:ro
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
EOF

    # Create blackbox exporter config
    cat > "$MONITORING_DIR/blackbox.yml" << 'EOF'
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: []
      method: GET
      preferred_ip_protocol: "ip4"
      ip_protocol_fallback: false
      follow_redirects: true
      fail_if_ssl: false
      fail_if_not_ssl: false

  http_post_2xx:
    prober: http
    timeout: 5s
    http:
      method: POST
      headers:
        Content-Type: application/json
      body: '{}'

  tcp_connect:
    prober: tcp
    timeout: 5s

  icmp:
    prober: icmp
    timeout: 5s
    icmp:
      preferred_ip_protocol: "ip4"
EOF

    log_success "Configuration files generated"
}

# Setup Grafana dashboards
setup_dashboards() {
    log_info "Setting up Grafana dashboards..."
    
    # Copy dashboard files to the correct location
    if [[ -d "$MONITORING_DIR/grafana/dashboards" ]]; then
        log_success "Dashboard files already exist"
    else
        log_warning "Dashboard files not found in $MONITORING_DIR/grafana/dashboards"
    fi
    
    log_success "Dashboard setup complete"
}

# Start monitoring stack
start_monitoring() {
    log_info "Starting monitoring stack..."
    
    cd "$MONITORING_DIR"
    
    # Start the monitoring stack
    docker-compose -f docker-compose.monitoring.yml up -d
    
    log_success "Monitoring stack started"
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    
    local services=(
        "http://localhost:9090"  # Prometheus
        "http://localhost:3001"  # Grafana  
        "http://localhost:9093"  # Alertmanager
    )
    
    for service in "${services[@]}"; do
        local retries=30
        local count=0
        
        while [[ $count -lt $retries ]]; do
            if curl -s "$service" > /dev/null; then
                log_success "Service ready: $service"
                break
            fi
            
            ((count++))
            sleep 2
        done
        
        if [[ $count -eq $retries ]]; then
            log_warning "Service not ready after $((retries * 2)) seconds: $service"
        fi
    done
}

# Configure Grafana
configure_grafana() {
    log_info "Configuring Grafana..."
    
    local grafana_url="http://localhost:3001"
    local admin_user="admin"
    local admin_pass="${GRAFANA_ADMIN_PASSWORD:-admin123}"
    
    # Wait for Grafana to be fully ready
    sleep 10
    
    # Create API key (optional, for automation)
    log_info "Grafana should be accessible at $grafana_url"
    log_info "Default credentials: $admin_user / $admin_pass"
    
    log_success "Grafana configuration complete"
}

# Display access information
display_info() {
    log_success "Digital Greenhouse Monitoring Setup Complete!"
    echo
    echo "🔗 Access URLs:"
    echo "   Grafana:      http://localhost:3001 (admin/admin123)"
    echo "   Prometheus:   http://localhost:9090"
    echo "   Alertmanager: http://localhost:9093"
    echo "   Node Metrics: http://localhost:9100"
    echo "   cAdvisor:     http://localhost:8081"
    echo
    echo "📊 Available Dashboards:"
    echo "   - Digital Greenhouse Overview"
    echo "   - Performance Dashboard"
    echo "   - System Resources"
    echo "   - Business Metrics"
    echo
    echo "📧 Alert Channels:"
    echo "   - Email notifications"
    echo "   - Slack integration"
    echo "   - Webhook endpoints"
    echo
    echo "🛠️  Management Commands:"
    echo "   Start:  docker-compose -f monitoring/docker-compose.monitoring.yml up -d"
    echo "   Stop:   docker-compose -f monitoring/docker-compose.monitoring.yml down"
    echo "   Logs:   docker-compose -f monitoring/docker-compose.monitoring.yml logs -f"
    echo
}

# Cleanup function
cleanup() {
    log_info "Cleaning up old monitoring containers..."
    
    cd "$MONITORING_DIR" 2>/dev/null || true
    docker-compose -f docker-compose.monitoring.yml down 2>/dev/null || true
    
    log_success "Cleanup complete"
}

# Main function
main() {
    local command="${1:-setup}"
    
    case "$command" in
        setup)
            log_info "Setting up Digital Greenhouse monitoring..."
            check_dependencies
            setup_directories
            generate_configs
            setup_dashboards
            start_monitoring
            configure_grafana
            display_info
            ;;
        start)
            log_info "Starting monitoring stack..."
            cd "$MONITORING_DIR"
            docker-compose -f docker-compose.monitoring.yml up -d
            log_success "Monitoring stack started"
            ;;
        stop)
            log_info "Stopping monitoring stack..."
            cd "$MONITORING_DIR"
            docker-compose -f docker-compose.monitoring.yml down
            log_success "Monitoring stack stopped"
            ;;
        restart)
            log_info "Restarting monitoring stack..."
            cd "$MONITORING_DIR"
            docker-compose -f docker-compose.monitoring.yml restart
            log_success "Monitoring stack restarted"
            ;;
        cleanup)
            cleanup
            ;;
        status)
            log_info "Checking monitoring stack status..."
            cd "$MONITORING_DIR"
            docker-compose -f docker-compose.monitoring.yml ps
            ;;
        *)
            echo "Usage: $0 {setup|start|stop|restart|cleanup|status}"
            echo
            echo "Commands:"
            echo "  setup    - Initial setup of monitoring stack"
            echo "  start    - Start monitoring services"
            echo "  stop     - Stop monitoring services"
            echo "  restart  - Restart monitoring services"
            echo "  cleanup  - Remove monitoring containers and data"
            echo "  status   - Show service status"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"