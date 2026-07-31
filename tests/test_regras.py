"""Um teste por regra de negocio (RN) sobre `src.regras` (Fase 2)."""

from decimal import Decimal

from src import regras
from src.modelo import Motivo
from tests._apoio import bruto, despesa, periodo


# --------------------------------------------------------------------------- #
# RN-011 — precisao / RN-001 — normalizacao (T-005)
# --------------------------------------------------------------------------- #
def test_rn_011_arredonda_33_333():
    d = despesa(valor=Decimal("33.333"))
    assert d.valor == Decimal("33.33")


def test_rn_001_normaliza_caixa():
    d = despesa(categoria="ALIMENTACAO")
    assert d.categoria_norm == "alimentacao"


# --------------------------------------------------------------------------- #
# RN-013 — validacao estrutural (T-006)
# --------------------------------------------------------------------------- #
def test_rn_013_registro_sem_data():
    registro = bruto()
    del registro["data"]
    assert regras.valida_estrutura(registro) is Motivo.REGISTRO_INVALIDO


def test_rn_013_valor_nao_numerico():
    assert regras.valida_estrutura(bruto(valor="abc")) is Motivo.REGISTRO_INVALIDO


def test_rn_013_data_nao_parseavel():
    assert regras.valida_estrutura(bruto(data="2026-13-40")) is Motivo.REGISTRO_INVALIDO


def test_rn_013_registro_valido_passa():
    assert regras.valida_estrutura(bruto()) is None


# --------------------------------------------------------------------------- #
# RN-008 — duplicatas (T-007)
# --------------------------------------------------------------------------- #
def test_rn_008_mantem_primeira():
    d006 = despesa(id="d-006", descricao="Almoco", valor=Decimal("54.90"))
    d007 = despesa(id="d-007", descricao="Almoco", valor=Decimal("54.90"))
    resultado = regras.deduplica([d006, d007])
    assert resultado[0] == (d006, None)
    assert resultado[1] == (d007, Motivo.REGISTRO_DUPLICADO)


def test_rn_008_id_nao_conta_para_duplicidade():
    a = despesa(id="a")
    b = despesa(id="b")
    resultado = regras.deduplica([a, b])
    assert resultado[1][1] is Motivo.REGISTRO_DUPLICADO


# --------------------------------------------------------------------------- #
# RN-001 — categoria valida (T-008)
# --------------------------------------------------------------------------- #
def test_rn_001_coworking_invalida():
    assert regras.valida_categoria(despesa(categoria="coworking")) is (
        Motivo.CATEGORIA_NAO_APLICAVEL
    )


def test_rn_001_uppercase_valida():
    assert regras.valida_categoria(despesa(categoria="ALIMENTACAO")) is None


# --------------------------------------------------------------------------- #
# RN-007 — periodo (T-009)
# --------------------------------------------------------------------------- #
def test_rn_007_fora():
    d = despesa(data="2026-04-15")
    assert regras.valida_periodo(d, periodo()) is Motivo.DATA_FORA_COMPETENCIA


def test_rn_007_limite_inclusivo():
    d = despesa(data="2026-07-31")
    assert regras.valida_periodo(d, periodo()) is None


# --------------------------------------------------------------------------- #
# RN-010 — valor invalido (T-010)
# --------------------------------------------------------------------------- #
def test_rn_010_negativo():
    d = despesa(valor=Decimal("-45.00"))
    assert regras.valida_valor(d) is Motivo.VALOR_INVALIDO


def test_rn_010_zero_invalido():
    assert regras.valida_valor(despesa(valor=Decimal("0"))) is Motivo.VALOR_INVALIDO


# --------------------------------------------------------------------------- #
# RN-006 — nota fiscal (T-011)
# --------------------------------------------------------------------------- #
def test_rn_006_100_ok():
    d = despesa(valor=Decimal("100.00"), tem_nota_fiscal=False)
    assert regras.valida_nota_fiscal(d) is None


def test_rn_006_100_01_recusa():
    d = despesa(valor=Decimal("100.01"), tem_nota_fiscal=False)
    assert regras.valida_nota_fiscal(d) is Motivo.SEM_NOTA_FISCAL


# --------------------------------------------------------------------------- #
# RN-009 — tetos de viagem (T-012)
# --------------------------------------------------------------------------- #
def test_rn_009_tetos_viagem():
    tetos = regras.tetos_efetivos(em_viagem=True)
    assert tetos["alimentacao"] == Decimal("90.00")
    assert tetos["transporte_urbano"] == Decimal("120.00")
    assert tetos["hospedagem"] == Decimal("375.00")


def test_rn_009_nf_nao_escala():
    # O limiar de NF continua 100 mesmo em viagem: 100,01 sem NF ainda recusa.
    d = despesa(valor=Decimal("100.01"), tem_nota_fiscal=False)
    assert regras.valida_nota_fiscal(d) is Motivo.SEM_NOTA_FISCAL


def test_rn_009_sem_viagem_tetos_base():
    tetos = regras.tetos_efetivos(em_viagem=False)
    assert tetos["alimentacao"] == Decimal("60.00")
    assert tetos["transporte_urbano"] == Decimal("80.00")
    assert tetos["hospedagem"] == Decimal("250.00")


