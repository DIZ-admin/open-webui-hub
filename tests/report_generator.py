#!/usr/bin/env python3
"""
Генератор детального отчета A/B тестирования Open WebUI Hub
Создает комплексный отчет с анализом производительности и рекомендациями
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from jinja2 import Template

class ABTestingReportGenerator:
    """Генератор отчетов A/B тестирования"""
    
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.results = self._load_results()
        self.report_dir = "tests/reports"
        os.makedirs(self.report_dir, exist_ok=True)
    
    def _load_results(self) -> Dict[str, Any]:
        """Загрузка результатов тестирования"""
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Ошибка загрузки результатов: {e}")
    
    def generate_comprehensive_report(self) -> str:
        """Генерация комплексного отчета"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{self.report_dir}/ab_testing_report_{timestamp}.html"
        
        # Анализ результатов
        analysis = self._analyze_results()
        
        # Генерация графиков
        charts = self._generate_charts()
        
        # Создание HTML отчета
        html_content = self._create_html_report(analysis, charts)
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Создание текстового резюме
        summary_filename = f"{self.report_dir}/ab_testing_summary_{timestamp}.md"
        summary_content = self._create_summary_report(analysis)
        
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"📊 Детальный отчет создан: {report_filename}")
        print(f"📋 Краткое резюме создано: {summary_filename}")
        
        return report_filename
    
    def _analyze_results(self) -> Dict[str, Any]:
        """Анализ результатов тестирования"""
        analysis = {
            'overall_health': self._analyze_system_health(),
            'performance_analysis': self._analyze_performance(),
            'cache_analysis': self._analyze_caching(),
            'integration_analysis': self._analyze_integration(),
            'llm_analysis': self._analyze_llm_performance(),
            'recommendations': self._generate_recommendations(),
            'compliance': self._check_target_compliance()
        }
        
        return analysis
    
    def _analyze_system_health(self) -> Dict[str, Any]:
        """Анализ здоровья системы"""
        health_data = self.results.get('health_check', {})
        
        total_services = len(health_data)
        healthy_services = sum(1 for service in health_data.values() 
                             if isinstance(service, dict) and service.get('is_healthy', False))
        
        health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        service_details = []
        for service_name, metrics in health_data.items():
            if isinstance(metrics, dict):
                service_details.append({
                    'name': service_name,
                    'healthy': metrics.get('is_healthy', False),
                    'response_time': metrics.get('response_time_ms', -1),
                    'container_status': metrics.get('container_status', 'unknown'),
                    'error': metrics.get('error_message')
                })
        
        return {
            'total_services': total_services,
            'healthy_services': healthy_services,
            'health_percentage': health_percentage,
            'service_details': service_details,
            'status': 'excellent' if health_percentage >= 95 else 
                     'good' if health_percentage >= 80 else 
                     'warning' if health_percentage >= 60 else 'critical'
        }
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Анализ производительности"""
        performance_data = self.results.get('performance_metrics', [])
        
        if not performance_data:
            return {'status': 'no_data', 'message': 'Данные о производительности отсутствуют'}
        
        # Агрегация метрик по сервисам
        service_performance = {}
        total_avg_response = 0
        total_success_rate = 0
        
        for metrics in performance_data:
            if isinstance(metrics, dict):
                service_name = metrics.get('service_name', 'unknown')
                
                service_performance[service_name] = {
                    'avg_response_time': metrics.get('avg_response_time', 0),
                    'p95_response_time': metrics.get('p95_response_time', 0),
                    'p99_response_time': metrics.get('p99_response_time', 0),
                    'success_rate': metrics.get('success_rate', 0),
                    'total_requests': metrics.get('total_requests', 0),
                    'error_count': metrics.get('error_count', 0),
                    'cpu_usage': metrics.get('cpu_usage', 0),
                    'memory_usage_mb': metrics.get('memory_usage_mb', 0)
                }
                
                total_avg_response += metrics.get('avg_response_time', 0)
                total_success_rate += metrics.get('success_rate', 0)
        
        avg_response_time = total_avg_response / len(performance_data) if performance_data else 0
        avg_success_rate = total_success_rate / len(performance_data) if performance_data else 0
        
        # Определение статуса производительности
        performance_status = 'excellent' if avg_response_time <= 50 and avg_success_rate >= 0.95 else \
                           'good' if avg_response_time <= 100 and avg_success_rate >= 0.90 else \
                           'warning' if avg_response_time <= 200 and avg_success_rate >= 0.80 else 'critical'
        
        return {
            'status': performance_status,
            'avg_response_time': avg_response_time,
            'avg_success_rate': avg_success_rate,
            'service_performance': service_performance,
            'total_services_tested': len(performance_data)
        }
    
    def _analyze_caching(self) -> Dict[str, Any]:
        """Анализ эффективности кэширования"""
        cache_data = self.results.get('cache_metrics', {})
        
        if not cache_data:
            return {'status': 'no_data', 'message': 'Данные о кэшировании отсутствуют'}
        
        hit_rate = cache_data.get('hit_rate', 0)
        miss_rate = cache_data.get('miss_rate', 0)
        used_memory_mb = cache_data.get('used_memory_mb', 0)
        ops_per_second = cache_data.get('operations_per_second', 0)
        
        # Определение статуса кэширования
        cache_status = 'excellent' if hit_rate >= 0.90 else \
                      'good' if hit_rate >= 0.75 else \
                      'warning' if hit_rate >= 0.50 else 'critical'
        
        return {
            'status': cache_status,
            'hit_rate': hit_rate,
            'miss_rate': miss_rate,
            'hit_rate_percentage': hit_rate * 100,
            'used_memory_mb': used_memory_mb,
            'operations_per_second': ops_per_second,
            'efficiency': 'высокая' if hit_rate >= 0.90 else 
                         'средняя' if hit_rate >= 0.75 else 'низкая'
        }
    
    def _analyze_integration(self) -> Dict[str, Any]:
        """Анализ интеграционного тестирования"""
        integration_data = self.results.get('integration_results', {})
        
        if not integration_data:
            return {'status': 'no_data', 'message': 'Данные об интеграции отсутствуют'}
        
        # Анализ Nginx маршрутизации
        nginx_results = integration_data.get('nginx_routing', {})
        nginx_success_count = sum(1 for result in nginx_results.values() 
                                if isinstance(result, dict) and result.get('success', False))
        nginx_total = len(nginx_results)
        
        # Анализ service discovery
        discovery_results = integration_data.get('service_discovery', {})
        discovery_success = discovery_results.get('success', False)
        
        # Анализ health check цепочки
        health_chain = integration_data.get('health_checks', {})
        health_chain_success = health_chain.get('success', False)
        health_percentage = health_chain.get('health_percentage', 0)
        
        # Анализ Docker интеграции
        docker_results = integration_data.get('docker_integration', {})
        docker_success = docker_results.get('success', False)
        running_containers = docker_results.get('running_containers', 0)
        total_containers = docker_results.get('total_containers', 0)
        
        # Общий статус интеграции
        integration_score = 0
        if nginx_total > 0:
            integration_score += (nginx_success_count / nginx_total) * 25
        if discovery_success:
            integration_score += 25
        if health_chain_success:
            integration_score += 25
        if docker_success:
            integration_score += 25
        
        integration_status = 'excellent' if integration_score >= 90 else \
                           'good' if integration_score >= 75 else \
                           'warning' if integration_score >= 50 else 'critical'
        
        return {
            'status': integration_status,
            'integration_score': integration_score,
            'nginx_routing': {
                'success_rate': (nginx_success_count / nginx_total * 100) if nginx_total > 0 else 0,
                'details': nginx_results
            },
            'service_discovery': {
                'success': discovery_success,
                'discovered_services': discovery_results.get('discovered_services', 0)
            },
            'health_chain': {
                'success': health_chain_success,
                'health_percentage': health_percentage,
                'healthy_services': health_chain.get('healthy_services', 0),
                'total_services': health_chain.get('total_services', 0)
            },
            'docker_integration': {
                'success': docker_success,
                'running_containers': running_containers,
                'total_containers': total_containers,
                'container_health_rate': (running_containers / total_containers * 100) if total_containers > 0 else 0
            }
        }
    
    def _analyze_llm_performance(self) -> Dict[str, Any]:
        """Анализ производительности LLM"""
        llm_data = self.results.get('llm_performance', {})
        
        if not llm_data:
            return {'status': 'no_data', 'message': 'Данные о LLM производительности отсутствуют'}
        
        # Анализ здоровья LiteLLM
        health_check = llm_data.get('health_check', {})
        health_success = health_check.get('success', False)
        
        # Анализ списка моделей
        model_listing = llm_data.get('model_listing', {})
        models_available = model_listing.get('total_models', 0)
        
        # Анализ производительности провайдеров
        provider_performance = llm_data.get('provider_performance', {})
        successful_providers = sum(1 for result in provider_performance.values() 
                                 if isinstance(result, dict) and result.get('success', False))
        total_providers = len(provider_performance)
        
        # Анализ fallback механизмов
        fallback_results = llm_data.get('fallback_mechanism', {})
        fallback_tested = fallback_results.get('fallback_tested', False)
        
        # Общий статус LLM
        llm_score = 0
        if health_success:
            llm_score += 30
        if models_available > 0:
            llm_score += 30
        if total_providers > 0:
            llm_score += (successful_providers / total_providers) * 30
        if fallback_tested:
            llm_score += 10
        
        llm_status = 'excellent' if llm_score >= 90 else \
                    'good' if llm_score >= 75 else \
                    'warning' if llm_score >= 50 else 'critical'
        
        return {
            'status': llm_status,
            'llm_score': llm_score,
            'health_check': health_success,
            'models_available': models_available,
            'provider_success_rate': (successful_providers / total_providers * 100) if total_providers > 0 else 0,
            'fallback_tested': fallback_tested,
            'provider_details': provider_performance
        }

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Генерация рекомендаций по оптимизации"""
        recommendations = []

        # Анализ производительности для рекомендаций
        performance_data = self.results.get('performance_metrics', [])
        cache_data = self.results.get('cache_metrics', {})
        health_data = self.results.get('health_check', {})

        # Рекомендации по производительности
        for metrics in performance_data:
            if isinstance(metrics, dict):
                service_name = metrics.get('service_name', 'unknown')
                avg_response = metrics.get('avg_response_time', 0)
                success_rate = metrics.get('success_rate', 0)
                cpu_usage = metrics.get('cpu_usage', 0)
                memory_usage = metrics.get('memory_usage_mb', 0)

                if avg_response > 50:
                    recommendations.append({
                        'priority': 'high',
                        'category': 'performance',
                        'service': service_name,
                        'issue': f'Высокое время отклика: {avg_response:.1f}ms',
                        'recommendation': 'Оптимизировать алгоритмы обработки запросов, добавить кэширование',
                        'target': '< 50ms',
                        'impact': 'Улучшение пользовательского опыта'
                    })

                if success_rate < 0.95:
                    recommendations.append({
                        'priority': 'critical',
                        'category': 'reliability',
                        'service': service_name,
                        'issue': f'Низкая успешность запросов: {success_rate:.1%}',
                        'recommendation': 'Исследовать причины ошибок, улучшить обработку исключений',
                        'target': '> 95%',
                        'impact': 'Повышение надежности системы'
                    })

                if cpu_usage > 0.05:  # 5%
                    recommendations.append({
                        'priority': 'medium',
                        'category': 'resources',
                        'service': service_name,
                        'issue': f'Высокое использование CPU: {cpu_usage:.1%}',
                        'recommendation': 'Оптимизировать алгоритмы, рассмотреть горизонтальное масштабирование',
                        'target': '< 5%',
                        'impact': 'Снижение нагрузки на систему'
                    })

                if memory_usage > 100:  # 100MB
                    recommendations.append({
                        'priority': 'medium',
                        'category': 'resources',
                        'service': service_name,
                        'issue': f'Высокое использование памяти: {memory_usage:.1f}MB',
                        'recommendation': 'Оптимизировать использование памяти, проверить утечки',
                        'target': '< 100MB',
                        'impact': 'Эффективное использование ресурсов'
                    })

        # Рекомендации по кэшированию
        if cache_data:
            hit_rate = cache_data.get('hit_rate', 0)
            if hit_rate < 0.90:
                recommendations.append({
                    'priority': 'high',
                    'category': 'caching',
                    'service': 'redis',
                    'issue': f'Низкий hit rate кэша: {hit_rate:.1%}',
                    'recommendation': 'Пересмотреть стратегию кэширования, увеличить TTL для стабильных данных',
                    'target': '> 90%',
                    'impact': 'Значительное улучшение производительности'
                })

        # Рекомендации по здоровью сервисов
        unhealthy_services = []
        for service_name, metrics in health_data.items():
            if isinstance(metrics, dict) and not metrics.get('is_healthy', False):
                unhealthy_services.append(service_name)

        if unhealthy_services:
            recommendations.append({
                'priority': 'critical',
                'category': 'health',
                'service': ', '.join(unhealthy_services),
                'issue': f'Нездоровые сервисы: {len(unhealthy_services)}',
                'recommendation': 'Немедленно исследовать и устранить проблемы с сервисами',
                'target': '100% здоровых сервисов',
                'impact': 'Восстановление функциональности системы'
            })

        # Сортировка рекомендаций по приоритету
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return recommendations

    def _check_target_compliance(self) -> Dict[str, Any]:
        """Проверка соответствия целевым метрикам"""
        compliance = {
            'response_time': {'target': 50, 'status': 'unknown', 'actual': 0},
            'cache_hit_rate': {'target': 90, 'status': 'unknown', 'actual': 0},
            'cpu_usage': {'target': 5, 'status': 'unknown', 'actual': 0},
            'memory_usage': {'target': 100, 'status': 'unknown', 'actual': 0},
            'success_rate': {'target': 95, 'status': 'unknown', 'actual': 0}
        }

        # Проверка времени отклика
        performance_data = self.results.get('performance_metrics', [])
        if performance_data:
            avg_response_times = [m.get('avg_response_time', 0) for m in performance_data if isinstance(m, dict)]
            if avg_response_times:
                actual_response_time = sum(avg_response_times) / len(avg_response_times)
                compliance['response_time']['actual'] = actual_response_time
                compliance['response_time']['status'] = 'pass' if actual_response_time <= 50 else 'fail'

        # Проверка hit rate кэша
        cache_data = self.results.get('cache_metrics', {})
        if cache_data:
            hit_rate = cache_data.get('hit_rate', 0) * 100
            compliance['cache_hit_rate']['actual'] = hit_rate
            compliance['cache_hit_rate']['status'] = 'pass' if hit_rate >= 90 else 'fail'

        # Проверка использования CPU
        if performance_data:
            cpu_usages = [m.get('cpu_usage', 0) * 100 for m in performance_data if isinstance(m, dict)]
            if cpu_usages:
                actual_cpu = sum(cpu_usages) / len(cpu_usages)
                compliance['cpu_usage']['actual'] = actual_cpu
                compliance['cpu_usage']['status'] = 'pass' if actual_cpu <= 5 else 'fail'

        # Проверка использования памяти
        if performance_data:
            memory_usages = [m.get('memory_usage_mb', 0) for m in performance_data if isinstance(m, dict)]
            if memory_usages:
                actual_memory = sum(memory_usages) / len(memory_usages)
                compliance['memory_usage']['actual'] = actual_memory
                compliance['memory_usage']['status'] = 'pass' if actual_memory <= 100 else 'fail'

        # Проверка успешности запросов
        if performance_data:
            success_rates = [m.get('success_rate', 0) * 100 for m in performance_data if isinstance(m, dict)]
            if success_rates:
                actual_success_rate = sum(success_rates) / len(success_rates)
                compliance['success_rate']['actual'] = actual_success_rate
                compliance['success_rate']['status'] = 'pass' if actual_success_rate >= 95 else 'fail'

        # Общий статус соответствия
        passed_checks = sum(1 for check in compliance.values() if check['status'] == 'pass')
        total_checks = len([check for check in compliance.values() if check['status'] != 'unknown'])

        overall_compliance = (passed_checks / total_checks * 100) if total_checks > 0 else 0

        return {
            'overall_compliance': overall_compliance,
            'passed_checks': passed_checks,
            'total_checks': total_checks,
            'details': compliance
        }

    def _generate_charts(self) -> Dict[str, str]:
        """Генерация графиков для отчета"""
        charts = {}

        try:
            # График времени отклика по сервисам
            performance_data = self.results.get('performance_metrics', [])
            if performance_data:
                services = []
                response_times = []

                for metrics in performance_data:
                    if isinstance(metrics, dict):
                        services.append(metrics.get('service_name', 'unknown'))
                        response_times.append(metrics.get('avg_response_time', 0))

                if services and response_times:
                    plt.figure(figsize=(10, 6))
                    bars = plt.bar(services, response_times, color='skyblue')
                    plt.axhline(y=50, color='red', linestyle='--', label='Целевое значение (50ms)')
                    plt.title('Время отклика по сервисам')
                    plt.xlabel('Сервисы')
                    plt.ylabel('Время отклика (ms)')
                    plt.xticks(rotation=45)
                    plt.legend()
                    plt.tight_layout()

                    # Добавление значений на столбцы
                    for bar, value in zip(bars, response_times):
                        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                                f'{value:.1f}ms', ha='center', va='bottom')

                    chart_path = f"{self.report_dir}/response_times_chart.png"
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    charts['response_times'] = chart_path

            # График соответствия целевым метрикам
            compliance_data = self._check_target_compliance()
            if compliance_data['details']:
                metrics_names = []
                actual_values = []
                target_values = []
                statuses = []

                for metric_name, data in compliance_data['details'].items():
                    if data['status'] != 'unknown':
                        metrics_names.append(metric_name.replace('_', ' ').title())
                        actual_values.append(data['actual'])
                        target_values.append(data['target'])
                        statuses.append(data['status'])

                if metrics_names:
                    fig, ax = plt.subplots(figsize=(12, 6))
                    x = range(len(metrics_names))

                    # Столбцы для фактических и целевых значений
                    width = 0.35
                    bars1 = ax.bar([i - width/2 for i in x], actual_values, width,
                                  label='Фактические значения', alpha=0.8)
                    bars2 = ax.bar([i + width/2 for i in x], target_values, width,
                                  label='Целевые значения', alpha=0.8)

                    # Цветовая кодировка по статусу
                    for i, (bar, status) in enumerate(zip(bars1, statuses)):
                        bar.set_color('green' if status == 'pass' else 'red')

                    ax.set_xlabel('Метрики')
                    ax.set_ylabel('Значения')
                    ax.set_title('Соответствие целевым метрикам')
                    ax.set_xticks(x)
                    ax.set_xticklabels(metrics_names, rotation=45)
                    ax.legend()

                    plt.tight_layout()
                    chart_path = f"{self.report_dir}/compliance_chart.png"
                    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    charts['compliance'] = chart_path

        except Exception as e:
            print(f"⚠️ Ошибка генерации графиков: {e}")

        return charts

    def _create_html_report(self, analysis: Dict[str, Any], charts: Dict[str, str]) -> str:
        """Создание HTML отчета"""
        html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет A/B Тестирования Open WebUI Hub</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .status-excellent { background-color: #d4edda; border-color: #c3e6cb; }
        .status-good { background-color: #d1ecf1; border-color: #bee5eb; }
        .status-warning { background-color: #fff3cd; border-color: #ffeaa7; }
        .status-critical { background-color: #f8d7da; border-color: #f5c6cb; }
        .metric { display: inline-block; margin: 10px; padding: 10px; border-radius: 5px; background: #f8f9fa; }
        .recommendation { margin: 10px 0; padding: 10px; border-left: 4px solid #007bff; background: #f8f9fa; }
        .priority-critical { border-left-color: #dc3545; }
        .priority-high { border-left-color: #fd7e14; }
        .priority-medium { border-left-color: #ffc107; }
        .priority-low { border-left-color: #28a745; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .chart { text-align: center; margin: 20px 0; }
        .chart img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Отчет A/B Тестирования Open WebUI Hub</h1>
        <p>Дата создания: {{ timestamp }}</p>
        <p>Общая длительность тестирования: {{ test_duration }} секунд</p>
    </div>

    <!-- Общий статус системы -->
    <div class="section status-{{ overall_status }}">
        <h2>📊 Общий статус системы</h2>
        <div class="metric">
            <strong>Здоровье системы:</strong> {{ health_percentage }}%
        </div>
        <div class="metric">
            <strong>Производительность:</strong> {{ performance_status }}
        </div>
        <div class="metric">
            <strong>Кэширование:</strong> {{ cache_status }}
        </div>
        <div class="metric">
            <strong>Интеграция:</strong> {{ integration_status }}
        </div>
    </div>

    <!-- Детальный анализ здоровья -->
    <div class="section">
        <h2>🏥 Анализ здоровья сервисов</h2>
        <p><strong>Здоровых сервисов:</strong> {{ health_analysis.healthy_services }}/{{ health_analysis.total_services }}</p>
        <table>
            <tr><th>Сервис</th><th>Статус</th><th>Время отклика (ms)</th><th>Контейнер</th><th>Ошибка</th></tr>
            {% for service in health_analysis.service_details %}
            <tr>
                <td>{{ service.name }}</td>
                <td>{{ '✅ Здоров' if service.healthy else '❌ Нездоров' }}</td>
                <td>{{ service.response_time if service.response_time > 0 else 'N/A' }}</td>
                <td>{{ service.container_status }}</td>
                <td>{{ service.error or 'Нет' }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <!-- Анализ производительности -->
    <div class="section">
        <h2>⚡ Анализ производительности</h2>
        <p><strong>Среднее время отклика:</strong> {{ performance_analysis.avg_response_time }}ms</p>
        <p><strong>Средняя успешность:</strong> {{ (performance_analysis.avg_success_rate * 100) }}%</p>

        {% if charts.response_times %}
        <div class="chart">
            <img src="{{ charts.response_times }}" alt="График времени отклика">
        </div>
        {% endif %}

        <table>
            <tr><th>Сервис</th><th>Среднее время (ms)</th><th>P95 (ms)</th><th>Успешность</th><th>CPU %</th><th>Память (MB)</th></tr>
            {% for service, metrics in performance_analysis.service_performance.items() %}
            <tr>
                <td>{{ service }}</td>
                <td>{{ metrics.avg_response_time }}</td>
                <td>{{ metrics.p95_response_time }}</td>
                <td>{{ (metrics.success_rate * 100) }}%</td>
                <td>{{ (metrics.cpu_usage * 100) }}%</td>
                <td>{{ metrics.memory_usage_mb }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <!-- Анализ кэширования -->
    <div class="section">
        <h2>🔄 Анализ кэширования</h2>
        <p><strong>Hit Rate:</strong> {{ cache_analysis.hit_rate_percentage }}%</p>
        <p><strong>Эффективность:</strong> {{ cache_analysis.efficiency }}</p>
        <p><strong>Использование памяти:</strong> {{ cache_analysis.used_memory_mb }}MB</p>
        <p><strong>Операций в секунду:</strong> {{ cache_analysis.operations_per_second }}</p>
    </div>

    <!-- Соответствие целевым метрикам -->
    <div class="section">
        <h2>🎯 Соответствие целевым метрикам</h2>
        <p><strong>Общее соответствие:</strong> {{ compliance.overall_compliance }}%</p>

        {% if charts.compliance %}
        <div class="chart">
            <img src="{{ charts.compliance }}" alt="График соответствия метрикам">
        </div>
        {% endif %}

        <table>
            <tr><th>Метрика</th><th>Целевое значение</th><th>Фактическое значение</th><th>Статус</th></tr>
            {% for metric, data in compliance.details.items() %}
            {% if data.status != 'unknown' %}
            <tr>
                <td>{{ metric.replace('_', ' ').title() }}</td>
                <td>{{ data.target }}</td>
                <td>{{ data.actual }}</td>
                <td>{{ '✅ Соответствует' if data.status == 'pass' else '❌ Не соответствует' }}</td>
            </tr>
            {% endif %}
            {% endfor %}
        </table>
    </div>

    <!-- Рекомендации -->
    <div class="section">
        <h2>💡 Рекомендации по оптимизации</h2>
        {% for rec in recommendations %}
        <div class="recommendation priority-{{ rec.priority }}">
            <h4>{{ rec.category.title() }} - {{ rec.service }}</h4>
            <p><strong>Проблема:</strong> {{ rec.issue }}</p>
            <p><strong>Рекомендация:</strong> {{ rec.recommendation }}</p>
            <p><strong>Целевое значение:</strong> {{ rec.target }}</p>
            <p><strong>Влияние:</strong> {{ rec.impact }}</p>
            <p><strong>Приоритет:</strong> {{ rec.priority.upper() }}</p>
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>📈 Заключение</h2>
        <p>Тестирование завершено. Общий статус системы: <strong>{{ overall_status.upper() }}</strong></p>
        <p>Для улучшения производительности рекомендуется выполнить {{ recommendations|length }} оптимизаций.</p>
    </div>
</body>
</html>
        """

        # Подготовка данных для шаблона
        template_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'test_duration': self.results.get('test_duration', 0),
            'overall_status': self._get_overall_status(analysis),
            'health_percentage': analysis['overall_health']['health_percentage'],
            'performance_status': analysis['performance_analysis']['status'],
            'cache_status': analysis['cache_analysis']['status'],
            'integration_status': analysis['integration_analysis']['status'],
            'health_analysis': analysis['overall_health'],
            'performance_analysis': analysis['performance_analysis'],
            'cache_analysis': analysis['cache_analysis'],
            'compliance': analysis['compliance'],
            'recommendations': analysis['recommendations'],
            'charts': charts
        }

        # Рендеринг шаблона
        template = Template(html_template)
        return template.render(**template_data)

    def _create_summary_report(self, analysis: Dict[str, Any]) -> str:
        """Создание краткого отчета в формате Markdown"""
        summary = f"""# 📊 Краткий отчет A/B тестирования Open WebUI Hub

**Дата:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Длительность тестирования:** {self.results.get('test_duration', 0):.1f} секунд

## 🎯 Общие результаты

- **Общий статус системы:** {self._get_overall_status(analysis).upper()}
- **Здоровье системы:** {analysis['overall_health']['health_percentage']:.1f}%
- **Соответствие целевым метрикам:** {analysis['compliance']['overall_compliance']:.1f}%

## 📈 Ключевые метрики

### Производительность
- **Среднее время отклика:** {analysis['performance_analysis'].get('avg_response_time', 0):.1f}ms (цель: <50ms)
- **Успешность запросов:** {analysis['performance_analysis'].get('avg_success_rate', 0)*100:.1f}% (цель: >95%)

### Кэширование
- **Hit Rate:** {analysis['cache_analysis'].get('hit_rate_percentage', 0):.1f}% (цель: >90%)
- **Эффективность:** {analysis['cache_analysis'].get('efficiency', 'неизвестно')}

### Интеграция
- **Оценка интеграции:** {analysis['integration_analysis'].get('integration_score', 0):.1f}/100

## ⚠️ Критические проблемы

"""

        # Добавление критических рекомендаций
        critical_recommendations = [r for r in analysis['recommendations'] if r['priority'] == 'critical']
        if critical_recommendations:
            for rec in critical_recommendations:
                summary += f"- **{rec['service']}:** {rec['issue']} - {rec['recommendation']}\n"
        else:
            summary += "Критических проблем не обнаружено.\n"

        summary += f"""
## 💡 Приоритетные рекомендации

"""

        # Добавление топ-5 рекомендаций
        top_recommendations = analysis['recommendations'][:5]
        for i, rec in enumerate(top_recommendations, 1):
            summary += f"{i}. **[{rec['priority'].upper()}]** {rec['service']}: {rec['recommendation']}\n"

        summary += f"""
## 📊 Детальная статистика

### Здоровье сервисов
- Всего сервисов: {analysis['overall_health']['total_services']}
- Здоровых сервисов: {analysis['overall_health']['healthy_services']}
- Процент здоровых: {analysis['overall_health']['health_percentage']:.1f}%

### Соответствие целям
"""

        # Добавление статуса соответствия целям
        for metric, data in analysis['compliance']['details'].items():
            if data['status'] != 'unknown':
                status_icon = '✅' if data['status'] == 'pass' else '❌'
                summary += f"- {metric.replace('_', ' ').title()}: {status_icon} {data['actual']:.1f} (цель: {data['target']})\n"

        summary += f"""
---
*Отчет сгенерирован автоматически системой A/B тестирования Open WebUI Hub*
"""

        return summary

    def _get_overall_status(self, analysis: Dict[str, Any]) -> str:
        """Определение общего статуса системы"""
        statuses = [
            analysis['overall_health']['status'],
            analysis['performance_analysis']['status'],
            analysis['cache_analysis']['status'],
            analysis['integration_analysis']['status']
        ]

        if 'critical' in statuses:
            return 'critical'
        elif 'warning' in statuses:
            return 'warning'
        elif 'good' in statuses:
            return 'good'
        else:
            return 'excellent'
