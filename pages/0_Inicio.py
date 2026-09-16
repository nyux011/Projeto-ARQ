"""Página inicial: explica o que é a ferramenta e como usar cada módulo."""

import streamlit as st

st.title(":material/home: Gestão de Demandas Inteligente")
st.caption("Sua central pessoal para acompanhar projetos, prazos e recebimentos de arquitetura.")

st.write("")

with st.container(border=True):
    st.subheader(":material/space_dashboard: Dashboard")
    st.write(
        "Visão geral rápida: quantos projetos estão ativos, quanto já foi recebido e o que "
        "está previsto para este mês, quanto está atrasado, quantos projetos há em cada etapa "
        "e um gráfico comparando valores recebidos e previstos por mês."
    )
    st.caption("Use esta página no início do dia para ter o panorama geral antes de entrar nos detalhes.")

with st.container(border=True):
    st.subheader(":material/view_kanban: Projetos")
    st.write(
        "Cadastro e acompanhamento de cada projeto. A aba **Kanban** mostra os projetos em colunas "
        "por etapa (Estudo Preliminar, Projeto Legal, Projeto Executivo, Concluído, Cancelado) — "
        "basta **arrastar o card** para a coluna certa para atualizar a etapa. A aba **Lista** mostra "
        "os mesmos projetos em formato de tabela, com prioridade, prazos e horas estimadas/trabalhadas."
    )
    st.write(
        "Dentro de cada projeto (seção **Detalhes e parcelas**) você edita dados do cliente, "
        "prioridade, prazos e cadastra as parcelas de pagamento combinadas."
    )
    st.caption("Use para saber em que pé cada projeto está e planejar a carga de trabalho.")

with st.container(border=True):
    st.subheader(":material/payments: Financeiro")
    st.write(
        "Controle de todas as parcelas cadastradas nos projetos: o que já foi **recebido**, o que "
        "está **previsto** e o que está **atrasado**. Marque uma parcela como paga informando a "
        "forma de pagamento (PIX, transferência, cartão, boleto ou dinheiro) e a data."
    )
    st.caption("Use para o controle financeiro do dia a dia e para consultar o histórico de recebimentos.")

st.write("")
st.info(
    "Todos os dados ficam salvos em um banco de dados próprio da aplicação — continuam disponíveis "
    "mesmo depois de fechar o navegador ou reiniciar o app.",
    icon=":material/lock:",
)
