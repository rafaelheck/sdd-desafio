# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Status:** rascunho · **Última alteração:** `2026-07-30`

> **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ. Nenhuma linha
> aqui pode citar linguagem, biblioteca, classe, função ou estrutura de pasta.
> Se apareceu solução, o lugar dela é o `plan.md`.
>
> **Teste de aceitação da própria spec:** uma pessoa que nunca viu o projeto
> consegue, lendo só este arquivo, verificar se o sistema está correto?

---

## 1. Problema

Hoje a decisão sobre reembolso de despesas dos colaboradores é feita à mão a
partir de uma política de RH escrita em prosa e cheia de casos não resolvidos
(limites, notas fiscais, duplicatas, período). Isso é lento, inconsistente entre
analistas e não deixa rastro de _por que_ cada despesa foi aceita, recusada ou
paga parcialmente.

## 2. Objetivo

Dado um conjunto de despesas de um colaborador em uma competência, o sistema
decide de forma determinística e auditável o que é reembolsável, quanto é
reembolsável por categoria e por que cada despesa recusada foi recusada.

## Clarifications

### Session 2026-07-30

- Q: Como tratar um registro estruturalmente inválido (campo obrigatório faltando, `valor` não numérico, ou `data` não parseável)? → A: Recusar apenas o registro (motivo "registro inválido") e processar os demais; um JSON de topo que não parseia aborta a execução.
- Q: Entre duplicatas exatas, qual registro é mantido e qual vira "registro duplicado"? → A: Mantém a primeira ocorrência na ordem do input; as cópias seguintes são as duplicatas.

## 3. Fora de escopo

- Não calcula estornos, créditos ou saldos negativos — o sistema só produz
  valores de reembolso maiores ou iguais a zero.
- Não valida a autenticidade da nota fiscal; confia no campo `tem_nota_fiscal`.
- Não faz conversão de moeda; todos os valores são em BRL.
- Não decide teto por diária individual de hospedagem quando um registro agrupa
  várias diárias (ver AMB-006); o teto é por registro.
- Não trata dias úteis/fins de semana/feriados de forma diferente — não existe
  regra de calendário na política.
- Não persiste dados nem expõe interface além de ler um input e emitir um output.

## 4. Entrada e saída

**Entrada:** conforme `exemplos/despesas-exemplo.json`, acrescida do indicador de
viagem (ver AMB-008). Campos e significado:

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | texto | Identificador do colaborador | sim |
| `colaborador.nome` | texto | Nome do colaborador | sim |
| `colaborador.centro_custo` | texto | Centro de custo | sim |
| `periodo.competencia` | texto `YYYY-MM` | Rótulo da competência | sim |
| `periodo.inicio` | data `YYYY-MM-DD` | Primeiro dia elegível (inclusive) | sim |
| `periodo.fim` | data `YYYY-MM-DD` | Último dia elegível (inclusive) | sim |
| `em_viagem` | booleano | Se toda a competência deste input é em viagem (default `false` quando ausente) | não |
| `despesas[].id` | texto | Identificador do registro (não é campo de negócio, ver AMB-002) | sim |
| `despesas[].data` | data `YYYY-MM-DD` | Dia civil da despesa | sim |
| `despesas[].categoria` | texto | Categoria declarada | sim |
| `despesas[].descricao` | texto | Descrição livre | sim |
| `despesas[].fornecedor` | texto | Fornecedor | sim |
| `despesas[].valor` | número | Valor em BRL | sim |
| `despesas[].tem_nota_fiscal` | booleano | Se há nota fiscal anexada | sim |

**Saída:** definida por mim. Estrutura e significado de cada campo:

| Campo | Tipo | Significado |
|---|---|---|
| `competencia` | texto | Competência processada (eco do input) |
| `em_viagem` | booleano | Indicador de viagem aplicado |
| `categorias.<cat>.total_aceito` | número | Soma do `valor` das despesas **aceitas** da categoria (após arredondamento) |
| `categorias.<cat>.total_reembolso` | número | Soma efetivamente reembolsável da categoria (após aplicação de tetos) |
| `categorias.<cat>.reprovadas[]` | lista | Despesas recusadas cuja categoria declarada é essa categoria válida, cada uma com `id` e `motivo` |
| `reprovadas_sem_categoria[]` | lista | Despesas recusadas por categoria não aplicável (não pertencem a nenhuma categoria válida), com `id`, `categoria_informada` e `motivo` |
| `total_reembolso_geral` | número | Soma de `total_reembolso` das três categorias |

