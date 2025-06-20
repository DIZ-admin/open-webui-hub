# ⚙️ Environment Variables

## 📋 Overview

Complete reference for all environment variables used in Open WebUI Hub. Variables are organized by service and can be configured in their respective `.env` files.

## 🔧 Global Settings



## 🤖 AI Services

### Ollama Configuration
**File**: `env/ollama.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_ORIGINS` | `*` | Allowed CORS origins |
| `OLLAMA_HOST` | `0.0.0.0:11434` | Server bind address |
| `OLLAMA_MODELS` | `/root/.ollama/models` | Model storage directory |
| `OLLAMA_KEEP_ALIVE` | `5m` | Model memory retention |
| `OLLAMA_MAX_LOADED_MODELS` | `3` | Maximum concurrent models |
| `OLLAMA_MAX_QUEUE` | `512` | Request queue size |
| `OLLAMA_DEBUG` | `false` | Enable debug logging |

### LiteLLM Configuration  
**File**: `env/litellm.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `LITELLM_MASTER_KEY` | `sk-1234567890abcdef` | Master API key |
| `LITELLM_PORT` | `4000` | Service port |
| `LITELLM_LOG_LEVEL` | `INFO` | Logging level |
| `OPENAI_API_KEY` | - | OpenAI API key (optional) |
| `ANTHROPIC_API_KEY` | - | Anthropic API key (optional) |
| `GOOGLE_API_KEY` | - | Google AI API key (optional) |
| `AZURE_API_KEY` | - | Azure OpenAI key (optional) |
| `AZURE_API_BASE` | - | Azure OpenAI endpoint (optional) |

### Docling Configuration
**File**: `env/docling.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCLING_LOG_LEVEL` | `INFO` | Logging level |
| `DOCLING_PORT` | `5001` | Service port |
| `DOCLING_HOST` | `0.0.0.0` | Bind address |

### EdgeTTS Configuration
**File**: `env/edgetts.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `EDGETTS_PORT` | `5050` | Service port |
| `EDGETTS_HOST` | `0.0.0.0` | Bind address |

## 🗄️ Database Services

### PostgreSQL Configuration
**File**: `env/db.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_DB` | `openwebui` | Database name |
| `POSTGRES_USER` | `postgres` | Database username |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `POSTGRES_HOST` | `db` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `PGDATA` | `/var/lib/postgresql/data` | Data directory |

### Redis Configuration
**File**: `env/redis.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `redis` | Redis server host |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_PASSWORD` | - | Redis password (optional) |
| `REDIS_DB` | `0` | Default database number |
| `REDIS_MAXMEMORY` | `256mb` | Maximum memory usage |
| `REDIS_MAXMEMORY_POLICY` | `allkeys-lru` | Eviction policy |

## 🌐 Web Services

### Open WebUI Configuration
**File**: `env/openwebui.env`

#### Core Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `WEBUI_SECRET_KEY` | - | **Required** - JWT secret key |
| `WEBUI_URL` | `http://localhost:3000` | Public URL |
| `ENV` | `dev` | Environment (dev/prod) |
| `GLOBAL_LOG_LEVEL` | `info` | Global logging level |
| `ANONYMIZED_TELEMETRY` | `false` | Enable telemetry |

#### Database Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@db:5432/openwebui` | Primary database |
| `PGVECTOR_DB_URL` | `postgresql://postgres:postgres@db:5432/openwebui` | Vector database |
| `VECTOR_DB` | `pgvector` | Vector database type |

#### AI Integration
| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URLS` | `http://ollama:11434` | Ollama API endpoints |
| `ENABLE_OLLAMA_API` | `true` | Enable Ollama integration |
| `ENABLE_OPENAI_API` | `false` | Enable OpenAI integration |
| `ENABLE_IMAGE_GENERATION` | `false` | Enable image generation |

#### RAG Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_EMBEDDING_ENGINE` | `ollama` | Embedding engine |
| `RAG_EMBEDDING_MODEL` | `nomic-embed-text:latest` | Embedding model |
| `RAG_OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama for embeddings |
| `RAG_TEXT_SPLITTER` | `token` | Text splitting method |

#### Search Integration
| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_WEB_SEARCH` | `true` | Enable web search |
| `ENABLE_RAG_WEB_SEARCH` | `true` | Enable RAG web search |
| `WEB_SEARCH_ENGINE` | `searxng` | Search engine |
| `RAG_WEB_SEARCH_ENGINE` | `searxng` | RAG search engine |
| `SEARXNG_QUERY_URL` | `http://searxng:8080/search?q=<query>` | SearXNG endpoint |

