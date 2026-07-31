"""Modelo de dados do nucleo puro (dataclasses + enums).

Valores monetarios sao `Decimal` com 2 casas. Nomes de campo de saida seguem a
Secao 4 da spec. Ver `data-model.md`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum


class Categoria(str, Enum):
    """Categorias validas (RN-001)."""

    ALIMENTACAO = "alimentacao"
    TRANSPORTE_URBANO = "transporte_urbano"
    HOSPEDAGEM = "hospedagem"


class Motivo(str, Enum):
    """Motivos de recusa — texto exato da spec (RN-006/007/008/010/013, AMB-011)."""

    CATEGORIA_NAO_APLICAVEL = "categoria não aplicável"
    DATA_FORA_COMPETENCIA = "data fora da competência"
    REGISTRO_DUPLICADO = "registro duplicado"
    SEM_NOTA_FISCAL = "sem nota fiscal obrigatória"
    VALOR_INVALIDO = "valor inválido"
    REGISTRO_INVALIDO = "registro inválido"


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
    """Despesa normalizada (RN-011, RN-001)."""

    id: str
    data: date
    categoria: str
    categoria_norm: str
    descricao: str
    fornecedor: str
    valor: Decimal
    tem_nota_fiscal: bool

    def chave_duplicidade(self) -> tuple:
        """Chave de negocio para duplicidade (RN-008) — sem `id` (AMB-002)."""
        return (
            self.data,
            self.categoria_norm,
            self.descricao,
            self.fornecedor,
            self.valor,
            self.tem_nota_fiscal,
        )


@dataclass
class Reprovacao:
    """Despesa recusada, com o motivo do primeiro gate que falhou."""

    id: str
    motivo: Motivo
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
    """Raiz da saida (Secao 4 da spec)."""

    colaborador: Colaborador
    competencia: str
    periodo: Periodo
    em_viagem: bool
    categorias: dict[str, ResultadoCategoria]
    reprovadas_sem_categoria: list[Reprovacao]
    total_reembolso_geral: Decimal
