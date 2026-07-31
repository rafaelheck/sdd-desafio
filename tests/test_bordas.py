"""Casos de borda da Secao 7 da spec 1.4, um teste por linha (T-046).

Roda o pipeline sobre os inputs oficiais (exemplo em CC-ENG-PLATAFORMA sem moeda;
envelope em CC-COMERCIAL com EUR/USD/GBP) e verifica o comportamento de cada `id`.
"""

from decimal import Decimal

import pytest

from src import io_json
from src.calculo import calcula
from src.modelo import Motivo, motivo_texto


@pytest.fixture(scope="module")
def exemplo(caminho_exemplo, politica_v4, cambio_real):
    entrada = io_json.ler_entrada(caminho_exemplo)
    return calcula(
        entrada.despesas_brutas, entrada.colaborador, entrada.periodo, politica_v4, cambio_real
    )


@pytest.fixture(scope="module")
def envelope(caminho_envelope, politica_v4, cambio_real):
    entrada = io_json.ler_entrada(caminho_envelope)
    return calcula(
        entrada.despesas_brutas, entrada.colaborador, entrada.periodo, politica_v4, cambio_real
    )


def _reprovada(resultado, id_):
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


# --------------------------------------------------------------------------- #
# Exemplo (CC-ENG-PLATAFORMA)
# --------------------------------------------------------------------------- #
def test_borda_soma_diaria_excede_teto(exemplo):
    # d-001 72,50 + d-002 38,00 no mesmo dia; limite 75 -> reembolso do dia 75.
    assert "d-001" not in _ids_reprovados(exemplo)
    assert "d-002" not in _ids_reprovados(exemplo)
    assert exemplo.categorias["alimentacao"].total_reembolso == Decimal("271.43")


def test_borda_d003_limiar_nf_exato(exemplo):
    assert "d-003" not in _ids_reprovados(exemplo)  # 100,00 sem NF -> aceita


def test_borda_d004_um_centavo_acima(exemplo):
    assert _reprovada(exemplo, "d-004").motivo is Motivo.SEM_NOTA_FISCAL


def test_borda_d005_categoria_fora(exemplo):
    rep = _reprovada(exemplo, "d-005")
    assert rep.motivo is Motivo.CATEGORIA_NAO_APLICAVEL
    assert rep in exemplo.reprovadas_sem_categoria


def test_borda_d006_d007_duplicata(exemplo):
    assert "d-006" not in _ids_reprovados(exemplo)
    assert _reprovada(exemplo, "d-007").motivo is Motivo.REGISTRO_DUPLICADO


def test_borda_d008_data_fora(exemplo):
    assert _reprovada(exemplo, "d-008").motivo is Motivo.DATA_FORA_COMPETENCIA


def test_borda_d009_valor_negativo(exemplo):
    assert _reprovada(exemplo, "d-009").motivo is Motivo.VALOR_INVALIDO


def test_borda_d010_d013_limite_zero(exemplo):
    # hospedagem limite 0 em CC-ENG -> "nao reembolsavel" sob a categoria.
    assert motivo_texto(_reprovada(exemplo, "d-010").motivo) == "nao reembolsavel"
    assert motivo_texto(_reprovada(exemplo, "d-013").motivo) == "nao reembolsavel"
    hosp = exemplo.categorias["hospedagem"]
    assert hosp.total_aceito == Decimal("0.00")
    assert hosp.total_reembolso == Decimal("0.00")
    assert hosp.total_despesas == Decimal("1170.00")  # valores > 0 somam


def test_borda_d011_mais_de_2_casas(exemplo):
    assert "d-011" not in _ids_reprovados(exemplo)  # 33,333 -> 33,33
    assert exemplo.categorias["alimentacao"].total_aceito == Decimal("306.93")


def test_borda_d012_fim_de_semana_sem_regra(exemplo):
    assert "d-012" not in _ids_reprovados(exemplo)  # sabado tratado como qualquer dia


def test_borda_d014_caixa_alta_e_data_fim(exemplo):
    assert "d-014" not in _ids_reprovados(exemplo)  # ALIMENTACAO; data == fim elegivel


# --------------------------------------------------------------------------- #
# Envelope (CC-COMERCIAL, moedas estrangeiras)
# --------------------------------------------------------------------------- #
def test_borda_e002_moeda_estrangeira_viagem(envelope):
    # EUR 22 (07-14, taxa 5,93) -> 130,46; viagem (limite 90 -> 135); aceito integral.
    assert "e-002" not in _ids_reprovados(envelope)
    assert envelope.categorias["alimentacao"].total_aceito >= Decimal("130.46")


def test_borda_e004_fim_de_semana_taxa_mais_proxima(envelope):
    # EUR 30 (07-18 sabado -> 07-17 5,96) = 178,80; viagem limite 135 -> reembolso 135.
    assert "e-004" not in _ids_reprovados(envelope)


def test_borda_e005_nf_apos_conversao(envelope):
    # USD 40 (07-20 5,50) = 220 > 100 e sem NF -> recusada.
    assert _reprovada(envelope, "e-005").motivo is Motivo.SEM_NOTA_FISCAL


def test_borda_e006_cambio_nao_identificado(envelope):
    # GBP ausente de todas as taxas -> cambio nao identificado sob representacao.
    rep = _reprovada(envelope, "e-006")
    assert rep.motivo is Motivo.CAMBIO_NAO_IDENTIFICADO
    # Fora de total_despesas (AMB-017).
    assert envelope.categorias["representacao"].total_despesas == Decimal("340.00")


def test_borda_e009_categoria_fora_do_cc(envelope):
    rep = _reprovada(envelope, "e-009")
    assert rep.motivo is Motivo.CATEGORIA_NAO_APLICAVEL
    assert rep in envelope.reprovadas_sem_categoria


def test_borda_e010_sem_moeda_nao_e_viagem(envelope):
    # e-010 sem `moeda` -> base, nao viagem; aceito.
    assert "e-010" not in _ids_reprovados(envelope)


def test_borda_e008_moeda_base_sem_conversao(envelope):
    # e-008 BRL 95 (= base) -> sem conversao, nao viagem; min(95,90)=90.
    assert "e-008" not in _ids_reprovados(envelope)
