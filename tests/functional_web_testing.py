#!/usr/bin/env python3
"""
Функциональное тестирование веб-интерфейсов Open WebUI Hub
Тестирует доступные веб-интерфейсы и их функциональность
"""

import asyncio
import aiohttp
import time
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebInterfaceTester:
    """Тестер веб-интерфейсов"""
    
    def __init__(self):
        self.base_urls = {
            'hub': 'http://localhost:5003',
            'openwebui': 'http://localhost:3000',
            'redis_insight': 'http://localhost:8001',
            'searxng': 'http://localhost:8080',
            'nginx': 'http://localhost:80'
        }
        self.results = {}
    
    async def run_functional_tests(self) -> Dict[str, Any]:
        """Запуск функционального тестирования"""
        logger.info("🚀 Начало функционального тестирования веб-интерфейсов")
        
        test_results = {}
        
        # Тестирование каждого веб-интерфейса
        for service_name, base_url in self.base_urls.items():
            logger.info(f"🔍 Тестирование {service_name} ({base_url})")
            
            service_results = await self._test_web_interface(service_name, base_url)
            test_results[service_name] = service_results
        
        # Специальные тесты для Hub API
        logger.info("🔧 Специальное тестирование Hub API")
        hub_api_results = await self._test_hub_api_functionality()
        test_results['hub_api_detailed'] = hub_api_results
        
        self.results = test_results
        return test_results
    
    async def _test_web_interface(self, service_name: str, base_url: str) -> Dict[str, Any]:
        """Тестирование одного веб-интерфейса"""
        results = {
            'service_name': service_name,
            'base_url': base_url,
            'accessibility': {},
            'performance': {},
            'functionality': {},
            'timestamp': datetime.now().isoformat()
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            # Тест доступности
            accessibility_result = await self._test_accessibility(session, base_url)
            results['accessibility'] = accessibility_result
            
            # Тест производительности загрузки
            if accessibility_result.get('accessible', False):
                performance_result = await self._test_loading_performance(session, base_url)
                results['performance'] = performance_result
                
                # Функциональные тесты (если интерфейс доступен)
                functionality_result = await self._test_basic_functionality(session, service_name, base_url)
                results['functionality'] = functionality_result
        
        return results
    
    async def _test_accessibility(self, session: aiohttp.ClientSession, base_url: str) -> Dict[str, Any]:
        """Тест доступности веб-интерфейса"""
        try:
            start_time = time.time()
            async with session.get(base_url) as response:
                response_time = (time.time() - start_time) * 1000
                content = await response.text()
                
                return {
                    'accessible': True,
                    'status_code': response.status,
                    'response_time_ms': response_time,
                    'content_length': len(content),
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'has_html': '<html' in content.lower() or '<!doctype html' in content.lower(),
                    'has_title': '<title>' in content.lower(),
                    'server': response.headers.get('server', 'unknown')
                }
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e),
                'response_time_ms': -1
            }
    
    async def _test_loading_performance(self, session: aiohttp.ClientSession, base_url: str) -> Dict[str, Any]:
        """Тест производительности загрузки"""
        load_times = []
        
        # Выполняем 5 запросов для получения средней производительности
        for i in range(5):
            try:
                start_time = time.time()
                async with session.get(base_url) as response:
                    await response.read()  # Полное чтение контента
                    load_time = (time.time() - start_time) * 1000
                    load_times.append(load_time)
                
                # Небольшая пауза между запросами
                await asyncio.sleep(0.5)
            except Exception:
                continue
        
        if load_times:
            return {
                'avg_load_time_ms': sum(load_times) / len(load_times),
                'min_load_time_ms': min(load_times),
                'max_load_time_ms': max(load_times),
                'load_times': load_times,
                'performance_rating': self._rate_performance(sum(load_times) / len(load_times))
            }
        else:
            return {
                'avg_load_time_ms': -1,
                'error': 'Не удалось измерить производительность'
            }
    
    def _rate_performance(self, avg_time_ms: float) -> str:
        """Оценка производительности"""
        if avg_time_ms < 100:
            return 'excellent'
        elif avg_time_ms < 300:
            return 'good'
        elif avg_time_ms < 1000:
            return 'fair'
        else:
            return 'poor'
    
    async def _test_basic_functionality(self, session: aiohttp.ClientSession, service_name: str, base_url: str) -> Dict[str, Any]:
        """Базовое функциональное тестирование"""
        functionality_tests = {
            'static_resources': await self._test_static_resources(session, base_url),
            'interactive_elements': await self._test_interactive_elements(session, service_name, base_url)
        }
        
        return functionality_tests
    
    async def _test_static_resources(self, session: aiohttp.ClientSession, base_url: str) -> Dict[str, Any]:
        """Тест статических ресурсов"""
        common_resources = [
            '/favicon.ico',
            '/robots.txt',
            '/css/style.css',
            '/js/app.js',
            '/assets/logo.png'
        ]
        
        resource_results = {}
        
        for resource in common_resources:
            try:
                async with session.get(f"{base_url}{resource}") as response:
                    resource_results[resource] = {
                        'available': response.status == 200,
                        'status_code': response.status,
                        'content_type': response.headers.get('content-type', 'unknown')
                    }
            except Exception:
                resource_results[resource] = {
                    'available': False,
                    'error': 'Request failed'
                }
        
        available_count = sum(1 for r in resource_results.values() if r.get('available', False))
        
        return {
            'resources_tested': len(common_resources),
            'resources_available': available_count,
            'availability_rate': available_count / len(common_resources),
            'details': resource_results
        }
    
    async def _test_interactive_elements(self, session: aiohttp.ClientSession, service_name: str, base_url: str) -> Dict[str, Any]:
        """Тест интерактивных элементов (специфично для каждого сервиса)"""
        if service_name == 'hub':
            return await self._test_hub_interactive_elements(session, base_url)
        elif service_name == 'openwebui':
            return await self._test_openwebui_interactive_elements(session, base_url)
        elif service_name == 'redis_insight':
            return await self._test_redis_insight_elements(session, base_url)
        else:
            return {'tested': False, 'reason': 'No specific tests for this service'}
    
    async def _test_hub_interactive_elements(self, session: aiohttp.ClientSession, base_url: str) -> Dict[str, Any]:
        """Тест интерактивных элементов Hub"""
        try:
            # Получение главной страницы
            async with session.get(base_url) as response:
                content = await response.text()
                
                # Проверка наличия ключевых элементов
                has_navigation = 'nav' in content.lower() or 'menu' in content.lower()
                has_dashboard = 'dashboard' in content.lower()
                has_services = 'services' in content.lower() or 'сервисы' in content.lower()
                has_metrics = 'metrics' in content.lower() or 'метрики' in content.lower()
                
                return {
                    'tested': True,
                    'has_navigation': has_navigation,
                    'has_dashboard_elements': has_dashboard,
                    'has_services_section': has_services,
                    'has_metrics_section': has_metrics,
                    'interactive_score': sum([has_navigation, has_dashboard, has_services, has_metrics]) / 4
                }
        except Exception as e:
            return {
                'tested': False,
                'error': str(e)
            }
    
    async def _test_openwebui_interactive_elements(self, session: aiohttp.ClientSession, base_url: str) -> Dict[str, Any]:
        """Тест интерактивных элементов Open WebUI"""
        try:
            async with session.get(base_url) as response:
                content = await response.text()
                
                # Проверка элементов Open WebUI
                has_chat_interface = 'chat' in content.lower() or 'message' in content.lower()
                has_model_selector = 'model' in content.lower()
                has_settings = 'settings' in content.lower() or 'config' in content.lower()
                
                return {
                    'tested': True,
                    'has_chat_interface': has_chat_interface,
                    'has_model_selector': has_model_selector,
                    'has_settings': has_settings,
                    'interactive_score': sum([has_chat_interface, has_model_selector, has_settings]) / 3
                }
        except Exception as e:
            return {
                'tested': False,
                'error': str(e)
            }
    
    async def _test_redis_insight_elements(self, session: aiohttp.ClientSession, base_url: str) -> Dict[str, Any]:
        """Тест интерактивных элементов Redis Insight"""
        try:
            async with session.get(base_url) as response:
                content = await response.text()
                
                # Проверка элементов Redis Insight
                has_redis_interface = 'redis' in content.lower()
                has_database_view = 'database' in content.lower() or 'db' in content.lower()
                has_monitoring = 'monitor' in content.lower() or 'stats' in content.lower()
                
                return {
                    'tested': True,
                    'has_redis_interface': has_redis_interface,
                    'has_database_view': has_database_view,
                    'has_monitoring': has_monitoring,
                    'interactive_score': sum([has_redis_interface, has_database_view, has_monitoring]) / 3
                }
        except Exception as e:
            return {
                'tested': False,
                'error': str(e)
            }
    
    async def _test_hub_api_functionality(self) -> Dict[str, Any]:
        """Детальное тестирование функциональности Hub API"""
        hub_api_url = self.base_urls['hub']
        
        api_tests = {
            'health_endpoint': await self._test_api_endpoint(f"{hub_api_url}/api/health"),
            'services_endpoint': await self._test_api_endpoint(f"{hub_api_url}/api/services"),
            'metrics_endpoint': await self._test_api_endpoint(f"{hub_api_url}/api/metrics"),
            'architecture_endpoint': await self._test_api_endpoint(f"{hub_api_url}/api/architecture"),
            'cache_info_endpoint': await self._test_api_endpoint(f"{hub_api_url}/api/cache/info"),
            'real_time_updates': await self._test_real_time_updates(hub_api_url)
        }
        
        return api_tests
    
    async def _test_api_endpoint(self, endpoint_url: str) -> Dict[str, Any]:
        """Тест API эндпоинта"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(endpoint_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            return {
                                'success': True,
                                'status_code': response.status,
                                'response_time_ms': response_time,
                                'data_keys': list(data.keys()) if isinstance(data, dict) else [],
                                'data_size': len(str(data)),
                                'has_timestamp': 'timestamp' in str(data).lower()
                            }
                        except json.JSONDecodeError:
                            return {
                                'success': False,
                                'status_code': response.status,
                                'response_time_ms': response_time,
                                'error': 'Invalid JSON response'
                            }
                    else:
                        return {
                            'success': False,
                            'status_code': response.status,
                            'response_time_ms': response_time,
                            'error': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response_time_ms': -1
            }
    
    async def _test_real_time_updates(self, hub_api_url: str) -> Dict[str, Any]:
        """Тест обновлений в реальном времени"""
        try:
            # Делаем два запроса к метрикам с интервалом
            metrics_url = f"{hub_api_url}/api/metrics"
            
            async with aiohttp.ClientSession() as session:
                # Первый запрос
                async with session.get(metrics_url) as response1:
                    data1 = await response1.json()
                    timestamp1 = data1.get('timestamp', 0)
                
                # Ждем 2 секунды
                await asyncio.sleep(2)
                
                # Второй запрос
                async with session.get(metrics_url) as response2:
                    data2 = await response2.json()
                    timestamp2 = data2.get('timestamp', 0)
                
                # Проверяем, обновились ли данные
                timestamps_different = timestamp1 != timestamp2
                uptime_increased = data2.get('uptime', 0) > data1.get('uptime', 0)
                
                return {
                    'tested': True,
                    'timestamps_update': timestamps_different,
                    'uptime_increases': uptime_increased,
                    'real_time_score': sum([timestamps_different, uptime_increased]) / 2,
                    'timestamp_diff': timestamp2 - timestamp1 if isinstance(timestamp1, (int, float)) and isinstance(timestamp2, (int, float)) else 0
                }
        except Exception as e:
            return {
                'tested': False,
                'error': str(e)
            }
    
    def save_results(self, filename: Optional[str] = None):
        """Сохранение результатов тестирования"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tests/functional_web_testing_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 Результаты функционального тестирования сохранены в {filename}")
        return filename

