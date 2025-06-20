# 🏗️ Hub Service Deployment Guide

## Overview

Hub Service - это микросервис для архитектурной визуализации и service discovery в Open WebUI Hub. Он предоставляет интерактивную диаграмму архитектуры системы, real-time мониторинг сервисов и API для управления экосистемой.

## 🎯 Архитектура

Hub Service состоит из двух основных компонентов:

### Frontend (React + TypeScript)
- **Интерактивная диаграмма архитектуры** с 5 слоями
- **Real-time мониторинг** с автообновлением каждые 30 секунд
- **Детальная информация** о каждом сервисе
- **Метрики в реальном времени** с графиками
- **Responsive дизайн** для всех устройств

### Backend (Python Flask)
- **Service Discovery API** для автоматического обнаружения сервисов
- **Health Monitoring** всех компонентов системы
- **Architecture API** с структурированными данными
- **Metrics Collection** и агрегация
- **Caching** для повышения производительности

## 🚀 Deployment

### 1. Подготовка окружения

```bash
# Создание необходимых директорий
mkdir -p logs/hub cache/hub

# Копирование конфигурации
cp env/hub.example env/hub.env
```

### 2. Конфигурация переменных окружения

Отредактируйте `env/hub.env`:

```bash
# API Configuration
HUB_API_HOST=0.0.0.0
HUB_API_PORT=5003
HUB_DEBUG_MODE=false

# Logging
HUB_LOG_LEVEL=INFO
HUB_LOG_FORMAT=simple

# Caching
HUB_CACHE_TTL=30

# Service Discovery
HUB_ENABLE_SERVICE_DISCOVERY=true
HUB_DASHBOARD_API_URL=http://dashboard:5002

# Security
HUB_SECRET_KEY=your-production-secret-key-here
```

### 3. Docker Compose интеграция

Hub Service уже интегрирован в `compose.local.yml`:

```yaml
hub:
  build:
    context: services/hub
    dockerfile: Dockerfile
  depends_on:
    - dashboard
    - db
    - redis
    - watchtower
  env_file: env/hub.env
  healthcheck:
    interval: 30s
    retries: 5
    start_period: 15s
    test: curl --fail http://localhost:5003/api/health || exit 1
    timeout: 5s
  restart: unless-stopped
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - ./logs/hub:/app/logs
    - ./cache/hub:/app/cache
  ports:
    - "5003:5003"
```

### 4. Nginx конфигурация

Hub Service интегрирован в Nginx proxy через `conf/nginx/conf.d/default.local.conf`:

```nginx
upstream hubUpstream {
  server hub:5003 max_fails=0 fail_timeout=10s;
  keepalive 512;
}

# Hub Service - Architecture visualization
location /hub {
  rewrite ^/hub/(.*) /$1 break;
  proxy_pass http://hubUpstream;
  # ... proxy headers and CORS
}

# Alternative API endpoint for Hub
location /api/hub {
  rewrite ^/api/hub/(.*) /api/$1 break;
  proxy_pass http://hubUpstream;
  # ... proxy headers
}
```

### 5. Запуск сервиса

```bash
# Запуск Hub сервиса
docker-compose -f compose.local.yml up -d hub

# Проверка статуса
docker-compose -f compose.local.yml ps hub

# Просмотр логов
docker-compose -f compose.local.yml logs -f hub
```

## 🔍 Проверка развертывания

### Health Check

```bash
# Прямой доступ к API
curl http://localhost:5003/api/health

# Через Nginx proxy
curl http://localhost/api/hub/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "service": "hub-api",
  "version": "1.0.0",
  "uptime_seconds": 123.45,
  "timestamp": 1703123456.789,
  "docker_available": true
}
```

### API Endpoints

```bash
# Список всех сервисов
curl http://localhost:5003/api/services

# Архитектурные данные
curl http://localhost:5003/api/architecture

# Системные метрики
curl http://localhost:5003/api/metrics

# Service discovery
curl http://localhost:5003/api/discovery
```

### Web Interface

- **Прямой доступ**: http://localhost:5003
- **Через Nginx**: http://localhost/hub

## 🧪 Тестирование

### Быстрая проверка

```bash
cd services/hub
python test_hub_basic.py
```

### Unit тесты

```bash
cd services/hub/backend
python -m pytest test_hub_api.py -v
```

### Интеграционные тесты

```bash
cd services/hub/backend
HUB_API_URL=http://localhost:5003 python -m pytest test_integration.py -v
```

## 📊 Мониторинг

### Метрики

