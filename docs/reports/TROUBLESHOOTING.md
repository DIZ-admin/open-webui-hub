# 🔧 Руководство по решению проблем - Open WebUI Hub

## Общие проблемы и решения

### 1. 🐳 Проблемы с Docker

#### Проблема: "Docker daemon is not running"
```bash
# Решение: Запустить Docker
# macOS/Windows: Запустить Docker Desktop
# Linux:
sudo systemctl start docker
sudo systemctl enable docker
```

#### Проблема: "Permission denied" при работе с Docker
```bash
# Решение: Добавить пользователя в группу docker (Linux)
sudo usermod -aG docker $USER
# Перелогиниться или выполнить:
newgrp docker
```

#### Проблема: Недостаточно места на диске
```bash
# Проверить использование места Docker
docker system df

# Очистить неиспользуемые ресурсы
docker system prune -a

# Удалить неиспользуемые volumes
docker volume prune
```

### 2. 🌐 Проблемы с портами

#### Проблема: "Port already in use"
```bash
# Найти процесс, использующий порт
lsof -i :80  # или другой порт

# Остановить процесс
sudo kill -9 <PID>

# Или изменить порт в compose.local.yml
```

#### Проблема: Не удается подключиться к сервису
```bash
# Проверить статус контейнеров
docker-compose -f compose.local.yml ps

# Проверить логи
docker-compose -f compose.local.yml logs [service_name]

# Перезапустить сервис
docker-compose -f compose.local.yml restart [service_name]
```

### 3. 🗄️ Проблемы с базой данных

#### Проблема: PostgreSQL не запускается
```bash
# Проверить логи базы данных
docker-compose -f compose.local.yml logs db

# Удалить данные и пересоздать (ВНИМАНИЕ: потеря данных!)
docker-compose -f compose.local.yml down
sudo rm -rf data/postgres
docker-compose -f compose.local.yml up -d db
```

#### Проблема: "Connection refused" к базе данных
```bash
# Проверить, что база данных запущена
docker-compose -f compose.local.yml exec db pg_isready -U postgres

# Проверить переменные окружения
cat env/db.env
cat env/openwebui.env | grep DATABASE_URL
```

### 4. 🤖 Проблемы с Ollama

#### Проблема: Модели не загружаются
```bash
# Проверить статус Ollama
docker-compose -f compose.local.yml exec ollama ollama list

# Загрузить модель вручную
docker-compose -f compose.local.yml exec ollama ollama pull llama3.2:3b

# Проверить место на диске
df -h
```

#### Проблема: Ollama API недоступен
```bash
# Проверить логи Ollama
docker-compose -f compose.local.yml logs ollama

# Тестировать API напрямую
curl http://localhost:11434/api/version

# Перезапустить Ollama
docker-compose -f compose.local.yml restart ollama
```

### 5. 🔍 Проблемы с поиском (SearXNG)

#### Проблема: SearXNG не отвечает
```bash
# Проверить логи SearXNG
docker-compose -f compose.local.yml logs searxng

# Проверить конфигурацию
cat conf/searxng/settings.yml | grep secret

# Перезапустить SearXNG
docker-compose -f compose.local.yml restart searxng redis
```

#### Проблема: Поиск не работает в Open WebUI
```bash
# Проверить настройки в env/openwebui.env
grep SEARXNG env/openwebui.env

# Убедиться, что URL правильный
curl "http://localhost:8080/search?q=test"
```

### 6. 📄 Проблемы с обработкой документов

#### Проблема: Docling не обрабатывает документы
```bash
# Проверить статус Docling
curl http://localhost:5001/health

# Проверить логи
docker-compose -f compose.local.yml logs docling

# Тестировать обработку
curl -X POST "http://localhost:5001/v1alpha/convert/source" \
  -H "Content-Type: application/json" \
  -d '{"http_sources": [{"url": "https://example.com/test.pdf"}]}'
```

#### Проблема: Tika не извлекает текст
```bash
# Проверить статус Tika
curl http://localhost:9998/tika

# Проверить логи
docker-compose -f compose.local.yml logs tika

# Тестировать извлечение
echo "test" | curl -X POST "http://localhost:9998/tika" \
  -H "Content-Type: text/plain" \
  -d @-
```

### 7. 🛠️ Проблемы с MCP серверами

#### Проблема: MCP серверы не отображаются в Open WebUI
```bash
# Проверить статус MCP сервера
docker-compose -f compose.local.yml logs mcposerver

# Проверить конфигурацию
cat conf/mcposerver/config.json

# Добавить серверы вручную в Open WebUI:
# Settings > Tools > General
# Добавить: http://mcposerver:8000/time
# Добавить: http://mcposerver:8000/postgres
```

### 8. 🔐 Проблемы с аутентификацией

#### Проблема: Не удается войти в Open WebUI
```bash
# Проверить секретные ключи
grep WEBUI_SECRET_KEY env/openwebui.env
grep WEBUI_SECRET_KEY env/auth.env

# Убедиться, что ключи одинаковые
# Перезапустить auth сервис
docker-compose -f compose.local.yml restart auth openwebui
```

### 9. 🚨 Экстренное восстановление

#### Полная перезагрузка системы
```bash
# Остановить все сервисы
docker-compose -f compose.local.yml down

# Удалить все данные (ВНИМАНИЕ: потеря всех данных!)
sudo rm -rf data/

# Пересоздать конфигурацию
./setup-local.sh

# Запустить заново
./start-local.sh
```

#### Сброс только базы данных
```bash
# Остановить сервисы
docker-compose -f compose.local.yml stop openwebui db

# Удалить данные базы
sudo rm -rf data/postgres

# Запустить базу данных
docker-compose -f compose.local.yml up -d db

# Дождаться готовности и запустить Open WebUI
sleep 30
docker-compose -f compose.local.yml up -d openwebui
```

## 📊 Мониторинг и диагностика

### Проверка статуса всех сервисов
```bash
# Статус контейнеров
docker-compose -f compose.local.yml ps

# Использование ресурсов
docker stats

# Логи всех сервисов
docker-compose -f compose.local.yml logs --tail=50
```

### Проверка сетевого подключения
```bash
# Тестирование всех эндпоинтов
./test-local.sh

# Ручная проверка
curl -I http://localhost:3000
curl -I http://localhost:11434/api/version
curl -I http://localhost:8080
```

### Проверка использования дискового пространства
```bash
# Общее использование
df -h

# Использование Docker
docker system df

# Размер данных проекта
du -sh data/
```

## 🆘 Получение помощи

Если проблема не решается:

1. **Соберите информацию:**
   ```bash
   # Версии
   docker --version
   docker-compose --version
   
   # Статус сервисов
   docker-compose -f compose.local.yml ps
   
   # Логи проблемного сервиса
   docker-compose -f compose.local.yml logs [service_name]
   ```

2. **Проверьте документацию:**
   - [Open WebUI Docs](https://docs.openwebui.com/)
   - [Ollama Documentation](https://ollama.com/docs)

3. **Обратитесь за помощью:**
   - [Open WebUI Discord](https://discord.gg/xD89WPmgut)
   - GitHub Issues в соответствующих репозиториях

## 📝 Полезные команды

```bash
# Просмотр логов в реальном времени
docker-compose -f compose.local.yml logs -f [service_name]

# Выполнение команд в контейнере
docker-compose -f compose.local.yml exec [service_name] bash

# Перезапуск конкретного сервиса
docker-compose -f compose.local.yml restart [service_name]

# Обновление образов
docker-compose -f compose.local.yml pull

# Пересборка и перезапуск
docker-compose -f compose.local.yml up -d --force-recreate [service_name]
```
