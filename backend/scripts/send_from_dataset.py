#!/usr/bin/env python3
"""
Отправляет случайные сообщения из датасета для стресс-тестирования системы.
"""

import csv
import random
import smtplib
import time
from email.mime.text import MIMEText

# --- Настройки ---
DATASET_PATH = 'spam_filter_dataset2.csv'  # Путь к датасету
SMTP_HOST = 'localhost'
SMTP_PORT = 10025
SENDER_EMAIL = 'test@dataset-sender.com'
RECIPIENT_EMAIL = 'recipient@example.com'

NUM_SAFE = 15      # Количество безопасных сообщений для отправки
NUM_THREATS = 15   # Количество сообщений с угрозами

# --- Функции ---

def load_messages_from_dataset(path: str):
    """Загружает сообщения из CSV-файла, разделяя их на безопасные и угрозы."""
    safe_messages = []
    threat_messages = []
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                message_text = row['text']
                label = int(row['label'])
                
                # Тема и тело содержат полный текст для максимального контекста
                subject = message_text[:70] # Ограничим тему для почтовых клиентов
                body = message_text
                
                message = {"subject": subject, "body": body}
                
                if label == 0:
                    safe_messages.append(message)
                else:
                    threat_messages.append(message)
                    
    except FileNotFoundError:
        print(f"Ошибка: Файл датасета не найден по пути '{path}'")
        return None, None
        
    print(f"Загружено сообщений из датасета: {len(safe_messages)} безопасных, {len(threat_messages)} с угрозами.")
    return safe_messages, threat_messages

def send_email(subject: str, body: str, sender: str, recipient: str):
    """Отправляет одно электронное письмо."""
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"   - Ошибка отправки: {e}")
        return False


def main():
    """Главная функция для запуска отправки."""
    print("--- Запуск скрипта отправки сообщений из датасета ---")
    
    # 1. Загружаем сообщения
    safe_messages, threat_messages = load_messages_from_dataset(DATASET_PATH)
    if safe_messages is None:
        return

    # 2. Выбираем случайные сообщения
    if len(safe_messages) < NUM_SAFE:
        print(f"Предупреждение: В датасете меньше {NUM_SAFE} безопасных сообщений. Использую все {len(safe_messages)}.")
        selected_safe = safe_messages
    else:
        selected_safe = random.sample(safe_messages, NUM_SAFE)
        
    if len(threat_messages) < NUM_THREATS:
        print(f"Предупреждение: В датасете меньше {NUM_THREATS} сообщений с угрозами. Использую все {len(threat_messages)}.")
        selected_threats = threat_messages
    else:
        selected_threats = random.sample(threat_messages, NUM_THREATS)

    # 3. Объединяем и перемешиваем
    all_to_send = selected_safe + selected_threats
    random.shuffle(all_to_send)
    
    total_to_send = len(all_to_send)
    print(f"\nПодготовлено к отправке {total_to_send} сообщений ({len(selected_safe)} безопасных, {len(selected_threats)} с угрозами).")
    print("---")

    # 4. Отправляем письма
    sent_count = 0
    for i, message in enumerate(all_to_send, 1):
        print(f"Отправка {i}/{total_to_send}: Тема: '{message['subject']}'")
        if send_email(message['subject'], message['body'], SENDER_EMAIL, RECIPIENT_EMAIL):
            sent_count += 1
        time.sleep(0.5)  # Небольшая задержка, чтобы не перегружать сервер
    
    print("---")
    print(f"Завершено. Отправлено {sent_count} из {total_to_send} сообщений.")
    print(f"Проверьте результаты в MailHog (http://localhost:8025) и в панели заблокированных писем.")


if __name__ == "__main__":
    main()
