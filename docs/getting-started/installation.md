# 📥 Installation Guide

## 📋 Overview

This guide provides detailed step-by-step instructions for installing Open WebUI Hub in various environments. For quick setup, see the [Quick Start Guide](quick-start.md).

## 🎯 Prerequisites

Before starting installation:
- [ ] Review [System Requirements](system-requirements.md)
- [ ] Ensure Docker and Docker Compose are installed
- [ ] Have internet connection for downloading dependencies
- [ ] Administrative access to your system

## 🚀 Installation Methods

### Method 1: Automated Installation (Recommended)

The fastest and most reliable installation method:

```bash
# Clone the repository
git clone https://github.com/DIZ-admin/open-webui-hub.git
cd open-webui-hub

# Run automated setup
./scripts/setup-local.sh

# Deploy all services
./scripts/deploy-local.sh
```

### Method 2: Manual Installation

For users who prefer full control over the installation process:

#### Step 1: Clone Repository
```bash
git clone https://github.com/DIZ-admin/open-webui-hub.git
cd open-webui-hub
```

#### Step 2: Prepare Environment Files
```bash
# Copy example environment files
cp env/auth.example env/auth.env
cp env/db.example env/db.env
cp env/docling.example env/docling.env
cp env/edgetts.example env/edgetts.env
cp env/litellm.example env/litellm.env
cp env/ollama.example env/ollama.env
cp env/mcposerver.example env/mcposerver.env
cp env/openwebui.example env/openwebui.env
cp env/redis.example env/redis.env
cp env/searxng.example env/searxng.env
cp env/tika.example env/tika.env
cp env/watchtower.example env/watchtower.env
```

#### Step 3: Configure Services
```bash
# Copy configuration files
cp conf/nginx/nginx.example conf/nginx/nginx.conf
cp conf/nginx/conf.d/default.example conf/nginx/conf.d/default.conf
cp conf/mcposerver/config.example conf/mcposerver/config.json
cp conf/searxng/settings.yml.example conf/searxng/settings.yml
cp conf/searxng/uwsgi.ini.example conf/searxng/uwsgi.ini
cp conf/litellm/litellm_config.yaml.example conf/litellm/litellm_config.yaml
```

#### Step 4: Generate Security Keys
```bash
# Generate secure secret key
SECRET_KEY=$(openssl rand -hex 32)
echo "Generated secret: $SECRET_KEY"

# Update environment files with the same secret
sed -i "s/your_secret_key_here/$SECRET_KEY/g" env/auth.env
sed -i "s/your_secret_key_here/$SECRET_KEY/g" env/openwebui.env
sed -i "s/ultrasecretkey/$SECRET_KEY/g" conf/searxng/settings.yml
```

#### Step 5: Create Data Directories
```bash
# Create persistent data directories
mkdir -p data/{postgres,redis,ollama,openwebui}
sudo chown -R $USER:$USER data/
```

#### Step 6: Start Services
```bash
# Start all services
docker-compose -f compose.local.yml up -d

# Wait for services to be healthy
./scripts/wait-for-services.sh
```

## 🔧 Configuration Options

### Environment Variables

Key environment variables to configure:

#### Authentication & Security
```bash
# env/auth.env
WEBUI_SECRET_KEY=your_generated_secret_key_here

# env/openwebui.env  
WEBUI_SECRET_KEY=your_generated_secret_key_here
WEBUI_URL=http://localhost:3000
```

#### Database Configuration
```bash
# env/db.env
POSTGRES_DB=openwebui
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
```

#### AI Services
```bash
# env/ollama.env
OLLAMA_ORIGINS=*
OLLAMA_HOST=0.0.0.0:11434

# env/litellm.env
LITELLM_MASTER_KEY=sk-1234567890abcdef
LITELLM_PORT=4000
```

### Port Configuration

Default ports (can be changed in docker-compose file):
- Open WebUI: 3000
- Hub Service: 5003
- Ollama: 11435
- PostgreSQL: 5432
- Redis: 6379
- Redis UI: 8001
- SearXNG: 8080
- Tika: 9998
- Nginx: 80

## 🤖 AI Model Setup

