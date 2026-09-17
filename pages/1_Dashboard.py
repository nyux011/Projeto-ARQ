"""Dashboard com indicadores gerais de projetos e financeiro."""

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.db.models import StatusParcela, StatusProjeto
from src.services import financeiro_service, projetos_service
from src.ui.formatting import formatar_moeda
from src.ui.styles import PALETTE, STATUS_COLORS, inject_global_css, kpi_card, status_badge

inject_global_css()
st.title(":material/space_dashboard: Dashboard")

projetos = projetos_service.listar_projetos()
projetos_ativos = [p for p in projetos if p.status not in (StatusProjeto.CONCLUIDO, StatusProjeto.CANCELADO)]

hoje = date.today()
resumo_mes = financeiro_service.resumo_financeiro(mes=hoje.month, ano=hoje.year)
todas_parcelas = financeiro_service.listar_parcelas()
total_atrasado = sum(float(p.valor) for p in todas_parcelas if financeiro_service.esta_atrasada(p))

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("Projetos ativos", str(len(projetos_ativos)), PALETTE["blue"]), unsafe_allow_html=True)
with c2:
    st.markdown(
        kpi_card("Recebido no mês", formatar_moeda(resumo_mes["recebido"]), PALETTE["green"]),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        kpi_card("Previsto no mês", formatar_moeda(resumo_mes["previsto"]), PALETTE["yellow"]),
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(kpi_card("Total atrasado", formatar_moeda(total_atrasado), PALETTE["red"]), unsafe_allow_html=True)

st.write("")
col1, col2 = st.columns([1, 1.6])

with col1:
    st.subheader("Projetos por etapa")
    if projetos:
        for status in StatusProjeto:
            qtd = sum(1 for p in projetos if p.status == status)
            if qtd == 0:
                continue
            with st.container(border=True):
                linha1, linha2 = st.columns([3, 1])
                linha1.markdown(status_badge(status.value, STATUS_COLORS[status.value]), unsafe_allow_html=True)
                linha2.markdown(f"**{qtd}**")
    else:
        st.info("Nenhum projeto cadastrado ainda.")

with col2:
    st.subheader("Recebimentos por mês")
    if todas_parcelas:
        df = pd.DataFrame(
            [
                {
                    "mes": p.data_prevista.strftime("%Y-%m"),
                    "valor": float(p.valor),
                    "situacao": "Recebido" if p.status == StatusParcela.PAGO else "Previsto",
                }
                for p in todas_parcelas
            ]
        )
        resumo = df.groupby(["mes", "situacao"], as_index=False)["valor"].sum().sort_values("mes")
        recebido_df = resumo[resumo["situacao"] == "Recebido"]
        previsto_df = resumo[resumo["situacao"] == "Previsto"]

        fig = go.Figure()
        fig.add_bar(
            x=previsto_df["mes"],
            y=previsto_df["valor"],
            name="Previsto",
            marker_color=PALETTE["blue"],
            text=[formatar_moeda(v, decimais=0) for v in previsto_df["valor"]],
            textposition="outside",
            textangle=-90,
            textfont=dict(size=12),
            cliponaxis=False,
            hovertemplate="%{x}<br>Previsto: R$ %{y:,.2f}<extra></extra>",
        )
        fig.add_bar(
            x=recebido_df["mes"],
            y=recebido_df["valor"],
            name="Recebido",
            marker_color=PALETTE["green"],
            text=[formatar_moeda(v, decimais=0) for v in recebido_df["valor"]],
            textposition="outside",
            textangle=-90,
            textfont=dict(size=12),
            cliponaxis=False,
            hovertemplate="%{x}<br>Recebido: R$ %{y:,.2f}<extra></extra>",
        )
        maior_valor = float(resumo["valor"].max())
        fig.update_layout(
            barmode="group",
            bargap=0.25,
            uniformtext=dict(mode="show", minsize=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(zeroline=False, title=None, showticklabels=False, range=[0, maior_valor * 1.6]),
            xaxis=dict(title=None),
            height=420,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma parcela cadastrada ainda.")
