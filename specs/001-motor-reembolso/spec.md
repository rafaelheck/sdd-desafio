# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.3 · **Status:** rascunho · **Última alteração:** `2026-07-31`

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
reembolsável por categoria e por que cada despesa recusada foi recusada. As
categorias válidas, seus limites, o limiar de nota fiscal e o acréscimo de
viagem passam a ser lidos de uma **política externa versionada** e podem variar
por **centro de custo**.

## Clarifications

### Session 2026-07-30

- Q: Como tratar um registro estruturalmente inválido (campo obrigatório faltando, `valor` não numérico, ou `data` não parseável)? → A: Recusar apenas o registro (motivo "registro inválido") e processar os demais; um JSON de topo que não parseia aborta a execução.
- Q: Entre duplicatas exatas, qual registro é mantido e qual vira "registro duplicado"? → A: Mantém a primeira ocorrência na ordem do input; as cópias seguintes são as duplicatas.
- Q: Uma despesa com `valor ≤ 0` recusada por um motivo anterior à checagem de valor (ex.: duplicata ou fora da competência com valor negativo) entra em `total_despesas`? → A: Não. A exclusão de `total_despesas` é **por valor**: qualquer despesa com `valor ≤ 0` fica fora da somatória, independentemente do motivo da recusa.

### Session 2026-07-31

- Q: Onde reportar despesas de uma categoria que existe no centro de custo mas tem limite ≤ 0 (ex.: hospedagem em `CC-ENG-PLATAFORMA`, `observacao` "nao reembolsavel")? → A: Sob a própria categoria (a categoria aparece no bloco `categorias` com `total_aceito`/`total_reembolso` = 0 e as despesas em `reprovadas[]`).
- Q: Quando uma despesa de categoria com limite ≤ 0 também viola outra regra (sem NF, fora do período, etc.), qual motivo prevalece? → A: O motivo de limite ≤ 0 prevalece — a aplicabilidade da categoria (existência + limite > 0) é avaliada logo após a normalização, antes de duplicata/período/valor/nota fiscal.
- Q: Quais categorias aparecem no bloco `categorias` da saída, agora que cada centro de custo tem seu próprio conjunto? → A: Apenas as categorias válidas para o centro de custo que tenham ao menos uma despesa no input; não se emitem blocos zerados para categorias configuradas sem despesas.
- Q: As regras de teto RN-002/RN-003/RN-004 ainda citavam categorias fixas (alimentação, transporte, hospedagem). Como generalizá-las para que o sistema não conheça categoria alguma? → A: Reescritas por **papel**, sem nome de categoria: RN-002 = teto de periodicidade "dia" (`min(soma_do_dia, limite)`); RN-003 = teto de periodicidade "diaria" (`min(valor, limite)` por registro); RN-004 = origem do teto (o `limite` vem da entrada da categoria na política do centro de custo resolvido — nenhuma categoria é privilegiada). O conjunto de categorias, seus limites e periodicidades saem inteiramente de `politica-v4.json`; novas categorias passam a ser reembolsáveis e categorias removidas deixam de ser aplicáveis sem qualquer mudança de regra ou código.

## 3. Fora de escopo

- Não calcula estornos, créditos ou saldos negativos — o sistema só produz
  valores de reembolso maiores ou iguais a zero.
- Não valida a autenticidade da nota fiscal; confia no campo `tem_nota_fiscal`.
- Não faz conversão de moeda; todos os valores são em BRL. (A política externa
  declara `moeda_base` BRL; não há regra de câmbio nesta versão.)
- Não decide teto por diária individual de hospedagem quando um registro agrupa
  várias diárias (ver AMB-006); em categorias de periodicidade "diaria" o teto é
  por registro.
- Não trata dias úteis/fins de semana/feriados de forma diferente — não existe
  regra de calendário na política.
- Não valida o conteúdo da política externa além de ler os parâmetros que usa;
  assume-se que o arquivo de política está bem formado.
- Não persiste dados nem expõe interface além de ler um input e emitir um output.

## 4. Entrada e saída

**Entrada:** conforme `exemplos/despesas-exemplo.json`, acrescida do indicador de
viagem (ver AMB-008). Campos e significado:

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | texto | Identificador do colaborador | sim |
| `colaborador.nome` | texto | Nome do colaborador | sim |
| `colaborador.centro_custo` | texto | Centro de custo; determina o conjunto de categorias e limites via política (RN-015). Se não existir na política, usa o objeto `padrao` | sim |
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

**Política externa (fonte da verdade de categorias e limites):** um arquivo
versionado (`politica-v4.json`) fornece, por centro de custo, o conjunto de
categorias reembolsáveis e, para cada categoria, `limite` e `periodicidade`
(e, opcionalmente, `observacao`). Fornece também os parâmetros globais
`nota_fiscal_obrigatoria_acima_de` e `acrescimo_em_viagem_percentual`. Estrutura
relevante:

