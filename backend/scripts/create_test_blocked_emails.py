#!/usr/bin/env python3
"""
Создает тестовые заблокированные письма для демонстрации веб-интерфейса.
"""

from database.repo import log_blocked_email
from datetime import datetime, timedelta
import random

# Тестовые данные для демонстрации
test_blocked_emails = [
    {
        "sender": "suspicious@evil.com",
        "subject": "Операция начинается",
        "body": "Завтра в 15:00 взорвем здание правительства. Все готовы к действию.",
        "threat_probability": 1
    },
    {
        "sender": "terrorist@bad.org", 
        "subject": "Urgent Plan",
        "body": "I will bomb the school tomorrow at 3pm. Everything is prepared. Kill everyone.",
        "threat_probability": 1
    },
    {
        "sender": "danger@threat.net",
        "subject": "Последнее предупреждение",
        "body": "Если не выполните наши требования, мы устроим резню в торговом центре. У нас есть оружие.",
        "threat_probability": 1
    },
    {
        "sender": "anonymous@dark.web",
        "subject": "Cyber Attack",
        "body": "We will destroy all your servers and kill your employees. This is not a joke. Terror begins now.",
        "threat_probability": 1
    },
    {
        "sender": "radical@extremist.com",
        "subject": "Джихад",
        "body": "Священная война продолжается. Сегодня мы нанесем удар по неверным. Смерть врагам!",
        "threat_probability": 1
    },
    {
        "sender": "fake.bomb@hoax.com",
        "subject": "ВНИМАНИЕ! БОМБА!",
        "body": "В здании заложена бомба. Эвакуируйтесь немедленно или все погибнут в 18:00.",
        "threat_probability": 1
    },
    {
        "sender": "psycho@killer.net",
        "subject": "Месть",
        "body": "Я найду всех ваших сотрудников и убью их по одному. Никто не останется в живых.",
        "threat_probability": 1
    },
    {
        "sender": "violence@gang.org",
        "subject": "Warning",
        "body": "Your family will suffer if you don't pay. We know where you live. Terror is coming.",
        "threat_probability": 1
    }
]

def create_test_emails():
    """Создает тестовые заблокированные письма в базе данных."""
    print("📧 Создание тестовых заблокированных писем...")
    
    for i, email_data in enumerate(test_blocked_emails, 1):
        try:
            log_blocked_email(
                sender=email_data["sender"],
                subject=email_data["subject"],
                body=email_data["body"],
                threat_prob=email_data["threat_probability"]
            )
            print(f"✅ {i}. Письмо от {email_data['sender']} добавлено")
            
        except Exception as e:
            print(f"❌ Ошибка добавления письма {i}: {e}")
    
    print(f"\n🎉 Создано {len(test_blocked_emails)} тестовых писем!")
    print("Теперь можете открыть веб-интерфейс для просмотра:")
    print("  • Главная: http://localhost:8000/interface/")
    print("  • Заблокированные: http://localhost:8000/interface/blocked.html")

if __name__ == "__main__":
    create_test_emails()