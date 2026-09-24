from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from crisisops.core.config import get_settings


class Base(DeclarativeBase):
    """Base común de los modelos ORM.

    Los módulos son dueños de sus tablas. No importar modelos de otro módulo
    para reutilizar su lógica de negocio.
    """


settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