| Elemento | Significado |
|---|---|
| `padrao` | Conjunto de categorias/limites usado quando o centro de custo do input não existe em `centros_custo` (RN-015) |
| `centros_custo.<CC>` | Conjunto de categorias/limites específico de um centro de custo |
| `<CC>.<categoria>.limite` | Teto monetário da categoria naquele centro. Se ≤ 0, a categoria não é reembolsável (RN-017) |
| `<CC>.<categoria>.periodicidade` | `"dia"` (limite sobre a soma da categoria por dia civil) ou `"diaria"` (limite por registro) — ver RN-016 |
| `<CC>.<categoria>.observacao` | Texto opcional usado como motivo quando o limite ≤ 0 (RN-017) |
| `nota_fiscal_obrigatoria_acima_de` | Valor acima do qual a nota fiscal é obrigatória (RN-006) |
| `acrescimo_em_viagem_percentual` | Percentual de acréscimo aplicado aos limites quando `em_viagem = true` (RN-009) |

**Saída:** definida por mim. Estrutura e significado de cada campo:

| Campo | Tipo | Significado |
|---|---|---|
| `colaborador.id` | texto | Identificador do colaborador (eco do input) |
| `colaborador.nome` | texto | Nome do colaborador (eco do input) |
| `colaborador.centro_custo` | texto | Centro de custo (eco do input) |
| `competencia` | texto | Competência processada (eco do input) |
| `periodo.inicio` | data `YYYY-MM-DD` | Primeiro dia elegível (eco do input) |
| `periodo.fim` | data `YYYY-MM-DD` | Último dia elegível (eco do input) |
| `em_viagem` | booleano | Indicador de viagem aplicado |
| `categorias.<cat>` | objeto | Um bloco por categoria **válida para o centro de custo que tenha ao menos uma despesa no input** (ver RN-016, AMB-015). Categorias com limite ≤ 0 também aparecem quando têm despesas, com totais aceito/reembolso zerados (AMB-014) |
| `categorias.<cat>.total_despesas` | número | Soma do `valor` de **todas** as despesas da categoria, aceitas **e** reprovadas, **exceto valores ≤ 0** (após arredondamento). Vale a invariante `total_despesas ≥ total_aceito ≥ total_reembolso`. Ver AMB-012, RN-014 |
| `categorias.<cat>.total_aceito` | número | Soma do `valor` das despesas **aceitas** da categoria (após arredondamento) |
| `categorias.<cat>.total_reembolso` | número | Soma efetivamente reembolsável da categoria (após aplicação de limites) |
| `categorias.<cat>.reprovadas[]` | lista | Despesas recusadas cuja categoria declarada é essa categoria válida, cada uma com `id` e `motivo` |
| `reprovadas_sem_categoria[]` | lista | Despesas recusadas por categoria não aplicável (categoria que não pertence ao conjunto do centro de custo), com `id`, `categoria_informada` e `motivo` |
| `total_reembolso_geral` | número | Soma de `total_reembolso` de **todas** as categorias presentes na saída |

Exemplo de saída (para o input de `exemplos/despesas-exemplo.json`, centro de
custo `CC-ENG-PLATAFORMA`, `em_viagem = false`). Na política vigente esse centro
tem `alimentacao` limite 75,00 (dia), `transporte_urbano` limite 80,00 (dia) e
`hospedagem` limite 0,00 (diaria, `observacao` "nao reembolsavel"):

```json
{
  "colaborador": {
    "id": "c-0417",
    "nome": "Marina Volpi",
    "centro_custo": "CC-ENG-PLATAFORMA"
  },
  "competencia": "2026-07",
  "periodo": {
    "inicio": "2026-07-01",
    "fim": "2026-07-31"
  },
  "em_viagem": false,
  "categorias": {
    "alimentacao": {
      "total_despesas": 402.83,
      "total_aceito": 306.93,
      "total_reembolso": 271.43,
      "reprovadas": [
        { "id": "d-007", "motivo": "registro duplicado" },
        { "id": "d-008", "motivo": "data fora da competência" }
      ]
    },
    "transporte_urbano": {
      "total_despesas": 200.01,
      "total_aceito": 100.00,
      "total_reembolso": 80.00,
      "reprovadas": [
        { "id": "d-004", "motivo": "sem nota fiscal obrigatória" },
        { "id": "d-009", "motivo": "valor inválido" }
      ]
    },
    "hospedagem": {
      "total_despesas": 1170.00,
      "total_aceito": 0.00,
      "total_reembolso": 0.00,
      "reprovadas": [
        { "id": "d-010", "motivo": "nao reembolsavel" },
        { "id": "d-013", "motivo": "nao reembolsavel" }
      ]
    }
  },
  "reprovadas_sem_categoria": [
    { "id": "d-005", "categoria_informada": "coworking", "motivo": "categoria não aplicável" }
  ],
  "total_reembolso_geral": 351.43
}
```

