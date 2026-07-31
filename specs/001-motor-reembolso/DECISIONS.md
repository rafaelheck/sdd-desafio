# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-007 — Conversão de câmbio (`cambio.json`) e viagem por moeda · `2026-07-31`

**Gatilho:** pedido do usuário via `/speckit-specify`: despesas podem vir em moeda
estrangeira e devem ser convertidas para a moeda base por uma tabela de câmbio externa
(`src/informacoes_externas/cambio.json`); e a condição de "em viagem" deixa de ser um
input e passa a ser derivada **por registro** (moeda ≠ base).

**O que mudou na spec (versão 1.3 → 1.4):**
- **Novas RN-018/019/020:** conversão para a base (RN-018), resolução da taxa por data
  com data mais próxima e desempate pela menor taxa (RN-019), e recusa
  "cambio não identificado" para moeda ausente de todas as `taxas` (RN-020). O conjunto
  passou de 17 para **20 regras**.
- **RN-009 reescrita:** viagem é **por registro** (moeda ≠ `moeda_base` do câmbio); some
  o `em_viagem` de input; o acréscimo incide sobre o valor já convertido; a `moeda_base`
  de referência é a do `cambio.json` (a da política é ignorada).
- **RN-006:** o limiar de NF é comparado contra o **valor convertido** (NF após conversão).
- **RN-008:** a chave de duplicidade inclui a `moeda` de origem.
- **RN-011:** arredondamento da conversão (origem → ×taxa → resultado, half-up).
- **RN-002:** dia misto viagem/não-viagem usa **baldes separados**.
- **Seção 4:** nova coluna `despesas[].moeda` (opcional), remoção do `em_viagem` de
  input e de saída, nova tabela do `cambio.json`, totais declarados em moeda base, e
  nota de conversão para o `despesas-envelope.json`.
- **Seção 8:** novo passo 6 "Conversão de câmbio" (após validade da categoria/limite,
  antes de duplicata/período/valor/NF), NF passa a usar o valor convertido, teto com
  limite amplificado por registro e baldes no "dia".
- **Novas AMB-016/017/018** e **AMB-008 marcada como substituída** (viagem por moeda).
- **Seção 9:** critérios de câmbio, viagem por registro, baldes e "cambio não
  identificado"; motivo novo na lista; contagem 17 → 20. **Seção 10:** câmbio sai de
  "em aberto" (agora implementado por `cambio.json`), resta a não-validação do arquivo.

**Decisões tomadas com o usuário (Clarifications Session 2026-07-31 — câmbio e viagem):**
- **AMB-016** — dia "dia" misto → **baldes separados**; saída **remove** `em_viagem`.
- **AMB-017** — "cambio não identificado" fica **sob a categoria** (se válida) e é
  **excluído de `total_despesas`**; busca de data mais próxima irrestrita, empate → menor.
- **AMB-018** — arredonda origem (2c) → × taxa cheia → arredonda resultado (2c).

**Contexto do envelope:** o `despesas-envelope.json` (CC-COMERCIAL) foi usado para
validar: `e-006` GBP não está em nenhuma `taxas` (→ "cambio não identificado"); `e-004`
EUR num sábado (→ data mais próxima 07-17); `e-010` sem `moeda` (→ base, não viagem).
O arquivo **não** contém dia+categoria com moedas mistas, então o teto de dia misto é
uma regra de robustez (não exercitada pelos goldens atuais).

**O que isso invalida na implementação:** `io_json.py`/`cli.py` não leem `cambio.json`
nem aceitam `moeda`; `regras.py`/`politica.py` não convertem, tratam viagem como flag de
input e não têm gate de câmbio; a saída ainda emite `em_viagem`. Tudo isso precisa ser
refeito via `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`. **Este passo
alterou apenas `spec.md`, `checklists/requirements.md` e este log.**

**Tasks afetadas:** leitura/validação do `cambio.json`; parsing do campo `moeda`; gate de
conversão e "cambio não identificado" na ordem nova; NF sobre valor convertido; viagem e
teto por registro com baldes; remoção de `em_viagem` do contrato de saída; golden do
`despesas-envelope.json` calculado no plano/quickstart.

**Custo:** 3 arquivos (`spec.md`, `checklists/requirements.md`, `DECISIONS.md`); na spec,
~20 blocos (3 RNs novas, 5 RNs reescritas, 3 AMBs novas + 1 substituída, Seções 2/3/4/7/8/9/10
e o exemplo).

