"""Regras de negócio para cadastro e acompanhamento de projetos."""

from datetime import date

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