async def main():
    """Основная функция"""
    print("🌐 Функциональное тестирование веб-интерфейсов Open WebUI Hub")
    print("=" * 60)
    
    tester = WebInterfaceTester()
    
    try:
        results = await tester.run_functional_tests()
        results_file = tester.save_results()
        
        # Краткий отчет
        print("\n" + "="*60)
        print("📊 КРАТКИЙ ОТЧЕТ ФУНКЦИОНАЛЬНОГО ТЕСТИРОВАНИЯ")
        print("="*60)
        
        total_services = len(results)
        accessible_services = sum(1 for r in results.values() 
                                if isinstance(r, dict) and r.get('accessibility', {}).get('accessible', False))
        
        print(f"🌐 Доступных веб-интерфейсов: {accessible_services}/{total_services}")
        
        for service_name, service_results in results.items():
            if isinstance(service_results, dict) and 'accessibility' in service_results:
                accessible = service_results['accessibility'].get('accessible', False)
                status_icon = '✅' if accessible else '❌'
                response_time = service_results['accessibility'].get('response_time_ms', -1)
                
                print(f"{status_icon} {service_name}: {'Доступен' if accessible else 'Недоступен'} "
                      f"({response_time:.1f}ms)" if response_time > 0 else f"{status_icon} {service_name}: {'Доступен' if accessible else 'Недоступен'}")
        
        print("="*60)
        print(f"📄 Детальные результаты: {results_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
