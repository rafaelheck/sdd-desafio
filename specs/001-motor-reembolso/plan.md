# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.1 · **Baseado na spec:** 1.1 (inclui Clarifications 2026-07-30, D-003 e D-004)

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

**Constitution Check:** `.specify/memory/constitution.md` está no estado de
template (sem princípios preenchidos). Não há gate de governança a violar; se a
constituição for ratificada depois, este plano deve ser reavaliado.

---

## 1. Stack

| Escolha | O quê | Por quê | O que descartei e por quê |
|---|---|---|---|
| Linguagem | Python 3.13.x | Requisito do usuário; stdlib rica (`json`, `argparse`, `decimal`, `datetime`) cobre tudo sem dependências | — |
| Testes | `pytest` | Parametrização ergonômica para mapear um teste por `RN-NNN` e por caso de borda | `unittest` — mais verboso para tabelas de casos |
| Parsing/validação | stdlib `json` + `argparse`, validação manual em módulo próprio | Zero dependências de runtime; controle explícito das mensagens de recusa (a spec exige motivos textuais precisos) | `pydantic` — esconderia a validação de regra que o usuário pediu para deixar explícita e separada |
| Aritmética monetária | `decimal.Decimal`, `quantize(0.01, ROUND_HALF_UP)` | Dinheiro não pode usar ponto flutuante binário; `ROUND_HALF_UP` é exatamente a RN-011 | `float` — erro de arredondamento previsível; descartado |

> **Detalhe crítico de aritmética:** os valores monetários são lidos do JSON já
> como `Decimal` (via `json.load(..., parse_float=Decimal)`), **nunca** como
> `float`. Isso evita que `33.333` vire `33.33299999…` antes do `quantize`.

## 2. Arquitetura

Duas camadas: um **núcleo puro** de regra de negócio (sem I/O, determinístico) e
uma **casca de I/O** (CLI, leitura/escrita de arquivo, serialização).

```
calcular --input --output [--em-viagem]
        │
        ▼
   cli.py (argparse)                 ── casca de I/O
        │
        ▼
   io_json.py  ── lê JSON (parse_float=Decimal), valida estrutura, serializa saída
        │  Despesa[] + contexto
        ▼
   calculo.py (pipeline)             ── núcleo puro
        │  normaliza → deduplica → aplica gates → aplica tetos → agrega
        ├── regras.py   (uma função por RN: gates de validação + tetos + total_despesas)
        ├── politica.py (constantes: limites, limiar NF, multiplicador viagem)
        └── modelo.py   (dataclasses + enums)
        │  Resultado
        ▼
   io_json.py → resultado.json
```

**Fronteiras:** `calculo.py` + `regras.py` + `politica.py` + `modelo.py` não
importam nada de I/O e não conhecem arquivos nem `argparse` — recebem estruturas
e devolvem estruturas. Todo contato com o mundo (ler arquivo, `print`, exit code)
mora em `cli.py` e `io_json.py`. Essa linha é o que faz as ~14 regras testáveis
sem tocar em disco e resistentes a troca de formato de entrada.

**Estrutura de pastas:**

```
src/
  __init__.py
  __main__.py     # python -m src ... (dev)
  cli.py          # argparse, main() → comando `calcular`; exit codes
  io_json.py      # leitura (parse_float=Decimal) + validação estrutural + serialização (ensure_ascii=False)
  modelo.py       # dataclasses: Despesa, Reprovacao, ResultadoCategoria, Resultado; enums Categoria, Motivo
  politica.py     # constantes de política (Seção 4)
  regras.py       # FUNÇÕES DE REGRA DE NEGÓCIO — arquivo próprio (requisito do usuário)
  calculo.py      # pipeline puro que orquestra regras.py
tests/
  test_regras.py       # 1 teste por RN
  test_calculo.py      # tetos, agregação, dedup, ordem
  test_bordas.py       # casos da Seção 7 da spec
  test_integracao.py   # golden: exemplos/despesas-exemplo.json → saída da Seção 4
  test_cli.py          # flags, arquivos, --em-viagem, exit codes
pyproject.toml         # metadados + console_script `calcular` + config do pytest
```

## 3. Modelo de dados

Detalhe completo em [`data-model.md`](./data-model.md). Resumo:

- **`Despesa`** (entrada normalizada): `id`, `data: date`, `categoria: str`,
  `categoria_norm: str` (trim + lower), `descricao`, `fornecedor`,
  `valor: Decimal` (já em 2 casas), `tem_nota_fiscal: bool`.
- **`Reprovacao`**: `id`, `motivo: Motivo`, e opcional `categoria_informada`
  (usado só em `reprovadas_sem_categoria`).
- **`ResultadoCategoria`**: `total_despesas`, `total_aceito`, `total_reembolso`
  (todos `Decimal`), `reprovadas: list[Reprovacao]`.
- **`Resultado`**: `colaborador`, `competencia`, `periodo`, `em_viagem`,
  `categorias: dict[str, ResultadoCategoria]`, `reprovadas_sem_categoria`,
  `total_reembolso_geral`.
