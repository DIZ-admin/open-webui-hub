# 🤖 LiteLLM Configuration

## 📋 Overview

LiteLLM serves as a unified proxy for accessing various LLM providers in Open WebUI Hub, including local Ollama models and external APIs (OpenAI, Anthropic, Google).

## 🎯 Prerequisites

- Docker and Docker Compose installed
- Open WebUI Hub basic setup completed
- [System Requirements](../../getting-started/system-requirements.md) met

## 🔧 Configuration Files

### Primary Configuration
- **File**: `conf/litellm/litellm_config.yaml`
- **Purpose**: Main LiteLLM proxy configuration
- **Format**: YAML

### Environment Variables
- **File**: `env/litellm.env`
- **Purpose**: Runtime configuration and API keys
- **Format**: KEY=value

## 📊 Default Configuration

### Core Settings

| Setting | Default Value | Description |
|---------|---------------|-------------|
| Port | 4000 | Service listening port |
| API Base | `http://localhost:4000/v1/` | Base API endpoint |
| Master Key | `sk-1234567890abcdef` | Authentication key |
| Request Timeout | 120s | Maximum request duration |
| Max Retries | 2 | Retry failed requests |

### Available Models

#### Local Models (via Ollama)
- `llama3.2:3b` - General conversation model
- `qwen2.5-coder:1.5b` - Specialized coding model
- `llama3` - Alias for llama3.2:3b
- `coder` - Alias for qwen2.5-coder:1.5b
- `auto` - Automatic model selection

#### External Providers (require API keys)
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-5-sonnet`, `claude-3-haiku`  
- **Google**: `gemini-1.5-pro`, `gemini-1.5-flash`

## 🔑 API Usage

### Basic Request
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-1234567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

### List Available Models
```bash
curl -H "Authorization: Bearer sk-1234567890abcdef" \
  http://localhost:4000/v1/models
```

### Health Check
```bash
curl -H "Authorization: Bearer sk-1234567890abcdef" \
  http://localhost:4000/health
```

## 🔄 Fallback Configuration

### Model Groups with Fallbacks
```yaml
# Example fallback chain
model_list:
  - model_name: chat-fallback
    litellm_params:
      model: llama3.2:3b
    fallbacks:
      - model: gpt-4o-mini
      - model: claude-3-haiku
      - model: gemini-1.5-flash
```

### Performance Groups
- **fast**: Local models → Fast external APIs
- **advanced**: Premium external APIs → Local fallback
- **coding**: Specialized code models → General purpose
- **balanced**: Mix of speed and quality

## 🔐 External Provider Setup

### Adding API Keys

Edit `env/litellm.env`:
```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google
GOOGLE_API_KEY=your_google_api_key_here

# Azure OpenAI (optional)
AZURE_API_KEY=your_azure_key_here
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2023-12-01-preview
```

### Restart Service
```bash
docker-compose -f compose.local.yml restart litellm
```

### Verify Configuration
```bash
# Check available models
curl -H "Authorization: Bearer sk-1234567890abcdef" \
  http://localhost:4000/v1/models | jq '.data[].id'
```

## 📈 Performance Optimization

### Local Model Optimization
```yaml
# conf/litellm/litellm_config.yaml
general_settings:
  max_parallel_requests: 10  # Optimize for local resources
  request_timeout: 120       # Allow time for model loading
  
litellm_settings:
  success_callback: ["redis"]
  failure_callback: ["redis"]
  cache:
    type: "redis"
    host: "redis"
    port: 6379
    ttl: 3600
```

### External API Optimization
```yaml
general_settings:
  max_parallel_requests: 50  # Higher for external APIs
  request_timeout: 60        # Shorter timeouts
  rate_limit_per_user: 100   # Requests per minute
```

## 🔍 Monitoring and Testing

### Direct API Testing

Check LiteLLM status directly:
```bash
# Service status
curl http://localhost:4000/v1/models

# Test specific model
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3", "messages": [{"role": "user", "content": "Test message"}]}'
```

### Manual Testing
```bash
# Test local model
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-1234567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [{"role": "user", "content": "Hello from local model!"}],
    "max_tokens": 50
  }'

# Test external model (if configured)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-1234567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello from OpenAI!"}],
    "max_tokens": 50
  }'
```

## 🎛️ Advanced Configuration

### Custom Model Configurations
```yaml
model_list:
  - model_name: custom-llama
    litellm_params:
      model: ollama/llama3.2:3b
      api_base: http://ollama:11434
      temperature: 0.7
      max_tokens: 2048
    model_info:
      mode: chat
      input_cost_per_token: 0
      output_cost_per_token: 0
```

### Rate Limiting
```yaml
router_settings:
  routing_strategy: "least-busy"
  allowed_failures: 3
  cooldown_time: 30
  
general_settings:
  master_key: "sk-1234567890abcdef"
  database_url: "postgresql://postgres:postgres@db:5432/openwebui"
```

### Logging Configuration
```yaml
litellm_settings:
  set_verbose: true
  json_logs: true
  log_level: "INFO"
  success_callback: ["redis", "postgresql"]
  failure_callback: ["redis", "postgresql"]
```

## 🚨 Troubleshooting

### Common Issues

#### Timeout Errors
**Symptoms**: Requests timing out, especially for local models
**Solution**: 
```bash
# Increase timeouts in config
general_settings:
  request_timeout: 180  # 3 minutes for large models
```

#### Health Endpoint Hanging
**Symptoms**: `/health` endpoint not responding
**Solution**: Use `/v1/models` endpoint instead for health checks

#### External Models Not Working
**Symptoms**: External APIs returning authentication errors
**Solution**:
1. Verify API keys in `env/litellm.env`
2. Check API key permissions and quotas
3. Restart LiteLLM service

#### Memory Issues
**Symptoms**: High memory usage, OOM errors
**Solution**:
```bash
# Reduce parallel requests
general_settings:
  max_parallel_requests: 5
  
# Add memory limits to docker-compose
services:
  litellm:
    mem_limit: 2g
```

### Debug Mode
```bash
# Enable debug logging
echo "LITELLM_LOG_LEVEL=DEBUG" >> env/litellm.env
docker-compose -f compose.local.yml restart litellm

# View detailed logs
docker-compose -f compose.local.yml logs -f litellm
```

## ✅ Verification Checklist

- [ ] LiteLLM service is running and healthy
- [ ] Can list available models via API
- [ ] Local models respond correctly
- [ ] External APIs work (if configured)
- [ ] Fallback chains function properly
- [ ] Hub Service integration shows correct status

## 📚 Related Documentation

- [Ollama Configuration](ollama.md) - Local LLM server setup
- [API Reference](../../development/api-reference.md) - Full API documentation  
- [Troubleshooting](../../operations/troubleshooting.md) - Common issues and solutions
- [Performance Optimization](../../operations/performance.md) - System tuning

## 🏷️ Tags
#litellm #ai #configuration #proxy #api

---
*For production deployments, review the [Security Configuration](../security.md) guide*