---

## D-006 — Regras de teto agnósticas de categoria (RN-002/003/004 por papel) · `2026-07-31`

**Gatilho:** pedido do usuário via `/speckit-specify`: o sistema não deve conhecer
nem citar categorias específicas (`alimentacao`, `transporte_urbano`, `hospedagem`).
Todas as categorias, limites e periodicidades devem sair de `politica-v4.json`, e o
motor deve funcionar sem alteração diante de mudanças na política (limite/periodicidade
alterados, categorias novas ou removidas).

**Decisão de estrutura (escolhida com o usuário):** manter os três IDs RN-002/003/004
(mínimo impacto em `tasks.md` e nos testes nomeados por RN), reescrevendo cada um por
**papel**, sem nome de categoria:
- **RN-002 — Teto de periodicidade "dia"**: `min(soma_do_dia, limite)` para qualquer
  categoria cuja `periodicidade` seja "dia". Absorve o antigo teto de transporte.
- **RN-003 — Teto de periodicidade "diaria"**: `min(valor, limite)` por registro para
  qualquer categoria "diaria". Deixa de ser "teto de transporte" e passa a ser a
  mecânica por registro (antes só em RN-004/hospedagem).
- **RN-004 — Origem do teto**: o `limite` vem de `politica[<CC>][<categoria>].limite`
  (RN-015); nenhuma categoria tem limite embutido no código. Deixa de ser "teto de
  hospedagem".

**O que mudou na spec (versão 1.2 → 1.3):**
- **RN-002/003/004** reescritas por papel (acima); nenhuma cita categoria como regra —
  só como exemplo do que a política vigente traz.
- **RN-016** reposicionada como **classificação**: o valor de `periodicidade` seleciona
  a mecânica (RN-002 ou RN-003) sem o sistema conhecer o nome da categoria.
- **AMB-001** (agregação diária) → afeta RN-002 (não mais RN-003); **AMB-006**
  (hospedagem por registro) → afeta RN-003/RN-004.
- Seção 7 (bordas): linhas de teto reescritas por periodicidade; Seção 8 (passo 10)
  descreve limite via RN-004 + mecânica via RN-016 (RN-002/RN-003).
- Seção 9 (aceite): novo critério de que nenhuma categoria é conhecida/privilegiada e
  que adicionar/remover/alterar categoria na política muda o resultado sem tocar código.
- Clarifications: nova entrada Session 2026-07-31 registrando a generalização.

**Por quê:** a v1.2 externalizou a política (RN-015/016/017), mas RN-002/003/004 ainda
enunciavam categorias fixas — uma inconsistência com o objetivo de política dirigir tudo.
Generalizar por papel remove o último acoplamento de regra a categoria.

**O que isso invalida na implementação:** `politica.py` e `regras.py` ainda embutem
`CATEGORIAS_VALIDAS`, `LIMITES_DIARIOS`, `LIMITE_HOSPEDAGEM`, `ORDEM_CATEGORIAS` e
funções separadas `aplica_teto_diario`/`aplica_teto_hospedagem`, e **não leem**
`politica-v4.json`. Tudo isso precisa passar a derivar da política (limite/periodicidade
por categoria do CC resolvido) via `/speckit-plan` → `/speckit-tasks` →
`/speckit-implement`. **Este passo alterou apenas `spec.md`, `checklists/requirements.md`
e este log.**

**Tasks afetadas:** teto passa a ser dirigido por `periodicidade` da política (uma
mecânica "dia", uma "diaria") sobre um conjunto **dinâmico** de categorias; testes
`test_rn_002/003/004` re-expressos por papel, não por categoria; agregação/ordem de
categorias na saída derivada da política, não de `ORDEM_CATEGORIAS` fixo.

**Custo:** 3 arquivos (`spec.md`, `checklists/requirements.md`, `DECISIONS.md`); na
spec, ~9 blocos (RN-002/003/004, RN-016, AMB-001, AMB-006, Seções 7/8/9, Clarifications).

---

## D-005 — Política externa por centro de custo (`politica-v4.json`) · `2026-07-31`

**Gatilho:** pedido do usuário via `/speckit-specify`: as categorias, limites e o
tratamento de viagem/nota fiscal deixam de ser fixos e passam a ser lidos de um
arquivo externo (`src/informacoes_externas/politica-v4.json`), podendo variar por
**centro de custo**.

