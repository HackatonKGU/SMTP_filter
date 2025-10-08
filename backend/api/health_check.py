from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from core.config import DB_NAME

def check_db_connection():
    try:
        engine = create_engine(f"sqlite:///{DB_NAME}")
        Session = sessionmaker(bind=engine)
        session = Session()
        session.execute(text("SELECT 1"))
        session.close()
        return "ok"
    except Exception:
        return "error"
