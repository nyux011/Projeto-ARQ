"""Página de cadastro e acompanhamento de projetos em formato Kanban e Lista."""

from datetime import date

import pandas as pd
import streamlit as st
from streamlit_sortables import sort_items

from src.db.models import Prioridade, StatusProjeto
from src.services import projetos_service
from src.ui.formatting import formatar_data, formatar_moeda, horas_minutos_para_float
from src.ui.styles import PRIORIDADE_COLORS, STATUS_COLORS, inject_global_css, status_badge

inject_global_css()

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

AJUSTES_PARCELA = {
    "Sem ajuste": 1.0,
    "Desconto de 5%": 0.95,
    "Desconto de 10%": 0.90,
    "Desconto de 15%": 0.85,
    "Desconto de 20%": 0.80,
    "Juros de 5%": 1.05,
    "Juros de 10%": 1.10,
    "Juros de 15%": 1.15,
    "Juros de 20%": 1.20,
}

st.title(":material/view_kanban: Projetos")

with st.expander("Novo projeto", icon=":material/add:"):
    with st.form("novo_projeto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_projeto = st.text_input("Nome do projeto")
            cliente_nome = st.text_input("Nome do(s) cliente(s)*")
            cliente_telefone = st.text_input("Telefone")
            cliente_email = st.text_input("E-mail")
            cidade = st.text_input("Cidade")
        with col2:
            valor_total = st.number_input("Valor total (R$)*", min_value=0.0, step=100.0)
            status = st.selectbox("Etapa atual", list(StatusProjeto), format_func=lambda s: s.value)
            prioridade = st.selectbox("Prioridade", list(Prioridade), index=1, format_func=lambda p: p.value)
            data_inicio = st.date_input("Data de início", value=date.today(), format="DD/MM/YYYY")
            data_previsao_entrega = st.date_input("Previsão de entrega", value=None, format="DD/MM/YYYY")
            st.caption("Estimativa de horas")
            ce1, ce2 = st.columns(2)
            est_horas = ce1.number_input("Horas", min_value=0, step=1, key="novo_est_h")
            est_minutos = ce2.number_input("Minutos", min_value=0, max_value=59, step=5, key="novo_est_m")
        descricao = st.text_area("Escopo / descrição")
        observacoes = st.text_area("Observações")
        enviado = st.form_submit_button("Salvar projeto")

        if enviado:
            if not cliente_nome or valor_total <= 0:
                st.error("Informe ao menos o nome do cliente e um valor total maior que zero.")
            else:
                projetos_service.criar_projeto(
                    nome_projeto=nome_projeto,
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
                    estimativa_horas=horas_minutos_para_float(est_horas, est_minutos) or None,
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
        label_por_id = {p.id: f"#{p.id} · {p.nome_projeto or p.cliente_nome}" for p in projetos}
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
        .sortable-container:nth-of-type(3) .sortable-item { border-left: 4px solid #8a6d3b; }
        .sortable-container:nth-of-type(4) .sortable-item { border-left: 4px solid #1baf7a; }
        .sortable-container:nth-of-type(5) .sortable-item { border-left: 4px solid #0ca30c; }
        .sortable-container:nth-of-type(6) .sortable-item { border-left: 4px solid #d03b3b; }
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
                c1, c2 = st.columns([3, 1.2])
                c1.markdown(f"**{projeto.nome_projeto or 'Sem nome definido'}**")
                c1.caption(projeto.cliente_nome)
                c2.markdown(
                    status_badge(projeto.status.value, STATUS_COLORS[projeto.status.value]),
                    unsafe_allow_html=True,
                )

st.divider()
st.subheader("Detalhes e parcelas")

for projeto in projetos:
    titulo = f"{projeto.nome_projeto} — {projeto.cliente_nome}" if projeto.nome_projeto else projeto.cliente_nome
    with st.expander(f"{titulo} — {projeto.status.value}"):
        colN, colC = st.columns(2)
        novo_nome_projeto = colN.text_input(
            "Nome do projeto", value=projeto.nome_projeto or "", key=f"nome_{projeto.id}"
        )
        colC.write(f"**Valor total:** {formatar_moeda(float(projeto.valor_total))}")

        col1, col2, col3 = st.columns(3)
        col1.write(f"**Cidade:** {projeto.cidade or '-'}")
        col1.write(f"**Telefone:** {projeto.cliente_telefone or '-'}")
        col2.write(f"**E-mail:** {projeto.cliente_email or '-'}")
        col2.write(f"**Início:** {formatar_data(projeto.data_inicio)}")
        col3.write(f"**Previsão de entrega:** {formatar_data(projeto.data_previsao_entrega)}")
        if projeto.descricao:
            st.write(f"**Escopo:** {projeto.descricao}")
        if projeto.observacoes:
            st.write(f"**Observações:** {projeto.observacoes}")

        colS, colP = st.columns(2)
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

        st.caption("Horas trabalhadas")
        h_atual, m_atual = divmod(round((projeto.horas_trabalhadas or 0) * 60), 60)
        colH1, colH2 = st.columns(2)
        horas_trab = colH1.number_input(
            "Horas", min_value=0, step=1, value=h_atual, key=f"horas_h_{projeto.id}"
        )
        minutos_trab = colH2.number_input(
            "Minutos", min_value=0, max_value=59, step=5, value=m_atual, key=f"horas_m_{projeto.id}"
        )

        colA, colB = st.columns(2)
        if colA.button("Salvar alterações", key=f"upd_{projeto.id}"):
            projetos_service.atualizar_projeto(
                projeto.id,
                nome_projeto=novo_nome_projeto,
                status=novo_status,
                prioridade=nova_prioridade,
                horas_trabalhadas=horas_minutos_para_float(horas_trab, minutos_trab),
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
                        "Valor": formatar_moeda(float(p.valor)),
                        "Previsto": formatar_data(p.data_prevista),
                        "Status": p.status.value,
                    }
                    for p in sorted(projeto.parcelas, key=lambda p: p.numero)
                ]
            )
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.caption("Nenhuma parcela cadastrada para este projeto.")

        st.markdown("**Gerar parcelas em lote**")
        with st.form(f"lote_parcelas_{projeto.id}", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            quantidade = c1.number_input(
                "Quantidade de parcelas", min_value=1, step=1, value=1, key=f"lote_qtd_{projeto.id}"
            )
            valor_parcela = c2.number_input(
                "Valor de cada parcela (R$)", min_value=0.0, step=50.0, key=f"lote_val_{projeto.id}"
            )
            dia_vencimento = c3.number_input(
                "Dia do vencimento", min_value=1, max_value=31, value=5, key=f"lote_dia_{projeto.id}"
            )
            c4, c5, c6 = st.columns(3)
            mes_inicial = c4.selectbox(
                "Mês da 1ª parcela", options=list(range(1, 13)), format_func=lambda m: MESES[m - 1],
                index=date.today().month - 1, key=f"lote_mes_{projeto.id}",
            )
            ano_inicial = c5.number_input(
                "Ano da 1ª parcela", min_value=2000, step=1, value=date.today().year, key=f"lote_ano_{projeto.id}"
            )
            ajuste_label = c6.selectbox(
                "Desconto / juros", options=list(AJUSTES_PARCELA.keys()), key=f"lote_ajuste_{projeto.id}"
            )
            if st.form_submit_button("Gerar parcelas"):
                multiplicador = AJUSTES_PARCELA[ajuste_label]
                valor_final = valor_parcela * multiplicador
                observacao = ajuste_label if ajuste_label != "Sem ajuste" else ""
                projetos_service.gerar_parcelas_em_lote(
                    projeto_id=projeto.id,
                    quantidade=int(quantidade),
                    valor_parcela=valor_final,
                    dia_vencimento=int(dia_vencimento),
                    mes_inicial=int(mes_inicial),
                    ano_inicial=int(ano_inicial),
                    observacao=observacao,
                )
                st.success(f"{quantidade} parcela(s) gerada(s).")
                st.rerun()

        with st.expander("Adicionar uma parcela manualmente"):
            with st.form(f"nova_parcela_{projeto.id}", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                numero = c1.number_input("Nº", min_value=1, step=1, key=f"num_{projeto.id}")
                valor_parcela_manual = c2.number_input(
                    "Valor (R$)", min_value=0.0, step=50.0, key=f"val_{projeto.id}"
                )
                data_prevista = c3.date_input("Data prevista", key=f"data_{projeto.id}", format="DD/MM/YYYY")
                descricao_parcela = st.text_input(
                    "Descrição (ex: Entrada, 1ª parcela)", key=f"desc_{projeto.id}"
                )
                if st.form_submit_button("Adicionar parcela"):
                    projetos_service.adicionar_parcela(
                        projeto_id=projeto.id,
                        numero=int(numero),
                        valor=valor_parcela_manual,
                        data_prevista=data_prevista,
                        descricao=descricao_parcela,
                    )
                    st.rerun()