Hub Service предоставляет следующие метрики:

- **Общее количество сервисов**
- **Здоровые сервисы** (с успешными health checks)
- **Запущенные контейнеры**
- **Сервисы с ошибками**
- **Время работы Hub API**
- **Метрики по архитектурным слоям**

### Логирование

```bash
# Просмотр логов в реальном времени
docker-compose -f compose.local.yml logs -f hub

# Логи в файловой системе
tail -f logs/hub/app.log
```

### Health Checks

Hub Service автоматически проверяет состояние всех сервисов:

- **HTTP health endpoints** для REST API сервисов
- **Docker container status** для всех контейнеров
- **Custom checks** для специфичных сервисов (PostgreSQL, Redis)

## 🔧 Управление

### Очистка кэша

```bash
# Через API
curl -X POST http://localhost:5003/api/cache/clear

# Информация о кэше
curl http://localhost:5003/api/cache/info
```

### Перезапуск сервиса

```bash
# Перезапуск Hub сервиса
docker-compose -f compose.local.yml restart hub

# Пересборка и перезапуск
docker-compose -f compose.local.yml up -d --build hub
```

### Обновление конфигурации

```bash
# После изменения env/hub.env
docker-compose -f compose.local.yml restart hub

# После изменения Nginx конфигурации
docker-compose -f compose.local.yml restart nginx
```

## 🐛 Troubleshooting

### Частые проблемы

1. **Hub сервис не запускается**
   ```bash
   # Проверка логов
   docker-compose -f compose.local.yml logs hub
   
   # Проверка зависимостей
   docker-compose -f compose.local.yml ps dashboard db redis
   ```

2. **API возвращает ошибки 500**
   ```bash
   # Проверка Docker доступности
   docker-compose -f compose.local.yml exec hub python -c "import docker; print(docker.from_env().ping())"
   
   # Очистка кэша
   curl -X POST http://localhost:5003/api/cache/clear
   ```

3. **Frontend не загружается**
   ```bash
   # Проверка сборки frontend
   docker-compose -f compose.local.yml exec hub ls -la /app/dist
   
   # Пересборка контейнера
   docker-compose -f compose.local.yml up -d --build hub
   ```

4. **Service Discovery не работает**
   ```bash
   # Проверка переменной окружения
   docker-compose -f compose.local.yml exec hub env | grep HUB_ENABLE_SERVICE_DISCOVERY
   
   # Проверка доступа к Docker socket
   docker-compose -f compose.local.yml exec hub ls -la /var/run/docker.sock
   ```

### Диагностика

```bash
# Полная диагностика
python services/hub/test_hub_basic.py

# Проверка всех API endpoints
for endpoint in health services architecture metrics layers discovery; do
  echo "=== Testing /api/$endpoint ==="
  curl -s http://localhost:5003/api/$endpoint | jq . || echo "Failed"
  echo
done
```

## 🔒 Безопасность

### Рекомендации для production

1. **Измените секретный ключ**
   ```bash
   # Генерация нового ключа
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Ограничьте доступ к Docker socket**
   - Используйте Docker socket proxy в production
   - Настройте правильные права доступа

3. **Настройте HTTPS**
   - Используйте SSL сертификаты
   - Настройте Nginx для HTTPS

4. **Обновляйте зависимости**
   ```bash
   # Проверка обновлений Python пакетов
   cd services/hub/backend
   pip list --outdated
   
   # Проверка обновлений Node.js пакетов
   cd services/hub
   pnpm outdated
   ```

## 📈 Производительность

### Оптимизация

- **Кэширование**: TTL 30 секунд по умолчанию
- **Неблокирующие запросы**: Параллельные health checks
- **Эффективная память**: Автоматическая очистка кэша

### Мониторинг производительности

```bash
# Время отклика API
time curl -s http://localhost:5003/api/health > /dev/null

# Использование ресурсов
docker stats open-webui-hub-hub-1
```

## 🔗 Интеграция с другими сервисами

### Dashboard API

Hub Service интегрируется с Dashboard API для получения дополнительных системных метрик.

### Open WebUI

Hub Service добавлен в зависимости Open WebUI для обеспечения правильного порядка запуска.

### Nginx

Настроена маршрутизация для доступа к Hub Service через основной домен.

## 📚 Дополнительная документация

- [Hub Service README](../../services/hub/README.md)
- [API Documentation](../../services/hub/backend/README.md)
- [Frontend Documentation](../../services/hub/src/README.md)
- [Docker Compose Configuration](../../compose.local.yml)
