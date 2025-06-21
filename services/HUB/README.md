# 🏗️ Hub Service - Архитектурная визуализация и Service Discovery

Микросервис Hub предоставляет интерактивную визуализацию архитектуры Open WebUI Hub, real-time мониторинг сервисов и функциональность service discovery.

## 🌟 Возможности

### Frontend (React)
- **Интерактивная диаграмма архитектуры** - 5 слоев с визуализацией всех микросервисов
- **Real-time мониторинг** - автоматическое обновление статуса сервисов каждые 30 секунд
- **Детальная информация** - статус контейнеров, health checks, порты, ошибки
- **Метрики в реальном времени** - системные показатели с графиками и прогресс-барами
- **Responsive дизайн** - адаптивный интерфейс для всех устройств

### Backend API (Python Flask)
- **Service Discovery** - автоматическое обнаружение Docker контейнеров
- **Health Monitoring** - проверка состояния всех сервисов
- **Architecture API** - структурированные данные об архитектуре системы
- **Metrics Collection** - сбор и агрегация системных метрик
- **Caching** - кэширование данных для повышения производительности

## 🚀 Быстрый старт

### Запуск через Docker Compose

```bash
# Запуск Hub сервиса вместе с остальной экосистемой
docker-compose -f compose.local.yml up -d hub

# Проверка статуса
docker-compose -f compose.local.yml ps hub
```

### Доступ к сервису

- **Web Interface**: http://localhost:5003
- **Via Nginx proxy**: http://localhost/hub
- **API Documentation**: http://localhost:5003/api/health

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check сервиса |
| `/api/services` | GET | Список всех сервисов с статусами |
| `/api/services/{id}` | GET | Детальная информация о сервисе |
| `/api/architecture` | GET | Полные данные архитектуры |
| `/api/metrics` | GET | Системные метрики |
| `/api/layers` | GET | Архитектурные слои |

### Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/discovery` | GET | Service discovery |
| `/api/cache/info` | GET | Информация о кэше |
| `/api/cache/clear` | POST | Очистка кэша |

### Примеры использования

```bash
# Проверка здоровья сервиса
curl http://localhost:5003/api/health

# Получение всех сервисов
curl http://localhost:5003/api/services

# Получение метрик системы
curl http://localhost:5003/api/metrics

# Очистка кэша
curl -X POST http://localhost:5003/api/cache/clear
```

## 🔧 Конфигурация

### Переменные окружения

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
HUB_SECRET_KEY=your-secret-key-here
```

### Docker Configuration

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

## 🏗️ Архитектура

### Структура проекта

```
services/hub/
├── backend/                 # Python Flask API
│   ├── app.py              # Основное приложение
│   ├── requirements.txt    # Python зависимости
│   ├── test_hub_api.py     # Unit тесты
│   └── test_integration.py # Интеграционные тесты
├── src/                    # React Frontend
│   ├── components/         # React компоненты
│   │   ├── ArchitectureDiagram.tsx
│   │   ├── RealTimeMetrics.tsx
│   │   └── ...
│   └── ...
├── Dockerfile             # Multi-stage build
├── package.json           # Node.js зависимости
└── README.md              # Документация
```

### Архитектурные слои

1. **Presentation Layer** - Nginx, интерфейсы пользователя
2. **Application Layer** - Open WebUI, Dashboard, Hub, Auth, MCP Server
3. **Service Layer** - Ollama, LiteLLM, Docling, Tika, EdgeTTS, SearXNG
4. **Data Layer** - PostgreSQL, Redis
5. **Infrastructure Layer** - Watchtower, мониторинг

## 🔍 Мониторинг и метрики

### Системные метрики

- **Общее количество сервисов** - все настроенные сервисы
- **Здоровые сервисы** - сервисы с успешными health checks
- **Запущенные контейнеры** - активные Docker контейнеры
- **Сервисы с ошибками** - проблемные сервисы
- **Время работы** - uptime Hub API

### Метрики по слоям

Для каждого архитектурного слоя:
- Общее количество сервисов
- Количество здоровых сервисов
- Количество запущенных контейнеров
- Процент здоровых сервисов

### Health Checks

Hub сервис проверяет состояние других сервисов через:
- **HTTP health endpoints** - для сервисов с REST API
- **Docker container status** - статус контейнеров
- **Custom checks** - специальные проверки (например, PostgreSQL)

## 🧪 Тестирование

### Unit тесты

```bash
cd services/hub/backend
python -m pytest test_hub_api.py -v
```

### Интеграционные тесты

```bash
cd services/hub/backend
python -m pytest test_integration.py -v
```

### Быстрая проверка

```bash
cd services/hub
python test_hub_basic.py
```

### Тестирование API

```bash
# Health check
curl http://localhost:5003/api/health

# Проверка всех endpoints
for endpoint in health services architecture metrics layers; do
  echo "Testing /api/$endpoint"
  curl -s http://localhost:5003/api/$endpoint | jq .
done
```

## 🔧 Разработка

### Локальная разработка

```bash
# Backend development
cd services/hub/backend
pip install -r requirements.txt
python app.py

# Frontend development
cd services/hub
pnpm install
pnpm dev
```

### Сборка Docker образа

```bash
cd services/hub
docker build -t hub-service .
```

### Отладка

```bash
# Просмотр логов
docker-compose -f compose.local.yml logs hub

# Подключение к контейнеру
docker-compose -f compose.local.yml exec hub bash

# Проверка переменных окружения
docker-compose -f compose.local.yml exec hub env | grep HUB_
```

## 🔒 Безопасность

### Рекомендации

- Измените `HUB_SECRET_KEY` в production
- Ограничьте доступ к Docker socket
- Используйте HTTPS в production
- Регулярно обновляйте зависимости

### Docker Security

- Сервис запускается от non-root пользователя
- Docker socket доступен только для чтения
- Минимальные привилегии контейнера

## 📈 Производительность

### Кэширование

- **TTL**: 30 секунд по умолчанию
- **Автоматическая очистка** устаревших записей
- **Thread-safe** операции с кэшем

### Оптимизация

- Неблокирующие HTTP запросы
- Параллельные health checks
- Эффективное использование памяти

## 🔗 Интеграция

### С Dashboard API

Hub сервис интегрируется с Dashboard API для получения дополнительных метрик системы.

### С Docker

Прямая интеграция с Docker Engine для:
- Обнаружения контейнеров
- Мониторинга статуса
- Service discovery

### С Nginx

Настроена маршрутизация через Nginx proxy:
- `/hub` - основной интерфейс
- `/api/hub` - API endpoints

## 🐛 Устранение неполадок

### Частые проблемы

1. **Hub сервис не запускается**
   ```bash
   # Проверьте логи
   docker-compose logs hub

   # Проверьте переменные окружения
   cat env/hub.env
   ```

2. **API возвращает ошибки**
   ```bash
   # Проверьте доступность Docker
   curl http://localhost:5003/api/health

   # Очистите кэш
   curl -X POST http://localhost:5003/api/cache/clear
   ```

3. **Frontend не загружается**
   ```bash
   # Проверьте сборку frontend
   docker-compose exec hub ls -la /app/dist
   ```

### Диагностика

```bash
# Полная диагностика
python services/hub/test_hub_basic.py

# Проверка Docker интеграции
docker-compose exec hub python -c "import docker; print(docker.from_env().ping())"
```

## 📚 Дополнительные ресурсы

- [Open WebUI Hub Documentation](../../docs/README.md)
- [Docker Compose Configuration](../../compose.local.yml)
- [Nginx Configuration](../../conf/nginx/conf.d/default.local.conf)
