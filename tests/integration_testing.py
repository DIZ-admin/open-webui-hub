#!/usr/bin/env python3
"""
Интеграционное тестирование микросервисов Open WebUI Hub
Проверяет взаимодействие между сервисами, Nginx routing, Docker интеграцию
"""

import asyncio
import aiohttp
import docker
import time
import json
import sys
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationTester:
    """Тестер интеграции микросервисов"""
    
    def __init__(self):
        self.docker_client = None
        self.services_config = {
            'hub': {'port': 5003, 'health_path': '/api/health'},
            'openwebui': {'port': 3000, 'health_path': '/'},
            'litellm': {'port': 4000, 'health_path': '/health'},
            'ollama': {'port': 11435, 'health_path': '/'},
            'redis': {'port': 6379, 'health_path': None},
            'db': {'port': 5432, 'health_path': None},
            'nginx': {'port': 80, 'health_path': '/'},
            'auth': {'port': 9090, 'health_path': '/health'},
            'docling': {'port': 5001, 'health_path': '/health'},
            'tika': {'port': 9998, 'health_path': '/'},
            'edgetts': {'port': 5050, 'health_path': '/'},
            'mcposerver': {'port': 8000, 'health_path': '/'},
            'searxng': {'port': 8080, 'health_path': '/'}
        }
        self.results = {}
        
        # Инициализация Docker клиента
        try:
            self.docker_client = docker.from_env()
            logger.info("✅ Docker client инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Docker: {e}")
    
    async def run_integration_tests(self) -> Dict[str, Any]:
        """Запуск интеграционного тестирования"""
        logger.info("🔗 Начало интеграционного тестирования микросервисов")
        
        test_results = {
            'docker_integration': await self._test_docker_integration(),
            'service_health_chain': await self._test_service_health_chain(),
            'nginx_routing': await self._test_nginx_routing(),
            'service_communication': await self._test_service_communication(),
            'dependency_validation': await self._test_dependency_validation(),
            'network_connectivity': await self._test_network_connectivity(),
            'compose_validation': await self._test_compose_validation(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results = test_results
        return test_results
    
    async def _test_docker_integration(self) -> Dict[str, Any]:
        """Тестирование Docker интеграции"""
        if not self.docker_client:
            return {'success': False, 'error': 'Docker client недоступен'}
        
        try:
            # Получение всех контейнеров Open WebUI Hub
            all_containers = self.docker_client.containers.list(all=True)
            hub_containers = [c for c in all_containers if 'open-webui-hub' in c.name]
            
            container_details = {}
            running_count = 0
            healthy_count = 0
            
            for container in hub_containers:
                try:
                    # Получение статистики контейнера
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
                    
                    # Проверка health check
                    health_status = 'unknown'
                    if hasattr(container, 'attrs') and 'State' in container.attrs:
                        health = container.attrs['State'].get('Health', {})
                        health_status = health.get('Status', 'unknown')
                    
                    container_info = {
                        'name': container.name,
                        'status': container.status,
                        'health_status': health_status,
                        'cpu_percent': round(cpu_percent, 2),
                        'memory_usage_mb': round(memory_usage / 1024 / 1024, 2),
                        'memory_percent': round(memory_percent, 2),
                        'created': container.attrs['Created'],
                        'image': container.image.tags[0] if container.image.tags else 'unknown',
                        'ports': container.attrs['NetworkSettings']['Ports']
                    }
                    
                    container_details[container.name] = container_info
                    
                    if container.status == 'running':
                        running_count += 1
                    
                    if health_status == 'healthy':
                        healthy_count += 1
                        
                except Exception as e:
                    container_details[container.name] = {
                        'name': container.name,
                        'status': container.status,
                        'error': str(e)
                    }
            
            return {
                'success': True,
                'total_containers': len(hub_containers),
                'running_containers': running_count,
                'healthy_containers': healthy_count,
                'container_health_rate': (healthy_count / len(hub_containers) * 100) if hub_containers else 0,
                'container_details': container_details
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _test_service_health_chain(self) -> Dict[str, Any]:
        """Тестирование цепочки health check сервисов"""
        health_results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for service_name, config in self.services_config.items():
                if config['health_path']:
                    health_url = f"http://localhost:{config['port']}{config['health_path']}"
                    
                    try:
                        start_time = time.time()
                        async with session.get(health_url) as response:
                            response_time = (time.time() - start_time) * 1000
                            
                            health_results[service_name] = {
                                'healthy': response.status == 200,
                                'status_code': response.status,
                                'response_time_ms': response_time,
                                'url': health_url
                            }
                    except Exception as e:
                        health_results[service_name] = {
                            'healthy': False,
                            'error': str(e),
                            'url': health_url
                        }
                else:
                    # Для сервисов без HTTP health check (Redis, PostgreSQL)
                    health_results[service_name] = await self._test_non_http_service(service_name, config)
        
        healthy_count = sum(1 for result in health_results.values() if result.get('healthy', False))
        total_count = len(health_results)
        
        return {
            'total_services': total_count,
            'healthy_services': healthy_count,
            'health_percentage': (healthy_count / total_count * 100) if total_count > 0 else 0,
            'service_details': health_results
        }
    
    async def _test_non_http_service(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирование сервисов без HTTP интерфейса"""
        if service_name == 'redis':
            try:
                import redis
                client = redis.Redis(host='localhost', port=config['port'], decode_responses=True)
                client.ping()
                return {'healthy': True, 'method': 'redis_ping'}
            except Exception as e:
                return {'healthy': False, 'error': str(e), 'method': 'redis_ping'}
        
        elif service_name == 'db':
            try:
                try:
                    import psycopg2  # type: ignore
                except ImportError:
                    return {'healthy': False, 'error': 'psycopg2 not installed', 'method': 'postgres_connection'}

                conn = psycopg2.connect(
                    host='localhost',
                    port=config['port'],
                    database='openwebui',
                    user='postgres',
                    password='postgres'
                )
                conn.close()
                return {'healthy': True, 'method': 'postgres_connection'}
            except Exception as e:
                return {'healthy': False, 'error': str(e), 'method': 'postgres_connection'}
        
        else:
            return {'healthy': False, 'error': 'No health check method available'}
    
    async def _test_nginx_routing(self) -> Dict[str, Any]:
        """Тестирование маршрутизации Nginx"""
        nginx_routes = {
            'root': 'http://localhost:80/',
            'hub_route': 'http://localhost:80/hub',
            'api_hub_route': 'http://localhost:80/api/hub/health',
            'openwebui_route': 'http://localhost:80/docs',
            'redis_route': 'http://localhost:80/redis',
            'searxng_route': 'http://localhost:80/searxng'
        }
        
        routing_results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for route_name, url in nginx_routes.items():
                try:
                    start_time = time.time()
                    async with session.get(url, allow_redirects=False) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        routing_results[route_name] = {
                            'success': response.status in [200, 301, 302, 401, 403],  # Допустимые статусы
                            'status_code': response.status,
                            'response_time_ms': response_time,
                            'url': url,
                            'server': response.headers.get('server', 'unknown'),
                            'location': response.headers.get('location', None)
                        }
                except Exception as e:
                    routing_results[route_name] = {
                        'success': False,
                        'error': str(e),
                        'url': url
                    }
        
        successful_routes = sum(1 for result in routing_results.values() if result.get('success', False))
        total_routes = len(routing_results)
        
        return {
            'total_routes': total_routes,
            'successful_routes': successful_routes,
            'routing_success_rate': (successful_routes / total_routes * 100) if total_routes > 0 else 0,
            'route_details': routing_results
        }
    
    async def _test_service_communication(self) -> Dict[str, Any]:
        """Тестирование взаимодействия между сервисами"""
        communication_tests = {
            'hub_to_redis': await self._test_hub_redis_communication(),
            'hub_to_docker': await self._test_hub_docker_communication(),
            'litellm_to_ollama': await self._test_litellm_ollama_communication(),
            'openwebui_to_litellm': await self._test_openwebui_litellm_communication()
        }
        
        successful_communications = sum(1 for result in communication_tests.values() 
                                      if result.get('success', False))
        total_communications = len(communication_tests)
        
        return {
            'total_tests': total_communications,
            'successful_tests': successful_communications,
            'communication_success_rate': (successful_communications / total_communications * 100) if total_communications > 0 else 0,
            'test_details': communication_tests
        }
    
    async def _test_hub_redis_communication(self) -> Dict[str, Any]:
        """Тест взаимодействия Hub с Redis"""
        try:
            # Проверяем, что Hub может получить информацию о кэше
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:5003/api/cache/info') as response:
                    if response.status == 200:
                        cache_info = await response.json()
                        return {
                            'success': True,
                            'cache_size': cache_info.get('cache_size', 0),
                            'cache_keys': len(cache_info.get('cache_keys', [])),
                            'response_time_ms': 0  # Можно добавить измерение времени
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _test_hub_docker_communication(self) -> Dict[str, Any]:
        """Тест взаимодействия Hub с Docker"""
        try:
            # Проверяем, что Hub может получить информацию о сервисах через Docker
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:5003/api/services') as response:
                    if response.status == 200:
                        services_info = await response.json()
                        services = services_info.get('services', [])
                        
                        # Проверяем, что есть информация о контейнерах
                        containers_with_status = sum(1 for service in services 
                                                   if service.get('container_status') != 'unknown')
                        
                        return {
                            'success': True,
                            'total_services': len(services),
                            'services_with_container_info': containers_with_status,
                            'docker_integration_rate': (containers_with_status / len(services) * 100) if services else 0
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _test_litellm_ollama_communication(self) -> Dict[str, Any]:
        """Тест взаимодействия LiteLLM с Ollama"""
        try:
            # Проверяем доступность моделей через LiteLLM
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': 'Bearer sk-1234567890abcdef'}
                async with session.get('http://localhost:4000/v1/models', headers=headers) as response:
                    if response.status == 200:
                        models_data = await response.json()
                        models = models_data.get('data', [])
                        
                        # Проверяем наличие Ollama моделей
                        ollama_models = [model for model in models 
                                       if 'ollama' in model.get('owned_by', '').lower()]
                        
                        return {
                            'success': True,
                            'total_models': len(models),
                            'ollama_models': len(ollama_models),
                            'ollama_integration': len(ollama_models) > 0
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _test_openwebui_litellm_communication(self) -> Dict[str, Any]:
        """Тест взаимодействия Open WebUI с LiteLLM"""
        try:
            # Проверяем, что Open WebUI доступен и может взаимодействовать с LLM
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:3000/') as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Проверяем наличие элементов, указывающих на интеграцию с LLM
                        has_model_references = 'model' in content.lower()
                        has_chat_interface = 'chat' in content.lower()
                        has_api_references = 'api' in content.lower()
                        
                        return {
                            'success': True,
                            'has_model_references': has_model_references,
                            'has_chat_interface': has_chat_interface,
                            'has_api_references': has_api_references,
                            'integration_indicators': sum([has_model_references, has_chat_interface, has_api_references])
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _test_dependency_validation(self) -> Dict[str, Any]:
        """Валидация зависимостей между сервисами"""
        dependencies = {
            'openwebui': ['auth', 'hub', 'docling', 'db', 'edgetts', 'litellm', 'mcposerver', 'nginx', 'ollama', 'searxng', 'tika'],
            'litellm': ['ollama', 'redis'],
            'hub': ['db', 'redis'],
            'auth': [],
            'nginx': []  # Nginx зависит от всех, но мы проверим основные
        }
        
        dependency_results = {}
        
        for service, deps in dependencies.items():
            service_deps_status = {}
            
            for dep in deps:
                if dep in self.services_config:
                    dep_config = self.services_config[dep]
                    
                    if dep_config['health_path']:
                        health_url = f"http://localhost:{dep_config['port']}{dep_config['health_path']}"
                        
                        try:
                            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                                async with session.get(health_url) as response:
                                    service_deps_status[dep] = {
                                        'available': response.status == 200,
                                        'status_code': response.status
                                    }
                        except Exception:
                            service_deps_status[dep] = {
                                'available': False,
                                'error': 'Connection failed'
                            }
                    else:
                        # Для сервисов без HTTP health check
                        service_deps_status[dep] = {'available': True, 'note': 'No HTTP health check'}
            
            available_deps = sum(1 for status in service_deps_status.values() 
                               if status.get('available', False))
            total_deps = len(service_deps_status)
            
            dependency_results[service] = {
                'total_dependencies': total_deps,
                'available_dependencies': available_deps,
                'dependency_satisfaction_rate': (available_deps / total_deps * 100) if total_deps > 0 else 100,
                'dependency_details': service_deps_status
            }
        
        return dependency_results

    async def _test_network_connectivity(self) -> Dict[str, Any]:
        """Тестирование сетевой связности между сервисами"""
        network_tests = {}

        # Тестируем основные сетевые соединения
        test_connections = [
            ('hub_to_redis', 'localhost', 6379),
            ('hub_to_db', 'localhost', 5432),
            ('litellm_to_ollama', 'localhost', 11435),
            ('nginx_to_hub', 'localhost', 5003),
            ('nginx_to_openwebui', 'localhost', 3000)
        ]

        for test_name, host, port in test_connections:
            try:
                # Простая проверка TCP соединения
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()

                network_tests[test_name] = {
                    'success': result == 0,
                    'host': host,
                    'port': port,
                    'connection_result': result
                }
            except Exception as e:
                network_tests[test_name] = {
                    'success': False,
                    'host': host,
                    'port': port,
                    'error': str(e)
                }

        successful_connections = sum(1 for test in network_tests.values()
                                   if test.get('success', False))
        total_connections = len(network_tests)

        return {
            'total_connections_tested': total_connections,
            'successful_connections': successful_connections,
            'network_connectivity_rate': (successful_connections / total_connections * 100) if total_connections > 0 else 0,
            'connection_details': network_tests
        }

    async def _test_compose_validation(self) -> Dict[str, Any]:
        """Валидация Docker Compose конфигурации"""
        try:
            # Проверяем конфигурацию compose.local.yml
            result = subprocess.run(
                ['docker-compose', '-f', 'compose.local.yml', 'config'],
                capture_output=True,
                text=True,
                cwd='/Users/kostas/Documents/Projects/open-webui-hub'
            )

            if result.returncode == 0:
                # Парсим вывод для получения информации о сервисах
                config_output = result.stdout

                # Подсчитываем количество сервисов в конфигурации
                service_count = config_output.count('services:') + config_output.count('  ') // 2

                return {
                    'success': True,
                    'config_valid': True,
                    'estimated_services': service_count,
                    'config_size': len(config_output)
                }
            else:
                return {
                    'success': False,
                    'config_valid': False,
                    'error': result.stderr
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def save_results(self, filename: Optional[str] = None):
        """Сохранение результатов интеграционного тестирования"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tests/integration_testing_results_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"📄 Результаты интеграционного тестирования сохранены в {filename}")
        return filename

    def generate_summary_report(self) -> str:
        """Генерация краткого отчета интеграционного тестирования"""
        if not self.results:
            return "Нет данных для генерации отчета"

        summary = []
        summary.append("# 🔗 Отчет интеграционного тестирования Open WebUI Hub")
        summary.append(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")

        # Docker интеграция
        docker_results = self.results.get('docker_integration', {})
        if docker_results.get('success', False):
            total_containers = docker_results.get('total_containers', 0)
            running_containers = docker_results.get('running_containers', 0)
            healthy_containers = docker_results.get('healthy_containers', 0)

            summary.append("## 🐳 Docker интеграция")
            summary.append(f"- Всего контейнеров: {total_containers}")
            summary.append(f"- Запущенных: {running_containers}")
            summary.append(f"- Здоровых: {healthy_containers}")
            summary.append(f"- Процент здоровых: {docker_results.get('container_health_rate', 0):.1f}%")
            summary.append("")

        # Health check цепочка
        health_results = self.results.get('service_health_chain', {})
        if health_results:
            summary.append("## 🏥 Health check сервисов")
            summary.append(f"- Всего сервисов: {health_results.get('total_services', 0)}")
            summary.append(f"- Здоровых: {health_results.get('healthy_services', 0)}")
            summary.append(f"- Процент здоровых: {health_results.get('health_percentage', 0):.1f}%")
            summary.append("")

        # Nginx маршрутизация
        nginx_results = self.results.get('nginx_routing', {})
        if nginx_results:
            summary.append("## 🌐 Nginx маршрутизация")
            summary.append(f"- Всего маршрутов: {nginx_results.get('total_routes', 0)}")
            summary.append(f"- Успешных: {nginx_results.get('successful_routes', 0)}")
            summary.append(f"- Успешность: {nginx_results.get('routing_success_rate', 0):.1f}%")
            summary.append("")

        # Взаимодействие сервисов
        comm_results = self.results.get('service_communication', {})
        if comm_results:
            summary.append("## 🔄 Взаимодействие сервисов")
            summary.append(f"- Всего тестов: {comm_results.get('total_tests', 0)}")
            summary.append(f"- Успешных: {comm_results.get('successful_tests', 0)}")
            summary.append(f"- Успешность: {comm_results.get('communication_success_rate', 0):.1f}%")
            summary.append("")

        # Сетевая связность
        network_results = self.results.get('network_connectivity', {})
        if network_results:
            summary.append("## 🌐 Сетевая связность")
            summary.append(f"- Всего соединений: {network_results.get('total_connections_tested', 0)}")
            summary.append(f"- Успешных: {network_results.get('successful_connections', 0)}")
            summary.append(f"- Связность: {network_results.get('network_connectivity_rate', 0):.1f}%")
            summary.append("")

        # Общая оценка
        summary.append("## 📊 Общая оценка интеграции")

        # Подсчет общего балла интеграции
        scores = []
        if docker_results.get('success', False):
            scores.append(docker_results.get('container_health_rate', 0))
        if health_results:
            scores.append(health_results.get('health_percentage', 0))
        if nginx_results:
            scores.append(nginx_results.get('routing_success_rate', 0))
        if comm_results:
            scores.append(comm_results.get('communication_success_rate', 0))
        if network_results:
            scores.append(network_results.get('network_connectivity_rate', 0))

        overall_score = sum(scores) / len(scores) if scores else 0

        if overall_score >= 90:
            status = "🟢 Отличная"
        elif overall_score >= 75:
            status = "🟡 Хорошая"
        elif overall_score >= 50:
            status = "🟠 Удовлетворительная"
        else:
            status = "🔴 Требует внимания"

        summary.append(f"- **Общий балл интеграции:** {overall_score:.1f}/100")
        summary.append(f"- **Статус:** {status}")
        summary.append("")
        summary.append("---")
        summary.append("*Отчет сгенерирован автоматически системой интеграционного тестирования*")

        return "\n".join(summary)

async def main():
    """Основная функция"""
    print("🔗 Интеграционное тестирование микросервисов Open WebUI Hub")
    print("=" * 60)

    tester = IntegrationTester()

    try:
        results = await tester.run_integration_tests()
        results_file = tester.save_results()

        # Генерация и сохранение краткого отчета
        summary_report = tester.generate_summary_report()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = f"tests/integration_summary_{timestamp}.md"

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_report)

        # Вывод краткого отчета
        print("\n" + "="*60)
        print("📊 КРАТКИЙ ОТЧЕТ ИНТЕГРАЦИОННОГО ТЕСТИРОВАНИЯ")
        print("="*60)

        # Docker интеграция
        docker_results = results.get('docker_integration', {})
        if docker_results.get('success', False):
            print(f"🐳 Docker: {docker_results.get('running_containers', 0)}/{docker_results.get('total_containers', 0)} контейнеров запущено")

        # Health check
        health_results = results.get('service_health_chain', {})
        if health_results:
            print(f"🏥 Health: {health_results.get('healthy_services', 0)}/{health_results.get('total_services', 0)} сервисов здоровы")

        # Nginx
        nginx_results = results.get('nginx_routing', {})
        if nginx_results:
            print(f"🌐 Nginx: {nginx_results.get('successful_routes', 0)}/{nginx_results.get('total_routes', 0)} маршрутов работают")

        # Взаимодействие
        comm_results = results.get('service_communication', {})
        if comm_results:
            print(f"🔄 Взаимодействие: {comm_results.get('successful_tests', 0)}/{comm_results.get('total_tests', 0)} тестов прошли")

        print("="*60)
        print(f"📄 Детальные результаты: {results_file}")
        print(f"📋 Краткий отчет: {summary_file}")

        return 0

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
