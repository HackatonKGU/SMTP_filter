import subprocess
import time
import psutil
import platform
from pathlib import Path
from core.config import MAILHOG_PATH, MAILHOG_SMTP_PORT, MAILHOG_WEB_PORT, MAILHOG_HOST

class MailHogManager:
    def __init__(self):
        self.process = None
        self.mailhog_path = Path(MAILHOG_PATH)

    def is_running(self) -> bool:
        """Проверяет, запущен ли MailHog, путем проверки, слушается ли его веб-порт."""
        try:
            # Команда netstat -ano -p tcp | findstr "8025"
            # является надежным способом для Windows проверить порт.
            cmd = f'netstat -ano -p tcp | findstr ":{MAILHOG_WEB_PORT}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            # Если вывод содержит "LISTENING", значит порт занят и MailHog, скорее всего, работает.
            return "LISTENING" in result.stdout
        except Exception:
            return False
    
    def find_mailhog_process(self):
        """Находит процесс MailHog."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'MailHog' in proc.info['name'] or any('MailHog' in arg for arg in proc.info['cmdline']):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def start(self) -> bool:
        """Запускает MailHog."""
        if self.is_running():
            print(f"✅ MailHog уже запущен на порту {MAILHOG_WEB_PORT}")
            return True
        
        if not self.mailhog_path.exists():
            print(f"❌ MailHog не найден по пути: {self.mailhog_path}")
            return False
        
        try:
            print(f"🚀 Запускаю MailHog...")
            print(f"   SMTP: {MAILHOG_HOST}:{MAILHOG_SMTP_PORT}")
            print(f"   Web:  http://{MAILHOG_HOST}:{MAILHOG_WEB_PORT}")
            
            # Запускаем MailHog с настройками
            cmd = [
                str(self.mailhog_path),
                "-smtp-bind-addr", f"{MAILHOG_HOST}:{MAILHOG_SMTP_PORT}",
                "-ui-bind-addr", f"{MAILHOG_HOST}:{MAILHOG_WEB_PORT}",
                "-api-bind-addr", f"{MAILHOG_HOST}:{MAILHOG_WEB_PORT}"
            ]
            
            # Запускаем в фоновом режиме
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # Ждем запуска
            for i in range(10):
                if self.is_running():
                    print(f"✅ MailHog запущен успешно!")
                    print(f"   Веб-интерфейс: http://{MAILHOG_HOST}:{MAILHOG_WEB_PORT}")
                    return True
                time.sleep(1)
                print(f"   Ожидание запуска... ({i+1}/10)")
            
            print("❌ MailHog не удалось запустить")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка запуска MailHog: {e}")
            return False
    
    def stop(self) -> bool:
        """Останавливает MailHog."""
        try:
            # Останавливаем наш процесс
            if self.process:
                self.process.terminate()
                self.process = None
            
            # Находим и останавливаем все процессы MailHog
            proc = self.find_mailhog_process()
            if proc:
                proc.terminate()
                proc.wait(timeout=5)
                print("✅ MailHog остановлен")
                return True
            else:
                print("⚠️ Процесс MailHog не найден")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка остановки MailHog: {e}")
            return False
    
    def restart(self) -> bool:
        """Перезапускает MailHog."""
        print("🔄 Перезапуск MailHog...")
        self.stop()
        time.sleep(2)
        return self.start()
    
    def status(self):
        """Показывает статус MailHog."""
        if self.is_running():
            print(f"✅ MailHog работает:")
            print(f"   SMTP: {MAILHOG_HOST}:{MAILHOG_SMTP_PORT}")
            print(f"   Web:  http://{MAILHOG_HOST}:{MAILHOG_WEB_PORT}")
            
            # Получаем количество сообщений
            try:
                response = requests.get(f"http://{MAILHOG_HOST}:{MAILHOG_WEB_PORT}/api/v1/messages?limit=1")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Сообщений: {data.get('total', 0)}")
            except:
                pass
        else:
            print("❌ MailHog не запущен")
    
    def clear_messages(self) -> bool:
        """Очищает все сообщения в MailHog."""
        try:
            response = requests.delete(f"http://{MAILHOG_HOST}:{MAILHOG_WEB_PORT}/api/v1/messages")
            if response.status_code == 200:
                print("✅ Все сообщения удалены")
                return True
            else:
                print(f"❌ Ошибка очистки сообщений: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка очистки сообщений: {e}")
            return False

def main():
    """Интерфейс командной строки для управления MailHog."""
    import sys
    
    manager = MailHogManager()
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python mailhog_manager.py start    - Запустить MailHog")
        print("  python mailhog_manager.py stop     - Остановить MailHog")
        print("  python mailhog_manager.py restart  - Перезапустить MailHog")
        print("  python mailhog_manager.py status   - Показать статус")
        print("  python mailhog_manager.py clear    - Очистить сообщения")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        manager.start()
    elif command == "stop":
        manager.stop()
    elif command == "restart":
        manager.restart()
    elif command == "status":
        manager.status()
    elif command == "clear":
        manager.clear_messages()
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main()