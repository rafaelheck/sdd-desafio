"""Constantes de politica de reembolso (Secao 4 da spec / plan.md secao 4).

A politica muda em ciclos de meses e e versionada junto do codigo; por isso vive
como constantes nomeadas, nao como config externa. Todos os valores monetarios
sao `Decimal` para aritmetica exata (DT-001).
"""

from decimal import Decimal

# Tetos diarios por categoria agregada (RN-002, RN-003).
LIMITES_DIARIOS: dict[str, Decimal] = {
    "alimentacao": Decimal("60"),
    "transporte_urbano": Decimal("80"),
}

# Teto de hospedagem por registro, nao por diaria (RN-004 / AMB-006).
LIMITE_HOSPEDAGEM = Decimal("250")

# Nota fiscal exigida para valores estritamente acima deste limiar (RN-006).
LIMIAR_NOTA_FISCAL = Decimal("100")

# Multiplicador aplicado somente aos tetos quando em viagem (RN-009).
MULTIPLICADOR_VIAGEM = Decimal("1.5")

# Categorias reembolsaveis (RN-001).
CATEGORIAS_VALIDAS: frozenset[str] = frozenset(
    {"alimentacao", "transporte_urbano", "hospedagem"}
)

# Precisao monetaria: 2 casas (RN-011).
CASAS_DECIMAIS = Decimal("0.01")