Exemplo de saída (para o input de `exemplos/despesas-exemplo.json`, `em_viagem = false`):

```json
{
  "competencia": "2026-07",
  "em_viagem": false,
  "categorias": {
    "alimentacao": {
      "total_aceito": 306.93,
      "total_reembolso": 255.43,
      "reprovadas": [
        { "id": "d-007", "motivo": "registro duplicado" },
        { "id": "d-008", "motivo": "data fora da competência" }
      ]
    },
    "transporte_urbano": {
      "total_aceito": 100.00,
      "total_reembolso": 80.00,
      "reprovadas": [
        { "id": "d-004", "motivo": "sem nota fiscal obrigatória" },
        { "id": "d-009", "motivo": "valor inválido" }
      ]
    },
    "hospedagem": {
      "total_aceito": 480.00,
      "total_reembolso": 250.00,
      "reprovadas": [
        { "id": "d-013", "motivo": "sem nota fiscal obrigatória" }
      ]
    }
  },
  "reprovadas_sem_categoria": [
    { "id": "d-005", "categoria_informada": "coworking", "motivo": "categoria não aplicável" }
  ],
  "total_reembolso_geral": 585.43
}
```

---

## 5. Regras de negócio

Cada regra recebe um ID (`RN-001`, ...). As tasks vão referenciar esses IDs.

### RN-001 — Categorias válidas
**Regra:** Só existem três categorias reembolsáveis: `alimentacao`,
`transporte_urbano` e `hospedagem`. A comparação é feita sem diferenciar
maiúsculas/minúsculas e após remover espaços nas pontas (ver AMB-003). Qualquer
outra categoria é "categoria não aplicável" e não é reembolsável.
**Origem:** política do RH, item "Categorias fora da política não são reembolsáveis".
**Aceite:** `coworking` é recusada com motivo "categoria não aplicável"; `ALIMENTACAO`
é tratada como `alimentacao`.

### RN-002 — Teto diário de alimentação
**Regra:** O teto de `alimentacao` é R$ 60,00 por dia civil, somando **todas** as
despesas aceitas da categoria naquele dia. O excedente não é reembolsado; o
reembolso do dia é `min(soma_do_dia, teto)`.
**Origem:** política do RH, "Alimentação tem limite de R$ 60 por dia" + "Despesas acima do limite são reembolsadas parcialmente".
**Aceite:** 72,50 + 38,00 no mesmo dia → total aceito 110,50, reembolso 60,00.

### RN-003 — Teto diário de transporte urbano
**Regra:** O teto de `transporte_urbano` é R$ 80,00 por dia civil, somando todas
as despesas aceitas da categoria naquele dia. Reembolso do dia = `min(soma_do_dia, teto)`.
**Origem:** política do RH, "Transporte urbano tem limite de R$ 80 por dia".
**Aceite:** uma corrida aceita de 100,00 no dia → reembolso 80,00.

### RN-004 — Teto de hospedagem por registro
**Regra:** O teto de `hospedagem` é R$ 250,00 **por registro**, independente da
quantidade de diárias que o registro declare ou de quantos registros houver no
dia. Reembolso do registro = `min(valor, teto)`.
**Origem:** política do RH, "Hospedagem tem limite de R$ 250 por diária" (reinterpretado — ver AMB-006).
**Aceite:** registro de 480,00 ("2 diárias") → reembolso 250,00.

### RN-005 — Reembolso parcial no teto
**Regra:** Quando o valor aceito ultrapassa o teto aplicável, reembolsa-se apenas
até o teto; o excedente é perdido. A despesa continua **aceita** (entra em
`total_aceito`), apenas contribui parcialmente para o reembolso.
**Origem:** política do RH, "Despesas acima do limite são reembolsadas parcialmente".
**Aceite:** ver RN-002/003/004.

