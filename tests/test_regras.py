"""Um teste por regra de negocio (RN) sobre `src.regras` (T-046), spec 1.4.

RN-012/RN-015/RN-016/RN-018/RN-019/RN-020 sao cobertas em `test_calculo.py`,
`test_politica.py` e `test_cambio.py` (com testes cujo nome contem o proprio RN).
"""

from decimal import Decimal

from src import regras
from src.modelo import Motivo
from tests._apoio import CAMBIO_PADRAO, aceita, config, despesa, periodo


# --------------------------------------------------------------------------- #
# RN-011 — precisao
# --------------------------------------------------------------------------- #
def test_rn_011_arredonda_33_333():
    d = despesa(valor=Decimal("33.333"))
    assert d.valor_origem == Decimal("33.33")


# --------------------------------------------------------------------------- #
# RN-013 — validacao estrutural (inclui tipo de `moeda`)
# --------------------------------------------------------------------------- #
def test_rn_013_registro_sem_data():
    from tests._apoio import bruto

    registro = bruto()
    del registro["data"]
    assert regras.valida_estrutura(registro) is Motivo.REGISTRO_INVALIDO


def test_rn_013_moeda_numerica_invalida():
    from tests._apoio import bruto

    assert regras.valida_estrutura(bruto(moeda=5)) is Motivo.REGISTRO_INVALIDO


def test_rn_013_moeda_vazia_nao_e_invalida():
    from tests._apoio import bruto

    # "" e vazio apos trim -> sem moeda (base), nao invalido.
    assert regras.valida_estrutura(bruto(moeda="")) is None
    assert regras.valida_estrutura(bruto(moeda=None)) is None


# --------------------------------------------------------------------------- #
# RN-001 — categoria valida por centro de custo (dinamica)
# --------------------------------------------------------------------------- #
def test_rn_001_coworking_invalida():
    conjunto = {"alimentacao": config("60")}
    assert regras.valida_categoria(despesa(categoria="coworking"), conjunto) is (
        Motivo.CATEGORIA_NAO_APLICAVEL
    )


def test_rn_001_uppercase_valida():
    conjunto = {"alimentacao": config("60")}
    assert regras.valida_categoria(despesa(categoria="ALIMENTACAO"), conjunto) is None


def test_rn_001_representacao_so_comercial():
    eng = {"alimentacao": config("75")}
    comercial = {"alimentacao": config("90"), "representacao": config("300")}
    d = despesa(categoria="representacao")
    assert regras.valida_categoria(d, eng) is Motivo.CATEGORIA_NAO_APLICAVEL
    assert regras.valida_categoria(d, comercial) is None


# --------------------------------------------------------------------------- #
# RN-017 — categoria com limite <= 0 (nao reembolsavel)
# --------------------------------------------------------------------------- #
def test_rn_017_limite_zero_nao_reembolsavel():
    # limite 0 com observacao -> motivo e a observacao (prevalece sobre sem NF).
    cfg = config("0", periodicidade="diaria", observacao="nao reembolsavel")
    d = despesa(valor=Decimal("690.00"), tem_nota_fiscal=False)
    assert regras.valida_limite_categoria(d, cfg) == "nao reembolsavel"


def test_rn_017_limite_zero_sem_observacao():
    cfg = config("0")
    assert regras.valida_limite_categoria(despesa(), cfg) is (
        Motivo.CATEGORIA_NAO_APLICAVEL
    )


def test_rn_017_limite_positivo_passa():
    assert regras.valida_limite_categoria(despesa(), config("60")) is None


# --------------------------------------------------------------------------- #
# RN-007 — periodo
# --------------------------------------------------------------------------- #
def test_rn_007_fora():
    d = despesa(data="2026-04-15")
    assert regras.valida_periodo(d, periodo()) is Motivo.DATA_FORA_COMPETENCIA


def test_rn_007_limite_inclusivo():
    d = despesa(data="2026-07-31")
    assert regras.valida_periodo(d, periodo()) is None


# --------------------------------------------------------------------------- #
# RN-010 — valor invalido
# --------------------------------------------------------------------------- #
def test_rn_010_negativo():
    assert regras.valida_valor(despesa(valor=Decimal("-45.00"))) is Motivo.VALOR_INVALIDO


def test_rn_010_zero_invalido():
    assert regras.valida_valor(despesa(valor=Decimal("0"))) is Motivo.VALOR_INVALIDO


# --------------------------------------------------------------------------- #
# RN-006 — nota fiscal sobre o valor convertido
# --------------------------------------------------------------------------- #
def test_rn_006_sobre_valor_convertido():
    # USD 40 em 07-20 (taxa 5,50) -> 220,00 > 100 e sem NF -> recusada.
    d = despesa(
        moeda="USD", data="2026-07-20", valor=Decimal("40.00"), tem_nota_fiscal=False
    )
    assert d.valor_base == Decimal("220.00")
    assert regras.valida_nota_fiscal(d, Decimal("100")) is Motivo.SEM_NOTA_FISCAL


def test_rn_006_limiar_exato():
    d = despesa(valor=Decimal("100.00"), tem_nota_fiscal=False)  # base, valor_base 100
    assert regras.valida_nota_fiscal(d, Decimal("100")) is None
    acima = despesa(valor=Decimal("100.01"), tem_nota_fiscal=False)
    assert regras.valida_nota_fiscal(acima, Decimal("100")) is Motivo.SEM_NOTA_FISCAL


# --------------------------------------------------------------------------- #
# RN-008 — duplicatas (chave inclui moeda/valor de origem, ignora id)
# --------------------------------------------------------------------------- #
def test_rn_008_mantem_primeira():
    a = despesa(id="d-006", descricao="Almoco", valor=Decimal("54.90"))
    b = despesa(id="d-007", descricao="Almoco", valor=Decimal("54.90"))
    assert a.chave_duplicidade() == b.chave_duplicidade()  # sao duplicatas


