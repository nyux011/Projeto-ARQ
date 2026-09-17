"""Funções de formatação no padrão brasileiro (moeda, data e duração em horas)."""


def formatar_moeda(valor: float, decimais: int = 2) -> str:
    """Formata um valor monetário no padrão brasileiro (ponto para milhar, vírgula para decimal).

    Args:
        valor: Valor numérico a formatar.
        decimais: Quantidade de casas decimais (use 0 para rótulos compactos em gráficos).

    Returns:
        Texto no formato "R$ 1.234,56".
    """
    texto = f"{valor:,.{decimais}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_data(data) -> str:
    """Formata uma data no padrão brasileiro dia/mês/ano.

    Args:
        data: Objeto date/datetime a formatar, ou None.

    Returns:
        Texto no formato "DD/MM/AAAA", ou "-" se `data` for None.
    """
    if data is None:
        return "-"
    return data.strftime("%d/%m/%Y")


def horas_para_texto(horas: float | None) -> str:
    """Converte uma quantidade de horas em float para o formato HH:MM.

    Args:
        horas: Quantidade de horas (ex: 1.5 = 1h30). Pode ser None.

    Returns:
        Texto no formato "HH:MM".
    """
    total_minutos = round((horas or 0) * 60)
    h, m = divmod(total_minutos, 60)
    return f"{h:02d}:{m:02d}"


def horas_minutos_para_float(horas: int, minutos: int) -> float:
    """Converte horas e minutos inteiros em uma quantidade de horas em float.

    Args:
        horas: Quantidade de horas inteiras.
        minutos: Quantidade de minutos (0-59).

    Returns:
        Quantidade de horas em float (ex: 1h30 -> 1.5).
    """
    return horas + minutos / 60
