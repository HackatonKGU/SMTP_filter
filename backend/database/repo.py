from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import BlockedEmail, init_db
from config import DB_NAME

# Инициализация сессии
engine = create_engine(f"sqlite:///{DB_NAME}")
Session = sessionmaker(bind=engine)

def log_blocked_email(sender: str, subject: str, body: str, threat_prob: int):
    """Логирует заблокированное письмо в базу данных."""
    init_db()  # Убедимся, что таблица существует
    session = Session()
    try:
        email = BlockedEmail(
            sender=sender,
            subject=subject,
            body=body,
            threat_probability=threat_prob
        )
        session.add(email)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Ошибка при логировании письма: {e}")
    finally:
        session.close()
