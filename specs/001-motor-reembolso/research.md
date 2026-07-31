# Research — Motor de Cálculo de Reembolso

Fase 0 do plano (spec 1.4). Não há `NEEDS CLARIFICATION` em aberto: stack e CLI foram
fixados pelo usuário e as ambiguidades de negócio foram resolvidas na spec
(AMB-001..018) e no `/speckit-clarify` de 2026-07-31. Este arquivo consolida as decisões
técnicas e alternativas avaliadas. R-001..R-005 vêm do plano 1.1 (atualizadas onde a spec
mudou); R-006..R-011 cobrem política externa e câmbio.

## R-001 — Representação de dinheiro em Python

- **Decisão:** `decimal.Decimal` com `quantize(Decimal("0.01"), ROUND_HALF_UP)`; JSON lido
  com `json.load(f, parse_float=Decimal)`. Vale também para as **taxas** de `cambio.json`.
- **Rationale:** RN-011 pede 2 casas half-up; `float` não representa `0.01` e produziria erro
  de centavo nas somas e conversões (goldens exigem igualdade exata). `parse_float=Decimal`
  preserva a precisão do texto (`33.333`) até o `quantize` controlado.
- **Alternativas:** inteiros em centavos (conversão manual em toda leitura); `float`+`round()`
  (impreciso para dinheiro).

## R-002 — Parsing e validação sem framework

- **Decisão:** stdlib `json` para I/O e validação manual das regras em `regras.py`.
- **Rationale:** o usuário pediu funções de validação de regra separadas e explícitas; a spec
  exige mensagens de recusa com texto exato. Validação manual dá controle total sobre o motivo.
- **Alternativas:** `pydantic` (esconderia a regra, dependência); `jsonschema` (só forma).

## R-003 — Interface de linha de comando

- **Decisão:** `argparse`, comando único `calcular`; console script `calcular = src.cli:main`.
- **Atualização 1.4:** remove `--em-viagem` (viagem virou por-registro, RN-009); adiciona
  `--politica`/`--cambio` opcionais (default: arquivos empacotados em `src/informacoes_externas`).
  Ver R-009. `CLAUDE.md` (que ainda cita `--em-viagem`) precisa ser atualizado.
- **Alternativas:** `click`/`typer` — dependência desnecessária.

## R-004 — Serialização determinística da saída

- **Decisão:** `json.dumps(..., ensure_ascii=False, indent=2)` com `default=` que injeta
  `Decimal` como número de 2 casas; ordem de chaves fixa.
- **Rationale:** motivos contêm acentos ("não", "inválido", "cambio não identificado"); a saída
  precisa ser byte-estável para os goldens e legível.
- **Atualização 1.4:** a saída **não** tem mais `em_viagem`; a ordem do bloco `categorias` passa
  a ser dinâmica — ver R-011.

## R-005 — Testes

- **Decisão:** `pytest`; um teste por `RN-NNN` (agora RN-001..RN-020) e por caso de borda; dois
  goldens (exemplo e envelope). `test_cobertura_rn` audita a cobertura das 20 RNs.
- **Rationale:** rastreabilidade spec↔teste por nome; parametrização reduz boilerplate.
- **Alternativas:** `unittest` (mais verboso).

## R-006 — Política externa: onde parsear e como resolver o centro de custo

- **Decisão:** `io_json.ler_politica` abre o arquivo; `politica.politica_de_dict` converte
  dict→`Politica` (puro). A resolução do CC usa `centros_custo[cc]` se existir, senão `padrao`
  (RN-015). As categorias válidas são as **chaves** do CC resolvido (RN-001); limite/periodicidade/
  observacao vêm de cada `CategoriaConfig`. `nota_fiscal_obrigatoria_acima_de` e
  `acrescimo_em_viagem_percentual` são globais.
- **Rationale:** mantém o núcleo puro (I/O só na casca); RN-015/016/017 exigem dados, não código.
- **Alternativas:** constantes em `politica.py` (modelo 1.1) — viola RN-004/015.

