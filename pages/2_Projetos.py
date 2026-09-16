"""Página de cadastro e acompanhamento de projetos em formato Kanban e Lista."""

from datetime import date

import pandas as pd
import streamlit as st
from streamlit_sortables import sort_items

from src.db.models import Prioridade, StatusProjeto
from src.services import projetos_service
from src.ui.styles import PRIORIDADE_COLORS, STATUS_COLORS, status_badge

st.title(":material/view_kanban: Projetos")

with st.expander("Novo projeto", icon=":material/add:"):
    with st.form("novo_projeto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cliente_nome = st.text_input("Nome do cliente*")
            cliente_telefone = st.text_input("Telefone")
            cliente_email = st.text_input("E-mail")
            cidade = st.text_input("Cidade")
        with col2:
            valor_total = st.number_input("Valor total (R$)*", min_value=0.0, step=100.0)
            status = st.selectbox("Etapa atual", list(StatusProjeto), format_func=lambda s: s.value)
            prioridade = st.selectbox("Prioridade", list(Prioridade), index=1, format_func=lambda p: p.value)
            data_inicio = st.date_input("Data de início", value=date.today())
            data_previsao_entrega = st.date_input("Previsão de entrega", value=None)
            estimativa_horas = st.number_input("Estimativa de horas", min_value=0.0, step=1.0)
        descricao = st.text_area("Escopo / descrição")
        observacoes = st.text_area("Observações")
        enviado = st.form_submit_button("Salvar projeto")

        if enviado:
            if not cliente_nome or valor_total <= 0:
                st.error("Informe ao menos o nome do cliente e um valor total maior que zero.")
            else:
                projetos_service.criar_projeto(
                    cliente_nome=cliente_nome,
                    valor_total=valor_total,
                    cliente_telefone=cliente_telefone,
                    cliente_email=cliente_email,
                    cidade=cidade,
                    descricao=descricao,
                    status=status,
                    prioridade=prioridade,
                    data_inicio=data_inicio,
                    data_previsao_entrega=data_previsao_entrega,
                    estimativa_horas=estimativa_horas or None,
                    observacoes=observacoes,
                )
                st.success("Projeto criado com sucesso.")
                st.rerun()

st.divider()

projetos = projetos_service.listar_projetos()
aba_kanban, aba_lista = st.tabs(["Kanban", "Lista"])

with aba_kanban:
    if not projetos:
        st.info("Nenhum projeto cadastrado ainda.")
    else:
        st.caption("Arraste os cards entre as colunas para atualizar a etapa do projeto.")

        projeto_por_id = {p.id: p for p in projetos}
        label_por_id = {
            p.id: f"#{p.id} · {p.cliente_nome} · R$ {float(p.valor_total):,.0f}" for p in projetos
        }
        id_por_label = {label: pid for pid, label in label_por_id.items()}

        colunas = [
            {"header": status.value, "items": [label_por_id[p.id] for p in projetos if p.status == status]}
            for status in StatusProjeto
        ]

        KANBAN_CSS = """
        .sortable-component { gap: 14px; align-items: flex-start; }
        .sortable-container { background: #f4f3f0; border-radius: 12px; padding: 10px; min-width: 210px; }
        .sortable-container-header { font-weight: 700; padding: 6px 8px; color: #52514e; font-size: 0.85rem; }
        .sortable-item {
            background: #ffffff; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;
            box-shadow: 0 1px 2px rgba(11,11,11,0.10); font-size: 0.82rem; color: #0b0b0b;
        }
        .sortable-container:nth-of-type(1) .sortable-item { border-left: 4px solid #2a78d6; }
        .sortable-container:nth-of-type(2) .sortable-item { border-left: 4px solid #eb6834; }
        .sortable-container:nth-of-type(3) .sortable-item { border-left: 4px solid #1baf7a; }
        .sortable-container:nth-of-type(4) .sortable-item { border-left: 4px solid #0ca30c; }
        .sortable-container:nth-of-type(5) .sortable-item { border-left: 4px solid #d03b3b; }
        """

        resultado = sort_items(
            colunas, multi_containers=True, direction="horizontal", custom_style=KANBAN_CSS, key="kanban_projetos"
        )

        for coluna in resultado:
            novo_status = StatusProjeto(coluna["header"])
            for label in coluna["items"]:
                projeto_id = id_por_label.get(label)
                if projeto_id is None:
                    continue
                if projeto_por_id[projeto_id].status != novo_status:
                    projetos_service.atualizar_projeto(projeto_id, status=novo_status)
                    st.rerun()

with aba_lista:
    if not projetos:
        st.info("Nenhum projeto cadastrado ainda.")
    else:
        for projeto in projetos:
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([2.4, 1.3, 1.3, 1.3, 1.3])
                c1.markdown(f"**{projeto.cliente_nome}**")
                c1.caption(projeto.cidade or "sem cidade")
                c2.caption("Data inicial")
                c2.write(projeto.data_inicio.strftime("%d/%m/%Y"))
                c3.caption("Vencimento")
                c3.write(
                    projeto.data_previsao_entrega.strftime("%d/%m/%Y") if projeto.data_previsao_entrega else "-"
                )
                c4.caption("Horas (trab. / est.)")
                c4.write(f"{projeto.horas_trabalhadas or 0:g} / {projeto.estimativa_horas or 0:g} h")
                c5.markdown(
                    status_badge(projeto.prioridade.value, PRIORIDADE_COLORS[projeto.prioridade.value]),
                    unsafe_allow_html=True,
                )
                c5.write("")
                c5.markdown(
                    status_badge(projeto.status.value, STATUS_COLORS[projeto.status.value]),
                    unsafe_allow_html=True,
                )

st.divider()
st.subheader("Detalhes e parcelas")

for projeto in projetos:
    with st.expander(f"{projeto.cliente_nome} — {projeto.status.value} — R$ {float(projeto.valor_total):,.2f}"):
        col1, col2, col3 = st.columns(3)
        col1.write(f"**Cidade:** {projeto.cidade or '-'}")
        col1.write(f"**Telefone:** {projeto.cliente_telefone or '-'}")
        col2.write(f"**E-mail:** {projeto.cliente_email or '-'}")
        col2.write(f"**Início:** {projeto.data_inicio}")
        col3.write(f"**Previsão de entrega:** {projeto.data_previsao_entrega or '-'}")
        if projeto.descricao:
            st.write(f"**Escopo:** {projeto.descricao}")
        if projeto.observacoes:
            st.write(f"**Observações:** {projeto.observacoes}")

        colS, colP, colH = st.columns(3)
        novo_status = colS.selectbox(
            "Etapa",
            list(StatusProjeto),
            index=list(StatusProjeto).index(projeto.status),
            format_func=lambda s: s.value,
            key=f"status_{projeto.id}",
        )
        nova_prioridade = colP.selectbox(
            "Prioridade",
            list(Prioridade),
            index=list(Prioridade).index(projeto.prioridade),
            format_func=lambda p: p.value,
            key=f"prioridade_{projeto.id}",
        )
        novas_horas = colH.number_input(
            "Horas trabalhadas",
            min_value=0.0,
            step=1.0,
            value=float(projeto.horas_trabalhadas or 0),
            key=f"horas_{projeto.id}",
        )

        colA, colB = st.columns(2)
        if colA.button("Salvar alterações", key=f"upd_{projeto.id}"):
            projetos_service.atualizar_projeto(
                projeto.id, status=novo_status, prioridade=nova_prioridade, horas_trabalhadas=novas_horas
            )
            st.rerun()
        if colB.button("Excluir projeto", key=f"del_{projeto.id}"):
            projetos_service.deletar_projeto(projeto.id)
            st.rerun()

        st.markdown("**Parcelas**")
        if projeto.parcelas:
            df = pd.DataFrame(
                [
                    {
                        "Nº": p.numero,
                        "Descrição": p.descricao,
                        "Valor": float(p.valor),
                        "Previsto": p.data_prevista,
                        "Status": p.status.value,
                    }
                    for p in projeto.parcelas
                ]
            )
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.caption("Nenhuma parcela cadastrada para este projeto.")

        with st.form(f"nova_parcela_{projeto.id}", clear_on_submit=True):
            st.caption("Adicionar parcela")
            c1, c2, c3 = st.columns(3)
            numero = c1.number_input("Nº", min_value=1, step=1, key=f"num_{projeto.id}")
            valor_parcela = c2.number_input("Valor (R$)", min_value=0.0, step=50.0, key=f"val_{projeto.id}")
            data_prevista = c3.date_input("Data prevista", key=f"data_{projeto.id}")
            descricao_parcela = st.text_input("Descrição (ex: Entrada, 1ª parcela)", key=f"desc_{projeto.id}")
            if st.form_submit_button("Adicionar parcela"):
                projetos_service.adicionar_parcela(
                    projeto_id=projeto.id,
                    numero=int(numero),
                    valor=valor_parcela,
                    data_prevista=data_prevista,
                    descricao=descricao_parcela,
                )
                st.rerun()
