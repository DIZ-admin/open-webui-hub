#!/usr/bin/env python3
"""
Скрипт запуска комплексного A/B тестирования Open WebUI Hub
Выполняет полный цикл тестирования и генерирует отчеты
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime
import subprocess

# Добавляем путь к модулям тестирования
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ab_testing_framework import ABTestingFramework, TestConfig
from report_generator import ABTestingReportGenerator

def check_dependencies():
    """Проверка зависимостей для тестирования"""
    required_packages = [
        'aiohttp', 'docker', 'redis', 'psutil', 
        'matplotlib', 'seaborn', 'pandas', 'jinja2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Отсутствуют необходимые пакеты:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nУстановите их командой:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_services_availability():
    """Проверка доступности сервисов перед тестированием"""
    import requests
    
    services_to_check = [
        ("Hub API", "http://localhost:5003/api/health"),
        ("Dashboard API", "http://localhost:5002/api/health"),
        ("LiteLLM", "http://localhost:4000/health"),
        ("Nginx", "http://localhost:80"),
    ]
    
    print("🔍 Проверка доступности сервисов...")
    
    available_services = 0
    for service_name, url in services_to_check:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 301, 302]:
                print(f"   ✅ {service_name}: доступен")
                available_services += 1
            else:
                print(f"   ⚠️ {service_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {service_name}: недоступен ({e})")
    
    print(f"\n📊 Доступно сервисов: {available_services}/{len(services_to_check)}")
    
    if available_services < len(services_to_check) // 2:
        print("⚠️ Слишком много недоступных сервисов. Рекомендуется запустить систему:")
        print("   docker-compose -f compose.local.yml up -d")
        return False
    
    return True

def setup_test_environment():
    """Настройка тестовой среды"""
    # Создание директорий для тестов
    test_dirs = ['tests', 'tests/reports', 'tests/logs']
    
    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
    
    print("✅ Тестовая среда настроена")

async def run_comprehensive_testing(config: TestConfig, verbose: bool = False):
    """Запуск комплексного тестирования"""
    print("🚀 Запуск комплексного A/B тестирования Open WebUI Hub")
    print("=" * 60)
    
    # Инициализация фреймворка тестирования
    framework = ABTestingFramework(config)
    
    try:
        # Выполнение тестирования
        results = await framework.run_comprehensive_tests()
        
        # Сохранение результатов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"tests/ab_testing_results_{timestamp}.json"
        framework.save_results_to_file(results_file)
        
        # Генерация отчетов
        print("\n📊 Генерация отчетов...")
        report_generator = ABTestingReportGenerator(results_file)
        report_file = report_generator.generate_comprehensive_report()
        
        # Вывод краткого резюме
        print_test_summary(results)
        
        print(f"\n✅ Тестирование завершено успешно!")
        print(f"📄 Детальный отчет: {report_file}")
        print(f"📊 Результаты: {results_file}")
        
        return True, results_file, report_file
        
    except Exception as e:
        print(f"❌ Критическая ошибка тестирования: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False, None, None

def print_test_summary(results: dict):
    """Вывод краткого резюме тестирования"""
    print("\n" + "="*60)
    print("📊 КРАТКОЕ РЕЗЮМЕ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    # Здоровье системы
    health_data = results.get('health_check', {})
    if health_data:
        healthy_count = sum(1 for service in health_data.values() 
                          if isinstance(service, dict) and service.get('is_healthy', False))
        total_count = len(health_data)
        health_percentage = (healthy_count / total_count * 100) if total_count > 0 else 0
        
        print(f"🏥 Здоровье системы: {healthy_count}/{total_count} сервисов ({health_percentage:.1f}%)")
    
    # Производительность
    performance_data = results.get('performance_metrics', [])
    if performance_data:
        avg_response_times = []
        success_rates = []
        
        for metrics in performance_data:
            if isinstance(metrics, dict):
                avg_response_times.append(metrics.get('avg_response_time', 0))
                success_rates.append(metrics.get('success_rate', 0))
        
        if avg_response_times:
            avg_response = sum(avg_response_times) / len(avg_response_times)
            avg_success = sum(success_rates) / len(success_rates) * 100
            
            print(f"⚡ Производительность: {avg_response:.1f}ms среднее время отклика, {avg_success:.1f}% успешность")
    
    # Кэширование
    cache_data = results.get('cache_metrics', {})
    if cache_data:
        if hasattr(cache_data, 'hit_rate'):
            hit_rate = cache_data.hit_rate * 100
        else:
            hit_rate = cache_data.get('hit_rate', 0) * 100
        print(f"🔄 Кэширование: {hit_rate:.1f}% hit rate")
    
    # LLM производительность
    llm_data = results.get('llm_performance', {})
    if llm_data and isinstance(llm_data, dict):
        health_check = llm_data.get('health_check', {})
        model_listing = llm_data.get('model_listing', {})

        llm_healthy = health_check.get('success', False) if isinstance(health_check, dict) else False
        models_count = model_listing.get('total_models', 0) if isinstance(model_listing, dict) else 0

        print(f"🤖 LLM интеграция: {'✅ Работает' if llm_healthy else '❌ Проблемы'}, {models_count} моделей доступно")
    
    print(f"⏱️  Общее время тестирования: {results.get('test_duration', 0):.1f} секунд")
    print("="*60)

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='A/B тестирование Open WebUI Hub')
    parser.add_argument('--skip-checks', action='store_true', 
                       help='Пропустить проверки доступности сервисов')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод ошибок')
    parser.add_argument('--duration', type=int, default=60,
                       help='Длительность нагрузочного тестирования в секундах (по умолчанию: 60)')
    parser.add_argument('--concurrent', type=int, default=10,
                       help='Количество конкурентных запросов (по умолчанию: 10)')
    parser.add_argument('--target-response-time', type=int, default=50,
                       help='Целевое время отклика в миллисекундах (по умолчанию: 50)')
    parser.add_argument('--target-cache-hit-rate', type=float, default=0.90,
                       help='Целевой hit rate кэша (по умолчанию: 0.90)')
    
    args = parser.parse_args()
    
    print("🔧 Подготовка к A/B тестированию Open WebUI Hub")
    print(f"Параметры тестирования:")
    print(f"  - Длительность: {args.duration} секунд")
    print(f"  - Конкурентные запросы: {args.concurrent}")
    print(f"  - Целевое время отклика: {args.target_response_time}ms")
    print(f"  - Целевой cache hit rate: {args.target_cache_hit_rate*100}%")
    print()
    
    # Проверка зависимостей
    if not check_dependencies():
        return 1
    
    # Настройка тестовой среды
    setup_test_environment()
    
    # Проверка доступности сервисов
    if not args.skip_checks:
        if not check_services_availability():
            print("\n❌ Не все сервисы доступны. Используйте --skip-checks для принудительного запуска.")
            return 1
    
    # Конфигурация тестирования
    config = TestConfig(
        test_duration_seconds=args.duration,
        concurrent_requests=args.concurrent,
        target_response_time_ms=args.target_response_time,
        target_cache_hit_rate=args.target_cache_hit_rate
    )
    
    # Запуск тестирования
    try:
        success, results_file, report_file = asyncio.run(
            run_comprehensive_testing(config, args.verbose)
        )
        
        if success:
            print(f"\n🎉 A/B тестирование завершено успешно!")
            
            # Предложение открыть отчет
            if report_file and os.path.exists(report_file):
                try:
                    # Попытка открыть отчет в браузере
                    if sys.platform.startswith('darwin'):  # macOS
                        subprocess.run(['open', report_file])
                    elif sys.platform.startswith('linux'):  # Linux
                        subprocess.run(['xdg-open', report_file])
                    elif sys.platform.startswith('win'):  # Windows
                        subprocess.run(['start', report_file], shell=True)
                    
                    print(f"📖 Отчет открыт в браузере: {report_file}")
                except Exception:
                    print(f"📖 Отчет сохранен: {report_file}")
            
            return 0
        else:
            print(f"\n❌ A/B тестирование завершилось с ошибками")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Тестирование прервано пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
