"""Pipeline puro que orquestra as regras na ordem da Secao 8 da spec (DT-004).

estrutura -> normalizacao -> deduplicacao -> categoria -> periodo -> valor ->
nota fiscal -> tetos -> agregacao. O primeiro gate que falha define o motivo da
recusa (AMB-010). Nao faz I/O.
"""

from __future__ import annotations

from decimal import Decimal

from src import regras
from src.modelo import (
    Colaborador,
    Despesa,
    Motivo,
    Periodo,
    Reprovacao,
    Resultado,
    ResultadoCategoria,
)
from src.politica import CATEGORIAS_VALIDAS
from src.regras import ORDEM_CATEGORIAS


def calcula(
    despesas_brutas: list,
    colaborador: Colaborador,
    periodo: Periodo,
    em_viagem: bool,
) -> Resultado:
    """Executa o pipeline completo e devolve o `Resultado` agregado."""
    tetos = regras.tetos_efetivos(em_viagem)

    reprovadas_sem_categoria: list[Reprovacao] = []
    aceitas_por_cat: dict[str, list[Despesa]] = {c: [] for c in ORDEM_CATEGORIAS}
    reprovadas_por_cat: dict[str, list[tuple[Despesa, Motivo]]] = {
        c: [] for c in ORDEM_CATEGORIAS
    }

    # Passo 1 — validacao estrutural (por registro).
    validos: list[dict] = []
    for bruto in despesas_brutas:
        motivo = regras.valida_estrutura(bruto)
        if motivo is not None:
            reprovadas_sem_categoria.append(
                Reprovacao(
                    id=_id_bruto(bruto),
                    motivo=motivo,
                    categoria_informada=_categoria_bruta(bruto),
                )
            )
        else:
            validos.append(bruto)

    # Passo 2 — normalizacao.
    normalizadas = [regras.normaliza_despesa(b) for b in validos]

    # Passo 3 — deduplicacao (mantem 1a ocorrencia).
    dedup = regras.deduplica(normalizadas)

    # Passos 4-7 — gates. O primeiro que falha define o motivo.
    for despesa, motivo_dedup in dedup:
        motivo = motivo_dedup
        if motivo is None:
            motivo = regras.valida_categoria(despesa)
            if motivo is Motivo.CATEGORIA_NAO_APLICAVEL:
                reprovadas_sem_categoria.append(
                    Reprovacao(
                        id=despesa.id,
                        motivo=motivo,
                        categoria_informada=despesa.categoria,
                    )
                )
                continue
            if motivo is None:
                motivo = regras.valida_periodo(despesa, periodo)
            if motivo is None:
                motivo = regras.valida_valor(despesa)
            if motivo is None:
                motivo = regras.valida_nota_fiscal(despesa)

        _classifica(
            despesa, motivo, reprovadas_por_cat, aceitas_por_cat, reprovadas_sem_categoria
        )

    # Passos 8-9 — tetos e agregacao, em ordem fixa de categoria.
    categorias: dict[str, ResultadoCategoria] = {}
    total_geral = Decimal("0")
    for cat in ORDEM_CATEGORIAS:
        aceitas = aceitas_por_cat[cat]
        if cat == "hospedagem":
            reembolso = regras.aplica_teto_hospedagem(aceitas, tetos[cat])
        else:
            reembolso = regras.aplica_teto_diario(aceitas, tetos[cat])
        categorias[cat] = regras.agrega_categoria(
            aceitas, reprovadas_por_cat[cat], reembolso
        )
        total_geral += reembolso

    return Resultado(
        colaborador=colaborador,
        competencia=periodo.competencia,
        periodo=periodo,
        em_viagem=em_viagem,
        categorias=categorias,
        reprovadas_sem_categoria=reprovadas_sem_categoria,
        total_reembolso_geral=total_geral,
    )


def _classifica(
    despesa: Despesa,
    motivo: Motivo | None,
    reprovadas_por_cat: dict[str, list[tuple[Despesa, Motivo]]],
    aceitas_por_cat: dict[str, list[Despesa]],
    reprovadas_sem_categoria: list[Reprovacao],
) -> None:
    """Coloca a despesa no balde certo. Recusas com categoria valida ficam sob a
    categoria; recusas sem categoria valida vao para `reprovadas_sem_categoria`."""
    if motivo is None:
        aceitas_por_cat[despesa.categoria_norm].append(despesa)
        return
    if despesa.categoria_norm in CATEGORIAS_VALIDAS:
        reprovadas_por_cat[despesa.categoria_norm].append((despesa, motivo))
    else:
        reprovadas_sem_categoria.append(
            Reprovacao(
                id=despesa.id,
                motivo=motivo,
                categoria_informada=despesa.categoria,
            )
        )


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
