#!/bin/bash

# Open WebUI Hub - Local Development Configuration Script
# This script performs initial configuration after services are running

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

# Function to check if service is running
check_service() {
    local service=$1
    if ! docker-compose -f compose.local.yml ps $service | grep -q "Up"; then
        print_error "$service is not running. Please start services first with ./start-local.sh"
        return 1
    fi
    return 0
}

echo "⚙️ Configuring Open WebUI Hub - Local Development"
echo "================================================"

# Check if services are running
print_step "1. Checking service status..."
required_services=(db ollama openwebui)
for service in "${required_services[@]}"; do
    if ! check_service $service; then
        exit 1
    fi
done
print_status "All required services are running ✓"

# Download Ollama models
print_step "2. Downloading Ollama models..."
print_status "Downloading llama3.2:3b model (this may take several minutes)..."

if docker-compose -f compose.local.yml exec -T ollama ollama pull llama3.2:3b; then
    print_status "llama3.2:3b model downloaded successfully ✓"
else
    print_warning "Failed to download llama3.2:3b model. You can download it manually later."
fi

print_status "Downloading nomic-embed-text model for embeddings..."
if docker-compose -f compose.local.yml exec -T ollama ollama pull nomic-embed-text:latest; then
    print_status "nomic-embed-text model downloaded successfully ✓"
else
    print_warning "Failed to download nomic-embed-text model. You can download it manually later."
fi

# List available models
print_step "3. Listing available models..."
docker-compose -f compose.local.yml exec -T ollama ollama list

print_step "4. Configuration completed!"
echo ""
echo "🎉 Open WebUI Hub is fully configured!"
echo ""
echo "Manual configuration steps:"
echo ""
echo "1. Open http://localhost:3000 in your browser"
echo "2. Create your first admin user account"
echo "3. Go to Settings > Tools > General"
echo "4. Add the following MCP server URLs:"
echo "   - http://mcposerver:8000/time"
echo "   - http://mcposerver:8000/postgres"
echo ""
echo "5. Go to Settings > Models to verify Ollama models are available"
echo ""
echo "Available endpoints:"
echo "- Open WebUI: http://localhost:3000"
echo "- Ollama API: http://localhost:11434"
echo "- SearXNG: http://localhost:8080"
echo "- Redis Insight: http://localhost:8001"
echo "- Docling: http://localhost:5001"
echo "- Tika: http://localhost:9998"
echo ""
echo "Useful commands:"
echo "- View logs: docker-compose -f compose.local.yml logs [service]"
echo "- Stop all: docker-compose -f compose.local.yml down"
echo "- Restart service: docker-compose -f compose.local.yml restart [service]"