#### Document Processing
| Variable | Default | Description |
|----------|---------|-------------|
| `CONTENT_EXTRACTION_ENGINE` | `docling` | Document extraction engine |
| `DOCLING_SERVER_URL` | `http://docling:5001` | Docling service URL |
| `TIKA_SERVER_URL` | `http://tika:9998` | Tika service URL |
| `PDF_EXTRACT_IMAGES` | `true` | Extract images from PDFs |

#### Audio Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `AUDIO_TTS_ENGINE` | `openai` | TTS engine |
| `AUDIO_TTS_MODEL` | `tts-1-hd` | TTS model |
| `AUDIO_TTS_OPENAI_API_BASE_URL` | `http://edgetts:5050/v1` | TTS API base |
| `AUDIO_TTS_API_KEY` | `your_api_key_here` | TTS API key |
| `AUDIO_TTS_VOICE` | `en-US-EmmaMultilingualNeural` | Default voice |

### SearXNG Configuration
**File**: `env/searxng.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_SECRET` | - | **Required** - Secret key |
| `SEARXNG_BASE_URL` | `http://localhost:8080/searxng` | Base URL |
| `SEARXNG_REDIS_URL` | `redis://redis:6379/1` | Redis connection |

## 🔐 Security Services

### Auth Service Configuration
**File**: `env/auth.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBUI_SECRET_KEY` | - | **Required** - JWT secret (same as Open WebUI) |
| `AUTH_PORT` | `8080` | Service port |
| `AUTH_HOST` | `0.0.0.0` | Bind address |

### Watchtower Configuration
**File**: `env/watchtower.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `WATCHTOWER_NOTIFICATIONS` | - | Notification settings |
| `WATCHTOWER_CLEANUP` | `true` | Remove old images |
| `WATCHTOWER_POLL_INTERVAL` | `300` | Check interval (seconds) |
| `WATCHTOWER_DEBUG` | `false` | Enable debug mode |

## 🛠️ Utility Services

### Tika Configuration
**File**: `env/tika.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `TIKA_PORT` | `9998` | Service port |
| `TIKA_HOST` | `0.0.0.0` | Bind address |

### MCP Server Configuration  
**File**: `env/mcposerver.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `MCPO_PORT` | `8000` | Service port |
| `MCPO_HOST` | `0.0.0.0` | Bind address |

## 🎯 Port Configuration

### Default Port Mapping
| Service | Internal Port | External Port | Purpose |
|---------|---------------|---------------|---------|
| Open WebUI | 8080 | 3000 | Main interface |

| Ollama | 11434 | 11435 | LLM API |
| LiteLLM | 4000 | 4000 | AI proxy |
| PostgreSQL | 5432 | 5432 | Database |
| Redis | 6379 | 6379 | Cache |
| Redis UI | 8001 | 8001 | Cache management |
| SearXNG | 8080 | 8080 | Search |
| Tika | 9998 | 9998 | Document processing |
| Nginx | 80 | 80 | Reverse proxy |

### Changing Ports
To change external ports, edit `compose.local.yml`:
```yaml
services:
  openwebui:
    ports:
      - "3001:8080"  # Change external port to 3001
```

## 🔒 Security Considerations

### Required Secret Keys
These variables must be set with secure values:
- `WEBUI_SECRET_KEY` - Must be same across auth.env and openwebui.env
- `SEARXNG_SECRET` - Unique secret for SearXNG
- `POSTGRES_PASSWORD` - Secure database password

### API Keys (Optional)
External AI provider keys can be added for extended functionality:
- `OPENAI_API_KEY` - For OpenAI models
- `ANTHROPIC_API_KEY` - For Claude models  
- `GOOGLE_API_KEY` - For Gemini models

### Security Best Practices
```bash
# Generate secure secrets
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Never commit secrets to version control
echo "*.env" >> .gitignore
```

## ✅ Configuration Validation

### Check Current Settings
```bash
# View all environment variables
docker-compose -f compose.local.yml config

# Check specific service config
docker-compose -f compose.local.yml exec openwebui env | grep WEBUI
```

### Test Configuration
```bash
# Validate PostgreSQL connection
docker-compose -f compose.local.yml exec db psql -U postgres -d openwebui -c "SELECT version();"

# Test Redis connection
docker-compose -f compose.local.yml exec redis redis-cli ping
```

## 📚 Related Documentation

- [Service Configuration](services/README.md) - Individual service setup
- [Security Settings](security.md) - Security configuration
- [Getting Started](../getting-started/README.md) - Initial setup
- [Troubleshooting](../operations/troubleshooting.md) - Common issues

## 🏷️ Tags
#configuration #environment #variables #setup

---
*Always backup configuration files before making changes*