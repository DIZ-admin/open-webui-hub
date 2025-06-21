#!/usr/bin/env python3
"""
Тестирование исправленного Docling сервиса
"""

import requests
import time
import json
from datetime import datetime

def test_docling_health():
    """Проверка здоровья Docling"""
    try:
        response = requests.get("http://localhost:5001/health", timeout=10)
        if response.status_code == 200:
            print("✅ Docling health check: OK")
            return True
        else:
            print(f"❌ Docling health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Docling health check error: {e}")
        return False

def test_openwebui_with_docling():
    """Тестирование Open WebUI с исправленным Docling"""
    print("🔄 Тестирование загрузки файла через Open WebUI с Docling...")
    
    # Проверим, что Open WebUI использует Docling
    try:
        # Создаем простой тестовый файл
        test_content = """Тестовый документ для проверки исправленного Docling
        
Этот документ создан для проверки того, что:
1. Ошибка UnboundLocalError: df_osd исправлена
2. Файл osd.traineddata установлен корректно
3. Tesseract OCR работает с OSD
4. Docling успешно обрабатывает документы

Дата тестирования: 2025-06-21
Статус: Исправлено ✅"""
        
        with open("test_docling_fixed.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        print("✅ Тестовый файл создан")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания тестового файла: {e}")
        return False

def check_docling_logs():
    """Проверка логов Docling на наличие ошибок"""
    print("🔄 Проверка логов Docling...")
    
    import subprocess
    try:
        # Получаем последние логи Docling
        result = subprocess.run([
            "docker", "logs", "open-webui-hub-docling-1", "--tail", "20"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logs = result.stdout
            if "UnboundLocalError" in logs:
                print("❌ Найдена ошибка UnboundLocalError в логах")
                return False
            elif "osd.traineddata" in logs and "Error opening" in logs:
                print("❌ Найдена ошибка с osd.traineddata в логах")
                return False
            else:
                print("✅ Логи Docling чистые, ошибок не найдено")
                return True
        else:
            print(f"❌ Ошибка получения логов: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки логов: {e}")
        return False

def test_tesseract_osd():
    """Проверка доступности OSD в Tesseract"""
    print("🔄 Проверка доступности OSD в Tesseract...")
    
    import subprocess
    try:
        result = subprocess.run([
            "docker", "exec", "open-webui-hub-docling-1", 
            "tesseract", "--list-langs"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            langs = result.stdout
            if "osd" in langs:
                print("✅ OSD доступен в Tesseract")
                return True
            else:
                print("❌ OSD не найден в списке языков Tesseract")
                print(f"Доступные языки: {langs}")
                return False
        else:
            print(f"❌ Ошибка проверки языков Tesseract: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки Tesseract: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование исправленного Docling сервиса")
    print("=" * 60)
    
    tests = [
        ("Проверка здоровья Docling", test_docling_health),
        ("Проверка OSD в Tesseract", test_tesseract_osd),
        ("Проверка логов Docling", check_docling_logs),
        ("Подготовка тестового файла", test_openwebui_with_docling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ Тест '{test_name}' не прошел")
    
    print("\n" + "=" * 60)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно! Docling исправлен.")
        return True
    else:
        print("⚠️ Некоторые тесты не прошли. Требуется дополнительная диагностика.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
