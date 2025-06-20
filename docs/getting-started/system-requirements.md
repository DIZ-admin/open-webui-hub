# 🔧 System Requirements

## 📋 Overview

Open WebUI Hub requires specific hardware and software configurations to run efficiently. This document outlines the minimum and recommended specifications for optimal performance.

## 🖥️ Hardware Requirements

### Minimum Configuration
- **CPU**: 4 cores (Intel i5 or AMD Ryzen 5 equivalent)
- **RAM**: 8GB
- **Storage**: 20GB free space on SSD
- **Network**: Broadband internet connection

### Recommended Configuration
- **CPU**: 8+ cores (Intel i7/i9 or AMD Ryzen 7/9)
- **RAM**: 16GB+ (32GB for multiple large AI models)
- **Storage**: 50GB+ free space on NVMe SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional, for accelerated AI inference)
- **Network**: High-speed internet for model downloads

### Production Configuration
- **CPU**: 16+ cores
- **RAM**: 64GB+
- **Storage**: 200GB+ enterprise SSD with backup
- **GPU**: Multiple NVIDIA GPUs (A100, RTX 4090, etc.)
- **Network**: Dedicated bandwidth with redundancy

## 💿 Operating System Support

### Fully Supported
- **Ubuntu**: 20.04 LTS, 22.04 LTS, 24.04 LTS
- **Debian**: 11 (Bullseye), 12 (Bookworm)
- **CentOS/RHEL**: 8, 9
- **macOS**: 11.0+ (Big Sur and newer)

### Experimental Support
- **Windows**: 10/11 with WSL2
- **Fedora**: 36+
- **Arch Linux**: Rolling release

## 🐳 Docker Requirements

### Docker Engine
- **Version**: 20.10.0 or newer
- **Storage Driver**: overlay2 (recommended)
- **Logging Driver**: json-file or journald

### Docker Compose
- **Version**: 2.0.0 or newer
- **Compose File Format**: 3.8+

### Installation Verification
```bash
# Check Docker version
docker --version
# Expected: Docker version 20.10+ or newer

# Check Docker Compose version  
docker compose version
# Expected: Docker Compose version 2.0+ or newer

# Test Docker functionality
docker run hello-world
```

## 📦 Additional Software Dependencies

### Required
- **Git**: 2.30+ (for cloning repository)
- **Curl**: 7.68+ (for health checks and API calls)
- **OpenSSL**: 1.1.1+ (for security features)

### Optional
- **NVIDIA Container Toolkit**: For GPU acceleration
- **Node.js**: 18+ (for development tasks)
- **Python**: 3.9+ (for custom scripts)

## 🌐 Network Requirements

### Ports Used
| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Open WebUI | 3000 | HTTP | Main web interface |
| Hub Service | 5003 | HTTP | Architecture visualization |
| Ollama | 11435 | HTTP | LLM API server |
| PostgreSQL | 5432 | TCP | Database |
| Redis | 6379 | TCP | Cache |
| Redis UI | 8001 | HTTP | Cache management |
| SearXNG | 8080 | HTTP | Search engine |
| Tika | 9998 | HTTP | Document processing |
| Nginx | 80 | HTTP | Reverse proxy |

### Firewall Configuration
```bash
# Allow required ports (adjust for your firewall)
sudo ufw allow 3000/tcp  # Open WebUI
sudo ufw allow 5003/tcp  # Hub Service
sudo ufw allow 80/tcp    # Nginx
```

### Internet Access
- **Model Downloads**: 5-50GB depending on AI models
- **Container Images**: 2-5GB total
- **Package Updates**: Ongoing as needed

## 🔒 Security Requirements

### User Permissions
- **Docker Group**: User must be in docker group
- **Sudo Access**: Required for initial setup
- **File Permissions**: Write access to project directory

### Security Considerations
- **SELinux/AppArmor**: May require configuration
- **Antivirus**: Exclude Docker directories from real-time scanning
- **Corporate Networks**: May need proxy configuration

## ⚡ Performance Optimization

### Storage Optimization
```bash
# Enable Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Configure Docker daemon for better performance
# /etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Memory Optimization
- **Swap**: Disable or minimize swap usage
- **Memory Overcommit**: Configure vm.overcommit_memory=1
- **Docker Memory**: Set appropriate limits per service

## 🧪 Environment Testing

### Quick System Check
```bash
# Download and run system check script
curl -sSL https://raw.githubusercontent.com/DIZ-admin/open-webui-hub/main/scripts/check-requirements.sh | bash
```

### Manual Verification
```bash
# Check CPU cores
nproc

# Check available RAM
free -h

# Check disk space
df -h

# Check Docker status
docker info
```

## 🔄 Next Steps

After verifying system requirements:
1. [Quick Start Guide](quick-start.md) - Begin installation
2. [Installation Guide](installation.md) - Detailed setup
3. [Configuration](../configuration/README.md) - Customize your setup

---
*For production deployments, consider additional requirements for high availability and disaster recovery*