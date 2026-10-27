from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from backend.app.core.config import settings

# Берём адрес базы из конфига
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Создаёт таблицы, если их ещё нет"""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()