### RN-006 — Nota fiscal obrigatória
**Regra:** Nota fiscal é obrigatória para valores **estritamente acima** de
R$ 100,00. Em R$ 100,00 exatos não é necessária. Se obrigatória e ausente
(`tem_nota_fiscal = false`), a despesa é recusada com motivo "sem nota fiscal
obrigatória" e reembolsa 0 (ver AMB-004).
**Origem:** política do RH, "Nota fiscal é obrigatória acima de R$ 100".
**Aceite:** 100,00 sem NF → aceita; 100,01 sem NF → recusada.

### RN-007 — Período de competência
**Regra:** Só são elegíveis despesas cuja `data` esteja no intervalo
`[inicio, fim]` inclusive. Data anterior a `inicio` ou posterior a `fim` é
recusada com motivo "data fora da competência" (ver AMB-009).
**Origem:** política do RH, "Despesas devem ser lançadas dentro do período de competência".
**Aceite:** despesa de 2026-04-15 numa competência 2026-07-01..2026-07-31 → recusada.

### RN-008 — Duplicatas
**Regra:** Dois registros são duplicados quando todos os campos de negócio são
iguais (`data`, `categoria` normalizada, `descricao`, `fornecedor`, `valor`,
`tem_nota_fiscal`), ignorando o `id`. Duplicatas colapsam em um único registro:
mantém-se a **primeira ocorrência na ordem do input** e cada cópia seguinte é
recusada com motivo "registro duplicado" (ver AMB-002).
**Origem:** política do RH, "Duplicatas devem ser tratadas".
**Aceite:** `d-006` e `d-007` (idênticos exceto `id`) → `d-006` (primeiro) é aceito, `d-007` é "registro duplicado".

### RN-009 — Limites ampliados em viagem
**Regra:** Se `em_viagem = true`, os tetos das três categorias são multiplicados
por 1,5 (alimentação 90,00/dia; transporte 120,00/dia; hospedagem 375,00/registro).
O limiar de nota fiscal (R$ 100,00) **não** é ampliado. O indicador vale para
todas as despesas do input (ver AMB-008).
**Origem:** política do RH, "Colaborador em viagem tem limites ampliados em 50%".
**Aceite:** em viagem, alimentação de 85,00 num dia → reembolso 85,00 (dentro de 90).

### RN-010 — Valores inválidos
**Regra:** Valor menor ou igual a zero é inválido; a despesa é recusada com
motivo "valor inválido" e não entra em `total_aceito` nem no reembolso (ver AMB-005).
**Origem:** decisão de escopo — não há reembolso negativo (Seção 3).
**Aceite:** valor -45,00 → recusada com "valor inválido".

### RN-011 — Precisão monetária
**Regra:** Todo valor é tratado com 2 casas decimais. Entradas com mais casas são
arredondadas para 2 casas por arredondamento meio-para-cima (_half up_, afastando
de zero) **antes** de qualquer cálculo. Toda saída tem 2 casas (ver AMB-007).
**Origem:** decisão — moeda tem precisão de centavo.
**Aceite:** 33,333 → 33,33.

### RN-013 — Registro estruturalmente inválido
**Regra:** Um registro cujo formato impede a avaliação — campo obrigatório
ausente, `valor` não numérico, ou `data` que não parseia como `YYYY-MM-DD` — é
recusado com motivo "registro inválido" e reportado em `reprovadas_sem_categoria`
(pois não pode ser classificado com confiança). Os demais registros são
processados normalmente. Se o JSON de topo não puder ser parseado, a execução
aborta com erro e nada é reembolsado.
**Origem:** decisão de esclarecimento (Clarifications 2026-07-30).
**Aceite:** um registro sem `data` → recusado "registro inválido"; as demais
despesas do input continuam sendo avaliadas.

### RN-012 — Agregação por categoria
**Regra:** Para cada categoria válida o sistema reporta: `total_aceito` (soma do
`valor` das despesas aceitas), `total_reembolso` (soma reembolsável após tetos) e
a lista de despesas recusadas daquela categoria com motivo. Recusas por categoria
não aplicável vão para `reprovadas_sem_categoria` (ver AMB-011).
**Origem:** requisito de saída do desafio.
**Aceite:** ver exemplo da Seção 4.

---

## 6. Ambiguidades identificadas e decisões

> **Esta seção é o coração da spec.** Uma ambiguidade resolvida no código sem
> registro aqui conta como não resolvida.

