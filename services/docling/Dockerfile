# Исправленный Docling с поддержкой OSD
FROM quay.io/docling-project/docling-serve:latest

# Переключаемся на root для установки недостающих файлов
USER root

# Устанавливаем недостающий файл osd.traineddata для Tesseract OCR
RUN wget -O /usr/share/tesseract/tessdata/osd.traineddata \
    https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata

# Проверяем, что файл установлен корректно
RUN ls -la /usr/share/tesseract/tessdata/osd.traineddata

# Возвращаемся к пользователю по умолчанию
USER 1001

# Проверяем доступность OSD в Tesseract
RUN tesseract --list-langs

# Метаданные
LABEL maintainer="Open WebUI Hub"
LABEL description="Docling service with OSD support fix"
LABEL version="v0.15.0-fixed"
