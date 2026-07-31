"""Golden test ponta a ponta contra a saida da Secao 4 da spec (T-022)."""

import json
from decimal import Decimal

import pytest

from src import io_json
from src.calculo import calcula

# Saida esperada exata da Secao 4 da spec (em_viagem = false).
_ESPERADO_SEM_VIAGEM = """
{
  "colaborador": {
    "id": "c-0417",
    "nome": "Marina Volpi",
    "centro_custo": "CC-ENG-PLATAFORMA"
  },
  "competencia": "2026-07",
  "periodo": {
    "inicio": "2026-07-01",
    "fim": "2026-07-31"
  },
  "em_viagem": false,
  "categorias": {
    "alimentacao": {
      "total_despesas": 402.83,
      "total_aceito": 306.93,
      "total_reembolso": 255.43,
      "reprovadas": [
        { "id": "d-007", "motivo": "registro duplicado" },
        { "id": "d-008", "motivo": "data fora da competência" }
      ]
    },
    "transporte_urbano": {
      "total_despesas": 200.01,
      "total_aceito": 100.00,
      "total_reembolso": 80.00,
      "reprovadas": [
        { "id": "d-004", "motivo": "sem nota fiscal obrigatória" },
        { "id": "d-009", "motivo": "valor inválido" }
      ]
    },
    "hospedagem": {
      "total_despesas": 1170.00,
      "total_aceito": 480.00,
      "total_reembolso": 250.00,
      "reprovadas": [
        { "id": "d-013", "motivo": "sem nota fiscal obrigatória" }
      ]
    }
  },
  "reprovadas_sem_categoria": [
    { "id": "d-005", "categoria_informada": "coworking", "motivo": "categoria não aplicável" }
  ],
  "total_reembolso_geral": 585.43
}
"""


def _produz(caminho, em_viagem):
    entrada = io_json.ler_entrada(caminho)
    resultado = calcula(
        entrada.despesas_brutas, entrada.colaborador, entrada.periodo, em_viagem
    )
    # Parse com Decimal dos dois lados para comparacao exata de centavos.
    return json.loads(io_json.serializa(resultado), parse_float=Decimal)


def test_golden_sem_viagem(caminho_exemplo):
    produzido = _produz(caminho_exemplo, em_viagem=False)
    esperado = json.loads(_ESPERADO_SEM_VIAGEM, parse_float=Decimal)
    assert produzido == esperado


def test_golden_invariante_por_categoria(caminho_exemplo):
    produzido = _produz(caminho_exemplo, em_viagem=False)
    for cat in produzido["categorias"].values():
        assert cat["total_despesas"] >= cat["total_aceito"] >= cat["total_reembolso"]


def test_em_viagem_amplia_tetos_mas_nao_nf(caminho_exemplo):
    produzido = _produz(caminho_exemplo, em_viagem=True)
    cats = produzido["categorias"]
    # Tetos ampliados (90/120/375):
    assert cats["alimentacao"]["total_reembolso"] == Decimal("286.43")
    assert cats["transporte_urbano"]["total_reembolso"] == Decimal("100.00")
    assert cats["hospedagem"]["total_reembolso"] == Decimal("375.00")
    assert produzido["total_reembolso_geral"] == Decimal("761.43")
    # Limiar de NF NAO escala: d-004 e d-013 continuam recusados.
    ids_recusados = {
        r["id"] for c in cats.values() for r in c["reprovadas"]
    } | {r["id"] for r in produzido["reprovadas_sem_categoria"]}
    assert {"d-004", "d-013"} <= ids_recusados


@pytest.mark.parametrize("em_viagem", [False, True])
def test_determinismo(caminho_exemplo, em_viagem):
    assert _produz(caminho_exemplo, em_viagem) == _produz(caminho_exemplo, em_viagem)