# --------------------------------------------------------------------------- #
# RN-002 / RN-003 — tetos diarios (T-013)
# --------------------------------------------------------------------------- #
def test_rn_002_soma_dia():
    aceitas = [
        despesa(data="2026-07-03", valor=Decimal("72.50")),
        despesa(data="2026-07-03", valor=Decimal("38.00")),
    ]
    assert regras.aplica_teto_diario(aceitas, Decimal("60")) == Decimal("60.00")


def test_rn_003_transporte():
    aceitas = [despesa(data="2026-07-06", valor=Decimal("100.00"))]
    assert regras.aplica_teto_diario(aceitas, Decimal("80")) == Decimal("80.00")


def test_rn_002_dias_distintos_somam():
    aceitas = [
        despesa(data="2026-07-03", valor=Decimal("50.00")),
        despesa(data="2026-07-04", valor=Decimal("50.00")),
    ]
    assert regras.aplica_teto_diario(aceitas, Decimal("60")) == Decimal("100.00")


# --------------------------------------------------------------------------- #
# RN-004 — teto de hospedagem por registro (T-014)
# --------------------------------------------------------------------------- #
def test_rn_004_por_registro():
    aceitas = [despesa(id="d-010", valor=Decimal("480.00"))]
    assert regras.aplica_teto_hospedagem(aceitas, Decimal("250")) == Decimal("250.00")


def test_rn_004_dois_registros_no_dia_nao_agregam():
    aceitas = [
        despesa(valor=Decimal("200.00")),
        despesa(valor=Decimal("200.00")),
    ]
    # Cada registro tem seu proprio teto de 250: 200 + 200 = 400.
    assert regras.aplica_teto_hospedagem(aceitas, Decimal("250")) == Decimal("400.00")


# --------------------------------------------------------------------------- #
# RN-005 — reembolso parcial no teto (T-013)
# --------------------------------------------------------------------------- #
def test_rn_005_reembolso_parcial_mantem_aceito_cheio():
    aceitas = [despesa(valor=Decimal("100.00"))]
    reembolso = regras.aplica_teto_diario(aceitas, Decimal("80"))
    rc = regras.agrega_categoria(aceitas, [], reembolso)
    assert rc.total_aceito == Decimal("100.00")  # aceita com valor cheio
    assert rc.total_reembolso == Decimal("80.00")  # limitada ao teto


# --------------------------------------------------------------------------- #
# RN-014 / RN-012 — agregacao (T-015)
# --------------------------------------------------------------------------- #
def test_rn_014_total_despesas():
    # RN-014/D-004: total_despesas soma aceitas + reprovadas, mas exclui valores
    # <= 0. O estorno d-009 (-45,00) NAO entra: 100,00 + 100,01 = 200,01.
    aceitas = [despesa(id="d-003", valor=Decimal("100.00"))]
    reprovadas = [
        (despesa(id="d-004", valor=Decimal("100.01")), Motivo.SEM_NOTA_FISCAL),
        (despesa(id="d-009", valor=Decimal("-45.00")), Motivo.VALOR_INVALIDO),
    ]
    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal("80.00"))
    assert rc.total_despesas == Decimal("200.01")
    assert rc.total_aceito == Decimal("100.00")


def test_rn_014_exclui_valor_nao_positivo():
    # D-004 (opcao A): a exclusao e POR VALOR, nao pelo motivo. Uma despesa
    # negativa recusada por um gate anterior ao de valor (ex.: duplicidade)
    # tambem fica fora de total_despesas.
    aceitas = [despesa(valor=Decimal("50.00"))]
    reprovadas = [
        (despesa(valor=Decimal("-10.00")), Motivo.REGISTRO_DUPLICADO),
        (despesa(valor=Decimal("0.00")), Motivo.DATA_FORA_COMPETENCIA),
        (despesa(valor=Decimal("30.00")), Motivo.SEM_NOTA_FISCAL),
    ]
    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal("50.00"))
    # 50,00 (aceita) + 30,00 (reprovada positiva); -10,00 e 0,00 excluidos.
    assert rc.total_despesas == Decimal("80.00")
    assert rc.total_aceito == Decimal("50.00")


def test_invariante_totais():
    aceitas = [despesa(valor=Decimal("100.00"))]
    reprovadas = [(despesa(valor=Decimal("100.01")), Motivo.SEM_NOTA_FISCAL)]
    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal("80.00"))
    assert rc.total_despesas >= rc.total_aceito >= rc.total_reembolso


def test_rn_012_agrega_aceitas_e_reprovadas():
    aceitas = [despesa(valor=Decimal("50.00"))]
    reprovadas = [(despesa(valor=Decimal("30.00")), Motivo.REGISTRO_DUPLICADO)]
    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal("50.00"))
    assert rc.total_aceito == Decimal("50.00")
    assert rc.total_despesas == Decimal("80.00")
    assert [r.id for r in rc.reprovadas] == ["d-x"]
