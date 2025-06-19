#!/bin/bash

# Open WebUI Hub - One-Click Local Deployment
# This script performs complete local deployment in one command

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo ""
print_header "�� Open WebUI Hub - One-Click Local Deployment"
print_header "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "compose.yml.example" ]; then
    print_error "Please run this script from the open-webui-hub directory"
    exit 1
fi

# Step 1: Check dependencies
print_step "1/6 Checking system dependencies..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command_exists git; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

print_status "All dependencies are installed ✓"

# Step 2: Setup configuration
print_step "2/6 Setting up configuration..."

if [ -f "setup-local.sh" ]; then
    ./setup-local.sh
else
    print_error "setup-local.sh not found. Please ensure all files are present."
    exit 1
fi

# Step 3: Start services
print_step "3/6 Starting services..."

if [ -f "start-local.sh" ]; then
    ./start-local.sh
else
    print_error "start-local.sh not found. Please ensure all files are present."
    exit 1
fi

# Step 4: Configure services
print_step "4/6 Configuring services..."

if [ -f "configure-local.sh" ]; then
    ./configure-local.sh
else
    print_error "configure-local.sh not found. Please ensure all files are present."
    exit 1
fi

# Step 5: Test functionality
print_step "5/6 Testing functionality..."

if [ -f "test-local.sh" ]; then
    ./test-local.sh
else
    print_warning "test-local.sh not found. Skipping tests."
fi

# Step 6: Final summary
print_step "6/6 Deployment completed!"

echo ""
print_header "🎉 Open WebUI Hub is ready for use!"
print_header "=================================="
echo ""

print_status "Access your services:"
echo "  🌐 Open WebUI:    http://localhost:3000"
echo "  🤖 Ollama API:    http://localhost:11435"
echo "  🔍 SearXNG:       http://localhost:8080"
echo "  📊 Redis Insight: http://localhost:8001"
echo "  📄 Docling:       http://localhost:5001"
echo "  🔧 Tika:          http://localhost:9998"
echo ""

print_status "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Create your first admin user account"
echo "  3. Go to Settings > Tools > General and add MCP servers:"
echo "     - http://mcposerver:8000/time"
echo "     - http://mcposerver:8000/postgres"
echo "  4. Start chatting with AI!"
echo ""

print_status "Useful commands:"
echo "  📊 Check status:    docker-compose -f compose.local.yml ps"
echo "  📋 View logs:       docker-compose -f compose.local.yml logs [service]"
echo "  🔄 Restart:         docker-compose -f compose.local.yml restart [service]"
echo "  🛑 Stop all:        docker-compose -f compose.local.yml down"
echo "  🧪 Run tests:       ./test-local.sh"
echo ""

print_status "For troubleshooting, see: TROUBLESHOOTING.md"
print_status "For detailed documentation, see: README-LOCAL.md"

echo ""
print_header "Happy coding! 🚀"
