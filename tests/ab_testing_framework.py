#!/usr/bin/env python3
"""
Комплексный A/B Testing Framework для Open WebUI Hub
Проводит тестирование производительности, функциональности и интеграции
"""

import asyncio
import aiohttp
import time
import json
import statistics
import psutil
import docker
import redis
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests/ab_testing_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """Конфигурация тестирования"""
    # Базовые URL сервисов
    hub_api_url: str = "http://localhost:5003"
    litellm_api_url: str = "http://localhost:4000"
    nginx_url: str = "http://localhost:80"
    redis_url: str = "redis://localhost:6379"
    
    # Целевые метрики производительности
    target_response_time_ms: int = 50
    target_cache_hit_rate: float = 0.90
    target_cpu_usage: float = 0.05  # 5%
    target_memory_usage_mb: int = 100
    
    # Параметры нагрузочного тестирования
    concurrent_requests: int = 10
    test_duration_seconds: int = 60
    warmup_requests: int = 5
    
    # Таймауты
    request_timeout: int = 10
    health_check_timeout: int = 5

@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    service_name: str
    endpoint: str
    response_times: List[float]
    success_rate: float
    error_count: int
    total_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    cpu_usage: float
    memory_usage_mb: float
    timestamp: datetime

@dataclass
class CacheMetrics:
    """Метрики кэширования Redis"""
    hit_rate: float
    miss_rate: float
    total_commands: int
    used_memory_mb: float
    connected_clients: int
    operations_per_second: float
    timestamp: datetime

@dataclass
class ServiceHealthMetrics:
    """Метрики здоровья сервиса"""
    service_name: str
    is_healthy: bool
    response_time_ms: float
    status_code: int
    error_message: Optional[str]
    container_status: str
    timestamp: datetime

