 ▐▛███▜▌   Claude Code v2.1.220
▝▜█████▛▘  Opus 4.8 · Claude Pro
  ▘▘ ▝▝    ~\Área de Trabalho\Teste SDD\sdd-desafio


❯ /speckit-specify Atualize a spec existente seguindo as novas regras de        
negócio                                                                         
                                                                                
Novas regras sobre categorias existentes, limites e centros de custo:           
<regras-centro-de-custo>                                                        
- Informações sobre categorias de despesas estão especificadas em um arquivo    
externo src/informacoes_externas/politica-v4.json                               
- Cada centro de custo pode ter categorias diferentes, as categorias existentes 
agora devem obedecer o arquivo politica-v4.json                                 
- Caso o centro de custo enviado no input não existir no objeto                 
"centros_custo", deve seguir a regra do objeto "padrao"                         
- Os valores de limite de despesa agora devem respeitar os especificados para   
cada centro de custo no arquivo politica-v4.json                                
- Se o limite de uma categoria for menor ou igual a zero, deve considerar como  
reembolso negado e o campo "motivo" da saida deve ser o parameto "observacao"   
da categoria, caso não exista observacao, motivo deve ser "categoria não        
aplicável"                                                                      
- O percentual de aumento para colaboradores em viagem deve respeitar o valor   
do parametro "acrescimo_em_viagem_percentual"                                   
- O valor base para nota fiscal obrigatório deve respeitar o valor do parametro 
"nota_fiscal_obrigatoria_acima_de"                                              
- Cada categoria possui um parametro "peridiocidade", para o valor do campo     
periodicidade siga as regras a baixo:                                           
  1. Valor "dia": Considere o limite sobre a somatoria dos registros da         
categoria (exemplo: regras atuais para categorias alimentacao e                 
transporte_urbano)                                                              
  2. Valor "diaria": Considere o limite sobre o registro unico, cada registro   
terá seu próprio limite (exemplo: regra atual para categoria hospedagem)        

● I'll start by understanding the current state — the existing spec, the
  extensions config, and the external policy file the new rules reference.

  Read 1 file (ctrl+o to expand)

● No extensions.yml (so no hooks), and feature.json points at
  specs/001-motor-reembolso. This is an update to the existing spec. The new
  rules reference politica-v4.json, which I've now read. Let me pull the
  remaining context: the example input, DECISIONS.md, and the plan/tasks to
  understand the current model.

  Listed 1 directory (ctrl+o to expand)

● I have full context now. Key facts:

  - No extensions.yml → no hooks to run. feature.json →
  specs/001-motor-reembolso, so this is an in-place update of the existing spec
  (not a new feature dir).
  - The example input uses CC-ENG-PLATAFORMA, which in politica-v4.json has
  alimentacao limit 75 (not 60) and hospedagem limit 0.00 with observacao "nao 
  reembolsavel". So the current spec's example output becomes wrong and must be
  recomputed.
  - No DECISIONS.md exists yet (referenced but absent).

  The new rules are mostly a clean parameterization of existing RNs, but three
  points genuinely change the output contract and I can't safely default them.
  Let me settle those before rewriting the spec.

● User answered Claude's questions:
  ⎿  · Quando uma categoria existe no centro de custo mas tem limite ≤ 0 (ex.: 
     hospedagem em CC-ENG-PLATAFORMA, observacao "nao reembolsavel"), onde as 
     despesas negadas devem ser reportadas na saída? → Sob a própria categoria
     · Quando uma despesa de categoria com limite ≤ 0 também viola outra regra 
     (ex.: hospedagem sem nota fiscal obrigatória, ou fora do período), qual 
     motivo deve prevalecer? → Limite ≤ 0 prevalece
     · Quais categorias aparecem no bloco `categorias` da saída, agora que cada 
     centro de custo tem seu próprio conjunto? → Só as que têm despesas

● All three resolved:
  1. Limit ≤ 0 denials → under their own category (reprovadas[], category shown
  with zeroed totals).
  2. Limit ≤ 0 motivo prevails — evaluated right after category validity, before
  período/duplicata/valor/NF.
  3. Output categorias block shows only categories that have expenses.

  Now I'll rewrite the spec. Let me write the complete updated spec.md.

● Write(specs\001-motor-reembolso\spec.md)
  ⎿  User rejected write to specs\001-motor-reembolso\spec.md
       1 # Spec — Motor de Cálculo de Reembolso
       2 
       3 **Versão:** 1.2 · **Status:** rascunho · **Última alteração:** `
         2026-07-31`
       4 
       5 > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
       6 > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
       7 > Se apareceu solução, o lugar dela é o `plan.md`.
       8 >
       9 > **Teste de aceitação da própria spec:** uma pessoa que nunca v
         iu o projeto
      10 > consegue, lendo só este arquivo, verificar se o sistema está c
         orreto?
     … +586 lines

✻ Cooked for 9m 16s

❯ Rejeitei a alteração do spec.md por engano. Realize a alteração novamente     
  seguindo as mesmas alterações.                                                

● Sem problema — vou reaplicar exatamente a mesma alteração no spec.md.

