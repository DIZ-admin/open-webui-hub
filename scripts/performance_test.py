#!/usr/bin/env python3
"""
Скрипт для тестирования производительности Dashboard API
Сравнивает старую и оптимизированную версии
"""

import time
import requests
import threading
import psutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

class PerformanceTester:
    def __init__(self):
        self.old_api_url = "http://localhost:5002"
        self.new_api_url = "http://localhost:5003"
        self.results = {
            'old_api': {'response_times': [], 'errors': 0, 'cpu_usage': []},
            'new_api': {'response_times': [], 'errors': 0, 'cpu_usage': []}
        }

    def get_process_cpu(self, process_name: str) -> float:
        """Получить использование CPU процессом"""
        try:
            result = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, text=True
            )
            
            for line in result.stdout.split('\n'):
                if process_name in line and 'python' in line:
                    parts = line.split()
                    if len(parts) > 2:
                        return float(parts[2])  # CPU %
            return 0.0
        except:
            return 0.0

    def test_endpoint(self, url: str, endpoint: str, num_requests: int = 10) -> Dict[str, Any]:
        """Тестировать конкретный endpoint"""
        response_times = []
        errors = 0
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(f"{url}{endpoint}", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
                else:
                    nonlocal errors
                    errors += 1
            except Exception:
                errors += 1

        # Выполняем запросы параллельно
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            for future in futures:
                future.result()

        return {
            'response_times': response_times,
            'errors': errors,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0
        }

    def run_load_test(self, api_name: str, base_url: str, duration: int = 30):
        """Запустить нагрузочный тест"""
        print(f"\n🔥 Нагрузочный тест {api_name} ({duration}s)")
        print("-" * 40)
        
        start_time = time.time()
        request_count = 0
        errors = 0
        response_times = []
        cpu_measurements = []
        
        # Определяем имя процесса для мониторинга CPU
        process_name = "dashboard-api.py" if "5002" in base_url else "dashboard-api-optimized.py"
        
        while time.time() - start_time < duration:
            # Делаем запросы к разным endpoints
            endpoints = ['/api/status', '/api/metrics', '/api/services']
            
            for endpoint in endpoints:
                try:
                    req_start = time.time()
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                    req_end = time.time()
                    
                    request_count += 1
                    response_times.append(req_end - req_start)
                    
                    if response.status_code != 200:
                        errors += 1
                        
                except Exception:
                    errors += 1
                    request_count += 1
            
            # Измеряем CPU
            cpu_usage = self.get_process_cpu(process_name)
            cpu_measurements.append(cpu_usage)
            
            time.sleep(0.5)  # Небольшая пауза между циклами
        
        # Вычисляем статистику
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        avg_cpu = sum(cpu_measurements) / len(cpu_measurements) if cpu_measurements else 0
        max_cpu = max(cpu_measurements) if cpu_measurements else 0
        
        success_rate = ((request_count - errors) / request_count * 100) if request_count > 0 else 0
        
        print(f"📊 Результаты:")
        print(f"   Запросов: {request_count}")
        print(f"   Ошибок: {errors}")
        print(f"   Успешность: {success_rate:.1f}%")
        print(f"   Среднее время ответа: {avg_response_time:.3f}s")
        print(f"   Мин время ответа: {min(response_times):.3f}s" if response_times else "   Мин время ответа: N/A")
        print(f"   Макс время ответа: {max(response_times):.3f}s" if response_times else "   Макс время ответа: N/A")
        print(f"   Среднее CPU: {avg_cpu:.1f}%")
        print(f"   Максимальное CPU: {max_cpu:.1f}%")
        print(f"   RPS: {request_count/duration:.1f}")
        
        return {
            'requests': request_count,
            'errors': errors,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'avg_cpu': avg_cpu,
            'max_cpu': max_cpu,
            'rps': request_count/duration
        }

    def test_specific_endpoints(self):
        """Тестировать конкретные endpoints"""
        print("\n🎯 ТЕСТИРОВАНИЕ КОНКРЕТНЫХ ENDPOINTS")
        print("=" * 50)
        
        endpoints = ['/api/status', '/api/metrics', '/api/services']
        
        for endpoint in endpoints:
            print(f"\n📍 Тестирование {endpoint}")
            print("-" * 30)
            
            # Тест старого API
            print("Старый API:")
            old_result = self.test_endpoint(self.old_api_url, endpoint, 5)
            print(f"  Среднее время: {old_result['avg_response_time']:.3f}s")
            print(f"  Ошибок: {old_result['errors']}/5")
            
            # Тест нового API
            print("Новый API:")
            new_result = self.test_endpoint(self.new_api_url, endpoint, 5)
            print(f"  Среднее время: {new_result['avg_response_time']:.3f}s")
            print(f"  Ошибок: {new_result['errors']}/5")
            
            # Сравнение
            if old_result['avg_response_time'] > 0 and new_result['avg_response_time'] > 0:
                improvement = (old_result['avg_response_time'] - new_result['avg_response_time']) / old_result['avg_response_time'] * 100
                print(f"  🚀 Улучшение: {improvement:.1f}%")

    def run_comparison_test(self):
        """Запустить сравнительный тест"""
        print("🚀 СРАВНИТЕЛЬНЫЙ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("=" * 60)
        
        # Тестируем конкретные endpoints
        self.test_specific_endpoints()
        
        # Нагрузочные тесты
        print("\n🔥 НАГРУЗОЧНЫЕ ТЕСТЫ")
        print("=" * 30)
        
        # Тест старого API
        old_results = self.run_load_test("СТАРЫЙ API", self.old_api_url, 20)
        
        # Небольшая пауза
        time.sleep(2)
        
        # Тест нового API
        new_results = self.run_load_test("НОВЫЙ API", self.new_api_url, 20)
        
        # Итоговое сравнение
        print("\n📊 ИТОГОВОЕ СРАВНЕНИЕ")
        print("=" * 40)
        
        metrics = [
            ('Среднее время ответа', 'avg_response_time', 's', True),
            ('Среднее CPU', 'avg_cpu', '%', True),
            ('Максимальное CPU', 'max_cpu', '%', True),
            ('RPS', 'rps', 'req/s', False),
            ('Успешность', 'success_rate', '%', False)
        ]
        
        for metric_name, metric_key, unit, lower_is_better in metrics:
            old_val = old_results.get(metric_key, 0)
            new_val = new_results.get(metric_key, 0)
            
            if old_val > 0:
                if lower_is_better:
                    improvement = (old_val - new_val) / old_val * 100
                    comparison = "лучше" if improvement > 0 else "хуже"
                else:
                    improvement = (new_val - old_val) / old_val * 100
                    comparison = "лучше" if improvement > 0 else "хуже"
                
                print(f"{metric_name}:")
                print(f"  Старый API: {old_val:.3f}{unit}")
                print(f"  Новый API:  {new_val:.3f}{unit}")
                print(f"  Изменение:  {abs(improvement):.1f}% {comparison}")
                print()

if __name__ == "__main__":
    tester = PerformanceTester()
    
    # Проверяем доступность API
    try:
        requests.get(tester.old_api_url + "/api/status", timeout=5)
        print("✅ Старый API доступен")
    except:
        print("❌ Старый API недоступен")
        exit(1)
    
    try:
        requests.get(tester.new_api_url + "/api/status", timeout=5)
        print("✅ Новый API доступен")
    except:
        print("❌ Новый API недоступен")
        exit(1)
    
    # Запускаем тесты
    tester.run_comparison_test()