**O que mudou na spec (versão 1.1 → 1.2):**
- **Nova RN-015 — Política externa e resolução de centro de custo**: categorias,
  limites, periodicidade, limiar de NF e acréscimo de viagem vêm do arquivo; se o
  `centro_custo` do input não existe em `centros_custo`, usa-se o objeto `padrao`.
- **Nova RN-016 — Periodicidade do limite**: `"dia"` (limite sobre a soma da
  categoria por dia civil) vs `"diaria"` (limite por registro). Generaliza o
  mecanismo antes embutido em RN-002/003 (dia) e RN-004 (registro).
- **Nova RN-017 — Categoria com limite ≤ 0 (não reembolsável)**: recusa toda
  despesa da categoria com `motivo` = `observacao` (ou "categoria não aplicável"
  se ausente), reembolso 0, reportada **sob a própria categoria**.
- **RN-001** reescrita: categorias válidas = chaves do conjunto do centro de custo
  resolvido (não mais um trio fixo `alimentacao`/`transporte_urbano`/`hospedagem`).
- **RN-002/003/004** reescritas: o teto agora é o `limite` da política do centro
  de custo (o `padrao` mantém 60/80/250); cada uma referencia sua periodicidade.
- **RN-006** (limiar de NF) e **RN-009** (acréscimo de viagem) passam a ler
  `nota_fiscal_obrigatoria_acima_de` e `acrescimo_em_viagem_percentual` do arquivo.
- Seção 2 (Objetivo), Seção 3 (Fora de escopo), Seção 4 (nova tabela da política
  externa + tabela de saída ajustada) e Seção 8 (ordem de aplicação: novo passo 2
  "Resolução da política" e passo 5 "Limite da categoria > 0", renumerando os
  demais) atualizadas.
- Seção 7 (casos de borda): novas linhas para limite ≤ 0, categoria só-em-alguns-
  centros e centro de custo desconhecido.
- Seção 9 (critérios de aceite): contagem de regras 14 → **17** (RN-001..RN-017) e
  novos critérios para política externa, limite ≤ 0 e viagem parametrizada.
- **Exemplo da Seção 4 recalculado** para `CC-ENG-PLATAFORMA` (alimentação limite
  **75**, hospedagem limite **0**): `alimentacao.total_reembolso` 255,43 → **271,43**
  (07-03 vai a 75, 07-31 a 61); `hospedagem` fica não reembolsável (aceito/reembolso
  0, `d-010`/`d-013` → "nao reembolsavel"); **`total_reembolso_geral` 585,43 → 351,43**.

**Três ambiguidades resolvidas com o usuário (Clarifications Session 2026-07-31):**
- **AMB-013** — centro de custo ausente na política → fallback para `padrao`.
- **AMB-014** — despesa de categoria com limite ≤ 0: (a) reportada **sob a própria
  categoria** e (b) esse motivo **prevalece** — a aplicabilidade da categoria
  (existência + limite > 0) é avaliada **antes** de duplicata/período/valor/NF.
- **AMB-015** — o bloco `categorias` lista **apenas** categorias válidas do centro
  **com ao menos uma despesa** no input (sem blocos zerados).

**Por quê:** tirar a política de dentro do código torna limites e categorias
configuráveis por RH sem alterar o motor, e o modelo por centro de custo reflete
que times diferentes têm tetos e categorias diferentes (ex.: `representacao` só em
`CC-COMERCIAL`; hospedagem bloqueada em `CC-ENG-PLATAFORMA`).

**O que isso invalidou:** o pressuposto (D-003/D-004 e anteriores) de três
categorias fixas com limites 60/80/250 embutidos — agora esses são apenas os
valores do objeto `padrao`. O exemplo de saída anterior (`total_reembolso_geral`
585,43) foi substituído. RN-002/003/004 deixam de citar valores literais como
regra e passam a apontar para a política.

**O que isso invalida na implementação:** `politica.py`/`regras.py` têm categorias
e limites fixos e não leem o arquivo externo; `io_json.py` não carrega a política;
a saída assume sempre três categorias. Tudo isso precisa ser refeito via
`/speckit-plan` → `/speckit-tasks` → `/speckit-implement`. Há também um
`cambio.json` no mesmo diretório, mas câmbio permanece **fora de escopo** (Seção
3/10). **Este passo alterou apenas `spec.md`, `checklists/requirements.md` e este log.**

