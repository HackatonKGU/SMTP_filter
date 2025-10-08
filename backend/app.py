#!/usr/bin/env python3
"""
SMTP Filter System - Главный файл запуска
"""

import asyncio
import sys
import uvicorn
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time

# Импорты из новой структуры
from utils.mailhog_manager import MailHogManager
from core.ollama.client import test_ollama_connection
from core.smtp.server import run_smtp_server
from core.config import SMTP_PORT, API_PORT, MAILHOG_WEB_PORT, MAILHOG_HOST
from api.main import app

class SMTPFilterLauncher:
    def __init__(self):
        self.mailhog_manager = MailHogManager()

    def check_dependencies(self) -> bool:
        """Проверяет все зависимости системы."""
        print("Проверка зависимостей...")
        if not test_ollama_connection():
            print("Ollama недоступна. Убедитесь, что сервис запущен.")
            return False
        print("Ollama доступна")

        if not Path(self.mailhog_manager.mailhog_path).exists():
            print(f"MailHog не найден: {self.mailhog_manager.mailhog_path}")
            return False
        print("MailHog найден")
        return True

    def start_api_server(self):
        """Запускает API сервер uvicorn."""
        print(f"API-сервер запускается на http://0.0.0.0:{API_PORT}")
        uvicorn.run(app, host="0.0.0.0", port=API_PORT, log_level="info")

    def start_all_services(self):
        """Запускает все сервисы системы с корректной обработкой остановки."""
        print("ЗАПУСК СИСТЕМЫ SMTP ФИЛЬТРАЦИИ")
        print("=" * 50)

        if not self.check_dependencies():
            print("Проверка зависимостей не прошла. Выход.")
            return

        if not self.mailhog_manager.start():
            print("Не удалось запустить MailHog. Выход.")
            return

        print("\nЗапуск основных сервисов...")
        print("-" * 50)

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                # Запускаем SMTP и API серверы в отдельных потоках
                executor.submit(run_smtp_server, SMTP_PORT)
                executor.submit(self.start_api_server)

                print(f"SMTP фильтр запущен на порту: {SMTP_PORT}")
                print(f"API сервер запущен на порту: {API_PORT}")
                print("Система запущена. Нажмите Ctrl+C для остановки.")
                
                # Держим основной поток живым
                while True:
                    time.sleep(1)

        except KeyboardInterrupt:
            print("\nПолучен сигнал Ctrl+C. Идет остановка сервисов...")
        finally:
            print("Остановка MailHog...")
            self.mailhog_manager.stop()
            print("Все сервисы корректно остановлены.")

    def show_status(self):
        """Показывает статус всех компонентов."""
        print("СТАТУС СИСТЕМЫ")
        print("=" * 40)
        if test_ollama_connection():
            print("Ollama: Работает")
        else:
            print("Ollama: Недоступна")
        self.mailhog_manager.status()
        print(f"\nПорты:")
        print(f"  SMTP фильтр: {SMTP_PORT}")
        print(f"  API сервер: {API_PORT}")

def main():
    """Главная функция launcher."""
    launcher = SMTPFilterLauncher()
    
    if len(sys.argv) < 2:
        print("SMTP Filter System - Управление")
        print("-" * 40)
        print("  python app.py start     - Запустить всю систему")
        print("  python app.py status    - Показать статус")
        print("  python app.py stop      - Остановить MailHog")
        print("  python app.py test      - Запустить интеграционные тесты")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        launcher.start_all_services()
    elif command == "status":
        launcher.show_status()
    elif command == "stop":
        launcher.mailhog_manager.stop()
    elif command == "test":
        from tests.test_smtp_integration import run_integration_test
        run_integration_test()
    else:
        print(f"Неизвестная команда: {command}")

if __name__ == "__main__":
    main()
