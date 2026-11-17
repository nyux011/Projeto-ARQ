"""Configuração da aplicação: caminhos e string de conexão do banco de dados."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_SQLITE_URL = f"sqlite:///{(DATA_DIR / 'plataforma.db').as_posix()}"


def _usar_driver_psycopg2(url: str) -> str:
    """Normaliza uma URL do Postgres para usar o driver psycopg2.

    Aceita URLs com prefixo "postgres://", "postgresql://" ou com outro
    driver já indicado (ex.: "postgresql+pg8000://"), todas convertidas para
    "postgresql+psycopg2://".

    Args:
        url: URL de conexão original.

    Returns:
        URL com o dialeto "+psycopg2" aplicado, se for uma URL do Postgres.
    """
    for prefixo in ("postgresql+pg8000://", "postgresql://", "postgres://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg2://" + url[len(prefixo):]
    return url


def get_database_url() -> str:
    """Resolve a string de conexão do banco de dados.

    Ordem de prioridade: st.secrets (DATABASE_URL ou SUPABASE_URL, usado no
    deploy no Streamlit Cloud) > variável de ambiente DATABASE_URL ou
    SUPABASE_URL > SQLite local, usado como padrão para desenvolvimento.
    As variáveis de ambiente são lidas pelo próprio processo do sistema
    operacional, nunca a partir de um arquivo .env por esta aplicação.

    Returns:
        URL de conexão compatível com SQLAlchemy (Postgres normalizado para o driver psycopg2).
    """
    try:
        import streamlit as st

        for nome in ("DATABASE_URL", "SUPABASE_URL"):
            if nome in st.secrets and st.secrets[nome]:
                return _usar_driver_psycopg2(st.secrets[nome])
    except Exception:
        pass

    url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_URL")
    if url:
        return _usar_driver_psycopg2(url)
    return DEFAULT_SQLITE_URL
