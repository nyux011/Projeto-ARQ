"""Modelos ORM da plataforma: projetos e parcelas."""

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class StatusProjeto(str, enum.Enum):
    """Etapas possíveis de um projeto de arquitetura."""

    ESTUDO_PRELIMINAR = "Estudo Preliminar"
    PROJETO_LEGAL = "Projeto Legal"
    PROJETO_INTERIORES = "Projeto de Interiores"
    PROJETO_EXECUTIVO = "Projeto Executivo"
    CONCLUIDO = "Concluído"
    CANCELADO = "Cancelado"


class Prioridade(str, enum.Enum):
    """Nível de prioridade de um projeto."""

    BAIXA = "Baixa"
    NORMAL = "Normal"
    ALTA = "Alta"
    URGENTE = "Urgente"


class StatusParcela(str, enum.Enum):
    """Situação de pagamento de uma parcela."""

    PENDENTE = "Pendente"
    PAGO = "Pago"


class FormaPagamento(str, enum.Enum):
    """Formas de pagamento aceitas."""

    PIX = "PIX"
    TRANSFERENCIA = "Transferência bancária"
    CARTAO = "Cartão"
    BOLETO = "Boleto"
    DINHEIRO = "Dinheiro"


class Projeto(Base):
    """Projeto de arquitetura contratado por um cliente."""

    __tablename__ = "projetos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_projeto: Mapped[str | None] = mapped_column(String(200))
    cliente_nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cliente_telefone: Mapped[str | None] = mapped_column(String(30))
    cliente_email: Mapped[str | None] = mapped_column(String(150))
    cidade: Mapped[str | None] = mapped_column(String(100))
    descricao: Mapped[str | None] = mapped_column(Text)
    valor_total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    status: Mapped[StatusProjeto] = mapped_column(
        SAEnum(StatusProjeto), nullable=False, default=StatusProjeto.ESTUDO_PRELIMINAR
    )
    data_inicio: Mapped[date] = mapped_column(Date, default=date.today)
    data_previsao_entrega: Mapped[date | None] = mapped_column(Date)
    prioridade: Mapped[Prioridade] = mapped_column(SAEnum(Prioridade), nullable=False, default=Prioridade.NORMAL)
    estimativa_horas: Mapped[float | None] = mapped_column(Float)
    horas_trabalhadas: Mapped[float | None] = mapped_column(Float, default=0)
    observacoes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    parcelas: Mapped[list["Parcela"]] = relationship(
        back_populates="projeto", cascade="all, delete-orphan"
    )


class Parcela(Base):
    """Parcela financeira (recebimento previsto ou realizado) de um projeto."""

    __tablename__ = "parcelas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    projeto_id: Mapped[int] = mapped_column(ForeignKey("projetos.id"), nullable=False)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(150))
    valor: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    data_prevista: Mapped[date] = mapped_column(Date, nullable=False)
    data_pagamento: Mapped[date | None] = mapped_column(Date)
    status: Mapped[StatusParcela] = mapped_column(
        SAEnum(StatusParcela), nullable=False, default=StatusParcela.PENDENTE
    )
    forma_pagamento: Mapped[FormaPagamento | None] = mapped_column(SAEnum(FormaPagamento))
    observacoes: Mapped[str | None] = mapped_column(Text)

    projeto: Mapped["Projeto"] = relationship(back_populates="parcelas")
