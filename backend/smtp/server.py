import time
from aiosmtpd.controller import Controller
from .handler import EmailHandler

class CustomSMTPHandler:
    async def handle_DATA(self, server, session, envelope):
        """Обрабатывает входящее письмо."""
        email_data = envelope.content.decode("utf-8", errors="ignore")
        response = EmailHandler.process_email(envelope.mail_from, email_data)
        return response if response else "250 OK"

def run_smtp_server(port: int = 10025):
    """Запускает SMTP-сервер."""
    controller = Controller(
        CustomSMTPHandler(),
        hostname="127.0.0.1",
        port=port
    )
    print(f"🔍 SMTP-сервер запущен на 127.0.0.1:{port}...")
    controller.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()
