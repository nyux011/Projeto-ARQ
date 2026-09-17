"""Página de controle financeiro: parcelas, recebimentos e formas de pagamento."""

from datetime import date

import pandas as pd
import streamlit as st

from src.db.models import FormaPagamento, StatusParcela
from src.services import financeiro_service
from src.ui.formatting import formatar_data, formatar_moeda
from src.ui.styles import PALETTE, inject_global_css, kpi_card, status_badge

inject_global_css()
st.title(":material/payments: Financeiro")

col1, col2, col3 = st.columns(3)
filtro_status_label = col1.selectbox("Status", ["Todos"] + [s.value for s in StatusParcela])
data_inicio = col2.date_input("De", value=None, format="DD/MM/YYYY")
data_fim = col3.date_input("Até", value=None, format="DD/MM/YYYY")

status_filtrado = None if filtro_status_label == "Todos" else StatusParcela(filtro_status_label)
parcelas = financeiro_service.listar_parcelas(
    status=status_filtrado, data_inicio=data_inicio or None, data_fim=data_fim or None
)

recebido = sum(float(p.valor) for p in parcelas if p.status == StatusParcela.PAGO)
previsto = sum(float(p.valor) for p in parcelas if p.status == StatusParcela.PENDENTE)
atrasado = sum(float(p.valor) for p in parcelas if financeiro_service.esta_atrasada(p))

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(kpi_card("Recebido", formatar_moeda(recebido), PALETTE["green"]), unsafe_allow_html=True)
with m2:
    st.markdown(kpi_card("Previsto", formatar_moeda(previsto), PALETTE["blue"]), unsafe_allow_html=True)
with m3:
    st.markdown(kpi_card("Atrasado", formatar_moeda(atrasado), PALETTE["red"]), unsafe_allow_html=True)

st.write("")

if not parcelas:
    st.info("Nenhuma parcela encontrada para os filtros selecionados.")
else:
    for parcela in parcelas:
        atrasada = financeiro_service.esta_atrasada(parcela)
        if parcela.status == StatusParcela.PAGO:
            rotulo, cor = "Pago", PALETTE["green"]
        elif atrasada:
            rotulo, cor = "Atrasada", PALETTE["red"]
        else:
            rotulo, cor = "Pendente", PALETTE["yellow"]

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1.4])
            c1.markdown(f"**{parcela.projeto.cliente_nome}**")
            c1.caption(f"Parcela {parcela.numero} · {parcela.descricao or 'sem descrição'}")
            c2.markdown(f"**{formatar_moeda(float(parcela.valor))}**")
            c3.markdown(f"Previsto: {formatar_data(parcela.data_prevista)}")
            c4.markdown(status_badge(rotulo, cor), unsafe_allow_html=True)

            if parcela.status == StatusParcela.PAGO:
                forma = parcela.forma_pagamento.value if parcela.forma_pagamento else "-"
                data_pg = formatar_data(parcela.data_pagamento)
                st.caption(f"Pago em {data_pg} via {forma}")
            else:
                fc1, fc2, fc3 = st.columns([2, 2, 1])
                forma_selecionada = fc1.selectbox(
                    "Forma de pagamento",
                    list(FormaPagamento),
                    format_func=lambda f: f.value,
                    key=f"forma_{parcela.id}",
                    label_visibility="collapsed",
                )
                data_pagamento = fc2.date_input(
                    "Data do pagamento",
                    value=date.today(),
                    key=f"data_{parcela.id}",
                    label_visibility="collapsed",
                    format="DD/MM/YYYY",
                )
                if fc3.button("Marcar como pago", key=f"pagar_{parcela.id}"):
                    financeiro_service.marcar_parcela_como_paga(
                        parcela.id, forma_pagamento=forma_selecionada, data_pagamento=data_pagamento
                    )
                    st.rerun()

    with st.expander("📋 Ver como tabela"):
        df = pd.DataFrame(
            [
                {
                    "Cliente": p.projeto.cliente_nome,
                    "Nº": p.numero,
                    "Descrição": p.descricao,
                    "Valor": formatar_moeda(float(p.valor)),
                    "Previsto": formatar_data(p.data_prevista),
                    "Pago em": formatar_data(p.data_pagamento),
                    "Status": p.status.value,
                    "Forma de pagamento": p.forma_pagamento.value if p.forma_pagamento else "-",
                }
                for p in parcelas
            ]
        )
        st.dataframe(df, hide_index=True, use_container_width=True)