### AMB-001 — Como distribuir o teto diário entre várias despesas do mesmo dia
**Texto original do RH:** "Alimentação tem limite de R$ 60 por dia." + "Despesas acima do limite são reembolsadas parcialmente."
**O que não está claro:** com duas despesas no mesmo dia somando mais que o teto, reembolsa-se por despesa (e nesse caso, em que ordem?) ou agrega-se o dia?
**Decisão:** o teto incide sobre o **agregado do dia** por categoria. Reembolso do dia = `min(soma das aceitas do dia, teto)`. Como a saída é por categoria, não é preciso ratear por despesa individual.
**Justificativa:** o limite da política é diário, não por despesa; agregar evita depender de ordenação arbitrária.
**Regra afetada:** RN-002, RN-003, RN-005.

### AMB-002 — O campo `id` conta para definir duplicidade?
**Texto original do RH:** "Duplicatas devem ser tratadas." (decisão recebida: "todos os campos iguais")
**O que não está claro:** `d-006` e `d-007` diferem apenas no `id`; se o `id` conta, não são duplicatas.
**Decisão:** `id` é identificador técnico, não campo de negócio. Duplicidade compara os demais campos. Logo `d-006`/`d-007` são duplicatas.
**Justificativa:** dois lançamentos idênticos de mesmo dia, fornecedor e valor são o mesmo evento econômico digitado duas vezes.
**Regra afetada:** RN-008.

### AMB-003 — Categoria com caixa diferente (`ALIMENTACAO`)
**Texto original do RH:** lista de categorias em minúsculas; `d-014` vem como `ALIMENTACAO`.
**O que não está claro:** `ALIMENTACAO` é a categoria válida ou uma categoria "diferente" e portanto não aplicável?
**Decisão:** comparação **sem diferenciar caixa** e com _trim_; `ALIMENTACAO` é tratada como `alimentacao`.
**Justificativa:** caixa é formatação de digitação, não distinção de negócio; punir o colaborador por maiúscula seria arbitrário.
**Alternativa considerada:** correspondência estrita (recusaria `d-014` como categoria não aplicável) — descartada por ser um artefato de digitação.
**Regra afetada:** RN-001.

### AMB-004 — Falta de nota fiscal: recusa ou apenas não reembolsa?
**Texto original do RH:** "Nota fiscal é obrigatória acima de R$ 100."
**O que não está claro:** a lista de motivos de recusa do desafio não inclui "sem nota fiscal"; o que fazer com `d-004` e `d-013`?
**Decisão:** falta de NF obrigatória **recusa** a despesa (motivo "sem nota fiscal obrigatória"), reembolso 0, e ela não entra em `total_aceito`. A lista de motivos do enunciado é ilustrativa, não exaustiva.
**Justificativa:** sem documento fiscal a empresa não pode reembolsar legalmente.
**Regra afetada:** RN-006.

### AMB-005 — Valores negativos / estornos (`-45,00`)
**Texto original do RH:** nada sobre valores negativos.
**O que não está claro:** um valor negativo é estorno que abate a categoria, registro inválido, ou ignorado?
**Decisão:** valor ≤ 0 é **inválido** e recusado ("valor inválido"); o motor não processa créditos.
**Justificativa:** reembolso é um pagamento não negativo; estorno é outro processo (Seção 3).
**Regra afetada:** RN-010.

### AMB-006 — Hospedagem: "por diária" vs. "por registro"
**Texto original do RH:** "Hospedagem tem limite de R$ 250 por diária." (decisão recebida: "250 por registro")
**O que não está claro:** um registro de 480,00 dizendo "2 diárias" deveria ter teto de 500 (2×250) ou 250?
**Decisão:** teto de **R$ 250 por registro**, conforme decisão recebida, independentemente de quantas diárias o texto mencione. `d-010` reembolsa 250,00.
**Justificativa:** o input não traz número de diárias de forma estruturada e confiável; contar diárias a partir da descrição seria adivinhação. Divergência da letra do RH registrada em `DECISIONS.md`.
**Regra afetada:** RN-004.

### AMB-007 — Precisão e arredondamento monetário (`33,333`)
**Texto original do RH:** nada sobre casas decimais.
**O que não está claro:** valores com três casas; como e quando arredondar.
**Decisão:** arredondar para 2 casas (_half up_) antes de qualquer cálculo; todas as saídas com 2 casas.
**Justificativa:** moeda tem precisão de centavo; _half up_ é o padrão financeiro usual.
**Regra afetada:** RN-011.

