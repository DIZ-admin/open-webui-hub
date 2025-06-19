# ⚡ Быстрый старт - Open WebUI Hub

## 🚀 Развертывание одной командой

```bash
# Клонировать репозиторий
git clone https://github.com/DIZ-admin/open-webui-hub.git
cd open-webui-hub

# Запустить полное развертывание
./deploy-local.sh
```

Этот скрипт автоматически:
- ✅ Проверит зависимости
- ✅ Создаст конфигурацию
- ✅ Запустит все сервисы
- ✅ Загрузит AI модели
- ✅ Протестирует функциональность

## 🌐 Доступ

После завершения откройте: **http://localhost:3000**

## �� Системные требования

- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM (рекомендуется 16GB+)
- 20GB свободного места

## 🔧 Управление

```bash
# Статус сервисов
docker-compose -f compose.local.yml ps

# Остановить все
docker-compose -f compose.local.yml down

# Перезапустить
./start-local.sh

# Тестирование
./test-local.sh
```

## 🆘 Помощь

- 📖 Подробная документация: [README-LOCAL.md](README-LOCAL.md)
- 🔧 Решение проблем: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 💬 Discord: https://discord.gg/xD89WPmgut

---

**Время развертывания:** ~10-15 минут (зависит от скорости интернета)
