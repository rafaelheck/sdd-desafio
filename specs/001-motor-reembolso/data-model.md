# Modelo de Dados — Motor de Cálculo de Reembolso

Estruturas internas do núcleo (spec 1.4). Todas puras (sem I/O). Valores monetários são
`Decimal` com 2 casas. Nomes de campo de saída seguem a Seção 4 da spec. **Não há mais**
enum `Categoria` (categorias são dinâmicas por centro de custo, RN-001/015) nem campo
`em_viagem` na saída (viagem é por registro, RN-009).

## Enums

### `Motivo` (motivos de recusa — texto exato da spec)
`CATEGORIA_NAO_APLICAVEL = "categoria não aplicável"`,
`DATA_FORA_COMPETENCIA = "data fora da competência"`,
`REGISTRO_DUPLICADO = "registro duplicado"`,
`SEM_NOTA_FISCAL = "sem nota fiscal obrigatória"`,
`VALOR_INVALIDO = "valor inválido"`,
`REGISTRO_INVALIDO = "registro inválido"`,
`CAMBIO_NAO_IDENTIFICADO = "cambio não identificado"` (novo, RN-020).

> `motivo` de categoria com limite ≤ 0 (RN-017) **não** é um valor de enum: é a `observacao`
> da `CategoriaConfig` (texto livre) ou, se ausente, `CATEGORIA_NAO_APLICAVEL`.

## Entidades da política externa (`politica-v4.json` → puro)

### `CategoriaConfig`
| Campo | Tipo | Regra |
|---|---|---|
| `limite` | `Decimal` | teto da categoria no CC (RN-004); ≤ 0 → não reembolsável (RN-017) |
| `periodicidade` | str | `"dia"` (RN-002) ou `"diaria"` (RN-003) (RN-016) |
| `observacao` | str \| None | motivo quando `limite ≤ 0` (RN-017) |

### `Politica`
| Campo | Tipo | Regra |
|---|---|---|
| `padrao` | dict[str, `CategoriaConfig`] | conjunto usado quando o CC não existe (RN-015) |
| `centros_custo` | dict[str, dict[str, `CategoriaConfig`]] | conjunto por CC |
| `limiar_nf` | `Decimal` | `nota_fiscal_obrigatoria_acima_de` (RN-006) |
| `acrescimo_viagem_pct` | `Decimal` | `acrescimo_em_viagem_percentual` (RN-009) |

**Resolução do CC (RN-015):** `conjunto = centros_custo.get(cc, padrao)`. Categorias válidas =
chaves de `conjunto` (comparadas trim+lower, RN-001/AMB-003).

## Entidade do câmbio externo (`cambio.json` → puro)

### `Cambio`
| Campo | Tipo | Regra |
|---|---|---|
| `moeda_base` | str | normalizada trim+upper; referência de "sem conversão"/"viagem" (RN-018) |
| `taxas` | dict[`date`, dict[str, `Decimal`]] | por data, `MOEDA → fator` (chaves de moeda trim+upper) |

> A `moeda_base` de `politica-v4.json` é ignorada (RN-018).

## Entidades de entrada

### `Colaborador`
| Campo | Tipo | Origem |
|---|---|---|
| `id` / `nome` / `centro_custo` | str | input (eco) |

### `Periodo`
| Campo | Tipo | Regra |
|---|---|---|
| `competencia` | str `YYYY-MM` | eco |
| `inicio` / `fim` | `date` | limites inclusive (RN-007) |

### `Despesa` (após normalização — RN-011, RN-001, RN-018)
| Campo | Tipo | Observação |
|---|---|---|
| `id` | str | técnico; não conta para duplicidade (AMB-002) |
| `data` | `date` | dia civil; também resolve a taxa (RN-019) |
| `categoria` | str | valor original informado |
| `categoria_norm` | str | `categoria.strip().lower()` (RN-001) |
| `descricao` / `fornecedor` | str | |
| `valor_origem` | `Decimal` | `quantize` a 2 casas, na moeda de origem (RN-011) |
| `moeda_norm` | str \| None | `moeda.strip().upper()`; `None` se ausente/`null`/vazio (RN-018) |
| `valor_base` | `Decimal` \| None | convertido para a base; `None` até a conversão ou se "cambio não identificado" |
| `em_viagem` | bool | `moeda_norm is not None and moeda_norm != cambio.moeda_base` (RN-009) |
| `tem_nota_fiscal` | bool | avaliada sobre `valor_base` (RN-006) |

