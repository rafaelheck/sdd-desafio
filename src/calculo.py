"""Pipeline puro que orquestra as regras na ordem da Secao 8 da spec 1.4 (DT-012).

estrutura -> resolucao politica+cambio -> normalizacao -> categoria valida ->
limite > 0 -> conversao -> deduplicacao -> periodo -> valor -> nota fiscal (sobre
valor convertido) -> tetos (baldes/periodicidade) -> agregacao. O primeiro gate que
falha define o motivo da recusa (AMB-010). Categorias sao dinamicas por centro de
custo; nenhuma e conhecida em codigo. Nao faz I/O.
"""

from __future__ import annotations

from decimal import Decimal

from src import regras
from src.modelo import (
    Cambio,
    CategoriaConfig,
    Colaborador,
    Despesa,
    Motivo,
    Periodo,
    Politica,
    Reprovacao,
    Resultado,
    ResultadoCategoria,
)


def calcula(
    despesas_brutas: list,
    colaborador: Colaborador,
    periodo: Periodo,
    politica: Politica,
    cambio: Cambio,
) -> Resultado:
    """Executa o pipeline completo e devolve o `Resultado` agregado (sem
    `em_viagem`). O conjunto de categorias e resolvido pelo centro de custo."""
    conjunto = regras.resolve_conjunto(politica, colaborador.centro_custo)
    fator = Decimal("1") + politica.acrescimo_viagem_pct / Decimal("100")

    reprovadas_sem_categoria: list[Reprovacao] = []
    aceitas_por_cat: dict[str, list[Despesa]] = {c: [] for c in conjunto}
    reprovadas_por_cat: dict[str, list[tuple[Despesa, Motivo | str]]] = {
        c: [] for c in conjunto
    }
    vistas: set[tuple] = set()

    for bruto in despesas_brutas:
        # 1 — validacao estrutural.
        if regras.valida_estrutura(bruto) is not None:
            reprovadas_sem_categoria.append(
                Reprovacao(
                    id=_id_bruto(bruto),
                    motivo=Motivo.REGISTRO_INVALIDO,
                    categoria_informada=_categoria_bruta(bruto),
                )
            )
            continue

        # 3 — normalizacao (valor, categoria, moeda, viagem).
        despesa = regras.normaliza_despesa(bruto, cambio)

        # 4 — categoria valida (chaves do conjunto do CC).
        if regras.valida_categoria(despesa, conjunto) is not None:
            reprovadas_sem_categoria.append(
                Reprovacao(
                    id=despesa.id,
                    motivo=Motivo.CATEGORIA_NAO_APLICAVEL,
                    categoria_informada=despesa.categoria,
                )
            )
            continue

        cat = despesa.categoria_norm
        config = conjunto[cat]

        # 6 — conversao de cambio (calculada aqui para dar `valor_base` inclusive
        # aos reprovados por limite <= 0 que compoem `total_despesas`); a RECUSA
        # por cambio nao identificado so e emitida apos o gate de limite (precedencia
        # da Secao 8), abaixo.
        motivo_cambio = regras.valida_cambio(despesa, cambio)

        # 5 — limite da categoria > 0 (prevalece sobre cambio nao identificado).
        motivo_limite = regras.valida_limite_categoria(despesa, config)
        if motivo_limite is not None:
            reprovadas_por_cat[cat].append((despesa, motivo_limite))
            continue

        # 6 (recusa) — cambio nao identificado.
        if motivo_cambio is not None:
            reprovadas_por_cat[cat].append((despesa, motivo_cambio))
            continue

        # 7 — deduplicacao (1a ocorrencia; chave inclui valor/moeda de origem).
        chave = despesa.chave_duplicidade()
        if chave in vistas:
            reprovadas_por_cat[cat].append((despesa, Motivo.REGISTRO_DUPLICADO))
            continue
        vistas.add(chave)

        # 8 — periodo.
        if regras.valida_periodo(despesa, periodo) is not None:
            reprovadas_por_cat[cat].append((despesa, Motivo.DATA_FORA_COMPETENCIA))
            continue

        # 9 — valor valido.
        if regras.valida_valor(despesa) is not None:
            reprovadas_por_cat[cat].append((despesa, Motivo.VALOR_INVALIDO))
            continue

        # 10 — nota fiscal (sobre o valor convertido).
        if regras.valida_nota_fiscal(despesa, politica.limiar_nf) is not None:
            reprovadas_por_cat[cat].append((despesa, Motivo.SEM_NOTA_FISCAL))
            continue

        # Passou de 1 a 10 -> aceita.
        aceitas_por_cat[cat].append(despesa)

    # 11-12 — tetos e agregacao, na ordem das chaves do CC; so categorias com >= 1
    # despesa aparecem (AMB-015).
    categorias: dict[str, ResultadoCategoria] = {}
    total_geral = Decimal("0")
    for cat, config in conjunto.items():
        aceitas = aceitas_por_cat[cat]
        reprovadas = reprovadas_por_cat[cat]
        if not aceitas and not reprovadas:
            continue  # categoria sem despesa nao e emitida.
        reembolso = _reembolso_categoria(aceitas, config, fator)
        categorias[cat] = regras.agrega_categoria(aceitas, reprovadas, reembolso)
        total_geral += reembolso

    return Resultado(
        colaborador=colaborador,
        competencia=periodo.competencia,
        periodo=periodo,
        categorias=categorias,
        reprovadas_sem_categoria=reprovadas_sem_categoria,
        total_reembolso_geral=total_geral,
    )


def _reembolso_categoria(
    aceitas: list[Despesa], config: CategoriaConfig, fator: Decimal
) -> Decimal:
    """Aplica o teto conforme a `periodicidade` (RN-016)."""
    if config.periodicidade == "diaria":
        return regras.aplica_teto_diaria(aceitas, config.limite, fator)
    return regras.aplica_teto_dia(aceitas, config.limite, fator)


def _id_bruto(bruto: object) -> str | None:
    if isinstance(bruto, dict):
        valor = bruto.get("id")
        return valor if isinstance(valor, str) else None
    return None


def _categoria_bruta(bruto: object) -> str | None:
    if isinstance(bruto, dict):
        valor = bruto.get("categoria")
        return valor if isinstance(valor, str) else None
    return None