> **Nota sobre `total_despesas`:** inclui o `valor` de despesas reprovadas por
> duplicidade, fora da competência, sem nota fiscal e por limite ≤ 0
> ("nao reembolsavel") — desde que a categoria declarada seja uma categoria
> válida do centro de custo. **Valores ≤ 0 (estornos / "valor inválido") não
> entram na somatória**, assim como despesas de categoria não aplicável e
> registros estruturalmente inválidos (esses vão para `reprovadas_sem_categoria`).
> Por isso, em `transporte_urbano`, o estorno `d-009` (−45,00) **não** entra:
> 100,00 + 100,01 = 200,01. Em `hospedagem`, os dois registros são reprovados
> por "nao reembolsavel" mas seus valores (> 0) somam `total_despesas` = 1170,00
> com `total_aceito` e `total_reembolso` = 0,00.
>
> **Nota sobre o exemplo x versão anterior:** com `CC-ENG-PLATAFORMA` na política
> v4, o teto diário de alimentação passou de 60,00 para 75,00 (07-03: 110,50 →
> reembolso 75,00; 07-31: 61,00 → reembolso 61,00) e hospedagem ficou não
> reembolsável (limite 0,00), reduzindo `total_reembolso_geral` de 585,43 para
> 351,43.

---

## 5. Regras de negócio

Cada regra recebe um ID (`RN-001`, ...). As tasks vão referenciar esses IDs.

### RN-015 — Política externa e resolução de centro de custo
**Regra:** As categorias reembolsáveis, seus limites, sua periodicidade, o limiar
de nota fiscal e o acréscimo de viagem são lidos de uma política externa
versionada, não codificados na regra. Para um input, resolve-se o conjunto
aplicável assim: se `colaborador.centro_custo` existe em `centros_custo`, usa-se
o objeto daquele centro; caso contrário, usa-se o objeto `padrao`. Os parâmetros
globais `nota_fiscal_obrigatoria_acima_de` e `acrescimo_em_viagem_percentual`
valem para qualquer centro.
**Origem:** nova política de centros de custo (2026-07-31).
**Aceite:** um input com `centro_custo` inexistente na política é avaliado pelos
limites de `padrao` (alimentacao 60,00/dia, transporte 80,00/dia, hospedagem
250,00/diaria).

### RN-016 — Periodicidade do limite (classificação)
**Regra:** Cada categoria traz na política um campo `periodicidade` que **seleciona
qual mecânica de teto** se aplica, sem que o sistema precise conhecer a categoria:
- `"dia"`: aplica-se o teto de periodicidade "dia" (RN-002).
- `"diaria"`: aplica-se o teto de periodicidade "diaria" (RN-003).

A seleção é feita exclusivamente pelo valor de `periodicidade` lido da política; o
nome da categoria (`alimentacao`, `hospedagem`, etc.) **não** influencia a escolha.
Uma categoria nova com `periodicidade` "dia" já reembolsa pela mecânica de RN-002
sem qualquer alteração de regra ou código. (Um valor de `periodicidade` fora de
{"dia", "diaria"} está fora de escopo — assume-se política bem formada, ver Seção 10.)
**Origem:** nova política de centros de custo (2026-07-31); generalização 2026-07-31.
**Aceite:** na política vigente, `alimentacao` e `transporte_urbano` são "dia" e
`hospedagem` é "diaria"; se `hospedagem` passar a "dia", seu limite passa a incidir
sobre a soma do dia sem mudança no sistema.

### RN-017 — Categoria com limite ≤ 0 (não reembolsável)
**Regra:** Se, para o centro de custo resolvido, a categoria existe mas seu
`limite` é **menor ou igual a zero**, toda despesa dessa categoria é recusada com
reembolso 0. O `motivo` é o valor de `observacao` da categoria; se não houver
`observacao`, o motivo é "categoria não aplicável". Essas despesas são reportadas
**sob a própria categoria** (`categorias.<cat>.reprovadas[]`) e a categoria
aparece na saída com `total_aceito` = 0 e `total_reembolso` = 0 (mas
`total_despesas` soma os valores > 0). Esta checagem é avaliada logo após a
validade da categoria e **antes** de duplicata, período, valor e nota fiscal
(ver AMB-014, Seção 8).
**Origem:** nova política de centros de custo (2026-07-31).
**Aceite:** em `CC-ENG-PLATAFORMA` (hospedagem limite 0,00, `observacao`
"nao reembolsavel"), `d-010` e `d-013` são recusados com motivo "nao reembolsavel"
sob `hospedagem`, mesmo `d-013` estando sem nota fiscal.

### RN-001 — Categorias válidas por centro de custo
**Regra:** As categorias reembolsáveis são exatamente as **chaves do conjunto do
centro de custo resolvido** na política (RN-015) — não mais um conjunto fixo. A
comparação da categoria declarada é feita sem diferenciar maiúsculas/minúsculas e
após remover espaços nas pontas (ver AMB-003). Qualquer categoria declarada que
não esteja nesse conjunto é "categoria não aplicável", não é reembolsável e vai
para `reprovadas_sem_categoria`.
**Origem:** política do RH + nova política de centros de custo (2026-07-31).
**Aceite:** em `CC-ENG-PLATAFORMA`, `coworking` é recusada "categoria não
aplicável"; `ALIMENTACAO` é tratada como `alimentacao`. Em `CC-ADM` (sem
`hospedagem` no conjunto), uma despesa de `hospedagem` é "categoria não aplicável".

