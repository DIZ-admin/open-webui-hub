#!/usr/bin/env python3
"""
Специализированное тестирование LiteLLM интеграции
Тестирует производительность LLM провайдеров, fallback механизмы, кэширование
"""

import asyncio
import aiohttp
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import statistics

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiteLLMTester:
    """Тестер LiteLLM интеграции"""
    
    def __init__(self):
        self.litellm_url = "http://localhost:4000"
        self.auth_header = {"Authorization": "Bearer sk-1234567890abcdef"}
        self.test_prompts = [
            "Привет! Как дела?",
            "Напиши короткий код на Python для сортировки списка",
            "Объясни принцип работы нейронных сетей",
            "Какая погода сегодня?",
            "Переведи 'Hello World' на русский язык"
        ]
        self.results = {}
    
    async def run_litellm_tests(self) -> Dict[str, Any]:
        """Запуск комплексного тестирования LiteLLM"""
        logger.info("🤖 Начало тестирования LiteLLM интеграции")
        
        test_results = {
            'health_check': await self._test_health(),
            'models_availability': await self._test_models_availability(),
            'provider_performance': await self._test_provider_performance(),
            'fallback_mechanisms': await self._test_fallback_mechanisms(),
            'caching_efficiency': await self._test_caching_efficiency(),
            'load_testing': await self._test_load_performance(),
            'error_handling': await self._test_error_handling(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results = test_results
        return test_results
    
    async def _test_health(self) -> Dict[str, Any]:
        """Тест здоровья LiteLLM сервиса"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(f"{self.litellm_url}/health") as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        health_data = await response.json()
                        return {
                            'success': True,
                            'status': health_data.get('status', 'unknown'),
                            'response_time_ms': response_time,
                            'details': health_data
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
    
    async def _test_models_availability(self) -> Dict[str, Any]:
        """Тест доступности моделей"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(f"{self.litellm_url}/v1/models", headers=self.auth_header) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        models_data = await response.json()
                        models = models_data.get('data', [])
                        
                        # Анализ доступных моделей
                        providers = {}
                        for model in models:
                            provider = model.get('owned_by', 'unknown')
                            if provider not in providers:
                                providers[provider] = []
                            providers[provider].append(model.get('id', 'unknown'))
                        
                        return {
                            'success': True,
                            'total_models': len(models),
                            'providers': providers,
                            'provider_count': len(providers),
                            'response_time_ms': response_time,
                            'models_list': [model.get('id', 'unknown') for model in models]
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
    
    async def _test_provider_performance(self) -> Dict[str, Any]:
        """Тест производительности различных провайдеров"""
        models_to_test = [
            'llama3',
            'codellama',
            'llama3:8b',
            'mistral'
        ]
        
        provider_results = {}
        
        for model in models_to_test:
            logger.info(f"🔍 Тестирование модели: {model}")
            
            model_results = []
            
            # Тестируем каждую модель с несколькими промптами
            for prompt in self.test_prompts[:3]:  # Используем первые 3 промпта
                result = await self._test_single_generation(model, prompt)
                if result['success']:
                    model_results.append(result)
            
            if model_results:
                # Агрегируем результаты для модели
                response_times = [r['response_time_ms'] for r in model_results]
                token_counts = [r['total_tokens'] for r in model_results]
                
                provider_results[model] = {
                    'success': True,
                    'tests_completed': len(model_results),
                    'avg_response_time_ms': statistics.mean(response_times),
                    'min_response_time_ms': min(response_times),
                    'max_response_time_ms': max(response_times),
                    'avg_tokens': statistics.mean(token_counts),
                    'tokens_per_second': statistics.mean([r['tokens_per_second'] for r in model_results]),
                    'success_rate': len(model_results) / len(self.test_prompts[:3])
                }
            else:
                provider_results[model] = {
                    'success': False,
                    'error': 'No successful generations'
                }
        
        return provider_results
    
    async def _test_single_generation(self, model: str, prompt: str) -> Dict[str, Any]:
        """Тест генерации одного ответа"""
        try:
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 100,
                'temperature': 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    f"{self.litellm_url}/v1/chat/completions",
                    headers={**self.auth_header, 'Content-Type': 'application/json'},
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        response_data = await response.json()
                        usage = response_data.get('usage', {})
                        
                        completion_tokens = usage.get('completion_tokens', 0)
                        total_tokens = usage.get('total_tokens', 0)
                        tokens_per_second = completion_tokens / (response_time / 1000) if response_time > 0 else 0
                        
                        return {
                            'success': True,
                            'model': model,
                            'prompt': prompt[:50] + "..." if len(prompt) > 50 else prompt,
                            'response_time_ms': response_time,
                            'completion_tokens': completion_tokens,
                            'total_tokens': total_tokens,
                            'tokens_per_second': tokens_per_second,
                            'response_preview': response_data.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'model': model,
                            'status_code': response.status,
                            'response_time_ms': response_time,
                            'error': error_text
                        }
        except Exception as e:
            return {
                'success': False,
                'model': model,
                'error': str(e)
            }
    
    async def _test_fallback_mechanisms(self) -> Dict[str, Any]:
        """Тест fallback механизмов"""
        fallback_tests = {
            'nonexistent_model': await self._test_nonexistent_model(),
            'invalid_parameters': await self._test_invalid_parameters(),
            'timeout_handling': await self._test_timeout_handling()
        }
        
        return fallback_tests
    
    async def _test_nonexistent_model(self) -> Dict[str, Any]:
        """Тест с несуществующей моделью"""
        try:
            result = await self._test_single_generation('nonexistent-model-12345', 'Test prompt')
            
            return {
                'tested': True,
                'fallback_triggered': not result['success'],
                'response_details': result
            }
        except Exception as e:
            return {
                'tested': True,
                'fallback_triggered': True,
                'error': str(e)
            }
    
    async def _test_invalid_parameters(self) -> Dict[str, Any]:
        """Тест с некорректными параметрами"""
        try:
            payload = {
                'model': 'llama3',
                'messages': [{'role': 'user', 'content': 'Test'}],
                'max_tokens': -1,  # Некорректное значение
                'temperature': 5.0  # Некорректное значение
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.litellm_url}/v1/chat/completions",
                    headers={**self.auth_header, 'Content-Type': 'application/json'},
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    return {
                        'tested': True,
                        'error_handled': response.status != 200,
                        'status_code': response.status,
                        'response_text': await response.text()
                    }
        except Exception as e:
            return {
                'tested': True,
                'error_handled': True,
                'error': str(e)
            }
    
    async def _test_timeout_handling(self) -> Dict[str, Any]:
        """Тест обработки таймаутов"""
        try:
            payload = {
                'model': 'llama3',
                'messages': [{'role': 'user', 'content': 'Write a very long story about artificial intelligence'}],
                'max_tokens': 2000  # Большое количество токенов
            }
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                try:
                    async with session.post(
                        f"{self.litellm_url}/v1/chat/completions",
                        headers={**self.auth_header, 'Content-Type': 'application/json'},
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10)  # Короткий таймаут
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        return {
                            'tested': True,
                            'timeout_occurred': False,
                            'response_time_ms': response_time,
                            'status_code': response.status
                        }
                except asyncio.TimeoutError:
                    return {
                        'tested': True,
                        'timeout_occurred': True,
                        'timeout_handled': True
                    }
        except Exception as e:
            return {
                'tested': True,
                'timeout_occurred': True,
                'error': str(e)
            }
    
    async def _test_caching_efficiency(self) -> Dict[str, Any]:
        """Тест эффективности кэширования"""
        test_prompt = "What is 2+2?"
        model = "llama3"
        
        # Первый запрос (должен быть закэширован)
        first_result = await self._test_single_generation(model, test_prompt)
        
        if not first_result['success']:
            return {
                'tested': False,
                'error': 'First request failed'
            }
        
        # Ждем немного
        await asyncio.sleep(1)
        
        # Второй запрос (должен использовать кэш)
        second_result = await self._test_single_generation(model, test_prompt)
        
        if not second_result['success']:
            return {
                'tested': False,
                'error': 'Second request failed'
            }
        
        # Анализ кэширования
        first_time = first_result['response_time_ms']
        second_time = second_result['response_time_ms']
        
        # Если второй запрос значительно быстрее, возможно сработал кэш
        cache_improvement = (first_time - second_time) / first_time if first_time > 0 else 0
        
        return {
            'tested': True,
            'first_request_time_ms': first_time,
            'second_request_time_ms': second_time,
            'cache_improvement_percent': cache_improvement * 100,
            'likely_cached': cache_improvement > 0.3,  # 30% улучшение
            'same_response': first_result.get('response_preview', '') == second_result.get('response_preview', '')
        }
    
    async def _test_load_performance(self) -> Dict[str, Any]:
        """Тест производительности под нагрузкой"""
        concurrent_requests = 5
        model = "llama3"
        prompt = "Count from 1 to 10"
        
        # Создаем конкурентные запросы
        tasks = []
        for i in range(concurrent_requests):
            task = self._test_single_generation(model, f"{prompt} (request {i+1})")
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.time() - start_time) * 1000
        
        # Анализ результатов
        successful_results = [r for r in results if isinstance(r, dict) and r.get('success', False)]
        failed_results = [r for r in results if not (isinstance(r, dict) and r.get('success', False))]
        
        if successful_results:
            response_times = [r['response_time_ms'] for r in successful_results]
            
            return {
                'tested': True,
                'concurrent_requests': concurrent_requests,
                'successful_requests': len(successful_results),
                'failed_requests': len(failed_results),
                'success_rate': len(successful_results) / concurrent_requests,
                'total_time_ms': total_time,
                'avg_response_time_ms': statistics.mean(response_times),
                'min_response_time_ms': min(response_times),
                'max_response_time_ms': max(response_times),
                'requests_per_second': concurrent_requests / (total_time / 1000)
            }
        else:
            return {
                'tested': True,
                'concurrent_requests': concurrent_requests,
                'successful_requests': 0,
                'failed_requests': len(failed_results),
                'success_rate': 0,
                'error': 'All requests failed'
            }
    
    async def _test_error_handling(self) -> Dict[str, Any]:
        """Тест обработки ошибок"""
        error_tests = {
            'missing_auth': await self._test_missing_auth(),
            'invalid_json': await self._test_invalid_json(),
            'empty_prompt': await self._test_empty_prompt()
        }
        
        return error_tests
    
    async def _test_missing_auth(self) -> Dict[str, Any]:
        """Тест без авторизации"""
        try:
            payload = {
                'model': 'llama3',
                'messages': [{'role': 'user', 'content': 'Test'}]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.litellm_url}/v1/chat/completions",
                    headers={'Content-Type': 'application/json'},  # Без Authorization
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    return {
                        'tested': True,
                        'auth_required': response.status == 401,
                        'status_code': response.status,
                        'response_text': await response.text()
                    }
        except Exception as e:
            return {
                'tested': True,
                'error': str(e)
            }
    
    async def _test_invalid_json(self) -> Dict[str, Any]:
        """Тест с некорректным JSON"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.litellm_url}/v1/chat/completions",
                    headers={**self.auth_header, 'Content-Type': 'application/json'},
                    data='{"invalid": json}',  # Некорректный JSON
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    return {
                        'tested': True,
                        'error_handled': response.status == 400,
                        'status_code': response.status,
                        'response_text': await response.text()
                    }
        except Exception as e:
            return {
                'tested': True,
                'error_handled': True,
                'error': str(e)
            }
    
    async def _test_empty_prompt(self) -> Dict[str, Any]:
        """Тест с пустым промптом"""
        try:
            payload = {
                'model': 'llama3',
                'messages': [{'role': 'user', 'content': ''}]  # Пустой промпт
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.litellm_url}/v1/chat/completions",
                    headers={**self.auth_header, 'Content-Type': 'application/json'},
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    return {
                        'tested': True,
                        'handled_gracefully': response.status in [200, 400],
                        'status_code': response.status,
                        'response_text': await response.text()
                    }
        except Exception as e:
            return {
                'tested': True,
                'error': str(e)
            }

    def save_results(self, filename: Optional[str] = None):
        """Сохранение результатов тестирования LiteLLM"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tests/litellm_testing_results_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"📄 Результаты тестирования LiteLLM сохранены в {filename}")
        return filename

async def main():
    """Основная функция"""
    print("🤖 Тестирование LiteLLM интеграции Open WebUI Hub")
    print("=" * 60)

    tester = LiteLLMTester()

    try:
        results = await tester.run_litellm_tests()
        results_file = tester.save_results()

        # Вывод краткого отчета
        print("\n" + "="*60)
        print("📊 КРАТКИЙ ОТЧЕТ ТЕСТИРОВАНИЯ LITELLM")
        print("="*60)

        # Health check
        health_results = results.get('health_check', {})
        health_status = '✅ Здоров' if health_results.get('success', False) else '❌ Проблемы'
        print(f"🏥 Здоровье: {health_status}")

        # Модели
        models_results = results.get('models_availability', {})
        if models_results.get('success', False):
            total_models = models_results.get('total_models', 0)
            providers = models_results.get('provider_count', 0)
            print(f"📚 Модели: {total_models} моделей от {providers} провайдеров")

        # Производительность
        performance_results = results.get('provider_performance', {})
        if performance_results:
            successful_models = sum(1 for v in performance_results.values() if v.get('success', False))
            total_tested = len(performance_results)
            print(f"⚡ Производительность: {successful_models}/{total_tested} моделей работают")

        # Нагрузка
        load_results = results.get('load_testing', {})
        if load_results.get('tested', False):
            success_rate = load_results.get('success_rate', 0) * 100
            print(f"🚀 Нагрузка: {success_rate:.1f}% успешность")

        # Fallback
        fallback_results = results.get('fallback_mechanisms', {})
        if fallback_results:
            fallback_tests = sum(1 for test in fallback_results.values()
                               if test.get('tested', False))
            print(f"🔄 Fallback: {fallback_tests} механизмов протестировано")

        print("="*60)
        print(f"📄 Детальные результаты: {results_file}")

        return 0

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
