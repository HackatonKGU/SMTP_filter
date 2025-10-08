from email.parser import Parser
from typing import Optional
from ollama.client import classify_with_ollama
from database.repo import log_blocked_email

class EmailHandler:
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
    def process_email(sender: str, email_data: str) -> Optional[str]:
        """
        Обрабатывает письмо: извлекает текст, классифицирует и блокирует при необходимости.
        Возвращает:
        - "550 Message blocked" если угроза,
        - None если письмо безопасно.
        """
        subject, body = EmailHandler.extract_email_text(email_data)
        threat_prob = classify_with_ollama(subject + "\n" + body)

        if threat_prob == 1:
            print(f"🚨 Блокировка письма от {sender}. Угроза: {threat_prob}")
            log_blocked_email(sender, subject, body, threat_prob)
            return "550 Message blocked due to threat detection"
        else:
            print(f"✅ Письмо от {sender} пропущено. Угроза: {threat_prob}")
            return None
