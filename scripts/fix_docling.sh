#!/bin/bash

# Скрипт для исправления проблемы Docling с osd.traineddata
# Автор: Augment Agent
# Дата: 2025-06-21

set -e

echo "🔧 Исправление проблемы Docling: UnboundLocalError df_osd"
echo "=========================================================="

# Функция для проверки статуса контейнера
check_container() {
    local container_name="$1"
    if docker ps --format "table {{.Names}}" | grep -q "$container_name"; then
        echo "✅ Контейнер $container_name запущен"
        return 0
    else
        echo "❌ Контейнер $container_name не запущен"
        return 1
    fi
}

# Функция для проверки здоровья Docling
check_docling_health() {
    echo "🔄 Проверка здоровья Docling..."
    if curl -s http://localhost:5001/health | grep -q "ok"; then
        echo "✅ Docling health check: OK"
        return 0
    else
        echo "❌ Docling health check: FAILED"
        return 1
    fi
}

# Функция для установки osd.traineddata
install_osd_traineddata() {
    echo "🔄 Установка недостающего файла osd.traineddata..."
    
    # Проверяем, есть ли уже файл
    if docker exec open-webui-hub-docling-1 test -f /usr/share/tesseract/tessdata/osd.traineddata; then
        echo "✅ Файл osd.traineddata уже существует"
        return 0
    fi
    
    # Загружаем файл
    echo "📥 Загрузка osd.traineddata..."
    docker exec -u root open-webui-hub-docling-1 \
        wget -O /usr/share/tesseract/tessdata/osd.traineddata \
        https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata
    
    if [ $? -eq 0 ]; then
        echo "✅ Файл osd.traineddata успешно установлен"
        return 0
    else
        echo "❌ Ошибка установки osd.traineddata"
        return 1
    fi
}

# Функция для проверки доступности OSD
check_osd_availability() {
    echo "🔄 Проверка доступности OSD в Tesseract..."
    
    local langs=$(docker exec open-webui-hub-docling-1 tesseract --list-langs 2>/dev/null)
    if echo "$langs" | grep -q "osd"; then
        echo "✅ OSD доступен в Tesseract"
        echo "📋 Доступные языки: $(echo "$langs" | grep -v "List of available languages")"
        return 0
    else
        echo "❌ OSD не найден в Tesseract"
        echo "📋 Доступные языки: $langs"
        return 1
    fi
}

# Функция для перезапуска Docling
restart_docling() {
    echo "🔄 Перезапуск Docling сервиса..."
    docker-compose -f compose.local.yml restart docling
    
    # Ждем запуска
    echo "⏳ Ожидание запуска сервиса..."
    sleep 10
    
    if check_docling_health; then
        echo "✅ Docling успешно перезапущен"
        return 0
    else
        echo "❌ Ошибка перезапуска Docling"
        return 1
    fi
}

# Функция для проверки логов на ошибки
check_logs() {
    echo "🔄 Проверка логов Docling на ошибки..."
    
    local logs=$(docker logs open-webui-hub-docling-1 --tail 20 2>/dev/null)
    
    if echo "$logs" | grep -q "UnboundLocalError"; then
        echo "❌ Найдена ошибка UnboundLocalError в логах"
        return 1
    elif echo "$logs" | grep -q "osd.traineddata" && echo "$logs" | grep -q "Error opening"; then
        echo "❌ Найдена ошибка с osd.traineddata в логах"
        return 1
    else
        echo "✅ Логи чистые, ошибок не найдено"
        return 0
    fi
}

# Функция для создания постоянного решения
create_permanent_fix() {
    echo "🔄 Создание постоянного решения..."
    
    if [ -f "services/docling/Dockerfile" ]; then
        echo "✅ Dockerfile для исправленного Docling уже существует"
        
        echo "🔄 Сборка исправленного образа..."
        docker-compose -f compose.local.yml build docling
        
        if [ $? -eq 0 ]; then
            echo "✅ Исправленный образ собран успешно"
            return 0
        else
            echo "❌ Ошибка сборки образа"
            return 1
        fi
    else
        echo "❌ Dockerfile не найден. Создайте services/docling/Dockerfile"
        return 1
    fi
}

# Основная функция
main() {
    echo "🚀 Начало исправления Docling..."
    
    # Проверяем контейнер
    if ! check_container "open-webui-hub-docling-1"; then
        echo "❌ Запустите Docling контейнер перед выполнением скрипта"
        exit 1
    fi
    
    # Проверяем текущее состояние
    if check_docling_health && check_osd_availability && check_logs; then
        echo "🎉 Docling уже исправлен и работает корректно!"
        exit 0
    fi
    
    # Применяем исправление
    echo "🔧 Применение исправления..."
    
    if install_osd_traineddata && restart_docling && check_osd_availability && check_logs; then
        echo "🎉 Исправление применено успешно!"
        
        # Предлагаем создать постоянное решение
        echo ""
        echo "💡 Хотите создать постоянное решение? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            create_permanent_fix
        fi
        
        echo ""
        echo "✅ Docling исправлен и готов к работе!"
        echo "📋 Рекомендации:"
        echo "   - Протестируйте загрузку документов через Open WebUI"
        echo "   - Мониторьте логи на предмет новых ошибок"
        echo "   - Рассмотрите создание постоянного образа для продакшена"
        
    else
        echo "❌ Не удалось применить исправление"
        echo "🔍 Проверьте логи для диагностики:"
        echo "   docker logs open-webui-hub-docling-1 --tail 50"
        exit 1
    fi
}

# Запуск основной функции
main "$@"
