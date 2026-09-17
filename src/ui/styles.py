"""Paleta de cores e componentes visuais (cards, badges) compartilhados entre páginas."""

import streamlit as st

PALETTE = {
    "blue": "#2a78d6",
    "orange": "#eb6834",
    "aqua": "#1baf7a",
    "yellow": "#eda100",
    "magenta": "#e87ba4",
    "green": "#0ca30c",
    "red": "#d03b3b",
    "muted": "#898781",
    "brown": "#8a6d3b",
}

STATUS_COLORS = {
    "Estudo Preliminar": PALETTE["blue"],
    "Projeto Legal": PALETTE["orange"],
    "Projeto de Interiores": PALETTE["brown"],
    "Projeto Executivo": PALETTE["aqua"],
    "Concluído": PALETTE["green"],
    "Cancelado": PALETTE["red"],
}

PRIORIDADE_COLORS = {
    "Baixa": PALETTE["muted"],
    "Normal": PALETTE["blue"],
    "Alta": PALETTE["orange"],
    "Urgente": PALETTE["red"],
}


def inject_global_css() -> None:
    """Injeta o CSS global da aplicação: tipografia, barra lateral e componentes (cards/badges)."""
    st.markdown(
        """
        <style>
        html, body, [class*="css"], [data-testid="stAppViewContainer"] {
            font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
        }
        [data-testid="stSidebarNav"] a {
            font-size: 0.92rem;
            border-radius: 8px;
        }
        .sidebar-brand {
            padding: 4px 4px 14px 4px;
            border-bottom: 1px solid rgba(128,128,128,0.25);
            margin-bottom: 10px;
        }
        .sidebar-brand-title {
            font-size: 1.02rem;
            font-weight: 700;
            color: var(--text-color);
            line-height: 1.2;
        }
        .sidebar-brand-caption {
            font-size: 0.75rem;
            color: var(--text-color);
            opacity: 0.6;
        }
        .kpi-card {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128,128,128,0.25);
            border-radius: 14px;
            padding: 16px 20px;
        }
        .kpi-label {
            font-size: 0.78rem;
            color: var(--text-color);
            opacity: 0.6;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--text-color);
        }
        .status-badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            color: #ffffff;
            white-space: nowrap;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand(title: str, caption: str = "") -> None:
    """Renderiza o bloco de marca (nome da ferramenta) no topo da barra lateral.

    Args:
        title: Nome da ferramenta.
        caption: Texto curto complementar exibido abaixo do nome.
    """
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">{title}</div>
            <div class="sidebar-brand-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, accent: str = PALETTE["blue"]) -> str:
    """Monta o HTML de um card de indicador (KPI) com borda de destaque colorida.

    Args:
        label: Rótulo curto do indicador.
        value: Valor já formatado a exibir.
        accent: Cor de destaque da borda esquerda do card.

    Returns:
        HTML pronto para renderizar via st.markdown(..., unsafe_allow_html=True).
    """
    return (
        f'<div class="kpi-card" style="border-left: 4px solid {accent};">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f"</div>"
    )


def status_badge(label: str, color: str) -> str:
    """Monta o HTML de um badge colorido de status ou prioridade.

    Args:
        label: Texto do badge.
        color: Cor de fundo do badge.

    Returns:
        HTML pronto para renderizar via st.markdown(..., unsafe_allow_html=True).
    """
    return f'<span class="status-badge" style="background:{color};">{label}</span>'
