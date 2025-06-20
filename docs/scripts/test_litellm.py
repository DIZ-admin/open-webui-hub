#!/usr/bin/env python3
"""
LiteLLM Testing Script for Open WebUI Hub
Автоматическое тестирование всех доступных моделей и функций LiteLLM
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

# Конфигурация
LITELLM_BASE_URL = "http://localhost:4000"
API_KEY = "sk-1234567890abcdef"
DASHBOARD_API_URL = "http://localhost:5002"

class LiteLLMTester:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        self.results = {
            "models_test": {},
            "generation_test": {},
            "performance_test": {},
            "errors": []
        }

    def test_models_endpoint(self) -> bool:
        """Тестирование endpoint для получения списка моделей"""
        print("🔍 Тестирование /v1/models endpoint...")
        try:
            response = requests.get(f"{LITELLM_BASE_URL}/v1/models", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                self.results['models_test'] = {
                    'status': 'success',
                    'total_models': len(models),
                    'models': [model['id'] for model in models]
                }
                print(f"✅ Найдено {len(models)} моделей")
                return True
            else:
                self.results['models_test'] = {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                print(f"❌ Ошибка: {response.status_code}")
                return False
        except Exception as e:
            self.results['models_test'] = {'status': 'error', 'error': str(e)}
            print(f"❌ Исключение: {e}")
            return False

    def test_model_generation(self, model_name: str, test_prompt: str = "Привет! Скажи одно слово.") -> Dict[str, Any]:
        """Тестирование генерации для конкретной модели"""
        print(f"🤖 Тестирование модели {model_name}...")
        
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": 20
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{LITELLM_BASE_URL}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    usage = data.get('usage', {})
                    
                    result = {
                        'status': 'success',
                        'response_time': round(end_time - start_time, 2),
                        'content': content[:100],
                        'usage': usage,
                        'actual_model': data.get('model', model_name)
                    }
                    print(f"✅ {model_name}: {result['response_time']}s - \"{content[:50]}...\"")
                    return result
                else:
                    result = {'status': 'error', 'error': 'No choices in response'}
                    print(f"❌ {model_name}: Нет choices в ответе")
                    return result
            else:
                result = {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}: {response.text[:200]}"
                }
                print(f"❌ {model_name}: HTTP {response.status_code}")
                return result
                
        except Exception as e:
            result = {'status': 'error', 'error': str(e)}
            print(f"❌ {model_name}: {e}")
            return result

    def test_all_models(self) -> None:
        """Тестирование всех доступных моделей"""
        if not self.test_models_endpoint():
            return
            
        models = self.results['models_test'].get('models', [])
        local_models = [m for m in models if not any(provider in m for provider in ['gpt-', 'claude-', 'gemini-'])]
        
        print(f"\n🧪 Тестирование {len(local_models)} локальных моделей...")
        
        for model in local_models:
            result = self.test_model_generation(model)
            self.results['generation_test'][model] = result
            time.sleep(1)  # Небольшая пауза между запросами

    def test_dashboard_api(self) -> None:
        """Тестирование Dashboard API endpoints"""
        print("\n📊 Тестирование Dashboard API...")
        
        # Тест статуса
        try:
            response = requests.get(f"{DASHBOARD_API_URL}/api/litellm/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Dashboard API статус: {data.get('status', 'unknown')}")
                print(f"   Моделей: {data.get('total_models', 0)}")
            else:
                print(f"❌ Dashboard API статус: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Dashboard API ошибка: {e}")
        
        # Тест генерации через Dashboard API
        try:
            payload = {"model": "llama3", "message": "Тест через Dashboard API"}
            response = requests.post(
                f"{DASHBOARD_API_URL}/api/litellm/test",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print("✅ Dashboard API генерация работает")
                else:
                    print(f"❌ Dashboard API генерация: {data.get('error', 'unknown')}")
            else:
                print(f"❌ Dashboard API генерация: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Dashboard API генерация ошибка: {e}")

    def performance_benchmark(self) -> None:
        """Бенчмарк производительности"""
        print("\n⚡ Бенчмарк производительности...")
        
        test_cases = [
            {"model": "llama3", "prompt": "Привет!", "max_tokens": 10},
            {"model": "coder", "prompt": "def hello():", "max_tokens": 20},
        ]
        
        for test_case in test_cases:
            model = test_case["model"]
            times = []
            
            print(f"   Тестирование {model} (5 запросов)...")
            for i in range(5):
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{LITELLM_BASE_URL}/v1/chat/completions",
                        headers=self.headers,
                        json={
                            "model": test_case["model"],
                            "messages": [{"role": "user", "content": test_case["prompt"]}],
                            "max_tokens": test_case["max_tokens"]
                        },
                        timeout=60
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        times.append(end_time - start_time)
                        print(f"     Запрос {i+1}: {end_time - start_time:.2f}s")
                    else:
                        print(f"     Запрос {i+1}: Ошибка HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"     Запрос {i+1}: Ошибка {e}")
                
                time.sleep(2)  # Пауза между запросами
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                self.results['performance_test'][model] = {
                    'avg_time': round(avg_time, 2),
                    'min_time': round(min_time, 2),
                    'max_time': round(max_time, 2),
                    'successful_requests': len(times)
                }
                
                print(f"   📈 {model}: avg={avg_time:.2f}s, min={min_time:.2f}s, max={max_time:.2f}s")

    def generate_report(self) -> None:
        """Генерация итогового отчета"""
        print("\n" + "="*60)
        print("📋 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ LITELLM")
        print("="*60)
        
        # Статус моделей
        models_status = self.results.get('models_test', {})
        if models_status.get('status') == 'success':
            print(f"✅ Endpoint /v1/models: {models_status['total_models']} моделей доступно")
        else:
            print(f"❌ Endpoint /v1/models: {models_status.get('error', 'unknown')}")
        
        # Результаты генерации
        print(f"\n🤖 Тестирование генерации:")
        generation_results = self.results.get('generation_test', {})
        successful = sum(1 for r in generation_results.values() if r.get('status') == 'success')
        total = len(generation_results)
        print(f"   Успешных: {successful}/{total}")
        
        for model, result in generation_results.items():
            if result.get('status') == 'success':
                print(f"   ✅ {model}: {result.get('response_time', 0)}s")
            else:
                print(f"   ❌ {model}: {result.get('error', 'unknown')[:50]}...")
        
        # Производительность
        print(f"\n⚡ Производительность:")
        perf_results = self.results.get('performance_test', {})
        for model, stats in perf_results.items():
            print(f"   {model}: avg={stats['avg_time']}s, успешных={stats['successful_requests']}/5")
        
        # Сохранение результатов
        with open('litellm_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Результаты сохранены в litellm_test_results.json")

    def run_all_tests(self) -> None:
        """Запуск всех тестов"""
        print("🚀 Запуск полного тестирования LiteLLM...")
        print("="*60)
        
        self.test_all_models()
        self.test_dashboard_api()
        self.performance_benchmark()
        self.generate_report()

if __name__ == "__main__":
    tester = LiteLLMTester()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "models":
            tester.test_models_endpoint()
        elif sys.argv[1] == "generation":
            tester.test_all_models()
        elif sys.argv[1] == "performance":
            tester.performance_benchmark()
        elif sys.argv[1] == "dashboard":
            tester.test_dashboard_api()
        else:
            print("Доступные команды: models, generation, performance, dashboard")
    else:
        tester.run_all_tests()
