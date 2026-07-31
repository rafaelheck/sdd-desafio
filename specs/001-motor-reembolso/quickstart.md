# Quickstart — Motor de Cálculo de Reembolso

Guia de execução e validação (spec 1.4). Detalhes de regra na [`spec.md`](./spec.md),
de arquitetura no [`plan.md`](./plan.md) e da CLI em
[`contracts/cli-contract.md`](./contracts/cli-contract.md).

## Pré-requisitos

- Python 3.13.x
- (Dev) `pytest`

## Setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"   # instala o pacote + pytest; cria o comando `calcular`
```

## Rodar

`calcular` é um **subcomando** do `argparse`; as três formas abaixo são equivalentes.

```bash
# sem instalar, direto do repositório (forma primária)
python -m src.cli calcular --input exemplos/despesas-exemplo.json --output resultado.json

# equivalente via pacote
python -m src calcular --input exemplos/despesas-exemplo.json --output resultado.json

# console script instalado (usa política/câmbio empacotados em src/informacoes_externas/)
calcular --input exemplos/despesas-exemplo.json --output resultado.json

# input com moedas estrangeiras (converte via cambio.json; viagem por registro)
python -m src.cli calcular --input exemplos/despesas-envelope.json --output resultado.json

# apontando política/câmbio alternativos
python -m src.cli calcular --input in.json --output out.json --politica outra-politica.json --cambio outro-cambio.json
```

> `calcular` é obrigatório: `python -m src --input ...` (sem o subcomando) não vale mais.
> Não há mais `--em-viagem`: viagem é derivada por registro (moeda ≠ base, RN-009).

## Validação ponta a ponta (aceite)

### Golden 1 — `exemplos/despesas-exemplo.json` (`CC-ENG-PLATAFORMA`, sem `moeda`)

Todos os registros na base (sem `moeda`) → nenhum é viagem; a saída é a da Seção 4 da spec.

| O que conferir | Esperado |
|---|---|
| `total_reembolso_geral` | **`351.43`** |
| `alimentacao` | `total_despesas 402.83`, `total_aceito 306.93`, `total_reembolso 271.43` |
| `transporte_urbano` | `total_despesas 200.01` (exclui `d-009` −45,00, RN-014/D-004), `total_aceito 100.00`, `total_reembolso 80.00` |
| `hospedagem` | limite 0,00 → não reembolsável: `total_despesas 1170.00`, `total_aceito 0.00`, `total_reembolso 0.00`; `d-010`/`d-013` motivo `nao reembolsavel` |
| Reprovadas | `d-004` sem NF, `d-007` duplicado, `d-008` fora competência, `d-009` valor inválido; `d-005` coworking em `reprovadas_sem_categoria` |
| Sem `em_viagem` | a chave `em_viagem` **não** aparece na saída |

### Golden 2 — `exemplos/despesas-envelope.json` (`CC-COMERCIAL`, moedas EUR/USD/GBP)

Política `CC-COMERCIAL`: alimentacao 90 (dia), transporte_urbano 150 (dia), hospedagem 400 (diaria),
representacao 300 (dia); NF > 100; viagem +50%. Conversões usadas: EUR 07-14 = 5,93; EUR 07-15 = 5,88;
EUR 07-18 (sábado) → 07-17 = 5,96; USD 07-20 = 5,50; GBP inexistente.

| Registro | Cálculo | Resultado |
|---|---|---|
| `e-001` representacao BRL 340 (07-13) | base, não-viagem; min(340, 300) | aceito 340,00; reembolso 300,00 |
| `e-002` alimentacao EUR 22 (07-14) | 22×5,93 = 130,46; viagem (limite 135); NF ok | aceito 130,46; reembolso 130,46 |
| `e-003` alimentacao EUR 14,50 (07-15) | 14,50×5,88 = 85,26; 85,26 ≤ 100 → NF dispensada | aceito 85,26; reembolso 85,26 |
| `e-004` alimentacao EUR 30 (07-18 sáb) | 30×5,96 = 178,80; viagem (limite 135); min(178,80, 135) | aceito 178,80; reembolso 135,00 |
| `e-005` transporte USD 40 (07-20) | 40×5,50 = 220,00 > 100 e sem NF | recusado `sem nota fiscal obrigatória` |
| `e-006` representacao GBP 55 (07-21) | GBP ausente das taxas | recusado `cambio não identificado`; fora de `total_despesas` |
| `e-007` hospedagem BRL 1200 (07-22) | diaria; min(1200, 400) | aceito 1200,00; reembolso 400,00 |
| `e-008` alimentacao BRL 95 (07-23) | base; min(95, 90) | aceito 95,00; reembolso 90,00 |
| `e-009` coworking BRL 120 (07-24) | fora do conjunto do CC | recusado `categoria não aplicável` (sem_categoria) |
| `e-010` alimentacao BRL 88 (07-27) | sem `moeda` → base; min(88, 90) | aceito 88,00; reembolso 88,00 |

Totais esperados (cada despesa de alimentação está num dia distinto, então cada dia é seu próprio balde):

| Categoria | total_despesas | total_aceito | total_reembolso | reprovadas |
|---|---|---|---|---|
| `alimentacao` | 577.52 | 577.52 | **528.72** | — |
| `transporte_urbano` | 220.00 | 0.00 | 0.00 | `e-005` sem nota fiscal obrigatória |
| `hospedagem` | 1200.00 | 1200.00 | 400.00 | — |
| `representacao` | 340.00 | 340.00 | 300.00 | `e-006` cambio não identificado |
| `reprovadas_sem_categoria` | — | — | — | `e-009` categoria não aplicável (coworking) |

- `total_reembolso_geral` = 528,72 + 0 + 400,00 + 300,00 = **`1228.72`**.
- `alimentacao.total_reembolso` = 130,46 + 85,26 + 135,00 + 90,00 + 88,00 = 528,72.
- Ordem do bloco `categorias` (DT-011): alimentacao, transporte_urbano, hospedagem, representacao.
- Invariante `total_despesas ≥ total_aceito ≥ total_reembolso` vale em todas.

## Testes

```bash
pytest                              # tudo
pytest tests/test_regras.py         # 1 teste por RN (RN-001..RN-020)
pytest tests/test_cambio.py         # conversão, data mais próxima, empate, cambio não identificado
pytest tests/test_integracao.py     # goldens: exemplo (351.43) e envelope (1228.72)
pytest -k rn_018                    # foco numa regra
```

Convenção: cada teste cita o `RN-NNN` ou o caso de borda da Seção 7 no nome. `test_cobertura_rn`
garante que toda `RN-001..RN-020` tem cobertura.

## Cenários de erro (ver contrato da CLI)

| Cenário | Resultado |
|---|---|
| `--input`/`--politica`/`--cambio` inexistente ou JSON inparseável | mensagem em `stderr`, código `1`, nada escrito |
| Falta o subcomando `calcular`, ou falta `--input`/`--output` | erro de uso do `argparse`, código `2` |
| Registro de despesa malformado (ex.: `moeda` numérica) | `registro inválido`; os demais processados; código `0` |
| `moeda` sem taxa em todo o câmbio (ex.: GBP) | `cambio não identificado` **por registro**; código `0` |
