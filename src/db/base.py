"""Engine, sessão e base declarativa do SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import get_database_url

engine = create_engine(get_database_url(), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base declarativa para todos os modelos ORM."""


def init_db() -> None:
    """Cria as tabelas no banco de dados caso ainda não existam.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: Se a conexão com o banco falhar.
    """
    from src.db import models  # noqa: F401  garante o registro dos modelos

    Base.metadata.create_all(bind=engine)
