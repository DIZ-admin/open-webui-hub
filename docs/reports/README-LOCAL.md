# 🚀 Open WebUI Hub - Локальное развертывание

Это руководство поможет вам развернуть Open WebUI Hub на локальной машине для разработки и тестирования без использования внешних сервисов типа Cloudflare.

## 📋 Системные требования

### Минимальные требования:
- **ОС**: macOS, Linux, Windows (с WSL2)
- **RAM**: 8GB (рекомендуется 16GB+)
- **Диск**: 20GB свободного места
- **CPU**: 4+ ядра

### Необходимые зависимости:
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git**
- **curl** (для тестирования)

## 🛠️ Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/DIZ-admin/open-webui-hub.git
cd open-webui-hub
```

### 2. Автоматическая настройка
```bash
# Запустить скрипт настройки
./setup-local.sh
```

Этот скрипт:
- Проверит зависимости
- Создаст все конфигурационные файлы
- Сгенерирует безопасные секретные ключи
- Настроит окружение для локального использования

### 3. Запуск сервисов
```bash
# Запустить все сервисы
./start-local.sh
```

Скрипт запустит сервисы в правильном порядке и проверит их работоспособность.

### 4. Первоначальная настройка
```bash
# Загрузить модели и выполнить настройку
./configure-local.sh
```

### 5. Тестирование
```bash
# Проверить работоспособность всех сервисов
./test-local.sh
```

## 🌐 Доступ к сервисам

После успешного запуска доступны следующие сервисы:

| Сервис | URL | Описание |
|--------|-----|----------|
| **Open WebUI** | http://localhost:3000 | Основной интерфейс AI |
| **Ollama API** | http://localhost:11434 | API для LLM моделей |
| **SearXNG** | http://localhost:8080 | Анонимный поиск |
| **Redis Insight** | http://localhost:8001 | Интерфейс Redis |
| **Docling** | http://localhost:5001 | Обработка документов |
| **Tika** | http://localhost:9998 | Извлечение текста |

## ⚙️ Ручная настройка

### 1. Создание первого пользователя
1. Откройте http://localhost:3000
2. Создайте учетную запись администратора
3. Войдите в систему

### 2. Настройка MCP серверов
1. Перейдите в **Settings > Tools > General**
2. Добавьте следующие URL:
   - `http://mcposerver:8000/time`
   - `http://mcposerver:8000/postgres`

### 3. Проверка моделей
1. Перейдите в **Settings > Models**
2. Убедитесь, что модели Ollama доступны
3. При необходимости загрузите дополнительные модели

## 🔧 Управление сервисами

### Основные команды
```bash
# Просмотр статуса
docker-compose -f compose.local.yml ps

# Просмотр логов
docker-compose -f compose.local.yml logs [service_name]

# Перезапуск сервиса
docker-compose -f compose.local.yml restart [service_name]

# Остановка всех сервисов
docker-compose -f compose.local.yml down

# Полная очистка (удаление данных)
docker-compose -f compose.local.yml down -v
sudo rm -rf data/
```

### Загрузка дополнительных моделей Ollama
```bash
# Список доступных моделей
docker-compose -f compose.local.yml exec ollama ollama list

# Загрузка новой модели
docker-compose -f compose.local.yml exec ollama ollama pull [model_name]

# Примеры популярных моделей:
docker-compose -f compose.local.yml exec ollama ollama pull llama3.1:8b
docker-compose -f compose.local.yml exec ollama ollama pull codellama:7b
docker-compose -f compose.local.yml exec ollama ollama pull mistral:7b
```

## 🧪 Тестирование функций

### 1. Тест чата с AI
1. Откройте Open WebUI
2. Создайте новый чат
3. Отправьте сообщение
4. Убедитесь, что AI отвечает

### 2. Тест загрузки документов
1. Загрузите PDF или текстовый файл
2. Задайте вопрос о содержимом
3. Проверьте, что AI может анализировать документ

### 3. Тест веб-поиска
1. Включите веб-поиск в настройках
2. Задайте вопрос, требующий актуальной информации
3. Убедитесь, что AI использует результаты поиска

### 4. Тест MCP инструментов
1. Настройте MCP серверы
2. Используйте команды времени или базы данных
3. Проверьте работу инструментов

## 🔍 Мониторинг и отладка

### Проверка здоровья сервисов
```bash
# Автоматическая проверка
./test-local.sh

# Ручная проверка эндпоинтов
curl -I http://localhost:3000
curl http://localhost:11434/api/version
curl -I http://localhost:8080
```

### Просмотр логов
```bash
# Все сервисы
docker-compose -f compose.local.yml logs

# Конкретный сервис
docker-compose -f compose.local.yml logs openwebui

# В реальном времени
docker-compose -f compose.local.yml logs -f ollama
```

### Использование ресурсов
```bash
# Статистика контейнеров
docker stats

# Использование места
docker system df
du -sh data/
```

## 🚨 Решение проблем

Для решения типичных проблем см. [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Быстрые решения:

#### Порты заняты
```bash
# Найти процесс
lsof -i :3000

# Изменить порт в compose.local.yml
```

#### Сервисы не запускаются
```bash
# Проверить логи
docker-compose -f compose.local.yml logs

# Перезапустить
docker-compose -f compose.local.yml restart
```

#### Нет места на диске
```bash
# Очистить Docker
docker system prune -a

# Удалить старые данные
sudo rm -rf data/postgres data/redis
```

## �� Структура проекта

```
open-webui-hub/
├── compose.local.yml          # Docker Compose для локальной разработки
├── setup-local.sh            # Скрипт автоматической настройки
├── start-local.sh            # Скрипт запуска сервисов
├── configure-local.sh        # Скрипт первоначальной настройки
├── test-local.sh            # Скрипт тестирования
├── TROUBLESHOOTING.md       # Руководство по решению проблем
├── conf/                    # Конфигурационные файлы
│   ├── nginx/              # Настройки Nginx
│   ├── mcposerver/         # Настройки MCP серверов
│   └── searxng/           # Настройки SearXNG
├── env/                    # Переменные окружения
└── data/                   # Данные сервисов (создается автоматически)
    ├── postgres/          # База данных
    ├── redis/            # Кэш Redis
    ├── ollama/           # Модели Ollama
    └── openwebui/        # Данные Open WebUI
```

## 🔒 Безопасность

### Для локальной разработки:
- Аутентификация упрощена
- Используются стандартные пароли
- Сервисы доступны без SSL

### Для продакшена:
- Измените все пароли и ключи
- Настройте SSL сертификаты
- Включите полную аутентификацию
- Используйте оригинальный compose.yml с Cloudflare

## 🤝 Поддержка

- **Документация**: [Open WebUI Docs](https://docs.openwebui.com/)
- **Discord**: [Open WebUI Community](https://discord.gg/xD89WPmgut)
- **Issues**: [GitHub Issues](https://github.com/DIZ-admin/open-webui-hub/issues)

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE) файл.
