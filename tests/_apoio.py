"""Fabricas de apoio para os testes (registros brutos, despesas, periodo)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from src.modelo import Periodo
from src.regras import normaliza_despesa

_PADRAO_BRUTO = {
    "id": "d-x",
    "data": "2026-07-10",
    "categoria": "alimentacao",
    "descricao": "Almoco",
    "fornecedor": "Restaurante",
    "valor": Decimal("10.00"),
    "tem_nota_fiscal": True,
}


def bruto(**over) -> dict:
    """Registro de despesa cru, valido por padrao; sobrescreva o que precisar."""
    registro = dict(_PADRAO_BRUTO)
    registro.update(over)
    return registro


def despesa(**over):
    """Despesa ja normalizada a partir de um registro cru."""
    return normaliza_despesa(bruto(**over))


def periodo(
    inicio: str = "2026-07-01",
    fim: str = "2026-07-31",
    competencia: str = "2026-07",
) -> Periodo:
    return Periodo(
        competencia=competencia,
        inicio=date.fromisoformat(inicio),
        fim=date.fromisoformat(fim),
    )
