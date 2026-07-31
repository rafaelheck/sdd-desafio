# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 1.5 · **Baseado na spec:** 1.4 (Clarifications 2026-07-30 e 2026-07-31;
D-003..D-007). O plano 1.5 ajusta apenas a *forma de invocação* da CLI — `calcular`
passa a ser um **subcomando** do `argparse`, rodável por
`python -m src.cli calcular --input ... --output ...`, sem tocar em regra de negócio.
Substitui o plano 1.1, que assumia política embutida em código, categorias fixas e
viagem por flag de CLI.

> Aqui mora o COMO. Este arquivo pode e deve falar de linguagem, biblioteca e
> arquitetura. O que ele **não** pode é introduzir regra de negócio nova — se
> apareceu uma, ela pertence à `spec.md`.

**Constitution Check:** `.specify/memory/constitution.md` está no estado de template
(princípios não preenchidos). Não há gate de governança a violar. As convenções
efetivas vêm de `CLAUDE.md` (núcleo puro sem I/O; uma função por RN; um teste por RN;
`Decimal` sempre; regra de negócio só na spec) e são respeitadas por este plano. Se a
constituição for ratificada depois, reavaliar.

---

## 0. O que mudou desde o plano 1.1 (gap a fechar)

O código atual (`src/`) implementa a spec 1.0/1.1 e diverge da spec 1.4 em cinco frentes:

| Frente | Hoje no código | Exigido pela spec 1.4 |
|---|---|---|
| Política | `politica.py` com constantes fixas (`LIMITES_DIARIOS`, `CATEGORIAS_VALIDAS`, ...) | Ler `politica-v4.json`; categorias/limites/periodicidade por centro de custo, com `padrao` (RN-015/016/017); nenhuma categoria embutida (RN-001/004) |
| Categorias | trio fixo `alimentacao/transporte_urbano/hospedagem` (enum `Categoria`, `ORDEM_CATEGORIAS`) | conjunto **dinâmico** por CC; teto por **periodicidade**, não por nome (RN-002/003/004/016) |
| Viagem | flag de CLI `--em-viagem`, por input inteiro; campo `em_viagem` na saída | **por registro**, derivada da moeda (RN-009); sem `--em-viagem`; sem `em_viagem` na saída |
| Câmbio | inexistente | ler `cambio.json`; converter por data (RN-018/019); "cambio não identificado" (RN-020) |
| Nota fiscal | compara `valor` de entrada | compara **valor convertido** (RN-006, após conversão) |

Este plano redesenha as fronteiras para acomodar as duas fontes externas mantendo o
núcleo puro.

## 1. Stack

| Escolha | O quê | Por quê | Descartado |
|---|---|---|---|
| Linguagem | Python 3.13.x | Requisito; stdlib (`json`, `argparse`, `decimal`, `datetime`) cobre tudo sem dependências | — |
| Testes | `pytest` | Um teste por `RN-NNN` + tabela de bordas; auditoria de cobertura de RN | `unittest` (verboso) |
| Parsing/validação | stdlib `json` + `argparse`, validação manual | Zero dependências; mensagens de recusa explícitas | `pydantic` (esconderia a validação que é regra) |
| Dinheiro | `decimal.Decimal`, `quantize(0.01, ROUND_HALF_UP)`, JSON lido com `parse_float=Decimal` | RN-011; conversão de câmbio precisa de centavo exato | `float` (erro binário) |

> **Aritmética crítica:** valores e **taxas** de câmbio são lidos como `Decimal` (via
> `parse_float=Decimal`), nunca `float`. A conversão (RN-018/AMB-018) arredonda o valor
> de origem a 2 casas, multiplica pela **taxa cheia** e arredonda o resultado a 2 casas.

## 2. Arquitetura

Duas camadas: **núcleo puro** (regra de negócio, determinístico, sem I/O) e **casca de
I/O** (CLI, leitura de 3 arquivos JSON, serialização). As duas fontes externas
(`politica-v4.json`, `cambio.json`) são lidas na casca e **injetadas já parseadas** no
núcleo — o núcleo nunca abre arquivo.

