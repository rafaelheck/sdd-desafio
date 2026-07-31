# Modelo de Dados — Motor de Cálculo de Reembolso

Estruturas internas do núcleo. Todas puras (sem I/O). Valores monetários são
`Decimal` com 2 casas. Nomes de campo de saída seguem a Seção 4 da spec.

## Enums

### `Categoria` (categorias válidas — RN-001)
`ALIMENTACAO = "alimentacao"`, `TRANSPORTE_URBANO = "transporte_urbano"`,
`HOSPEDAGEM = "hospedagem"`.

### `Motivo` (motivos de recusa — texto exato da spec)
`CATEGORIA_NAO_APLICAVEL = "categoria não aplicável"`,
`DATA_FORA_COMPETENCIA = "data fora da competência"`,
`REGISTRO_DUPLICADO = "registro duplicado"`,
`SEM_NOTA_FISCAL = "sem nota fiscal obrigatória"`,
`VALOR_INVALIDO = "valor inválido"`,
`REGISTRO_INVALIDO = "registro inválido"`.

## Entidades de entrada

### `Colaborador`
| Campo | Tipo | Origem |
|---|---|---|
| `id` | str | input |
| `nome` | str | input |
| `centro_custo` | str | input |

### `Periodo`
| Campo | Tipo | Regra |
|---|---|---|
| `competencia` | str `YYYY-MM` | eco |
| `inicio` | `date` | limite inferior inclusive (RN-007) |
| `fim` | `date` | limite superior inclusive (RN-007) |

### `Despesa` (após normalização — RN-011, RN-001)
| Campo | Tipo | Observação |
|---|---|---|
| `id` | str | identificador técnico; não conta para duplicidade (AMB-002) |
| `data` | `date` | dia civil |
| `categoria` | str | valor original informado |
| `categoria_norm` | str | `categoria.strip().lower()` para comparação (RN-001) |
| `descricao` | str | |
| `fornecedor` | str | |
| `valor` | `Decimal` | já `quantize` a 2 casas (RN-011) |
| `tem_nota_fiscal` | bool | |

**Chave de duplicidade (RN-008):** tupla
`(data, categoria_norm, descricao, fornecedor, valor, tem_nota_fiscal)` —
**sem** `id`. Mantém-se a 1ª ocorrência na ordem do input (D-002); as demais
viram `REGISTRO_DUPLICADO`.

**Chave de agregação diária (RN-002/003):** `(categoria_norm, data)` para
`alimentacao` e `transporte_urbano`. `hospedagem` é por registro (RN-004).

## Entidades de saída

### `Reprovacao`
| Campo | Tipo | Observação |
|---|---|---|
| `id` | str | id da despesa recusada |
| `motivo` | `Motivo` | |
| `categoria_informada` | str \| None | preenchido só em `reprovadas_sem_categoria` |

### `ResultadoCategoria`
| Campo | Tipo | Regra |
|---|---|---|
| `total_despesas` | `Decimal` | soma do `valor` de aceitas + reprovadas da categoria (RN-014) |
| `total_aceito` | `Decimal` | soma do `valor` das aceitas (RN-012) |
| `total_reembolso` | `Decimal` | soma após tetos (RN-002..RN-005) |
| `reprovadas` | list[`Reprovacao`] | recusas cuja categoria declarada é válida |

Invariante: `total_despesas ≥ total_aceito ≥ total_reembolso` (AMB-012).

### `Resultado` (raiz da saída)
| Campo | Tipo |
|---|---|
| `colaborador` | `Colaborador` |
| `competencia` | str |
| `periodo` | `{inicio, fim}` |
| `em_viagem` | bool |
| `categorias` | dict[str, `ResultadoCategoria`] (as 3 válidas, sempre presentes) |
| `reprovadas_sem_categoria` | list[`Reprovacao`] (categoria não aplicável + registro inválido) |
| `total_reembolso_geral` | `Decimal` |

> As três categorias válidas aparecem sempre em `categorias`, mesmo com totais
> zerados (nenhuma despesa naquela categoria) — mantém a saída previsível.

## Fluxo de transformação (pipeline — Seção 8 da spec)

```
JSON bruto
  → validação estrutural (por registro)         → REGISTRO_INVALIDO (sem_categoria)
  → normalização (Decimal 2 casas, categoria_norm, multiplicador de viagem nos tetos)
  → deduplicação (1ª ocorrência vence)          → REGISTRO_DUPLICADO
  → gate categoria válida                        → CATEGORIA_NAO_APLICAVEL (sem_categoria)
  → gate período [inicio, fim]                   → DATA_FORA_COMPETENCIA
  → gate valor > 0                               → VALOR_INVALIDO
  → gate nota fiscal (valor > 100 exige NF)      → SEM_NOTA_FISCAL
  → aceitas: aplica teto (dia p/ alim/transp, registro p/ hospedagem)
  → agrega por categoria (total_despesas, total_aceito, total_reembolso) + total geral
Resultado
```

`total_despesas` acumula o `valor` de **todas** as despesas com categoria válida
(aceitas e reprovadas por duplicidade/período/NF/valor); registros inválidos e
categoria não aplicável não entram em nenhuma categoria (vão para
`reprovadas_sem_categoria`).
