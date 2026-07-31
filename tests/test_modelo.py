"""Testes do modelo de dados (T-028), spec 1.4."""

import dataclasses
from decimal import Decimal

from src.modelo import Despesa, Motivo, Resultado, motivo_texto


def test_motivos_texto_exato():
    """Os 7 motivos batem com o texto exato da spec (inclui cambio nao identificado)."""
    assert Motivo.CATEGORIA_NAO_APLICAVEL.value == "categoria não aplicável"
    assert Motivo.DATA_FORA_COMPETENCIA.value == "data fora da competência"
    assert Motivo.REGISTRO_DUPLICADO.value == "registro duplicado"
    assert Motivo.SEM_NOTA_FISCAL.value == "sem nota fiscal obrigatória"
    assert Motivo.VALOR_INVALIDO.value == "valor inválido"
    assert Motivo.REGISTRO_INVALIDO.value == "registro inválido"
    assert Motivo.CAMBIO_NAO_IDENTIFICADO.value == "cambio não identificado"


def test_resultado_sem_em_viagem():
    """O `Resultado` nao tem mais campo `em_viagem` (viagem e por registro, RN-009)."""
    campos = {f.name for f in dataclasses.fields(Resultado)}
    assert "em_viagem" not in campos


def test_despesa_campos_cambio():
    """A `Despesa` carrega os campos de cambio/viagem da spec 1.4."""
    campos = {f.name for f in dataclasses.fields(Despesa)}
    assert {"valor_origem", "moeda_norm", "valor_base", "em_viagem"} <= campos
    assert "valor" not in campos  # renomeado para valor_origem/valor_base


def test_motivo_texto_aceita_str_da_observacao():
    """`motivo_texto` devolve a observacao (str) intacta e o `.value` do enum."""
    assert motivo_texto("nao reembolsavel") == "nao reembolsavel"
    assert motivo_texto(Motivo.VALOR_INVALIDO) == "valor inválido"


def test_chave_duplicidade_inclui_moeda_e_valor_origem():
    d = Despesa(
        id="a",
        data=None,
        categoria="Alimentacao",
        categoria_norm="alimentacao",
        descricao="d",
        fornecedor="f",
        valor_origem=Decimal("10.00"),
        moeda_norm="USD",
        tem_nota_fiscal=True,
    )
    chave = d.chave_duplicidade()
    assert Decimal("10.00") in chave and "USD" in chave
    assert "a" not in chave  # id nao entra (AMB-002)
