"""Testes do pipeline `src.calculo` (ordem dos gates, dedup, categorias) (T-016)."""

from decimal import Decimal

from src.calculo import calcula
from src.modelo import Colaborador, Motivo
from src.regras import ORDEM_CATEGORIAS
from tests._apoio import bruto, periodo

COLAB = Colaborador(id="c-1", nome="Fulano", centro_custo="CC-1")


def _calcula(despesas, em_viagem=False):
    return calcula(despesas, COLAB, periodo(), em_viagem)


def test_ordem_primeiro_gate():
    # d-013 esta no periodo mas e sem NF e acima do teto: o primeiro gate que
    # falha (NF) define o motivo, nao o teto.
    r = _calcula([bruto(categoria="hospedagem", valor=Decimal("690.00"),
                        tem_nota_fiscal=False, data="2026-07-22")])
    assert r.categorias["hospedagem"].reprovadas[0].motivo is Motivo.SEM_NOTA_FISCAL


def test_ordem_periodo_antes_de_nf():
    # Fora do periodo E sem NF acima de 100: deve reportar "data fora da
    # competencia" (periodo e gate anterior a NF).
    r = _calcula([bruto(categoria="transporte_urbano", valor=Decimal("150.00"),
                        tem_nota_fiscal=False, data="2026-04-01")])
    assert r.categorias["transporte_urbano"].reprovadas[0].motivo is (
        Motivo.DATA_FORA_COMPETENCIA
    )


def test_categorias_sempre_presentes():
    r = _calcula([])
    assert set(r.categorias.keys()) == set(ORDEM_CATEGORIAS)
    for cat in ORDEM_CATEGORIAS:
        rc = r.categorias[cat]
        assert rc.total_despesas == Decimal("0")
        assert rc.total_aceito == Decimal("0")
        assert rc.total_reembolso == Decimal("0")


def test_ordem_categorias_fixa():
    r = _calcula([])
    assert list(r.categorias.keys()) == list(ORDEM_CATEGORIAS)


def test_categoria_invalida_vai_para_sem_categoria():
    r = _calcula([bruto(id="d-005", categoria="coworking", valor=Decimal("89.00"))])
    assert len(r.reprovadas_sem_categoria) == 1
    rep = r.reprovadas_sem_categoria[0]
    assert rep.id == "d-005"
    assert rep.categoria_informada == "coworking"
    assert rep.motivo is Motivo.CATEGORIA_NAO_APLICAVEL


def test_registro_invalido_nao_aborta_lote():
    invalido = bruto(id="d-bad")
    del invalido["data"]
    valido = bruto(id="d-ok", valor=Decimal("40.00"))
    r = _calcula([invalido, valido])
    assert any(x.motivo is Motivo.REGISTRO_INVALIDO for x in r.reprovadas_sem_categoria)
    assert r.categorias["alimentacao"].total_aceito == Decimal("40.00")


def test_dedup_no_pipeline_mantem_primeira():
    d1 = bruto(id="d-006", valor=Decimal("54.90"))
    d2 = bruto(id="d-007", valor=Decimal("54.90"))
    r = _calcula([d1, d2])
    alim = r.categorias["alimentacao"]
    assert alim.total_aceito == Decimal("54.90")
    assert alim.reprovadas[0].id == "d-007"
    assert alim.reprovadas[0].motivo is Motivo.REGISTRO_DUPLICADO


def test_em_viagem_amplia_teto():
    d = bruto(categoria="alimentacao", valor=Decimal("85.00"), data="2026-07-05")
    r = _calcula([d], em_viagem=True)
    # 85 <= 90 (teto ampliado) -> reembolso integral.
    assert r.categorias["alimentacao"].total_reembolso == Decimal("85.00")
