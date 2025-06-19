#!/bin/bash

# 🔍 Автоматическая диагностика Open WebUI Hub Dashboard
# Дата создания: 19 июня 2025
# Версия: 1.0

echo "🔍 Автоматическая диагностика Open WebUI Hub Dashboard"
echo "=================================================="
echo "Дата: $(date)"
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для цветного вывода
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_section() {
    echo ""
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Счетчики
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

check_result() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ $1 -eq 0 ]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        print_success "$2"
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        print_error "$2"
    fi
}

# 1. Проверка Dashboard API
print_section "1. Dashboard API"

# Проверка процесса
if pgrep -f "dashboard-api.py" > /dev/null; then
    check_result 0 "Dashboard API процесс запущен"
    
    # Получаем PID и информацию о процессе
    PID=$(pgrep -f "dashboard-api.py")
    print_info "PID: $PID"
    
    # Проверка порта
    if lsof -i :5002 > /dev/null 2>&1; then
        check_result 0 "Порт 5002 открыт"
    else
        check_result 1 "Порт 5002 не доступен"
    fi
else
    check_result 1 "Dashboard API не запущен"
    print_warning "Запустите: python3 dashboard-api.py"
fi

# 2. Проверка API endpoints
print_section "2. API Endpoints"

API_BASE="http://localhost:5002"
ENDPOINTS=(
    "/api/status:Статус сервисов"
    "/api/services:Информация о сервисах"
    "/api/system/stats:Системная статистика"
    "/api/service/litellm/config:Конфигурация LiteLLM"
)

for endpoint_info in "${ENDPOINTS[@]}"; do
    IFS=':' read -r endpoint description <<< "$endpoint_info"
    
    if curl -s -f "${API_BASE}${endpoint}" > /dev/null 2>&1; then
        check_result 0 "$description ($endpoint)"
    else
        check_result 1 "$description ($endpoint)"
    fi
done

# 3. Проверка производительности
print_section "3. Производительность API"

print_info "Тестирование скорости ответа..."

# Тест быстрого endpoint
START_TIME=$(date +%s%N)
if curl -s "${API_BASE}/api/services" > /dev/null 2>&1; then
    END_TIME=$(date +%s%N)
    DURATION=$(( (END_TIME - START_TIME) / 1000000 ))
    
    if [ $DURATION -lt 1000 ]; then
        check_result 0 "/api/services отвечает быстро (${DURATION}ms)"
    elif [ $DURATION -lt 5000 ]; then
        check_result 0 "/api/services отвечает приемлемо (${DURATION}ms)"
        print_warning "Время ответа больше 1 секунды"
    else
        check_result 1 "/api/services отвечает медленно (${DURATION}ms)"
    fi
else
    check_result 1 "/api/services не отвечает"
fi

# 4. Проверка Docker
print_section "4. Docker контейнеры"

if command -v docker > /dev/null 2>&1; then
    check_result 0 "Docker установлен"
    
    # Проверка запущенных контейнеров
    RUNNING_CONTAINERS=$(docker ps --filter "name=open-webui-hub" --format "{{.Names}}" | wc -l)
    
    if [ $RUNNING_CONTAINERS -gt 0 ]; then
        check_result 0 "Найдено $RUNNING_CONTAINERS запущенных контейнеров Open WebUI Hub"
        
        # Список контейнеров
        print_info "Запущенные контейнеры:"
        docker ps --filter "name=open-webui-hub" --format "  • {{.Names}} ({{.Status}})"
    else
        check_result 1 "Контейнеры Open WebUI Hub не запущены"
        print_warning "Запустите: docker-compose -f compose.local.yml up -d"
    fi
else
    check_result 1 "Docker не установлен"
fi

# 5. Проверка файлов проекта
print_section "5. Файлы проекта"

PROJECT_FILES=(
    "dashboard-api.py:Dashboard API скрипт"
    "advanced-dashboard.html:Панель управления"
    "compose.local.yml:Docker Compose конфигурация"
    "env/:Директория переменных окружения"
    "conf/:Директория конфигураций"
)

for file_info in "${PROJECT_FILES[@]}"; do
    IFS=':' read -r file description <<< "$file_info"
    
    if [ -e "$file" ]; then
        check_result 0 "$description существует"
    else
        check_result 1 "$description отсутствует"
    fi
done

# 6. Проверка зависимостей Python
print_section "6. Python зависимости"