```
python -m src.cli calcular --input despesas.json --output resultado.json
                           [--politica ...] [--cambio ...]
        │  (subcomando `calcular`; console script `calcular ...` chega aqui via wrapper)
        ▼
   cli.py (argparse + subparser `calcular`)  ── casca de I/O
        │
        ▼
   io_json.py  ── lê input, politica-v4.json e cambio.json (parse_float=Decimal);
        │         valida topo; ABORTA se input/política/câmbio ausentes ou inparseáveis
        │         (RN-013, RN-018); serializa a saída
        │  Entrada{despesas_brutas, colaborador, periodo} + Politica + Cambio
        ▼
   calculo.py (pipeline puro)                ── núcleo puro
        │  estrutura → normaliza → categoria → limite>0 → CONVERSÃO →
        │  dedup → período → valor → NF(convertido) → teto(baldes) → agrega
        ├── regras.py   (uma função por RN; gates, conversão, taxa, tetos, agregação)
        ├── politica.py (dict → Politica/Cambio; resolução de CC; constantes)
        └── modelo.py   (dataclasses + enums)
        │  Resultado (sem em_viagem)
        ▼
   io_json.py → resultado.json (2 casas, ensure_ascii=False, ordem determinística)
```

**Fronteiras:** `calculo.py`, `regras.py`, `politica.py`, `modelo.py` não importam I/O e
não conhecem caminhos de arquivo — recebem `Politica`/`Cambio` já construídos. Todo
contato com o mundo (abrir os 3 arquivos, `print`, exit code) mora em `cli.py`/`io_json.py`.

**Estrutura de pastas (inalterada; conteúdo dos módulos muda):**

```
src/
  __init__.py
  __main__.py     # python -m src calcular ... (dev; delega a cli.main)
  cli.py          # argparse c/ subcomando `calcular` (SEM --em-viagem); wrapper main_console; caminhos de política/câmbio; exit codes
  io_json.py      # ler_entrada / ler_politica / ler_cambio + serialização
  modelo.py       # dataclasses: Despesa, CategoriaConfig, Politica, Cambio, Reprovacao, ResultadoCategoria, Resultado; enum Motivo
  politica.py     # politica_de_dict / cambio_de_dict (dict→estrutura, puro); CASAS_DECIMAIS
  regras.py       # UMA FUNÇÃO POR RN (RN-001..RN-020)
  calculo.py      # pipeline puro na ordem da Seção 8
  informacoes_externas/
    politica-v4.json
    cambio.json
tests/
  test_regras.py       # 1 teste por RN (RN-001..RN-020)
  test_calculo.py      # dedup/ordem/tetos/baldes/agregação
  test_bordas.py       # casos da Seção 7
  test_cambio.py       # RN-018/019/020: conversão, data mais próxima, empate, não identificado
  test_politica.py     # RN-015: resolução de CC, padrão, conjunto dinâmico
  test_integracao.py   # goldens: despesas-exemplo.json e despesas-envelope.json
  test_cobertura_rn.py # auditoria: nenhuma RN sem teste
  test_cli.py          # flags, arquivos, exit codes, abort de câmbio
  test_io.py           # serialização (2 casas, acentos, ordem)
pyproject.toml
```

## 3. Modelo de dados

Detalhe em [`data-model.md`](./data-model.md). Mudanças-chave:

- **`Despesa`** ganha câmbio e viagem: `moeda_norm: str | None` (trim+upper; `None` =
  sem moeda), `valor_origem: Decimal` (2 casas, na moeda de origem), `valor_base:
  Decimal | None` (convertido; `None` até a conversão / se "cambio não identificado"),
  `em_viagem: bool`. A `categoria_norm` continua trim+lower.
- **`CategoriaConfig`**: `limite: Decimal`, `periodicidade: str` (`"dia"`/`"diaria"`),
  `observacao: str | None`.
- **`Politica`**: `padrao: dict[str, CategoriaConfig]`, `centros_custo: dict[str,
  dict[str, CategoriaConfig]]`, `limiar_nf: Decimal`, `acrescimo_viagem_pct: Decimal`.
- **`Cambio`**: `moeda_base: str` (normalizada), `taxas: dict[date, dict[str, Decimal]]`.
- **`Resultado`**: **remove** `em_viagem`; `categorias` é `dict[str, ResultadoCategoria]`
  na ordem determinística (Seção 5, DT-011).
- **`Motivo`**: acrescenta `CAMBIO_NAO_IDENTIFICADO = "cambio não identificado"`. O enum
  `Categoria` (trio fixo) é **removido** — não há mais categoria conhecida em código.

## 4. Como as fontes externas são representadas

Ambas viram estruturas puras construídas na casca e passadas ao núcleo:

- `io_json.ler_politica(caminho) -> Politica` e `io_json.ler_cambio(caminho) -> Cambio`
  abrem o arquivo (uma vez), leem com `parse_float=Decimal` e delegam a
  `politica.politica_de_dict` / `politica.cambio_de_dict` (puros: dict → dataclass).
- **Localização:** por padrão os arquivos empacotados em
  `src/informacoes_externas/{politica-v4.json,cambio.json}`, resolvidos relativos ao
  pacote; sobrescrevíveis por `--politica`/`--cambio` (contrato em
  [`contracts/cli-contract.md`](./contracts/cli-contract.md)).
