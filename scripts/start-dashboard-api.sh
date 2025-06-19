#!/bin/bash

# Open WebUI Hub - Dashboard API Starter
echo "🚀 Запуск Dashboard API для Open WebUI Hub"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Создание виртуального окружения если не существует
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker не найден. Некоторые функции могут не работать."
fi

# Запуск API
echo "🌐 Запуск Dashboard API на http://localhost:5000"
echo "📊 Панель управления: file://$(pwd)/test-page.html"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""

python3 dashboard-api.py
