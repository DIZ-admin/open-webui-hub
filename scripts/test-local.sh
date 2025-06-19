#!/bin/bash

# Open WebUI Hub - Local Development Test Script
# This script tests the functionality of all services

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

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    print_status "Testing $description..."
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" -eq "$expected_status" ]; then
            print_status "$description: ✓ (HTTP $response)"
            return 0
        else
            print_warning "$description: ⚠ (HTTP $response, expected $expected_status)"
            return 1
        fi
    else
        print_error "$description: ✗ (Connection failed)"
        return 1
    fi
}

echo "🧪 Testing Open WebUI Hub - Local Development"
echo "============================================="

# Test basic connectivity
print_step "1. Testing service connectivity..."

test_endpoint "http://localhost:3000" "Open WebUI"
test_endpoint "http://localhost:11435/api/version" "Ollama API"
test_endpoint "http://localhost:8080" "SearXNG"
test_endpoint "http://localhost:8001" "Redis Insight"
test_endpoint "http://localhost:5001/health" "Docling"
test_endpoint "http://localhost:9998/tika" "Tika" 200

# Test Ollama models
print_step "2. Testing Ollama models..."
if models=$(docker-compose -f compose.local.yml exec -T ollama ollama list 2>/dev/null); then
    if echo "$models" | grep -q "llama3.2:3b"; then
        print_status "Ollama llama3.2:3b model: ✓"
    else
        print_warning "Ollama llama3.2:3b model: ⚠ (not found)"
    fi
    
    if echo "$models" | grep -q "nomic-embed-text"; then
        print_status "Ollama nomic-embed-text model: ✓"
    else
        print_warning "Ollama nomic-embed-text model: ⚠ (not found)"
    fi
else
    print_error "Failed to list Ollama models"
fi

# Test database connectivity
print_step "3. Testing database connectivity..."
if docker-compose -f compose.local.yml exec -T db pg_isready -U postgres >/dev/null 2>&1; then
    print_status "PostgreSQL database: ✓"
else
    print_error "PostgreSQL database: ✗"
fi

# Test Redis connectivity
print_step "4. Testing Redis connectivity..."
if docker-compose -f compose.local.yml exec -T redis redis-cli ping | grep -q "PONG"; then
    print_status "Redis cache: ✓"
else
    print_error "Redis cache: ✗"
fi

# Test document processing
print_step "5. Testing document processing..."

# Test Tika
if curl -s -X POST "http://localhost:9998/tika" \
    -H "Content-Type: application/pdf" \
    -H "Accept: text/plain" \
    --data-binary "@/dev/null" >/dev/null 2>&1; then
    print_status "Tika document processing: ✓"
else
    print_warning "Tika document processing: ⚠ (test failed)"
fi

# Test Docling health
if curl -s "http://localhost:5001/health" | grep -q "healthy\|ok"; then
    print_status "Docling document processing: ✓"
else
    print_warning "Docling document processing: ⚠ (health check failed)"
fi

# Test search functionality
print_step "6. Testing search functionality..."
if curl -s "http://localhost:8080/search?q=test" | grep -q "html\|search"; then
    print_status "SearXNG search: ✓"
else
    print_warning "SearXNG search: ⚠ (test failed)"
fi

# Test MCP servers
print_step "7. Testing MCP servers..."
if docker-compose -f compose.local.yml ps mcposerver | grep -q "Up"; then
    print_status "MCP server container: ✓"
    
    # Test if MCP server is responding
    if curl -s "http://localhost:8000" >/dev/null 2>&1; then
        print_status "MCP server connectivity: ✓"
    else
        print_warning "MCP server connectivity: ⚠ (not responding)"
    fi
else
    print_error "MCP server container: ✗"
fi

print_step "8. Test summary"
echo ""
echo "🎯 Test Results Summary"
echo "======================"
echo ""
echo "✅ Core Services:"
echo "   - Open WebUI interface"
echo "   - Ollama LLM API"
echo "   - PostgreSQL database"
echo "   - Redis cache"
echo ""
echo "🔍 Search & Processing:"
echo "   - SearXNG metasearch"
echo "   - Tika document extraction"
echo "   - Docling document parsing"
echo ""
echo "🛠️ Tools & Extensions:"
echo "   - MCP server framework"
echo ""
echo "Manual testing checklist:"
echo "1. Open http://localhost:3000"
echo "2. Create user account"
echo "3. Start a chat with AI"
echo "4. Upload a document"
echo "5. Test web search integration"
echo "6. Configure MCP tools in Settings"
echo ""
echo "If any tests failed, check logs with:"
echo "docker-compose -f compose.local.yml logs [service_name]"