### AMB-008 — Onde e como o indicador de viagem é informado, e o que ele amplia
**Texto original do RH:** "Colaborador em viagem tem limites ampliados em 50%." (decisões: usuário informa; inputs separados; se em viagem, todas as despesas do input são em viagem)
**O que não está claro:** o exemplo não tem campo de viagem; onde ele fica e se o limiar de NF também escala.
**Decisão:** indicador é um campo booleano de topo `em_viagem` (default `false`), válido para todo o input; amplia em 50% **apenas os três tetos de categoria**; o limiar de R$ 100 de NF **não** escala. O exemplo representa uma competência sem viagem.
**Justificativa:** viagem amplia a tolerância de gasto, não a obrigação fiscal.
**Regra afetada:** RN-009, RN-006.

### AMB-009 — Limites do período são inclusivos? Qual campo manda?
**Texto original do RH:** "Despesas devem ser lançadas dentro do período de competência."
**O que não está claro:** `inicio`/`fim` são inclusivos? Vale o rótulo `competencia` (2026-07) ou o intervalo de datas?
**Decisão:** janela autoritativa é `[inicio, fim]` **inclusive**; se `competencia` divergir do intervalo, vale o intervalo. `d-014` (2026-07-31 = `fim`) é elegível.
**Justificativa:** datas explícitas são mais precisas que um rótulo de mês.
**Regra afetada:** RN-007.

### AMB-010 — Precedência quando uma despesa viola várias regras
**Texto original do RH:** implícito — regras coexistem.
**O que não está claro:** `d-013` está no período mas é sem NF e acima do teto; qual motivo reportar?
**Decisão:** ordem fixa de avaliação (Seção 8); o **primeiro** portão que falha determina o motivo. Teto só se aplica a despesas já aceitas.
**Justificativa:** determinismo e auditabilidade — o mesmo input sempre produz o mesmo motivo.
**Regra afetada:** RN-001..RN-011 (ordem de aplicação).

### AMB-011 — Onde reportar recusas de categoria não aplicável
**Texto original do RH:** "para cada categoria válida ... despesas reprovadas".
**O que não está claro:** uma despesa de `coworking` recusada não pertence a nenhuma categoria válida; sob qual categoria listá-la?
**Decisão:** despesas recusadas por categoria não aplicável vão para uma lista separada `reprovadas_sem_categoria`; recusas de despesas com categoria válida (ex.: sem NF) ficam sob a respectiva categoria.
**Justificativa:** manter a saída por categoria válida coerente, sem inventar uma categoria "outras" reembolsável.
**Regra afetada:** RN-012.

---

## 7. Casos de borda

| Caso | Entrada (exemplo) | Comportamento esperado | Regra |
|---|---|---|---|
| Soma diária excede teto | `d-001` 72,50 + `d-002` 38,00 (alimentação, mesmo dia) | aceito 110,50; reembolso 60,00 | RN-002, RN-005 |
| Valor exatamente no limiar de NF | `d-003` 100,00 sem NF | aceita (NF não obrigatória) | RN-006 |
| Valor um centavo acima do limiar | `d-004` 100,01 sem NF | recusada "sem nota fiscal obrigatória" | RN-006 |
| Categoria fora da política | `d-005` `coworking` | recusada "categoria não aplicável" em `reprovadas_sem_categoria` | RN-001, RN-012 |
| Duplicata (só o `id` difere) | `d-006`/`d-007` | uma aceita, a outra "registro duplicado" | RN-008 |
| Data fora do período | `d-008` 2026-04-15 | recusada "data fora da competência" | RN-007 |
| Valor negativo | `d-009` -45,00 | recusada "valor inválido" | RN-010 |
| Registro malformado | despesa sem `data` ou `valor` não numérico | recusada "registro inválido" em `reprovadas_sem_categoria`; demais processados | RN-013 |
| Hospedagem acima do teto (várias diárias num registro) | `d-010` 480,00 | aceito 480,00; reembolso 250,00 | RN-004 |
| Mais de 2 casas decimais | `d-011` 33,333 | arredonda para 33,33 | RN-011 |
| Fim de semana | `d-012` sábado 47,20 | tratado como qualquer dia (sem regra de calendário) | Seção 3 |
| Categoria em caixa alta | `d-014` `ALIMENTACAO` 61,00 | tratada como `alimentacao`; teto 60 → reembolso 60,00 | RN-001, RN-002 |
| Data igual a `fim` | `d-014` 2026-07-31 | elegível (limite inclusivo) | RN-009 |
| Despesa aceita mas com reembolso 0 por teto já consumido | 3ª despesa de alimentação num dia já no teto | permanece **aceita** (entra em `total_aceito`), reembolso 0 | RN-005 |

