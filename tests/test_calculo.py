"""Testes do pipeline `src.calculo` (T-040), spec 1.4.

Ordem dos gates (com conversao), exclusao de cambio nao identificado, categorias
dinamicas e agregacao em valor_base. Cobre RN-012 e RN-016.
"""

from decimal import Decimal

from src.calculo import calcula
from src.modelo import Colaborador, Motivo
from src.modelo import motivo_texto
from tests._apoio import CAMBIO_PADRAO, bruto, config, periodo, politica

COLAB = Colaborador(id="c-1", nome="Fulano", centro_custo="CC-X")


def _calcula(despesas, pol):
    return calcula(despesas, COLAB, periodo(), pol, CAMBIO_PADRAO)


def test_ordem_gates_cambio():
    # GBP (cambio nao id) numa categoria valida, tambem fora do periodo: o gate de
    # cambio (6) vem antes de periodo (8) -> reporta cambio nao identificado.
    pol = politica(padrao={"representacao": config("300")})
    r = _calcula(
        [bruto(categoria="representacao", moeda="GBP", data="2026-04-01", valor=Decimal("55.00"))],
        pol,
    )
    assert r.categorias["representacao"].reprovadas[0].motivo is (
        Motivo.CAMBIO_NAO_IDENTIFICADO
    )


def test_limite_zero_prevalece_sobre_nf_e_cambio():
    # hospedagem limite 0: "nao reembolsavel" (gate 5) prevalece sobre sem NF e
    # sobre cambio nao identificado (GBP).
    pol = politica(padrao={"hospedagem": config("0", "diaria", "nao reembolsavel")})
    r = _calcula(
        [bruto(categoria="hospedagem", moeda="GBP", data="2026-07-14", valor=Decimal("690.00"), tem_nota_fiscal=False)],
        pol,
    )
    rep = r.categorias["hospedagem"].reprovadas[0]
    assert motivo_texto(rep.motivo) == "nao reembolsavel"


def test_agrega_exclui_cambio_nao_id():
    # e-006-like: GBP em categoria valida -> reprovada, fora de total_despesas.
    pol = politica(padrao={"representacao": config("300")})
    r = _calcula(
        [
            bruto(id="ok", categoria="representacao", data="2026-07-13", valor=Decimal("340.00")),
            bruto(id="gbp", categoria="representacao", moeda="GBP", data="2026-07-14", valor=Decimal("55.00")),
        ],
        pol,
    )
    rep = r.categorias["representacao"]
    assert rep.total_despesas == Decimal("340.00")  # gbp excluido
    assert any(x.id == "gbp" and x.motivo is Motivo.CAMBIO_NAO_IDENTIFICADO for x in rep.reprovadas)


def test_categorias_dinamicas_so_com_despesa():
    # Politica com 2 categorias, input so com uma -> so ela aparece (AMB-015).
    pol = politica(padrao={"alimentacao": config("60"), "transporte_urbano": config("80")})
    r = _calcula([bruto(categoria="alimentacao", valor=Decimal("40.00"))], pol)
    assert list(r.categorias.keys()) == ["alimentacao"]


def test_rn_012_agrega_valor_base():
    # RN-012 — a agregacao usa o valor JA convertido para a base (EUR -> BRL).
    pol = politica(padrao={"alimentacao": config("200")})
    r = _calcula(
        [bruto(categoria="alimentacao", moeda="EUR", data="2026-07-14", valor=Decimal("22.00"), tem_nota_fiscal=True)],
        pol,
    )
    # 22,00 x 5,93 = 130,46 (base).
    assert r.categorias["alimentacao"].total_aceito == Decimal("130.46")
    assert r.categorias["alimentacao"].total_reembolso == Decimal("130.46")


def test_rn_016_seleciona_mecanica():
    # RN-016 — a periodicidade escolhe a mecanica; o nome da categoria nao influi.
    despesas = [
        bruto(id="a", categoria="alimentacao", descricao="cafe", data="2026-07-05", valor=Decimal("100.00")),
        bruto(id="b", categoria="alimentacao", descricao="jantar", data="2026-07-05", valor=Decimal("100.00")),
    ]
    dia = _calcula(despesas, politica(padrao={"alimentacao": config("150", "dia")}))
    diaria = _calcula(despesas, politica(padrao={"alimentacao": config("150", "diaria")}))
    # "dia": min(200,150)=150; "diaria": min(100,150)+min(100,150)=200.
    assert dia.categorias["alimentacao"].total_reembolso == Decimal("150.00")
    assert diaria.categorias["alimentacao"].total_reembolso == Decimal("200.00")


def test_registro_invalido_nao_aborta_lote():
    invalido = bruto(id="d-bad")
    del invalido["data"]
    valido = bruto(id="d-ok", categoria="alimentacao", valor=Decimal("40.00"))
    r = _calcula([invalido, valido], politica(padrao={"alimentacao": config("60")}))
    assert any(x.motivo is Motivo.REGISTRO_INVALIDO for x in r.reprovadas_sem_categoria)
    assert r.categorias["alimentacao"].total_aceito == Decimal("40.00")


def test_categoria_invalida_vai_para_sem_categoria():
    r = _calcula(
        [bruto(id="d-005", categoria="coworking", valor=Decimal("89.00"))],
        politica(padrao={"alimentacao": config("60")}),
    )
    assert len(r.reprovadas_sem_categoria) == 1
    rep = r.reprovadas_sem_categoria[0]
    assert rep.id == "d-005"
    assert rep.categoria_informada == "coworking"
    assert rep.motivo is Motivo.CATEGORIA_NAO_APLICAVEL


def test_dedup_no_pipeline_mantem_primeira():
    d1 = bruto(id="d-006", valor=Decimal("54.90"))
    d2 = bruto(id="d-007", valor=Decimal("54.90"))
    r = _calcula([d1, d2], politica(padrao={"alimentacao": config("60")}))
    alim = r.categorias["alimentacao"]
    assert alim.total_aceito == Decimal("54.90")
    assert alim.reprovadas[0].id == "d-007"
    assert alim.reprovadas[0].motivo is Motivo.REGISTRO_DUPLICADO


def test_sem_despesa_nenhuma_categoria():
    r = _calcula([], politica(padrao={"alimentacao": config("60")}))
    assert r.categorias == {}
    assert r.total_reembolso_geral == Decimal("0")