**Tasks afetadas:** nova carga de leitura/validação da política e resolução do
centro de custo; agregação por conjunto dinâmico de categorias; portão de limite ≤ 0
antes da deduplicação; golden de integração recalculado para `total_reembolso_geral
= 351,43`. `plan.md`/`data-model.md`/`quickstart.md`/`tasks.md` ainda assumem o
modelo fixo e serão regenerados.

**Custo:** 3 arquivos (`spec.md`, `checklists/requirements.md`, `DECISIONS.md`);
na spec, ~10 blocos (3 RNs novas, 5 RNs reescritas, 3 AMBs novas, Seções 2/3/4/7/8/9
e o exemplo JSON).

---

## D-004 — `total_despesas` ignora valores ≤ 0 na somatória · `2026-07-30`

**Gatilho:** pedido do usuário via `/speckit-specify`: "para o parâmetro
`total_despesas`, para a somatória não considere valores abaixo ou igual a zero".

**O que mudou na spec:**
- **RN-014**: `total_despesas` passa a **excluir da somatória qualquer valor ≤ 0**
  (estornos / despesas com "valor inválido"). Antes somava todas as despesas da
  categoria — aceitas e reprovadas, inclusive o −45,00 de `d-009`.
- Seção 4 (tabela de saída, nota sobre `total_despesas` e exemplo JSON):
  `transporte_urbano.total_despesas` passa de **155,01 → 200,01**; a nota foi
  reescrita para dizer que `d-009` (−45,00) **não** entra: 100,00 + 100,01 = 200,01.
- **RN-012**: menção a `total_despesas` ajustada para citar a exclusão de valores ≤ 0.
- Seção 9 (critérios de aceite): o critério da invariante passou a exigir
  `transporte_urbano = 200,01` (sem o estorno).
- Versão da spec: 1.0 → 1.1.

**Por quê:** o usuário definiu que valores não positivos (estornos) não devem
compor o total de despesas da categoria. `total_despesas` passa a representar o
gasto **bruto positivo** (aceito + reprovado), sem ser reduzido por estornos.

**O que isso invalidou:** reverte o comportamento previsto em **D-003**, que
instruía testar o estorno `d-009` (−45,00) **reduzindo** `total_despesas` de
`transporte_urbano` (155,01). Agora `d-009` é **excluído** da somatória e o total
sobe para 200,01. `d-009` continua **recusado** ("valor inválido", RN-010) e
listado em `reprovadas` — apenas não entra em `total_despesas`. A invariante
`total_despesas ≥ total_aceito ≥ total_reembolso` continua válida (fica até mais
folgada, pois removemos uma parcela negativa).

**O que isso invalida na implementação:** o código já existe (`src/`, `tests/`) e
os artefatos derivados (`plan.md`, `data-model.md`, `quickstart.md`,
`contracts/cli-contract.md`, `tasks.md`) ainda assumem 155,01. Precisam ser
atualizados via `/speckit-plan` → `/speckit-implement`. **Este passo alterou
apenas `spec.md` e este log.**

**Tasks afetadas:** a task de agregação/serialização de `total_despesas` e seus
testes devem passar a **excluir valores ≤ 0** e esperar `transporte_urbano = 200,01`.

**Custo:** 2 arquivos (`spec.md`, `DECISIONS.md`), ~6 blocos na spec.

---

## D-003 — Enriquecimento do exemplo de saída (colaborador, período, total_despesas) · `2026-07-30`

**Gatilho:** pedido do usuário via `/speckit-specify`. O exemplo de saída não
ecoava a identificação do colaborador nem o período, e não havia um total de
despesas por categoria antes da aplicação das regras.

**O que mudou na spec:**
- Seção 4 (tabela de saída + exemplo JSON): a saída passa a ecoar `colaborador`
  (`id`, `nome`, `centro_custo`) e `periodo` (`inicio`, `fim`); cada objeto de
  categoria ganha `total_despesas`.
- Nova **RN-014 — Total de despesas por categoria**: `total_despesas` = soma do
  `valor` de todas as despesas da categoria (aceitas + reprovadas), valendo a
  invariante `total_despesas ≥ total_aceito ≥ total_reembolso`.
