#!/bin/bash

# Dashboard Log Monitoring Script
# Monitors logs from all Open WebUI Hub services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Log monitoring functions
monitor_all_logs() {
    echo -e "${GREEN}🔍 Monitoring logs from all services...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop monitoring${NC}"
    echo ""
    
    docker-compose -f "$PROJECT_ROOT/compose.local.yml" logs -f --tail=10
}

monitor_service_log() {
    local service="$1"
    
    if [ -z "$service" ]; then
        echo -e "${RED}❌ Error: Service name required${NC}"
        echo "Usage: $0 <service_name>"
        echo "Available services: dashboard, db, redis, ollama, litellm, nginx, openwebui, etc."
        exit 1
    fi
    
    echo -e "${GREEN}🔍 Monitoring logs for service: ${BLUE}$service${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop monitoring${NC}"
    echo ""
    
    docker-compose -f "$PROJECT_ROOT/compose.local.yml" logs -f --tail=20 "$service"
}

monitor_dashboard_detailed() {
    echo -e "${GREEN}🔍 Detailed Dashboard monitoring...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop monitoring${NC}"
    echo ""
    
    # Monitor dashboard logs with health check filtering
    docker logs -f open-webui-hub-dashboard-1 | while read line; do
        timestamp=$(date '+%H:%M:%S')
        
        # Color code different log types
        if echo "$line" | grep -q "ERROR\|error"; then
            echo -e "${RED}[$timestamp] $line${NC}"
        elif echo "$line" | grep -q "WARNING\|warning"; then
            echo -e "${YELLOW}[$timestamp] $line${NC}"
        elif echo "$line" | grep -q "Health check\|health"; then
            echo -e "${CYAN}[$timestamp] $line${NC}"
        elif echo "$line" | grep -q "GET\|POST"; then
            echo -e "${BLUE}[$timestamp] $line${NC}"
        else
            echo "[$timestamp] $line"
        fi
    done
}

show_service_status() {
    echo -e "${GREEN}📊 Current service status:${NC}"
    echo ""
    
    # Show Docker container status
    docker-compose -f "$PROJECT_ROOT/compose.local.yml" ps
    
    echo ""
    echo -e "${GREEN}🏥 Dashboard health check:${NC}"
    
    # Test dashboard health endpoint
    if curl -s http://localhost:5002/api/health > /dev/null; then
        echo -e "${GREEN}✅ Dashboard API is responding${NC}"
        
        # Show health summary
        health_response=$(curl -s http://localhost:5002/api/health)
        status=$(echo "$health_response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        uptime=$(echo "$health_response" | grep -o '"uptime":[^,]*' | cut -d':' -f2)
        
        echo -e "${BLUE}   Status: $status${NC}"
        echo -e "${BLUE}   Uptime: $(printf "%.1f" $uptime) seconds${NC}"
    else
        echo -e "${RED}❌ Dashboard API is not responding${NC}"
    fi
}

tail_service_logs() {
    local service="$1"
    local lines="${2:-50}"
    
    echo -e "${GREEN}📜 Last $lines lines from $service:${NC}"
    echo ""
    
    docker-compose -f "$PROJECT_ROOT/compose.local.yml" logs --tail="$lines" "$service"
}

# Main script logic
case "${1:-all}" in
    "all")
        monitor_all_logs
        ;;
    "dashboard")
        monitor_dashboard_detailed
        ;;
    "status")
        show_service_status
        ;;
    "tail")
        tail_service_logs "$2" "$3"
        ;;
    *)
        if [ -n "$1" ]; then
            monitor_service_log "$1"
        else
            echo -e "${GREEN}🔍 Open WebUI Hub Log Monitor${NC}"
            echo ""
            echo "Usage:"
            echo "  $0                    # Monitor all services"
            echo "  $0 all               # Monitor all services" 
            echo "  $0 dashboard         # Monitor dashboard with detailed formatting"
            echo "  $0 <service_name>    # Monitor specific service"
            echo "  $0 status            # Show current service status"
            echo "  $0 tail <service> [lines]  # Show last N lines from service"
            echo ""
            echo "Available services:"
            echo "  dashboard, db, redis, ollama, litellm, nginx, openwebui,"
            echo "  searxng, auth, docling, edgetts, mcposerver, tika, watchtower"
        fi
        ;;
esac
