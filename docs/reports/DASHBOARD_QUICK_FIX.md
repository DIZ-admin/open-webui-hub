# ⚡ Быстрое устранение неполадок панели управления

## 🚨 Частые проблемы и решения

### 1. "Load failed" или "Ошибка загрузки данных"

#### ✅ Проверка Dashboard API
```bash
# Проверить, запущен ли API
ps aux | grep dashboard-api.py

# Если не запущен - запустить
cd /path/to/open-webui-hub
python3 dashboard-api.py
```

#### ✅ Проверка доступности API
```bash
# Тест основных endpoints
curl http://localhost:5002/api/services
curl http://localhost:5002/api/system/stats

# Должны вернуть JSON данные
```

#### ✅ Проверка CORS
- **Симптом**: Ошибки в консоли браузера о CORS
- **Решение**: Убедиться, что в dashboard-api.py есть `from flask_cors import CORS`

### 2. Медленная загрузка данных

#### ✅ Оптимизация запросов
```javascript
// Используйте быстрый endpoint без ресурсов
fetch('http://localhost:5002/api/services')

// Ресурсы загружайте отдельно только при необходимости
fetch('http://localhost:5002/api/services?resources=true')
```

### 3. Ошибки управления сервисами

#### ✅ Проверка Docker
```bash
# Проверить статус Docker
docker ps

# Проверить docker-compose
docker-compose -f compose.local.yml ps
```

#### ✅ Тест управления через API
```bash
curl -X POST http://localhost:5002/api/service/litellm/control \
  -H "Content-Type: application/json" \
  -d '{"action": "restart"}'
```

### 4. Проблемы с конфигурацией

#### ✅ Проверка файлов конфигурации
```bash
# Проверить структуру проекта
ls -la env/
ls -la conf/

# Проверить права доступа
chmod 644 env/*.env
chmod 644 conf/*/*.yml
```

## 🔧 Диагностические команды

### Полная диагностика системы
```bash
echo "=== Диагностика Open WebUI Hub ==="

echo "1. Dashboard API:"
ps aux | grep dashboard-api.py

echo "2. Docker контейнеры:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "3. API endpoints:"
curl -s http://localhost:5002/api/services | jq 'keys'

echo "4. Системные ресурсы:"
curl -s http://localhost:5002/api/system/stats | jq '.system'
```

### Быстрый тест API
```bash
# Создать и запустить тест
cat > quick_test.sh << 'EOF'
#!/bin/bash
echo "🧪 Быстрый тест Dashboard API"

endpoints=(
    "/api/status"
    "/api/services" 
    "/api/system/stats"
    "/api/service/litellm/config"
)

for endpoint in "${endpoints[@]}"; do
    echo -n "Testing $endpoint: "
    if curl -s -f "http://localhost:5002$endpoint" > /dev/null; then
        echo "✅ OK"
    else
        echo "❌ FAIL"
    fi
done
EOF

chmod +x quick_test.sh
./quick_test.sh
```

## 🚀 Перезапуск системы

### Полный перезапуск
```bash
# 1. Остановить Dashboard API
pkill -f dashboard-api.py

# 2. Перезапустить Docker сервисы
docker-compose -f compose.local.yml restart

# 3. Запустить Dashboard API
python3 dashboard-api.py

# 4. Проверить работу
curl http://localhost:5002/api/services
```

### Быстрый перезапуск API
```bash
# Остановить и запустить API
pkill -f dashboard-api.py && python3 dashboard-api.py
```

## 🌐 Проблемы с браузером

### Очистка кэша
1. **Chrome/Edge**: Ctrl+Shift+R (принудительное обновление)
2. **Firefox**: Ctrl+F5
3. **Safari**: Cmd+Option+R

### Проверка консоли браузера
1. Открыть **Developer Tools** (F12)
2. Перейти на вкладку **Console**
3. Обновить страницу и проверить ошибки
4. Перейти на вкладку **Network** и проверить HTTP запросы

### Проверка CORS ошибок
- **Ошибка**: "Access to fetch at 'http://localhost:5002' from origin 'file://' has been blocked by CORS policy"
- **Решение**: Убедиться, что Dashboard API запущен с CORS поддержкой

## 📱 Альтернативные способы доступа

### Через локальный веб-сервер
```bash
# Запустить простой HTTP сервер
cd /path/to/open-webui-hub
python3 -m http.server 8080

# Открыть в браузере
# http://localhost:8080/advanced-dashboard.html
```

### Прямые API вызовы
```bash
# Если панель не работает, используйте прямые команды
curl -X POST http://localhost:5002/api/service/litellm/control \
  -H "Content-Type: application/json" \
  -d '{"action": "restart"}'
```

## 🔍 Логи и отладка

### Просмотр логов Dashboard API
```bash
# API логи в реальном времени
tail -f /dev/stdout  # если API запущен в терминале

# Или проверить вывод процесса
ps aux | grep dashboard-api.py
```

### Логи безопасности
```bash
# Просмотр логов безопасности
cat logs/security.log | jq '.'

# Последние 10 записей
tail -10 logs/security.log | jq '.'
```

### Логи Docker контейнеров
```bash
# Логи конкретного сервиса
docker logs open-webui-hub-litellm-1

# Логи всех сервисов
docker-compose -f compose.local.yml logs --tail=50
```

## 📞 Контрольный список

### ✅ Перед обращением за помощью проверьте:

1. **Dashboard API запущен** на порту 5002
2. **Docker контейнеры работают** (docker ps)
3. **API endpoints отвечают** (curl тесты)
4. **Нет ошибок в консоли браузера**
5. **Файлы конфигурации существуют** (env/, conf/)
6. **Права доступа корректны** (chmod 644)

### 🆘 Если ничего не помогает:

1. **Полный перезапуск системы**
2. **Проверка диагностической страницы**: `test-dashboard-api.html`
3. **Просмотр логов безопасности**: `logs/security.log`
4. **Проверка документации**: `ADVANCED_DASHBOARD_GUIDE.md`

---
**💡 Совет**: Используйте диагностическую страницу `test-dashboard-api.html` для быстрой проверки всех компонентов системы.
