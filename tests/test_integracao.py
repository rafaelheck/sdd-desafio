"""Goldens ponta a ponta contra a spec 1.4 (T-048).

Golden 1: `despesas-exemplo.json` (CC-ENG-PLATAFORMA, sem moeda) -> 351,43 (Secao 4).
Golden 2: `despesas-envelope.json` (CC-COMERCIAL, EUR/USD/GBP) -> 1228,72 (quickstart).
"""

import json
from decimal import Decimal

import pytest

from src import io_json
from src.calculo import calcula

_GOLDEN_EXEMPLO = """
{
  "colaborador": { "id": "c-0417", "nome": "Marina Volpi", "centro_custo": "CC-ENG-PLATAFORMA" },
  "competencia": "2026-07",
  "periodo": { "inicio": "2026-07-01", "fim": "2026-07-31" },
  "categorias": {
    "alimentacao": {
      "total_despesas": 402.83, "total_aceito": 306.93, "total_reembolso": 271.43,
      "reprovadas": [
        { "id": "d-007", "motivo": "registro duplicado" },
        { "id": "d-008", "motivo": "data fora da competência" }
      ]
    },
    "transporte_urbano": {
      "total_despesas": 200.01, "total_aceito": 100.00, "total_reembolso": 80.00,
      "reprovadas": [
        { "id": "d-004", "motivo": "sem nota fiscal obrigatória" },
        { "id": "d-009", "motivo": "valor inválido" }
      ]
    },
    "hospedagem": {
      "total_despesas": 1170.00, "total_aceito": 0.00, "total_reembolso": 0.00,
      "reprovadas": [
        { "id": "d-010", "motivo": "nao reembolsavel" },
        { "id": "d-013", "motivo": "nao reembolsavel" }
      ]
    }
  },
  "reprovadas_sem_categoria": [
    { "id": "d-005", "categoria_informada": "coworking", "motivo": "categoria não aplicável" }
  ],
  "total_reembolso_geral": 351.43
}
"""

_GOLDEN_ENVELOPE = """
{
  "colaborador": { "id": "c-0912", "nome": "Rafael Nkemelu", "centro_custo": "CC-COMERCIAL" },
  "competencia": "2026-07",
  "periodo": { "inicio": "2026-07-01", "fim": "2026-07-31" },
  "categorias": {
    "alimentacao": {
      "total_despesas": 577.52, "total_aceito": 577.52, "total_reembolso": 528.72,
      "reprovadas": []
    },
    "transporte_urbano": {
      "total_despesas": 220.00, "total_aceito": 0.00, "total_reembolso": 0.00,
      "reprovadas": [ { "id": "e-005", "motivo": "sem nota fiscal obrigatória" } ]
    },
    "hospedagem": {
      "total_despesas": 1200.00, "total_aceito": 1200.00, "total_reembolso": 400.00,
      "reprovadas": []
    },
    "representacao": {
      "total_despesas": 340.00, "total_aceito": 340.00, "total_reembolso": 300.00,
      "reprovadas": [ { "id": "e-006", "motivo": "cambio não identificado" } ]
    }
  },
  "reprovadas_sem_categoria": [
    { "id": "e-009", "categoria_informada": "coworking", "motivo": "categoria não aplicável" }
  ],
  "total_reembolso_geral": 1228.72
}
"""


def _produz(caminho, politica, cambio):
    entrada = io_json.ler_entrada(caminho)
    resultado = calcula(
        entrada.despesas_brutas, entrada.colaborador, entrada.periodo, politica, cambio
    )
    return json.loads(io_json.serializa(resultado), parse_float=Decimal)


def test_golden_exemplo(caminho_exemplo, politica_v4, cambio_real):
    produzido = _produz(caminho_exemplo, politica_v4, cambio_real)
    esperado = json.loads(_GOLDEN_EXEMPLO, parse_float=Decimal)
    assert produzido == esperado


def test_golden_envelope(caminho_envelope, politica_v4, cambio_real):
    produzido = _produz(caminho_envelope, politica_v4, cambio_real)
    esperado = json.loads(_GOLDEN_ENVELOPE, parse_float=Decimal)
    assert produzido == esperado


@pytest.mark.parametrize("caminho", ["caminho_exemplo", "caminho_envelope"])
def test_invariante_por_categoria(caminho, request, politica_v4, cambio_real):
    produzido = _produz(request.getfixturevalue(caminho), politica_v4, cambio_real)
    for cat in produzido["categorias"].values():
        assert cat["total_despesas"] >= cat["total_aceito"] >= cat["total_reembolso"]


def test_determinismo(caminho_envelope, politica_v4, cambio_real):
    a = _produz(caminho_envelope, politica_v4, cambio_real)
    b = _produz(caminho_envelope, politica_v4, cambio_real)
    assert a == b
