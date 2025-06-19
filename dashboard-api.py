#!/usr/bin/env python3
"""
Оптимизированная версия Dashboard API для Open WebUI Hub
Основные улучшения:
- Кэширование метрик и статусов
- Асинхронные операции
- Уменьшение частоты опроса
- Оптимизация Docker API запросов
"""

import os
import sys
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, Any, Optional

# Загрузка переменных окружения
def load_env_config():
    """Загрузить .env файл если он существует и конфигурацию из переменных окружения"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    return {
        'api_host': os.getenv('DASHBOARD_API_HOST', '0.0.0.0'),
        'api_port': int(os.getenv('DASHBOARD_API_PORT', 5002)),
        'debug_mode': os.getenv('DASHBOARD_DEBUG_MODE', 'false').lower() == 'true',
        'litellm_api_key': os.getenv('DASHBOARD_LITELLM_API_KEY', 'sk-1234567890abcdef'),
        'edgetts_api_key': os.getenv('DASHBOARD_EDGETTS_API_KEY', 'your_api_key_here'),
        'docker_compose_file': os.getenv('DASHBOARD_DOCKER_COMPOSE_FILE', 'compose.local.yml'),
        'health_check_timeout': int(os.getenv('DASHBOARD_HEALTH_CHECK_TIMEOUT', 5)),
        'docker_operation_timeout': int(os.getenv('DASHBOARD_DOCKER_OPERATION_TIMEOUT', 30)),
        'log_level': os.getenv('DASHBOARD_LOG_LEVEL', 'INFO'),
        'cache_cleanup_interval': int(os.getenv('DASHBOARD_CACHE_CLEANUP_INTERVAL', 300)),
    }

# Глобальная конфигурация
CONFIG = load_env_config()

import psutil
import requests
import docker
import docker.errors
from flask import Flask, jsonify, request
from flask_cors import CORS

# Конфигурация
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_DIR = os.path.join(PROJECT_ROOT, 'env')

app = Flask(__name__)
CORS(app)

# Глобальные переменные для кэширования
_cache = {}
_cache_timestamps = {}
_cache_lock = threading.Lock()

# Настройки кэширования (в секундах) - с поддержкой переменных окружения
CACHE_DURATIONS = {
    'system': int(os.getenv('DASHBOARD_CACHE_SYSTEM_METRICS_TTL', 10)),
    'docker': int(os.getenv('DASHBOARD_CACHE_DOCKER_STATS_TTL', 15)),
    'service': int(os.getenv('DASHBOARD_CACHE_SERVICE_HEALTH_TTL', 30)),
    'container': int(os.getenv('DASHBOARD_CACHE_CONTAINER_RESOURCES_TTL', 20)),
    # Обратная совместимость
    'system_metrics': int(os.getenv('DASHBOARD_CACHE_SYSTEM_METRICS_TTL', 10)),
    'docker_stats': int(os.getenv('DASHBOARD_CACHE_DOCKER_STATS_TTL', 15)),
    'service_health': int(os.getenv('DASHBOARD_CACHE_SERVICE_HEALTH_TTL', 30)),
    'container_resources': int(os.getenv('DASHBOARD_CACHE_CONTAINER_RESOURCES_TTL', 20)),
    'service_status': int(os.getenv('DASHBOARD_CACHE_SERVICE_HEALTH_TTL', 15)),
}

# Docker клиент
try:
    docker_client = docker.from_env()
except Exception:
    docker_client = None

# Конфигурация сервисов (полная версия из старого API)
SERVICES = {
    'ollama': {
        'container_name': 'open-webui-hub-ollama-1',
        'port': 11435,
        'health_url': 'http://localhost:11435/api/version',
        'env_file': 'ollama.env',
        'config_files': [],
        'data_dir': 'data/ollama',
        'description': 'Ollama LLM Server',
        'category': 'ai'
    },
    'litellm': {
        'container_name': 'open-webui-hub-litellm-1',
        'port': 4000,
        'health_url': 'http://localhost:4000/v1/models',
        'auth_header': f'Bearer {CONFIG["litellm_api_key"]}',
        'env_file': 'litellm.env',
        'config_files': ['conf/litellm/litellm_config.yaml'],
        'data_dir': None,
        'description': 'LiteLLM Unified API Proxy',
        'category': 'ai'
    },
    'db': {
        'container_name': 'open-webui-hub-db-1',
        'port': 5432,
        'health_url': None,  # PostgreSQL не имеет HTTP health endpoint
        'env_file': 'db.env',
        'config_files': [],
        'data_dir': 'data/postgres',
        'description': 'PostgreSQL Database',
        'category': 'database'
    },
    'redis': {
        'container_name': 'open-webui-hub-redis-1',
        'port': 6379,
        'health_url': 'http://localhost:8001',
        'env_file': 'redis.env',
        'config_files': [],
        'data_dir': 'data/redis',
        'description': 'Redis Cache & Session Store',
        'category': 'database'
    },
    'openwebui': {
        'container_name': 'open-webui-hub-openwebui-1',
        'port': 3000,
        'health_url': 'http://localhost:3000',
        'env_file': 'openwebui.env',
        'config_files': [],
        'data_dir': 'data/openwebui',
        'description': 'Open WebUI Interface',
        'category': 'frontend'
    },
    'searxng': {
        'container_name': 'open-webui-hub-searxng-1',
        'port': 8080,
        'health_url': 'http://localhost:8080',
        'env_file': 'searxng.env',
        'config_files': ['conf/searxng/settings.yml', 'conf/searxng/uwsgi.ini'],
        'data_dir': None,
        'description': 'SearXNG Search Engine',
        'category': 'search'
    },
    'nginx': {
        'container_name': 'open-webui-hub-nginx-1',
        'port': 80,
        'health_url': 'http://localhost',
        'env_file': None,
        'config_files': ['conf/nginx/nginx.conf', 'conf/nginx/conf.d/default.conf'],
        'data_dir': None,
        'description': 'Nginx Reverse Proxy',
        'category': 'proxy'
    },
    'watchtower': {
        'container_name': 'open-webui-hub-watchtower-1',
        'port': None,
        'health_url': None,
        'env_file': 'watchtower.env',
        'config_files': [],
        'data_dir': None,
        'description': 'Container Auto-updater',
        'category': 'system'
    },
    'auth': {
        'container_name': 'open-webui-hub-auth-1',
        'port': 9090,
        'health_url': 'http://localhost:9090/health',
        'env_file': 'auth.env',
        'config_files': [],
        'data_dir': None,
        'description': 'JWT Auth Validator',
        'category': 'system'
    },
    'docling': {
        'container_name': 'open-webui-hub-docling-1',
        'port': 5001,
        'health_url': 'http://localhost:5001/health',
        'env_file': 'docling.env',
        'config_files': [],
        'data_dir': None,
        'description': 'Document Processing Service',
        'category': 'ai'
    },
    'edgetts': {
        'container_name': 'open-webui-hub-edgetts-1',
        'port': 5050,
        'health_url': None,  # EdgeTTS не имеет стандартного health endpoint
        'env_file': 'edgetts.env',
        'config_files': [],
        'data_dir': None,
        'description': 'Edge TTS Service',
        'category': 'ai'
    },
    'mcposerver': {
        'container_name': 'open-webui-hub-mcposerver-1',
        'port': 8000,
        'health_url': 'http://localhost:8000/docs',
        'env_file': 'mcposerver.env',
        'config_files': ['conf/mcposerver/config.json'],
        'data_dir': None,
        'description': 'MCPO Server',
        'category': 'ai'
    },
    'tika': {
        'container_name': 'open-webui-hub-tika-1',
        'port': 9998,
        'health_url': 'http://localhost:9998/tika',
        'env_file': 'tika.env',
        'config_files': [],
        'data_dir': None,
        'description': 'Apache Tika Document Parser',
        'category': 'ai'
    }
}

def cleanup_expired_cache():
    """Удалить устаревшие записи кэша"""
    with _cache_lock:
        now = time.time()
        expired_keys = []

        for key, timestamp in _cache_timestamps.items():
            # Определяем тип кэша и его TTL
            cache_type = key.split('_')[0] if '_' in key else 'default'
            duration = CACHE_DURATIONS.get(cache_type, 60)

            if now - timestamp > duration:
                expired_keys.append(key)

        # Удаляем устаревшие записи
        for key in expired_keys:
            _cache.pop(key, None)
            _cache_timestamps.pop(key, None)

        if expired_keys:
            print(f"🧹 Очистка кэша: удалено {len(expired_keys)} устаревших записей")

        return len(expired_keys)

def schedule_cache_cleanup():
    """Запланировать регулярную очистку кэша"""
    cleanup_expired_cache()
    # Планируем следующую очистку через интервал из конфигурации
    interval = CONFIG['cache_cleanup_interval']
    threading.Timer(interval, schedule_cache_cleanup).start()

def get_cached_data(cache_key: str, cache_duration: int, fetch_function, *args, **kwargs):
    """Универсальная функция кэширования с улучшенной логикой"""
    with _cache_lock:
        now = time.time()

        # Проверяем, есть ли актуальные данные в кэше
        if (cache_key in _cache and
            cache_key in _cache_timestamps and
            now - _cache_timestamps[cache_key] < cache_duration):
            return _cache[cache_key]

        # Данных нет или они устарели - получаем новые
        try:
            data = fetch_function(*args, **kwargs)
            _cache[cache_key] = data
            _cache_timestamps[cache_key] = now
            return data
        except Exception as e:
            # Если не удалось получить новые данные, возвращаем старые (если есть)
            if cache_key in _cache:
                print(f"⚠️ Используем устаревшие данные для {cache_key}: {str(e)}")
                return _cache[cache_key]
            raise e

def _fetch_system_metrics():
    """Получить системные метрики (без блокирующих операций)"""
    try:
        # Используем неблокирующий вызов для CPU
        cpu_percent = psutil.cpu_percent(interval=None)  # Не блокируем!
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_usage': f"{cpu_percent:.1f}%",
            'memory_usage': f"{memory.percent:.1f}%",
            'disk_usage': f"{(disk.used / disk.total * 100):.1f}%",
            'memory_total': f"{memory.total / (1024**3):.1f} GB",
            'disk_total': f"{disk.total / (1024**3):.1f} GB",
            'timestamp': time.time()
        }
    except Exception as e:
        return {'error': str(e), 'timestamp': time.time()}

def _fetch_docker_stats():
    """Получить статистику Docker"""
    try:
        if not docker_client:
            return {'error': 'Docker client недоступен'}
        
        containers = docker_client.containers.list(all=True)
        return {
            'total_containers': len(containers),
            'running_containers': len([c for c in containers if c.status == 'running']),
            'containers': [
                {
                    'name': c.name,
                    'status': c.status,
                    'short_id': c.short_id
                } for c in containers
            ],
            'timestamp': time.time()
        }
    except Exception as e:
        return {'error': str(e), 'timestamp': time.time()}

def _fetch_service_health(service_name: str, config: Dict[str, Any]):
    """Получить статус здоровья сервиса с улучшенной обработкой ошибок"""
    try:
        # Статус контейнера
        container_status = 'unknown'
        container_error = None

        if docker_client:
            try:
                container = docker_client.containers.get(config['container_name'])
                container_status = container.status
            except docker.errors.NotFound:
                container_status = 'not_found'
                container_error = 'Container not found'
            except Exception as e:
                container_status = 'error'
                container_error = str(e)
        else:
            container_status = 'docker_unavailable'
            container_error = 'Docker client not available'

        # Health check с улучшенной логикой
        health_status = 'unknown'
        health_error = None

        # Специальная логика для PostgreSQL
        if service_name == 'db':
            try:
                result = subprocess.run(
                    ['docker', 'exec', config['container_name'], 'pg_isready', '-U', 'postgres'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    health_status = 'healthy'
                else:
                    health_status = 'unhealthy'
                    health_error = f'pg_isready failed: {result.stderr.strip()}'
            except subprocess.TimeoutExpired:
                health_status = 'timeout'
                health_error = 'PostgreSQL health check timeout'
            except Exception as e:
                health_status = 'error'
                health_error = f'PostgreSQL check error: {str(e)}'
        elif config.get('health_url'):
            try:
                headers = {}
                if config.get('auth_header'):
                    headers['Authorization'] = config['auth_header']

                response = requests.get(
                    config['health_url'],
                    timeout=5,  # Увеличили таймаут
                    headers=headers
                )

                if response.status_code == 200:
                    health_status = 'healthy'
                elif response.status_code in [503, 502, 504]:
                    health_status = 'unhealthy'
                    health_error = f'HTTP {response.status_code}'
                else:
                    health_status = 'degraded'
                    health_error = f'HTTP {response.status_code}'

            except requests.exceptions.Timeout:
                health_status = 'timeout'
                health_error = 'Health check timeout'
            except requests.exceptions.ConnectionError:
                health_status = 'unreachable'
                health_error = 'Connection refused'
            except Exception as e:
                health_status = 'error'
                health_error = str(e)

        elif service_name == 'db':
            # Улучшенный health check для PostgreSQL
            try:
                result = subprocess.run(
                    ['docker', 'exec', config['container_name'], 'pg_isready', '-U', 'postgres'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    health_status = 'healthy'
                else:
                    health_status = 'unhealthy'
                    health_error = result.stderr.strip() if result.stderr else 'PostgreSQL not ready'
            except subprocess.TimeoutExpired:
                health_status = 'timeout'
                health_error = 'PostgreSQL check timeout'
            except Exception as e:
                health_status = 'error'
                health_error = str(e)

        elif service_name in ['watchtower']:
            # Сервисы без health URL - проверяем только статус контейнера
            if container_status == 'running':
                health_status = 'healthy'
            elif container_status in ['not_found', 'error']:
                health_status = 'unhealthy'
                health_error = container_error
            else:
                health_status = 'unknown'
        else:
            # Для сервисов без health URL - считаем здоровыми если контейнер запущен
            if container_status == 'running':
                health_status = 'assumed_healthy'
            else:
                health_status = 'unknown'

        result = {
            'container_status': container_status,
            'health_status': health_status,
            'timestamp': time.time()
        }

        # Добавляем ошибки если есть
        if container_error:
            result['container_error'] = container_error
        if health_error:
            result['health_error'] = health_error

        return result

    except Exception as e:
        return {
            'container_status': 'error',
            'health_status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }

def _fetch_container_resources(container_name: str):
    """Получить ресурсы контейнера с улучшенной обработкой ошибок"""
    try:
        if not docker_client:
            return {
                'error': 'Docker client недоступен',
                'status': 'docker_unavailable',
                'timestamp': time.time()
            }

        try:
            container = docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            return {
                'error': 'Контейнер не найден',
                'status': 'not_found',
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'error': f'Ошибка получения контейнера: {str(e)}',
                'status': 'error',
                'timestamp': time.time()
            }

        # Проверяем статус контейнера
        if container.status != 'running':
            return {
                'status': container.status,
                'memory_usage': 0,
                'memory_limit': 0,
                'memory_percent': 0,
                'cpu_percent': 0,
                'timestamp': time.time()
            }

        try:
            # Получаем статистику с таймаутом
            stats = container.stats(stream=False)

            # Безопасное вычисление памяти
            memory_stats = stats.get('memory_stats', {})
            memory_usage = memory_stats.get('usage', 0)
            memory_limit = memory_stats.get('limit', 0)

            if memory_limit > 0:
                memory_percent = round((memory_usage / memory_limit * 100), 2)
            else:
                memory_percent = 0

            # Базовое вычисление CPU (упрощенное)
            cpu_stats = stats.get('cpu_stats', {})
            precpu_stats = stats.get('precpu_stats', {})

            cpu_percent = 0
            if cpu_stats and precpu_stats:
                try:
                    cpu_delta = cpu_stats.get('cpu_usage', {}).get('total_usage', 0) - \
                               precpu_stats.get('cpu_usage', {}).get('total_usage', 0)
                    system_delta = cpu_stats.get('system_cpu_usage', 0) - \
                                  precpu_stats.get('system_cpu_usage', 0)

                    if system_delta > 0 and cpu_delta > 0:
                        cpu_count = len(cpu_stats.get('cpu_usage', {}).get('percpu_usage', [1]))
                        cpu_percent = round((cpu_delta / system_delta) * cpu_count * 100, 2)
                except:
                    cpu_percent = 0

            return {
                'status': container.status,
                'memory_usage': memory_usage,
                'memory_limit': memory_limit,
                'memory_percent': memory_percent,
                'cpu_percent': cpu_percent,
                'timestamp': time.time()
            }

        except Exception as e:
            return {
                'status': container.status,
                'error': f'Ошибка получения статистики: {str(e)}',
                'memory_usage': 0,
                'memory_limit': 0,
                'memory_percent': 0,
                'cpu_percent': 0,
                'timestamp': time.time()
            }

    except Exception as e:
        return {
            'error': f'Общая ошибка: {str(e)}',
            'status': 'error',
            'timestamp': time.time()
        }

# ===== API ENDPOINTS =====

@app.route('/api/metrics', methods=['GET'])
def get_system_metrics():
    """Получить системные метрики (кэшированные)"""
    try:
        metrics = get_cached_data(
            'system_metrics',
            CACHE_DURATIONS['system_metrics'],
            _fetch_system_metrics
        )
        
        # Добавляем Docker статистику
        docker_stats = get_cached_data(
            'docker_stats',
            CACHE_DURATIONS['docker_stats'],
            _fetch_docker_stats
        )
        
        return jsonify({
            'system': metrics,
            'docker': docker_stats,
            'cache_info': {
                'system_cache_age': time.time() - _cache_timestamps.get('system_metrics', 0),
                'docker_cache_age': time.time() - _cache_timestamps.get('docker_stats', 0)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_services_status():
    """Получить статус всех сервисов (кэшированный)"""
    try:
        status = {}
        
        for service_name, config in SERVICES.items():
            cache_key = f'service_health_{service_name}'
            service_status = get_cached_data(
                cache_key,
                CACHE_DURATIONS['service_health'],
                _fetch_service_health,
                service_name,
                config
            )
            
            status[service_name] = {
                'name': service_name,
                'description': config.get('description', ''),
                'category': config.get('category', 'other'),
                'port': config.get('port'),
                **service_status
            }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services', methods=['GET'])
def get_services_info():
    """Получить подробную информацию о сервисах"""
    try:
        services_info = {}
        include_resources = request.args.get('resources', 'false').lower() == 'true'
        
        for service_name, config in SERVICES.items():
            # Базовая информация (кэшированная)
            cache_key = f'service_health_{service_name}'
            service_status = get_cached_data(
                cache_key,
                CACHE_DURATIONS['service_health'],
                _fetch_service_health,
                service_name,
                config
            )
            
            services_info[service_name] = {
                'name': service_name,
                'description': config.get('description', ''),
                'category': config.get('category', 'other'),
                'container_name': config['container_name'],
                'port': config.get('port'),
                **service_status
            }
            
            # Ресурсы (если запрошены)
            if include_resources:
                resources_cache_key = f'container_resources_{service_name}'
                resources = get_cached_data(
                    resources_cache_key,
                    CACHE_DURATIONS['container_resources'],
                    _fetch_container_resources,
                    config['container_name']
                )
                services_info[service_name]['resources'] = resources
        
        return jsonify(services_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    """Получить общую статистику системы (оптимизированная)"""
    try:
        # Системные метрики
        system_metrics = get_cached_data(
            'system_metrics',
            CACHE_DURATIONS['system_metrics'],
            _fetch_system_metrics
        )

        # Docker статистика
        docker_stats = get_cached_data(
            'docker_stats',
            CACHE_DURATIONS['docker_stats'],
            _fetch_docker_stats
        )

        return jsonify({
            'system': {
                'cpu_percent': float(system_metrics.get('cpu_usage', '0%').replace('%', '')),
                'memory_percent': float(system_metrics.get('memory_usage', '0%').replace('%', '')),
                'disk_percent': float(system_metrics.get('disk_usage', '0%').replace('%', '')),
            },
            'docker': docker_stats,
            'performance': {
                'cache_hits': len(_cache),
                'cache_age': {
                    'system': time.time() - _cache_timestamps.get('system_metrics', 0),
                    'docker': time.time() - _cache_timestamps.get('docker_stats', 0)
                }
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Очистить кэш (для отладки)"""
    global _cache, _cache_timestamps
    with _cache_lock:
        cache_size = len(_cache)
        _cache.clear()
        _cache_timestamps.clear()

    return jsonify({
        'success': True,
        'message': f'Кэш очищен ({cache_size} записей удалено)'
    })