### RN-002 — Teto de periodicidade "dia" (soma diária)
**Regra:** Para **qualquer** categoria cuja `periodicidade` na política do centro
de custo resolvido seja `"dia"` (RN-016), o `limite` da categoria (RN-004) incide
sobre a **soma das despesas aceitas dessa categoria no mesmo dia civil**. O
excedente não é reembolsado; o reembolso do dia é `min(soma_do_dia, limite)`. A
regra não conhece nem cita categoria alguma — aplica-se a toda categoria "dia",
existente hoje ou adicionada no futuro. (Na política vigente, `alimentacao`,
`transporte_urbano` e `representacao` são "dia".)
**Origem:** política do RH, "limite por dia" + "despesas acima do limite são reembolsadas parcialmente"; limite e periodicidade vindos da política externa (RN-004, RN-015, RN-016).
**Aceite:** categoria "dia" com limite 75,00, 72,50 + 38,00 no mesmo dia →
total aceito 110,50, reembolso 75,00; com limite 80,00, uma despesa aceita de
100,00 no dia → reembolso 80,00.

### RN-003 — Teto de periodicidade "diaria" (por registro)
**Regra:** Para **qualquer** categoria cuja `periodicidade` na política do centro
de custo resolvido seja `"diaria"` (RN-016), o `limite` da categoria (RN-004)
incide **por registro individual**, independente de quantas diárias o registro
declare ou de quantos registros haja no dia (ver AMB-006). Reembolso do registro =
`min(valor, limite)`. A regra não conhece nem cita categoria alguma — aplica-se a
toda categoria "diaria". (Na política vigente, `hospedagem` é "diaria".)
**Origem:** política do RH, "limite por diária" (reinterpretado — ver AMB-006); limite e periodicidade vindos da política externa (RN-004, RN-015, RN-016).
**Aceite:** categoria "diaria" com limite 250,00, registro de 480,00 ("2 diárias")
→ reembolso 250,00; dois registros de 200,00 no mesmo dia → 200,00 + 200,00 (cada
um sob seu próprio teto, sem agregar o dia).

### RN-004 — Origem do teto (limite pela política, sem categoria privilegiada)
**Regra:** O teto de uma categoria é sempre o `limite` da entrada dessa categoria
na política do centro de custo resolvido (RN-015) — `politica[<CC>][<categoria>].limite`.
**Nenhuma categoria tem limite embutido no sistema**; não há valor padrão em código
para `alimentacao`, `hospedagem` ou qualquer outra. Alterar o `limite` na política
altera o teto sem mudança de regra; o conjunto `padrao` fornece o limite quando o
centro de custo não existe em `centros_custo`. Aplicado o limite, a mecânica segue
a periodicidade da categoria (RN-002 ou RN-003).
**Origem:** requisito de política externa; generalização das regras de teto (2026-07-31).
**Aceite:** `alimentacao` reembolsa com limite 60,00 no `padrao`, 75,00 em
`CC-ENG-PLATAFORMA` e 45,00 em `CC-ADM`, apenas trocando o valor na política; se a
política passar `alimentacao` para limite 80,00, o teto vira 80,00 sem tocar no código.

### RN-005 — Reembolso parcial no teto
**Regra:** Quando o valor aceito ultrapassa o teto aplicável, reembolsa-se apenas
até o teto; o excedente é perdido. A despesa continua **aceita** (entra em
`total_aceito`), apenas contribui parcialmente para o reembolso.
**Origem:** política do RH, "Despesas acima do limite são reembolsadas parcialmente".
**Aceite:** ver RN-002/003/004.

### RN-006 — Nota fiscal obrigatória
**Regra:** Nota fiscal é obrigatória para valores **estritamente acima** do
parâmetro `nota_fiscal_obrigatoria_acima_de` da política (R$ 100,00 na v4). No
valor exato do limiar não é necessária. Se obrigatória e ausente
(`tem_nota_fiscal = false`), a despesa é recusada com motivo "sem nota fiscal
obrigatória" e reembolsa 0 (ver AMB-004).
**Origem:** política do RH, "Nota fiscal é obrigatória acima de um valor base"; valor vindo da política externa (RN-015).
**Aceite:** com limiar 100,00: 100,00 sem NF → aceita; 100,01 sem NF → recusada.

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
**Regra:** Se `em_viagem = true`, os limites de **todas as categorias** do centro
de custo são multiplicados por `(1 + acrescimo_em_viagem_percentual / 100)` (na
v4, +50% → ×1,5). O limiar de nota fiscal **não** é ampliado. Uma categoria com
limite ≤ 0 permanece não reembolsável (0 × qualquer fator = 0). O indicador vale
para todas as despesas do input (ver AMB-008).
**Origem:** política do RH, "Colaborador em viagem tem limites ampliados"; percentual vindo da política externa (RN-015).
**Aceite:** em viagem, `CC-ENG-PLATAFORMA` alimentação 75,00 → 112,50; transporte
80,00 → 120,00; hospedagem 0,00 → 0,00 (permanece não reembolsável); limiar de NF
continua 100,00.

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
**Regra:** A saída ecoa os dados de identificação do input — `colaborador` (`id`,
`nome`, `centro_custo`), `competencia` e `periodo` (`inicio`, `fim`). Para cada
categoria válida do centro de custo **que tenha ao menos uma despesa no input**
(ver AMB-015) o sistema reporta: `total_despesas` (soma do `valor` de todas as
despesas da categoria, aceitas e reprovadas, exceto valores ≤ 0 — ver RN-014),
`total_aceito` (soma do `valor` das despesas aceitas), `total_reembolso` (soma
reembolsável após limites) e a lista de despesas recusadas daquela categoria com
motivo. Recusas por categoria não aplicável vão para `reprovadas_sem_categoria`
(ver AMB-011). `total_reembolso_geral` é a soma de `total_reembolso` de todas as
categorias presentes.
**Origem:** requisito de saída do desafio.
**Aceite:** ver exemplo da Seção 4.

