import asyncio
import time
from aiosmtpd.controller import Controller
from .handler import EmailHandler

class CustomSMTPHandler:
    async def handle_DATA(self, server, session, envelope):
        email_data = envelope.content.decode("utf-8", errors="ignore")
        recipients = envelope.rcpt_tos
        response = EmailHandler.process_email(envelope.mail_from, recipients, email_data)
        return response if response else "250 OK"

def run_smtp_server(port: int = 10025):
    """Запускает SMTP-сервер (блокирующий вызов)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    controller = Controller(
        CustomSMTPHandler(),
        hostname="127.0.0.1",
        port=port,
        loop=loop
    )
    
    # Эта команда блокирует, поэтому ее нужно запускать в потоке
    controller.start()
    print(f"SMTP-сервер запущен на 127.0.0.1:{port}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()
        loop.close()