- **`Motivo`** (enum, texto exato da spec): `categoria não aplicável`,
  `data fora da competência`, `registro duplicado`, `sem nota fiscal obrigatória`,
  `valor inválido`, `registro inválido`.

A justificativa da recusa é carregada pelo próprio `Motivo` na `Reprovacao`; uma
despesa aceita não gera `Reprovacao` e contribui para os três totais.

## 4. Como a política é representada

Os limites vivem como **constantes nomeadas** em `src/politica.py`, não em arquivo
de configuração externo:

```
LIMITES_DIARIOS        = {"alimentacao": Decimal("60"), "transporte_urbano": Decimal("80")}
LIMITE_HOSPEDAGEM      = Decimal("250")   # por registro (RN-004 / AMB-006)
LIMIAR_NOTA_FISCAL     = Decimal("100")   # NF exigida se valor > este limiar (RN-006)
MULTIPLICADOR_VIAGEM   = Decimal("1.5")   # aplica-se só aos tetos (RN-009)
CATEGORIAS_VALIDAS     = {"alimentacao", "transporte_urbano", "hospedagem"}
CASAS_DECIMAIS         = Decimal("0.01")
```

**Por quê constantes e não config externa:** a política muda raramente, é versionada
junto do código e cada valor é parte da regra testada. Um módulo único dá um ponto
de mudança sem overhead de I/O ou de validar um arquivo de config. **Trade-off:**
mudar a política exige alterar o código e re-deploy — aceitável para uma política
que muda em ciclos de meses (é "v3"). Se um dia a política precisar mudar sem
deploy, este é o único ponto a externalizar.

## 5. Decisões técnicas

### DT-001 — Dinheiro em `Decimal`, lido como `Decimal` desde o JSON
**Contexto:** RN-011 exige 2 casas e arredondamento half-up; há valor com 3 casas (`33.333`) e somas que precisam bater centavo a centavo no teste golden.
**Decisão:** todo valor é `Decimal`. O JSON é lido com `parse_float=Decimal`; cada valor recebe `quantize(CASAS_DECIMAIS, ROUND_HALF_UP)` na normalização; a saída é serializada com 2 casas.
**Alternativa descartada:** `float` — erro de ponto flutuante em dinheiro; e `Decimal(str(float))` depois de já ter perdido precisão.
**Consequência:** fácil: aritmética exata e testes determinísticos. Difícil: é preciso um encoder JSON que saiba serializar `Decimal` com 2 casas.

### DT-002 — Regras de negócio isoladas em `regras.py`, como funções puras
**Contexto:** requisito do usuário — funções de validação de regra separadas, bem declaradas, em arquivo próprio.
**Decisão:** `regras.py` concentra uma função por regra, nomeada e documentada com o `RN-NNN`: gates de validação com assinatura `def valida_<x>(despesa, contexto) -> Reprovacao | None` (retornam o motivo ou `None` se passa) e as funções de cálculo de teto/`total_despesas`. `calculo.py` só orquestra.
**Alternativa descartada:** regras espalhadas dentro do pipeline em `calculo.py` — dificultaria o mapeamento 1:1 com a spec e a rastreabilidade nos testes.
**Consequência:** fácil: cada RN vira um teste unitário direto; a spec e o código ficam rastreáveis. Difícil: exige disciplina para não vazar regra para `calculo.py`.

### DT-003 — CLI com `argparse`, comando único `calcular`
**Contexto:** invocação fixada pelo usuário: `calcular --input despesas.json --output resultado.json [--em-viagem]`.
**Decisão:** `argparse` com `--input` (obrigatório), `--output` (obrigatório) e `--em-viagem` (flag booleana `store_true`, default `False`). Exposto como `console_scripts` (`calcular = src.cli:main`) no `pyproject.toml`; em dev, `python -m src ...`. Contrato completo em [`contracts/cli-contract.md`](./contracts/cli-contract.md).
**Alternativa descartada:** `click`/`typer` — dependência externa desnecessária para 3 argumentos.
**Consequência:** fácil: sem dependências; `--em-viagem` mapeia direto para RN-009. Difícil: `argparse` dá menos açúcar para subcomandos futuros (não é necessário agora).

### DT-004 — Pipeline explícito seguindo a ordem da Seção 8 da spec
**Contexto:** RN/AMB-010 fixam a ordem de aplicação e o "primeiro gate que falha define o motivo".
**Decisão:** `calculo.py` executa os passos na ordem exata da Seção 8: validação estrutural → normalização → deduplicação (mantém 1ª ocorrência) → gates (categoria → período → valor → NF) → tetos → agregação. Cada despesa aceita entra em `total_aceito`/`total_despesas`; cada recusa registra o motivo do primeiro gate.
**Alternativa descartada:** avaliar todos os gates e escolher motivo por prioridade — mais código e mesmo resultado.
**Consequência:** fácil: determinístico e auditável, espelha a spec. Difícil: a ordem é acoplada à spec — mudou a spec, muda o pipeline (correto).