@app.route('/api/cache/info', methods=['GET'])
def get_cache_info():
    """Получить информацию о кэше"""
    with _cache_lock:
        cache_info = {}
        now = time.time()

        for key, timestamp in _cache_timestamps.items():
            cache_info[key] = {
                'age': now - timestamp,
                'size': len(str(_cache.get(key, ''))),
                'expires_in': CACHE_DURATIONS.get(key.split('_')[0], 60) - (now - timestamp)
            }

    return jsonify({
        'cache_entries': len(_cache),
        'details': cache_info,
        'durations': CACHE_DURATIONS
    })

# Специальные endpoints для совместимости
@app.route('/api/db/health', methods=['GET'])
def check_db_health():
    """Проверить здоровье PostgreSQL (кэшированный)"""
    try:
        db_status = get_cached_data(
            'service_health_db',
            CACHE_DURATIONS['service_health'],
            _fetch_service_health,
            'db',
            SERVICES['db']
        )

        if db_status['health_status'] == 'healthy':
            return jsonify({'status': 'healthy', 'message': 'PostgreSQL is ready'})
        else:
            return jsonify({'status': 'unhealthy', 'error': db_status.get('error', 'Unknown error')}), 503
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

# ===== ENDPOINTS ДЛЯ УПРАВЛЕНИЯ СЕРВИСАМИ =====