- **Abort:** input, política ou câmbio ausente/inparseável → `ErroEntrada` → `stderr` +
  exit 1 (RN-013 para o input; RN-018 para o câmbio; mesma classe para a política).
- **`moeda_base`:** sempre a do `cambio.json`; a `moeda_base` de `politica-v4.json` é
  ignorada (RN-018).

## 5. Decisões técnicas

Mantidas de 1.1: **DT-001** (dinheiro em `Decimal` desde o JSON), **DT-002** (regra em
`regras.py`, uma função por RN), **DT-003** (CLI `argparse`; `calcular` agora como
**subcomando** — ver DT-003b), **DT-004** (pipeline explícito na ordem da Seção 8), **DT-005** (só stdlib no runtime),
**DT-006** (erro de topo aborta; registro malformado é recusa individual),
**DT-007** (`total_despesas` exclui `valor ≤ 0`). Novas/alteradas:

### DT-003b — CLI: subcomando `calcular`, wrapper de console, sem `--em-viagem`, caminhos opcionais
**Contexto:** viagem virou por-registro (RN-009); o motor precisa de dois arquivos externos;
e a execução deve ser possível sem instalar, por `python -m src.cli calcular ...`.
**Decisão:** `calcular` deixa de ser só o nome do console script e passa a ser um **subcomando**
do `argparse` em `cli.py` (`add_subparsers(dest="comando", required=True)`). O subcomando carrega
`--input`/`--output` (obrigatórios) e `--politica`/`--cambio` (opcionais, default: arquivos
empacotados); `--em-viagem` continua removido. Sem regra de negócio na CLI. As três formas de
execução são equivalentes e todas chamam `cli.main`:
- `python -m src.cli calcular --input ... --output ...` — alvo do pedido; roda sem instalar;
- `python -m src calcular --input ... --output ...` — `__main__.py` delega a `cli.main`;
- `calcular --input ... --output ...` — console script instalado, preservado por um **wrapper**
  `cli.main_console` que injeta o subcomando (`main(["calcular", *argv])`); a linha instalada
  continua com uma só palavra. `pyproject` aponta `calcular = "src.cli:main_console"`.
**Consequência:** a forma antiga `python -m src --input ...` (sem subcomando) deixa de valer — passa
a exigir `calcular`. `CLAUDE.md` (que cita `python -m src --input ...` e a assinatura `[--em-viagem]`)
fica desatualizado; sinalizar para atualizar. Contrato em [`contracts/cli-contract.md`](./contracts/cli-contract.md).

### DT-008 — Política e câmbio como dados injetados, não constantes
**Contexto:** RN-015/018 externalizam política e câmbio; o núcleo deve permanecer puro.
**Decisão:** `politica.py` deixa de ter constantes de limite; passa a converter dict→`Politica`/`Cambio`
e a resolver o centro de custo (`conjunto_do_centro(politica, cc)` → `padrao` se ausente, RN-015).
Toda leitura de arquivo fica em `io_json.py`.
**Alternativa descartada:** ler os arquivos dentro do núcleo — violaria a fronteira de I/O.
**Consequência:** troca de política/câmbio não exige recompilar regra; o núcleo é testável com
`Politica`/`Cambio` montados em memória.

### DT-009 — Teto dirigido por periodicidade, sobre conjunto dinâmico
**Contexto:** RN-002/003/004/016 — nenhuma categoria privilegiada; duas mecânicas.
**Decisão:** `regras.py` expõe `aplica_teto_dia(aceitas, limite, fator_por_registro)` (baldes por
status de viagem) e `aplica_teto_diaria(aceitas, limite)`; `calculo.py` escolhe pela
`periodicidade` da `CategoriaConfig`. Sem `ORDEM_CATEGORIAS` fixo nem `hospedagem` hardcoded.
**Consequência:** categoria nova na política é reembolsada sem tocar código (RN-004).

### DT-010 — Conversão de câmbio e resolução de taxa por data
**Contexto:** RN-018/019/AMB-017/018.
**Decisão:** `regras.taxa_por_data(cambio, moeda, data) -> Decimal | None` percorre as datas de
`taxas` que contêm a moeda, escolhe a de **menor distância** absoluta em dias e, em empate,
a **menor** taxa; devolve `None` se a moeda não existe em nenhuma data (→ RN-020).
`regras.converte(valor_origem, taxa)` faz `quantize(valor)·taxa` e `quantize` do resultado
(AMB-018). A `moeda` é normalizada trim+upper (Clarify 2026-07-31) antes de comparar com
`moeda_base` e com as chaves de `taxas`.
**Consequência:** determinístico; datas de fim de semana caem na cotação mais próxima.

