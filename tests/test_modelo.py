"""Testes do modelo de dados (T-004)."""

from src.modelo import Motivo


def test_motivos_texto_exato():
    """Os 6 motivos batem com o texto exato da spec."""
    assert Motivo.CATEGORIA_NAO_APLICAVEL.value == "categoria não aplicável"
    assert Motivo.DATA_FORA_COMPETENCIA.value == "data fora da competência"
    assert Motivo.REGISTRO_DUPLICADO.value == "registro duplicado"
    assert Motivo.SEM_NOTA_FISCAL.value == "sem nota fiscal obrigatória"
    assert Motivo.VALOR_INVALIDO.value == "valor inválido"
    assert Motivo.REGISTRO_INVALIDO.value == "registro inválido"
