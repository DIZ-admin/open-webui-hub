# 🎛️ LiteLLM UI - Руководство пользователя

**Дата создания**: 19 июня 2025  
**Версия**: 1.0  
**Статус**: ✅ **Активен и доступен**

## 🌐 Доступ к LiteLLM UI

### 🔗 **Основные URL**

#### 1. 🎛️ **LiteLLM Dashboard (Административный интерфейс)**
```
URL: http://localhost:4000/ui
Описание: Полнофункциональный веб-интерфейс для управления LiteLLM
Аутентификация: Требуется API ключ
```

#### 2. 📚 **Swagger UI (API документация)**
```
URL: http://localhost:4000/
Описание: Интерактивная документация API с возможностью тестирования
Аутентификация: Не требуется для просмотра
```

### 🔑 **Аутентификация**
```
API Key: sk-1234567890abcdef
Заголовок: Authorization: Bearer sk-1234567890abcdef
```

## 🎛️ Функции LiteLLM Dashboard

### 📊 **Основные возможности**

#### 1. **Мониторинг моделей**
- ✅ Просмотр всех доступных моделей
- ✅ Статус каждой модели (активна/неактивна)
- ✅ Статистика использования
- ✅ Производительность моделей

#### 2. **Управление запросами**
- ✅ Мониторинг активных запросов
- ✅ История запросов
- ✅ Статистика ошибок
- ✅ Время отклика

#### 3. **Конфигурация**
- ✅ Управление моделями
- ✅ Настройка провайдеров
- ✅ Конфигурация кэширования
- ✅ Настройки безопасности

#### 4. **Аналитика**
- ✅ Графики использования
- ✅ Метрики производительности
- ✅ Отчеты по затратам
- ✅ Статистика пользователей

## 🚀 Быстрый старт

### 1. **Открытие Dashboard**
```bash
# Откройте в браузере
open http://localhost:4000/ui

# Или используйте curl для проверки
curl -H "Authorization: Bearer sk-1234567890abcdef" http://localhost:4000/ui
```

### 2. **Первоначальная настройка**
1. **Войдите в систему** используя API ключ `sk-1234567890abcdef`
2. **Проверьте модели** в разделе "Models"
3. **Настройте мониторинг** в разделе "Analytics"
4. **Проверьте конфигурацию** в разделе "Settings"

### 3. **Основные действия**

#### Просмотр моделей
```
Раздел: Models
Действие: Просмотр всех 4 доступных моделей
- llama3.2:3b
- qwen2.5-coder:1.5b  
- llama3 (алиас)
- coder (алиас)
```

#### Мониторинг запросов
```
Раздел: Requests / Analytics
Действие: Просмотр статистики API вызовов
- Количество запросов
- Время отклика
- Ошибки и успешные запросы
```

#### Управление конфигурацией
```
Раздел: Settings / Configuration
Действие: Изменение настроек LiteLLM
- Добавление новых моделей
- Настройка провайдеров
- Конфигурация кэширования
```

## 📚 Swagger UI (API документация)

### 🔗 **Доступ**
```
URL: http://localhost:4000/
Описание: Интерактивная документация всех API endpoints
```

### 📖 **Основные разделы**

#### 1. **Chat Completions**
```
Endpoint: POST /v1/chat/completions
Описание: Основной endpoint для генерации текста
Совместимость: OpenAI API
```

#### 2. **Models**
```
Endpoint: GET /v1/models
Описание: Список всех доступных моделей
Аутентификация: Требуется
```

#### 3. **Health Check**
```
Endpoint: GET /health
Описание: Проверка состояния сервиса
Аутентификация: Опционально
```

### 🧪 **Тестирование через Swagger UI**

#### Пример тестирования Chat Completions:
1. Откройте `POST /v1/chat/completions`
2. Нажмите "Try it out"
3. Добавьте Authorization header: `Bearer sk-1234567890abcdef`
4. Введите тестовый запрос:
```json
{
  "model": "llama3",
  "messages": [
    {"role": "user", "content": "Привет! Как дела?"}
  ],
  "max_tokens": 100
}
```
5. Нажмите "Execute"

## 🔧 Конфигурация UI

### 📁 **Файлы конфигурации**

#### conf/litellm/litellm_config.yaml
```yaml
general_settings:
  master_key: "sk-1234567890abcdef"
  disable_auth_on_health_endpoint: true
  
  # Настройки UI
  ui_access_mode: "admin"
  enable_ui: true
```

#### env/litellm.env
```bash
# Настройки LiteLLM UI
LITELLM_UI_ACCESS_MODE=admin
ENABLE_UI=true
```

### 🔄 **Применение изменений**
```bash
# После изменения конфигурации
docker-compose -f compose.local.yml restart litellm

# Проверка статуса
docker-compose -f compose.local.yml ps litellm
```

## 🛠️ Troubleshooting

### ❌ **Проблема: UI не загружается**
```bash
# Проверьте статус контейнера
docker-compose -f compose.local.yml ps litellm

# Проверьте логи
docker-compose -f compose.local.yml logs litellm

# Проверьте доступность
curl -I http://localhost:4000/ui
```

### ❌ **Проблема: Ошибка аутентификации**
```bash
# Проверьте API ключ в конфигурации
grep master_key conf/litellm/litellm_config.yaml

# Тест с правильным ключом
curl -H "Authorization: Bearer sk-1234567890abcdef" http://localhost:4000/v1/models
```

### ❌ **Проблема: UI показывает ошибку 404**
```bash
# Убедитесь, что UI активирован
grep enable_ui conf/litellm/litellm_config.yaml

# Перезапустите сервис
docker-compose -f compose.local.yml restart litellm
```

## 🎯 Полезные команды

### 🔍 **Диагностика**
```bash
# Проверка доступности UI
curl -s -I http://localhost:4000/ui

# Проверка API
curl -H "Authorization: Bearer sk-1234567890abcdef" http://localhost:4000/v1/models

# Проверка логов
docker-compose -f compose.local.yml logs --tail=20 litellm
```

### 📊 **Мониторинг**
```bash
# Статус контейнера
docker-compose -f compose.local.yml ps litellm

# Использование ресурсов
docker stats open-webui-hub-litellm-1

# Проверка портов
netstat -an | grep 4000
```

## 🎉 Заключение

**🎛️ LiteLLM UI успешно активирован и готов к использованию!**

### ✅ **Доступные интерфейсы:**
1. **Dashboard UI**: `http://localhost:4000/ui` - Полнофункциональный административный интерфейс
2. **Swagger UI**: `http://localhost:4000/` - Интерактивная документация API

### 🚀 **Возможности:**
- ✅ **Мониторинг моделей** и их производительности
- ✅ **Управление запросами** и аналитика
- ✅ **Конфигурация системы** через веб-интерфейс
- ✅ **Тестирование API** через Swagger UI

### 🔑 **Аутентификация:**
- **API Key**: `sk-1234567890abcdef`
- **Доступ**: Административный уровень

---
*Руководство создано: Augment Agent*  
*Дата: 19 июня 2025*  
*Статус: Готово к использованию*
