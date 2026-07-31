"""Testes de leitura e serializacao (`src.io_json`) (T-018, T-019)."""

import json
from decimal import Decimal

import pytest

from src import io_json
from src.calculo import calcula


@pytest.fixture
def resultado_exemplo(caminho_exemplo):
    entrada = io_json.ler_entrada(caminho_exemplo)
    return calcula(
        entrada.despesas_brutas, entrada.colaborador, entrada.periodo, em_viagem=False
    )


# --------------------------------------------------------------------------- #
# Leitura (T-018)
# --------------------------------------------------------------------------- #
def test_leitura_decimal(caminho_exemplo):
    entrada = io_json.ler_entrada(caminho_exemplo)
    for registro in entrada.despesas_brutas:
        assert isinstance(registro["valor"], (Decimal, int))
        assert not isinstance(registro["valor"], float)
    # d-011 tem 3 casas: precisa chegar como Decimal preservando o texto.
    d011 = next(r for r in entrada.despesas_brutas if r["id"] == "d-011")
    assert d011["valor"] == Decimal("33.333")


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
# Serializacao (T-019)
# --------------------------------------------------------------------------- #
def test_serializa_2_casas(resultado_exemplo):
    texto = io_json.serializa(resultado_exemplo)
    # Todo numero monetario aparece com exatamente 2 casas.
    assert '"total_reembolso_geral": 585.43' in texto
    assert '"total_aceito": 100.00' in texto
    assert '"total_reembolso": 250.00' in texto
    # Parse de volta confere igualdade numerica.
    dados = json.loads(texto)
    assert dados["total_reembolso_geral"] == 585.43


def test_acentos_preservados(resultado_exemplo):
    texto = io_json.serializa(resultado_exemplo)
    assert "categoria não aplicável" in texto
    assert "\\u00" not in texto  # sem escape unicode


def test_reprovada_sem_categoria_tem_categoria_informada(resultado_exemplo):
    texto = io_json.serializa(resultado_exemplo)
    dados = json.loads(texto)
    rep = dados["reprovadas_sem_categoria"][0]
    assert rep["id"] == "d-005"
    assert rep["categoria_informada"] == "coworking"
    assert rep["motivo"] == "categoria não aplicável"


def test_reprovadas_de_categoria_so_id_e_motivo(resultado_exemplo):
    texto = io_json.serializa(resultado_exemplo)
    dados = json.loads(texto)
    for rep in dados["categorias"]["transporte_urbano"]["reprovadas"]:
        assert set(rep.keys()) == {"id", "motivo"}