### RN-014 — Total de despesas por categoria
**Regra:** `total_despesas` de uma categoria é a soma do `valor` (já arredondado)
de todas as despesas cuja categoria normalizada é aquela — aceitas e reprovadas
(duplicidade, fora da competência, sem nota fiscal, limite ≤ 0) — **exceto
valores ≤ 0, que nunca entram na somatória, independentemente do motivo da recusa**
(a exclusão é por valor, não por motivo). Despesas de categoria não aplicável e
registros estruturalmente inválidos também não entram (não pertencem a categoria
válida). Vale sempre `total_despesas ≥ total_aceito ≥ total_reembolso` (ver AMB-012).
**Origem:** requisito de saída (esclarecimento do usuário, 2026-07-30; revisto em
2026-07-30, ver DECISIONS D-004).
**Aceite:** em `transporte_urbano` do exemplo: 100,00 + 100,01 = 200,01 (o estorno
`d-009` de −45,00 é excluído da somatória), com `total_aceito` 100,00.

---

## 6. Ambiguidades identificadas e decisões

> **Esta seção é o coração da spec.** Uma ambiguidade resolvida no código sem
> registro aqui conta como não resolvida.

### AMB-001 — Como distribuir o teto diário entre várias despesas do mesmo dia
**Texto original do RH:** "Alimentação tem limite por dia." + "Despesas acima do limite são reembolsadas parcialmente."
**O que não está claro:** com duas despesas no mesmo dia somando mais que o teto, reembolsa-se por despesa (e nesse caso, em que ordem?) ou agrega-se o dia?
**Decisão:** o teto de categorias com periodicidade "dia" incide sobre o **agregado do dia** por categoria. Reembolso do dia = `min(soma das aceitas do dia, limite)`. Como a saída é por categoria, não é preciso ratear por despesa individual.
**Justificativa:** o limite da política é diário, não por despesa; agregar evita depender de ordenação arbitrária.
**Regra afetada:** RN-002, RN-005, RN-016.

### AMB-002 — O campo `id` conta para definir duplicidade?
**Texto original do RH:** "Duplicatas devem ser tratadas." (decisão recebida: "todos os campos iguais")
**O que não está claro:** `d-006` e `d-007` diferem apenas no `id`; se o `id` conta, não são duplicatas.
**Decisão:** `id` é identificador técnico, não campo de negócio. Duplicidade compara os demais campos. Logo `d-006`/`d-007` são duplicatas.
**Justificativa:** dois lançamentos idênticos de mesmo dia, fornecedor e valor são o mesmo evento econômico digitado duas vezes.
**Regra afetada:** RN-008.

### AMB-003 — Categoria com caixa diferente (`ALIMENTACAO`)
**Texto original do RH:** lista de categorias em minúsculas; `d-014` vem como `ALIMENTACAO`.
**O que não está claro:** `ALIMENTACAO` é a categoria válida ou uma categoria "diferente" e portanto não aplicável?
**Decisão:** comparação **sem diferenciar caixa** e com _trim_; `ALIMENTACAO` é tratada como `alimentacao`. As chaves de categoria da política são comparadas do mesmo modo.
**Justificativa:** caixa é formatação de digitação, não distinção de negócio; punir o colaborador por maiúscula seria arbitrário.
**Alternativa considerada:** correspondência estrita (recusaria `d-014` como categoria não aplicável) — descartada por ser um artefato de digitação.
**Regra afetada:** RN-001.

### AMB-004 — Falta de nota fiscal: recusa ou apenas não reembolsa?
**Texto original do RH:** "Nota fiscal é obrigatória acima de um valor base."
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
**Texto original do RH:** "Hospedagem tem limite por diária." (decisão recebida: "por registro")
**O que não está claro:** um registro de 480,00 dizendo "2 diárias" deveria ter teto de 2× o limite ou 1×?
**Decisão:** para categorias de periodicidade "diaria", o teto é **por registro** (`min(valor, limite)`), independentemente de quantas diárias o texto mencione. `d-010` reembolsa `min(480,00, limite)`.
**Justificativa:** o input não traz número de diárias de forma estruturada e confiável; contar diárias a partir da descrição seria adivinhação. Divergência da letra do RH registrada em `DECISIONS.md`.
**Regra afetada:** RN-003, RN-004, RN-016.

### AMB-007 — Precisão e arredondamento monetário (`33,333`)
**Texto original do RH:** nada sobre casas decimais.
**O que não está claro:** valores com três casas; como e quando arredondar.
**Decisão:** arredondar para 2 casas (_half up_) antes de qualquer cálculo; todas as saídas com 2 casas.
**Justificativa:** moeda tem precisão de centavo; _half up_ é o padrão financeiro usual.
**Regra afetada:** RN-011.