## R-007 — Conversão de moeda para a base

- **Decisão:** registro sem `moeda` (ausente/`null`/vazio após `trim`) ou com `moeda` = `moeda_base`
  do **`cambio.json`**: sem conversão, não é viagem. Moeda diferente da base: `valor_base =
  round2(round2(valor_origem) × taxa)` (AMB-018). A `moeda` é normalizada trim+upper antes de
  comparar com `moeda_base` e com as chaves de `taxas` (Clarify 2026-07-31). A `moeda_base` de
  `politica-v4.json` é ignorada.
- **Rationale:** RN-018; arredondar origem e resultado (não a taxa) preserva centavo.
- **Alternativas:** arredondar a taxa/só o resultado — divergem do centavo esperado.

## R-008 — Resolução da taxa por data (mais próxima, empate → menor)

- **Decisão:** entre as datas de `taxas` que **contêm a moeda**, escolher a de menor
  `abs(data_taxa − data_registro)` em dias; em empate, a **menor** taxa. Busca irrestrita.
  `None` se a moeda não existe em nenhuma data → RN-020.
- **Rationale:** RN-019/AMB-017; cotações só em dias úteis; menor taxa no empate é conservadora.
- **Validação (envelope):** EUR em 2026-07-18 (sábado) → 07-17 (dist. 1, 5,96) vence 07-20 (dist. 2).
- **Alternativas:** interpolar (inventaria cotação); exigir data exata (não pedido).

## R-009 — Carregamento e falha das fontes externas

- **Decisão:** `input`, `politica-v4.json` e `cambio.json` lidos na casca com `parse_float=Decimal`;
  ausência ou JSON inparseável de qualquer um → `ErroEntrada` → `stderr` + exit 1 (abort).
  Distingue-se de "cambio não identificado" (recusa por registro com arquivo presente, RN-020).
- **Rationale:** RN-013 (input) e RN-018/Clarify (câmbio); sem `moeda_base` nada é valorável.
  Não há validação de consistência do conteúdo (assume-se bem formado — Seção 10).
- **Alternativas:** degradação parcial sem câmbio — rejeitada no Clarify (abort).

## R-010 — "cambio não identificado": reporte e efeito no total

- **Decisão:** moeda ausente de todas as `taxas` → "cambio não identificado", reembolso 0; sob a
  própria categoria se válida; **excluído de `total_despesas`** (sem valor em base). Categoria não
  aplicável prevalece (avaliada antes, DT-012).
- **Rationale:** RN-020/AMB-017; preserva `total_despesas ≥ total_aceito`.
- **Validação (envelope):** `e-006` GBP → sob `representacao`, fora de `total_despesas`.

## R-011 — Ordem determinística das categorias dinâmicas

- **Decisão:** `categorias` segue a ordem das chaves do conjunto do CC resolvido, só as com ≥1
  despesa (AMB-015); `reprovadas_sem_categoria` na ordem do input.
- **Rationale:** determinismo (Seção 9) sem depender da ordem de digitação; reflete a política.
- **Validação:** `CC-ENG-PLATAFORMA` → alimentacao, transporte_urbano, hospedagem (golden 1);
  `CC-COMERCIAL` → alimentacao, transporte_urbano, hospedagem, representacao (golden 2).
- **Alternativas:** 1ª aparição no input (equivalente nos goldens, menos estável); alfabética.

## Itens herdados da spec (regra, não decisão técnica)

- Hospedagem/"diaria" por registro (AMB-006), `total_despesas` monetário (AMB-012) com exclusão de
  `valor ≤ 0` por valor (RN-014/D-004), desempate de duplicata pela 1ª ocorrência (D-002), registro
  inválido (RN-013), teto por papel/periodicidade (D-006) e viagem por moeda/baldes (D-007) já estão
  resolvidos na spec e apenas são implementados aqui.
