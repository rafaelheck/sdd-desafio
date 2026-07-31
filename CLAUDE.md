# CLAUDE.md

> Este arquivo é lido pelo Claude Code no início de toda sessão. É onde moram as
> convenções que você não quer repetir em todo prompt.
> Substitua os `<...>` e apague o que não usar. Mantenha curto — CLAUDE.md longo
> é CLAUDE.md ignorado.

## O projeto

Motor de cálculo de reembolso de despesas corporativas. CLI que lê um JSON de
despesas e emite um JSON com o valor reembolsável e a justificativa de cada item.

## Fonte da verdade

`specs/001-motor-reembolso/spec.md` define **o que** o sistema faz.
`specs/001-motor-reembolso/plan.md` define **como**.
`specs/001-motor-reembolso/tasks.md` define **em que ordem**.

Quando o código e a spec discordarem, a spec está certa e o código é o bug —
a menos que a spec esteja errada, e nesse caso corrigimos a spec primeiro e
registramos em `DECISIONS.md`.

**Antes de implementar qualquer coisa, leia a task correspondente em `tasks.md`.**
Se o que eu pedi não está coberto por nenhuma task, me avise em vez de implementar.

## Regras de trabalho

- Toda regra de negócio vive na spec, não no chat e não em comentário de código.
- Se eu te explicar uma regra que não está na spec, **pare e me diga isso** antes
  de escrever código. Isso é um bug de spec.
- Todo commit referencia uma task: `feat(T-003): <descrição>`.
  Mudanças de documentação: `docs(spec):`, `docs(plan):`, `docs(tasks):`.
- Nenhuma regra de negócio entra sem teste.

## Stack e comandos

- Linguagem: Python 3.13 (somente stdlib em runtime; sem dependências externas)
- Rodar: `calcular --input despesas.json --output resultado.json [--politica p.json] [--cambio c.json]`
  (em dev, sem instalar: `python -m src --input ... --output ...`). Sem `--politica`/`--cambio`,
  usa a política e o câmbio empacotados em `src/informacoes_externas/`. Não há mais `--em-viagem`:
  viagem é derivada por registro (moeda ≠ base, RN-009).
- Instalar (dev): `pip install -e ".[dev]"` (cria o comando `calcular` e instala `pytest`)
- Testes: `pytest`
- Lint/format: não há ferramenta configurada; siga PEP 8

## Convenções de código

- Núcleo puro (`calculo.py`, `regras.py`, `politica.py`, `modelo.py`) não faz I/O;
  toda leitura/escrita/exit code vive em `cli.py` e `io_json.py`.
- Uma função por regra em `src/regras.py`, documentada com o `RN-NNN`.
- Cada regra tem teste nomeado pelo `RN` (`test_rn_0NN_*`); um teste de auditoria
  garante que nenhuma RN fica sem cobertura.
- Valores monetários: `decimal.Decimal` sempre, com 2 casas via
  `quantize(Decimal("0.01"), ROUND_HALF_UP)`. O JSON é lido com
  `parse_float=Decimal` — valores nunca passam por `float`.

## Fora de escopo

- Sem estornos, créditos ou saldos negativos; reembolso é sempre ≥ 0.
- Não valida autenticidade de nota fiscal (confia em `tem_nota_fiscal`).
- Converte moeda via `cambio.json` (RN-018..RN-020); a `moeda_base` é a do câmbio e não se
  buscam cotações fora do arquivo. Sem regra de calendário (dia útil/feriado).
- Não persiste dados nem expõe interface além de ler um input e emitir um output.
