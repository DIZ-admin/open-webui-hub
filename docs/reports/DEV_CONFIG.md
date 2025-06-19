# 🛠️ Open WebUI Hub - Конфигурация для разработки

## 🔗 API Endpoints и подключения

### 🤖 Ollama LLM API
```
Base URL: http://localhost:11435
API Version: /api/version
Models: /api/tags
Generate: /api/generate
Chat: /api/chat
```

### ⚡ LiteLLM Unified API
```
Base URL: http://localhost:4000
Health: /health
Models: /v1/models
Chat: /v1/chat/completions
Completions: /v1/completions
Authorization: Bearer sk-1234567890abcdef
```

**Доступные модели:**
- `llama3.2:3b` - Универсальная модель (2.0 GB)
- `qwen2.5-coder:1.5b` - Специализированная модель для программирования (986 MB)

**Пример использования:**
```bash
# Получить список моделей
curl http://localhost:11435/api/tags

# Генерация текста
curl -X POST http://localhost:11435/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:3b", "prompt": "Hello!", "stream": false}'
```

### 🗄️ PostgreSQL Database
```
Host: localhost
Port: 5432
Database: openwebui
Username: openwebui
Password: openwebui
```

**Connection String:**
```
postgresql://openwebui:openwebui@localhost:5432/openwebui
```

**Расширения:**
- ✅ pgvector - для векторных операций
- ✅ pg_trgm - для текстового поиска
- ✅ uuid-ossp - для UUID генерации

### 🔴 Redis Cache
```
Host: localhost
Port: 6379
Database: 0
Web UI: http://localhost:8001
```

**Connection String:**
```
redis://localhost:6379/0
```

### 🌐 Open WebUI
```
Main Interface: http://localhost:3000
Health Check: http://localhost:3000/health
API Docs: http://localhost:3000/docs
```

### 🔍 SearXNG Search Engine
```
Search Interface: http://localhost:8080
API: http://localhost:8080/search
Config: http://localhost:8080/config
```

### 📄 Document Processing
```
Tika Server: http://localhost:9998
Docling API: http://localhost:5001
```

### 🔐 Authentication Service
```
Auth API: http://localhost:9090
JWT Endpoint: http://localhost:9090/auth
```

## 🎛️ Dashboard API

### 📊 Monitoring API
```
Base URL: http://localhost:5002/api
Status: GET /status
Metrics: GET /metrics
Logs: GET /logs/<service>
Docker: POST /docker/<action>
Test: GET /test/<service>
```

**Доступные действия Docker:**
- `start` - Запуск всех сервисов
- `stop` - Остановка всех сервисов
- `restart` - Перезапуск всех сервисов

## 🔧 Environment Variables

### Основные переменные
```bash
# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_API_BASE_URL=http://localhost:11435/api

# LiteLLM
LITELLM_CONFIG_PATH=/app/config/litellm_config.yaml
LITELLM_MASTER_KEY=sk-1234567890abcdef
LITELLM_PORT=4000

# Database
DATABASE_URL=postgresql://openwebui:openwebui@db:5432/openwebui
POSTGRES_DB=openwebui
POSTGRES_USER=openwebui
POSTGRES_PASSWORD=openwebui

# Redis
REDIS_URL=redis://redis:6379/0

# Open WebUI
WEBUI_SECRET_KEY=your-secret-key-here
ENABLE_SIGNUP=true
ENABLE_LOGIN_FORM=true
DEFAULT_MODELS=llama3.2:3b,qwen2.5-coder:1.5b

# Search
SEARXNG_BASE_URL=http://searxng:8080

# Document Processing
TIKA_BASE_URL=http://tika:9998
DOCLING_BASE_URL=http://docling:5001
```

## 🚀 Quick Start для разработчиков

### 1. Проверка статуса сервисов
```bash
# Через Docker Compose
docker-compose -f compose.local.yml ps

# Через Dashboard API
curl http://localhost:5002/api/status
```

### 2. Тестирование подключений
```bash
# Ollama
curl http://localhost:11435/api/version

# LiteLLM
curl -H "Authorization: Bearer sk-1234567890abcdef" http://localhost:4000/v1/models

# PostgreSQL (требует psql)
psql postgresql://openwebui:openwebui@localhost:5432/openwebui -c "SELECT version();"

# Redis
redis-cli -h localhost -p 6379 ping

# Open WebUI
curl http://localhost:3000/health
```

### 3. Работа с моделями
```bash
# Список моделей
docker exec open-webui-hub-ollama-1 ollama list

# Загрузка новой модели
docker exec open-webui-hub-ollama-1 ollama pull <model-name>

# Удаление модели
docker exec open-webui-hub-ollama-1 ollama rm <model-name>
```

### 4. Просмотр логов
```bash
# Все сервисы
docker-compose -f compose.local.yml logs

# Конкретный сервис
docker-compose -f compose.local.yml logs <service-name>

# Через Dashboard API
curl http://localhost:5002/api/logs/<service>
```

## 🔍 Troubleshooting

### Проблемы с портами
```bash
# Проверка занятых портов
lsof -i :3000  # Open WebUI
lsof -i :4000  # LiteLLM
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :11435 # Ollama
```

### Проблемы с памятью
```bash
# Проверка использования памяти Docker
docker stats

# Очистка неиспользуемых ресурсов
docker system prune -f
```

### Проблемы с моделями
```bash
# Проверка места на диске
df -h

# Размер данных Ollama
du -sh ./data/ollama
```

## 📚 Полезные команды

### Docker Management
```bash
# Перезапуск всех сервисов
docker-compose -f compose.local.yml restart

# Пересборка и запуск
docker-compose -f compose.local.yml up -d --build

# Остановка и удаление
docker-compose -f compose.local.yml down -v
```

### Database Operations
```bash
# Подключение к PostgreSQL
docker exec -it open-webui-hub-db-1 psql -U openwebui -d openwebui

# Бэкап базы данных
docker exec open-webui-hub-db-1 pg_dump -U openwebui openwebui > backup.sql

# Восстановление базы данных
docker exec -i open-webui-hub-db-1 psql -U openwebui openwebui < backup.sql
```

### Redis Operations
```bash
# Подключение к Redis CLI
docker exec -it open-webui-hub-redis-1 redis-cli

# Очистка кэша
docker exec open-webui-hub-redis-1 redis-cli FLUSHALL
```

## 🎯 Рекомендации по разработке

1. **Используйте панель мониторинга** для отслеживания состояния сервисов
2. **Регулярно проверяйте логи** при возникновении проблем
3. **Тестируйте API endpoints** перед интеграцией
4. **Мониторьте использование ресурсов** при работе с большими моделями
5. **Делайте бэкапы данных** перед экспериментами
