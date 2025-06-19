# 🚀 Open WebUI Hub - Руководство разработчика

## ✅ Текущее состояние системы

### 🎯 Полностью настроенная среда разработки
- ✅ **12 сервисов** запущены и работают
- ✅ **2 AI модели** загружены и протестированы
- ✅ **Dashboard API** активен на порту 5002
- ✅ **Панель мониторинга** доступна и функциональна
- ✅ **Все интеграции** протестированы

### 🤖 Доступные AI модели
1. **Llama 3.2:3b** (2.0 GB) - Универсальная модель для общих задач
2. **Qwen2.5-Coder:1.5b** (986 MB) - Специализированная модель для программирования

### 🌐 Активные сервисы и порты
| Сервис | URL | Статус | Описание |
|--------|-----|--------|----------|
| **Open WebUI** | http://localhost:3000 | ✅ Работает | Основной веб-интерфейс |
| **Ollama API** | http://localhost:11435 | ✅ Работает | LLM сервер (v0.9.2) |
| **PostgreSQL** | localhost:5432 | ✅ Работает | Векторная база данных |
| **Redis Web UI** | http://localhost:8001 | ✅ Работает | Кэш и управление |
| **SearXNG** | http://localhost:8080 | ✅ Работает | Поисковый движок |
| **Tika** | http://localhost:9998 | ✅ Работает | Обработка документов |
| **Dashboard API** | http://localhost:5002 | ✅ Работает | Мониторинг и управление |

## 🎛️ Панель управления

### 📊 Доступ к панели
```
URL: file:///Users/kostas/Documents/Projects/open-webui-hub/test-page.html
Режим: Полный (API подключен)
Обновление: Автоматическое каждые 30 секунд
```

### 🔧 Возможности панели
- **Мониторинг в реальном времени** - статус всех сервисов
- **Метрики производительности** - CPU, память, диск
- **Управление сервисами** - запуск/остановка/перезапуск
- **Просмотр логов** - все сервисы с фильтрацией
- **Тестирование подключений** - Ollama, Redis, PostgreSQL
- **Быстрые действия** - скачивание моделей, очистка Docker

## 🚀 Быстрый старт для разработки

### 1. Проверка готовности системы
```bash
# Статус всех сервисов
curl http://localhost:5002/api/status

# Доступные модели
curl http://localhost:11435/api/tags

# Тест Open WebUI
curl http://localhost:3000/health
```

### 2. Первый AI запрос
```bash
# Универсальная модель
curl -X POST http://localhost:11435/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:3b", "prompt": "Привет! Как дела?", "stream": false}'

# Модель для программирования
curl -X POST http://localhost:11435/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5-coder:1.5b", "prompt": "Напиши функцию сортировки на Python", "stream": false}'
```

### 3. Работа с базой данных
```bash
# Подключение к PostgreSQL
docker exec -it open-webui-hub-db-1 psql -U openwebui -d openwebui

# Проверка векторных расширений
docker exec open-webui-hub-db-1 psql -U openwebui -d openwebui -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### 4. Работа с Redis
```bash
# Подключение к Redis
docker exec -it open-webui-hub-redis-1 redis-cli

# Проверка кэша
docker exec open-webui-hub-redis-1 redis-cli INFO memory
```

## 🛠️ Разработка AI приложений

### 📝 Пример интеграции с Ollama
```python
import requests
import json

def ask_llm(prompt, model="llama3.2:3b"):
    url = "http://localhost:11435/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Ошибка: {response.status_code}"

# Использование
result = ask_llm("Объясни принципы машинного обучения")
print(result)
```

### 🗄️ Пример работы с PostgreSQL
```python
import psycopg2
from pgvector.psycopg2 import register_vector

# Подключение к базе данных
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="openwebui",
    user="openwebui",
    password="openwebui"
)

# Регистрация векторного типа
register_vector(conn)

# Создание таблицы с векторами
cur = conn.cursor()
cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
cur.execute("CREATE TABLE IF NOT EXISTS embeddings (id SERIAL PRIMARY KEY, text TEXT, vector vector(384))")
conn.commit()
```

### 🔴 Пример работы с Redis
```python
import redis

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Кэширование результатов LLM
def cached_llm_request(prompt, model="llama3.2:3b"):
    cache_key = f"llm:{model}:{hash(prompt)}"
    
    # Проверка кэша
    cached_result = r.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    
    # Запрос к LLM
    result = ask_llm(prompt, model)
    
    # Сохранение в кэш на 1 час
    r.setex(cache_key, 3600, json.dumps(result))
    
    return result
```

## 📋 Workflow для разработки

### 1. Планирование
- Определите задачи AI (генерация, анализ, поиск)
- Выберите подходящую модель (универсальная vs специализированная)
- Спланируйте архитектуру данных (векторы, кэш, поиск)

### 2. Разработка
- Используйте панель мониторинга для отслеживания ресурсов
- Тестируйте API endpoints через curl или Postman
- Мониторьте логи сервисов при отладке

### 3. Тестирование
- Проверяйте производительность моделей
- Тестируйте векторный поиск в PostgreSQL
- Оптимизируйте кэширование в Redis

### 4. Деплой
- Используйте Docker Compose для консистентности
- Мониторьте метрики через Dashboard API
- Настройте автоматические бэкапы данных

## 🔧 Полезные команды

### Управление моделями
```bash
# Список доступных моделей в Ollama Hub
docker exec open-webui-hub-ollama-1 ollama list

# Загрузка новой модели
docker exec open-webui-hub-ollama-1 ollama pull mistral:7b

# Удаление модели
docker exec open-webui-hub-ollama-1 ollama rm mistral:7b

# Информация о модели
docker exec open-webui-hub-ollama-1 ollama show llama3.2:3b
```

### Мониторинг ресурсов
```bash
# Использование ресурсов контейнерами
docker stats

# Место на диске
du -sh ./data/*

# Логи сервисов
docker-compose -f compose.local.yml logs -f ollama
```

### Бэкапы и восстановление
```bash
# Бэкап PostgreSQL
docker exec open-webui-hub-db-1 pg_dump -U openwebui openwebui > backup_$(date +%Y%m%d).sql

# Бэкап данных Ollama
tar -czf ollama_backup_$(date +%Y%m%d).tar.gz ./data/ollama

# Бэкап Redis
docker exec open-webui-hub-redis-1 redis-cli BGSAVE
```

## 🎯 Рекомендации

### Производительность
- **Мониторьте память** при работе с большими моделями
- **Используйте кэширование** для частых запросов
- **Оптимизируйте векторные индексы** в PostgreSQL

### Безопасность
- **Не используйте дефолтные пароли** в продакшене
- **Ограничьте доступ к портам** через firewall
- **Регулярно обновляйте** образы Docker

### Масштабирование
- **Мониторьте метрики** через Dashboard API
- **Планируйте ресурсы** для новых моделей
- **Используйте load balancing** для высоких нагрузок

## 🎉 Заключение

**Среда разработки Open WebUI Hub полностью готова!**

- ✅ Все сервисы работают стабильно
- ✅ AI модели загружены и протестированы
- ✅ Панель мониторинга активна
- ✅ API endpoints доступны
- ✅ Документация создана

**Начинайте разработку AI-приложений прямо сейчас!** 🚀
