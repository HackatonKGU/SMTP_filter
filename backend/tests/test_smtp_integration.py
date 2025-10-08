import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.config import SMTP_PORT, MAILHOG_HOST, MAILHOG_WEB_PORT
from mailhog_manager import MailHogManager
import requests

def send_test_email(subject: str, body: str, from_addr: str = "test@example.com", 
                   to_addr: str = "recipient@example.com", smtp_port: int = SMTP_PORT):
    """Отправляет тестовое письмо через SMTP фильтр."""
    try:
        # Создаем письмо
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        
        # Добавляем тело письма
        msg.attach(MIMEText(body, 'plain'))
        
        # Отправляем через наш SMTP фильтр
        with smtplib.SMTP('localhost', smtp_port, timeout=10) as server:
            text = msg.as_string()
            server.sendmail(from_addr, [to_addr], text)
            
        print(f"✅ Письмо отправлено: {subject[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки письма: {e}")
        return False

def get_mailhog_messages():
    """Получает сообщения из MailHog."""
    try:
        response = requests.get(f"http://{MAILHOG_HOST}:{MAILHOG_WEB_PORT}/api/v1/messages")
        if response.status_code == 200:
            data = response.json()
            return data.get('items', []), data.get('total', 0)
        else:
            print(f"❌ Ошибка получения сообщений: {response.status_code}")
            return [], 0
    except Exception as e:
        print(f"❌ Ошибка соединения с MailHog: {e}")
        return [], 0

def run_integration_test():
    """Запускает полный интеграционный тест."""
    print("🧪 ИНТЕГРАЦИОННЫЙ ТЕСТ SMTP ФИЛЬТР + MailHog")
    print("=" * 60)
    
    # Проверяем, что MailHog запущен
    manager = MailHogManager()
    if not manager.is_running():
        print("❌ MailHog не запущен. Запускаю...")
        if not manager.start():
            print("❌ Не удалось запустить MailHog")
            return
        time.sleep(2)
    
    # Очищаем сообщения в MailHog
    print("🧹 Очищаю старые сообщения...")
    manager.clear_messages()
    time.sleep(1)
    
    # Тестовые письма
    test_emails = [
        {
            "name": "Безопасное письмо",
            "subject": "Встреча завтра",
            "body": "Привет! Не забудь о встрече завтра в 15:00. До свидания!",
            "expected_blocked": False
        },
        {
            "name": "Угроза взрыва",
            "subject": "Внимание!",
            "body": "Я взорву здание правительства в 18:00. Все готово.",
            "expected_blocked": True
        },
        {
            "name": "Рабочее письмо", 
            "subject": "Отчет по проекту",
            "body": "Добрый день! Отчет по проекту готов. Проверьте, пожалуйста.",
            "expected_blocked": False
        },
        {
            "name": "Угроза терроризма",
            "subject": "Операция",
            "body": "Kill everyone in the building tomorrow at 3pm. Bomb is ready.",
            "expected_blocked": True
        },
        {
            "name": "Обычное уведомление",
            "subject": "Ваш заказ готов",
            "body": "Здравствуйте! Ваш заказ №12345 готов к выдаче.",
            "expected_blocked": False
        }
    ]
    
    results = []
    
    print(f"📧 Отправляю {len(test_emails)} тестовых писем...")
    print("-" * 60)
    
    initial_count = get_mailhog_messages()[1]
    
    for i, email in enumerate(test_emails, 1):
        print(f"{i}. {email['name']}:")
        print(f"   Тема: {email['subject']}")
        
        # Отправляем письмо
        success = send_test_email(email['subject'], email['body'])
        time.sleep(2)  # Ждем обработки
        
        # Проверяем результат
        messages, total_count = get_mailhog_messages()
        received_count = total_count - initial_count
        
        if email['expected_blocked']:
            # Письмо должно быть заблокировано (не попасть в MailHog)
            if success:
                print("   ❌ ОШИБКА: Письмо было отправлено, но должно быть заблокировано")
                results.append("❌ FAIL")
            else:
                print("   ✅ Письмо заблокировано корректно")
                results.append("✅ PASS")
        else:
            # Письмо должно быть пропущено (попасть в MailHog)
            if success and received_count > len([r for r in results if "PASS" in r and "безопасн" in email['name']]):
                print(f"   ✅ Письмо пропущено и получено в MailHog")
                results.append("✅ PASS") 
            else:
                print(f"   ❌ ОШИБКА: Письмо не дошло до MailHog")
                results.append("❌ FAIL")
        
        print()
        initial_count = total_count
    
    # Итоговая статистика
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    passed = sum(1 for r in results if "PASS" in r)
    failed = sum(1 for r in results if "FAIL" in r)
    
    for i, (email, result) in enumerate(zip(test_emails, results), 1):
        print(f"{i}. {email['name']}: {result}")
    
    print("-" * 60)
    print(f"Успешных тестов: {passed}/{len(test_emails)}")
    print(f"Провалившихся: {failed}/{len(test_emails)}")
    
    if failed == 0:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
    
    # Показываем финальное состояние MailHog
    messages, total_count = get_mailhog_messages()
    print(f"\n📬 В MailHog получено сообщений: {total_count}")
    print(f"🌐 Веб-интерфейс: http://{MAILHOG_HOST}:{MAILHOG_WEB_PORT}")

if __name__ == "__main__":
    run_integration_test()