**Validação estrutural (RN-013):** `moeda`, quando presente, deve ser texto; tipo não-textual
(número/booleano/objeto) → `REGISTRO_INVALIDO`. `moeda` ausente/`null`/vazio após `trim` →
`moeda_norm = None` (não inválido).

**Chave de duplicidade (RN-008):** tupla
`(data, categoria_norm, descricao, fornecedor, valor_origem, moeda_norm, tem_nota_fiscal)` — **sem**
`id`, com `valor`/`moeda` de **origem**. Mantém-se a 1ª ocorrência (D-002); as demais →
`REGISTRO_DUPLICADO`.

**Agregação de teto:** periodicidade `"dia"` agrega por `(categoria_norm, data)` com **baldes por
`em_viagem`** (RN-002/009); `"diaria"` é por registro (RN-003).

## Entidades de saída

### `Reprovacao`
| Campo | Tipo | Observação |
|---|---|---|
| `id` | str | id da despesa recusada |
| `motivo` | str | valor de `Motivo` **ou** a `observacao` da categoria (RN-017) |
| `categoria_informada` | str \| None | só em `reprovadas_sem_categoria` |

### `ResultadoCategoria`
| Campo | Tipo | Regra |
|---|---|---|
| `total_despesas` | `Decimal` | soma do `valor_base` de aceitas + reprovadas da categoria, **exceto `valor ≤ 0` e exceto "cambio não identificado"** (RN-014, AMB-017) |
| `total_aceito` | `Decimal` | soma do `valor_base` das aceitas (RN-012) |
| `total_reembolso` | `Decimal` | soma após teto/periodicidade/baldes (RN-002..005/009) |
| `reprovadas` | list[`Reprovacao`] | recusas cuja categoria declarada é válida (incl. limite ≤ 0 e cambio não identificado) |

Invariante: `total_despesas ≥ total_aceito ≥ total_reembolso` (AMB-012).

### `Resultado` (raiz da saída)
| Campo | Tipo |
|---|---|
| `colaborador` | `Colaborador` |
| `competencia` | str |
| `periodo` | `{inicio, fim}` |
| `categorias` | dict[str, `ResultadoCategoria`] — só as válidas do CC **com ≥1 despesa** (AMB-015), na ordem das chaves do CC (DT-011) |
| `reprovadas_sem_categoria` | list[`Reprovacao`] (categoria não aplicável + registro inválido), ordem do input |
| `total_reembolso_geral` | `Decimal` (soma de `total_reembolso` das categorias presentes) |

> Sem campo `em_viagem`. Categorias configuradas sem despesas **não** aparecem (AMB-015).

## Fluxo de transformação (pipeline — Seção 8 da spec 1.4)

```
JSON bruto (input) + Politica + Cambio (já carregados; abort se qualquer arquivo falta/inválido)
  → validação estrutural (por registro)          → REGISTRO_INVALIDO (sem_categoria)
  → normalização (valor 2 casas; categoria_norm; moeda_norm; em_viagem)
  → gate categoria válida (chaves do CC)          → CATEGORIA_NAO_APLICAVEL (sem_categoria)
  → gate limite > 0                               → observacao / CATEGORIA_NAO_APLICAVEL (sob a categoria)
  → CONVERSÃO (taxa por data; valor_base)         → CAMBIO_NAO_IDENTIFICADO (sob a categoria; fora do total)
  → deduplicação (1ª ocorrência; chave inclui moeda) → REGISTRO_DUPLICADO
  → gate período [inicio, fim]                    → DATA_FORA_COMPETENCIA
  → gate valor > 0                                → VALOR_INVALIDO
  → gate nota fiscal (valor_base > limiar exige NF) → SEM_NOTA_FISCAL
  → aceitas: teto por periodicidade (dia c/ baldes de viagem; diaria por registro)
  → agrega por categoria + total geral
Resultado (sem em_viagem)
```

`total_despesas` acumula o `valor_base` das despesas de categoria válida (aceitas e reprovadas por
limite ≤ 0 / duplicidade / período / NF) **cujo `valor > 0`**; exclui `valor ≤ 0` (por valor, não por
motivo — RN-014/D-004) e "cambio não identificado" (sem `valor_base` — AMB-017). Registros inválidos e
categoria não aplicável vão para `reprovadas_sem_categoria`.