## 8. Ordem de aplicação das regras

Quando várias regras incidem sobre a mesma despesa, aplica-se nesta ordem; o
**primeiro** portão que falha define o motivo da recusa:

1. **Validação estrutural** — campos obrigatórios presentes e tipados, `valor`
   numérico, `data` parseável; senão "registro inválido" (RN-013). Se o JSON de
   topo não parseia, aborta a execução.
2. **Normalização** — arredondar `valor` para 2 casas (RN-011); aplicar `trim`
   e caixa na `categoria` (RN-001); aplicar multiplicador de viagem aos tetos se
   `em_viagem` (RN-009).
3. **Deduplicação** — colapsar registros idênticos por campos de negócio,
   mantendo a primeira ocorrência; cada cópia seguinte → "registro duplicado" (RN-008).
4. **Categoria válida** — senão "categoria não aplicável" (RN-001).
5. **Período** — `data` em `[inicio, fim]`; senão "data fora da competência" (RN-007).
6. **Valor válido** — `valor > 0`; senão "valor inválido" (RN-010).
7. **Nota fiscal** — se `valor > 100`, exige NF; senão "sem nota fiscal obrigatória" (RN-006).
8. **Aplicação de teto** — as despesas que passaram de 1 a 7 são **aceitas**;
   calcula-se o reembolso agregando por dia (alimentação/transporte) ou por
   registro (hospedagem) e aplicando `min(valor, teto)` (RN-002..RN-005).
9. **Agregação** — totais por categoria e total geral (RN-012).

## 9. Critérios de aceite

O sistema está pronto quando:

- [ ] Para o input de `exemplos/despesas-exemplo.json` com `em_viagem = false`, a
      saída é exatamente a do exemplo da Seção 4 (totais e recusas por categoria,
      `total_reembolso_geral = 585,43`).
- [ ] Cada uma das 11 regras (RN-001..RN-012) tem ao menos um teste com números.
- [ ] Cada despesa recusada traz um dos motivos: "categoria não aplicável",
      "data fora da competência", "registro duplicado", "sem nota fiscal
      obrigatória", "valor inválido", "registro inválido".
- [ ] Um registro malformado é recusado ("registro inválido") sem impedir o
      processamento das demais despesas do input.
- [ ] Valor 100,00 sem NF é aceito e 100,01 sem NF é recusado.
- [ ] Uma despesa aceita cujo reembolso foi limitado pelo teto continua contando
      em `total_aceito` com seu valor cheio.
- [ ] Com `em_viagem = true`, os três tetos passam a 90 / 120 / 375 e o limiar de
      NF continua em 100,00.
- [ ] Todos os valores de saída têm exatamente 2 casas decimais.
- [ ] O resultado é determinístico: o mesmo input produz sempre a mesma saída.

## 10. O que fica em aberto

- **Diárias reais de hospedagem:** o input não estrutura número de diárias, então
  o teto é por registro (AMB-006). Se no futuro o input trouxer `qtd_diarias`, a
  regra deve ser revista para teto por diária, e isso exige nova entrada em
  `DECISIONS.md`.
- **Duplicata parcial:** registros "quase iguais" (mesmo dia/fornecedor/valor,
  descrições diferentes) **não** são considerados duplicados nesta versão. Decisão
  provisória: só duplicidade exata conta; casos suspeitos passam como aceitos.
- **Moeda e fuso:** assume-se BRL e datas civis sem fuso horário; multi-moeda e
  fuso ficam fora até haver requisito.
- **Vários inputs de uma mesma competência (viagem + não-viagem):** cada input é
  processado isoladamente; a consolidação entre inputs (se necessária) não está
  especificada aqui.
