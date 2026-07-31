# Quickstart — Motor de Cálculo de Reembolso

Guia de execução e validação. Detalhes de regra estão na [`spec.md`](./spec.md),
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

```bash
# com o console script instalado
calcular --input exemplos/despesas-exemplo.json --output resultado.json

# ou, sem instalar, direto do repositório
python -m src --input exemplos/despesas-exemplo.json --output resultado.json

# marcando toda a competência como em viagem (limites +50%)
calcular --input exemplos/despesas-exemplo.json --output resultado.json --em-viagem
```

## Validação ponta a ponta (aceite)

Rodar sobre `exemplos/despesas-exemplo.json` **sem** `--em-viagem` deve produzir a
saída da Seção 4 da spec. Verificações-chave:

| O que conferir | Esperado |
|---|---|
| `total_reembolso_geral` | `585.00`? Não — **`585.43`** |
| `alimentacao` | `total_despesas 402.83`, `total_aceito 306.93`, `total_reembolso 255.43` |
| `transporte_urbano` | `total_despesas 155.01`, `total_aceito 100.00`, `total_reembolso 80.00` |
| `hospedagem` | `total_despesas 1170.00`, `total_aceito 480.00`, `total_reembolso 250.00` |
| Reprovadas | `d-004` sem NF, `d-007` duplicado, `d-008` fora competência, `d-009` valor inválido, `d-013` sem NF, `d-005` categoria não aplicável |
| Invariante | `total_despesas ≥ total_aceito ≥ total_reembolso` em toda categoria |
| Casas decimais | todo valor com 2 casas |
| Acentos | motivos legíveis ("não", "inválido"), sem escape |

## Testes

```bash
pytest                 # tudo
pytest tests/test_regras.py         # 1 teste por RN
pytest tests/test_integracao.py     # golden test do exemplo oficial
pytest -k rn_006                    # foco numa regra
```

Convenção: cada teste cita o `RN-NNN` ou o caso de borda da Seção 7 no nome,
fechando a rastreabilidade spec ↔ teste. Um teste de auditoria garante que toda
`RN-001..RN-014` tem cobertura.

## Cenários de erro (ver contrato da CLI)

| Cenário | Resultado |
|---|---|
| `--input` inexistente ou JSON de topo inválido | mensagem em `stderr`, código de saída `1`, nada escrito |
| Falta `--input` ou `--output` | erro de uso do `argparse`, código `2` |
| Um registro de despesa malformado | recusado como `registro inválido`; os demais processados; código `0` |