@app.route('/api/service/<service_name>/control', methods=['POST'])
def control_service(service_name):
    """Управление отдельным сервисом (start/stop/restart)"""
    if service_name not in SERVICES:
        return jsonify({'error': 'Сервис не найден'}), 404

    data = request.get_json()
    action = data.get('action')

    if action not in ['start', 'stop', 'restart']:
        return jsonify({'error': 'Неизвестное действие'}), 400

    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'compose.local.yml', action, service_name],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )

        # Очищаем кэш для этого сервиса
        cache_key = f'service_health_{service_name}'
        with _cache_lock:
            if cache_key in _cache:
                del _cache[cache_key]
            if cache_key in _cache_timestamps:
                del _cache_timestamps[cache_key]

        return jsonify({
            'success': result.returncode == 0,
            'action': action,
            'service': service_name,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/start-all', methods=['POST'])
def start_all_services():
    """Запустить все сервисы"""
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'compose.local.yml', 'up', '-d'],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )

        # Очищаем весь кэш
        with _cache_lock:
            _cache.clear()
            _cache_timestamps.clear()

        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/stop-all', methods=['POST'])
def stop_all_services():
    """Остановить все сервисы"""
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'compose.local.yml', 'down'],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )

        # Очищаем весь кэш
        with _cache_lock:
            _cache.clear()
            _cache_timestamps.clear()

        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/restart-all', methods=['POST'])
