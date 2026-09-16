r"""Testa a conexão com o banco de dados configurado (DATABASE_URL) e cria as tabelas.

Uso:
    $env:DATABASE_URL = "postgresql://usuario:senha@host:5432/postgres"
    .\.venv\Scripts\python.exe scripts\testar_conexao.py
"""

import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402

from src.config import get_database_url  # noqa: E402
from src.db.base import engine, init_db  # noqa: E402


def ofuscar_url(url: str) -> str:
    """Oculta usuário e senha de uma URL de conexão para exibição segura em log.

    Args:
        url: URL de conexão completa.

    Returns:
        URL com usuário e senha substituídos por asteriscos.
    """
    partes = urlsplit(url)
    host_info = partes.hostname or ""
    if partes.port:
        host_info += f":{partes.port}"
    return f"{partes.scheme}://***:***@{host_info}{partes.path}"


def main() -> int:
    """Testa a conexão com o banco e cria/verifica as tabelas em caso de sucesso.

    Returns:
        Código de saída: 0 em caso de sucesso, 1 em caso de falha.
    """
    url = get_database_url()
    print(f"Testando conexão com: {ofuscar_url(url)}")

    try:
        with engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))
        init_db()
    except SQLAlchemyError as erro:
        print(f"Falha na conexão: {erro}")
        return 1

    print("Conexão bem-sucedida. Tabelas criadas/verificadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
