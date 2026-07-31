"""Construcao das fontes externas como estruturas puras (spec 1.4 / DT-008).

Nao ha mais constantes de limite/categoria embutidas: categorias, limites,
periodicidade, limiar de NF e acrescimo de viagem vem de `politica-v4.json`
(RN-015); moeda base e taxas vem de `cambio.json` (RN-018). Estas funcoes sao
puras (dict -> estrutura); a leitura de arquivo vive em `io_json.py`.

Todos os valores monetarios e taxas sao `Decimal` (lidos com
`parse_float=Decimal`), nunca `float` (DT-001).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from src.modelo import Cambio, CategoriaConfig, Politica

# Precisao monetaria: 2 casas (RN-011).
CASAS_DECIMAIS = Decimal("0.01")


def _categoria_de_dict(bruto: dict) -> CategoriaConfig:
    """Converte um objeto de categoria da politica em `CategoriaConfig`."""
    observacao = bruto.get("observacao")
    return CategoriaConfig(
        limite=Decimal(bruto["limite"]),
        periodicidade=bruto["periodicidade"],
        observacao=observacao if isinstance(observacao, str) else None,
    )


def _conjunto_de_dict(bruto: dict) -> dict[str, CategoriaConfig]:
    """Converte um conjunto de categorias (padrao ou de um centro) em dict."""
    return {nome: _categoria_de_dict(cfg) for nome, cfg in bruto.items()}


def politica_de_dict(dados: dict) -> Politica:
    """RN-015 — constroi a `Politica` a partir do dict de `politica-v4.json`.

    A `moeda_base` de `politica-v4.json`, se houver, e ignorada (RN-018): a moeda
    base de referencia e sempre a do `cambio.json`."""
    padrao = _conjunto_de_dict(dados["padrao"])
    centros_custo = {
        cc: _conjunto_de_dict(conjunto)
        for cc, conjunto in dados.get("centros_custo", {}).items()
    }
    return Politica(
        padrao=padrao,
        centros_custo=centros_custo,
        limiar_nf=Decimal(dados["nota_fiscal_obrigatoria_acima_de"]),
        acrescimo_viagem_pct=Decimal(dados["acrescimo_em_viagem_percentual"]),
    )


def cambio_de_dict(dados: dict) -> Cambio:
    """RN-018 — constroi o `Cambio` a partir do dict de `cambio.json`.

    Datas viram `date`; moedas sao normalizadas trim+upper; taxas ficam `Decimal`."""
    taxas: dict[date, dict[str, Decimal]] = {}
    for data_str, cotacoes in dados.get("taxas", {}).items():
        taxas[date.fromisoformat(data_str)] = {
            moeda.strip().upper(): Decimal(fator) for moeda, fator in cotacoes.items()
        }
    return Cambio(moeda_base=dados["moeda_base"].strip().upper(), taxas=taxas)
