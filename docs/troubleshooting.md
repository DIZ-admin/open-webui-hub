# 🔧 Устранение неполадок Open WebUI Hub

## Проблемы с обработкой документов

### Ошибки Docling

#### ✅ UnboundLocalError: df_osd - РЕШЕНО
**Проблема:** `UnboundLocalError: cannot access local variable 'df_osd'`  
**Причина:** Отсутствует файл `osd.traineddata` для Tesseract OCR  
**Решение:** 
```bash
# Автоматическое исправление
./scripts/fix_docling.sh

# Или ручное исправление
docker exec -u root open-webui-hub-docling-1 \
  wget -O /usr/share/tesseract/tessdata/osd.traineddata \
  https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata
docker-compose -f compose.local.yml restart docling
```

#### Общая диагностика Docling
- Проверьте логи: `docker logs open-webui-hub-docling-1`
- Убедитесь, что сервис запущен: `curl http://localhost:5001/health`
- Проверьте доступность OSD: `docker exec open-webui-hub-docling-1 tesseract --list-langs`

### Переключение между Docling и Tika

#### Переключение на Tika (быстрое решение)
```bash
# Обновить в базе данных
docker exec open-webui-hub-db-1 psql -U postgres -d openwebui -c \
  "UPDATE config SET data = data::jsonb || '{\"rag\": {\"CONTENT_EXTRACTION_ENGINE\": \"tika\"}}' 
   WHERE id = (SELECT id FROM config ORDER BY created_at DESC LIMIT 1);"

# Перезапустить Open WebUI
docker-compose -f compose.local.yml restart openwebui
```

#### Переключение на Docling
```bash
# Обновить в базе данных
docker exec open-webui-hub-db-1 psql -U postgres -d openwebui -c \
  "UPDATE config SET data = data::jsonb || '{\"rag\": {\"CONTENT_EXTRACTION_ENGINE\": \"docling\"}}' 
   WHERE id = (SELECT id FROM config ORDER BY created_at DESC LIMIT 1);"

# Перезапустить Open WebUI
docker-compose -f compose.local.yml restart openwebui
```

## Проблемы с базой данных

### PostgreSQL не запускается
```bash
# Проверить логи
docker logs open-webui-hub-db-1

# Проверить права доступа к данным
ls -la data/postgres/

# Пересоздать контейнер
docker-compose -f compose.local.yml down db
docker-compose -f compose.local.yml up -d db
```

### Проблемы с pgvector
```bash
# Проверить установку расширения
docker exec open-webui-hub-db-1 psql -U postgres -d openwebui -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Переустановить расширение
docker exec open-webui-hub-db-1 psql -U postgres -d openwebui -c "DROP EXTENSION IF EXISTS vector; CREATE EXTENSION vector;"
```

## Проблемы с LLM

### Ollama недоступен
```bash
# Проверить статус
curl http://localhost:11434/api/tags

# Перезапустить Ollama
docker-compose -f compose.local.yml restart ollama

# Проверить модели
docker exec open-webui-hub-ollama-1 ollama list
```

### LiteLLM ошибки
```bash
# Проверить логи
docker logs open-webui-hub-litellm-1

# Проверить конфигурацию
cat env/litellm.env

# Тестовый запрос
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "ollama/llama2", "messages": [{"role": "user", "content": "test"}]}'
```

## Проблемы с веб-поиском

### SearXNG недоступен
```bash
# Проверить статус
curl "http://localhost:8888/search?q=test&format=json"

# Перезапустить SearXNG
docker-compose -f compose.local.yml restart searxng

# Проверить конфигурацию
docker exec open-webui-hub-searxng-1 cat /etc/searxng/settings.yml
```

## Общие проблемы

### Контейнеры не запускаются
```bash
# Проверить статус всех сервисов
docker-compose -f compose.local.yml ps

# Проверить логи конкретного сервиса
docker-compose -f compose.local.yml logs [service_name]

# Пересоздать все сервисы
docker-compose -f compose.local.yml down
docker-compose -f compose.local.yml up -d
```

### Проблемы с портами
```bash
# Проверить занятые порты
netstat -tulpn | grep LISTEN

# Найти процесс, использующий порт
lsof -i :3000

# Остановить конфликтующий процесс
sudo kill -9 [PID]
```

### Проблемы с дисковым пространством
```bash
# Проверить использование места
df -h

# Очистить неиспользуемые Docker образы
docker system prune -a

# Очистить логи Docker
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

## Полезные команды для диагностики

### Проверка здоровья всех сервисов
```bash
# Скрипт проверки всех сервисов
./scripts/health_check.sh

# Или ручная проверка
curl http://localhost:3000/health          # Open WebUI
curl http://localhost:5001/health          # Docling
curl http://localhost:9998/tika            # Tika
curl http://localhost:11434/api/tags       # Ollama
curl http://localhost:4000/health          # LiteLLM
curl "http://localhost:8888/search?q=test" # SearXNG
```

### Мониторинг ресурсов
```bash
# Использование ресурсов контейнерами
docker stats

# Логи в реальном времени
docker-compose -f compose.local.yml logs -f [service_name]

# Проверка сетевого взаимодействия
docker network ls
docker network inspect open-webui-hub_default
```

## Контакты для поддержки

- **Документация:** `docs/`
- **Логи:** `docker-compose logs [service]`
- **Конфигурация:** `env/`
- **Скрипты:** `scripts/`

---
**Обновлено:** 2025-06-21  
**Версия:** 1.0
