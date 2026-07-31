"""Testes de leitura e serializacao (`src.io_json`) (T-030/T-041/T-049), spec 1.4."""

import json
from decimal import Decimal

import pytest

from src import io_json
from src.calculo import calcula


@pytest.fixture
def resultado_exemplo(caminho_exemplo, politica_v4, cambio_real):
    entrada = io_json.ler_entrada(caminho_exemplo)
    return calcula(
        entrada.despesas_brutas, entrada.colaborador, entrada.periodo, politica_v4, cambio_real
    )


@pytest.fixture
def resultado_envelope(caminho_envelope, politica_v4, cambio_real):
    entrada = io_json.ler_entrada(caminho_envelope)
    return calcula(
        entrada.despesas_brutas, entrada.colaborador, entrada.periodo, politica_v4, cambio_real
    )


# --------------------------------------------------------------------------- #
# Leitura
# --------------------------------------------------------------------------- #
def test_leitura_decimal(caminho_exemplo):
    entrada = io_json.ler_entrada(caminho_exemplo)
    for registro in entrada.despesas_brutas:
        assert isinstance(registro["valor"], (Decimal, int))
        assert not isinstance(registro["valor"], float)
    d011 = next(r for r in entrada.despesas_brutas if r["id"] == "d-011")
    assert d011["valor"] == Decimal("33.333")


def test_ler_entrada_nao_le_em_viagem(caminho_exemplo):
    entrada = io_json.ler_entrada(caminho_exemplo)
    assert not hasattr(entrada, "em_viagem")


def test_json_topo_invalido_erro(tmp_path):
    ruim = tmp_path / "ruim.json"
    ruim.write_text("{ isto nao e json", encoding="utf-8")
    with pytest.raises(io_json.ErroEntrada):
        io_json.ler_entrada(ruim)


def test_arquivo_inexistente_erro(tmp_path):
    with pytest.raises(io_json.ErroEntrada):
        io_json.ler_entrada(tmp_path / "nao-existe.json")


def test_campo_topo_ausente_erro(tmp_path):
    incompleto = tmp_path / "incompleto.json"
    incompleto.write_text(json.dumps({"despesas": []}), encoding="utf-8")
    with pytest.raises(io_json.ErroEntrada):
        io_json.ler_entrada(incompleto)


# --------------------------------------------------------------------------- #
# Serializacao
# --------------------------------------------------------------------------- #
def test_saida_sem_em_viagem(resultado_exemplo):
    dados = json.loads(io_json.serializa(resultado_exemplo))
    assert "em_viagem" not in dados


def test_serializa_2_casas(resultado_exemplo):
    texto = io_json.serializa(resultado_exemplo)
    assert '"total_reembolso_geral": 351.43' in texto
    assert '"total_aceito": 100.00' in texto
    dados = json.loads(texto)
    assert dados["total_reembolso_geral"] == 351.43


def test_acentos_preservados(resultado_exemplo):
    texto = io_json.serializa(resultado_exemplo)
    assert "categoria não aplicável" in texto
    assert "\\u00" not in texto  # sem escape unicode


def test_ordem_categorias_por_politica(resultado_envelope):
    # DT-011 — ordem das chaves do CC-COMERCIAL na politica.
    dados = json.loads(io_json.serializa(resultado_envelope))
    assert list(dados["categorias"].keys()) == [
        "alimentacao",
        "transporte_urbano",
        "hospedagem",
        "representacao",
    ]


def test_cambio_nao_identificado_serializado(resultado_envelope):
    texto = io_json.serializa(resultado_envelope)
    assert "cambio não identificado" in texto


def test_reprovada_sem_categoria_tem_categoria_informada(resultado_exemplo):
    dados = json.loads(io_json.serializa(resultado_exemplo))
    rep = dados["reprovadas_sem_categoria"][0]
    assert rep["id"] == "d-005"
    assert rep["categoria_informada"] == "coworking"
    assert rep["motivo"] == "categoria não aplicável"


def test_reprovadas_de_categoria_so_id_e_motivo(resultado_exemplo):
    dados = json.loads(io_json.serializa(resultado_exemplo))
    for rep in dados["categorias"]["transporte_urbano"]["reprovadas"]:
        assert set(rep.keys()) == {"id", "motivo"}