def test_rn_008_moeda_diferencia():
    # Iguais salvo a moeda NAO sao duplicados (RN-008 usa moeda de origem).
    brl = despesa(valor=Decimal("50.00"), data="2026-07-14")
    usd = despesa(valor=Decimal("50.00"), data="2026-07-14", moeda="USD")
    assert brl.chave_duplicidade() != usd.chave_duplicidade()


# --------------------------------------------------------------------------- #
# RN-002 — teto de periodicidade "dia" (baldes por viagem)
# --------------------------------------------------------------------------- #
def test_rn_002_soma_dia():
    aceitas = [
        aceita("72.50", data="2026-07-03"),
        aceita("38.00", data="2026-07-03"),
    ]
    # min(110,50, 75) = 75 (nao-viagem).
    assert regras.aplica_teto_dia(aceitas, Decimal("75"), Decimal("1.5")) == Decimal("75.00")


def test_rn_002_baldes_dia_misto():
    # BRL 80 (base) + convertido 80 (viagem) no mesmo dia; limite base 90 / viagem 135.
    aceitas = [
        aceita("80.00", data="2026-07-14", em_viagem=False),
        aceita("80.00", data="2026-07-14", em_viagem=True),
    ]
    # min(80,90) + min(80,135) = 80 + 80 = 160.
    assert regras.aplica_teto_dia(aceitas, Decimal("90"), Decimal("1.5")) == Decimal("160.00")


# --------------------------------------------------------------------------- #
# RN-003 — teto de periodicidade "diaria" (por registro)
# --------------------------------------------------------------------------- #
def test_rn_003_diaria_por_registro():
    aceitas = [aceita("480.00", data="2026-07-14")]
    assert regras.aplica_teto_diaria(aceitas, Decimal("250"), Decimal("1.5")) == Decimal("250.00")


def test_rn_003_dois_registros_no_dia_nao_agregam():
    aceitas = [aceita("200.00"), aceita("200.00")]
    assert regras.aplica_teto_diaria(aceitas, Decimal("250"), Decimal("1.5")) == Decimal("400.00")


# --------------------------------------------------------------------------- #
# RN-004 — origem do teto (limite pela politica, sem categoria privilegiada)
# --------------------------------------------------------------------------- #
def test_rn_004_limite_pela_politica():
    aceitas = [aceita("100.00", data="2026-07-05")]
    # Mesmas aceitas, so muda o `limite` argumento -> muda o teto (vem da politica).
    assert regras.aplica_teto_dia(aceitas, Decimal("60"), Decimal("1.5")) == Decimal("60.00")
    assert regras.aplica_teto_dia(aceitas, Decimal("80"), Decimal("1.5")) == Decimal("80.00")


# --------------------------------------------------------------------------- #
# RN-009 — limite ampliado em viagem (por registro)
# --------------------------------------------------------------------------- #
def test_rn_009_viagem_por_registro():
    viagem = [aceita("1200.00", em_viagem=True)]
    nao = [aceita("1200.00", em_viagem=False)]
    # diaria: limite 400; viagem -> 400 x 1,5 = 600.
    assert regras.aplica_teto_diaria(viagem, Decimal("400"), Decimal("1.5")) == Decimal("600.00")
    assert regras.aplica_teto_diaria(nao, Decimal("400"), Decimal("1.5")) == Decimal("400.00")


# --------------------------------------------------------------------------- #
# RN-005 — reembolso parcial no teto (aceita com valor cheio)
# --------------------------------------------------------------------------- #
def test_rn_005_parcial_no_teto():
    aceitas = [aceita("100.00", data="2026-07-05")]
    reembolso = regras.aplica_teto_dia(aceitas, Decimal("80"), Decimal("1.5"))
    rc = regras.agrega_categoria(aceitas, [], reembolso)
    assert rc.total_aceito == Decimal("100.00")  # aceita com valor cheio
    assert rc.total_reembolso == Decimal("80.00")  # limitada ao teto


# --------------------------------------------------------------------------- #
# RN-014 — total_despesas exclui valor <= 0 e cambio nao identificado
# --------------------------------------------------------------------------- #
def test_rn_014_exclui_valor_nao_positivo():
    aceitas = [aceita("50.00")]
    reprovadas = [
        (aceita("-10.00"), Motivo.REGISTRO_DUPLICADO),
        (aceita("0.00"), Motivo.DATA_FORA_COMPETENCIA),
        (aceita("30.00"), Motivo.SEM_NOTA_FISCAL),
    ]
    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal("50.00"))
    # 50 (aceita) + 30 (reprovada positiva); -10 e 0 excluidos por valor.
    assert rc.total_despesas == Decimal("80.00")
    assert rc.total_aceito == Decimal("50.00")


def test_rn_014_exclui_cambio_nao_id():
    aceitas = [aceita("100.00")]
    gbp = despesa(moeda="GBP", data="2026-07-14", valor=Decimal("55.00"))
    regras.valida_cambio(gbp, CAMBIO_PADRAO)
    reprovadas = [(gbp, Motivo.CAMBIO_NAO_IDENTIFICADO)]
    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal("100.00"))
    assert gbp.valor_base is None
    assert rc.total_despesas == Decimal("100.00")  # gbp fora do total (AMB-017)


def test_invariante_totais():
    aceitas = [aceita("100.00")]
    reprovadas = [(aceita("100.01"), Motivo.SEM_NOTA_FISCAL)]
    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal("80.00"))
    assert rc.total_despesas >= rc.total_aceito >= rc.total_reembolso