- RN-012 ampliada para citar o eco de `colaborador`/`periodo` e o novo campo.
- Nova **AMB-012**: resolvida a ambiguidade "valor monetário vs. contagem" de
  `total_despesas` → decidido **valor monetário** (parideia com `total_aceito`).
- Seção 9 (critérios de aceite): contagem de regras corrigida para 14
  (RN-001..RN-014) e adicionados critérios para o eco e para a invariante.

**Por quê:** relatório de reembolso mais completo e auditável — mostra de quem/de
que período é o resultado e, por categoria, quanto foi gasto no total, quanto foi
aceito e quanto será reembolsado.

**O que isso invalidou:** o exemplo de saída anterior (sem `colaborador`,
`periodo` e `total_despesas`) — substituído. Nada de implementação foi afetado
(ainda não há código).

**Tasks afetadas:** nenhuma ainda (`tasks.md` não gerado). A futura task de
serialização da saída deve incluir os novos campos e testar a invariante e o caso
do estorno (`d-009`, −45,00) reduzindo `total_despesas` de `transporte_urbano`.

**Custo:** 1 arquivo (`spec.md`), 5 blocos tocados (tabela, exemplo, RN-012,
RN-014, AMB-012, critérios de aceite).

**Ponto em aberto sinalizado ao usuário:** a interpretação de `total_despesas`
como valor monetário (AMB-012) é reversível para contagem caso essa fosse a
intenção.

---

## D-002 — Desempate de duplicatas: mantém a primeira ocorrência · `2026-07-30`

**Gatilho:** pergunta de `/speckit-clarify`. A RN-008 dizia que duplicatas exatas
colapsam em um registro, mas não fixava **qual** cópia sobrevive. Como a spec
exige saída determinística (Seção 9), o teste de aceite não tinha um `id`
previsível para verificar entre duas duplicatas.

**O que mudou na spec:**
- RN-008: de "um sobrevive, o outro é duplicado" → "mantém-se a **primeira
  ocorrência na ordem do input**; cada cópia seguinte é recusada". Aceite fixado
  em `d-006` aceito / `d-007` duplicado.
- Seção 8 (ordem de aplicação), passo 3 de deduplicação: explicitado "mantendo a
  primeira ocorrência".
- Registrado em `## Clarifications → Session 2026-07-30`.

**Por quê:** saída determinística exige survivor previsível; "primeira ocorrência"
é o critério mais intuitivo e já era o assumido no exemplo da Seção 4.

**O que isso invalidou:** nada implementado ainda — apenas fixou um ponto antes
ambíguo. Nenhuma decisão técnica anterior caiu.

**Tasks afetadas:** nenhuma ainda (`tasks.md` não gerado). A futura task de
deduplicação deve testar explicitamente a ordem de entrada.

**Custo:** 1 arquivo (`spec.md`), 3 edições pontuais.

---

## D-001 — Tratamento de registro estruturalmente inválido · `2026-07-30`

**Gatilho:** pergunta de `/speckit-clarify`. A spec só previa `valor ≤ 0` (RN-010),
mas não dizia nada sobre registros malformados: campo obrigatório ausente,
`valor` não numérico ou `data` que não parseia como `YYYY-MM-DD`.

**O que mudou na spec:**
- Nova **RN-013 — Registro estruturalmente inválido**: recusa apenas o registro
  com motivo "registro inválido", reportado em `reprovadas_sem_categoria`; os
  demais registros seguem sendo processados; JSON de topo inparseável aborta a
  execução.
- Seção 8 (ordem de aplicação): novo passo 1 "Validação estrutural" à frente da
  normalização; os demais passos foram renumerados (2..9).
- Seção 7 (casos de borda): nova linha "Registro malformado".
- Seção 9 (critérios de aceite): "registro inválido" somado à lista de motivos e
  novo critério de que um registro malformado não impede os demais.
- Registrado em `## Clarifications → Session 2026-07-30`.

**Por quê:** processamento em lote resiliente — uma linha ruim não deve bloquear
o reembolso das despesas válidas do colaborador, e mantém rastro auditável do
problema em vez de descartá-lo silenciosamente.

**O que isso invalidou:** nada implementado ainda; ampliou o contrato de erro do
sistema (antes implícito).

**Tasks afetadas:** nenhuma ainda (`tasks.md` não gerado). A futura task de
parsing/validação de entrada deve cobrir os três casos malformados e o abort de
JSON de topo.

**Custo:** 1 arquivo (`spec.md`), 5 seções tocadas.
