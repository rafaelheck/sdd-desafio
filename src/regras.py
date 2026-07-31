"""Regras de negocio — uma funcao pura por RN (DT-002), spec 1.4.

Os gates de validacao retornam `Motivo | str | None` (motivo da recusa, ou `None`
se a despesa passa). As funcoes de conversao, taxa, teto e agregacao calculam
valores monetarios. Nada aqui faz I/O; `calculo.py` apenas orquestra estas funcoes
na ordem da Secao 8. Categorias, limites e taxas vem sempre de `Politica`/`Cambio`
injetados (RN-004/RN-015/RN-018) — nenhuma categoria e conhecida em codigo.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from src.modelo import (
    Cambio,
    CategoriaConfig,
    Despesa,
    Motivo,
    Periodo,
    Politica,
    Reprovacao,
    ResultadoCategoria,
)
from src.politica import CASAS_DECIMAIS

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


def _quantiza(valor: Decimal) -> Decimal:
    """Arredonda para 2 casas, meio-para-cima (RN-011)."""
    return valor.quantize(CASAS_DECIMAIS, ROUND_HALF_UP)


# --------------------------------------------------------------------------- #
# Passo 1 — Validacao estrutural (RN-013)
# --------------------------------------------------------------------------- #
def valida_estrutura(bruto: object) -> Motivo | None:
    """RN-013 — campos obrigatorios presentes e tipados, `valor` numerico, `data`
    parseavel, `moeda` (se presente) textual. Retorna `REGISTRO_INVALIDO` ou `None`.

    `moeda` ausente, `null` ou vazio apos `trim` NAO e invalido (conta como sem
    moeda, RN-018); `moeda` de tipo nao-textual (numero, booleano, objeto) e
    "registro inválido"."""
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

    # `moeda` e opcional; se presente e nao-nula, deve ser texto (RN-013/RN-018).
    moeda = bruto.get("moeda")
    if moeda is not None and not isinstance(moeda, str):
        return Motivo.REGISTRO_INVALIDO

    try:
        date.fromisoformat(bruto["data"])
    except (ValueError, TypeError):
        return Motivo.REGISTRO_INVALIDO

    return None


# --------------------------------------------------------------------------- #
# Passo 3 — Normalizacao (RN-011, RN-001, RN-018)
# --------------------------------------------------------------------------- #
def _norma_moeda(bruto: dict) -> str | None:
    """Moeda normalizada trim+upper; `None` se ausente/`null`/vazio (RN-018)."""
    moeda = bruto.get("moeda")
    if not isinstance(moeda, str):
        return None
    return moeda.strip().upper() or None


def normaliza_despesa(bruto: dict, cambio: Cambio) -> Despesa:
    """RN-011/RN-001/RN-018 — arredonda `valor` a 2 casas (half-up), deriva
    `categoria_norm` (`strip().lower()`), `moeda_norm` (`strip().upper()`) e o
    status de viagem (moeda != base -> viagem, RN-009). Assume estrutura validada.

    Nao converte o valor: `valor_base` e preenchido depois por `valida_cambio`."""
    valor_bruto = bruto["valor"]
    if isinstance(valor_bruto, float):
        # Guarda-costas: valores devem chegar como Decimal (parse_float=Decimal),
        # mas se vier float converte via texto para nao herdar erro binario.
        valor_bruto = Decimal(str(valor_bruto))
    valor_origem = _quantiza(Decimal(valor_bruto))

    moeda_norm = _norma_moeda(bruto)
    em_viagem = moeda_norm is not None and moeda_norm != cambio.moeda_base

    categoria = bruto["categoria"]
    return Despesa(
        id=bruto["id"],
        data=date.fromisoformat(bruto["data"]),
        categoria=categoria,
        categoria_norm=categoria.strip().lower(),
        descricao=bruto["descricao"],
        fornecedor=bruto["fornecedor"],
        valor_origem=valor_origem,
        moeda_norm=moeda_norm,
        tem_nota_fiscal=bruto["tem_nota_fiscal"],
        em_viagem=em_viagem,
    )


# --------------------------------------------------------------------------- #
# Passo 2/4 — Resolucao do centro de custo e categoria valida (RN-015, RN-001)
# --------------------------------------------------------------------------- #
def resolve_conjunto(
    politica: Politica, centro_custo: str
) -> dict[str, CategoriaConfig]:
    """RN-015 — conjunto de categorias do centro de custo, ou `padrao` se o centro
    nao existe na politica (AMB-013)."""
    return politica.centros_custo.get(centro_custo, politica.padrao)


def valida_categoria(
    despesa: Despesa, conjunto: dict[str, CategoriaConfig]
) -> Motivo | None:
    """RN-001 — `categoria_norm` deve ser uma chave do conjunto do centro de custo
    resolvido. Senao "categoria não aplicável"."""
    if despesa.categoria_norm not in conjunto:
        return Motivo.CATEGORIA_NAO_APLICAVEL
    return None


# --------------------------------------------------------------------------- #
# Passo 5 — Limite da categoria > 0 (RN-017)
# --------------------------------------------------------------------------- #
def valida_limite_categoria(
    despesa: Despesa, config: CategoriaConfig
) -> Motivo | str | None:
    """RN-017 — se `limite <= 0`, recusa com motivo = `observacao` (ou
    "categoria não aplicável" se nao houver). Reportado sob a propria categoria
    (AMB-014). Senao `None`."""
    if config.limite <= 0:
        return config.observacao or Motivo.CATEGORIA_NAO_APLICAVEL
    return None


# --------------------------------------------------------------------------- #
# Passo 6 — Conversao de cambio (RN-018, RN-019, RN-020, AMB-018)
# --------------------------------------------------------------------------- #
def taxa_por_data(
    cambio: Cambio, moeda_norm: str, data: date
) -> Decimal | None:
    """RN-019 — fator de `moeda_norm` na `data`, ou na data mais proxima que
    contenha a moeda (menor `abs(dist)` em dias; empate -> menor taxa). `None` se a
    moeda nao existe em nenhuma data de `taxas` (-> RN-020)."""
    candidatas = [
        (abs((data_taxa - data).days), cotacoes[moeda_norm])
        for data_taxa, cotacoes in cambio.taxas.items()
        if moeda_norm in cotacoes
    ]
    if not candidatas:
        return None
    # Menor distancia; em empate, menor taxa (a tupla (dist, taxa) ordena assim).
    return min(candidatas)[1]


def converte(valor_origem: Decimal, taxa: Decimal) -> Decimal:
    """RN-018/AMB-018 — arredonda a origem a 2 casas, multiplica pela taxa cheia e
    arredonda o resultado a 2 casas (half-up). A taxa NAO e arredondada."""
    return _quantiza(_quantiza(valor_origem) * taxa)


def valida_cambio(despesa: Despesa, cambio: Cambio) -> Motivo | None:
    """RN-018/RN-020 — preenche `despesa.valor_base`. Registro sem moeda ou com
    moeda = base fica com `valor_base = valor_origem`. Em viagem, converte pela taxa
    da data (RN-019); se a moeda nao existe em nenhuma data, retorna
    `CAMBIO_NAO_IDENTIFICADO` (e `valor_base` permanece `None`)."""
    if not despesa.em_viagem:
        despesa.valor_base = despesa.valor_origem
        return None
    taxa = taxa_por_data(cambio, despesa.moeda_norm, despesa.data)
    if taxa is None:
        return Motivo.CAMBIO_NAO_IDENTIFICADO
    despesa.valor_base = converte(despesa.valor_origem, taxa)
    return None


# --------------------------------------------------------------------------- #
# Passo 8 — Periodo (RN-007)
# --------------------------------------------------------------------------- #
def valida_periodo(despesa: Despesa, periodo: Periodo) -> Motivo | None:
    """RN-007 — `inicio <= data <= fim` inclusive (AMB-009)."""
    if periodo.inicio <= despesa.data <= periodo.fim:
        return None
    return Motivo.DATA_FORA_COMPETENCIA


# --------------------------------------------------------------------------- #
# Passo 9 — Valor valido (RN-010)
# --------------------------------------------------------------------------- #
def valida_valor(despesa: Despesa) -> Motivo | None:
    """RN-010 — `valor_origem > 0` (AMB-005)."""
    if despesa.valor_origem > 0:
        return None
    return Motivo.VALOR_INVALIDO


# --------------------------------------------------------------------------- #
# Passo 10 — Nota fiscal (RN-006), sobre o valor JA convertido
# --------------------------------------------------------------------------- #
def valida_nota_fiscal(despesa: Despesa, limiar: Decimal) -> Motivo | None:
    """RN-006 — se o valor convertido (`valor_base`) e estritamente maior que o
    limiar, exige nota fiscal. O limiar NAO escala em viagem (AMB-008/AMB-016)."""
    if despesa.valor_base > limiar and not despesa.tem_nota_fiscal:
        return Motivo.SEM_NOTA_FISCAL
    return None


# --------------------------------------------------------------------------- #
# Passo 11 — Tetos por periodicidade (RN-002/003/004/005/009/016)
# --------------------------------------------------------------------------- #
def _limite_viagem(limite: Decimal, fator: Decimal) -> Decimal:
    return _quantiza(limite * fator)


def aplica_teto_dia(
    aceitas: list[Despesa], limite: Decimal, fator: Decimal
) -> Decimal:
    """RN-002/RN-005/RN-009/AMB-016 — periodicidade "dia": agrega por dia civil com
    BALDES SEPARADOS por status de viagem. Cada balde e limitado pelo seu teto
    (base para nao-viagem, `limite * fator` para viagem) e o reembolso do dia e a
    soma dos dois baldes."""
    limite_viagem = _limite_viagem(limite, fator)
    por_dia: dict[date, dict[bool, Decimal]] = {}
    for despesa in aceitas:
        baldes = por_dia.setdefault(despesa.data, {False: Decimal("0"), True: Decimal("0")})
        baldes[despesa.em_viagem] += despesa.valor_base
    total = Decimal("0")
    for baldes in por_dia.values():
        total += min(baldes[False], limite) + min(baldes[True], limite_viagem)
    return total


def aplica_teto_diaria(
    aceitas: list[Despesa], limite: Decimal, fator: Decimal
) -> Decimal:
    """RN-003/RN-005/RN-009/AMB-006 — periodicidade "diaria": teto por registro
    individual, `min(valor_base, limite_efetivo)`, com `limite_efetivo = limite *
    fator` quando o registro esta em viagem."""
    total = Decimal("0")
    limite_viagem = _limite_viagem(limite, fator)
    for despesa in aceitas:
        teto = limite_viagem if despesa.em_viagem else limite
        total += min(despesa.valor_base, teto)
    return total


# --------------------------------------------------------------------------- #
# Passo 12 — Agregacao por categoria (RN-012, RN-014, AMB-012, AMB-017)
# --------------------------------------------------------------------------- #
def agrega_categoria(
    aceitas: list[Despesa],
    reprovadas: list[tuple[Despesa, Motivo | str]],
    total_reembolso: Decimal,
) -> ResultadoCategoria:
    """RN-012/RN-014 — `total_aceito` (aceitas), `total_despesas` (aceitas +
    reprovadas da categoria em `valor_base`, EXCETO `valor <= 0` e EXCETO
    "cambio não identificado") e a lista de reprovadas. Vale a invariante
    `total_despesas >= total_aceito >= total_reembolso`.

    Exclusoes (mesmo principio de nao-valoravel):
    - `valor_origem <= 0`: exclusao POR VALOR, nao pelo motivo (RN-014/D-004);
    - `valor_base is None` (cambio não identificado): sem valor em base para somar
      (AMB-017)."""
    total_aceito = sum((d.valor_base for d in aceitas), Decimal("0"))
    total_reprovadas = sum(
        (
            d.valor_base
            for d, _ in reprovadas
            if d.valor_origem > 0 and d.valor_base is not None
        ),
        Decimal("0"),
    )
    total_despesas = total_aceito + total_reprovadas
    return ResultadoCategoria(
        total_despesas=total_despesas,
        total_aceito=total_aceito,
        total_reembolso=total_reembolso,
        reprovadas=[Reprovacao(id=d.id, motivo=m) for d, m in reprovadas],
    )