● Write(specs\001-motor-reembolso\spec.md)
  ⎿  Added 258 lines, removed 107 lines
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.1 · **Status:** rascunho · **Última alteração:** `
        -2026-07-30`                                                     
      3 +**Versão:** 1.2 · **Status:** rascunho · **Última alteração:** `
        +2026-07-31`                                                     
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.
     ...
      23  
      24  Dado um conjunto de despesas de um colaborador em uma competênc
          ia, o sistema
      25  decide de forma determinística e auditável o que é reembolsável
          , quanto é
      26 -reembolsável por categoria e por que cada despesa recusada foi 
         -recusada.                                                      
      26 +reembolsável por categoria e por que cada despesa recusada foi 
         +recusada. As                                                   
      27 +categorias válidas, seus limites, o limiar de nota fiscal e o a
         +créscimo de                                                    
      28 +viagem passam a ser lidos de uma **política externa versionada*
         +* e podem variar                                               
      29 +por **centro de custo**.                                       
      30  
      31  ## Clarifications
      32  
     ...
      36  - Q: Entre duplicatas exatas, qual registro é mantido e qual vi
          ra "registro duplicado"? → A: Mantém a primeira ocorrência na o
          rdem do input; as cópias seguintes são as duplicatas.
      37  - Q: Uma despesa com `valor ≤ 0` recusada por um motivo anterio
          r à checagem de valor (ex.: duplicata ou fora da competência co
          m valor negativo) entra em `total_despesas`? → A: Não. A exclus
          ão de `total_despesas` é **por valor**: qualquer despesa com `v
          alor ≤ 0` fica fora da somatória, independentemente do motivo d
          a recusa.
      38  
      39 +### Session 2026-07-31                                         
      40 +                                                               
      41 +- Q: Onde reportar despesas de uma categoria que existe no cent
         +ro de custo mas tem limite ≤ 0 (ex.: hospedagem em `CC-ENG-PLAT
         +AFORMA`, `observacao` "nao reembolsavel")? → A: Sob a própria c
         +ategoria (a categoria aparece no bloco `categorias` com `total_
         +aceito`/`total_reembolso` = 0 e as despesas em `reprovadas[]`).
      42 +- Q: Quando uma despesa de categoria com limite ≤ 0 também viol
         +a outra regra (sem NF, fora do período, etc.), qual motivo prev
         +alece? → A: O motivo de limite ≤ 0 prevalece — a aplicabilidade
         + da categoria (existência + limite > 0) é avaliada logo após a 
         +normalização, antes de duplicata/período/valor/nota fiscal.    
      43 +- Q: Quais categorias aparecem no bloco `categorias` da saída, 
         +agora que cada centro de custo tem seu próprio conjunto? → A: A
         +penas as categorias válidas para o centro de custo que tenham a
         +o menos uma despesa no input; não se emitem blocos zerados para
         + categorias configuradas sem despesas.                         
      44 +                                                               
      45  ## 3. Fora de escopo
      46  
      47  - Não calcula estornos, créditos ou saldos negativos — o sistem
          a só produz
      48    valores de reembolso maiores ou iguais a zero.
      49  - Não valida a autenticidade da nota fiscal; confia no campo `t
          em_nota_fiscal`.
      41 -- Não faz conversão de moeda; todos os valores são em BRL.     
      50 +- Não faz conversão de moeda; todos os valores são em BRL. (A p
         +olítica externa                                                
      51 +  declara `moeda_base` BRL; não há regra de câmbio nesta versão
         +.)                                                             
      52  - Não decide teto por diária individual de hospedagem quando um
           registro agrupa
      43 -  várias diárias (ver AMB-006); o teto é por registro.         
      53 +  várias diárias (ver AMB-006); em categorias de periodicidade 
         +"diaria" o teto é                                              
      54 +  por registro.                                                
      55  - Não trata dias úteis/fins de semana/feriados de forma diferen
          te — não existe
      56    regra de calendário na política.
      57 +- Não valida o conteúdo da política externa além de ler os parâ
         +metros que usa;                                                
      58 +  assume-se que o arquivo de política está bem formado.        
      59  - Não persiste dados nem expõe interface além de ler um input e
           emitir um output.
      60  
      61  ## 4. Entrada e saída
     ...
      67  |---|---|---|---|
      68  | `colaborador.id` | texto | Identificador do colaborador | sim
           |
      69  | `colaborador.nome` | texto | Nome do colaborador | sim |
      57 -| `colaborador.centro_custo` | texto | Centro de custo | sim | 
      70 +| `colaborador.centro_custo` | texto | Centro de custo; determi
         +na o conjunto de categorias e limites via política (RN-015). Se
         + não existir na política, usa o objeto `padrao` | sim |        
      71  | `periodo.competencia` | texto `YYYY-MM` | Rótulo da competênc
          ia | sim |
      72  | `periodo.inicio` | data `YYYY-MM-DD` | Primeiro dia elegível 
          (inclusive) | sim |
      73  | `periodo.fim` | data `YYYY-MM-DD` | Último dia elegível (incl
          usive) | sim |
     ...
       80  | `despesas[].valor` | número | Valor em BRL | sim |
       81  | `despesas[].tem_nota_fiscal` | booleano | Se há nota fiscal 
           anexada | sim |
       82  
       83 +**Política externa (fonte da verdade de categorias e limites):
          +** um arquivo                                                 
       84 +versionado (`politica-v4.json`) fornece, por centro de custo, 
          +o conjunto de                                                 
       85 +categorias reembolsáveis e, para cada categoria, `limite` e `p
          +eriodicidade`                                                 
       86 +(e, opcionalmente, `observacao`). Fornece também os parâmetros
          + globais                                                      
       87 +`nota_fiscal_obrigatoria_acima_de` e `acrescimo_em_viagem_perc
          +entual`. Estrutura                                            
       88 +relevante:                                                    
       89 +                                                              
       90 +| Elemento | Significado |                                    
       91 +|---|---|                                                     
       92 +| `padrao` | Conjunto de categorias/limites usado quando o cen
          +tro de custo do input não existe em `centros_custo` (RN-015) |
       93 +| `centros_custo.<CC>` | Conjunto de categorias/limites especí
          +fico de um centro de custo |                                  
       94 +| `<CC>.<categoria>.limite` | Teto monetário da categoria naqu
          +ele centro. Se ≤ 0, a categoria não é reembolsável (RN-017) | 
       95 +| `<CC>.<categoria>.periodicidade` | `"dia"` (limite sobre a s
          +oma da categoria por dia civil) ou `"diaria"` (limite por regi
          +stro) — ver RN-016 |                                          
       96 +| `<CC>.<categoria>.observacao` | Texto opcional usado como mo
          +tivo quando o limite ≤ 0 (RN-017) |                           
       97 +| `nota_fiscal_obrigatoria_acima_de` | Valor acima do qual a n
          +ota fiscal é obrigatória (RN-006) |                           
       98 +| `acrescimo_em_viagem_percentual` | Percentual de acréscimo a
          +plicado aos limites quando `em_viagem = true` (RN-009) |      
       99 +                                                              
      100  **Saída:** definida por mim. Estrutura e significado de cada c
           ampo:
      101  
      102  | Campo | Tipo | Significado |
     ...
      108  | `periodo.inicio` | data `YYYY-MM-DD` | Primeiro dia elegível
            (eco do input) |
      109  | `periodo.fim` | data `YYYY-MM-DD` | Último dia elegível (eco
            do input) |
      110  | `em_viagem` | booleano | Indicador de viagem aplicado |
      111 +| `categorias.<cat>` | objeto | Um bloco por categoria **válid
          +a para o centro de custo que tenha ao menos uma despesa no inp
          +ut** (ver RN-016, AMB-015). Categorias com limite ≤ 0 também a
          +parecem quando têm despesas, com totais aceito/reembolso zerad
          +os (AMB-014) |                                                
      112  | `categorias.<cat>.total_despesas` | número | Soma do `valor`
            de **todas** as despesas da categoria, aceitas **e** reprovad
           as, **exceto valores ≤ 0** (após arredondamento). Vale a invar
           iante `total_despesas ≥ total_aceito ≥ total_reembolso`. Ver A
           MB-012, RN-014 |
      113  | `categorias.<cat>.total_aceito` | número | Soma do `valor` d
           as despesas **aceitas** da categoria (após arredondamento) |
       83 -| `categorias.<cat>.total_reembolso` | número | Soma efetivame
          -nte reembolsável da categoria (após aplicação de tetos) |     
      114 +| `categorias.<cat>.total_reembolso` | número | Soma efetivame
          +nte reembolsável da categoria (após aplicação de limites) |   
      115  | `categorias.<cat>.reprovadas[]` | lista | Despesas recusadas
            cuja categoria declarada é essa categoria válida, cada uma co
           m `id` e `motivo` |
       85 -| `reprovadas_sem_categoria[]` | lista | Despesas recusadas po
          -r categoria não aplicável (não pertencem a nenhuma categoria v
          -álida), com `id`, `categoria_informada` e `motivo` |          
       86 -| `total_reembolso_geral` | número | Soma de `total_reembolso`
          - das três categorias |                                        
      116 +| `reprovadas_sem_categoria[]` | lista | Despesas recusadas po
          +r categoria não aplicável (categoria que não pertence ao conju
          +nto do centro de custo), com `id`, `categoria_informada` e `mo
          +tivo` |                                                       
      117 +| `total_reembolso_geral` | número | Soma de `total_reembolso`
          + de **todas** as categorias presentes na saída |              
      118  
       88 -Exemplo de saída (para o input de `exemplos/despesas-exemplo.j
          -son`, `em_viagem = false`):                                   
      119 +Exemplo de saída (para o input de `exemplos/despesas-exemplo.j
          +son`, centro de                                               
      120 +custo `CC-ENG-PLATAFORMA`, `em_viagem = false`). Na política v
          +igente esse centro                                            
      121 +tem `alimentacao` limite 75,00 (dia), `transporte_urbano` limi
          +te 80,00 (dia) e                                              
      122 +`hospedagem` limite 0,00 (diaria, `observacao` "nao reembolsav
          +el"):                                                         
      123  
      124  ```json
      125  {
     ...
      138      "alimentacao": {
      139        "total_despesas": 402.83,
      140        "total_aceito": 306.93,
      107 -      "total_reembolso": 255.43,                              
      141 +      "total_reembolso": 271.43,                              
      142        "reprovadas": [
      143          { "id": "d-007", "motivo": "registro duplicado" },
      144          { "id": "d-008", "motivo": "data fora da competência" 
           }
     ...
      155      },
      156      "hospedagem": {
      157        "total_despesas": 1170.00,
      124 -      "total_aceito": 480.00,                                 
      125 -      "total_reembolso": 250.00,                              
      158 +      "total_aceito": 0.00,                                   
      159 +      "total_reembolso": 0.00,                                
      160        "reprovadas": [
      127 -        { "id": "d-013", "motivo": "sem nota fiscal obrigatóri
          -a" }                                                          
      161 +        { "id": "d-010", "motivo": "nao reembolsavel" },      
      162 +        { "id": "d-013", "motivo": "nao reembolsavel" }       
      163        ]
      164      }
      165    },
      166    "reprovadas_sem_categoria": [
      167      { "id": "d-005", "categoria_informada": "coworking", "moti
           vo": "categoria não aplicável" }
      168    ],
      134 -  "total_reembolso_geral": 585.43                             
      169 +  "total_reembolso_geral": 351.43                             
      170  }
      171  ```
      172  
      173  > **Nota sobre `total_despesas`:** inclui o `valor` de despesa
           s reprovadas por
      139 -> duplicidade, fora da competência e sem nota fiscal — desde q
          -ue a categoria                                                
      140 -> declarada seja uma categoria válida. **Valores ≤ 0 (estornos
          - / "valor inválido")                                          
      141 -> não entram na somatória**, assim como despesas de categoria 
          -não aplicável e                                               
      174 +> duplicidade, fora da competência, sem nota fiscal e por limi
          +te ≤ 0                                                        
      175 +> ("nao reembolsavel") — desde que a categoria declarada seja 
          +uma categoria                                                 
      176 +> válida do centro de custo. **Valores ≤ 0 (estornos / "valor 
          +inválido") não                                                
      177 +> entram na somatória**, assim como despesas de categoria não 
          +aplicável e                                                   
      178  > registros estruturalmente inválidos (esses vão para `reprova
           das_sem_categoria`).
      179  > Por isso, em `transporte_urbano`, o estorno `d-009` (−45,00)
            **não** entra:
      144 -> 100,00 + 100,01 = 200,01.                                   
      180 +> 100,00 + 100,01 = 200,01. Em `hospedagem`, os dois registros
          + são reprovados                                               
      181 +> por "nao reembolsavel" mas seus valores (> 0) somam `total_d
          +espesas` = 1170,00                                            
      182 +> com `total_aceito` e `total_reembolso` = 0,00.              
      183 +>                                                             
      184 +> **Nota sobre o exemplo x versão anterior:** com `CC-ENG-PLAT
          +AFORMA` na política                                           
      185 +> v4, o teto diário de alimentação passou de 60,00 para 75,00 
          +(07-03: 110,50 →                                              
      186 +> reembolso 75,00; 07-31: 61,00 → reembolso 61,00) e hospedage
          +m ficou não                                                   
      187 +> reembolsável (limite 0,00), reduzindo `total_reembolso_geral
          +` de 585,43 para                                              
      188 +> 351,43.                                                     
      189  
      190  ---
      191  
     ...
      193  
      194  Cada regra recebe um ID (`RN-001`, ...). As tasks vão referenc
           iar esses IDs.
      195  
      152 -### RN-001 — Categorias válidas                               
      153 -**Regra:** Só existem três categorias reembolsáveis: `alimenta
          -cao`,                                                         
      154 -`transporte_urbano` e `hospedagem`. A comparação é feita sem d
          -iferenciar                                                    
      155 -maiúsculas/minúsculas e após remover espaços nas pontas (ver A
          -MB-003). Qualquer                                             
      156 -outra categoria é "categoria não aplicável" e não é reembolsáv
          -el.                                                           
      157 -**Origem:** política do RH, item "Categorias fora da política 
          -não são reembolsáveis".                                       
      158 -**Aceite:** `coworking` é recusada com motivo "categoria não a
          -plicável"; `ALIMENTACAO`                                      
      159 -é tratada como `alimentacao`.                                 
      196 +### RN-015 — Política externa e resolução de centro de custo  
      197 +**Regra:** As categorias reembolsáveis, seus limites, sua peri
          +odicidade, o limiar                                           
      198 +de nota fiscal e o acréscimo de viagem são lidos de uma políti
          +ca externa                                                    
      199 +versionada, não codificados na regra. Para um input, resolve-s
          +e o conjunto                                                  
      200 +aplicável assim: se `colaborador.centro_custo` existe em `cent
          +ros_custo`, usa-se                                            
      201 +o objeto daquele centro; caso contrário, usa-se o objeto `padr
          +ao`. Os parâmetros                                            
      202 +globais `nota_fiscal_obrigatoria_acima_de` e `acrescimo_em_via
          +gem_percentual`                                               
      203 +valem para qualquer centro.                                   
      204 +**Origem:** nova política de centros de custo (2026-07-31).   
      205 +**Aceite:** um input com `centro_custo` inexistente na polític
          +a é avaliado pelos                                            
      206 +limites de `padrao` (alimentacao 60,00/dia, transporte 80,00/d
          +ia, hospedagem                                                
      207 +250,00/diaria).                                               
      208  
      161 -### RN-002 — Teto diário de alimentação                       
      162 -**Regra:** O teto de `alimentacao` é R$ 60,00 por dia civil, s
          -omando **todas** as                                           
      163 -despesas aceitas da categoria naquele dia. O excedente não é r
          -eembolsado; o                                                 
      164 -reembolso do dia é `min(soma_do_dia, teto)`.                  
      165 -**Origem:** política do RH, "Alimentação tem limite de R$ 60 p
          -or dia" + "Despesas acima do limite são reembolsadas parcialme
          -nte".                                                         
      166 -**Aceite:** 72,50 + 38,00 no mesmo dia → total aceito 110,50, 
          -reembolso 60,00.                                              
      209 +### RN-016 — Periodicidade do limite                          
      210 +**Regra:** Cada categoria tem uma `periodicidade` na política 
          +que define **como** o                                         
      211 +limite incide:                                                
      212 +- `"dia"`: o limite incide sobre a **soma das despesas aceitas
          + da categoria no                                              
      213 +  mesmo dia civil**; reembolso do dia = `min(soma_do_dia, limi
          +te)`. Ex.:                                                    
      214 +  `alimentacao`, `transporte_urbano` (e `representacao` onde e
          +xistir).                                                      
      215 +- `"diaria"`: o limite incide sobre **cada registro individual
          +mente**; reembolso                                            
      216 +  do registro = `min(valor, limite)`. Ex.: `hospedagem`.      
      217 +**Origem:** nova política de centros de custo (2026-07-31).   
      218 +**Aceite:** categoria "dia" com 100,00 + 100,01 no mesmo dia e
          + limite 80,00 →                                               
      219 +reembolso do dia 80,00; categoria "diaria" com dois registros 
          +de 200,00 e limite                                            
      220 +250,00 → reembolso 200,00 + 200,00 (cada registro sob seu próp
          +rio teto).                                                    
      221  
      168 -### RN-003 — Teto diário de transporte urbano                 
      169 -**Regra:** O teto de `transporte_urbano` é R$ 80,00 por dia ci
          -vil, somando todas                                            
      170 -as despesas aceitas da categoria naquele dia. Reembolso do dia
          - = `min(soma_do_dia, teto)`.                                  
      171 -**Origem:** política do RH, "Transporte urbano tem limite de R
          -$ 80 por dia".                                                
      172 -**Aceite:** uma corrida aceita de 100,00 no dia → reembolso 80
          -,00.                                                          
      222 +### RN-017 — Categoria com limite ≤ 0 (não reembolsável)      
      223 +**Regra:** Se, para o centro de custo resolvido, a categoria e
          +xiste mas seu                                                 
      224 +`limite` é **menor ou igual a zero**, toda despesa dessa categ
          +oria é recusada com                                           
      225 +reembolso 0. O `motivo` é o valor de `observacao` da categoria
          +; se não houver                                               
      226 +`observacao`, o motivo é "categoria não aplicável". Essas desp
          +esas são reportadas                                           
      227 +**sob a própria categoria** (`categorias.<cat>.reprovadas[]`) 
          +e a categoria                                                 
      228 +aparece na saída com `total_aceito` = 0 e `total_reembolso` = 
          +0 (mas                                                        
      229 +`total_despesas` soma os valores > 0). Esta checagem é avaliad
          +a logo após a                                                 
      230 +validade da categoria e **antes** de duplicata, período, valor
          + e nota fiscal                                                
      231 +(ver AMB-014, Seção 8).                                       
      232 +**Origem:** nova política de centros de custo (2026-07-31).   
      233 +**Aceite:** em `CC-ENG-PLATAFORMA` (hospedagem limite 0,00, `o
          +bservacao`                                                    
      234 +"nao reembolsavel"), `d-010` e `d-013` são recusados com motiv
          +o "nao reembolsavel"                                          
      235 +sob `hospedagem`, mesmo `d-013` estando sem nota fiscal.      
      236  
      237 +### RN-001 — Categorias válidas por centro de custo           
      238 +**Regra:** As categorias reembolsáveis são exatamente as **cha
          +ves do conjunto do                                            
      239 +centro de custo resolvido** na política (RN-015) — não mais um
          + conjunto fixo. A                                             
      240 +comparação da categoria declarada é feita sem diferenciar maiú
          +sculas/minúsculas e                                           
      241 +após remover espaços nas pontas (ver AMB-003). Qualquer catego
          +ria declarada que                                             
      242 +não esteja nesse conjunto é "categoria não aplicável", não é r
          +eembolsável e vai                                             
      243 +para `reprovadas_sem_categoria`.                              
      244 +**Origem:** política do RH + nova política de centros de custo
          + (2026-07-31).                                                
      245 +**Aceite:** em `CC-ENG-PLATAFORMA`, `coworking` é recusada "ca
          +tegoria não                                                   
      246 +aplicável"; `ALIMENTACAO` é tratada como `alimentacao`. Em `CC
          +-ADM` (sem                                                    
      247 +`hospedagem` no conjunto), uma despesa de `hospedagem` é "cate
          +goria não aplicável".                                         
      248 +                                                              
      249 +### RN-002 — Teto de alimentação                              
      250 +**Regra:** `alimentacao` tem periodicidade "dia" (RN-016): o t
          +eto (o `limite` da                                            
      251 +categoria na política do centro de custo) incide sobre a soma 
          +das despesas                                                  
      252 +aceitas da categoria no dia civil. O excedente não é reembolsa
          +do; o reembolso do                                            
      253 +dia é `min(soma_do_dia, limite)`. No conjunto `padrao` o limit
          +e é R$ 60,00.                                                 
      254 +**Origem:** política do RH, "Alimentação tem limite por dia" +
          + "Despesas acima do limite são reembolsadas parcialmente"; val
          +or vindo da política externa (RN-015).                        
      255 +**Aceite:** em `CC-ENG-PLATAFORMA` (limite 75,00), 72,50 + 38,
          +00 no mesmo dia →                                             
      256 +total aceito 110,50, reembolso 75,00.                         
      257 +                                                              
      258 +### RN-003 — Teto de transporte urbano                        
      259 +**Regra:** `transporte_urbano` tem periodicidade "dia" (RN-016
          +): o teto (o                                                  
      260 +`limite` da categoria na política do centro de custo) incide s
          +obre a soma das                                               
      261 +despesas aceitas da categoria no dia civil. Reembolso do dia =
          + `min(soma_do_dia, limite)`.                                  
      262 +No conjunto `padrao` o limite é R$ 80,00.                     
      263 +**Origem:** política do RH, "Transporte urbano tem limite por 
          +dia"; valor vindo da política externa (RN-015).               
      264 +**Aceite:** com limite 80,00, uma corrida aceita de 100,00 no 
          +dia → reembolso 80,00.                                        
      265 +                                                              
      266  ### RN-004 — Teto de hospedagem por registro
      175 -**Regra:** O teto de `hospedagem` é R$ 250,00 **por registro**
          -, independente da                                             
      176 -quantidade de diárias que o registro declare ou de quantos reg
          -istros houver no                                              
      177 -dia. Reembolso do registro = `min(valor, teto)`.              
      178 -**Origem:** política do RH, "Hospedagem tem limite de R$ 250 p
          -or diária" (reinterpretado — ver AMB-006).                    
      179 -**Aceite:** registro de 480,00 ("2 diárias") → reembolso 250,0
          -0.                                                            
      267 +**Regra:** `hospedagem` tem periodicidade "diaria" (RN-016): o
          + teto (o `limite`                                             
      268 +da categoria na política do centro de custo) incide **por regi
          +stro**,                                                       
      269 +independente da quantidade de diárias que o registro declare o
          +u de quantos                                                  
      270 +registros houver no dia. Reembolso do registro = `min(valor, l
          +imite)`. No                                                   
      271 +conjunto `padrao` o limite é R$ 250,00.                       
      272 +**Origem:** política do RH, "Hospedagem tem limite por diária"
          + (reinterpretado — ver AMB-006); valor vindo da política exter
          +na (RN-015).                                                  
      273 +**Aceite:** com limite 250,00, registro de 480,00 ("2 diárias"
          +) → reembolso 250,00.                                         
      274  
      275  ### RN-005 — Reembolso parcial no teto
      276  **Regra:** Quando o valor aceito ultrapassa o teto aplicável, 
           reembolsa-se apenas
     ...
      280  **Aceite:** ver RN-002/003/004.
      281  
      282  ### RN-006 — Nota fiscal obrigatória
      189 -**Regra:** Nota fiscal é obrigatória para valores **estritamen
          -te acima** de                                                 
      190 -R$ 100,00. Em R$ 100,00 exatos não é necessária. Se obrigatóri
          -a e ausente                                                   
      283 +**Regra:** Nota fiscal é obrigatória para valores **estritamen
          +te acima** do                                                 
      284 +parâmetro `nota_fiscal_obrigatoria_acima_de` da política (R$ 1
          +00,00 na v4). No                                              
      285 +valor exato do limiar não é necessária. Se obrigatória e ausen
          +te                                                            
      286  (`tem_nota_fiscal = false`), a despesa é recusada com motivo "
           sem nota fiscal
      287  obrigatória" e reembolsa 0 (ver AMB-004).
      193 -**Origem:** política do RH, "Nota fiscal é obrigatória acima d
          -e R$ 100".                                                    
      194 -**Aceite:** 100,00 sem NF → aceita; 100,01 sem NF → recusada. 
      288 +**Origem:** política do RH, "Nota fiscal é obrigatória acima d
          +e um valor base"; valor vindo da política externa (RN-015).   
      289 +**Aceite:** com limiar 100,00: 100,00 sem NF → aceita; 100,01 
          +sem NF → recusada.                                            
      290  
      291  ### RN-007 — Período de competência
      292  **Regra:** Só são elegíveis despesas cuja `data` esteja no int
           ervalo
     ...
      305  **Aceite:** `d-006` e `d-007` (idênticos exceto `id`) → `d-006
           ` (primeiro) é aceito, `d-007` é "registro duplicado".
      306  
      307  ### RN-009 — Limites ampliados em viagem
      213 -**Regra:** Se `em_viagem = true`, os tetos das três categorias
          - são multiplicados                                            
      214 -por 1,5 (alimentação 90,00/dia; transporte 120,00/dia; hospeda
          -gem 375,00/registro).                                         
      215 -O limiar de nota fiscal (R$ 100,00) **não** é ampliado. O indi
          -cador vale para                                               
      216 -todas as despesas do input (ver AMB-008).                     
      217 -**Origem:** política do RH, "Colaborador em viagem tem limites
          - ampliados em 50%".                                           
      218 -**Aceite:** em viagem, alimentação de 85,00 num dia → reembols
          -o 85,00 (dentro de 90).                                       
      308 +**Regra:** Se `em_viagem = true`, os limites de **todas as cat
          +egorias** do centro                                           
      309 +de custo são multiplicados por `(1 + acrescimo_em_viagem_perce
          +ntual / 100)` (na                                             
      310 +v4, +50% → ×1,5). O limiar de nota fiscal **não** é ampliado. 
          +Uma categoria com                                             
      311 +limite ≤ 0 permanece não reembolsável (0 × qualquer fator = 0)
          +. O indicador vale                                            
      312 +para todas as despesas do input (ver AMB-008).                
      313 +**Origem:** política do RH, "Colaborador em viagem tem limites
          + ampliados"; percentual vindo da política externa (RN-015).   
      314 +**Aceite:** em viagem, `CC-ENG-PLATAFORMA` alimentação 75,00 →
          + 112,50; transporte                                           
      315 +80,00 → 120,00; hospedagem 0,00 → 0,00 (permanece não reembols
          +ável); limiar de NF                                           
      316 +continua 100,00.                                              
      317  
      318  ### RN-010 — Valores inválidos
      319  **Regra:** Valor menor ou igual a zero é inválido; a despesa é
            recusada com
     ...
      342  ### RN-012 — Agregação por categoria
      343  **Regra:** A saída ecoa os dados de identificação do input — `
           colaborador` (`id`,
      344  `nome`, `centro_custo`), `competencia` e `periodo` (`inicio`, 
           `fim`). Para cada
      247 -categoria válida o sistema reporta: `total_despesas` (soma do 
          -`valor` de todas as                                           
      248 -despesas da categoria, aceitas e reprovadas, exceto valores ≤ 
          -0 — ver RN-014), `total_aceito` (soma                         
      249 -do `valor` das despesas aceitas), `total_reembolso` (soma reem
          -bolsável após tetos)                                          
      250 -e a lista de despesas recusadas daquela categoria com motivo. 
          -Recusas por                                                   
      251 -categoria não aplicável vão para `reprovadas_sem_categoria` (v
          -er AMB-011).                                                  
      345 +categoria válida do centro de custo **que tenha ao menos uma d
          +espesa no input**                                             
      346 +(ver AMB-015) o sistema reporta: `total_despesas` (soma do `va
          +lor` de todas as                                              
      347 +despesas da categoria, aceitas e reprovadas, exceto valores ≤ 
          +0 — ver RN-014),                                              
      348 +`total_aceito` (soma do `valor` das despesas aceitas), `total_
          +reembolso` (soma                                              
      349 +reembolsável após limites) e a lista de despesas recusadas daq
          +uela categoria com                                            
      350 +motivo. Recusas por categoria não aplicável vão para `reprovad
          +as_sem_categoria`                                             
      351 +(ver AMB-011). `total_reembolso_geral` é a soma de `total_reem
          +bolso` de todas as                                            
      352 +categorias presentes.                                         
      353  **Origem:** requisito de saída do desafio.
      354  **Aceite:** ver exemplo da Seção 4.
      355  
      356  ### RN-014 — Total de despesas por categoria
      357  **Regra:** `total_despesas` de uma categoria é a soma do `valo
           r` (já arredondado)
      358  de todas as despesas cuja categoria normalizada é aquela — ace
           itas e reprovadas
      258 -(duplicidade, fora da competência, sem nota fiscal) — **exceto
          - valores ≤ 0, que                                             
      259 -nunca entram na somatória, independentemente do motivo da recu
          -sa** (a exclusão é                                            
      260 -por valor, não por motivo). Despesas de categoria não aplicáve
          -l e registros                                                 
      261 -estruturalmente inválidos também não entram (não pertencem a c
          -ategoria válida).                                             
      262 -Vale sempre `total_despesas ≥ total_aceito ≥ total_reembolso` 
          -(ver AMB-012).                                                
      359 +(duplicidade, fora da competência, sem nota fiscal, limite ≤ 0
          +) — **exceto                                                  
      360 +valores ≤ 0, que nunca entram na somatória, independentemente 
          +do motivo da recusa**                                         
      361 +(a exclusão é por valor, não por motivo). Despesas de categori
          +a não aplicável e                                             
      362 +registros estruturalmente inválidos também não entram (não per
          +tencem a categoria                                            
      363 +válida). Vale sempre `total_despesas ≥ total_aceito ≥ total_re
          +embolso` (ver AMB-012).                                       
      364  **Origem:** requisito de saída (esclarecimento do usuário, 202
           6-07-30; revisto em
      365  2026-07-30, ver DECISIONS D-004).
      366  **Aceite:** em `transporte_urbano` do exemplo: 100,00 + 100,01
            = 200,01 (o estorno
     ...
      374  > registro aqui conta como não resolvida.
      375  
      376  ### AMB-001 — Como distribuir o teto diário entre várias despe
           sas do mesmo dia
      276 -**Texto original do RH:** "Alimentação tem limite de R$ 60 por
          - dia." + "Despesas acima do limite são reembolsadas parcialmen
          -te."                                                          
      377 +**Texto original do RH:** "Alimentação tem limite por dia." + 
          +"Despesas acima do limite são reembolsadas parcialmente."     
      378  **O que não está claro:** com duas despesas no mesmo dia soman
           do mais que o teto, reembolsa-se por despesa (e nesse caso, em
            que ordem?) ou agrega-se o dia?
      278 -**Decisão:** o teto incide sobre o **agregado do dia** por cat
          -egoria. Reembolso do dia = `min(soma das aceitas do dia, teto)
          -`. Como a saída é por categoria, não é preciso ratear por desp
          -esa individual.                                               
      379 +**Decisão:** o teto de categorias com periodicidade "dia" inci
          +de sobre o **agregado do dia** por categoria. Reembolso do dia
          + = `min(soma das aceitas do dia, limite)`. Como a saída é por 
          +categoria, não é preciso ratear por despesa individual.       
      380  **Justificativa:** o limite da política é diário, não por desp
           esa; agregar evita depender de ordenação arbitrária.
      280 -**Regra afetada:** RN-002, RN-003, RN-005.                    
      381 +**Regra afetada:** RN-002, RN-003, RN-005, RN-016.            
      382  
      383  ### AMB-002 — O campo `id` conta para definir duplicidade?
      384  **Texto original do RH:** "Duplicatas devem ser tratadas." (de
           cisão recebida: "todos os campos iguais")
     ...
      390  ### AMB-003 — Categoria com caixa diferente (`ALIMENTACAO`)
      391  **Texto original do RH:** lista de categorias em minúsculas; `
           d-014` vem como `ALIMENTACAO`.
      392  **O que não está claro:** `ALIMENTACAO` é a categoria válida o
           u uma categoria "diferente" e portanto não aplicável?
      292 -**Decisão:** comparação **sem diferenciar caixa** e com _trim_
          -; `ALIMENTACAO` é tratada como `alimentacao`.                 
      393 +**Decisão:** comparação **sem diferenciar caixa** e com _trim_
          +; `ALIMENTACAO` é tratada como `alimentacao`. As chaves de cat
          +egoria da política são comparadas do mesmo modo.              
      394  **Justificativa:** caixa é formatação de digitação, não distin
           ção de negócio; punir o colaborador por maiúscula seria arbitr
           ário.
      395  **Alternativa considerada:** correspondência estrita (recusari
           a `d-014` como categoria não aplicável) — descartada por ser u
           m artefato de digitação.
      396  **Regra afetada:** RN-001.
      397  
      398  ### AMB-004 — Falta de nota fiscal: recusa ou apenas não reemb
           olsa?
      298 -**Texto original do RH:** "Nota fiscal é obrigatória acima de 
          -R$ 100."                                                      
      399 +**Texto original do RH:** "Nota fiscal é obrigatória acima de 
          +um valor base."                                               
      400  **O que não está claro:** a lista de motivos de recusa do desa
           fio não inclui "sem nota fiscal"; o que fazer com `d-004` e `d
           -013`?
      401  **Decisão:** falta de NF obrigatória **recusa** a despesa (mot
           ivo "sem nota fiscal obrigatória"), reembolso 0, e ela não ent
           ra em `total_aceito`. A lista de motivos do enunciado é ilustr
           ativa, não exaustiva.
      402  **Justificativa:** sem documento fiscal a empresa não pode ree
           mbolsar legalmente.
     ...
      410  **Regra afetada:** RN-010.
      411  
      412  ### AMB-006 — Hospedagem: "por diária" vs. "por registro"
      312 -**Texto original do RH:** "Hospedagem tem limite de R$ 250 por
          - diária." (decisão recebida: "250 por registro")              
      313 -**O que não está claro:** um registro de 480,00 dizendo "2 diá
          -rias" deveria ter teto de 500 (2×250) ou 250?                 
      314 -**Decisão:** teto de **R$ 250 por registro**, conforme decisão
          - recebida, independentemente de quantas diárias o texto mencio
          -ne. `d-010` reembolsa 250,00.                                 
      413 +**Texto original do RH:** "Hospedagem tem limite por diária." 
          +(decisão recebida: "por registro")                            
      414 +**O que não está claro:** um registro de 480,00 dizendo "2 diá
          +rias" deveria ter teto de 2× o limite ou 1×?                  
      415 +**Decisão:** para categorias de periodicidade "diaria", o teto
          + é **por registro** (`min(valor, limite)`), independentemente 
          +de quantas diárias o texto mencione. `d-010` reembolsa `min(48
          +0,00, limite)`.                                               
      416  **Justificativa:** o input não traz número de diárias de forma
            estruturada e confiável; contar diárias a partir da descrição
            seria adivinhação. Divergência da letra do RH registrada em `
           DECISIONS.md`.
      316 -**Regra afetada:** RN-004.                                    
      417 +**Regra afetada:** RN-004, RN-016.                            
      418  
      419  ### AMB-007 — Precisão e arredondamento monetário (`33,333`)
      420  **Texto original do RH:** nada sobre casas decimais.
     ...
      424  **Regra afetada:** RN-011.
      425  
      426  ### AMB-008 — Onde e como o indicador de viagem é informado, e
            o que ele amplia
      326 -**Texto original do RH:** "Colaborador em viagem tem limites a
          -mpliados em 50%." (decisões: usuário informa; inputs separados
          -; se em viagem, todas as despesas do input são em viagem)     
      427 +**Texto original do RH:** "Colaborador em viagem tem limites a
          +mpliados." (decisões: usuário informa; inputs separados; se em
          + viagem, todas as despesas do input são em viagem)            
      428  **O que não está claro:** o exemplo não tem campo de viagem; o
           nde ele fica e se o limiar de NF também escala.
      328 -**Decisão:** indicador é um campo booleano de topo `em_viagem`
          - (default `false`), válido para todo o input; amplia em 50% **
          -apenas os três tetos de categoria**; o limiar de R$ 100 de NF 
          -**não** escala. O exemplo representa uma competência sem viage
          -m.                                                            
      429 +**Decisão:** indicador é um campo booleano de topo `em_viagem`
          + (default `false`), válido para todo o input; amplia os limite
          +s de categoria pelo percentual `acrescimo_em_viagem_percentual
          +`; o limiar de NF **não** escala. O exemplo representa uma com
          +petência sem viagem.                                          
      430  **Justificativa:** viagem amplia a tolerância de gasto, não a 
           obrigação fiscal.
      431  **Regra afetada:** RN-009, RN-006.
      432  
     ...
      439  
      440  ### AMB-010 — Precedência quando uma despesa viola várias regr
           as
      441  **Texto original do RH:** implícito — regras coexistem.
      341 -**O que não está claro:** `d-013` está no período mas é sem NF
          - e acima do teto; qual motivo reportar?                       
      342 -**Decisão:** ordem fixa de avaliação (Seção 8); o **primeiro**
          - portão que falha determina o motivo. Teto só se aplica a desp
          -esas já aceitas.                                              
      442 +**O que não está claro:** `d-013` está no período mas é hosped
          +agem não reembolsável e também sem NF; qual motivo reportar?  
      443 +**Decisão:** ordem fixa de avaliação (Seção 8); o **primeiro**
          + portão que falha determina o motivo. A aplicabilidade da cate
          +goria (existência + limite > 0) vem antes de duplicata/período
          +/valor/NF; o teto só se aplica a despesas já aceitas.         
      444  **Justificativa:** determinismo e auditabilidade — o mesmo inp
           ut sempre produz o mesmo motivo.
      344 -**Regra afetada:** RN-001..RN-011 (ordem de aplicação).       
      445 +**Regra afetada:** RN-001..RN-017 (ordem de aplicação).       
      446  
      447  ### AMB-011 — Onde reportar recusas de categoria não aplicável
      448  **Texto original do RH:** "para cada categoria válida ... desp
           esas reprovadas".
      449  **O que não está claro:** uma despesa de `coworking` recusada 
           não pertence a nenhuma categoria válida; sob qual categoria li
           stá-la?
      349 -**Decisão:** despesas recusadas por categoria não aplicável vã
          -o para uma lista separada `reprovadas_sem_categoria`; recusas 
          -de despesas com categoria válida (ex.: sem NF) ficam sob a res
          -pectiva categoria.                                            
      450 +**Decisão:** despesas recusadas por categoria não aplicável vã
          +o para uma lista separada `reprovadas_sem_categoria`; recusas 
          +de despesas com categoria válida (ex.: sem NF, limite ≤ 0) fic
          +am sob a respectiva categoria.                                
      451  **Justificativa:** manter a saída por categoria válida coerent
           e, sem inventar uma categoria "outras" reembolsável.
      351 -**Regra afetada:** RN-012.                                    
      452 +**Regra afetada:** RN-012, RN-017.                            
      453  
      454  ### AMB-012 — `total_despesas`: valor monetário ou contagem?
      455  **Texto original do usuário:** "inclua total_despesas, sendo o
            total de despesas incluindo aceitas e reprovadas".
     ...
      459  **Alternativa considerada:** contagem de despesas — descartada
            por quebrar a consistência de unidade com os campos vizinhos 
           (seria melhor nomeada `quantidade_despesas`).
      460  **Regra afetada:** RN-012, RN-014.
      461  
      462 +### AMB-013 — Centro de custo ausente na política             
      463 +**Texto original da nova regra:** "Caso o centro de custo envi
          +ado no input não existir no objeto `centros_custo`, deve segui
          +r a regra do objeto `padrao`."                                
      464 +**O que não está claro:** o que acontece com um centro de cust
          +o desconhecido — erro, sem reembolso, ou fallback?            
      465 +**Decisão:** usa-se o objeto `padrao` da política (categorias,
          + limites e periodicidades ali definidos). Não há erro; a avali
          +ação segue normalmente com o conjunto padrão.                 
      466 +**Justificativa:** a nova política define explicitamente `padr
          +ao` como o comportamento de fallback.                         
      467 +**Regra afetada:** RN-015.                                    
      468 +                                                              
      469 +### AMB-014 — Categoria com limite ≤ 0: onde reportar e qual a
          + precedência                                                  
      470 +**Texto original da nova regra:** "Se o limite de uma categori
          +a for menor ou igual a zero, deve considerar como reembolso ne
          +gado e o campo `motivo` da saída deve ser o parâmetro `observa
          +cao` da categoria, caso não exista observacao, motivo deve ser
          + 'categoria não aplicável'."                                  
      471 +**O que não está claro:** (a) essas despesas ficam sob a própr
          +ia categoria ou em `reprovadas_sem_categoria`? (b) o motivo de
          + limite ≤ 0 prevalece sobre outros motivos (sem NF, fora do pe
          +ríodo)?                                                       
      472 +**Decisão:** (a) ficam **sob a própria categoria** (`categoria
          +s.<cat>.reprovadas[]`), e a categoria aparece na saída com `to
          +tal_aceito`/`total_reembolso` = 0; (b) o motivo de limite ≤ 0 
          +**prevalece** — a aplicabilidade da categoria (existência + li
          +mite > 0) é avaliada logo após a normalização, antes de duplic
          +ata/período/valor/NF (esclarecimento 2026-07-31).             
      473 +**Justificativa:** a categoria está configurada para o centro 
          +de custo (só que zerada), então pertence ao conjunto válido; e
          + "não reembolsável" é uma propriedade da categoria, que deve s
          +er reportada antes de detalhes por registro.                  
      474 +**Alternativa considerada:** reportar em `reprovadas_sem_categ
          +oria` — descartada por a categoria de fato existir no conjunto
          + do centro de custo.                                          
      475 +**Regra afetada:** RN-017, RN-012, RN-014.                    
      476 +                                                              
      477 +### AMB-015 — Quais categorias aparecem no bloco `categorias` 
      478 +**Texto original da nova regra:** cada centro de custo pode te
          +r categorias diferentes.                                      
      479 +**O que não está claro:** o bloco `categorias` da saída lista 
          +todas as categorias configuradas no centro de custo (mesmo sem
          + despesas) ou só as que têm despesas?                         
      480 +**Decisão:** só aparecem as categorias válidas do centro de cu
          +sto **que tenham ao menos uma despesa no input**; não se emite
          +m blocos zerados para categorias configuradas sem despesas (ex
          +.: `representacao` em `CC-COMERCIAL` sem lançamentos não apare
          +ce) — esclarecimento 2026-07-31.                              
      481 +**Justificativa:** mantém o comportamento anterior (a saída re
          +flete o que foi lançado) e evita ruído de blocos vazios.      
      482 +**Regra afetada:** RN-012.                                    
      483 +                                                              
      484  ---
      485  
      486  ## 7. Casos de borda
      487  
      488  | Caso | Entrada (exemplo) | Comportamento esperado | Regra |
      489  |---|---|---|---|
      367 -| Soma diária excede teto | `d-001` 72,50 + `d-002` 38,00 (ali
          -mentação, mesmo dia) | aceito 110,50; reembolso 60,00 | RN-002
          -, RN-005 |                                                    
      490 +| Soma diária excede teto | `d-001` 72,50 + `d-002` 38,00 (ali
          +mentação, mesmo dia, `CC-ENG-PLATAFORMA` limite 75) | aceito 1
          +10,50; reembolso 75,00 | RN-002, RN-005, RN-016 |             
      491  | Valor exatamente no limiar de NF | `d-003` 100,00 sem NF | a
           ceita (NF não obrigatória) | RN-006 |
      492  | Valor um centavo acima do limiar | `d-004` 100,01 sem NF | r
           ecusada "sem nota fiscal obrigatória" | RN-006 |
      370 -| Categoria fora da política | `d-005` `coworking` | recusada 
          -"categoria não aplicável" em `reprovadas_sem_categoria` | RN-0
          -01, RN-012 |                                                  
      493 +| Categoria fora do conjunto do centro | `d-005` `coworking` |
          + recusada "categoria não aplicável" em `reprovadas_sem_categor
          +ia` | RN-001, RN-012 |                                        
      494 +| Categoria com limite ≤ 0 | `d-010`/`d-013` `hospedagem` em `
          +CC-ENG-PLATAFORMA` (limite 0, obs. "nao reembolsavel") | recus
          +adas "nao reembolsavel" sob `hospedagem`; total_aceito/reembol
          +so 0 | RN-017, AMB-014 |                                      
      495 +| Categoria válida só em alguns centros | `representacao` em `
          +CC-COMERCIAL` | reembolsável em `CC-COMERCIAL`; "categoria não
          + aplicável" nos demais | RN-001, RN-015 |                     
      496 +| Centro de custo desconhecido | `centro_custo` inexistente na
          + política | avaliado pelos limites de `padrao` | RN-015 |     
      497  | Duplicata (só o `id` difere) | `d-006`/`d-007` | uma aceita,
            a outra "registro duplicado" | RN-008 |
      498  | Data fora do período | `d-008` 2026-04-15 | recusada "data f
           ora da competência" | RN-007 |
      499  | Valor negativo | `d-009` -45,00 | recusada "valor inválido" 
           | RN-010 |
      500  | Registro malformado | despesa sem `data` ou `valor` não numé
           rico | recusada "registro inválido" em `reprovadas_sem_categor
           ia`; demais processados | RN-013 |
      375 -| Hospedagem acima do teto (várias diárias num registro) | `d-
          -010` 480,00 | aceito 480,00; reembolso 250,00 | RN-004 |      
      501 +| Hospedagem acima do teto (várias diárias num registro) | `d-
          +010` 480,00 num centro com limite 250 | aceito 480,00; reembol
          +so 250,00 | RN-004, RN-016 |                                  
      502  | Mais de 2 casas decimais | `d-011` 33,333 | arredonda para 3
           3,33 | RN-011 |
      503  | Fim de semana | `d-012` sábado 47,20 | tratado como qualquer
            dia (sem regra de calendário) | Seção 3 |
      378 -| Categoria em caixa alta | `d-014` `ALIMENTACAO` 61,00 | trat
          -ada como `alimentacao`; teto 60 → reembolso 60,00 | RN-001, RN
          --002 |                                                        
      379 -| Data igual a `fim` | `d-014` 2026-07-31 | elegível (limite i
          -nclusivo) | RN-009 |                                          
      504 +| Categoria em caixa alta | `d-014` `ALIMENTACAO` 61,00 | trat
          +ada como `alimentacao` | RN-001 |                             
      505 +| Data igual a `fim` | `d-014` 2026-07-31 | elegível (limite i
          +nclusivo) | RN-007, RN-009 (AMB-009) |                        
      506  | Despesa aceita mas com reembolso 0 por teto já consumido | 3
           ª despesa de alimentação num dia já no teto | permanece **acei
           ta** (entra em `total_aceito`), reembolso 0 | RN-005 |
      507 +| Limites ampliados em viagem | `em_viagem = true`, alimentaçã
          +o 85,00 num dia (limite 75 → 112,50) | reembolso 85,00 | RN-00
          +9 |                                                           
      508  
      509  ## 8. Ordem de aplicação das regras
      510  
     ...
      514  1. **Validação estrutural** — campos obrigatórios presentes e 
           tipados, `valor`
      515     numérico, `data` parseável; senão "registro inválido" (RN-0
           13). Se o JSON de
      516     topo não parseia, aborta a execução.
      390 -2. **Normalização** — arredondar `valor` para 2 casas (RN-011)
          -; aplicar `trim`                                              
      391 -   e caixa na `categoria` (RN-001); aplicar multiplicador de v
          -iagem aos tetos se                                            
      517 +2. **Resolução da política** — resolver o centro de custo (o d
          +o input ou                                                    
      518 +   `padrao`) e carregar categorias, limites, periodicidades e 
          +parâmetros globais                                            
      519 +   (RN-015).                                                  
      520 +3. **Normalização** — arredondar `valor` para 2 casas (RN-011)
          +; aplicar `trim` e                                            
      521 +   caixa na `categoria` (RN-001); aplicar o acréscimo de viage
          +m aos limites se                                              
      522     `em_viagem` (RN-009).
      393 -3. **Deduplicação** — colapsar registros idênticos por campos 
          -de negócio,                                                   
      523 +4. **Categoria válida** — a categoria normalizada pertence ao 
          +conjunto do centro                                            
      524 +   de custo? senão "categoria não aplicável" (RN-001), em `rep
          +rovadas_sem_categoria`.                                       
      525 +5. **Limite da categoria > 0** — se o `limite` da categoria fo
          +r ≤ 0, recusa com                                             
      526 +   motivo = `observacao` (ou "categoria não aplicável"), sob a
          + própria categoria                                            
      527 +   (RN-017).                                                  
      528 +6. **Deduplicação** — colapsar registros idênticos por campos 
          +de negócio,                                                   
      529     mantendo a primeira ocorrência; cada cópia seguinte → "regi
           stro duplicado" (RN-008).
      395 -4. **Categoria válida** — senão "categoria não aplicável" (RN-
          -001).                                                         
      396 -5. **Período** — `data` em `[inicio, fim]`; senão "data fora d
          -a competência" (RN-007).                                      
      397 -6. **Valor válido** — `valor > 0`; senão "valor inválido" (RN-
          -010).                                                         
      398 -7. **Nota fiscal** — se `valor > 100`, exige NF; senão "sem no
          -ta fiscal obrigatória" (RN-006).                              
      399 -8. **Aplicação de teto** — as despesas que passaram de 1 a 7 s
          -ão **aceitas**;                                               
      400 -   calcula-se o reembolso agregando por dia (alimentação/trans
          -porte) ou por                                                 
      401 -   registro (hospedagem) e aplicando `min(valor, teto)` (RN-00
          -2..RN-005).                                                   
      402 -9. **Agregação** — totais por categoria e total geral (RN-012)
          -.                                                             
      530 +7. **Período** — `data` em `[inicio, fim]`; senão "data fora d
          +a competência" (RN-007).                                      
      531 +8. **Valor válido** — `valor > 0`; senão "valor inválido" (RN-
          +010).                                                         
      532 +9. **Nota fiscal** — se `valor > nota_fiscal_obrigatoria_acima
          +_de`, exige NF;                                               
      533 +   senão "sem nota fiscal obrigatória" (RN-006).              
      534 +10. **Aplicação de teto** — as despesas que passaram de 1 a 9 
          +são **aceitas**;                                              
      535 +    calcula-se o reembolso conforme a periodicidade (RN-016): 
          +agregando por dia                                             
      536 +    civil (periodicidade "dia") ou por registro (periodicidade
          + "diaria"), sempre                                            
      537 +    aplicando `min(valor/soma, limite)` (RN-002..RN-005).     
      538 +11. **Agregação** — totais por categoria e total geral (RN-012
          +).                                                            
      539  
      540  ## 9. Critérios de aceite
      541  
      542  O sistema está pronto quando:
      543  
      408 -- [ ] Para o input de `exemplos/despesas-exemplo.json` com `em
          -_viagem = false`, a                                           
      409 -      saída é exatamente a do exemplo da Seção 4 (totais e rec
          -usas por categoria,                                           
      410 -      `total_reembolso_geral = 585,43`).                      
      411 -- [ ] Cada uma das 14 regras (RN-001..RN-014) tem ao menos um 
          -teste com números.                                            
      544 +- [ ] Para o input de `exemplos/despesas-exemplo.json` (centro
          + `CC-ENG-PLATAFORMA`)                                         
      545 +      com `em_viagem = false`, a saída é exatamente a do exemp
          +lo da Seção 4                                                 
      546 +      (totais e recusas por categoria, `total_reembolso_geral 
          += 351,43`).                                                   
      547 +- [ ] Categorias, limites, periodicidade, limiar de NF e acrés
          +cimo de viagem são                                            
      548 +      lidos da política externa, não codificados; um centro de
          + custo desconhecido                                           
      549 +      cai em `padrao` (RN-015).                               
      550 +- [ ] Cada uma das 17 regras (RN-001..RN-017) tem ao menos um 
          +teste com números.                                            
      551  - [ ] A saída ecoa `colaborador` (`id`, `nome`, `centro_custo`
           ) e `periodo`
      552        (`inicio`, `fim`) do input.
      553  - [ ] Em toda categoria vale `total_despesas ≥ total_aceito ≥ 
           total_reembolso`, e
      415 -      `total_despesas` inclui o `valor` das despesas reprovada
          -s da categoria, mas                                           
      416 -      **exclui valores ≤ 0** (ex.: `transporte_urbano` = 200,0
          -1, sem o estorno                                              
      417 -      `d-009` de −45,00).                                     
      554 +      `total_despesas` inclui o `valor` das despesas reprovada
          +s da categoria                                                
      555 +      (inclusive por limite ≤ 0), mas **exclui valores ≤ 0** (
          +ex.:                                                          
      556 +      `transporte_urbano` = 200,01, sem o estorno `d-009` de −
          +45,00).                                                       
      557 +- [ ] Uma categoria com limite ≤ 0 recusa suas despesas com mo
          +tivo igual à                                                  
      558 +      `observacao` (ou "categoria não aplicável" quando não ho
          +uver), sob a própria                                          
      559 +      categoria, e esse motivo prevalece sobre sem NF/fora do 
          +período.                                                      
      560 +- [ ] O bloco `categorias` lista apenas categorias válidas do 
          +centro com ao menos                                           
      561 +      uma despesa; categorias configuradas sem despesas não ap
          +arecem.                                                       
      562  - [ ] Cada despesa recusada traz um dos motivos: "categoria nã
           o aplicável",
      563        "data fora da competência", "registro duplicado", "sem n
           ota fiscal
      420 -      obrigatória", "valor inválido", "registro inválido".    
      564 +      obrigatória", "valor inválido", "registro inválido", ou 
          +a `observacao` da                                             
      565 +      categoria (limite ≤ 0).                                 
      566  - [ ] Um registro malformado é recusado ("registro inválido") 
           sem impedir o
      567        processamento das demais despesas do input.
      423 -- [ ] Valor 100,00 sem NF é aceito e 100,01 sem NF é recusado.
      568 +- [ ] Valor no limiar de NF sem NF é aceito e um centavo acima
          + sem NF é recusado.                                           
      569  - [ ] Uma despesa aceita cujo reembolso foi limitado pelo teto
            continua contando
      570        em `total_aceito` com seu valor cheio.
      426 -- [ ] Com `em_viagem = true`, os três tetos passam a 90 / 120 
          -/ 375 e o limiar de                                           
      427 -      NF continua em 100,00.                                  
      571 +- [ ] Com `em_viagem = true`, os limites de cada categoria do 
          +centro escalam pelo                                           
      572 +      `acrescimo_em_viagem_percentual` (na v4, ×1,5) e o limia
          +r de NF permanece                                             
      573 +      inalterado; categorias com limite ≤ 0 continuam não reem
          +bolsáveis.                                                    
      574  - [ ] Todos os valores de saída têm exatamente 2 casas decimai
           s.
      575  - [ ] O resultado é determinístico: o mesmo input produz sempr
           e a mesma saída.
      576  
      577  ## 10. O que fica em aberto
      578  
      579  - **Diárias reais de hospedagem:** o input não estrutura númer
           o de diárias, então
      434 -  o teto é por registro (AMB-006). Se no futuro o input trouxe
          -r `qtd_diarias`, a                                            
      435 -  regra deve ser revista para teto por diária, e isso exige no
          -va entrada em                                                 
      580 +  o teto de categorias "diaria" é por registro (AMB-006). Se n
          +o futuro o input                                              
      581 +  trouxer `qtd_diarias`, a regra deve ser revista, e isso exig
          +e nova entrada em                                             
      582    `DECISIONS.md`.
      583  - **Duplicata parcial:** registros "quase iguais" (mesmo dia/f
           ornecedor/valor,
      584    descrições diferentes) **não** são considerados duplicados n
           esta versão. Decisão
      585    provisória: só duplicidade exata conta; casos suspeitos pass
           am como aceitos.
      586 +- **Validação da política externa:** assume-se que o arquivo d
          +e política está bem                                           
      587 +  formado e vigente; não há verificação de consistência (limit
          +es negativos além                                             
      588 +  de 0, periodicidades desconhecidas, versão/vigência) nesta v
          +ersão.                                                        
      589 +- **Câmbio:** a política declara `moeda_base` BRL e há um arqu
          +ivo de câmbio no                                              
      590 +  ambiente, mas conversão de moeda continua fora de escopo até
          + haver requisito.                                             
      591  - **Moeda e fuso:** assume-se BRL e datas civis sem fuso horár
           io; multi-moeda e
      592    fuso ficam fora até haver requisito.
      593  - **Vários inputs de uma mesma competência (viagem + não-viage
           m):** cada input é

● Spec updated. Now creating the quality checklist and validating.

● Write(specs\001-motor-reembolso\checklists\requirements.md)
  ⎿  Error writing file

  Read 1 file (ctrl+o to expand)

● Write(specs\001-motor-reembolso\checklists\requirements.md)
  ⎿  Added 8 lines, removed 1 line
      1  # Specification Quality Checklist: Motor de Cálculo de Reembolso
      2  
      3  **Purpose**: Validate specification completeness and quality bef
         ore proceeding to planning
      4 -**Created**: 2026-07-30                                         
      4 +**Created**: 2026-07-30 · **Atualizado**: 2026-07-31 (política e
        +xterna e centros de custo)                                      
      5  **Feature**: [spec.md](../spec.md)
      6  
      7  ## Content Quality
     ...
      34  - As ambiguidades da política de RH foram resolvidas por decisã
          o própria (conforme
      35    o enunciado do desafio) e registradas na Seção 6 (AMB-001..AM
          B-011), em vez de
      36    virarem marcadores [NEEDS CLARIFICATION].
      37 +- Atualização 2026-07-31: novas regras de política externa (`po
         +litica-v4.json`) e                                             
      38 +  centros de custo adicionaram RN-015 (fonte externa + fallback
         + `padrao`), RN-016                                             
      39 +  (periodicidade "dia"/"diaria") e RN-017 (limite ≤ 0 não reemb
         +olsável). Três                                                 
      40 +  pontos ambíguos foram resolvidos com o usuário (Clarification
         +s Session                                                      
      41 +  2026-07-31) e encodados em AMB-013, AMB-014 e AMB-015.       
      42 +- O exemplo da Seção 4 foi recalculado para `CC-ENG-PLATAFORMA`
         + (alimentação                                                  
      43 +  limite 75, hospedagem limite 0): `total_reembolso_geral` = 35
         +1,43.                                                          
      44  - A divergência da letra do RH em hospedagem ("por diária" → "p
          or registro",
      45    AMB-006) deve ser registrada em `DECISIONS.md` na fase de pla
          no/implementação.
      46  - Items marked incomplete require spec updates before `/speckit
          -clarify` or `/speckit-plan`.

● Pronto. Sem extensions.yml no projeto, não há hooks pós-execução a disparar.

  Completion Report

  Modo: atualização in-place da spec existente (via feature.json →
  specs/001-motor-reembolso), não uma nova feature.

  - SPECIFY_FEATURE_DIRECTORY: specs/001-motor-reembolso
  - SPEC_FILE: specs/001-motor-reembolso/spec.md (v1.1 → v1.2)
  - Checklist: specs/001-motor-reembolso/checklists/requirements.md — todos os
  itens ✅

  O que mudou na spec

  Regras novas:
  - RN-015 — Política externa (politica-v4.json) como fonte da verdade; centro
  de custo desconhecido cai em padrao.
  - RN-016 — Periodicidade: "dia" (limite sobre a soma da categoria por dia
  civil) vs "diaria" (limite por registro).
  - RN-017 — Categoria com limite ≤ 0 → não reembolsável, motivo = observacao
  (ou "categoria não aplicável").

  Regras reescritas para ler da política: RN-001 (categorias válidas agora por
  centro de custo), RN-002/003/004 (limites vindos do arquivo + periodicidade),
  RN-006 (limiar via nota_fiscal_obrigatoria_acima_de), RN-009 (acréscimo via
  acrescimo_em_viagem_percentual).

  3 ambiguidades resolvidas com você (Session 2026-07-31 → AMB-013/014/015):
  1. Limite ≤ 0 → reportado sob a própria categoria.
  2. Motivo de limite ≤ 0 prevalece (avaliado logo após a validade da categoria
  — nova ordem no passo 5 da Seção 8).
  3. Bloco categorias mostra só categorias com despesas.

  Exemplo recalculado para CC-ENG-PLATAFORMA (alimentação limite 75, hospedagem
  limite 0): total_reembolso_geral 585,43 → 351,43.

  Atenção para as próximas fases

  - O código atual (regras.py, politica.py) tem limites/categorias fixos —
  precisará ler politica-v4.json. Isso é trabalho de /speckit-plan +
  /speckit-tasks.
  - A divergência de hospedagem (AMB-006) e o novo comportamento devem ser
  registrados em DECISIONS.md (que ainda não existe no repo).

  Próximo passo: /speckit-plan (a spec está pronta; se quiser revisar as 3
  decisões antes, /speckit-clarify).

✻ Brewed for 3m 43s

❯ Atualize DECISIONS.md baseado nas alterações realizadas na spec.md            

  Listed 1 directory (ctrl+o to expand)

● DECISIONS.md exists at specs/001-motor-reembolso/DECISIONS.md. Let me read it
  to match its format and D-numbering.

  Read 1 file (ctrl+o to expand)

● The format is clear. I'll add a new D-005 entry at the top (reverse
  chronological), following the established structure.
● Update(specs\001-motor-reembolso\DECISIONS.md)
  ⎿  Added 74 lines
      10  
      11  ---
      12  
      13 +## D-005 — Política externa por centro de custo (`politica-v4.j
         +son`) · `2026-07-31`                                           
      14 +                                                               
      15 +**Gatilho:** pedido do usuário via `/speckit-specify`: as categ
         +orias, limites e o                                             
      16 +tratamento de viagem/nota fiscal deixam de ser fixos e passam a
         + ser lidos de um                                               
      17 +arquivo externo (`src/informacoes_externas/politica-v4.json`), 
         +podendo variar por                                             
      18 +**centro de custo**.                                           
      19 +                                                               
      20 +**O que mudou na spec (versão 1.1 → 1.2):**                    
      21 +- **Nova RN-015 — Política externa e resolução de centro de cus
         +to**: categorias,                                              
      22 +  limites, periodicidade, limiar de NF e acréscimo de viagem vê
         +m do arquivo; se o                                             
      23 +  `centro_custo` do input não existe em `centros_custo`, usa-se
         + o objeto `padrao`.                                            
      24 +- **Nova RN-016 — Periodicidade do limite**: `"dia"` (limite so
         +bre a soma da                                                  
      25 +  categoria por dia civil) vs `"diaria"` (limite por registro).
         + Generaliza o                                                  
      26 +  mecanismo antes embutido em RN-002/003 (dia) e RN-004 (regist
         +ro).                                                           
      27 +- **Nova RN-017 — Categoria com limite ≤ 0 (não reembolsável)**
         +: recusa toda                                                  
      28 +  despesa da categoria com `motivo` = `observacao` (ou "categor
         +ia não aplicável"                                              
      29 +  se ausente), reembolso 0, reportada **sob a própria categoria
         +**.                                                            
      30 +- **RN-001** reescrita: categorias válidas = chaves do conjunto
         + do centro de custo                                            
      31 +  resolvido (não mais um trio fixo `alimentacao`/`transporte_ur
         +bano`/`hospedagem`).                                           
      32 +- **RN-002/003/004** reescritas: o teto agora é o `limite` da p
         +olítica do centro                                              
      33 +  de custo (o `padrao` mantém 60/80/250); cada uma referencia s
         +ua periodicidade.                                              
      34 +- **RN-006** (limiar de NF) e **RN-009** (acréscimo de viagem) 
         +passam a ler                                                   
      35 +  `nota_fiscal_obrigatoria_acima_de` e `acrescimo_em_viagem_per
         +centual` do arquivo.                                           
      36 +- Seção 2 (Objetivo), Seção 3 (Fora de escopo), Seção 4 (nova t
         +abela da política                                              
      37 +  externa + tabela de saída ajustada) e Seção 8 (ordem de aplic
         +ação: novo passo 2                                             
      38 +  "Resolução da política" e passo 5 "Limite da categoria > 0", 
         +renumerando os                                                 
      39 +  demais) atualizadas.                                         
      40 +- Seção 7 (casos de borda): novas linhas para limite ≤ 0, categ
         +oria só-em-alguns-                                             
      41 +  centros e centro de custo desconhecido.                      
      42 +- Seção 9 (critérios de aceite): contagem de regras 14 → **17**
         + (RN-001..RN-017) e                                            
      43 +  novos critérios para política externa, limite ≤ 0 e viagem pa
         +rametrizada.                                                   
      44 +- **Exemplo da Seção 4 recalculado** para `CC-ENG-PLATAFORMA` (
         +alimentação limite                                             
      45 +  **75**, hospedagem limite **0**): `alimentacao.total_reembols
         +o` 255,43 → **271,43**                                         
      46 +  (07-03 vai a 75, 07-31 a 61); `hospedagem` fica não reembolsá
         +vel (aceito/reembolso                                          
      47 +  0, `d-010`/`d-013` → "nao reembolsavel"); **`total_reembolso_
         +geral` 585,43 → 351,43**.                                      
      48 +                                                               
      49 +**Três ambiguidades resolvidas com o usuário (Clarifications Se
         +ssion 2026-07-31):**                                           
      50 +- **AMB-013** — centro de custo ausente na política → fallback 
         +para `padrao`.                                                 
      51 +- **AMB-014** — despesa de categoria com limite ≤ 0: (a) report
         +ada **sob a própria                                            
      52 +  categoria** e (b) esse motivo **prevalece** — a aplicabilidad
         +e da categoria                                                 
      53 +  (existência + limite > 0) é avaliada **antes** de duplicata/p
         +eríodo/valor/NF.                                               
      54 +- **AMB-015** — o bloco `categorias` lista **apenas** categoria
         +s válidas do centro                                            
      55 +  **com ao menos uma despesa** no input (sem blocos zerados).  
      56 +                                                               
      57 +**Por quê:** tirar a política de dentro do código torna limites
         + e categorias                                                  
      58 +configuráveis por RH sem alterar o motor, e o modelo por centro
         + de custo reflete                                              
      59 +que times diferentes têm tetos e categorias diferentes (ex.: `r
         +epresentacao` só em                                            
      60 +`CC-COMERCIAL`; hospedagem bloqueada em `CC-ENG-PLATAFORMA`).  
      61 +                                                               
      62 +**O que isso invalidou:** o pressuposto (D-003/D-004 e anterior
         +es) de três                                                    
      63 +categorias fixas com limites 60/80/250 embutidos — agora esses 
         +são apenas os                                                  
      64 +valores do objeto `padrao`. O exemplo de saída anterior (`total
         +_reembolso_geral`                                              
      65 +585,43) foi substituído. RN-002/003/004 deixam de citar valores
         + literais como                                                 
      66 +regra e passam a apontar para a política.                      
      67 +                                                               
      68 +**O que isso invalida na implementação:** `politica.py`/`regras
         +.py` têm categorias                                            
      69 +e limites fixos e não leem o arquivo externo; `io_json.py` não 
         +carrega a política;                                            
      70 +a saída assume sempre três categorias. Tudo isso precisa ser re
         +feito via                                                      
      71 +`/speckit-plan` → `/speckit-tasks` → `/speckit-implement`. Há t
         +ambém um                                                       
      72 +`cambio.json` no mesmo diretório, mas câmbio permanece **fora d
         +e escopo** (Seção                                              
      73 +3/10). **Este passo alterou apenas `spec.md`, `checklists/requi
         +rements.md` e este log.**                                      
      74 +                                                               
      75 +**Tasks afetadas:** nova carga de leitura/validação da política
         + e resolução do                                                
      76 +centro de custo; agregação por conjunto dinâmico de categorias;
         + portão de limite ≤ 0                                          
      77 +antes da deduplicação; golden de integração recalculado para `t
         +otal_reembolso_geral                                           
      78 += 351,43`. `plan.md`/`data-model.md`/`quickstart.md`/`tasks.md`
         + ainda assumem o                                               
      79 +modelo fixo e serão regenerados.                               
      80 +                                                               
      81 +**Custo:** 3 arquivos (`spec.md`, `checklists/requirements.md`,
         + `DECISIONS.md`);                                              
      82 +na spec, ~10 blocos (3 RNs novas, 5 RNs reescritas, 3 AMBs nova
         +s, Seções 2/3/4/7/8/9                                          
      83 +e o exemplo JSON).                                             
      84 +                                                               
      85 +---                                                            
      86 +                                                               
      87  ## D-004 — `total_despesas` ignora valores ≤ 0 na somatória · `
          2026-07-30`
      88  
      89  **Gatilho:** pedido do usuário via `/speckit-specify`: "para o 
          parâmetro

● Pronto. Adicionei a entrada D-005 no topo do
  specs/001-motor-reembolso/DECISIONS.md (ordem cronológica inversa), seguindo o
  mesmo formato das demais.

  Resumo da entrada D-005 · 2026-07-31

  Gatilho: o /speckit-specify que moveu a política para politica-v4.json com
  limites por centro de custo.

  Cobre tudo que mudou na spec (v1.1 → v1.2):
  - As 3 regras novas — RN-015 (política externa + fallback padrao), RN-016
  (periodicidade dia/diaria), RN-017 (limite ≤ 0 não reembolsável).
  - As 5 regras reescritas — RN-001, RN-002/003/004 (limites da política),
  RN-006 e RN-009 (parâmetros do arquivo).
  - As 3 ambiguidades resolvidas com você — AMB-013/014/015.
  - Recálculo do exemplo (total_reembolso_geral 585,43 → 351,43).

  Seções padronizadas preenchidas: O que mudou na spec, Por quê, O que isso 
  invalidou, O que isso invalida na implementação (aponta
  politica.py/regras.py/io_json.py a refazer, e câmbio permanece fora de
  escopo), Tasks afetadas e Custo.

  Deixei registrado explicitamente que este passo tocou apenas spec.md,
  checklists/requirements.md e o próprio DECISIONS.md — os artefatos derivados
  (plan.md, data-model.md, quickstart.md, tasks.md) ainda assumem o modelo fixo
  e serão regenerados via /speckit-plan → /speckit-tasks.

✻ Sautéed for 57s