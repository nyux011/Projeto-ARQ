"""Ponto de entrada da Plataforma de Gestão de Projetos de Arquitetura."""

import streamlit as st

from src.db.base import init_db
from src.ui.styles import inject_global_css, sidebar_brand

st.set_page_config(page_title="Gestão de Demandas Inteligente", page_icon=":material/task_alt:", layout="wide")

init_db()
inject_global_css()
sidebar_brand("Gestão de Demandas Inteligente", "uso pessoal")

pagina = st.navigation(
    [
        st.Page("pages/0_Inicio.py", title="Início", icon=":material/home:", default=True),
        st.Page("pages/1_Dashboard.py", title="Dashboard", icon=":material/space_dashboard:"),
        st.Page("pages/2_Projetos.py", title="Projetos", icon=":material/view_kanban:"),
        st.Page("pages/3_Financeiro.py", title="Financeiro", icon=":material/payments:"),
    ]
)
pagina.run()
