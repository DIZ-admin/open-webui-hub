#!/bin/bash

# Open WebUI Hub - Local Development Startup Script
# This script starts services in the correct order and monitors their health

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to wait for service health
wait_for_service() {
    local service=$1
    local max_attempts=${2:-30}
    local attempt=1
    
    print_status "Waiting for $service to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f compose.local.yml ps $service | grep -q "healthy\|Up"; then
            print_status "$service is healthy ✓"
            return 0
        fi
        
        echo -n "."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    print_error "$service failed to become healthy after $((max_attempts * 10)) seconds"
    return 1
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port $port is already in use. Please stop the service using this port."
        return 1
    fi
    return 0
}

echo "🚀 Starting Open WebUI Hub - Local Development"
echo "=============================================="

# Check if setup was run
if [ ! -f "env/auth.env" ]; then
    print_error "Environment files not found. Please run ./setup-local.sh first."
    exit 1
fi

# Check critical ports
print_step "1. Checking port availability..."
critical_ports=(80 3000 5432 6379 8080 11435)
for port in "${critical_ports[@]}"; do
    if ! check_port $port; then
        exit 1
    fi
done
print_status "All critical ports are available ✓"

# Start infrastructure services first
print_step "2. Starting infrastructure services..."
docker-compose -f compose.local.yml up -d watchtower db redis

# Wait for database
wait_for_service db 20

# Start core services
print_step "3. Starting core services..."
docker-compose -f compose.local.yml up -d ollama searxng tika docling edgetts

# Wait for Ollama
wait_for_service ollama 30

# Start application services
print_step "4. Starting application services..."
docker-compose -f compose.local.yml up -d mcposerver auth

# Wait for auth service
wait_for_service auth 15

# Start web services
print_step "5. Starting web services..."
docker-compose -f compose.local.yml up -d openwebui nginx

# Wait for Open WebUI
wait_for_service openwebui 30

# Final health check
print_step "6. Performing final health check..."
sleep 30

# Check all services
services=(watchtower db redis ollama searxng tika docling edgetts mcposerver auth openwebui nginx)
failed_services=()

for service in "${services[@]}"; do
    if ! docker-compose -f compose.local.yml ps $service | grep -q "healthy\|Up"; then
        failed_services+=($service)
    fi
done

if [ ${#failed_services[@]} -eq 0 ]; then
    print_status "All services are running successfully! ✓"
    echo ""
    echo "�� Open WebUI Hub is ready!"
    echo ""
    echo "Access points:"
    echo "- Open WebUI: http://localhost:3000"
    echo "- Ollama API: http://localhost:11435"
    echo "- SearXNG: http://localhost:8080"
    echo "- Redis Insight: http://localhost:8001"
    echo "- Docling: http://localhost:5001"
    echo "- Tika: http://localhost:9998"
    echo ""
    echo "Next steps:"
    echo "1. Download an Ollama model: docker-compose -f compose.local.yml exec ollama ollama pull llama3.2:3b"
    echo "2. Open http://localhost:3000 in your browser"
    echo "3. Create your first user account"
    echo "4. Configure MCP servers in Settings > Tools"
else
    print_error "Some services failed to start: ${failed_services[*]}"
    echo ""
    echo "Check logs with: docker-compose -f compose.local.yml logs [service_name]"
    exit 1
fi
