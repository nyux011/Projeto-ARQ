"""Regras de negócio para cadastro e acompanhamento de projetos."""

import calendar
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import selectinload

from src.db.base import SessionLocal
from src.db.models import Parcela, Prioridade, Projeto, StatusProjeto


def listar_projetos(status: StatusProjeto | None = None) -> list[Projeto]:
    """Lista projetos cadastrados, opcionalmente filtrados por status.

    As parcelas são carregadas antecipadamente para que continuem acessíveis
    depois que a sessão do banco for encerrada.

    Args:
        status: Etapa do projeto a filtrar. Se None, retorna todos.

    Returns:
        Lista de projetos ordenados do mais recente para o mais antigo.
    """
    with SessionLocal() as session:
        query = session.query(Projeto).options(selectinload(Projeto.parcelas))
        if status is not None:
            query = query.filter(Projeto.status == status)
        return query.order_by(Projeto.created_at.desc()).all()


def obter_projeto(projeto_id: int) -> Projeto | None:
    """Busca um projeto pelo id, incluindo suas parcelas.

    Args:
        projeto_id: Identificador do projeto.

    Returns:
        O projeto encontrado ou None.
    """
    with SessionLocal() as session:
        return (
            session.query(Projeto)
            .options(selectinload(Projeto.parcelas))
            .filter(Projeto.id == projeto_id)
            .one_or_none()
        )


def criar_projeto(
    cliente_nome: str,
    valor_total: float,
    nome_projeto: str = "",
    cliente_telefone: str = "",
    cliente_email: str = "",
    cidade: str = "",
    descricao: str = "",
    status: StatusProjeto = StatusProjeto.ESTUDO_PRELIMINAR,
    prioridade: Prioridade = Prioridade.NORMAL,
    data_inicio: date | None = None,
    data_previsao_entrega: date | None = None,
    estimativa_horas: float | None = None,
    observacoes: str = "",
) -> Projeto:
    """Cria um novo projeto.

    Args:
        cliente_nome: Nome do cliente contratante.
        valor_total: Valor total contratado para o projeto.
        nome_projeto: Nome/identificação do projeto (ex: "Residência Alto Padrão").
        cliente_telefone: Telefone de contato do cliente.
        cliente_email: E-mail de contato do cliente.
        cidade: Cidade onde o projeto será executado.
        descricao: Escopo/descrição livre do projeto.
        status: Etapa inicial do projeto.
        prioridade: Nível de prioridade do projeto.
        data_inicio: Data de início do projeto.
        data_previsao_entrega: Data prevista para entrega final.
        estimativa_horas: Estimativa de horas de trabalho para o projeto.
        observacoes: Observações gerais.

    Returns:
        O projeto criado, já persistido.
    """
    with SessionLocal() as session:
        projeto = Projeto(
            nome_projeto=nome_projeto,
            cliente_nome=cliente_nome,
            cliente_telefone=cliente_telefone,
            cliente_email=cliente_email,
            cidade=cidade,
            descricao=descricao,
            valor_total=valor_total,
            status=status,
            prioridade=prioridade,
            data_inicio=data_inicio or date.today(),
            data_previsao_entrega=data_previsao_entrega,
            estimativa_horas=estimativa_horas,
            horas_trabalhadas=0,
            observacoes=observacoes,
        )
        session.add(projeto)
        session.commit()
        session.refresh(projeto)
        return projeto


def atualizar_projeto(projeto_id: int, **campos) -> Projeto | None:
    """Atualiza campos de um projeto existente.

    Args:
        projeto_id: Identificador do projeto a atualizar.
        **campos: Pares campo/valor a serem alterados no projeto.

    Returns:
        O projeto atualizado ou None se não encontrado.
    """
    with SessionLocal() as session:
        projeto = session.get(Projeto, projeto_id)
        if projeto is None:
            return None
        for campo, valor in campos.items():
            setattr(projeto, campo, valor)
        session.commit()
        session.refresh(projeto)
        return projeto


def deletar_projeto(projeto_id: int) -> None:
    """Remove um projeto e suas parcelas associadas.

    Args:
        projeto_id: Identificador do projeto a remover.
    """
    with SessionLocal() as session:
        projeto = session.get(Projeto, projeto_id)
        if projeto is not None:
            session.delete(projeto)
            session.commit()


def adicionar_parcela(
    projeto_id: int,
    numero: int,
    valor: float,
    data_prevista: date,
    descricao: str = "",
    observacoes: str = "",
) -> Parcela:
    """Adiciona uma parcela de recebimento a um projeto.

    Args:
        projeto_id: Identificador do projeto.
        numero: Número sequencial da parcela.
        valor: Valor previsto da parcela.
        data_prevista: Data prevista para o recebimento.
        descricao: Descrição da parcela (ex: "Entrada", "Estudo Preliminar").
        observacoes: Observações gerais.

    Returns:
        A parcela criada, já persistida.
    """
    with SessionLocal() as session:
        parcela = Parcela(
            projeto_id=projeto_id,
            numero=numero,
            valor=valor,
            data_prevista=data_prevista,
            descricao=descricao,
            observacoes=observacoes,
        )
        session.add(parcela)
        session.commit()
        session.refresh(parcela)
        return parcela


def gerar_parcelas_em_lote(
    projeto_id: int,
    quantidade: int,
    valor_parcela: float,
    dia_vencimento: int,
    mes_inicial: int,
    ano_inicial: int,
    observacao: str = "",
) -> list[Parcela]:
    """Gera várias parcelas de uma vez, uma por mês, num dia fixo do mês.

    Args:
        projeto_id: Identificador do projeto.
        quantidade: Quantidade de parcelas a gerar.
        valor_parcela: Valor de cada parcela (já com desconto/juros aplicado, se houver).
        dia_vencimento: Dia do mês do vencimento (ajustado automaticamente em meses mais curtos).
        mes_inicial: Mês da primeira parcela (1-12).
        ano_inicial: Ano da primeira parcela.
        observacao: Texto complementar anexado à descrição de cada parcela (ex: "Desconto de 10%").

    Returns:
        Lista das parcelas criadas, já persistidas.
    """
    with SessionLocal() as session:
        ultimo_numero = (
            session.query(func.max(Parcela.numero)).filter(Parcela.projeto_id == projeto_id).scalar() or 0
        )
        parcelas_criadas = []
        for i in range(quantidade):
            numero = ultimo_numero + i + 1
            mes_total = mes_inicial - 1 + i
            ano = ano_inicial + mes_total // 12
            mes = mes_total % 12 + 1
            ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
            dia = min(dia_vencimento, ultimo_dia_mes)

            descricao = f"Parcela {numero}"
            if observacao:
                descricao += f" ({observacao})"

            parcela = Parcela(
                projeto_id=projeto_id,
                numero=numero,
                valor=valor_parcela,
                data_prevista=date(ano, mes, dia),
                descricao=descricao,
            )
            session.add(parcela)
            parcelas_criadas.append(parcela)

        session.commit()
        for parcela in parcelas_criadas:
            session.refresh(parcela)
        return parcelas_criadas
