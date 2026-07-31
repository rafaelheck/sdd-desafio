"""Fabricas de apoio para os testes (registros brutos, despesas, politica, cambio).

Modelo spec 1.4: `normaliza_despesa` recebe um `Cambio`; despesas tem `valor_origem`
/`valor_base`/`moeda_norm`/`em_viagem`. `CAMBIO_PADRAO` tem `moeda_base` BRL e algumas
taxas para exercitar conversao/viagem sem depender dos arquivos empacotados.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from src.modelo import Cambio, CategoriaConfig, Despesa, Periodo, Politica
from src.regras import normaliza_despesa, valida_cambio

# Cambio de teste: base BRL, com USD/EUR em algumas datas (e um empate proposital).
CAMBIO_PADRAO = Cambio(
    moeda_base="BRL",
    taxas={
        date(2026, 7, 14): {"USD": Decimal("5.44"), "EUR": Decimal("5.93")},
        date(2026, 7, 15): {"USD": Decimal("5.39"), "EUR": Decimal("5.88")},
        date(2026, 7, 17): {"USD": Decimal("5.47"), "EUR": Decimal("5.96")},
        date(2026, 7, 20): {"USD": Decimal("5.50"), "EUR": Decimal("6.01")},
    },
)

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


def despesa(cambio: Cambio = CAMBIO_PADRAO, **over) -> Despesa:
    """Despesa normalizada e convertida (valor_base preenchido) a partir de um cru."""
    d = normaliza_despesa(bruto(**over), cambio)
    valida_cambio(d, cambio)
    return d


def aceita(
    valor_base, *, data: str = "2026-07-03", em_viagem: bool = False, **over
) -> Despesa:
    """Despesa ja aceita com `valor_base` explicito (util para testes de teto)."""
    valor = Decimal(str(valor_base))
    d = despesa(valor=valor, data=data, **over)
    d.em_viagem = em_viagem
    d.valor_base = valor
    return d


def config(limite, periodicidade="dia", observacao=None) -> CategoriaConfig:
    return CategoriaConfig(
        limite=Decimal(str(limite)), periodicidade=periodicidade, observacao=observacao
    )


def politica(
    conjunto: dict[str, CategoriaConfig] | None = None,
    *,
    padrao: dict[str, CategoriaConfig] | None = None,
    centros: dict[str, dict[str, CategoriaConfig]] | None = None,
    limiar_nf="100",
    acrescimo_viagem_pct="50",
) -> Politica:
    """Politica de teste; `conjunto` vira o objeto `padrao` se `padrao` nao for dado."""
    if padrao is None:
        padrao = conjunto or {"alimentacao": config("60")}
    return Politica(
        padrao=padrao,
        centros_custo=centros or {},
        limiar_nf=Decimal(str(limiar_nf)),
        acrescimo_viagem_pct=Decimal(str(acrescimo_viagem_pct)),
    )


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
