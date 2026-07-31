# Motor de Cálculo de Reembolso

CLI que lê um JSON de despesas corporativas e emite um JSON com o valor
reembolsável e a justificativa de cada item, aplicando a política de RH,
limites por centro de custo e conversão de câmbio.

- **O quê:** [`specs/001-motor-reembolso/spec.md`](specs/001-motor-reembolso/spec.md)
- **Como:** [`specs/001-motor-reembolso/plan.md`](specs/001-motor-reembolso/plan.md)
- **Em que ordem:** [`specs/001-motor-reembolso/tasks.md`](specs/001-motor-reembolso/tasks.md)
- **Contrato da CLI:** [`specs/001-motor-reembolso/contracts/cli-contract.md`](specs/001-motor-reembolso/contracts/cli-contract.md)

## Pré-requisitos

- Python 3.13.x (runtime usa **somente a stdlib**; sem dependências externas)
- (Dev) `pytest`

## Setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS:        source .venv/bin/activate
pip install -e ".[dev]"   # instala o pacote + pytest; cria o comando `calcular`
```

O `pip install -e` é opcional: dá para rodar direto do repositório sem instalar
nada (veja abaixo). Ele só é necessário para usar o console script `calcular`.

## Como rodar

`calcular` é um **subcomando** do `argparse`; as três formas abaixo são equivalentes.

```bash
# sem instalar, direto do repositório (forma primária)
python -m src.cli calcular --input exemplos/despesas-exemplo.json --output resultado.json

# equivalente via pacote
python -m src calcular --input exemplos/despesas-exemplo.json --output resultado.json

# console script instalado (usa política/câmbio empacotados em src/informacoes_externas/)
calcular --input exemplos/despesas-exemplo.json --output resultado.json

# input com moedas estrangeiras (converte via cambio.json; viagem derivada por registro)
python -m src.cli calcular --input exemplos/despesas-envelope.json --output resultado.json

# apontando política/câmbio alternativos
python -m src.cli calcular --input in.json --output out.json --politica outra-politica.json --cambio outro-cambio.json
```

### Opções

| Flag | Obrigatória | Descrição |
|---|---|---|
| `--input` | sim | JSON de despesas de entrada |
| `--output` | sim | caminho do JSON de resultado |
| `--politica` | não | política alternativa; sem ela usa a empacotada em `src/informacoes_externas/` |
| `--cambio` | não | tabela de câmbio alternativa; sem ela usa a empacotada em `src/informacoes_externas/` |

> `calcular` é obrigatório: `python -m src --input ...` (sem o subcomando) não vale mais.
> Não há `--em-viagem`: viagem é derivada por registro quando `moeda ≠ moeda_base` (RN-009).

## Como testar

```bash
pytest                              # tudo
pytest tests/test_regras.py         # 1 teste por RN (RN-001..RN-020)
pytest tests/test_cambio.py         # conversão, data mais próxima, empate, câmbio não identificado
pytest tests/test_integracao.py     # goldens: exemplo (351.43) e envelope (1228.72)
pytest -k rn_018                    # foco numa regra específica
```

Convenção: cada teste cita o `RN-NNN` (ou o caso de borda da Seção 7 da spec) no
nome. O teste `test_cobertura_rn` garante que toda `RN-001..RN-020` tem cobertura.

### Validação ponta a ponta (aceite)

Dois exemplos de referência com resultados conhecidos:

| Input | Centro de custo | `total_reembolso_geral` esperado |
|---|---|---|
| `exemplos/despesas-exemplo.json` | `CC-ENG-PLATAFORMA` (sem moeda estrangeira) | **`351.43`** |
| `exemplos/despesas-envelope.json` | `CC-COMERCIAL` (EUR/USD/GBP) | **`1228.72`** |

O detalhamento por categoria e registro está no
[`quickstart.md`](specs/001-motor-reembolso/quickstart.md).

## Cenários de erro

| Cenário | Resultado |
|---|---|
| `--input`/`--politica`/`--cambio` inexistente ou JSON inparseável | mensagem em `stderr`, código `1`, nada escrito |
| Falta o subcomando `calcular`, ou falta `--input`/`--output` | erro de uso do `argparse`, código `2` |
| Registro de despesa malformado (ex.: `moeda` numérica) | `registro inválido`; os demais processados; código `0` |
| `moeda` sem taxa em todo o câmbio (ex.: GBP) | `cambio não identificado` **por registro**; código `0` |

## Estrutura

```
src/
├── cli.py                 # parsing de argumentos, I/O e exit codes
├── io_json.py             # leitura/escrita de JSON (Decimal)
├── calculo.py             # orquestração do cálculo (núcleo puro)
├── regras.py              # uma função por RN (RN-001..RN-020)
├── politica.py            # carga/validação da política
├── modelo.py              # tipos do domínio
└── informacoes_externas/  # política e câmbio empacotados (padrão)
tests/                     # 1 teste por RN + câmbio + integração (goldens)
specs/001-motor-reembolso/ # spec, plan, tasks, contrato e quickstart
```

Núcleo puro (`calculo.py`, `regras.py`, `politica.py`, `modelo.py`) não faz I/O;
toda leitura/escrita/exit code vive em `cli.py` e `io_json.py`. Valores monetários
usam `decimal.Decimal` com 2 casas (`ROUND_HALF_UP`) — nunca `float`.
