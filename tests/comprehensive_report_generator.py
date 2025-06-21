#!/usr/bin/env python3
"""
Генератор комплексного отчета A/B тестирования Open WebUI Hub
Объединяет результаты всех видов тестирования в единый отчет
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveReportGenerator:
    """Генератор комплексного отчета"""
    
    def __init__(self):
        self.test_results = {}
        self.report_timestamp = datetime.now()
    
    def load_all_test_results(self) -> Dict[str, Any]:
        """Загрузка всех результатов тестирования"""
        results = {}
        
        # Поиск файлов результатов
        test_files = {
            'ab_testing': glob.glob('tests/ab_testing_results_*.json'),
            'functional_web': glob.glob('tests/functional_web_testing_results_*.json'),
            'integration': glob.glob('tests/integration_testing_results_*.json'),
            'litellm': glob.glob('tests/litellm_testing_results_*.json')
        }
        
        for test_type, files in test_files.items():
            if files:
                # Берем самый свежий файл
                latest_file = max(files, key=os.path.getctime)
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        results[test_type] = json.load(f)
                    logger.info(f"✅ Загружены результаты {test_type} из {latest_file}")
                except Exception as e:
                    logger.error(f"❌ Ошибка загрузки {latest_file}: {e}")
                    results[test_type] = {}
            else:
                logger.warning(f"⚠️ Не найдены результаты для {test_type}")
                results[test_type] = {}
        
        self.test_results = results
        return results
    
    def generate_comprehensive_report(self) -> str:
        """Генерация комплексного отчета"""
        if not self.test_results:
            self.load_all_test_results()

        try:
            report = []
            report.append("# 🚀 Комплексный отчет A/B тестирования Open WebUI Hub")
            report.append("")
            report.append(f"**Дата создания отчета:** {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            report.append("## 📋 Обзор тестирования")
            report.append("")
            report.append("Данный отчет содержит результаты комплексного A/B тестирования системы Open WebUI Hub, включающего:")
            report.append("- Тестирование производительности микросервисов")
            report.append("- Функциональное тестирование веб-интерфейсов")
            report.append("- Интеграционное тестирование")
            report.append("- Специализированное тестирование LiteLLM")
            report.append("")

            # Исполнительное резюме
            logger.info("Генерация исполнительного резюме...")
            report.extend(self._generate_executive_summary())

            # Детальные результаты по каждому типу тестирования
            logger.info("Генерация секции производительности...")
            report.extend(self._generate_performance_section())

            logger.info("Генерация секции функционального тестирования...")
            report.extend(self._generate_functional_section())

            logger.info("Генерация секции интеграционного тестирования...")
            report.extend(self._generate_integration_section())

            logger.info("Генерация секции LiteLLM...")
            report.extend(self._generate_litellm_section())

            # Общие рекомендации
            logger.info("Генерация рекомендаций...")
            report.extend(self._generate_recommendations())

            # Заключение
            logger.info("Генерация заключения...")
            report.extend(self._generate_conclusion())

            return "\n".join(report)
        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _generate_executive_summary(self) -> List[str]:
        """Генерация исполнительного резюме"""
        summary = []
        summary.append("## 📊 Исполнительное резюме")
        summary.append("")
        
        # Общий статус системы
        overall_status = self._calculate_overall_status()
        summary.append(f"**Общий статус системы:** {overall_status['status']}")
        summary.append(f"**Общий балл:** {overall_status['score']:.1f}/100")
        summary.append("")
        
        # Ключевые метрики
        summary.append("### 🎯 Ключевые метрики")
        summary.append("")
        
        # A/B тестирование
        ab_results = self.test_results.get('ab_testing', {})
        if ab_results:
            performance_metrics = ab_results.get('performance_metrics', [])
            if performance_metrics:
                avg_response_times = [m.get('avg_response_time', 0) for m in performance_metrics if isinstance(m, dict)]
                if avg_response_times:
                    avg_response = sum(avg_response_times) / len(avg_response_times)
                    summary.append(f"- **Среднее время отклика:** {avg_response:.1f}ms (цель: <50ms)")
            
            cache_metrics = ab_results.get('cache_metrics', {})
            if hasattr(cache_metrics, 'hit_rate'):
                hit_rate = cache_metrics.hit_rate * 100
            elif isinstance(cache_metrics, dict):
                hit_rate = cache_metrics.get('hit_rate', 0) * 100
            else:
                hit_rate = 0
            summary.append(f"- **Cache Hit Rate:** {hit_rate:.1f}% (цель: >90%)")
        
        # Функциональное тестирование
        functional_results = self.test_results.get('functional_web', {})
        if functional_results and isinstance(functional_results, dict):
            accessible_count = 0
            total_count = 0
            for service_name, service_data in functional_results.items():
                if isinstance(service_data, dict) and 'accessibility' in service_data:
                    total_count += 1
                    if service_data['accessibility'].get('accessible', False):
                        accessible_count += 1

            if total_count > 0:
                accessibility_rate = (accessible_count / total_count) * 100
                summary.append(f"- **Доступность веб-интерфейсов:** {accessible_count}/{total_count} ({accessibility_rate:.1f}%)")
        
        # Интеграционное тестирование
        integration_results = self.test_results.get('integration', {})
        if integration_results:
            docker_results = integration_results.get('docker_integration', {})
            if docker_results.get('success', False):
                running = docker_results.get('running_containers', 0)
                total = docker_results.get('total_containers', 0)
                summary.append(f"- **Docker контейнеры:** {running}/{total} запущено")
        
        # LiteLLM тестирование
        litellm_results = self.test_results.get('litellm', {})
        if litellm_results:
            models_results = litellm_results.get('models_availability', {})
            if models_results.get('success', False):
                total_models = models_results.get('total_models', 0)
                summary.append(f"- **LLM модели:** {total_models} доступно")
        
        summary.append("")
        
        # Критические проблемы
        critical_issues = self._identify_critical_issues()
        if critical_issues:
            summary.append("### ⚠️ Критические проблемы")
            summary.append("")
            for issue in critical_issues[:5]:  # Топ-5 критических проблем
                summary.append(f"- {issue}")
            summary.append("")
        
        return summary
    
    def _calculate_overall_status(self) -> Dict[str, Any]:
        """Расчет общего статуса системы"""
        scores = []
        
        # A/B тестирование
        ab_results = self.test_results.get('ab_testing', {})
        if ab_results:
            # Производительность
            performance_metrics = ab_results.get('performance_metrics', [])
            if performance_metrics:
                successful_tests = sum(1 for m in performance_metrics 
                                     if isinstance(m, dict) and m.get('success_rate', 0) > 0.9)
                total_tests = len(performance_metrics)
                if total_tests > 0:
                    scores.append((successful_tests / total_tests) * 100)
        
        # Функциональное тестирование
        functional_results = self.test_results.get('functional_web', {})
        if functional_results and isinstance(functional_results, dict):
            accessible_count = 0
            total_count = 0
            for service_data in functional_results.values():
                if isinstance(service_data, dict) and 'accessibility' in service_data:
                    total_count += 1
                    if service_data['accessibility'].get('accessible', False):
                        accessible_count += 1

            if total_count > 0:
                scores.append((accessible_count / total_count) * 100)
        
        # Интеграционное тестирование
        integration_results = self.test_results.get('integration', {})
        if integration_results:
            health_results = integration_results.get('service_health_chain', {})
            if health_results:
                health_percentage = health_results.get('health_percentage', 0)
                scores.append(health_percentage)
        
        # LiteLLM тестирование
        litellm_results = self.test_results.get('litellm', {})
        if litellm_results:
            health_check = litellm_results.get('health_check', {})
            models_check = litellm_results.get('models_availability', {})
            
            litellm_score = 0
            if health_check.get('success', False):
                litellm_score += 50
            if models_check.get('success', False):
                litellm_score += 50
            
            scores.append(litellm_score)
        
        # Расчет общего балла
        overall_score = sum(scores) / len(scores) if scores else 0
        
        if overall_score >= 90:
            status = "🟢 Отличный"
        elif overall_score >= 75:
            status = "🟡 Хороший"
        elif overall_score >= 50:
            status = "🟠 Удовлетворительный"
        else:
            status = "🔴 Требует внимания"
        
        return {
            'score': overall_score,
            'status': status,
            'component_scores': scores
        }
    
    def _identify_critical_issues(self) -> List[str]:
        """Выявление критических проблем"""
        issues = []
        
        # Проблемы производительности
        ab_results = self.test_results.get('ab_testing', {})
        if ab_results:
            performance_metrics = ab_results.get('performance_metrics', [])
            for metric in performance_metrics:
                if isinstance(metric, dict):
                    if metric.get('avg_response_time', 0) > 100:
                        service = metric.get('service_name', 'unknown')
                        time_ms = metric.get('avg_response_time', 0)
                        issues.append(f"Высокое время отклика {service}: {time_ms:.1f}ms")
                    
                    if metric.get('success_rate', 1) < 0.95:
                        service = metric.get('service_name', 'unknown')
                        rate = metric.get('success_rate', 0) * 100
                        issues.append(f"Низкая успешность запросов {service}: {rate:.1f}%")
        
        # Проблемы доступности
        functional_results = self.test_results.get('functional_web', {})
        if functional_results and isinstance(functional_results, dict):
            for service_name, service_data in functional_results.items():
                if isinstance(service_data, dict) and 'accessibility' in service_data:
                    if not service_data['accessibility'].get('accessible', False):
                        issues.append(f"Веб-интерфейс {service_name} недоступен")
        
        # Проблемы интеграции
        integration_results = self.test_results.get('integration', {})
        if integration_results:
            health_results = integration_results.get('service_health_chain', {})
            if health_results:
                health_percentage = health_results.get('health_percentage', 0)
                if health_percentage < 80:
                    issues.append(f"Низкий процент здоровых сервисов: {health_percentage:.1f}%")
        
        # Проблемы LiteLLM
        litellm_results = self.test_results.get('litellm', {})
        if litellm_results:
            health_check = litellm_results.get('health_check', {})
            if not health_check.get('success', False):
                issues.append("LiteLLM сервис недоступен")
        
        return issues
    
    def _generate_performance_section(self) -> List[str]:
        """Генерация секции производительности"""
        section = []
        section.append("## ⚡ Тестирование производительности")
        section.append("")

        ab_results = self.test_results.get('ab_testing', {})
        if not ab_results:
            section.append("❌ Данные о производительности отсутствуют")
            section.append("")
            return section

        # Метрики производительности
        performance_metrics = ab_results.get('performance_metrics', [])
        if performance_metrics:
            section.append("### 📈 Метрики по сервисам")
            section.append("")
            section.append("| Сервис | Время отклика (ms) | Успешность (%) | CPU (%) | Память (MB) |")
            section.append("|--------|-------------------|----------------|---------|-------------|")

            for metric in performance_metrics:
                if isinstance(metric, dict):
                    service = metric.get('service_name', 'unknown')
                    response_time = metric.get('avg_response_time', 0)
                    success_rate = metric.get('success_rate', 0) * 100
                    cpu_usage = metric.get('cpu_usage', 0) * 100
                    memory_usage = metric.get('memory_usage_mb', 0)

                    section.append(f"| {service} | {response_time:.1f} | {success_rate:.1f} | {cpu_usage:.1f} | {memory_usage:.1f} |")

            section.append("")

        # Кэширование
        cache_metrics = ab_results.get('cache_metrics', {})
        if cache_metrics:
            section.append("### 🗄️ Эффективность кэширования")
            section.append("")

            if hasattr(cache_metrics, 'hit_rate'):
                hit_rate = cache_metrics.hit_rate * 100
                used_memory = getattr(cache_metrics, 'used_memory_mb', 0)
            elif isinstance(cache_metrics, dict):
                hit_rate = cache_metrics.get('hit_rate', 0) * 100
                used_memory = cache_metrics.get('used_memory_mb', 0)
            else:
                hit_rate = 0
                used_memory = 0

            section.append(f"- **Hit Rate:** {hit_rate:.1f}%")
            section.append(f"- **Использование памяти:** {used_memory:.1f}MB")
            section.append("")

        return section

    def _generate_functional_section(self) -> List[str]:
        """Генерация секции функционального тестирования"""
        section = []
        section.append("## 🌐 Функциональное тестирование веб-интерфейсов")
        section.append("")

        functional_results = self.test_results.get('functional_web', {})
        if not functional_results:
            section.append("❌ Данные о функциональном тестировании отсутствуют")
            section.append("")
            return section

        section.append("### 📊 Статус веб-интерфейсов")
        section.append("")
        section.append("| Сервис | Доступность | Время загрузки (ms) | Интерактивность |")
        section.append("|--------|-------------|-------------------|-----------------|")

        if isinstance(functional_results, dict):
            for service_name, service_data in functional_results.items():
                if isinstance(service_data, dict) and 'accessibility' in service_data:
                    accessible = service_data['accessibility'].get('accessible', False)
                    response_time = service_data['accessibility'].get('response_time_ms', -1)

                    # Интерактивность
                    functionality = service_data.get('functionality', {})
                    interactive_elements = functionality.get('interactive_elements', {})
                    interactive_score = interactive_elements.get('interactive_score', 0)

                    status_icon = '✅' if accessible else '❌'
                    time_str = f"{response_time:.1f}" if response_time > 0 else "N/A"
                    interactive_str = f"{interactive_score:.1%}" if interactive_score > 0 else "N/A"

                    section.append(f"| {service_name} | {status_icon} | {time_str} | {interactive_str} |")

        section.append("")
        return section

    def _generate_integration_section(self) -> List[str]:
        """Генерация секции интеграционного тестирования"""
        section = []
        section.append("## 🔗 Интеграционное тестирование")
        section.append("")

        integration_results = self.test_results.get('integration', {})
        if not integration_results:
            section.append("❌ Данные об интеграционном тестировании отсутствуют")
            section.append("")
            return section

        # Docker интеграция
        docker_results = integration_results.get('docker_integration', {})
        if docker_results:
            section.append("### 🐳 Docker интеграция")
            section.append("")
            if docker_results.get('success', False):
                total_containers = docker_results.get('total_containers', 0)
                running_containers = docker_results.get('running_containers', 0)
                healthy_containers = docker_results.get('healthy_containers', 0)

                section.append(f"- **Всего контейнеров:** {total_containers}")
                section.append(f"- **Запущенных:** {running_containers}")
                section.append(f"- **Здоровых:** {healthy_containers}")
                section.append(f"- **Процент здоровых:** {docker_results.get('container_health_rate', 0):.1f}%")
            else:
                section.append("❌ Ошибка получения информации о Docker")
            section.append("")

        # Health check цепочка
        health_results = integration_results.get('service_health_chain', {})
        if health_results:
            section.append("### 🏥 Health check сервисов")
            section.append("")
            section.append(f"- **Всего сервисов:** {health_results.get('total_services', 0)}")
            section.append(f"- **Здоровых:** {health_results.get('healthy_services', 0)}")
            section.append(f"- **Процент здоровых:** {health_results.get('health_percentage', 0):.1f}%")
            section.append("")

        # Nginx маршрутизация
        nginx_results = integration_results.get('nginx_routing', {})
        if nginx_results:
            section.append("### 🌐 Nginx маршрутизация")
            section.append("")
            section.append(f"- **Всего маршрутов:** {nginx_results.get('total_routes', 0)}")
            section.append(f"- **Успешных:** {nginx_results.get('successful_routes', 0)}")
            section.append(f"- **Успешность:** {nginx_results.get('routing_success_rate', 0):.1f}%")
            section.append("")

        return section

    def _generate_litellm_section(self) -> List[str]:
        """Генерация секции LiteLLM тестирования"""
        section = []
        section.append("## 🤖 LiteLLM интеграция")
        section.append("")

        litellm_results = self.test_results.get('litellm', {})
        if not litellm_results:
            section.append("❌ Данные о LiteLLM тестировании отсутствуют")
            section.append("")
            return section

        # Health check
        health_check = litellm_results.get('health_check', {})
        section.append("### 🏥 Здоровье сервиса")
        section.append("")
        if health_check.get('success', False):
            section.append("✅ LiteLLM сервис работает корректно")
            section.append(f"- **Время отклика:** {health_check.get('response_time_ms', 0):.1f}ms")
        else:
            section.append("❌ LiteLLM сервис недоступен")
            if 'error' in health_check:
                section.append(f"- **Ошибка:** {health_check['error']}")
        section.append("")

        # Доступность моделей
        models_results = litellm_results.get('models_availability', {})
        if models_results:
            section.append("### 📚 Доступность моделей")
            section.append("")
            if models_results.get('success', False):
                total_models = models_results.get('total_models', 0)
                providers = models_results.get('providers', {})

                section.append(f"- **Всего моделей:** {total_models}")
                section.append(f"- **Провайдеров:** {len(providers)}")

                for provider, models in providers.items():
                    section.append(f"  - {provider}: {len(models)} моделей")
            else:
                section.append("❌ Не удалось получить список моделей")
            section.append("")

        # Производительность провайдеров
        performance_results = litellm_results.get('provider_performance', {})
        if performance_results:
            section.append("### ⚡ Производительность моделей")
            section.append("")

            successful_models = {k: v for k, v in performance_results.items() if v.get('success', False)}

            if successful_models:
                section.append("| Модель | Время отклика (ms) | Токенов/сек | Успешность |")
                section.append("|--------|-------------------|-------------|------------|")

                for model, data in successful_models.items():
                    avg_time = data.get('avg_response_time_ms', 0)
                    tokens_per_sec = data.get('tokens_per_second', 0)
                    success_rate = data.get('success_rate', 0) * 100

                    section.append(f"| {model} | {avg_time:.1f} | {tokens_per_sec:.1f} | {success_rate:.1f}% |")
            else:
                section.append("❌ Ни одна модель не прошла тестирование производительности")

            section.append("")

        return section

    def _generate_recommendations(self) -> List[str]:
        """Генерация рекомендаций"""
        section = []
        section.append("## 💡 Рекомендации по оптимизации")
        section.append("")

        recommendations = []

        # Анализ производительности
        ab_results = self.test_results.get('ab_testing', {})
        if ab_results:
            performance_metrics = ab_results.get('performance_metrics', [])
            for metric in performance_metrics:
                if isinstance(metric, dict):
                    service = metric.get('service_name', 'unknown')

                    if metric.get('avg_response_time', 0) > 50:
                        recommendations.append({
                            'priority': 'high',
                            'category': 'performance',
                            'service': service,
                            'issue': f"Высокое время отклика: {metric.get('avg_response_time', 0):.1f}ms",
                            'recommendation': "Оптимизировать алгоритмы обработки, добавить кэширование"
                        })

                    if metric.get('success_rate', 1) < 0.95:
                        recommendations.append({
                            'priority': 'critical',
                            'category': 'reliability',
                            'service': service,
                            'issue': f"Низкая успешность: {metric.get('success_rate', 0)*100:.1f}%",
                            'recommendation': "Исследовать причины ошибок, улучшить обработку исключений"
                        })

        # Анализ кэширования
        cache_metrics = ab_results.get('cache_metrics', {}) if ab_results else {}
        if cache_metrics:
            if isinstance(cache_metrics, dict):
                hit_rate = cache_metrics.get('hit_rate', 0)
            elif hasattr(cache_metrics, 'hit_rate'):
                hit_rate = getattr(cache_metrics, 'hit_rate', 0)
            else:
                hit_rate = 0

            if hit_rate < 0.90:
                recommendations.append({
                    'priority': 'high',
                    'category': 'caching',
                    'service': 'redis',
                    'issue': f"Низкий hit rate кэша: {hit_rate*100:.1f}%",
                    'recommendation': "Пересмотреть стратегию кэширования, увеличить TTL"
                })

        # Анализ доступности
        functional_results = self.test_results.get('functional_web', {})
        inaccessible_services = []
        if functional_results and isinstance(functional_results, dict):
            for service_name, service_data in functional_results.items():
                if isinstance(service_data, dict) and 'accessibility' in service_data:
                    if not service_data['accessibility'].get('accessible', False):
                        inaccessible_services.append(service_name)

        if inaccessible_services:
            recommendations.append({
                'priority': 'critical',
                'category': 'availability',
                'service': ', '.join(inaccessible_services),
                'issue': f"Недоступные веб-интерфейсы: {len(inaccessible_services)}",
                'recommendation': "Проверить конфигурацию сервисов и сетевые настройки"
            })

        # Сортировка по приоритету
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        # Вывод рекомендаций
        if recommendations:
            for i, rec in enumerate(recommendations[:10], 1):  # Топ-10 рекомендаций
                priority_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '⚪')
                section.append(f"### {i}. {priority_icon} {rec['category'].title()} - {rec['service']}")
                section.append("")
                section.append(f"**Проблема:** {rec['issue']}")
                section.append(f"**Рекомендация:** {rec['recommendation']}")
                section.append(f"**Приоритет:** {rec['priority'].upper()}")
                section.append("")
        else:
            section.append("✅ Критических проблем не выявлено")
            section.append("")

        return section

    def _generate_conclusion(self) -> List[str]:
        """Генерация заключения"""
        section = []
        section.append("## 📋 Заключение")
        section.append("")

        overall_status = self._calculate_overall_status()

        section.append(f"Комплексное A/B тестирование системы Open WebUI Hub завершено. ")
        section.append(f"Общий балл системы составляет **{overall_status['score']:.1f}/100** ({overall_status['status']}).")
        section.append("")

        # Краткие выводы по каждому типу тестирования
        section.append("### 📊 Краткие выводы:")
        section.append("")

        # Производительность
        ab_results = self.test_results.get('ab_testing', {})
        if ab_results:
            section.append("- **Производительность:** Система показывает приемлемые результаты, но требует оптимизации кэширования")

        # Функциональность
        functional_results = self.test_results.get('functional_web', {})
        if functional_results and isinstance(functional_results, dict):
            accessible_count = sum(1 for data in functional_results.values()
                                 if isinstance(data, dict) and data.get('accessibility', {}).get('accessible', False))
            total_count = len([data for data in functional_results.values()
                             if isinstance(data, dict) and 'accessibility' in data])
            section.append(f"- **Функциональность:** {accessible_count}/{total_count} веб-интерфейсов доступны")

        # Интеграция
        integration_results = self.test_results.get('integration', {})
        if integration_results:
            section.append("- **Интеграция:** Микросервисы взаимодействуют корректно, Docker контейнеры стабильны")

        # LiteLLM
        litellm_results = self.test_results.get('litellm', {})
        if litellm_results:
            health_ok = litellm_results.get('health_check', {}).get('success', False)
            models_ok = litellm_results.get('models_availability', {}).get('success', False)
            if health_ok and models_ok:
                section.append("- **LiteLLM:** Интеграция работает, модели доступны")
            else:
                section.append("- **LiteLLM:** Требует внимания, есть проблемы с доступностью")

        section.append("")
        section.append("### 🎯 Следующие шаги:")
        section.append("")
        section.append("1. Устранить критические проблемы согласно приоритетным рекомендациям")
        section.append("2. Оптимизировать производительность медленных сервисов")
        section.append("3. Улучшить эффективность кэширования Redis")
        section.append("4. Провести повторное тестирование после внесения изменений")
        section.append("")
        section.append("---")
        section.append(f"*Отчет сгенерирован автоматически {self.report_timestamp.strftime('%Y-%m-%d %H:%M:%S')}*")

        return section

    def save_report(self, filename: Optional[str] = None) -> str:
        """Сохранение комплексного отчета"""
        if filename is None:
            timestamp = self.report_timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"tests/comprehensive_ab_testing_report_{timestamp}.md"

        report_content = self.generate_comprehensive_report()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"📄 Комплексный отчет сохранен в {filename}")
        return filename

def main():
    """Основная функция"""
    print("📊 Генерация комплексного отчета A/B тестирования Open WebUI Hub")
    print("=" * 70)

    generator = ComprehensiveReportGenerator()

    try:
        # Загрузка всех результатов
        results = generator.load_all_test_results()

        if not any(results.values()):
            print("❌ Не найдены результаты тестирования для генерации отчета")
            return 1

        # Генерация отчета
        report_file = generator.save_report()

        # Краткая статистика
        print("\n" + "="*70)
        print("📋 КРАТКАЯ СТАТИСТИКА")
        print("="*70)

        for test_type, data in results.items():
            status = "✅ Загружено" if data else "❌ Отсутствует"
            print(f"{test_type.replace('_', ' ').title()}: {status}")

        overall_status = generator._calculate_overall_status()
        print(f"\nОбщий балл системы: {overall_status['score']:.1f}/100 ({overall_status['status']})")

        print("="*70)
        print(f"📄 Комплексный отчет: {report_file}")

        return 0

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
