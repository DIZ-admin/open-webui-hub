#!/usr/bin/env python3
"""
Тестирование загрузки документов в Open WebUI Hub
"""

import requests
import json
import time
import os
from datetime import datetime

class DocumentUploadTester:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.session = requests.Session()
        self.test_results = {}
        
    def test_file_upload(self, file_path: str, knowledge_base_id: str = None):
        """Тестирование загрузки файла"""
        print(f"🔄 Тестирование загрузки файла: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            return False
            
        try:
            # Если нет knowledge_base_id, создаем новую базу знаний
            if not knowledge_base_id:
                knowledge_base_id = self.create_knowledge_base()
                
            if not knowledge_base_id:
                print("❌ Не удалось создать базу знаний")
                return False
                
            # Загружаем файл
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                
                upload_url = f"{self.base_url}/api/v1/knowledge/{knowledge_base_id}/file/add"
                response = self.session.post(upload_url, files=files)
                
                print(f"📤 Статус загрузки: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Файл успешно загружен: {result}")
                    return True
                else:
                    print(f"❌ Ошибка загрузки: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Исключение при загрузке: {e}")
            return False
    
    def create_knowledge_base(self):
        """Создание новой базы знаний"""
        print("🔄 Создание новой базы знаний...")
        
        try:
            create_url = f"{self.base_url}/api/v1/knowledge"
            data = {
                "name": f"Test Knowledge Base {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Тестовая база знаний для проверки загрузки документов"
            }
            
            response = self.session.post(create_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                kb_id = result.get('id')
                print(f"✅ База знаний создана: {kb_id}")
                return kb_id
            else:
                print(f"❌ Ошибка создания базы знаний: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Исключение при создании базы знаний: {e}")
            return None
    
    def list_knowledge_bases(self):
        """Получение списка баз знаний"""
        try:
            list_url = f"{self.base_url}/api/v1/knowledge"
            response = self.session.get(list_url)
            
            if response.status_code == 200:
                result = response.json()
                print(f"📋 Найдено баз знаний: {len(result)}")
                return result
            else:
                print(f"❌ Ошибка получения списка: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Исключение при получении списка: {e}")
            return []
    
    def test_search(self, query: str, knowledge_base_id: str):
        """Тестирование поиска в базе знаний"""
        print(f"🔍 Тестирование поиска: '{query}'")
        
        try:
            search_url = f"{self.base_url}/api/v1/knowledge/{knowledge_base_id}/search"
            data = {"query": query}
            
            response = self.session.post(search_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Поиск выполнен, найдено результатов: {len(result.get('results', []))}")
                return result
            else:
                print(f"❌ Ошибка поиска: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Исключение при поиске: {e}")
            return None
    
    def run_comprehensive_test(self):
        """Комплексное тестирование"""
        print("🚀 Начало комплексного тестирования загрузки документов")
        print("=" * 60)
        
        # 1. Проверка доступности API
        try:
            health_response = self.session.get(f"{self.base_url}/")
            if health_response.status_code != 200:
                print("❌ Open WebUI недоступен")
                return False
            print("✅ Open WebUI доступен")
        except:
            print("❌ Не удается подключиться к Open WebUI")
            return False
        
        # 2. Получение списка баз знаний
        knowledge_bases = self.list_knowledge_bases()
        
        # 3. Тестирование загрузки тестового файла
        test_file = "test_document.txt"
        if os.path.exists(test_file):
            success = self.test_file_upload(test_file)
            if success:
                print("✅ Тестирование загрузки завершено успешно")
            else:
                print("❌ Тестирование загрузки не удалось")
        else:
            print(f"❌ Тестовый файл не найден: {test_file}")
        
        print("=" * 60)
        print("🏁 Тестирование завершено")

def main():
    tester = DocumentUploadTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
