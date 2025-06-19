# 🚀 LiteLLM Setup and Configuration Guide

## 📋 Обзор

LiteLLM в Open WebUI Hub настроен как унифицированный прокси для доступа к различным LLM провайдерам, включая локальные модели Ollama и внешние API (OpenAI, Anthropic, Google).

## ✅ Текущий статус конфигурации

### 🔧 Основные компоненты
- **Порт**: 4000
- **API Endpoint**: `http://localhost:4000/v1/`
- **Мастер ключ**: `sk-1234567890abcdef`
- **Конфигурация**: `conf/litellm/litellm_config.yaml`
- **Переменные окружения**: `env/litellm.env`

### 🤖 Доступные модели

#### Локальные модели (через Ollama)
- `llama3.2:3b` - Основная модель для общения
- `qwen2.5-coder:1.5b` - Специализированная модель для кодирования
- `llama3` - Алиас для llama3.2:3b
- `coder` - Алиас для qwen2.5-coder:1.5b
- `auto` - Автоматический выбор модели

#### Внешние провайдеры (требуют API ключи)
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-5-sonnet`, `claude-3-haiku`
- **Google**: `gemini-1.5-pro`, `gemini-1.5-flash`

## 🔑 API Использование

### Базовый запрос
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-1234567890abcdef" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [{"role": "user", "content": "Привет!"}],
    "max_tokens": 100
  }'
```

### Список доступных моделей
```bash
curl -H "Authorization: Bearer sk-1234567890abcdef" \
  http://localhost:4000/v1/models
```

### Проверка статуса
```bash
curl -H "Authorization: Bearer sk-1234567890abcdef" \
  http://localhost:4000/health
```

## 🔧 Конфигурация

### Основные настройки производительности
- **Таймаут запросов**: 120 секунд
- **Максимальные повторы**: 2
- **Параллельные запросы**: 10 (оптимизировано для локальных моделей)
- **Rate limiting**: 100 запросов/минуту, 10000 токенов/минуту

### Кэширование
- **Тип**: Redis
- **Хост**: redis:6379
- **TTL**: 3600 секунд (1 час)

### Логирование
- **Уровень**: INFO
- **Callbacks**: Redis для успешных и неудачных запросов
- **База данных**: PostgreSQL для детального логирования

## 🔄 Fallback механизмы

### Группы моделей
- **chat**: llama3.2:3b → gpt-4o-mini → claude-3-haiku → gemini-1.5-flash
- **coding**: qwen2.5-coder:1.5b → gpt-4o → claude-3-5-sonnet
- **fast**: llama3.2:3b → gpt-3.5-turbo → gemini-1.5-flash
- **advanced**: gpt-4o → claude-3-5-sonnet → gemini-1.5-pro → llama3.2:3b

## 🔐 Настройка внешних провайдеров

### Добавление API ключей
Отредактируйте `env/litellm.env`:
```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google
GOOGLE_API_KEY=your_google_api_key_here
```

После добавления ключей перезапустите LiteLLM:
```bash
docker-compose -f compose.local.yml restart litellm
```

## 📊 Мониторинг через Dashboard API

### Статус LiteLLM
```bash
curl http://localhost:5002/api/litellm/status
```

### Тестирование модели
```bash
curl -X POST http://localhost:5002/api/litellm/test \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3", "message": "Тест"}'
```

### Список моделей
```bash
curl http://localhost:5002/api/litellm/models
```

## 🔧 Интеграция с Open WebUI

Open WebUI настроен для использования LiteLLM как дополнительного провайдера:
- **OpenAI API Base**: `http://litellm:4000/v1`
- **API Key**: `sk-1234567890abcdef`
- **Ollama Base**: `http://ollama:11434` (прямое подключение сохранено)

## 🚨 Устранение неполадок

### Проблема: Таймауты при генерации
**Решение**: Модели Ollama требуют времени для загрузки в память. Первый запрос может занять до 60 секунд.

### Проблема: Health endpoint зависает
**Решение**: Используйте `/v1/models` для проверки статуса вместо `/health`.

### Проблема: Внешние модели недоступны
**Решение**: Проверьте наличие и корректность API ключей в `env/litellm.env`.

## 📈 Оптимизация производительности

### Для локальных моделей
1. Уменьшите `max_parallel_requests` до 5-10
2. Используйте `ollama_keep_alive: "5m"` для сохранения моделей в памяти
3. Настройте подходящие таймауты (60-120 секунд)

### Для внешних провайдеров
1. Увеличьте `max_parallel_requests` до 50-100
2. Используйте более короткие таймауты (30-60 секунд)
3. Настройте rate limiting согласно лимитам провайдера

## 🔄 Обновление конфигурации

1. Отредактируйте `conf/litellm/litellm_config.yaml`
2. Перезапустите сервис: `docker-compose -f compose.local.yml restart litellm`
3. Проверьте статус: `curl -H "Authorization: Bearer sk-1234567890abcdef" http://localhost:4000/v1/models`

## 📚 Дополнительные ресурсы

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Google AI Studio](https://aistudio.google.com/)