class ABTestingFramework:
    """Основной класс для A/B тестирования"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.docker_client = None
        self.redis_client = None
        self.results: Dict[str, Any] = {}
        
        # Инициализация клиентов
        self._init_clients()
    
    def _init_clients(self):
        """Инициализация клиентов Docker и Redis"""
        try:
            self.docker_client = docker.from_env()
            logger.info("✅ Docker client инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Docker: {e}")
        
        try:
            self.redis_client = redis.from_url(self.config.redis_url)
            self.redis_client.ping()
            logger.info("✅ Redis client инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Redis: {e}")
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Запуск комплексного A/B тестирования"""
        logger.info("🚀 Начало комплексного A/B тестирования Open WebUI Hub")
        start_time = datetime.now()
        
        try:
            # 1. Предварительная проверка здоровья системы
            logger.info("📋 Этап 1: Проверка здоровья системы")
            health_results = await self._check_system_health()
            
            # 2. Тестирование производительности микросервисов
            logger.info("⚡ Этап 2: Тестирование производительности микросервисов")
            performance_results = await self._test_microservices_performance()
            
            # 3. Тестирование кэширования Redis
            logger.info("🔄 Этап 3: Тестирование эффективности кэширования")
            cache_results = await self._test_redis_caching()
            
            # 4. Интеграционное тестирование
            logger.info("🔗 Этап 4: Интеграционное тестирование")
            integration_results = await self._test_service_integration()
            
            # 5. Тестирование LiteLLM
            logger.info("🤖 Этап 5: Тестирование LiteLLM интеграции")
            llm_results = await self._test_litellm_performance()
            
            # Сохранение результатов
            self.results['health_check'] = health_results
            self.results['performance_metrics'] = performance_results
            self.results['cache_metrics'] = cache_results
            self.results['integration_results'] = integration_results
            self.results['llm_performance'] = llm_results
            self.results['test_duration'] = (datetime.now() - start_time).total_seconds()
            self.results['timestamp'] = start_time.isoformat()
            
            logger.info("✅ Комплексное тестирование завершено")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка тестирования: {e}")
            raise
    
    async def _check_system_health(self) -> Dict[str, ServiceHealthMetrics]:
        """Проверка здоровья всех сервисов"""
        services = {
            'hub': f"{self.config.hub_api_url}/api/health",
            'litellm': f"{self.config.litellm_api_url}/health",
            'nginx': f"{self.config.nginx_url}",
            'redis': None  # Специальная проверка для Redis
        }
        
        health_results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.health_check_timeout)) as session:
            for service_name, health_url in services.items():
                if service_name == 'redis':
                    health_results[service_name] = await self._check_redis_health()
                else:
                    health_results[service_name] = await self._check_http_health(session, service_name, health_url)
        
        return health_results
    
    async def _check_http_health(self, session: aiohttp.ClientSession, service_name: str, health_url: str) -> ServiceHealthMetrics:
        """Проверка HTTP здоровья сервиса"""
        start_time = time.time()
        
        try:
            async with session.get(health_url) as response:
                response_time = (time.time() - start_time) * 1000
                
                # Получение статуса контейнера
                container_status = self._get_container_status(service_name)
                
                return ServiceHealthMetrics(
                    service_name=service_name,
                    is_healthy=response.status == 200,
                    response_time_ms=response_time,
                    status_code=response.status,
                    error_message=None,
                    container_status=container_status,
                    timestamp=datetime.now()
                )
        except Exception as e:
            return ServiceHealthMetrics(
                service_name=service_name,
                is_healthy=False,
                response_time_ms=-1,
                status_code=-1,
                error_message=str(e),
                container_status=self._get_container_status(service_name),
                timestamp=datetime.now()
            )
    
    async def _check_redis_health(self) -> ServiceHealthMetrics:
        """Специальная проверка здоровья Redis"""
        start_time = time.time()
        
        try:
            if self.redis_client:
                self.redis_client.ping()
                response_time = (time.time() - start_time) * 1000
                
                return ServiceHealthMetrics(
                    service_name='redis',
                    is_healthy=True,
                    response_time_ms=response_time,
                    status_code=200,
                    error_message=None,
                    container_status=self._get_container_status('redis'),
                    timestamp=datetime.now()
                )
        except Exception as e:
            pass

        return ServiceHealthMetrics(
            service_name='redis',
            is_healthy=False,
            response_time_ms=-1,
            status_code=-1,
            error_message="Redis connection failed",
            container_status=self._get_container_status('redis'),
            timestamp=datetime.now()
        )
    
    def _get_container_status(self, service_name: str) -> str:
        """Получение статуса Docker контейнера"""
        if not self.docker_client:
            return "unknown"
        
        try:
            # Поиск контейнера по имени
            container_name = f"open-webui-hub-{service_name}-1"
            container = self.docker_client.containers.get(container_name)
            return container.status
        except Exception:
            return "not_found"
    
    def save_results_to_file(self, filename: Optional[str] = None):
        """Сохранение результатов в файл"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tests/ab_testing_results_{timestamp}.json"
        
        # Конвертация dataclass объектов в словари
        serializable_results = self._make_serializable(self.results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 Результаты сохранены в {filename}")
    
    def _make_serializable(self, obj):
        """Конвертация объектов в JSON-сериализуемый формат"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return asdict(obj) if hasattr(obj, '__dataclass_fields__') else obj.__dict__
        else:
            return obj

    async def _test_microservices_performance(self) -> List[PerformanceMetrics]:
        """Тестирование производительности микросервисов"""
        endpoints = [
            ('hub', f"{self.config.hub_api_url}/api/health"),
            ('hub', f"{self.config.hub_api_url}/api/services"),
            ('hub', f"{self.config.hub_api_url}/api/metrics"),
            ('hub', f"{self.config.hub_api_url}/api/architecture"),
            ('litellm', f"{self.config.litellm_api_url}/health"),
        ]

        performance_results = []

        for service_name, endpoint_url in endpoints:
            logger.info(f"🔍 Тестирование производительности: {service_name} - {endpoint_url}")

            # Warmup запросы
            await self._warmup_endpoint(endpoint_url)

            # Основное тестирование
            metrics = await self._load_test_endpoint(service_name, endpoint_url)
            performance_results.append(metrics)

            # Проверка соответствия целевым метрикам
            self._validate_performance_targets(metrics)

        return performance_results

    async def _warmup_endpoint(self, endpoint_url: str):
        """Прогрев эндпоинта перед тестированием"""
        async with aiohttp.ClientSession() as session:
            for _ in range(self.config.warmup_requests):
                try:
                    async with session.get(endpoint_url, timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)):
                        pass
                except Exception:
                    pass

    async def _load_test_endpoint(self, service_name: str, endpoint_url: str) -> PerformanceMetrics:
        """Нагрузочное тестирование эндпоинта"""
        response_times = []
        error_count = 0
        total_requests = 0

        # Мониторинг ресурсов до тестирования
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = psutil.virtual_memory().used / 1024 / 1024

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < self.config.test_duration_seconds:
                tasks = []

                # Создание пула конкурентных запросов
                for _ in range(self.config.concurrent_requests):
                    task = self._single_request(session, endpoint_url)
                    tasks.append(task)

                # Выполнение запросов
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in results:
                    total_requests += 1
                    if isinstance(result, Exception):
                        error_count += 1
                    else:
                        response_times.append(result)

                # Небольшая пауза между пулами запросов
                await asyncio.sleep(0.1)

        # Мониторинг ресурсов после тестирования
        final_cpu = psutil.cpu_percent(interval=1)
        final_memory = psutil.virtual_memory().used / 1024 / 1024

        # Расчет метрик
        success_rate = (total_requests - error_count) / total_requests if total_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else 0
        p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else 0

        return PerformanceMetrics(
            service_name=service_name,
            endpoint=endpoint_url,
            response_times=response_times,
            success_rate=success_rate,
            error_count=error_count,
            total_requests=total_requests,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            cpu_usage=max(final_cpu - initial_cpu, 0),
            memory_usage_mb=max(final_memory - initial_memory, 0),
            timestamp=datetime.now()
        )

    async def _single_request(self, session: aiohttp.ClientSession, url: str) -> float:
        """Выполнение одного HTTP запроса с измерением времени"""
        start_time = time.time()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)) as response:
                await response.read()  # Полное чтение ответа
                return (time.time() - start_time) * 1000  # Время в миллисекундах
        except Exception as e:
            raise e

    def _validate_performance_targets(self, metrics: PerformanceMetrics):
        """Проверка соответствия целевым метрикам производительности"""
        issues = []

        if metrics.avg_response_time > self.config.target_response_time_ms:
            issues.append(f"Среднее время отклика {metrics.avg_response_time:.1f}ms превышает целевое {self.config.target_response_time_ms}ms")

        if metrics.success_rate < 0.95:  # 95% успешных запросов
            issues.append(f"Успешность запросов {metrics.success_rate:.1%} ниже 95%")

        if metrics.cpu_usage > self.config.target_cpu_usage:
            issues.append(f"Использование CPU {metrics.cpu_usage:.1%} превышает целевое {self.config.target_cpu_usage:.1%}")

        if metrics.memory_usage_mb > self.config.target_memory_usage_mb:
            issues.append(f"Использование памяти {metrics.memory_usage_mb:.1f}MB превышает целевое {self.config.target_memory_usage_mb}MB")

        if issues:
            logger.warning(f"⚠️ Проблемы производительности для {metrics.service_name}:")
            for issue in issues:
                logger.warning(f"   - {issue}")
        else:
            logger.info(f"✅ {metrics.service_name} соответствует целевым метрикам производительности")

    async def _test_redis_caching(self) -> CacheMetrics:
        """Тестирование эффективности кэширования Redis"""
        if not self.redis_client:
            logger.error("❌ Redis client недоступен для тестирования кэширования")
            return CacheMetrics(0, 0, 0, 0, 0, 0, datetime.now())

        try:
            # Получение начальной статистики Redis
            initial_info = await self.redis_client.info()
            initial_hits = initial_info.get('keyspace_hits', 0)
            initial_misses = initial_info.get('keyspace_misses', 0)
            initial_commands = initial_info.get('total_commands_processed', 0)

            # Тестирование кэширования через Hub API
            logger.info("🔄 Тестирование кэширования через Hub API...")

            # Множественные запросы к одним и тем же эндпоинтам для проверки кэширования
            test_endpoints = [
                f"{self.config.hub_api_url}/api/services",
                f"{self.config.hub_api_url}/api/metrics",
                f"{self.config.hub_api_url}/api/architecture"
            ]

            # Выполнение запросов для заполнения кэша
            async with aiohttp.ClientSession() as session:
                for endpoint in test_endpoints:
                    for _ in range(10):  # 10 запросов к каждому эндпоинту
                        try:
                            async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)):
                                pass
                        except Exception:
                            pass
                        await asyncio.sleep(0.1)

            # Ожидание обновления статистики
            await asyncio.sleep(2)

            # Получение финальной статистики
            final_info = await self.redis_client.info()
            final_hits = final_info.get('keyspace_hits', 0)
            final_misses = final_info.get('keyspace_misses', 0)
            final_commands = final_info.get('total_commands_processed', 0)

            # Расчет метрик кэширования
            hits_diff = final_hits - initial_hits
            misses_diff = final_misses - initial_misses
            total_cache_operations = hits_diff + misses_diff

            hit_rate = hits_diff / total_cache_operations if total_cache_operations > 0 else 0
            miss_rate = misses_diff / total_cache_operations if total_cache_operations > 0 else 0

            # Дополнительные метрики Redis
            used_memory_mb = final_info.get('used_memory', 0) / 1024 / 1024
            connected_clients = final_info.get('connected_clients', 0)
            commands_diff = final_commands - initial_commands
            ops_per_second = commands_diff / 60  # За последнюю минуту

            cache_metrics = CacheMetrics(
                hit_rate=hit_rate,
                miss_rate=miss_rate,
                total_commands=commands_diff,
                used_memory_mb=used_memory_mb,
                connected_clients=connected_clients,
                operations_per_second=ops_per_second,
                timestamp=datetime.now()
            )

            # Проверка целевых метрик кэширования
            if hit_rate < self.config.target_cache_hit_rate:
                logger.warning(f"⚠️ Hit rate кэша {hit_rate:.1%} ниже целевого {self.config.target_cache_hit_rate:.1%}")
            else:
                logger.info(f"✅ Hit rate кэша {hit_rate:.1%} соответствует целевому показателю")

            return cache_metrics

        except Exception as e:
            logger.error(f"❌ Ошибка тестирования Redis кэширования: {e}")
            return CacheMetrics(0, 0, 0, 0, 0, 0, datetime.now())

    async def _test_service_integration(self) -> Dict[str, Any]:
        """Интеграционное тестирование взаимодействия сервисов"""
        integration_results = {
            'nginx_routing': await self._test_nginx_routing(),
            'service_discovery': await self._test_service_discovery(),
            'health_checks': await self._test_health_check_chain(),
            'docker_integration': await self._test_docker_integration()
        }

        return integration_results

    async def _test_nginx_routing(self) -> Dict[str, Any]:
        """Тестирование маршрутизации через Nginx"""
        nginx_tests = {
            'hub_route': f"{self.config.nginx_url}/hub",
            'api_route': f"{self.config.nginx_url}/api/hub/health"
        }

        results = {}

        async with aiohttp.ClientSession() as session:
            for route_name, url in nginx_tests.items():
                try:
                    start_time = time.time()
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        response_time = (time.time() - start_time) * 1000

                        results[route_name] = {
                            'status_code': response.status,
                            'response_time_ms': response_time,
                            'success': response.status in [200, 301, 302],
                            'headers': dict(response.headers)
                        }
                except Exception as e:
                    results[route_name] = {
                        'status_code': -1,
                        'response_time_ms': -1,
                        'success': False,
                        'error': str(e)
                    }

        return results

    async def _test_service_discovery(self) -> Dict[str, Any]:
        """Тестирование service discovery"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.hub_api_url}/api/discovery",
                                     timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        discovery_data = await response.json()
                        return {
                            'success': True,
                            'discovered_services': len(discovery_data.get('services', [])),
                            'data': discovery_data
                        }
                    else:
                        return {
                            'success': False,
                            'status_code': response.status,
                            'error': 'Service discovery endpoint failed'
                        }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _test_health_check_chain(self) -> Dict[str, Any]:
        """Тестирование цепочки health check всех сервисов"""
        health_chain_results = {}

        # Проверка health check через Hub API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.hub_api_url}/api/services",
                                     timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        services_data = await response.json()

                        healthy_count = 0
                        total_count = len(services_data.get('services', []))

                        for service in services_data.get('services', []):
                            if service.get('status') == 'Production Ready':
                                healthy_count += 1

                        health_chain_results = {
                            'success': True,
                            'total_services': total_count,
                            'healthy_services': healthy_count,
                            'health_percentage': (healthy_count / total_count * 100) if total_count > 0 else 0,
                            'services_detail': services_data.get('services', [])
                        }
                    else:
                        health_chain_results = {
                            'success': False,
                            'error': f'Health check chain failed with status {response.status}'
                        }
        except Exception as e:
            health_chain_results = {
                'success': False,
                'error': str(e)
            }

        return health_chain_results

    async def _test_docker_integration(self) -> Dict[str, Any]:
        """Тестирование интеграции с Docker"""
        if not self.docker_client:
            return {
                'success': False,
                'error': 'Docker client недоступен'
            }

        try:
            # Получение списка контейнеров Open WebUI Hub
            containers = self.docker_client.containers.list(all=True)
            hub_containers = [c for c in containers if 'open-webui-hub' in c.name]

            container_stats = {}
            for container in hub_containers:
                try:
                    stats = container.stats(stream=False)

                    # Расчет использования CPU
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                               stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                                  stats['precpu_stats']['system_cpu_usage']
                    cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0

                    # Расчет использования памяти
                    memory_usage = stats['memory_stats']['usage']
                    memory_limit = stats['memory_stats']['limit']
                    memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0

                    container_stats[container.name] = {
                        'status': container.status,
                        'cpu_percent': cpu_percent,
                        'memory_usage_mb': memory_usage / 1024 / 1024,
                        'memory_percent': memory_percent,
                        'network_rx_bytes': stats.get('networks', {}).get('bridge', {}).get('rx_bytes', 0),
                        'network_tx_bytes': stats.get('networks', {}).get('bridge', {}).get('tx_bytes', 0)
                    }
                except Exception as e:
                    container_stats[container.name] = {
                        'status': container.status,
                        'error': str(e)
                    }

            return {
                'success': True,
                'total_containers': len(hub_containers),
                'running_containers': len([c for c in hub_containers if c.status == 'running']),
                'container_stats': container_stats
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _test_litellm_performance(self) -> Dict[str, Any]:
        """Тестирование производительности LiteLLM интеграции"""
        litellm_results = {
            'health_check': await self._test_litellm_health(),
            'model_listing': await self._test_litellm_models(),
            'provider_performance': await self._test_llm_providers(),
            'fallback_mechanism': await self._test_llm_fallback()
        }

        return litellm_results

    async def _test_litellm_health(self) -> Dict[str, Any]:
        """Проверка здоровья LiteLLM сервиса"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(f"{self.config.litellm_api_url}/health",
                                     timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        health_data = await response.json()
                        return {
                            'success': True,
                            'response_time_ms': response_time,
                            'status': health_data.get('status', 'unknown'),
                            'data': health_data
                        }
                    else:
                        return {
                            'success': False,
                            'status_code': response.status,
                            'response_time_ms': response_time
                        }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _test_litellm_models(self) -> Dict[str, Any]:
        """Тестирование получения списка моделей LiteLLM"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': 'Bearer sk-1234567890abcdef'}

                start_time = time.time()
                async with session.get(f"{self.config.litellm_api_url}/v1/models",
                                     headers=headers,
                                     timeout=aiohttp.ClientTimeout(total=15)) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        models_data = await response.json()
                        models = models_data.get('data', [])

                        return {
                            'success': True,
                            'response_time_ms': response_time,
                            'total_models': len(models),
                            'models': [model.get('id', 'unknown') for model in models],
                            'providers': list(set([model.get('owned_by', 'unknown') for model in models]))
                        }
                    else:
                        return {
                            'success': False,
                            'status_code': response.status,
                            'response_time_ms': response_time
                        }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _test_llm_providers(self) -> Dict[str, Any]:
        """Тестирование производительности различных LLM провайдеров"""
        providers_to_test = [
            {'name': 'ollama', 'model': 'llama3'},
            {'name': 'ollama', 'model': 'codellama'}
        ]

        provider_results = {}

        for provider in providers_to_test:
            provider_key = f"{provider['name']}_{provider['model']}"

            try:
                result = await self._test_single_llm_provider(provider['model'])
                provider_results[provider_key] = result
            except Exception as e:
                provider_results[provider_key] = {
                    'success': False,
                    'error': str(e)
                }

        return provider_results

    async def _test_single_llm_provider(self, model: str) -> Dict[str, Any]:
        """Тестирование одного LLM провайдера"""
        test_prompt = "Привет! Как дела?"

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': 'Bearer sk-1234567890abcdef',
                    'Content-Type': 'application/json'
                }

                payload = {
                    'model': model,
                    'messages': [{'role': 'user', 'content': test_prompt}],
                    'max_tokens': 50,
                    'temperature': 0.7
                }

                start_time = time.time()
                async with session.post(f"{self.config.litellm_api_url}/v1/chat/completions",
                                      headers=headers,
                                      json=payload,
                                      timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        response_data = await response.json()

                        return {
                            'success': True,
                            'response_time_ms': response_time,
                            'model': model,
                            'tokens_generated': response_data.get('usage', {}).get('completion_tokens', 0),
                            'total_tokens': response_data.get('usage', {}).get('total_tokens', 0),
                            'response_preview': response_data.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'status_code': response.status,
                            'response_time_ms': response_time,
                            'error': error_text
                        }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _test_llm_fallback(self) -> Dict[str, Any]:
        """Тестирование fallback механизмов между провайдерами"""
        # Тест с несуществующей моделью для проверки fallback
        try:
            result = await self._test_single_llm_provider('nonexistent-model')

            return {
                'fallback_tested': True,
                'fallback_success': result.get('success', False),
                'fallback_details': result
            }
        except Exception as e:
            return {
                'fallback_tested': True,
                'fallback_success': False,
                'error': str(e)
            }

# Функция для запуска тестирования
async def main():
    """Основная функция для запуска A/B тестирования"""
    config = TestConfig()
    framework = ABTestingFramework(config)
    
    try:
        results = await framework.run_comprehensive_tests()
        framework.save_results_to_file()
        
        # Краткий отчет
        print("\n" + "="*60)
        print("📊 КРАТКИЙ ОТЧЕТ A/B ТЕСТИРОВАНИЯ")
        print("="*60)
        
        # Здоровье системы
        if 'health_check' in results:
            healthy_services = sum(1 for metrics in results['health_check'].values() 
                                 if hasattr(metrics, 'is_healthy') and metrics.is_healthy)
            total_services = len(results['health_check'])
            print(f"🏥 Здоровье системы: {healthy_services}/{total_services} сервисов здоровы")
        
        print(f"⏱️  Общее время тестирования: {results.get('test_duration', 0):.1f} секунд")
        print("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
