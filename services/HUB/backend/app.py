#!/usr/bin/env python3
"""
Hub Service Backend API for Open WebUI Hub
Provides service discovery, architecture visualization, and system monitoring
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from functools import lru_cache

# Configure logging
def setup_logging():
    """Setup structured logging for the hub service"""
    log_level = os.getenv('HUB_LOG_LEVEL', 'INFO')
    log_format = os.getenv('HUB_LOG_FORMAT', 'simple')

    if log_format == 'json':
        import json
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno,
                    'service': 'hub-api'
                }
                return json.dumps(log_entry)
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger('hub-api')
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(handler)

    return logger

# Initialize logger
logger = setup_logging()

# Load environment configuration
def load_env_config():
    """Load configuration from environment variables"""
    return {
        'api_host': os.getenv('HUB_API_HOST', '0.0.0.0'),
        'api_port': int(os.getenv('HUB_API_PORT', 5003)),
        'debug_mode': os.getenv('HUB_DEBUG_MODE', 'false').lower() == 'true',
        'docker_compose_file': os.getenv('HUB_DOCKER_COMPOSE_FILE', 'compose.local.yml'),
        'health_check_timeout': int(os.getenv('HUB_HEALTH_CHECK_TIMEOUT', 5)),
        'cache_ttl': int(os.getenv('HUB_CACHE_TTL', 30)),
        'secret_key': os.getenv('HUB_SECRET_KEY', 'change-this-secret-key-in-production'),

        'enable_service_discovery': os.getenv('HUB_ENABLE_SERVICE_DISCOVERY', 'true').lower() == 'true',
    }

# Global configuration
CONFIG = load_env_config()

import requests
import docker
import docker.errors
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.secret_key = CONFIG['secret_key']

# Track application start time
_app_start_time = time.time()

# Global cache
_cache = {}
_cache_timestamps = {}
_cache_lock = threading.Lock()

# Docker client
try:
    docker_client = docker.from_env()
    logger.info("🐳 Docker client initialized successfully")
except Exception as e:
    docker_client = None
    logger.warning(f"⚠️ Docker client initialization failed: {e}")

# Service definitions based on compose.local.yml
SERVICES_CONFIG = {
    'nginx': {
        'name': 'Nginx',
        'category': 'Gateway',
        'layer': 'presentation',
        'port': 80,
        'container_name': 'open-webui-hub-nginx-1',
        'health_url': 'http://localhost:80',
        'description': 'Reverse proxy и load balancer для маршрутизации трафика'
    },
    'openwebui': {
        'name': 'Open WebUI',
        'category': 'Core',
        'layer': 'application',
        'port': 3000,
        'container_name': 'open-webui-hub-openwebui-1',
        'health_url': 'http://localhost:3000',
        'description': 'Основной веб-интерфейс для взаимодействия с AI моделями'
    },

    'hub': {
        'name': 'Hub Service',
        'category': 'Architecture',
        'layer': 'application',
        'port': 5003,
        'container_name': 'open-webui-hub-hub-1',
        'health_url': 'http://localhost:5003/api/health',
        'description': 'Сервис архитектурной визуализации и service discovery'
    },
    'ollama': {
        'name': 'Ollama',
        'category': 'AI',
        'layer': 'service',
        'port': 11435,
        'container_name': 'open-webui-hub-ollama-1',
        'health_url': 'http://localhost:11435/api/version',
        'description': 'Локальный сервер для запуска LLM моделей'
    },
    'litellm': {
        'name': 'LiteLLM',
        'category': 'AI',
        'layer': 'service',
        'port': 4000,
        'container_name': 'open-webui-hub-litellm-1',
        'health_url': 'http://localhost:4000/v1/models',
        'health_method': 'GET',  # LiteLLM doesn't support HEAD
        'description': 'Унифицированный API прокси для различных LLM провайдеров'
    },
    'db': {
        'name': 'PostgreSQL + pgvector',
        'category': 'Data',
        'layer': 'data',
        'port': 5432,
        'container_name': 'open-webui-hub-db-1',
        'health_url': None,  # PostgreSQL doesn't have HTTP health endpoint
        'description': 'Основная база данных с поддержкой векторного поиска'
    },
    'redis': {
        'name': 'Redis Stack',
        'category': 'Data',
        'layer': 'data',
        'port': 6379,
        'container_name': 'open-webui-hub-redis-1',
        'health_url': 'http://localhost:8001',
        'description': 'In-memory база данных с поддержкой векторного поиска и кэширования'
    },
    'auth': {
        'name': 'JWT Auth Validator',
        'category': 'Security',
        'layer': 'application',
        'port': 9090,
        'container_name': 'open-webui-hub-auth-1',
        'health_url': 'http://localhost:9090/health',
        'description': 'Сервис валидации JWT токенов и авторизации'
    },
    'docling': {
        'name': 'Docling',
        'category': 'Processing',
        'layer': 'service',
        'port': 5001,
        'container_name': 'open-webui-hub-docling-1',
        'health_url': 'http://localhost:5001/health',
        'health_method': 'GET',  # Docling doesn't support HEAD
        'description': 'Сервис для обработки и парсинга документов с использованием AI'
    },
    'tika': {
        'name': 'Apache Tika',
        'category': 'Processing',
        'layer': 'service',
        'port': 9998,
        'container_name': 'open-webui-hub-tika-1',
        'health_url': 'http://localhost:9998/tika',
        'description': 'Извлечение текста и метаданных из документов различных форматов'
    },
    'edgetts': {
        'name': 'EdgeTTS',
        'category': 'Media',
        'layer': 'service',
        'port': 5050,
        'container_name': 'open-webui-hub-edgetts-1',
        'health_url': 'http://localhost:5050',
        'health_method': 'GET',  # Use simple GET to root
        'description': 'Text-to-Speech сервис для синтеза речи с использованием Microsoft Edge'
    },
    'searxng': {
        'name': 'SearXNG',
        'category': 'Search',
        'layer': 'service',
        'port': 8080,
        'container_name': 'open-webui-hub-searxng-1',
        'health_url': 'http://localhost:8080',
        'description': 'Приватный мета-поисковик для агрегации результатов из различных источников'
    },
    'mcposerver': {
        'name': 'MCP Server',
        'category': 'Integration',
        'layer': 'application',
        'port': 8000,
        'container_name': 'open-webui-hub-mcposerver-1',
        'health_url': 'http://localhost:8000/docs',
        'description': 'Model Context Protocol сервер для интеграции внешних инструментов'
    },
    'watchtower': {
        'name': 'Watchtower',
        'category': 'DevOps',
        'layer': 'infrastructure',
        'port': None,
        'container_name': 'open-webui-hub-watchtower-1',
        'health_url': None,
        'description': 'Автоматическое обновление Docker контейнеров при появлении новых версий'
    }
}

# Architecture layers definition
ARCHITECTURE_LAYERS = {
    'presentation': {
        'name': 'Presentation Layer',
        'description': 'Уровень представления - интерфейс пользователя',
        'color': '#3B82F6',
        'services': ['nginx']
    },
    'application': {
        'name': 'Application Layer',
        'description': 'Уровень приложений - бизнес-логика',
        'color': '#10B981',
        'services': ['openwebui', 'hub', 'auth', 'mcposerver']
    },
    'service': {
        'name': 'Service Layer',
        'description': 'Уровень сервисов - специализированные микросервисы',
        'color': '#F59E0B',
        'services': ['ollama', 'litellm', 'docling', 'tika', 'edgetts', 'searxng']
    },
    'data': {
        'name': 'Data Layer',
        'description': 'Уровень данных - хранение и кэширование',
        'color': '#EF4444',
        'services': ['db', 'redis']
    },
    'infrastructure': {
        'name': 'Infrastructure Layer',
        'description': 'Уровень инфраструктуры - операции и развертывание',
        'color': '#8B5CF6',
        'services': ['watchtower']
    }
}

def get_cached_data(cache_key: str, fetch_function, *args, **kwargs):
    """Universal caching function"""
    with _cache_lock:
        now = time.time()
        
        # Check if we have fresh data in cache
        if (cache_key in _cache and
            cache_key in _cache_timestamps and
            now - _cache_timestamps[cache_key] < CONFIG['cache_ttl']):
            return _cache[cache_key]
        
        # Fetch new data
        try:
            data = fetch_function(*args, **kwargs)
            _cache[cache_key] = data
            _cache_timestamps[cache_key] = now
            return data
        except Exception as e:
            # Return stale data if available
            if cache_key in _cache:
                logger.warning(f"⚠️ Using stale data for {cache_key}: {str(e)}")
                return _cache[cache_key]
            raise e

def _fetch_service_status(service_id: str, config: Dict[str, Any]):
    """Fetch status for a single service"""
    try:
        # Container status
        container_status = 'unknown'
        docker_health = 'unknown'
        if docker_client:
            try:
                container = docker_client.containers.get(config['container_name'])
                container_status = container.status

                # Get Docker health check status if available
                container.reload()  # Refresh container info
                health_status = container.attrs.get('State', {}).get('Health', {}).get('Status')
                if health_status:
                    docker_health = health_status.lower()

            except docker.errors.NotFound:
                container_status = 'not_found'
            except Exception as e:
                logger.debug(f"Docker status check failed for {service_id}: {e}")
                container_status = 'error'
        
        # Health check
        health_status = 'unknown'
        if config.get('health_url'):
            try:
                # Use specified HTTP method or default to HEAD
                method = config.get('health_method', 'HEAD')
                if method == 'GET':
                    response = requests.get(config['health_url'], timeout=CONFIG['health_check_timeout'])
                else:
                    response = requests.head(config['health_url'], timeout=CONFIG['health_check_timeout'])

                # Consider 200-299 as healthy
                health_status = 'healthy' if 200 <= response.status_code < 300 else 'unhealthy'
            except Exception as e:
                logger.debug(f"Health check failed for {service_id}: {e}")
                health_status = 'unreachable'
        
        # Determine overall status based on multiple factors
        overall_status = 'Needs Attention'
        if container_status == 'running':
            if health_status == 'healthy' or docker_health == 'healthy':
                overall_status = 'Production Ready'
            elif health_status == 'unknown' and docker_health == 'unknown':
                # If no health checks available but container is running
                overall_status = 'Running'
        elif container_status == 'not_found':
            overall_status = 'Not Deployed'
        elif container_status == 'error':
            overall_status = 'Error'

        return {
            'id': service_id,
            'name': config['name'],
            'category': config['category'],
            'layer': config['layer'],
            'port': config.get('port'),
            'container_status': container_status,
            'health_status': health_status,
            'docker_health': docker_health,
            'description': config['description'],
            'status': overall_status
        }
    except Exception as e:
        logger.error(f"❌ Error fetching status for {service_id}: {e}")
        return {
            'id': service_id,
            'name': config['name'],
            'category': config['category'],
            'layer': config['layer'],
            'port': config.get('port'),
            'container_status': 'error',
            'health_status': 'error',
            'docker_health': 'unknown',
            'description': config['description'],
            'status': 'Error',
            'error': str(e)
        }

def _fetch_all_services():
    """Fetch status for all services"""
    services = []
    for service_id, config in SERVICES_CONFIG.items():
        service_status = _fetch_service_status(service_id, config)
        services.append(service_status)
    return services

def _fetch_architecture_data():
    """Fetch complete architecture data with services and layers"""
    services = _fetch_all_services()

    # Add layer information
    layers = []
    for layer_id, layer_config in ARCHITECTURE_LAYERS.items():
        layers.append({
            'id': layer_id,
            'name': layer_config['name'],
            'description': layer_config['description'],
            'color': layer_config['color'],
            'services': layer_config['services']
        })

    return {
        'services': services,
        'layers': layers,
        'timestamp': time.time(),
        'total_services': len(services),
        'healthy_services': len([s for s in services if s.get('health_status') == 'healthy']),
        'running_containers': len([s for s in services if s.get('container_status') == 'running'])
    }

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        uptime = time.time() - _app_start_time
        return jsonify({
            'status': 'healthy',
            'service': 'hub-api',
            'version': '2.0.0',
            'uptime_seconds': uptime,
            'timestamp': time.time(),
            'docker_available': docker_client is not None,
            'total_services': len(SERVICES_CONFIG)
        })
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    """Get all services status"""
    try:
        services = get_cached_data('all_services', _fetch_all_services)
        return jsonify({
            'services': services,
            'timestamp': time.time(),
            'total': len(services)
        })
    except Exception as e:
        logger.error(f"❌ Error fetching services: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/<service_id>', methods=['GET'])
def get_service(service_id):
    """Get specific service status"""
    try:
        if service_id not in SERVICES_CONFIG:
            return jsonify({'error': 'Service not found'}), 404

        config = SERVICES_CONFIG[service_id]
        service_status = get_cached_data(f'service_{service_id}', _fetch_service_status, service_id, config)
        return jsonify(service_status)
    except Exception as e:
        logger.error(f"❌ Error fetching service {service_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/architecture', methods=['GET'])
def get_architecture():
    """Get complete architecture data"""
    try:
        architecture = get_cached_data('architecture', _fetch_architecture_data)
        return jsonify(architecture)
    except Exception as e:
        logger.error(f"❌ Error fetching architecture: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/layers', methods=['GET'])
def get_layers():
    """Get architecture layers"""
    try:
        layers = []
        for layer_id, layer_config in ARCHITECTURE_LAYERS.items():
            layers.append({
                'id': layer_id,
                'name': layer_config['name'],
                'description': layer_config['description'],
                'color': layer_config['color'],
                'services': layer_config['services']
            })
        return jsonify({
            'layers': layers,
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"❌ Error fetching layers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/discovery', methods=['GET'])
def service_discovery():
    """Service discovery endpoint"""
    try:
        if not CONFIG['enable_service_discovery']:
            return jsonify({'error': 'Service discovery disabled'}), 403

        discovered_services = {}

        if docker_client:
            try:
                containers = docker_client.containers.list(all=True)
                for container in containers:
                    if container.name.startswith('open-webui-hub-'):
                        service_name = container.name.replace('open-webui-hub-', '').replace('-1', '')
                        discovered_services[service_name] = {
                            'container_name': container.name,
                            'status': container.status,
                            'image': container.image.tags[0] if container.image.tags else 'unknown',
                            'ports': container.ports,
                            'labels': container.labels
                        }
            except Exception as e:
                logger.warning(f"⚠️ Docker discovery failed: {e}")

        return jsonify({
            'discovered_services': discovered_services,
            'configured_services': list(SERVICES_CONFIG.keys()),
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"❌ Service discovery failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics"""
    try:
        services = get_cached_data('all_services', _fetch_all_services)

        metrics = {
            'total_services': len(services),
            'healthy_services': len([s for s in services if s.get('status') == 'Production Ready']),
            'running_containers': len([s for s in services if s.get('container_status') == 'running']),
            'error_services': len([s for s in services if s.get('status') == 'Error']),
            'layers': len(ARCHITECTURE_LAYERS),
            'uptime': time.time() - _app_start_time,
            'timestamp': time.time()
        }

        # Add layer breakdown
        layer_metrics = {}
        for layer_id, layer_config in ARCHITECTURE_LAYERS.items():
            layer_services = [s for s in services if s.get('layer') == layer_id]
            layer_metrics[layer_id] = {
                'total': len(layer_services),
                'healthy': len([s for s in layer_services if s.get('status') == 'Production Ready']),
                'running': len([s for s in layer_services if s.get('container_status') == 'running'])
            }

        metrics['layer_metrics'] = layer_metrics
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"❌ Error fetching metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear service cache"""
    try:
        with _cache_lock:
            _cache.clear()
            _cache_timestamps.clear()

        logger.info("🧹 Cache cleared successfully")
        return jsonify({
            'message': 'Cache cleared successfully',
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"❌ Error clearing cache: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/info', methods=['GET'])
def cache_info():
    """Get cache information"""
    try:
        with _cache_lock:
            cache_keys = list(_cache.keys())
            cache_ages = {key: time.time() - _cache_timestamps.get(key, 0) for key in cache_keys}

        return jsonify({
            'cache_size': len(cache_keys),
            'cache_keys': cache_keys,
            'cache_ages': cache_ages,
            'cache_ttl': CONFIG['cache_ttl'],
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"❌ Error fetching cache info: {e}")
        return jsonify({'error': str(e)}), 500

# Static file serving for frontend
@app.route('/')
def serve_index():
    """Serve index.html"""
    frontend_dir = '/app/dist'
    index_path = os.path.join(frontend_dir, 'index.html')

    try:
        logger.info(f"📄 Serving index.html from: {index_path}")
        logger.info(f"📄 Index exists: {os.path.exists(index_path)}")

        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            from flask import Response
            logger.info(f"✅ Successfully serving index.html ({len(content)} chars)")
            return Response(content, content_type='text/html')
        else:
            logger.error(f"❌ Index.html not found at {index_path}")
            return jsonify({'error': 'Frontend not built'}), 404
    except Exception as e:
        logger.error(f"❌ Error serving index: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Frontend error: {str(e)}'}), 404

@app.route('/<path:path>')
def serve_frontend(path):
    """Serve React frontend files"""
    # Skip API routes
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404

    # Frontend files are in /app/dist
    frontend_dir = '/app/dist'

    try:
        logger.info(f"🔍 Serving frontend: path='{path}', frontend_dir='{frontend_dir}'")

        if path and os.path.exists(os.path.join(frontend_dir, path)):
            logger.info(f"📁 Serving specific file: {path}")
            # Serve specific file
            with open(os.path.join(frontend_dir, path), 'rb') as f:
                content = f.read()

            # Determine content type
            if path.endswith('.html'):
                content_type = 'text/html'
            elif path.endswith('.js'):
                content_type = 'application/javascript'
            elif path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.json'):
                content_type = 'application/json'
            else:
                content_type = 'application/octet-stream'

            from flask import Response
            return Response(content, content_type=content_type)
        else:
            # Always serve index.html for SPA routing
            index_path = os.path.join(frontend_dir, 'index.html')
            logger.info(f"📄 Serving index.html from: {index_path}")
            logger.info(f"📄 Index exists: {os.path.exists(index_path)}")

            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                from flask import Response
                logger.info(f"✅ Successfully serving index.html ({len(content)} chars)")
                return Response(content, content_type='text/html')
            else:
                logger.error(f"❌ Index.html not found at {index_path}")
                return jsonify({'error': 'Frontend not built'}), 404
    except Exception as e:
        logger.error(f"❌ Error serving frontend: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Frontend error: {str(e)}'}), 404

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 Not Found: {request.url}")
    return jsonify({
        'error': 'Endpoint not found',
        'message': f"The requested URL {request.url} was not found on the server",
        'timestamp': time.time()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 Internal Server Error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'timestamp': time.time()
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        'error': 'Unexpected error',
        'message': 'An unexpected error occurred',
        'timestamp': time.time()
    }), 500

# Request logging middleware
@app.before_request
def log_request_info():
    """Log request information"""
    if request.path.startswith('/api/'):
        logger.info(f"📥 {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """Log response information"""
    if request.path.startswith('/api/'):
        logger.info(f"📤 {request.method} {request.path} -> {response.status_code}")
    return response

# Cleanup function for graceful shutdown
def cleanup_resources():
    """Cleanup resources on shutdown"""
    logger.info("🧹 Cleaning up resources...")
    with _cache_lock:
        _cache.clear()
        _cache_timestamps.clear()
    logger.info("✅ Cleanup completed")

# Signal handlers for graceful shutdown
import signal
import atexit

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
    cleanup_resources()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup_resources)

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🚀 Starting Hub API Service")
    logger.info(f"🌐 Host: {CONFIG['api_host']}:{CONFIG['api_port']}")
    logger.info(f"🐳 Docker client: {'Available' if docker_client else 'Not available'}")
    logger.info(f"🔍 Service discovery: {'Enabled' if CONFIG['enable_service_discovery'] else 'Disabled'}")
    logger.info(f"🗂️ Cache TTL: {CONFIG['cache_ttl']} seconds")
    logger.info(f"🔒 Debug mode: {'Enabled' if CONFIG['debug_mode'] else 'Disabled'}")
    logger.info("=" * 50)

    try:
        app.run(
            host=CONFIG['api_host'],
            port=CONFIG['api_port'],
            debug=CONFIG['debug_mode']
        )
    except Exception as e:
        logger.error(f"❌ Failed to start Hub API: {e}")
        sys.exit(1)
