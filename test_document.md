# Тестовый документ для проверки обработки

## Введение

Это тестовый документ для проверки функциональности обработки документов в системе Open WebUI Hub.

## Содержание

- Тестирование Docling сервиса
- Тестирование Apache Tika  
- Проверка интеграции с OpenWebUI

## Технические детали

### Архитектура системы
- Система использует микросервисную архитектуру
- Docling обрабатывает современные форматы документов
- Tika поддерживает широкий спектр форматов файлов
- Redis используется для кэширования результатов

### Компоненты
1. **LiteLLM** - унифицированный API для LLM
2. **Ollama** - локальный LLM сервер
3. **SearXNG** - поисковая система
4. **PostgreSQL** - основная база данных
5. **Redis** - кэш и хранилище сессий

## Заключение

Этот документ должен быть успешно обработан системой обработки документов и преобразован в структурированный формат для дальнейшего использования в RAG pipeline.
