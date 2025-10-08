import smtplib
from email.parser import Parser
from typing import Optional
from ..ollama.client import classify_with_ollama
from ..database.repo import log_blocked_email
from ..config import MAILHOG_HOST, MAILHOG_SMTP_PORT

class EmailHandler:
    @staticmethod
    def forward_to_mailhog(sender: str, recipients: list, email_data: str) -> bool:
        """
        Пересылает письмо в MailHog.
        Возвращает True в случае успеха, False при ошибке.
        """
        try:
            # Подключаемся к MailHog SMTP серверу
            with smtplib.SMTP(MAILHOG_HOST, MAILHOG_SMTP_PORT) as server:
                # MailHog не требует аутентификации
                server.sendmail(sender, recipients, email_data)
            print(f"📬 Письмо от {sender} переслано в MailHog")
            return True
        except Exception as e:
            print(f"❌ Ошибка пересылки в MailHog: {e}")
            return False
    @staticmethod
    def extract_email_text(email_data: str) -> tuple[str, str]:
        """
        Извлекает тему и тело письма.
        Возвращает (subject, body).
        """
        email = Parser().parsestr(email_data)
        subject = email.get("Subject", "")

        body = ""
        if email.is_multipart():
            for part in email.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = email.get_payload(decode=True).decode(errors="ignore")

        return subject, body

    @staticmethod
    def process_email(sender: str, recipients: list, email_data: str) -> Optional[str]:
        """
        Обрабатывает письмо: извлекает текст, классифицирует и обрабатывает.
        Возвращает:
        - "550 Message blocked" если угроза,
        - "250 OK" если письмо безопасно и переслано.
        """
        subject, body = EmailHandler.extract_email_text(email_data)
        threat_prob = classify_with_ollama(subject + "\n" + body)

        if threat_prob == 1:
            print(f"🚨 Блокировка письма от {sender}. Угроза: {threat_prob}")
            log_blocked_email(sender, subject, body, threat_prob)
            return "550 Message blocked due to threat detection"
        else:
            print(f"✅ Письмо от {sender} безопасно. Пересылаю в MailHog...")
            
            # Пересылаем безопасное письмо в MailHog
            if EmailHandler.forward_to_mailhog(sender, recipients, email_data):
                return "250 OK"
            else:
                return "450 Temporary failure - could not forward message"
