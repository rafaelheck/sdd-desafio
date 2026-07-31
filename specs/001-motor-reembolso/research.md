# Research — Motor de Cálculo de Reembolso

Fase 0 do plano. Não havia `NEEDS CLARIFICATION` em aberto (stack e CLI foram
fixados pelo usuário); este arquivo consolida as decisões técnicas e as
alternativas avaliadas.

## R-001 — Representação de dinheiro em Python

- **Decisão:** `decimal.Decimal` com `quantize(Decimal("0.01"), ROUND_HALF_UP)`.
  Ler o JSON com `json.load(f, parse_float=Decimal)` para que os valores nunca
  passem por `float`.
- **Rationale:** RN-011 pede 2 casas e half-up; `float` binário não representa
  `0.01` exatamente e produziria erros de centavo nas somas (o teste golden exige
  igualdade exata). `parse_float=Decimal` preserva a precisão original do texto
  (`33.333`) até o `quantize` controlado.
- **Alternativas consideradas:** inteiros em centavos (funciona, mas exige
  conversão manual em toda leitura/escrita e complica valores com >2 casas antes
  do arredondamento); `float` + `round()` (descartado — impreciso para dinheiro).

## R-002 — Parsing e validação sem framework

- **Decisão:** stdlib `json` para I/O e validação manual das regras em `regras.py`.
- **Rationale:** o usuário pediu funções de validação de regra separadas e
  explícitas; a spec exige mensagens de recusa com texto exato. Validação manual
  dá controle total sobre o motivo retornado e mantém a regra visível.
- **Alternativas consideradas:** `pydantic` (bom para validação estrutural, mas
  esconderia a lógica de regra de negócio e adicionaria dependência); `jsonschema`
  (cobre forma, não regra de negócio).

## R-003 — Interface de linha de comando

- **Decisão:** `argparse`, comando único `calcular` com `--input`, `--output`,
  `--em-viagem` (flag). Console script `calcular = src.cli:main` no `pyproject.toml`.
- **Rationale:** invocação exata definida pelo usuário; `argparse` é stdlib e
  suficiente para 3 argumentos; `store_true` mapeia `--em-viagem` direto para o
  booleano de contexto da RN-009.
- **Alternativas consideradas:** `click`/`typer` (dependência desnecessária).

## R-004 — Serialização determinística da saída

- **Decisão:** `json.dump(..., ensure_ascii=False, indent=2)` com um `default=`
  que converte `Decimal` em número de 2 casas; ordem de categorias e chaves fixa.
- **Rationale:** motivos contêm acentos ("não", "inválido"); a saída precisa ser
  byte-estável para o teste golden e legível para o usuário.
- **Alternativas consideradas:** `ensure_ascii=True` (escapa acentos, ilegível);
  ordenar chaves alfabeticamente (mudaria a ordem semântica da Seção 4).

## R-005 — Testes

- **Decisão:** `pytest` com parametrização; um teste por `RN-NNN` e por caso de
  borda da Seção 7; teste golden sobre o exemplo oficial.
- **Rationale:** rastreabilidade spec ↔ teste por nome; parametrização reduz
  boilerplate das tabelas de casos.
- **Alternativas consideradas:** `unittest` (mais verboso para tabelas).

## Itens herdados da spec (não são decisão técnica, são regra)

- Hospedagem por registro (AMB-006), `total_despesas` monetário (AMB-012),
  desempate de duplicata pela 1ª ocorrência (D-002) e tratamento de registro
  inválido (RN-013) já estão resolvidos na spec e apenas são implementados aqui.
