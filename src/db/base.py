"""Engine, sessão e base declarativa do SQLAlchemy."""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import get_database_url

engine = create_engine(get_database_url(), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base declarativa para todos os modelos ORM."""


def _aplicar_migracoes() -> None:
    """Aplica ajustes de esquema em bancos já existentes, sem apagar dados.

    O Postgres suporta "IF NOT EXISTS" nessas operações; o SQLite não, então
    para o SQLite a tentativa é feita e o erro de "coluna já existe" é
    ignorado (é o comportamento esperado quando a tabela já foi criada com
    a coluna nova pelo create_all).
    """
    if engine.dialect.name == "postgresql":
        with engine.begin() as conexao:
            conexao.execute(text("ALTER TABLE projetos ADD COLUMN IF NOT EXISTS nome_projeto VARCHAR(200)"))
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conexao:
            conexao.execute(text("ALTER TYPE statusprojeto ADD VALUE IF NOT EXISTS 'PROJETO_INTERIORES'"))
        return

    with engine.begin() as conexao:
        try:
            conexao.execute(text("ALTER TABLE projetos ADD COLUMN nome_projeto VARCHAR(200)"))
        except (OperationalError, ProgrammingError):
            pass


def init_db() -> None:
    """Cria as tabelas no banco de dados e aplica ajustes de esquema pendentes.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: Se a conexão com o banco falhar.
    """
    from src.db import models  # noqa: F401  garante o registro dos modelos

    Base.metadata.create_all(bind=engine)
    _aplicar_migracoes()