### AMB-008 — Onde e como o indicador de viagem é informado, e o que ele amplia
**Texto original do RH:** "Colaborador em viagem tem limites ampliados." (decisões: usuário informa; inputs separados; se em viagem, todas as despesas do input são em viagem)
**O que não está claro:** o exemplo não tem campo de viagem; onde ele fica e se o limiar de NF também escala.
**Decisão:** indicador é um campo booleano de topo `em_viagem` (default `false`), válido para todo o input; amplia os limites de categoria pelo percentual `acrescimo_em_viagem_percentual`; o limiar de NF **não** escala. O exemplo representa uma competência sem viagem.
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
**O que não está claro:** `d-013` está no período mas é hospedagem não reembolsável e também sem NF; qual motivo reportar?
**Decisão:** ordem fixa de avaliação (Seção 8); o **primeiro** portão que falha determina o motivo. A aplicabilidade da categoria (existência + limite > 0) vem antes de duplicata/período/valor/NF; o teto só se aplica a despesas já aceitas.
**Justificativa:** determinismo e auditabilidade — o mesmo input sempre produz o mesmo motivo.
**Regra afetada:** RN-001..RN-017 (ordem de aplicação).

### AMB-011 — Onde reportar recusas de categoria não aplicável
**Texto original do RH:** "para cada categoria válida ... despesas reprovadas".
**O que não está claro:** uma despesa de `coworking` recusada não pertence a nenhuma categoria válida; sob qual categoria listá-la?
**Decisão:** despesas recusadas por categoria não aplicável vão para uma lista separada `reprovadas_sem_categoria`; recusas de despesas com categoria válida (ex.: sem NF, limite ≤ 0) ficam sob a respectiva categoria.
**Justificativa:** manter a saída por categoria válida coerente, sem inventar uma categoria "outras" reembolsável.
**Regra afetada:** RN-012, RN-017.

### AMB-012 — `total_despesas`: valor monetário ou contagem?
**Texto original do usuário:** "inclua total_despesas, sendo o total de despesas incluindo aceitas e reprovadas".
**O que não está claro:** "total de despesas" pode ser a quantidade (contagem) de despesas ou a soma monetária dos valores.
**Decisão:** é a **soma monetária** do `valor` das despesas da categoria (aceitas + reprovadas).
**Justificativa:** o campo fica ao lado de `total_aceito`/`total_reembolso` (ambos monetários) e segue o mesmo padrão `total_*`; como dinheiro, dá a invariante útil `total_despesas ≥ total_aceito ≥ total_reembolso` ("do gasto total, quanto foi aceito e quanto reembolsado").
**Alternativa considerada:** contagem de despesas — descartada por quebrar a consistência de unidade com os campos vizinhos (seria melhor nomeada `quantidade_despesas`).
**Regra afetada:** RN-012, RN-014.

### AMB-013 — Centro de custo ausente na política
**Texto original da nova regra:** "Caso o centro de custo enviado no input não existir no objeto `centros_custo`, deve seguir a regra do objeto `padrao`."
**O que não está claro:** o que acontece com um centro de custo desconhecido — erro, sem reembolso, ou fallback?
**Decisão:** usa-se o objeto `padrao` da política (categorias, limites e periodicidades ali definidos). Não há erro; a avaliação segue normalmente com o conjunto padrão.
**Justificativa:** a nova política define explicitamente `padrao` como o comportamento de fallback.
**Regra afetada:** RN-015.

### AMB-014 — Categoria com limite ≤ 0: onde reportar e qual a precedência
**Texto original da nova regra:** "Se o limite de uma categoria for menor ou igual a zero, deve considerar como reembolso negado e o campo `motivo` da saída deve ser o parâmetro `observacao` da categoria, caso não exista observacao, motivo deve ser 'categoria não aplicável'."
**O que não está claro:** (a) essas despesas ficam sob a própria categoria ou em `reprovadas_sem_categoria`? (b) o motivo de limite ≤ 0 prevalece sobre outros motivos (sem NF, fora do período)?
**Decisão:** (a) ficam **sob a própria categoria** (`categorias.<cat>.reprovadas[]`), e a categoria aparece na saída com `total_aceito`/`total_reembolso` = 0; (b) o motivo de limite ≤ 0 **prevalece** — a aplicabilidade da categoria (existência + limite > 0) é avaliada logo após a normalização, antes de duplicata/período/valor/NF (esclarecimento 2026-07-31).
**Justificativa:** a categoria está configurada para o centro de custo (só que zerada), então pertence ao conjunto válido; e "não reembolsável" é uma propriedade da categoria, que deve ser reportada antes de detalhes por registro.
**Alternativa considerada:** reportar em `reprovadas_sem_categoria` — descartada por a categoria de fato existir no conjunto do centro de custo.
**Regra afetada:** RN-017, RN-012, RN-014.

