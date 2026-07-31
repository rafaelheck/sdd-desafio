"""Testes da politica externa: construcao e resolucao de centro de custo (T-029/T-031/T-044).

Cobre RN-015 (fonte externa + fallback `padrao`) e RN-016 (periodicidade lida da
politica). Usa o arquivo empacotado `politica-v4.json`.
"""

from decimal import Decimal

from src import regras
from src.modelo import CategoriaConfig
from src.politica import politica_de_dict


def test_politica_de_dict(politica_v4):
    """`politica_de_dict` constroi limites/periodicidade/parametros globais."""
    assert politica_v4.limiar_nf == Decimal("100.00")
    assert politica_v4.acrescimo_viagem_pct == Decimal("50")
    eng = politica_v4.centros_custo["CC-ENG-PLATAFORMA"]
    assert eng["alimentacao"] == CategoriaConfig(Decimal("75.00"), "dia", None)
    assert eng["hospedagem"].limite == Decimal("0.00")
    assert eng["hospedagem"].observacao == "nao reembolsavel"
    assert isinstance(eng["alimentacao"].limite, Decimal)


def test_cambio_de_dict(cambio_real):
    """`cambio_de_dict` constroi moeda_base e taxas por data como Decimal."""
    from datetime import date

    assert cambio_real.moeda_base == "BRL"
    assert cambio_real.taxas[date(2026, 7, 14)]["EUR"] == Decimal("5.93")
    assert isinstance(cambio_real.taxas[date(2026, 7, 20)]["USD"], Decimal)


def test_rn_015_fallback_padrao(politica_v4):
    """RN-015/AMB-013 — centro de custo inexistente cai no conjunto `padrao`."""
    conjunto = regras.resolve_conjunto(politica_v4, "CC-INEXISTENTE")
    assert conjunto is politica_v4.padrao
    assert conjunto["alimentacao"].limite == Decimal("60.00")
    assert conjunto["hospedagem"].limite == Decimal("250.00")


def test_rn_015_cc_especifico(politica_v4):
    """RN-015 — centro existente usa o proprio conjunto."""
    conjunto = regras.resolve_conjunto(politica_v4, "CC-ENG-PLATAFORMA")
    assert conjunto["alimentacao"].limite == Decimal("75.00")
    assert "representacao" not in conjunto  # so existe em CC-COMERCIAL


def test_rn_016_periodicidade_lida_da_politica(politica_v4):
    """RN-016 — a periodicidade vem da politica, nao do nome da categoria."""
    comercial = regras.resolve_conjunto(politica_v4, "CC-COMERCIAL")
    assert comercial["alimentacao"].periodicidade == "dia"
    assert comercial["hospedagem"].periodicidade == "diaria"
    assert comercial["representacao"].periodicidade == "dia"


def test_moeda_base_da_politica_ignorada():
    """RN-018 — a `moeda_base` de `politica-v4.json` nao entra na `Politica`."""
    pol = politica_de_dict(
        {
            "moeda_base": "USD",  # deve ser ignorada
            "padrao": {"alimentacao": {"limite": 60.0, "periodicidade": "dia"}},
            "nota_fiscal_obrigatoria_acima_de": 100.0,
            "acrescimo_em_viagem_percentual": 50,
        }
    )
    assert not hasattr(pol, "moeda_base")