### Download Basic Models
```bash
# Wait for Ollama to be ready
sleep 30

# Download lightweight models for testing
docker-compose -f compose.local.yml exec ollama ollama pull llama3.2:3b
docker-compose -f compose.local.yml exec ollama ollama pull qwen2.5-coder:1.5b

# Download embedding model for RAG
docker-compose -f compose.local.yml exec ollama ollama pull nomic-embed-text:latest
```

### Verify Model Installation
```bash
# List installed models
docker-compose -f compose.local.yml exec ollama ollama list

# Test model inference
curl http://localhost:11435/api/generate \
  -d '{"model": "llama3.2:3b", "prompt": "Hello, world!", "stream": false}'
```

## 🌐 Access and Verification

### Service Health Checks
```bash
# Check all services status
docker-compose -f compose.local.yml ps

# Verify service health
curl http://localhost:3000        # Open WebUI
curl http://localhost:5003/api/health  # Hub Service
curl http://localhost:11435/api/version # Ollama
curl http://localhost:8001        # Redis UI
```

### Web Interface Access

1. **Open WebUI**: http://localhost:3000
   - Create your first admin account
   - Configure AI models and settings

2. **Hub Service**: http://localhost:5003
   - Architecture visualization
   - Service discovery
   - System metrics

3. **Redis Management**: http://localhost:8001
   - Monitor cache usage
   - View stored sessions

## 🔒 Security Hardening

### Production Security Setup
```bash
# 1. Change default passwords
# Update env/db.env with strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# 2. Configure firewall
sudo ufw enable
sudo ufw allow 3000/tcp  # Open WebUI
sudo ufw allow 80/tcp    # Nginx
sudo ufw deny 5432/tcp   # Block direct DB access

# 3. Set up SSL/TLS (optional)
# Configure nginx with Let's Encrypt certificates
```

### User Management
```bash
# Create dedicated user for running services
sudo useradd -m -s /bin/bash openwebui
sudo usermod -aG docker openwebui

# Set proper permissions
sudo chown -R openwebui:openwebui /path/to/open-webui-hub
```

## 🔄 Post-Installation Tasks

### 1. Configure Monitoring
```bash
# Enable comprehensive logging
echo "DOCKER_LOG_LEVEL=info" >> .env

# Set up log rotation
sudo tee /etc/logrotate.d/docker-compose << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
EOF
```

### 2. Schedule Backups
```bash
# Create backup script
mkdir -p scripts/backup
cat > scripts/backup/daily-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/openwebui-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup databases
docker-compose exec -T db pg_dump -U postgres openwebui > "$BACKUP_DIR/database.sql"

# Backup data directories
tar -czf "$BACKUP_DIR/data.tar.gz" data/

# Backup configuration
tar -czf "$BACKUP_DIR/config.tar.gz" env/ conf/
EOF

chmod +x scripts/backup/daily-backup.sh
```

### 3. Performance Tuning
```bash
# Optimize Docker daemon
sudo tee /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

sudo systemctl restart docker
```

## 🆘 Troubleshooting Installation

### Common Issues

#### Services Not Starting
```bash
# Check Docker daemon
sudo systemctl status docker

# Check service logs
docker-compose -f compose.local.yml logs [service-name]

# Restart specific service
docker-compose -f compose.local.yml restart [service-name]
```

#### Port Conflicts
```bash
# Check what's using a port
sudo netstat -tulpn | grep :3000

# Stop conflicting services
sudo systemctl stop [conflicting-service]
```

#### Permission Issues
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/
sudo chmod -R 755 data/

# Fix Docker socket permissions
sudo usermod -aG docker $USER
newgrp docker
```

### Getting Help

If you encounter issues:
1. Check [Troubleshooting Guide](../operations/troubleshooting.md)
2. Review service logs: `docker-compose logs [service]`
3. Join our [Discord community](https://discord.gg/open-webui-hub)
4. Open an issue on [GitHub](https://github.com/DIZ-admin/open-webui-hub/issues)

## 🔄 Next Steps

After successful installation:
1. [Configuration Guide](../configuration/README.md) - Customize your setup
2. [Developer Guide](../development/development-guide.md) - Development environment
3. [Operations Guide](../operations/README.md) - System administration
4. [Monitoring Setup](../operations/monitoring.md) - Set up comprehensive monitoring

---
*For production deployments, review the [Security Configuration](../configuration/security.md) guide*