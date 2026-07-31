"""Testes de cambio (T-045/T-030): conversao, taxa por data, cambio nao identificado.

Cobre RN-018 (conversao/normalizacao), RN-019 (data mais proxima, empate -> menor) e
RN-020 (cambio nao identificado), alem do abort de arquivo ausente/inparseavel.
"""

from datetime import date
from decimal import Decimal

import pytest

from src import io_json, regras
from src.modelo import Cambio, Motivo
from tests._apoio import CAMBIO_PADRAO, despesa


# --------------------------------------------------------------------------- #
# RN-018 — conversao e normalizacao de moeda
# --------------------------------------------------------------------------- #
def test_rn_018_converte_eur():
    # 22,00 x 5,93 = 130,46 (AMB-018: origem arredondada, taxa cheia, resultado 2 casas).
    assert regras.converte(Decimal("22.00"), Decimal("5.93")) == Decimal("130.46")


def test_rn_018_arredondamento():
    # A taxa NAO e arredondada; o resultado e arredondado half-up.
    assert regras.converte(Decimal("1.00"), Decimal("5.555")) == Decimal("5.56")
    # A origem e arredondada a 2 casas ANTES de multiplicar: 33,333 -> 33,33.
    assert regras.converte(Decimal("33.333"), Decimal("2")) == Decimal("66.66")


def test_rn_018_moeda_normalizada():
    # " usd " -> USD; moeda != base -> em viagem.
    d = despesa(moeda=" usd ", data="2026-07-14", valor=Decimal("10.00"))
    assert d.moeda_norm == "USD"
    assert d.em_viagem is True


def test_rn_018_moeda_base_sem_conversao():
    # moeda = base (BRL) -> sem conversao, nao e viagem, valor_base = valor_origem.
    d = despesa(moeda="BRL", valor=Decimal("95.00"))
    assert d.em_viagem is False
    assert d.valor_base == Decimal("95.00")


def test_rn_018_sem_moeda_nao_e_viagem():
    d = despesa(valor=Decimal("40.00"))  # _PADRAO_BRUTO nao tem moeda
    assert d.moeda_norm is None
    assert d.em_viagem is False
    assert d.valor_base == Decimal("40.00")


# --------------------------------------------------------------------------- #
# RN-019 — resolucao da taxa por data
# --------------------------------------------------------------------------- #
def test_rn_019_data_exata():
    taxa = regras.taxa_por_data(CAMBIO_PADRAO, "EUR", date(2026, 7, 14))
    assert taxa == Decimal("5.93")


def test_rn_019_fim_de_semana_mais_proxima():
    # 07-18 (sabado) sem cotacao: EUR mais proximo e 07-17 (dist 1) vs 07-20 (dist 2).
    taxa = regras.taxa_por_data(CAMBIO_PADRAO, "EUR", date(2026, 7, 18))
    assert taxa == Decimal("5.96")


def test_rn_019_empate_menor_taxa():
    # 07-18 equidistante de 07-17 (5,96) e 07-19 (6,00) -> menor taxa 5,96.
    cambio = Cambio(
        moeda_base="BRL",
        taxas={
            date(2026, 7, 17): {"EUR": Decimal("5.96")},
            date(2026, 7, 19): {"EUR": Decimal("6.00")},
        },
    )
    assert regras.taxa_por_data(cambio, "EUR", date(2026, 7, 18)) == Decimal("5.96")


def test_rn_019_moeda_ausente_retorna_none():
    assert regras.taxa_por_data(CAMBIO_PADRAO, "GBP", date(2026, 7, 14)) is None


# --------------------------------------------------------------------------- #
# RN-020 — cambio nao identificado
# --------------------------------------------------------------------------- #
def test_rn_020_cambio_nao_identificado():
    d = despesa(moeda="GBP", data="2026-07-14", valor=Decimal("55.00"))
    motivo = regras.valida_cambio(d, CAMBIO_PADRAO)
    assert motivo is Motivo.CAMBIO_NAO_IDENTIFICADO
    assert d.valor_base is None  # sem valor em base para somar (AMB-017)


# --------------------------------------------------------------------------- #
# Abort de arquivo ausente/inparseavel (T-030)
# --------------------------------------------------------------------------- #
def test_cambio_ausente_aborta(tmp_path):
    with pytest.raises(io_json.ErroEntrada):
        io_json.ler_cambio(tmp_path / "nao-existe.json")


def test_cambio_inparseavel_aborta(tmp_path):
    ruim = tmp_path / "cambio.json"
    ruim.write_text("{ nao e json", encoding="utf-8")
    with pytest.raises(io_json.ErroEntrada):
        io_json.ler_cambio(ruim)


def test_politica_ausente_aborta(tmp_path):
    with pytest.raises(io_json.ErroEntrada):
        io_json.ler_politica(tmp_path / "nao-existe.json")


def test_le_taxas_decimal(cambio_real):
    # As taxas chegam como Decimal (parse_float=Decimal), nunca float.
    for cotacoes in cambio_real.taxas.values():
        for fator in cotacoes.values():
            assert isinstance(fator, Decimal)