PYTHON_DEPS=(
    "flask:Flask веб-фреймворк"
    "flask_cors:CORS поддержка"
    "docker:Docker Python клиент"
    "requests:HTTP клиент"
    "psutil:Системная информация"
    "yaml:YAML парсер"
)

for dep_info in "${PYTHON_DEPS[@]}"; do
    IFS=':' read -r dep description <<< "$dep_info"
    
    if python3 -c "import $dep" 2>/dev/null; then
        check_result 0 "$description установлен"
    else
        check_result 1 "$description не установлен"
        print_warning "Установите: pip3 install $dep"
    fi
done

# 7. Проверка системных ресурсов
print_section "7. Системные ресурсы"

# CPU
CPU_USAGE=$(python3 -c "import psutil; print(psutil.cpu_percent(interval=1))" 2>/dev/null || echo "N/A")
if [ "$CPU_USAGE" != "N/A" ]; then
    if (( $(echo "$CPU_USAGE < 80" | bc -l) )); then
        check_result 0 "CPU загрузка в норме (${CPU_USAGE}%)"
    else
        check_result 1 "Высокая загрузка CPU (${CPU_USAGE}%)"
    fi
else
    check_result 1 "Не удалось получить загрузку CPU"
fi

# Память
MEMORY_INFO=$(python3 -c "import psutil; mem=psutil.virtual_memory(); print(f'{mem.percent:.1f}')" 2>/dev/null || echo "N/A")
if [ "$MEMORY_INFO" != "N/A" ]; then
    if (( $(echo "$MEMORY_INFO < 80" | bc -l) )); then
        check_result 0 "Память в норме (${MEMORY_INFO}%)"
    else
        check_result 1 "Высокое использование памяти (${MEMORY_INFO}%)"
    fi
else
    check_result 1 "Не удалось получить информацию о памяти"
fi

# 8. Проверка логов
print_section "8. Логи и мониторинг"

# Логи безопасности
if [ -f "logs/security.log" ]; then
    LOG_LINES=$(wc -l < logs/security.log)
    check_result 0 "Лог безопасности существует ($LOG_LINES записей)"
else
    check_result 1 "Лог безопасности отсутствует"
fi

# Бэкапы
if [ -d "backups" ]; then
    BACKUP_COUNT=$(find backups -type d -name "*_*" | wc -l)
    if [ $BACKUP_COUNT -gt 0 ]; then
        check_result 0 "Найдено $BACKUP_COUNT бэкапов"
    else
        check_result 0 "Директория бэкапов существует (пуста)"
    fi
else
    check_result 1 "Директория бэкапов отсутствует"
fi

# 9. Итоговый отчет
print_section "9. Итоговый отчет"

echo ""
echo "📊 Статистика проверок:"
echo "  • Всего проверок: $TOTAL_CHECKS"
echo "  • Успешно: $PASSED_CHECKS"
echo "  • Неудачно: $FAILED_CHECKS"
echo ""

SUCCESS_RATE=$(( PASSED_CHECKS * 100 / TOTAL_CHECKS ))

if [ $SUCCESS_RATE -ge 90 ]; then
    print_success "Система работает отлично! ($SUCCESS_RATE% проверок пройдено)"
    echo ""
    print_info "🚀 Панель управления готова к использованию:"
    echo "   • Dashboard API: http://localhost:5002"
    echo "   • Панель управления: file://$(pwd)/advanced-dashboard.html"
    echo "   • Диагностика: file://$(pwd)/test-dashboard-api.html"
elif [ $SUCCESS_RATE -ge 70 ]; then
    print_warning "Система работает с предупреждениями ($SUCCESS_RATE% проверок пройдено)"
    echo ""
    print_info "Рекомендации:"
    echo "   • Проверьте неудачные тесты выше"
    echo "   • Обратитесь к DASHBOARD_QUICK_FIX.md"
else
    print_error "Система требует внимания! ($SUCCESS_RATE% проверок пройдено)"
    echo ""
    print_info "Критические проблемы обнаружены:"
    echo "   • Проверьте все неудачные тесты"
    echo "   • Обратитесь к DASHBOARD_TROUBLESHOOTING_REPORT.md"
    echo "   • Выполните полный перезапуск системы"
fi

echo ""
echo "📚 Полезные ссылки:"
echo "   • Полное руководство: ADVANCED_DASHBOARD_GUIDE.md"
echo "   • Быстрый старт: QUICK_START_ADVANCED_DASHBOARD.md"
echo "   • Устранение неполадок: DASHBOARD_QUICK_FIX.md"
echo ""
echo "🔍 Диагностика завершена: $(date)"
