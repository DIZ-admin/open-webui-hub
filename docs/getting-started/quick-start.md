# ⚡ Quick Start Guide

## One-Command Deployment

```bash
# Clone repository (if not already done)
git clone https://github.com/DIZ-admin/open-webui-hub.git
cd open-webui-hub

# Run automated deployment
./scripts/deploy-local.sh
```

This script automatically:
- ✅ Checks dependencies
- ✅ Creates configuration
- ✅ Starts all services
- ✅ Downloads AI models
- ✅ Tests functionality

## Manual Setup

If you prefer step-by-step control:

### 1. Setup Environment
```bash
# Copy and configure environment files
./scripts/setup-local.sh
```

### 2. Start Services
```bash
# Start all containers
docker-compose -f compose.local.yml up -d
```

### 3. Download AI Models
```bash
# Download basic models
docker-compose -f compose.local.yml exec ollama ollama pull llama3.2:3b
docker-compose -f compose.local.yml exec ollama ollama pull qwen2.5-coder:1.5b
```

## 🌐 Access Points

After successful deployment:

| Service | URL | Description |
|---------|-----|-------------|
| **Open WebUI** | http://localhost:3000 | Main web interface |
| **Hub Service** | http://localhost:5003 | Architecture visualization |
| **Ollama API** | http://localhost:11435 | LLM API server |
| **Redis UI** | http://localhost:8001 | Cache management |
| **SearXNG** | http://localhost:8080 | Search engine |
| **Tika** | http://localhost:9998 | Document processing |

## 🔧 System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **Docker**: 20.10+ with Docker Compose 2.0+
- **RAM**: 8GB (16GB+ recommended for AI models)
- **Storage**: 20GB free space
- **Network**: Internet connection for initial setup

### Recommended Specifications
- **CPU**: 4+ cores (8+ cores for better AI performance)
- **RAM**: 16GB+ (32GB for multiple large models)
- **Storage**: SSD with 50GB+ free space
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster inference)

## 🚀 Next Steps

After successful installation:

1. **Configure Services**: [Service Configuration Guide](../configuration/services/README.md)
2. **Development Setup**: [Developer Guide](../development/development-guide.md)
3. **Monitoring**: [Dashboard and Monitoring](../operations/monitoring.md)
4. **Troubleshooting**: [Common Issues](../operations/troubleshooting.md)

## 🔍 Verification

Verify your installation:

```bash
# Check all services are running
docker-compose -f compose.local.yml ps

# Test Ollama API
curl http://localhost:11435/api/version

# Test main interface
curl http://localhost:3000
```

All services should show as "healthy" or "running" status.

## 📚 Quick Links

- [Environment Variables](../configuration/environment-variables.md)
- [LiteLLM Configuration](../configuration/services/litellm.md)
- [API Reference](../development/api-reference.md)
- [Performance Tuning](../operations/performance.md)

---
*For detailed configuration and advanced setup options, see the [Configuration Guide](../configuration/README.md)*