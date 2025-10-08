from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from .models import BlockedEmail, init_db
from ..config import DB_NAME
from typing import List, Dict, Optional

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

def get_blocked_emails(limit: int = 50, offset: int = 0) -> List[Dict]:
    """Получает список заблокированных писем."""
    init_db()
    session = Session()
    try:
        emails = session.query(BlockedEmail)\
                       .order_by(desc(BlockedEmail.timestamp))\
                       .limit(limit)\
                       .offset(offset)\
                       .all()
        
        result = []
        for email in emails:
            result.append({
                'id': email.id,
                'sender': email.sender,
                'subject': email.subject,
                'body': email.body,
                'threat_probability': email.threat_probability,
                'timestamp': email.timestamp.isoformat() if email.timestamp else None
            })
        return result
    except Exception as e:
        print(f"Ошибка при получении писем: {e}")
        return []
    finally:
        session.close()

def get_blocked_email_by_id(email_id: int) -> Optional[Dict]:
    """Получает заблокированное письмо по ID."""
    init_db()
    session = Session()
    try:
        email = session.query(BlockedEmail).filter(BlockedEmail.id == email_id).first()
        if email:
            return {
                'id': email.id,
                'sender': email.sender,
                'subject': email.subject,
                'body': email.body,
                'threat_probability': email.threat_probability,
                'timestamp': email.timestamp.isoformat() if email.timestamp else None
            }
        return None
    except Exception as e:
        print(f"Ошибка при получении письма: {e}")
        return None
    finally:
        session.close()

def get_blocked_emails_count() -> int:
    """Возвращает общее количество заблокированных писем."""
    init_db()
    session = Session()
    try:
        count = session.query(BlockedEmail).count()
        return count
    except Exception as e:
        print(f"Ошибка при подсчете писем: {e}")
        return 0
    finally:
        session.close()

def delete_blocked_email(email_id: int) -> bool:
    """Удаляет заблокированное письмо по ID."""
    init_db()
    session = Session()
    try:
        email = session.query(BlockedEmail).filter(BlockedEmail.id == email_id).first()
        if email:
            session.delete(email)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Ошибка при удалении письма: {e}")
        return False
    finally:
        session.close()

def clear_all_blocked_emails() -> bool:
    """Очищает все заблокированные письма."""
    init_db()
    session = Session()
    try:
        session.query(BlockedEmail).delete()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Ошибка при очистке базы: {e}")
        return False
    finally:
        session.close()