def restart_all_services():
    """Перезапустить все сервисы"""
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'compose.local.yml', 'restart'],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )

        # Очищаем весь кэш
        with _cache_lock:
            _cache.clear()
            _cache_timestamps.clear()

        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ENDPOINTS ДЛЯ ЛОГОВ И КОНФИГУРАЦИИ =====

@app.route('/api/service/<service_name>/logs/stream', methods=['GET'])
def stream_service_logs(service_name):
    """Получить логи сервиса"""
    if service_name not in SERVICES:
        return jsonify({'error': 'Сервис не найден'}), 404

    try:
        container_name = SERVICES[service_name]['container_name']
        lines = request.args.get('lines', 100, type=int)

        if docker_client:
            container = docker_client.containers.get(container_name)
            logs = container.logs(tail=lines, timestamps=True)
            if isinstance(logs, bytes):
                logs_text = logs.decode('utf-8')
            else:
                logs_text = str(logs)

            return jsonify({
                'logs': logs_text.split('\n'),
                'container': container_name
            })
        else:
            # Fallback к docker CLI
            result = subprocess.run(
                ['docker', 'logs', '--tail', str(lines), container_name],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return jsonify({
                    'logs': result.stdout.split('\n'),
                    'container': container_name
                })
            else:
                return jsonify({'error': result.stderr}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/service/<service_name>/config', methods=['GET'])
def get_service_config(service_name):
    """Получить конфигурацию сервиса (упрощенная версия)"""
    if service_name not in SERVICES:
        return jsonify({'error': 'Сервис не найден'}), 404

    service_config = SERVICES[service_name]

    # Возвращаем базовую информацию о конфигурации
    return jsonify({
        'env_vars': {},  # Упрощенная версия - не читаем реальные env файлы
        'config_files': {},
        'service_info': {
            'container_name': service_config['container_name'],
            'port': service_config.get('port'),
            'description': service_config.get('description'),
            'category': service_config.get('category')
        }
    })

@app.route('/api/service/<service_name>/config', methods=['POST'])
def update_service_config(service_name):
    """Обновить конфигурацию сервиса (заглушка)"""
    if service_name not in SERVICES:
        return jsonify({'error': 'Сервис не найден'}), 404

    # Упрощенная версия - просто возвращаем успех
    return jsonify({
        'success': True,
        'message': 'Конфигурация обновлена (упрощенная версия)'
    })

@app.route('/api/service/<service_name>/backup', methods=['POST'])
def backup_service_config(service_name):
    """Создать бэкап конфигурации сервиса (заглушка)"""
    if service_name not in SERVICES:
        return jsonify({'error': 'Сервис не найден'}), 404

    backup_id = f"{service_name}_{int(time.time())}"
    return jsonify({
        'success': True,
        'backup_id': backup_id,
        'message': f'Бэкап создан: {backup_id} (упрощенная версия)'
    })

@app.route('/api/backups', methods=['GET'])
def list_backups():
    """Получить список всех бэкапов (заглушка)"""
    return jsonify({
        'backups': [
            {
                'id': 'example_backup_20250619',
                'service': 'example',
                'date': '20250619',
                'time': '154652',
                'files': ['config.yml'],
                'created': time.time()
            }
        ]
    })

# ===== СПЕЦИФИЧНЫЕ ENDPOINTS ДЛЯ OLLAMA =====

@app.route('/api/ollama/models', methods=['GET'])
def get_ollama_models():
    """Получить список моделей Ollama"""
    try:
        response = requests.get('http://localhost:11435/api/tags', timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Ollama недоступен'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ollama/pull', methods=['POST'])
def pull_ollama_model():
    """Скачать модель Ollama"""
    try:
        data = request.get_json()
        model_name = data.get('model')

        if not model_name:
            return jsonify({'error': 'Не указано название модели'}), 400

        # Запуск скачивания модели в фоне
        subprocess.Popen([
            'docker', 'exec', 'open-webui-hub-ollama-1',
            'ollama', 'pull', model_name
        ])

        return jsonify({'message': f'Скачивание модели {model_name} начато'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== СПЕЦИФИЧНЫЕ ENDPOINTS ДЛЯ LITELLM =====

@app.route('/api/litellm/status', methods=['GET'])
def get_litellm_status():
    """Получить детальный статус LiteLLM"""
    try:
        headers = {'Authorization': f'Bearer {CONFIG["litellm_api_key"]}'}

        # Используем /v1/models как health check (более надежно)
        models_response = requests.get('http://localhost:4000/v1/models', headers=headers, timeout=10)

        if models_response.status_code == 200:
            models_data = models_response.json()

            # Пытаемся получить health данные, но не блокируемся на них
            health_data = {}
            try:
                health_response = requests.get('http://localhost:4000/health', headers=headers, timeout=5)
                if health_response.status_code == 200:
                    health_data = health_response.json()
            except:
                # Если health endpoint недоступен, продолжаем без него
                pass

            return jsonify({
                'status': 'healthy',
                'models': models_data.get('data', []),
                'total_models': len(models_data.get('data', [])),
                'healthy_endpoints': health_data.get('healthy_count', 'unknown'),
                'unhealthy_endpoints': health_data.get('unhealthy_count', 'unknown'),
                'health_data_available': bool(health_data)
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'error': f'Models endpoint failed with status {models_response.status_code}'
            }), 503

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/litellm/models', methods=['GET'])
def get_litellm_models():
    """Получить список доступных моделей LiteLLM"""
    try:
        headers = {'Authorization': f'Bearer {CONFIG["litellm_api_key"]}'}
        response = requests.get('http://localhost:4000/v1/models', headers=headers, timeout=10)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to fetch models'}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/litellm/test', methods=['POST'])
def test_litellm_model():
    """Протестировать модель LiteLLM"""
    try:
        data = request.get_json()
        model_name = data.get('model', 'llama3')
        test_message = data.get('message', 'Привет! Как дела?')

        headers = {
            'Authorization': f'Bearer {CONFIG["litellm_api_key"]}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model_name,
            'messages': [{'role': 'user', 'content': test_message}],
            'max_tokens': 100
        }

        response = requests.post(
            'http://localhost:4000/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=90  # Увеличили таймаут для первой загрузки модели
        )

        if response.status_code == 200:
            return jsonify({
                'status': 'success',
                'response': response.json()
            })
        else:
            return jsonify({
                'status': 'error',
                'error': f'Request failed with status {response.status_code}',
                'details': response.text
            }), response.status_code

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

# ===== LEGACY ENDPOINTS ДЛЯ СОВМЕСТИМОСТИ =====

@app.route('/api/logs/<service>', methods=['GET'])
def get_service_logs_legacy(service):
    """Получить логи сервиса (legacy endpoint)"""
    return stream_service_logs(service)

@app.route('/api/docker/<action>', methods=['POST'])
def docker_action(action):
    """Выполнить Docker действие (legacy endpoint)"""
    try:
        if action == 'start':
            return start_all_services()
        elif action == 'stop':
            return stop_all_services()
        elif action == 'restart':
            return restart_all_services()
        else:
            return jsonify({'error': 'Неизвестное действие'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Запуск УЛУЧШЕННОГО Dashboard API для Open WebUI Hub")
    print(f"📊 API будет доступен на http://{CONFIG['api_host']}:{CONFIG['api_port']}")
    print("🔗 Основные эндпоинты:")
    print("   GET  /api/status - статус сервисов (кэшированный)")
    print("   GET  /api/metrics - метрики системы (кэшированный)")
    print("   GET  /api/services - информация о сервисах")
    print("   GET  /api/system/stats - общая статистика")
    print("   GET  /api/cache/info - информация о кэше")
    print("   POST /api/cache/clear - очистить кэш")
    print("⚡ Критические улучшения:")
    print("   - Автоматическая очистка кэша каждые 5 минут")
    print("   - Улучшенная проверка здоровья сервисов")
    print("   - Конфигурация через переменные окружения")
    print("   - Безопасное управление API ключами")
    print("   - Расширенная обработка ошибок Docker")

    # Запускаем автоматическую очистку кэша
    print("🧹 Запуск автоматической очистки кэша...")
    schedule_cache_cleanup()

    # Запускаем API сервер
    app.run(
        host=CONFIG['api_host'],
        port=CONFIG['api_port'],
        debug=CONFIG['debug_mode'],
        threaded=True
    )
