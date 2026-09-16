"""Regras de negócio para controle financeiro: parcelas e recebimentos."""

from datetime import date

from sqlalchemy import extract
from sqlalchemy.orm import joinedload

from src.db.base import SessionLocal
from src.db.models import FormaPagamento, Parcela, StatusParcela


def listar_parcelas(
    status: StatusParcela | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[Parcela]:
    """Lista parcelas, opcionalmente filtradas por status e período.

    O projeto relacionado é carregado antecipadamente para que continue
    acessível depois que a sessão do banco for encerrada.

    Args:
        status: Situação da parcela a filtrar (Pendente/Pago). Se None, não filtra.
        data_inicio: Data prevista mínima (inclusive).
        data_fim: Data prevista máxima (inclusive).

    Returns:
        Lista de parcelas com o projeto relacionado já carregado.
    """
    with SessionLocal() as session:
        query = session.query(Parcela).options(joinedload(Parcela.projeto))
        if status is not None:
            query = query.filter(Parcela.status == status)
        if data_inicio is not None:
            query = query.filter(Parcela.data_prevista >= data_inicio)
        if data_fim is not None:
            query = query.filter(Parcela.data_prevista <= data_fim)
        return query.order_by(Parcela.data_prevista.asc()).all()


def esta_atrasada(parcela: Parcela) -> bool:
    """Indica se uma parcela pendente já passou da data prevista.

    Args:
        parcela: Parcela a avaliar.

    Returns:
        True se a parcela está pendente e vencida.
    """
    return parcela.status == StatusParcela.PENDENTE and parcela.data_prevista < date.today()


def marcar_parcela_como_paga(
    parcela_id: int, forma_pagamento: FormaPagamento, data_pagamento: date | None = None
) -> Parcela | None:
    """Registra o pagamento de uma parcela.

    Args:
        parcela_id: Identificador da parcela.
        forma_pagamento: Forma de pagamento utilizada.
        data_pagamento: Data em que o pagamento ocorreu (padrão: hoje).

    Returns:
        A parcela atualizada ou None se não encontrada.
    """
    with SessionLocal() as session:
        parcela = session.get(Parcela, parcela_id)
        if parcela is None:
            return None
        parcela.status = StatusParcela.PAGO
        parcela.forma_pagamento = forma_pagamento
        parcela.data_pagamento = data_pagamento or date.today()
        session.commit()
        session.refresh(parcela)
        return parcela


def resumo_financeiro(mes: int, ano: int) -> dict[str, float]:
    """Calcula o resumo financeiro (recebido, previsto, atrasado) de um mês.

    Args:
        mes: Mês de referência (1-12).
        ano: Ano de referência.

    Returns:
        Dicionário com as chaves "recebido", "previsto" e "atrasado".
    """
    with SessionLocal() as session:
        parcelas_do_mes = (
            session.query(Parcela)
            .filter(
                extract("month", Parcela.data_prevista) == mes,
                extract("year", Parcela.data_prevista) == ano,
            )
            .all()
        )
        recebido = sum(
            float(p.valor) for p in parcelas_do_mes if p.status == StatusParcela.PAGO
        )
        previsto = sum(
            float(p.valor) for p in parcelas_do_mes if p.status == StatusParcela.PENDENTE
        )
        atrasado = sum(float(p.valor) for p in parcelas_do_mes if esta_atrasada(p))
        return {"recebido": recebido, "previsto": previsto, "atrasado": atrasado}
