#!/usr/bin/env python3
"""
Скрипт для точной диагностики сетевого подключения к Ollama из Python.
"""

import requests

OLLAMA_API_URL = "http://localhost:11434/api/tags"

def check_connection():
    print(f"--- Диагностика подключения к Ollama ---")
    print(f"Пытаюсь отправить GET-запрос на: {OLLAMA_API_URL}")
    
    try:
        response = requests.get(OLLAMA_API_URL, timeout=5) # 5 секунд таймаут
        
        # Проверяем успешность запроса
        response.raise_for_status() # Вызовет ошибку, если код ответа не 2xx
        
        print("\n[РЕЗУЛЬТАТ]: УСПЕХ!")
        print("------------------------------------------")
        print("Сетевое подключение из Python к Ollama работает корректно.")
        print("Получен ответ от сервера:")
        print(response.json())
        
    except requests.exceptions.RequestException as e:
        print("\n[РЕЗУЛЬТАТ]: ОШИБКА ПОДКЛЮЧЕНИЯ!")
        print("------------------------------------------")
        print("Не удалось подключиться к серверу Ollama.")
        print(f"Детали ошибки: {e}")
        print("\nВероятные причины:")
        print("1. Сервер Ollama не запущен (выполните 'ollama serve' в отдельном терминале).")
        print("2. (Наиболее вероятно) Брандмауэр Windows или антивирус блокирует подключение для python.exe.")
        print("3. Неправильный адрес или порт сервера Ollama.")

if __name__ == "__main__":
    check_connection()