### DT-005 — Sem dependências de runtime (stdlib apenas)
**Contexto:** o problema é resolvível 100% com a biblioteca padrão.
**Decisão:** runtime usa só stdlib; `pytest` é dependência apenas de desenvolvimento.
**Consequência:** fácil: instalação e reprodução triviais. Difícil: nenhuma relevante.

### DT-006 — Tratamento de erro e códigos de saída
**Contexto:** RN-013 — registro malformado é recusado individualmente; JSON de topo inválido aborta.
**Decisão:** registro malformado vira `Reprovacao("registro inválido")` em `reprovadas_sem_categoria`. Erros de topo (JSON inparseável, arquivo de entrada inexistente, campos de topo ausentes) escrevem mensagem em `stderr` e saem com código ≠ 0 (sucesso = 0). Códigos detalhados no contrato da CLI.
**Consequência:** fácil: lote resiliente + falha clara para erro irrecuperável. Difícil: exige distinguir erro estrutural de registro vs. erro de topo.

### DT-007 — `total_despesas` exclui valores ≤ 0 (exclusão por valor)
**Contexto:** RN-014 revista em D-004 — `total_despesas` soma o `valor` das despesas de categoria válida (aceitas + reprovadas), **exceto** as com `valor ≤ 0`; a exclusão é **por valor, não pelo motivo da recusa** (Clarifications 2026-07-30, opção A).
**Decisão:** a função de agregação em `regras.py` que compõe `total_despesas` filtra `despesa.valor > 0` antes de acumular, independentemente de a despesa ter sido aceita ou recusada e de qual gate a recusou (duplicidade/período/NF/valor). Como a normalização arredonda antes (RN-011), o teste `> 0` usa o `Decimal` já `quantize`ado.
**Alternativa descartada:** excluir apenas as recusadas com motivo "valor inválido" (exclusão por motivo) — diverge da opção A para o caso raro de uma despesa negativa recusada antes do gate de valor (ex.: duplicata negativa).
**Consequência:** no exemplo, `transporte_urbano.total_despesas` passa de 155,01 para **200,01** (o estorno `d-009`, −45,00, sai da somatória; segue recusado como "valor inválido" e listado em `reprovadas`). A invariante `total_despesas ≥ total_aceito ≥ total_reembolso` continua válida (fica mais folgada).

## 6. Estratégia de testes

- **Nível:** predominantemente unitário sobre `regras.py` (cada RN isolada), mais
  testes de `calculo.py` (dedup/ordem/tetos/agregação) e um punhado de integração
  ponta a ponta pela CLI. Proporção alvo ≈ 75% unitário / 15% integração de núcleo
  / 10% CLI.
- **Cada `RN-NNN` tem teste?** Sim, por convenção de nome: `test_rn_001_*`,
  `test_rn_002_*`, … `test_rn_014_*` em `test_regras.py`/`test_calculo.py`. Um
  teste de auditoria (`test_cobertura_rn`) garante que não falta RN.
- **Casos de borda da Seção 7:** cada linha da tabela vira um teste em
  `test_bordas.py`, nomeado pelo `id` do exemplo (`test_borda_d004_sem_nf`, …).
- **Golden test:** `test_integracao.py` roda `exemplos/despesas-exemplo.json` (com
  e sem `--em-viagem`) e compara com a saída da Seção 4 da spec, incluindo a
  invariante `total_despesas ≥ total_aceito ≥ total_reembolso` e
  `total_reembolso_geral == 585.43`.
- **Nomenclatura:** o nome do teste cita o `RN`/caso de borda, fechando a
  rastreabilidade spec ↔ teste ↔ correção. Ver [`quickstart.md`](./quickstart.md).

## 7. Riscos

| Risco | Probabilidade | O que faço se acontecer |
|---|---|---|
| Ler valor como `float` antes de `Decimal` e perder precisão (`33.333`) | Média | `parse_float=Decimal` na leitura + teste específico de `d-011`; lint proibindo `float(` em valores |
| Serializar `Decimal` quebra `json.dumps` | Alta (se esquecido) | Encoder custom/`default=` convertendo `Decimal`→número com 2 casas; teste golden pega |
| Acentos nos motivos ("não", "inválido") saem escapados | Média | `json.dump(..., ensure_ascii=False)` + arquivo UTF-8; asserção no teste de integração |
| Ordem de chaves/categorias não determinística quebra golden | Baixa | Ordem fixa de categorias e de chaves na serialização |
| Stakeholder rejeita AMB-006 (hospedagem por registro ≠ "por diária" do RH) | Média | Decisão registrada em `DECISIONS.md`; troca isolada em `politica.py`/`regras.py` |
| AMB-012 (`total_despesas` monetário vs. contagem) estar errada | Baixa/Média | Confirmar com usuário; troca isolada em `regras.py` + `data-model.md` |
| `--em-viagem` interpretado por despesa em vez de por input | Baixa | RN-009 é por input inteiro; um único booleano de contexto no pipeline; teste de CLI |
