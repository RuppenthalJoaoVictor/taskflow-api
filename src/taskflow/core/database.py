"""Conexão com o banco de dados e fábrica de sessões."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from taskflow.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Classe base para todos os modelos do ORM."""


def get_db() -> Generator[Session, None, None]:
    """Dependency do FastAPI que garante uma sessão por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
