#!/bin/bash

# Open WebUI Hub - Local Development Setup Script
# This script sets up the project for local development without Cloudflare

set -e

echo "🚀 Open WebUI Hub - Local Development Setup"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to generate secure random key
generate_secret() {
    openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || head -c 32 /dev/urandom | xxd -p -c 32
}

# Check dependencies
print_step "1. Checking dependencies..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Dependencies check passed ✓"

# Generate secrets
print_step "2. Generating secure secrets..."

SECRET_KEY=$(generate_secret)
if [ -z "$SECRET_KEY" ]; then
    print_error "Failed to generate secret key"
    exit 1
fi

print_status "Generated secure secret key: $SECRET_KEY"

# Create directories
print_step "3. Creating data directories..."

mkdir -p data/{postgres,redis,ollama,openwebui}
print_status "Data directories created ✓"

# Copy configuration files
print_step "4. Setting up configuration files..."

# Configuration files
cp conf/nginx/nginx.example conf/nginx/nginx.conf
cp conf/nginx/conf.d/default.example conf/nginx/conf.d/default.conf
cp conf/mcposerver/config.example conf/mcposerver/config.json
cp conf/searxng/settings.yml.example conf/searxng/settings.yml
cp conf/searxng/uwsgi.ini.example conf/searxng/uwsgi.ini

print_status "Configuration files copied ✓"

# Create environment files with generated secrets
print_step "5. Creating environment files..."

# Auth environment
cat > env/auth.env << ENVEOF
WEBUI_SECRET_KEY=$SECRET_KEY
ENVEOF

# Database environment
cat > env/db.env << ENVEOF
POSTGRES_DB=openwebui
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
ENVEOF

# Docling environment
cat > env/docling.env << ENVEOF
# Docling configuration
DOCLING_LOG_LEVEL=INFO
ENVEOF

# EdgeTTS environment
cat > env/edgetts.env << ENVEOF
# EdgeTTS configuration
ENVEOF

# Ollama environment
cat > env/ollama.env << ENVEOF
# Ollama configuration
OLLAMA_ORIGINS=*
ENVEOF

# MCP Server environment
cat > env/mcposerver.env << ENVEOF
# MCP Server configuration
ENVEOF

# OpenWebUI environment
cat > env/openwebui.env << ENVEOF
ANONYMIZED_TELEMETRY=false
AUDIO_TTS_API_KEY=your_api_key_here
AUDIO_TTS_ENGINE=openai
AUDIO_TTS_MODEL=tts-1-hd
AUDIO_TTS_OPENAI_API_BASE_URL=http://edgetts:5050/v1
AUDIO_TTS_OPENAI_API_KEY=your_api_key_here
AUDIO_TTS_VOICE=en-US-EmmaMultilingualNeural
CONTENT_EXTRACTION_ENGINE=docling
DATABASE_URL="postgresql://postgres:postgres@db:5432/openwebui"
DOCLING_SERVER_URL=http://docling:5001
ENABLE_EVALUATION_ARENA_MODELS=false
ENABLE_IMAGE_GENERATION=false
ENABLE_OLLAMA_API=true
ENABLE_OPENAI_API=false
ENABLE_RAG_WEB_SEARCH=true
ENABLE_WEB_SEARCH=true
ENV=dev
GLOBAL_LOG_LEVEL=info
OLLAMA_BASE_URLS=http://ollama:11434
PDF_EXTRACT_IMAGES=true
PGVECTOR_DB_URL=postgresql://postgres:postgres@db:5432/openwebui
RAG_EMBEDDING_ENGINE=ollama
RAG_EMBEDDING_MODEL=nomic-embed-text:latest
RAG_OLLAMA_BASE_URL=http://ollama:11434
RAG_TEXT_SPLITTER=token
RAG_WEB_SEARCH_ENGINE=searxng
RAG_WEB_SEARCH_RESULT_COUNT=6
RAG_WEB_SEARCH_CONCURRENT_REQUESTS=10
SEARXNG_QUERY_URL=http://searxng:8080/search?q=<query>
TIKA_SERVER_URL=http://tika:9998
USE_CUDA_DOCKER=false
VECTOR_DB=pgvector
WEB_SEARCH_ENGINE=searxng
WEBUI_SECRET_KEY=$SECRET_KEY
WEBUI_URL=http://localhost
ENVEOF

# Redis environment
cat > env/redis.env << ENVEOF
# Redis configuration
ENVEOF

# SearXNG environment
cat > env/searxng.env << ENVEOF
SEARXNG_SECRET=$SECRET_KEY
SEARXNG_BASE_URL=http://localhost:8080/searxng
ENVEOF

# Tika environment
cat > env/tika.env << ENVEOF
# Tika configuration
ENVEOF

# Watchtower environment
cat > env/watchtower.env << ENVEOF
# Watchtower configuration - disabled notifications for local dev
WATCHTOWER_NOTIFICATIONS=
ENVEOF

print_status "Environment files created with secure secrets ✓"

# Update nginx configuration for localhost
print_step "6. Updating nginx configuration for localhost..."

sed -i.bak 's/<domain-name>/localhost/g' conf/nginx/conf.d/default.conf
rm -f conf/nginx/conf.d/default.conf.bak

print_status "Nginx configuration updated for localhost ✓"

# Update SearXNG configuration
print_step "7. Updating SearXNG configuration..."

sed -i.bak "s/ultrasecretkey/$SECRET_KEY/g" conf/searxng/settings.yml
rm -f conf/searxng/settings.yml.bak

print_status "SearXNG configuration updated ✓"

print_step "8. Setup completed successfully!"
echo ""
echo "🎉 Local development environment is ready!"
echo ""
echo "Next steps:"
echo "1. Start the services: docker-compose -f compose.local.yml up -d"
echo "2. Wait for all services to be healthy (may take 5-10 minutes)"
echo "3. Download an Ollama model: docker-compose -f compose.local.yml exec ollama ollama pull llama3.2:3b"
echo "4. Access Open WebUI at: http://localhost:3000"
echo ""
echo "Service endpoints:"
echo "- Open WebUI: http://localhost:3000"
echo "- Ollama API: http://localhost:11434"
echo "- SearXNG: http://localhost:8080"
echo "- Redis Insight: http://localhost:8001"
echo "- Docling: http://localhost:5001"
echo "- Tika: http://localhost:9998"
echo ""
echo "Generated secret key: $SECRET_KEY"
echo "⚠️  Save this key securely - it's used for authentication!"
