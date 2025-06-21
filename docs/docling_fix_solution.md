# 🔧 Решение проблемы Docling: UnboundLocalError df_osd

**Дата:** 2025-06-21  
**Статус:** ✅ Решено  
**Версия Docling:** v0.15.0

## 📋 Описание проблемы

### 🔴 Исходная ошибка
```
UnboundLocalError: cannot access local variable 'df_osd' where it is not associated with a value
```

### 🔍 Корень проблемы
Анализ логов показал, что ошибка вызвана отсутствием файла `osd.traineddata` для Tesseract OCR:

```
Error opening data file /usr/share/tesseract/tessdata/osd.traineddata
Please make sure the TESSDATA_PREFIX environment variable is set to your "tessdata" directory.
Failed loading language 'osd'
Tesseract couldn't load any languages!
Could not initialize tesseract.
```

### 📊 Диагностика
- **Версия образа:** `quay.io/docling-project/docling-serve:latest` (v0.15.0)
- **Дата образа:** 2025-06-17
- **Проблема:** Отсутствует файл OSD (Orientation and Script Detection) для Tesseract
- **Последствие:** Переменная `df_osd` не инициализируется, что приводит к UnboundLocalError

## ✅ Решение

### 🔧 Шаг 1: Установка недостающего файла
```bash
# Загрузка osd.traineddata в контейнер
docker exec -u root open-webui-hub-docling-1 \
  wget -O /usr/share/tesseract/tessdata/osd.traineddata \
  https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata
```

### 🔧 Шаг 2: Проверка установки
```bash
# Проверка наличия файла
docker exec open-webui-hub-docling-1 ls -la /usr/share/tesseract/tessdata/osd.traineddata

# Проверка доступности OSD в Tesseract
docker exec open-webui-hub-docling-1 tesseract --list-langs
# Должно показать: eng, osd
```

### 🔧 Шаг 3: Создание постоянного решения
Создан исправленный Dockerfile (`services/docling/Dockerfile`):

```dockerfile
FROM quay.io/docling-project/docling-serve:latest

USER root

# Установка недостающего файла osd.traineddata
RUN wget -O /usr/share/tesseract/tessdata/osd.traineddata \
    https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata

USER 1001

LABEL version="v0.15.0-fixed"
```

### 🔧 Шаг 4: Обновление docker-compose
```yaml
docling:
  build:
    context: ./services/docling
    dockerfile: Dockerfile
  image: openwebui-hub/docling:fixed
  # ... остальные настройки
```

## 🧪 Тестирование

### ✅ Результаты тестов
```
🚀 Тестирование исправленного Docling сервиса
============================================================

✅ Проверка здоровья Docling: OK
✅ Проверка OSD в Tesseract: OK  
✅ Проверка логов Docling: Чистые, ошибок не найдено
✅ Подготовка тестового файла: OK

📊 Результаты: 4/4 тестов прошли
🎉 Все тесты прошли успешно! Docling исправлен.
```

### 🔍 Проверка интеграции с Open WebUI
- ✅ Open WebUI переключен на использование Docling
- ✅ Настройка `CONTENT_EXTRACTION_ENGINE=docling` активна
- ✅ Конфигурация в базе данных обновлена
- ✅ Сервис перезапущен и работает стабильно

## 📊 Сравнение: Docling vs Tika

| Критерий | Docling (исправленный) | Tika |
|----------|------------------------|------|
| **Статус** | ✅ Работает | ✅ Работает |
| **Форматы** | PDF, DOCX, PPTX, HTML | Широкий спектр |
| **OCR** | Tesseract + AI | Tesseract |
| **Качество извлечения** | Высокое (AI-enhanced) | Хорошее |
| **Скорость** | Средняя | Быстрая |
| **Размер образа** | ~2GB | ~500MB |
| **Стабильность** | ✅ После исправления | ✅ Стабильная |

## 🎯 Рекомендации

### 🟢 Для продакшена
1. **Используйте исправленный Docling** для лучшего качества извлечения текста
2. **Соберите образ заранее** для быстрого развертывания
3. **Мониторьте логи** на предмет новых ошибок

### 🔄 Для разработки
1. **Tika как fallback** - оставьте возможность быстрого переключения
2. **Автоматические тесты** - используйте `tests/test_docling_fixed.py`
3. **Регулярные обновления** - следите за новыми версиями Docling

## 🚀 Развертывание исправления

### Быстрое развертывание (временное)
```bash
# Установка файла в существующий контейнер
docker exec -u root open-webui-hub-docling-1 \
  wget -O /usr/share/tesseract/tessdata/osd.traineddata \
  https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata

# Перезапуск сервиса
docker-compose -f compose.local.yml restart docling
```

### Постоянное решение
```bash
# Сборка исправленного образа
docker-compose -f compose.local.yml build docling

# Перезапуск с новым образом
docker-compose -f compose.local.yml up -d docling
```

## 📝 Заметки для будущих версий

### ⚠️ Потенциальные проблемы
1. **Обновления Docling** могут снова удалить osd.traineddata
2. **Изменения в Tesseract** могут потребовать других языковых файлов
3. **Новые версии** могут исправить проблему upstream

### 🔮 Мониторинг
- Следите за релизами Docling на GitHub
- Проверяйте логи после обновлений
- Тестируйте обработку документов после изменений

## 📚 Полезные ссылки

- [Docling GitHub](https://github.com/docling-project/docling-serve)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Tesseract traineddata](https://github.com/tesseract-ocr/tessdata)
- [Issue с osd.traineddata](https://github.com/tesseract-ocr/tesseract/issues/1133)

---
**Автор:** Augment Agent  
**Статус:** ✅ Проблема решена, документация обновлена  
**Следующие шаги:** Мониторинг стабильности и тестирование в продакшене