### AMB-015 — Quais categorias aparecem no bloco `categorias`
**Texto original da nova regra:** cada centro de custo pode ter categorias diferentes.
**O que não está claro:** o bloco `categorias` da saída lista todas as categorias configuradas no centro de custo (mesmo sem despesas) ou só as que têm despesas?
**Decisão:** só aparecem as categorias válidas do centro de custo **que tenham ao menos uma despesa no input**; não se emitem blocos zerados para categorias configuradas sem despesas (ex.: `representacao` em `CC-COMERCIAL` sem lançamentos não aparece) — esclarecimento 2026-07-31.
**Justificativa:** mantém o comportamento anterior (a saída reflete o que foi lançado) e evita ruído de blocos vazios.
**Regra afetada:** RN-012.

---

## 7. Casos de borda

| Caso | Entrada (exemplo) | Comportamento esperado | Regra |
|---|---|---|---|
| Soma diária excede teto (periodicidade "dia") | `d-001` 72,50 + `d-002` 38,00 (categoria "dia", mesmo dia, `CC-ENG-PLATAFORMA` limite 75) | aceito 110,50; reembolso 75,00 | RN-002, RN-004, RN-005, RN-016 |
| Valor exatamente no limiar de NF | `d-003` 100,00 sem NF | aceita (NF não obrigatória) | RN-006 |
| Valor um centavo acima do limiar | `d-004` 100,01 sem NF | recusada "sem nota fiscal obrigatória" | RN-006 |
| Categoria fora do conjunto do centro | `d-005` `coworking` | recusada "categoria não aplicável" em `reprovadas_sem_categoria` | RN-001, RN-012 |
| Categoria com limite ≤ 0 | `d-010`/`d-013` `hospedagem` em `CC-ENG-PLATAFORMA` (limite 0, obs. "nao reembolsavel") | recusadas "nao reembolsavel" sob `hospedagem`; total_aceito/reembolso 0 | RN-017, AMB-014 |
| Categoria válida só em alguns centros | `representacao` em `CC-COMERCIAL` | reembolsável em `CC-COMERCIAL`; "categoria não aplicável" nos demais | RN-001, RN-015 |
| Centro de custo desconhecido | `centro_custo` inexistente na política | avaliado pelos limites de `padrao` | RN-015 |
| Duplicata (só o `id` difere) | `d-006`/`d-007` | uma aceita, a outra "registro duplicado" | RN-008 |
| Data fora do período | `d-008` 2026-04-15 | recusada "data fora da competência" | RN-007 |
| Valor negativo | `d-009` -45,00 | recusada "valor inválido" | RN-010 |
| Registro malformado | despesa sem `data` ou `valor` não numérico | recusada "registro inválido" em `reprovadas_sem_categoria`; demais processados | RN-013 |
| Categoria "diaria" acima do teto (várias diárias num registro) | `d-010` 480,00 num centro com limite 250 | aceito 480,00; reembolso 250,00 | RN-003, RN-004, RN-016 |
| Mais de 2 casas decimais | `d-011` 33,333 | arredonda para 33,33 | RN-011 |
| Fim de semana | `d-012` sábado 47,20 | tratado como qualquer dia (sem regra de calendário) | Seção 3 |
| Categoria em caixa alta | `d-014` `ALIMENTACAO` 61,00 | tratada como `alimentacao` | RN-001 |
| Data igual a `fim` | `d-014` 2026-07-31 | elegível (limite inclusivo) | RN-007, RN-009 (AMB-009) |
| Despesa aceita mas com reembolso 0 por teto já consumido | 3ª despesa de alimentação num dia já no teto | permanece **aceita** (entra em `total_aceito`), reembolso 0 | RN-005 |
| Limites ampliados em viagem | `em_viagem = true`, alimentação 85,00 num dia (limite 75 → 112,50) | reembolso 85,00 | RN-009 |

## 8. Ordem de aplicação das regras

Quando várias regras incidem sobre a mesma despesa, aplica-se nesta ordem; o
**primeiro** portão que falha define o motivo da recusa:

1. **Validação estrutural** — campos obrigatórios presentes e tipados, `valor`
   numérico, `data` parseável; senão "registro inválido" (RN-013). Se o JSON de
   topo não parseia, aborta a execução.
2. **Resolução da política** — resolver o centro de custo (o do input ou
   `padrao`) e carregar categorias, limites, periodicidades e parâmetros globais
   (RN-015).
3. **Normalização** — arredondar `valor` para 2 casas (RN-011); aplicar `trim` e
   caixa na `categoria` (RN-001); aplicar o acréscimo de viagem aos limites se
   `em_viagem` (RN-009).
4. **Categoria válida** — a categoria normalizada pertence ao conjunto do centro
   de custo? senão "categoria não aplicável" (RN-001), em `reprovadas_sem_categoria`.
5. **Limite da categoria > 0** — se o `limite` da categoria for ≤ 0, recusa com
   motivo = `observacao` (ou "categoria não aplicável"), sob a própria categoria
   (RN-017).
6. **Deduplicação** — colapsar registros idênticos por campos de negócio,
   mantendo a primeira ocorrência; cada cópia seguinte → "registro duplicado" (RN-008).
