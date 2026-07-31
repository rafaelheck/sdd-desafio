"""Regras de negocio — uma funcao pura por RN (DT-002).

Os gates de validacao retornam `Motivo | None` (motivo da recusa, ou `None` se a
despesa passa). As funcoes de teto e agregacao calculam valores monetarios. Nada
aqui faz I/O; `calculo.py` apenas orquestra estas funcoes na ordem da Secao 8.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from src.modelo import Despesa, Motivo, Periodo, Reprovacao, ResultadoCategoria
from src.politica import (
    CASAS_DECIMAIS,
    CATEGORIAS_VALIDAS,
    LIMIAR_NOTA_FISCAL,
    LIMITE_HOSPEDAGEM,
    LIMITES_DIARIOS,
    MULTIPLICADOR_VIAGEM,
)

# Campos de negocio obrigatorios em cada registro de despesa (RN-013).
CAMPOS_OBRIGATORIOS: tuple[str, ...] = (
    "id",
    "data",
    "categoria",
    "descricao",
    "fornecedor",
    "valor",
    "tem_nota_fiscal",
)

# Ordem fixa das categorias na saida (determinismo — R-004).
ORDEM_CATEGORIAS: tuple[str, ...] = (
    "alimentacao",
    "transporte_urbano",
    "hospedagem",
)


def _quantiza(valor: Decimal) -> Decimal:
    """Arredonda para 2 casas, meio-para-cima (RN-011)."""
    return valor.quantize(CASAS_DECIMAIS, ROUND_HALF_UP)


# --------------------------------------------------------------------------- #
# Passo 1 — Validacao estrutural (RN-013)
# --------------------------------------------------------------------------- #
def valida_estrutura(bruto: object) -> Motivo | None:
    """RN-013 — campos obrigatorios presentes e tipados, `valor` numerico, `data`
    parseavel. Retorna `Motivo.REGISTRO_INVALIDO` ou `None`."""
    if not isinstance(bruto, dict):
        return Motivo.REGISTRO_INVALIDO

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in bruto or bruto[campo] is None:
            return Motivo.REGISTRO_INVALIDO

    for campo in ("id", "categoria", "descricao", "fornecedor"):
        if not isinstance(bruto[campo], str):
            return Motivo.REGISTRO_INVALIDO

    if not isinstance(bruto["tem_nota_fiscal"], bool):
        return Motivo.REGISTRO_INVALIDO

    # bool e subclasse de int; um booleano nao e um valor monetario valido.
    valor = bruto["valor"]
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal)):
        return Motivo.REGISTRO_INVALIDO

    try:
        date.fromisoformat(bruto["data"])
    except (ValueError, TypeError):
        return Motivo.REGISTRO_INVALIDO

    return None


# --------------------------------------------------------------------------- #
# Passo 2 — Normalizacao (RN-011, RN-001)
# --------------------------------------------------------------------------- #
def normaliza_despesa(bruto: dict) -> Despesa:
    """RN-011/RN-001 — arredonda `valor` a 2 casas (half-up) e deriva
    `categoria_norm` (`strip().lower()`). Assume estrutura ja validada."""
    valor_bruto = bruto["valor"]
    if isinstance(valor_bruto, float):
        # Guarda-costas: valores devem chegar como Decimal (parse_float=Decimal),
        # mas se vier float converte via texto para nao herdar erro binario.
        valor_bruto = Decimal(str(valor_bruto))
    valor = _quantiza(Decimal(valor_bruto))

    categoria = bruto["categoria"]
    return Despesa(
        id=bruto["id"],
        data=date.fromisoformat(bruto["data"]),
        categoria=categoria,
        categoria_norm=categoria.strip().lower(),
        descricao=bruto["descricao"],
        fornecedor=bruto["fornecedor"],
        valor=valor,
        tem_nota_fiscal=bruto["tem_nota_fiscal"],
    )


# --------------------------------------------------------------------------- #
# Passo 3 — Deduplicacao (RN-008, AMB-002, D-002)
# --------------------------------------------------------------------------- #
def deduplica(despesas: list[Despesa]) -> list[tuple[Despesa, Motivo | None]]:
    """RN-008 — colapsa por chave de negocio (sem `id`), mantendo a 1a ocorrencia.
    Cada copia seguinte recebe `Motivo.REGISTRO_DUPLICADO`."""
    vistas: set[tuple] = set()
    resultado: list[tuple[Despesa, Motivo | None]] = []
    for despesa in despesas:
        chave = despesa.chave_duplicidade()
        if chave in vistas:
            resultado.append((despesa, Motivo.REGISTRO_DUPLICADO))
        else:
            vistas.add(chave)
            resultado.append((despesa, None))
    return resultado


# --------------------------------------------------------------------------- #
# Passos 4-7 — Gates por despesa
# --------------------------------------------------------------------------- #
def valida_categoria(despesa: Despesa) -> Motivo | None:
    """RN-001 — `categoria_norm` deve estar entre as categorias validas."""
    if despesa.categoria_norm not in CATEGORIAS_VALIDAS:
        return Motivo.CATEGORIA_NAO_APLICAVEL
    return None


def valida_periodo(despesa: Despesa, periodo: Periodo) -> Motivo | None:
    """RN-007 — `inicio <= data <= fim` inclusive (AMB-009)."""
    if periodo.inicio <= despesa.data <= periodo.fim:
        return None
    return Motivo.DATA_FORA_COMPETENCIA


def valida_valor(despesa: Despesa) -> Motivo | None:
    """RN-010 — `valor > 0` (AMB-005)."""
    if despesa.valor > 0:
        return None
    return Motivo.VALOR_INVALIDO


def valida_nota_fiscal(despesa: Despesa) -> Motivo | None:
    """RN-006 — se `valor > LIMIAR_NOTA_FISCAL`, exige nota fiscal (AMB-004)."""
    if despesa.valor > LIMIAR_NOTA_FISCAL and not despesa.tem_nota_fiscal:
        return Motivo.SEM_NOTA_FISCAL
    return None


# --------------------------------------------------------------------------- #
# Passo 8 — Tetos (RN-002..RN-005, RN-009)
# --------------------------------------------------------------------------- #
def tetos_efetivos(em_viagem: bool) -> dict[str, Decimal]:
    """RN-009 — aplica o multiplicador de viagem aos tres tetos quando
    `em_viagem`. O limiar de nota fiscal NAO escala (AMB-008)."""
    mult = MULTIPLICADOR_VIAGEM if em_viagem else Decimal("1")
    return {
        "alimentacao": _quantiza(LIMITES_DIARIOS["alimentacao"] * mult),
        "transporte_urbano": _quantiza(LIMITES_DIARIOS["transporte_urbano"] * mult),
        "hospedagem": _quantiza(LIMITE_HOSPEDAGEM * mult),
    }


def aplica_teto_diario(aceitas: list[Despesa], teto: Decimal) -> Decimal:
    """RN-002/RN-003/RN-005 — agrega aceitas por dia civil e reembolsa
    `min(soma_do_dia, teto)`. Usado por alimentacao e transporte."""
    por_dia: dict[date, Decimal] = {}
    for despesa in aceitas:
        por_dia[despesa.data] = por_dia.get(despesa.data, Decimal("0")) + despesa.valor
    total = Decimal("0")
    for soma_dia in por_dia.values():
        total += min(soma_dia, teto)
    return total


def aplica_teto_hospedagem(aceitas: list[Despesa], teto: Decimal) -> Decimal:
    """RN-004/RN-005/AMB-006 — reembolsa `min(valor, teto)` por registro."""
    total = Decimal("0")
    for despesa in aceitas:
        total += min(despesa.valor, teto)
    return total


# --------------------------------------------------------------------------- #
# Passo 9 — Agregacao por categoria (RN-012, RN-014, AMB-012)
# --------------------------------------------------------------------------- #
def agrega_categoria(
    aceitas: list[Despesa],
    reprovadas: list[tuple[Despesa, Motivo]],
    total_reembolso: Decimal,
) -> ResultadoCategoria:
    """RN-012/RN-014 — calcula `total_aceito` (aceitas), `total_despesas`
    (aceitas + reprovadas da categoria) e monta a lista de reprovadas.
    Vale a invariante `total_despesas >= total_aceito >= total_reembolso`."""
    total_aceito = sum((d.valor for d in aceitas), Decimal("0"))
    total_reprovadas = sum((d.valor for d, _ in reprovadas), Decimal("0"))
    total_despesas = total_aceito + total_reprovadas
    return ResultadoCategoria(
        total_despesas=total_despesas,
        total_aceito=total_aceito,
        total_reembolso=total_reembolso,
        reprovadas=[Reprovacao(id=d.id, motivo=m) for d, m in reprovadas],
    )
