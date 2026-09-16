"""Configuração da aplicação: caminhos e string de conexão do banco de dados."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_SQLITE_URL = f"sqlite:///{(DATA_DIR / 'plataforma.db').as_posix()}"


def _usar_driver_pg8000(url: str) -> str:
    """Normaliza uma URL do Postgres para usar o driver pg8000 (puro Python).

    O pg8000 não precisa de compilação nem de bibliotecas nativas do sistema,
    ao contrário do psycopg2 — evita falhas de build quando a versão do
    Python do ambiente de deploy muda.

    Args:
        url: URL de conexão original.

    Returns:
        URL com o dialeto "+pg8000" aplicado, se for uma URL do Postgres.
    """
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+pg8000://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+pg8000://", 1)
    return url


def get_database_url() -> str:
    """Resolve a string de conexão do banco de dados.

    Ordem de prioridade: st.secrets (DATABASE_URL ou SUPABASE_URL, usado no
    deploy no Streamlit Cloud) > variável de ambiente DATABASE_URL ou
    SUPABASE_URL > SQLite local, usado como padrão para desenvolvimento.
    As variáveis de ambiente são lidas pelo próprio processo do sistema
    operacional, nunca a partir de um arquivo .env por esta aplicação.

    Returns:
        URL de conexão compatível com SQLAlchemy (Postgres normalizado para o driver pg8000).
    """
    try:
        import streamlit as st

        for nome in ("DATABASE_URL", "SUPABASE_URL"):
            if nome in st.secrets and st.secrets[nome]:
                return _usar_driver_pg8000(st.secrets[nome])
    except Exception:
        pass

    url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_URL")
    if url:
        return _usar_driver_pg8000(url)
    return DEFAULT_SQLITE_URL