7. **Período** — `data` em `[inicio, fim]`; senão "data fora da competência" (RN-007).
8. **Valor válido** — `valor > 0`; senão "valor inválido" (RN-010).
9. **Nota fiscal** — se `valor > nota_fiscal_obrigatoria_acima_de`, exige NF;
   senão "sem nota fiscal obrigatória" (RN-006).
10. **Aplicação de teto** — as despesas que passaram de 1 a 9 são **aceitas**; o
    `limite` vem da entrada da categoria na política do centro resolvido (RN-004) e
    a mecânica é escolhida pela `periodicidade` (RN-016): agregando por dia civil
    quando "dia" (RN-002) ou por registro quando "diaria" (RN-003), sempre
    aplicando `min(soma_ou_valor, limite)` com reembolso parcial no excedente (RN-005).
11. **Agregação** — totais por categoria e total geral (RN-012).

## 9. Critérios de aceite

O sistema está pronto quando:

- [ ] Para o input de `exemplos/despesas-exemplo.json` (centro `CC-ENG-PLATAFORMA`)
      com `em_viagem = false`, a saída é exatamente a do exemplo da Seção 4
      (totais e recusas por categoria, `total_reembolso_geral = 351,43`).
- [ ] Categorias, limites, periodicidade, limiar de NF e acréscimo de viagem são
      lidos da política externa, não codificados; um centro de custo desconhecido
      cai em `padrao` (RN-015).
- [ ] Nenhuma categoria é conhecida ou privilegiada pelo sistema: o teto de cada
      categoria vem de `politica[<CC>][<categoria>].limite` (RN-004) e a mecânica
      da `periodicidade` (RN-002/RN-003) é escolhida pelo valor lido da política,
      não pelo nome da categoria. Adicionar uma categoria à política a torna
      reembolsável, removê-la a torna "categoria não aplicável", e mudar seu
      `limite`/`periodicidade` muda o resultado — tudo **sem alterar regra ou
      código** (RN-001, RN-004, RN-015, RN-016).
- [ ] Cada uma das 17 regras (RN-001..RN-017) tem ao menos um teste com números.
- [ ] A saída ecoa `colaborador` (`id`, `nome`, `centro_custo`) e `periodo`
      (`inicio`, `fim`) do input.
- [ ] Em toda categoria vale `total_despesas ≥ total_aceito ≥ total_reembolso`, e
      `total_despesas` inclui o `valor` das despesas reprovadas da categoria
      (inclusive por limite ≤ 0), mas **exclui valores ≤ 0** (ex.:
      `transporte_urbano` = 200,01, sem o estorno `d-009` de −45,00).
- [ ] Uma categoria com limite ≤ 0 recusa suas despesas com motivo igual à
      `observacao` (ou "categoria não aplicável" quando não houver), sob a própria
      categoria, e esse motivo prevalece sobre sem NF/fora do período.
- [ ] O bloco `categorias` lista apenas categorias válidas do centro com ao menos
      uma despesa; categorias configuradas sem despesas não aparecem.
- [ ] Cada despesa recusada traz um dos motivos: "categoria não aplicável",
      "data fora da competência", "registro duplicado", "sem nota fiscal
      obrigatória", "valor inválido", "registro inválido", ou a `observacao` da
      categoria (limite ≤ 0).
- [ ] Um registro malformado é recusado ("registro inválido") sem impedir o
      processamento das demais despesas do input.
- [ ] Valor no limiar de NF sem NF é aceito e um centavo acima sem NF é recusado.
- [ ] Uma despesa aceita cujo reembolso foi limitado pelo teto continua contando
      em `total_aceito` com seu valor cheio.
- [ ] Com `em_viagem = true`, os limites de cada categoria do centro escalam pelo
      `acrescimo_em_viagem_percentual` (na v4, ×1,5) e o limiar de NF permanece
      inalterado; categorias com limite ≤ 0 continuam não reembolsáveis.
- [ ] Todos os valores de saída têm exatamente 2 casas decimais.
- [ ] O resultado é determinístico: o mesmo input produz sempre a mesma saída.

## 10. O que fica em aberto

- **Diárias reais de hospedagem:** o input não estrutura número de diárias, então
  o teto de categorias "diaria" é por registro (AMB-006). Se no futuro o input
  trouxer `qtd_diarias`, a regra deve ser revista, e isso exige nova entrada em
  `DECISIONS.md`.
- **Duplicata parcial:** registros "quase iguais" (mesmo dia/fornecedor/valor,
  descrições diferentes) **não** são considerados duplicados nesta versão. Decisão
  provisória: só duplicidade exata conta; casos suspeitos passam como aceitos.
- **Validação da política externa:** assume-se que o arquivo de política está bem
  formado e vigente; não há verificação de consistência (limites negativos além
  de 0, periodicidades desconhecidas, versão/vigência) nesta versão.
- **Câmbio:** a política declara `moeda_base` BRL e há um arquivo de câmbio no
  ambiente, mas conversão de moeda continua fora de escopo até haver requisito.
- **Moeda e fuso:** assume-se BRL e datas civis sem fuso horário; multi-moeda e
  fuso ficam fora até haver requisito.
- **Vários inputs de uma mesma competência (viagem + não-viagem):** cada input é
  processado isoladamente; a consolidação entre inputs (se necessária) não está
  especificada aqui.