### DT-011 — Ordem determinística das categorias na saída
**Contexto:** categorias agora são dinâmicas; a saída precisa ser determinística (Seção 9 da spec).
**Decisão:** o bloco `categorias` segue a **ordem das chaves do conjunto do centro de custo
resolvido** na política (ex.: `CC-ENG-PLATAFORMA` → alimentacao, transporte_urbano, hospedagem;
`CC-COMERCIAL` → alimentacao, transporte_urbano, hospedagem, representacao), emitindo só as que têm
≥1 despesa (AMB-015). `reprovadas_sem_categoria` segue a ordem do input.
**Alternativa descartada:** ordem de 1ª aparição no input — igual nos goldens atuais, mas acopla a
ordem da saída à ordem de digitação; a ordem da política é mais estável.

### DT-012 — Pipeline reordenado com passo de conversão
**Contexto:** Seção 8 da spec 1.4.
**Decisão:** ordem exata: estrutura(RN-013) → resolução política+câmbio(RN-015/018) →
normalização(RN-011/001, moeda+viagem) → categoria válida(RN-001) → limite>0(RN-017) →
**conversão(RN-018/019, falha→RN-020)** → dedup(RN-008, chave inclui moeda) → período(RN-007) →
valor>0(RN-010) → NF sobre valor convertido(RN-006) → teto(RN-002/003/004/005/009/016, baldes) →
agregação(RN-012/014). Conversão **antes** de dedup/período/valor/NF garante `valor_base` para
todo reprovado que compõe `total_despesas`; "cambio não identificado" não tem `valor_base` e é
excluído de `total_despesas` (AMB-017), como os `valor ≤ 0`.

## 6. Estratégia de testes

- **Nível:** unitário sobre `regras.py` (cada RN isolada) + `calculo.py`
  (dedup/ordem/tetos/baldes/agregação) + `test_cambio.py`/`test_politica.py` para as
  regras externas + integração ponta a ponta pela CLI. ≈70% unitário / 20% integração de
  núcleo / 10% CLII/IO.
- **Cobertura de RN:** `test_rn_001_*` … `test_rn_020_*`; `test_cobertura_rn` audita que
  nenhuma RN-NNN fica sem teste (RN-001..RN-020).
- **Bordas (Seção 7):** cada linha vira um teste em `test_bordas.py` (incl. moeda=base,
  sem moeda, dia misto/baldes, fim de semana, empate, cambio não identificado, NF pós-conversão).
- **Goldens (`test_integracao.py`):**
  - `exemplos/despesas-exemplo.json` (`CC-ENG-PLATAFORMA`, sem `moeda`) →
    `total_reembolso_geral == 351.43` (Seção 4 da spec; inalterado).
  - `exemplos/despesas-envelope.json` (`CC-COMERCIAL`, com EUR/USD/GBP) →
    `total_reembolso_geral == 1228.72` (valores completos em [`quickstart.md`](./quickstart.md)),
    exercitando conversão, baldes, "cambio não identificado" e NF sobre valor convertido.
  - Invariante `total_despesas ≥ total_aceito ≥ total_reembolso` em toda categoria.
- **Determinismo:** mesmo input+política+câmbio → mesma saída; ordem de categorias por DT-011.

## 7. Riscos

| Risco | Prob. | Mitigação |
|---|---|---|
| Ler valor **ou taxa** como `float` e perder centavo | Média | `parse_float=Decimal` em input/câmbio; teste de `d-011` (33,333) e de conversões do envelope |
| Arredondar na conversão em ordem errada (taxa arredondada, dupla) | Média | `converte()` isolada testada por RN-018/AMB-018; goldens do envelope pegam |
| Ordem não determinística das categorias dinâmicas quebra golden | Média | DT-011 (ordem da política); `test_io`/golden asseguram |
| Passo de conversão fora de posição quebra `total_despesas` ou motivo | Média | Ordem fixa DT-012; teste de precedência (cambio não id vs período/NF) |
| `moeda`/`categoria` não normalizadas recusam despesas legítimas | Média | normalização trim+upper/lower; testes de `" usd "`, `ALIMENTACAO` |
| Câmbio/política ausente tratado como recusa em vez de abort | Baixa | `ErroEntrada` + exit 1; `test_cli` cobre arquivo faltando |
| Stakeholder rejeita AMB-006/016/017 | Baixa/Média | Decisões em `DECISIONS.md`; trocas isoladas em `regras.py` |
| `CLAUDE.md` cita `--em-viagem` (agora removido) | Alta | Atualizar `CLAUDE.md` na implementação (DT-003b) |
