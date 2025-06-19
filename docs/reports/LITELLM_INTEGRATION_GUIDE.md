# ⚡ LiteLLM Integration Guide - Open WebUI Hub

## 🎯 Обзор интеграции

LiteLLM успешно интегрирован в Open WebUI Hub как унифицированный API слой для работы с различными LLM провайдерами. Это позволяет использовать единый OpenAI-совместимый API для доступа к локальным и внешним моделям.

### ✅ Что реализовано

1. **✅ LiteLLM Proxy Server** - Запущен как Docker сервис
2. **✅ Интеграция с Ollama** - Локальные модели доступны через LiteLLM
3. **✅ OpenAI-совместимый API** - Стандартный интерфейс для всех моделей
4. **✅ Dashboard интеграция** - Мониторинг и управление через панель
5. **✅ Redis кэширование** - Оптимизация производительности
6. **✅ Конфигурация для внешних провайдеров** - Готовность к расширению

## 🌐 Доступные endpoints

### 🔗 LiteLLM API
```
Base URL: http://localhost:4000
Health: http://localhost:4000/health
Models: http://localhost:4000/v1/models
Chat: http://localhost:4000/v1/chat/completions
Completions: http://localhost:4000/v1/completions
```

### 🔑 Аутентификация
```
Authorization: Bearer sk-1234567890abcdef
```

## 🤖 Доступные модели

### 📦 Локальные модели (через Ollama)
| Модель | Алиас | Размер | Назначение |
|--------|-------|--------|------------|
| `llama3.2:3b` | `llama3` | 2.0 GB | Универсальные задачи |
| `qwen2.5-coder:1.5b` | `coder` | 986 MB | Программирование |

### 🌍 Внешние провайдеры (требуют API ключи)
- **OpenAI**: `gpt-4`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-sonnet`
- **Google**: `gemini-pro`

## 🚀 Примеры использования

### 📝 Базовый запрос через curl
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

### 🐍 Python интеграция
```python
import requests
import json

def litellm_chat(message, model="llama3"):
    url = "http://localhost:4000/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-1234567890abcdef",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 150
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Ошибка: {response.status_code}"

# Использование
result = litellm_chat("Напиши функцию сортировки на Python", "coder")
print(result)
```

### 🌐 JavaScript/Node.js интеграция
```javascript
async function callLiteLLM(message, model = 'llama3') {
    const response = await fetch('http://localhost:4000/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer sk-1234567890abcdef',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: model,
            messages: [{ role: 'user', content: message }],
            max_tokens: 150
        })
    });
    
    const data = await response.json();
    return data.choices[0].message.content;
}

// Использование
const result = await callLiteLLM('Объясни принципы ООП');
console.log(result);
```

## 🔧 Конфигурация

### 📁 Файлы конфигурации
- **`conf/litellm/litellm_config.yaml`** - Основная конфигурация LiteLLM
- **`env/litellm.env`** - Переменные окружения
- **`compose.local.yml`** - Docker Compose конфигурация

### 🔑 Добавление внешних провайдеров

#### 1. Добавьте API ключи в `env/litellm.env`:
```bash
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

#### 2. Раскомментируйте модели в `conf/litellm/litellm_config.yaml`:
```yaml
# OpenAI
- model_name: gpt-4
  litellm_params:
    model: gpt-4
    api_key: ${OPENAI_API_KEY}

# Anthropic
- model_name: claude-3-sonnet
  litellm_params:
    model: anthropic/claude-3-sonnet-20240229
    api_key: ${ANTHROPIC_API_KEY}
```

#### 3. Перезапустите LiteLLM:
```bash
docker-compose -f compose.local.yml restart litellm
```

## 📊 Мониторинг через Dashboard

### 🎛️ Dashboard API endpoints
```
GET /api/status - Статус LiteLLM сервиса
GET /api/litellm/models - Список доступных моделей
POST /api/litellm/test - Тестирование генерации
GET /api/test/litellm - Комплексный тест LiteLLM
```

### 🧪 Тестирование через панель управления
1. Откройте панель: `file:///path/to/test-page.html`
2. Нажмите **"⚡ Тест LiteLLM"**
3. Проверьте результаты тестирования

## 🔍 Troubleshooting

### ❌ Проблема: LiteLLM не отвечает
```bash
# Проверьте статус контейнера
docker-compose -f compose.local.yml ps litellm

# Проверьте логи
docker logs open-webui-hub-litellm-1

# Перезапустите сервис
docker-compose -f compose.local.yml restart litellm
```

### ❌ Проблема: Модели не доступны
```bash
# Проверьте, что Ollama работает
curl http://localhost:11435/api/version

# Проверьте список моделей в Ollama
docker exec open-webui-hub-ollama-1 ollama list

# Проверьте конфигурацию LiteLLM
cat conf/litellm/litellm_config.yaml
```

### ❌ Проблема: Внешние провайдеры не работают
1. Убедитесь, что API ключи добавлены в `env/litellm.env`
2. Проверьте, что модели раскомментированы в конфигурации
3. Перезапустите LiteLLM после изменений

## 🎯 Преимущества интеграции

### ✅ Унификация API
- **Единый интерфейс** для всех LLM провайдеров
- **OpenAI-совместимость** для легкой интеграции
- **Простое переключение** между моделями

### ✅ Производительность
- **Redis кэширование** для ускорения повторных запросов
- **Параллельная обработка** запросов
- **Автоматические повторы** при ошибках

### ✅ Мониторинг
- **Интеграция с Dashboard** для визуального контроля
- **Детальное логирование** всех запросов
- **Метрики производительности** в реальном времени

### ✅ Гибкость
- **Легкое добавление** новых провайдеров
- **Конфигурация без перекомпиляции**
- **Поддержка различных форматов** API

## 🚀 Следующие шаги

### 🔮 Планы развития
1. **Добавление streaming** для real-time ответов
2. **Интеграция с Open WebUI** для прямого использования
3. **Расширенная аналитика** использования моделей
4. **Load balancing** между несколькими экземплярами
5. **Rate limiting** для контроля нагрузки

### 💡 Рекомендации
1. **Используйте алиасы** (`llama3`, `coder`) для удобства
2. **Мониторьте производительность** через Dashboard
3. **Кэшируйте частые запросы** для экономии ресурсов
4. **Тестируйте новые модели** перед продакшеном
5. **Регулярно обновляйте** конфигурацию

## 🎉 Заключение

LiteLLM успешно интегрирован в Open WebUI Hub и предоставляет:
- ✅ **Унифицированный API** для всех LLM провайдеров
- ✅ **Полную совместимость** с существующей инфраструктурой
- ✅ **Готовность к расширению** новыми провайдерами
- ✅ **Продвинутый мониторинг** и управление

**Теперь вы можете использовать единый API для работы с любыми LLM моделями!** 🚀
