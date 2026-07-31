"""Casos de borda da Secao 7 da spec, um teste por linha (T-017).

Roda o pipeline sobre o exemplo oficial e verifica o comportamento de cada `id`.
"""

from decimal import Decimal

import pytest

from src import io_json
from src.calculo import calcula
from src.modelo import Motivo


@pytest.fixture(scope="module")
def resultado(caminho_exemplo):
    entrada = io_json.ler_entrada(caminho_exemplo)
    return calcula(
        entrada.despesas_brutas, entrada.colaborador, entrada.periodo, em_viagem=False
    )


def _reprovada(resultado, id_):
    """Localiza a `Reprovacao` de um id em qualquer balde de recusa."""
    for cat in resultado.categorias.values():
        for rep in cat.reprovadas:
            if rep.id == id_:
                return rep
    for rep in resultado.reprovadas_sem_categoria:
        if rep.id == id_:
            return rep
    return None


def _ids_reprovados(resultado):
    ids = {rep.id for cat in resultado.categorias.values() for rep in cat.reprovadas}
    ids |= {rep.id for rep in resultado.reprovadas_sem_categoria}
    return ids


def test_borda_soma_diaria_excede_teto(resultado):
    # d-001 72,50 + d-002 38,00 no mesmo dia: aceito 110,50; reembolso do dia 60.
    alim = resultado.categorias["alimentacao"]
    assert "d-001" not in _ids_reprovados(resultado)
    assert "d-002" not in _ids_reprovados(resultado)
    # 07-03 contribui exatamente com o teto de 60 dentro do total_reembolso.
    assert alim.total_reembolso == Decimal("255.43")


def test_borda_d003_limiar_nf_exato(resultado):
    # 100,00 sem NF -> aceita.
    assert "d-003" not in _ids_reprovados(resultado)


def test_borda_d004_um_centavo_acima(resultado):
    # 100,01 sem NF -> recusada por falta de NF.
    assert _reprovada(resultado, "d-004").motivo is Motivo.SEM_NOTA_FISCAL


def test_borda_d005_categoria_fora(resultado):
    rep = _reprovada(resultado, "d-005")
    assert rep.motivo is Motivo.CATEGORIA_NAO_APLICAVEL
    assert rep in resultado.reprovadas_sem_categoria


def test_borda_d006_d007_duplicata(resultado):
    assert "d-006" not in _ids_reprovados(resultado)
    assert _reprovada(resultado, "d-007").motivo is Motivo.REGISTRO_DUPLICADO


def test_borda_d008_data_fora(resultado):
    assert _reprovada(resultado, "d-008").motivo is Motivo.DATA_FORA_COMPETENCIA


def test_borda_d009_valor_negativo(resultado):
    assert _reprovada(resultado, "d-009").motivo is Motivo.VALOR_INVALIDO


def test_borda_d010_hospedagem_acima_teto(resultado):
    # 480,00 aceito; reembolso limitado a 250.
    assert "d-010" not in _ids_reprovados(resultado)
    assert resultado.categorias["hospedagem"].total_reembolso == Decimal("250.00")


def test_borda_d011_mais_de_2_casas(resultado):
    # 33,333 -> 33,33; entra em total_aceito de alimentacao.
    assert "d-011" not in _ids_reprovados(resultado)
    assert resultado.categorias["alimentacao"].total_aceito == Decimal("306.93")


def test_borda_d012_fim_de_semana_sem_regra(resultado):
    # Sabado tratado como qualquer dia -> aceito.
    assert "d-012" not in _ids_reprovados(resultado)


def test_borda_d013_sem_nf(resultado):
    assert _reprovada(resultado, "d-013").motivo is Motivo.SEM_NOTA_FISCAL


def test_borda_d014_caixa_alta_e_data_fim(resultado):
    # ALIMENTACAO tratada como alimentacao; data == fim e elegivel.
    assert "d-014" not in _ids_reprovados(resultado)


def test_borda_aceita_com_reembolso_zero_por_teto():
    # 3a despesa de alimentacao num dia ja no teto: permanece aceita, reembolso 0.
    from src.modelo import Colaborador
    from tests._apoio import bruto, periodo

    # Descricoes distintas para nao serem tratadas como duplicatas (RN-008).
    despesas = [
        bruto(id="a", descricao="cafe", valor=Decimal("40.00"), data="2026-07-05"),
        bruto(id="b", descricao="almoco", valor=Decimal("40.00"), data="2026-07-05"),
        bruto(id="c", descricao="jantar", valor=Decimal("40.00"), data="2026-07-05"),
    ]
    r = calcula(despesas, Colaborador("c", "n", "cc"), periodo(), em_viagem=False)
    alim = r.categorias["alimentacao"]
    assert alim.total_aceito == Decimal("120.00")  # todas aceitas com valor cheio
    assert alim.total_reembolso == Decimal("60.00")  # teto do dia
    assert _ids_reprovados(r) == set()
