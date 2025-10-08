from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from config import DB_NAME

# База для SQLAlchemy
Base = declarative_base()

class BlockedEmail(Base):
    """Модель для заблокированных писем."""
    __tablename__ = "blocked_emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(String(255), nullable=False)
    subject = Column(Text)
    body = Column(Text)
    threat_probability = Column(Integer, nullable=False)  # 0 или 1
    timestamp = Column(DateTime, server_default=func.now())

def init_db():
    """Инициализирует базу данных."""
    engine = create_engine(f"sqlite:///{DB_NAME}")
    Base.metadata.create_all(engine)
