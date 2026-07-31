"""Modelo de dados do nucleo puro (dataclasses + enums) — spec 1.4.

Valores monetarios sao `Decimal` com 2 casas. Nomes de campo de saida seguem a
Secao 4 da spec. Ver `data-model.md`.

Nao ha mais enum `Categoria`: as categorias sao dinamicas por centro de custo
(RN-001/RN-015), lidas da politica externa. Tambem nao ha mais campo `em_viagem`
na saida: viagem e por registro, derivada da moeda (RN-009).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum


class Motivo(str, Enum):
    """Motivos de recusa — texto exato da spec.

    O motivo de categoria com limite <= 0 (RN-017) NAO e um valor deste enum: e a
    `observacao` da `CategoriaConfig` (texto livre) ou, na ausencia dela,
    `CATEGORIA_NAO_APLICAVEL`.
    """

    CATEGORIA_NAO_APLICAVEL = "categoria não aplicável"
    DATA_FORA_COMPETENCIA = "data fora da competência"
    REGISTRO_DUPLICADO = "registro duplicado"
    SEM_NOTA_FISCAL = "sem nota fiscal obrigatória"
    VALOR_INVALIDO = "valor inválido"
    REGISTRO_INVALIDO = "registro inválido"
    CAMBIO_NAO_IDENTIFICADO = "cambio não identificado"  # RN-020


def motivo_texto(motivo: Motivo | str) -> str:
    """Texto do motivo, seja ele um `Motivo` (enum) ou a `observacao` (str) da
    categoria com limite <= 0 (RN-017)."""
    return motivo.value if isinstance(motivo, Motivo) else motivo


# --------------------------------------------------------------------------- #
# Entidades da politica externa (politica-v4.json -> puro)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class CategoriaConfig:
    """Configuracao de uma categoria num centro de custo (RN-004/RN-016/RN-017)."""

    limite: Decimal
    periodicidade: str  # "dia" (RN-002) ou "diaria" (RN-003)
    observacao: str | None = None


@dataclass(frozen=True)
class Politica:
    """Politica externa versionada (RN-015)."""

    padrao: dict[str, CategoriaConfig]
    centros_custo: dict[str, dict[str, CategoriaConfig]]
    limiar_nf: Decimal  # nota_fiscal_obrigatoria_acima_de (RN-006)
    acrescimo_viagem_pct: Decimal  # acrescimo_em_viagem_percentual (RN-009)


# --------------------------------------------------------------------------- #
# Entidade do cambio externo (cambio.json -> puro)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Cambio:
    """Tabela de cambio externa (RN-018/RN-019)."""

    moeda_base: str  # normalizada trim+upper
    taxas: dict[date, dict[str, Decimal]]  # data -> {MOEDA: fator}


# --------------------------------------------------------------------------- #
# Entidades de entrada
# --------------------------------------------------------------------------- #
@dataclass
class Colaborador:
    """Identificacao do colaborador (eco do input)."""

    id: str
    nome: str
    centro_custo: str


@dataclass
class Periodo:
    """Janela de competencia; `[inicio, fim]` inclusive (RN-007)."""

    competencia: str
    inicio: date
    fim: date


@dataclass
class Despesa:
    """Despesa normalizada (RN-011, RN-001, RN-018).

    `valor_origem` e o valor na moeda do registro (2 casas); `valor_base` e o valor
    ja convertido para a `moeda_base` do cambio (`None` ate a conversao, ou se
    "cambio não identificado"). `em_viagem` deriva da moeda (RN-009).
    """

    id: str
    data: date
    categoria: str
    categoria_norm: str
    descricao: str
    fornecedor: str
    valor_origem: Decimal
    moeda_norm: str | None
    tem_nota_fiscal: bool
    em_viagem: bool = False
    valor_base: Decimal | None = None

    def chave_duplicidade(self) -> tuple:
        """Chave de negocio para duplicidade (RN-008) — sem `id` (AMB-002), com
        `valor`/`moeda` de ORIGEM (antes da conversao)."""
        return (
            self.data,
            self.categoria_norm,
            self.descricao,
            self.fornecedor,
            self.valor_origem,
            self.moeda_norm,
            self.tem_nota_fiscal,
        )


# --------------------------------------------------------------------------- #
# Entidades de saida
# --------------------------------------------------------------------------- #
@dataclass
class Reprovacao:
    """Despesa recusada, com o motivo do primeiro gate que falhou.

    `motivo` e um `Motivo` (enum) ou a `observacao` (str) da categoria com limite
    <= 0 (RN-017)."""

    id: str
    motivo: Motivo | str
    categoria_informada: str | None = None


@dataclass
class ResultadoCategoria:
    """Totais de uma categoria valida. Invariante: total_despesas >= total_aceito
    >= total_reembolso (AMB-012)."""

    total_despesas: Decimal
    total_aceito: Decimal
    total_reembolso: Decimal
    reprovadas: list[Reprovacao] = field(default_factory=list)


@dataclass
class Resultado:
    """Raiz da saida (Secao 4 da spec 1.4). Sem campo `em_viagem`."""

    colaborador: Colaborador
    competencia: str
    periodo: Periodo
    categorias: dict[str, ResultadoCategoria]
    reprovadas_sem_categoria: list[Reprovacao]
    total_reembolso_geral: Decimal
