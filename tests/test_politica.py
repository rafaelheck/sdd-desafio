"""Testes das constantes de politica (T-003)."""

from decimal import Decimal

from src import politica


def test_valores_politica():
    assert politica.LIMITES_DIARIOS["alimentacao"] == Decimal("60")
    assert politica.LIMITES_DIARIOS["transporte_urbano"] == Decimal("80")
    assert politica.LIMITE_HOSPEDAGEM == Decimal("250")
    assert politica.LIMIAR_NOTA_FISCAL == Decimal("100")
    assert politica.MULTIPLICADOR_VIAGEM == Decimal("1.5")
    assert politica.CATEGORIAS_VALIDAS == {
        "alimentacao",
        "transporte_urbano",
        "hospedagem",
    }
    assert politica.CASAS_DECIMAIS == Decimal("0.01")


def test_todos_valores_sao_decimal():
    for limite in politica.LIMITES_DIARIOS.values():
        assert isinstance(limite, Decimal)
    assert isinstance(politica.LIMITE_HOSPEDAGEM, Decimal)
    assert isinstance(politica.LIMIAR_NOTA_FISCAL, Decimal)
    assert isinstance(politica.MULTIPLICADOR_VIAGEM, Decimal)
    assert isinstance(politica.CASAS_DECIMAIS, Decimal)
