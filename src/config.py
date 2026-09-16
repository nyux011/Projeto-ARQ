"""Configuração da aplicação: caminhos e string de conexão do banco de dados."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_SQLITE_URL = f"sqlite:///{(DATA_DIR / 'plataforma.db').as_posix()}"


def get_database_url() -> str:
    """Resolve a string de conexão do banco de dados.

    Ordem de prioridade: st.secrets["DATABASE_URL"] (deploy no Streamlit
    Cloud) > variável de ambiente DATABASE_URL > variável de ambiente
    SUPABASE_URL > SQLite local, usado como padrão para desenvolvimento.
    As variáveis de ambiente são lidas pelo próprio processo do sistema
    operacional, nunca a partir de um arquivo .env por esta aplicação.

    Returns:
        URL de conexão compatível com SQLAlchemy.
    """
    try:
        import streamlit as st

        if "DATABASE_URL" in st.secrets and st.secrets["DATABASE_URL"]:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass

    return os.getenv("DATABASE_URL") or os.getenv("SUPABASE_URL") or DEFAULT_SQLITE_URL
