 ▐▛███▜▌   Claude Code v2.1.220
▝▜█████▛▘  Opus 4.8 · Claude Pro
  ▘▘ ▝▝    ~\Área de Trabalho\Teste SDD\sdd-desafio\specs\001-motor-reembol…


❯ /speckit-specify As regras de negóciod RN-002, RN-003 e RN-004 precisam ser   
ajustas. O Sistema não conhece e considera categorias especificas como          
alimentacao, transporte_urbano e hospedagem. Todas as informações sobre,        
categorias existentes por centro de custo e limites da categoria devem          
considerar o que está disposto no arquivo politica-v4.json.                     
                                                                                
O sistema deve funcionar independente de alterações na politica, como limite e  
peridiocidade alterados, novas categorias ou categorias removidas.              
                                                                                
Exemplo:                                                                        
Hoje a categoria alimentacao, para centro de custo "CC-ENG-PLATAFORMA" possui   
limite de 60 e peridiciocidade como "dia", porém no futuro pode ser alterado    
para limite "80" e peridiocidade "diaria". O sistema deve respeitar as          
alterações do arquivo politica-v4                                               

● I'll start by exploring the current state of the project to understand the
  existing spec and the context for this change.

  Read 1 file, listed 1 directory (ctrl+o to expand)

● The current spec already references an external policy heavily. Let me find
  the actual politica-v4.json and the new session doc to understand exactly
  what's changing.

  Read 1 file, listed 1 directory (ctrl+o to expand)

● This session doc is a transcript of the previous spec update — I have enough
  of it. Now let me read the actual policy file and see how RN-002/003/004 are
  wired into tasks, code, and tests, since that determines how invasive this
  change is.

  Read 2 files (ctrl+o to expand)

● Now I understand the real situation. Let me check how RN-002/003/004 are
  referenced in tasks and tests to ground my options.

  Ran 1 shell command (ctrl+o to expand)

● I now have the full picture. The key finding: the spec already externalized
  the policy last session (RN-015/016/017), but RN-002, RN-003, RN-004 are still
  written per-category ("Teto de alimentação/transporte/hospedagem") — and
  there are really only two cap mechanics: periodicidade "dia" (daily sum) and
  "diaria" (per record). So generalizing them fully leaves RN-002 and RN-003
  doing the identical thing.

  That's a genuine structural fork that changes tasks.md and the RN-named test
  suite, and I can't safely default it. One question before I rewrite:

● User answered Claude's questions:
  ⎿  · As regras RN-002/003/004 hoje são específicas por categoria (alimentação,
     transporte, hospedagem), mas só existem 2 mecânicas de teto: periodicidade
     "dia" (soma do dia) e "diaria" (por registro). Como quer reestruturar 
     esses 3 IDs para ficarem agnósticos de categoria? → 3 IDs por papel 
     (Recomendado)

● Option A confirmed. This is an in-place update of
  specs/001-motor-reembolso/spec.md (feature.json points there; no
  extensions.yml, so no hooks). Let me make the targeted edits.

  First, version bump and a Clarifications entry recording the decision:

● Update(spec.md)
  ⎿  Added 1 line, removed 1 line
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.2 · **Status:** rascunho · **Última alteração:** `
        -2026-07-31`                                                     
      3 +**Versão:** 1.3 · **Status:** rascunho · **Última alteração:** `
        +2026-07-31`                                                     
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.

● Update(spec.md)
  ⎿  Added 1 line
      41  - Q: Onde reportar despesas de uma categoria que existe no cent
          ro de custo mas tem limite ≤ 0 (ex.: hospedagem em `CC-ENG-PLAT
          AFORMA`, `observacao` "nao reembolsavel")? → A: Sob a própria c
          ategoria (a categoria aparece no bloco `categorias` com `total_
          aceito`/`total_reembolso` = 0 e as despesas em `reprovadas[]`).
      42  - Q: Quando uma despesa de categoria com limite ≤ 0 também viol
          a outra regra (sem NF, fora do período, etc.), qual motivo prev
          alece? → A: O motivo de limite ≤ 0 prevalece — a aplicabilidade
           da categoria (existência + limite > 0) é avaliada logo após a 
          normalização, antes de duplicata/período/valor/nota fiscal.
      43  - Q: Quais categorias aparecem no bloco `categorias` da saída, 
          agora que cada centro de custo tem seu próprio conjunto? → A: A
          penas as categorias válidas para o centro de custo que tenham a
          o menos uma despesa no input; não se emitem blocos zerados para
           categorias configuradas sem despesas.
      44 +- Q: As regras de teto RN-002/RN-003/RN-004 ainda citavam categ
         +orias fixas (alimentação, transporte, hospedagem). Como general
         +izá-las para que o sistema não conheça categoria alguma? → A: R
         +eescritas por **papel**, sem nome de categoria: RN-002 = teto d
         +e periodicidade "dia" (`min(soma_do_dia, limite)`); RN-003 = te
         +to de periodicidade "diaria" (`min(valor, limite)` por registro
         +); RN-004 = origem do teto (o `limite` vem da entrada da catego
         +ria na política do centro de custo resolvido — nenhuma categori
         +a é privilegiada). O conjunto de categorias, seus limites e per
         +iodicidades saem inteiramente de `politica-v4.json`; novas cate
         +gorias passam a ser reembolsáveis e categorias removidas deixam
         + de ser aplicáveis sem qualquer mudança de regra ou código.    
      45  
      46  ## 3. Fora de escopo
      47  

● Now the core edit — RN-016 as the classifier, then rewrite RN-002/003/004 by
  role:

● Update(spec.md)
  ⎿  Added 15 lines, removed 12 lines
      207  limites de `padrao` (alimentacao 60,00/dia, transporte 80,00/d
           ia, hospedagem
      208  250,00/diaria).
      209  
      210 -### RN-016 — Periodicidade do limite                          
      211 -**Regra:** Cada categoria tem uma `periodicidade` na política 
          -que define **como** o                                         
      212 -limite incide:                                                
      213 -- `"dia"`: o limite incide sobre a **soma das despesas aceitas
          - da categoria no                                              
      214 -  mesmo dia civil**; reembolso do dia = `min(soma_do_dia, limi
          -te)`. Ex.:                                                    
      215 -  `alimentacao`, `transporte_urbano` (e `representacao` onde e
          -xistir).                                                      
      216 -- `"diaria"`: o limite incide sobre **cada registro individual
          -mente**; reembolso                                            
      217 -  do registro = `min(valor, limite)`. Ex.: `hospedagem`.      
      218 -**Origem:** nova política de centros de custo (2026-07-31).   
      219 -**Aceite:** categoria "dia" com 100,00 + 100,01 no mesmo dia e
          - limite 80,00 →                                               
      220 -reembolso do dia 80,00; categoria "diaria" com dois registros 
          -de 200,00 e limite                                            
      221 -250,00 → reembolso 200,00 + 200,00 (cada registro sob seu próp
          -rio teto).                                                    
      210 +### RN-016 — Periodicidade do limite (classificação)          
      211 +**Regra:** Cada categoria traz na política um campo `periodici
          +dade` que **seleciona                                         
      212 +qual mecânica de teto** se aplica, sem que o sistema precise c
          +onhecer a categoria:                                          
      213 +- `"dia"`: aplica-se o teto de periodicidade "dia" (RN-002).  
      214 +- `"diaria"`: aplica-se o teto de periodicidade "diaria" (RN-0
          +03).                                                          
      215  
      216 +A seleção é feita exclusivamente pelo valor de `periodicidade`
          + lido da política; o                                          
      217 +nome da categoria (`alimentacao`, `hospedagem`, etc.) **não** 
          +influencia a escolha.                                         
      218 +Uma categoria nova com `periodicidade` "dia" já reembolsa pela
          + mecânica de RN-002                                           
      219 +sem qualquer alteração de regra ou código. (Um valor de `perio
          +dicidade` fora de                                             
      220 +{"dia", "diaria"} está fora de escopo — assume-se política bem
          + formada, ver Seção 10.)                                      
      221 +**Origem:** nova política de centros de custo (2026-07-31); ge
          +neralização 2026-07-31.                                       
      222 +**Aceite:** na política vigente, `alimentacao` e `transporte_u
          +rbano` são "dia" e                                            
      223 +`hospedagem` é "diaria"; se `hospedagem` passar a "dia", seu l
          +imite passa a incidir                                         
      224 +sobre a soma do dia sem mudança no sistema.                   
      225 +                                                              
      226  ### RN-017 — Categoria com limite ≤ 0 (não reembolsável)
      227  **Regra:** Se, para o centro de custo resolvido, a categoria e
           xiste mas seu
      228  `limite` é **menor ou igual a zero**, toda despesa dessa categ
           oria é recusada com

● Now the three teto rules, rewritten by role (no category names):

● Update(spec.md)
  ⎿  Added 35 lines, removed 23 lines
      250  aplicável"; `ALIMENTACAO` é tratada como `alimentacao`. Em `CC
           -ADM` (sem
      251  `hospedagem` no conjunto), uma despesa de `hospedagem` é "cate
           goria não aplicável".
      252  
      253 -### RN-002 — Teto de alimentação                              
      254 -**Regra:** `alimentacao` tem periodicidade "dia" (RN-016): o t
          -eto (o `limite` da                                            
      255 -categoria na política do centro de custo) incide sobre a soma 
          -das despesas                                                  
      256 -aceitas da categoria no dia civil. O excedente não é reembolsa
          -do; o reembolso do                                            
      257 -dia é `min(soma_do_dia, limite)`. No conjunto `padrao` o limit
          -e é R$ 60,00.                                                 
      258 -**Origem:** política do RH, "Alimentação tem limite por dia" +
          - "Despesas acima do limite são reembolsadas parcialmente"; val
          -or vindo da política externa (RN-015).                        
      259 -**Aceite:** em `CC-ENG-PLATAFORMA` (limite 75,00), 72,50 + 38,
          -00 no mesmo dia →                                             
      260 -total aceito 110,50, reembolso 75,00.                         
      253 +### RN-002 — Teto de periodicidade "dia" (soma diária)        
      254 +**Regra:** Para **qualquer** categoria cuja `periodicidade` na
          + política do centro                                           
      255 +de custo resolvido seja `"dia"` (RN-016), o `limite` da catego
          +ria (RN-004) incide                                           
      256 +sobre a **soma das despesas aceitas dessa categoria no mesmo d
          +ia civil**. O                                                 
      257 +excedente não é reembolsado; o reembolso do dia é `min(soma_do
          +_dia, limite)`. A                                             
      258 +regra não conhece nem cita categoria alguma — aplica-se a toda
          + categoria "dia",                                             
      259 +existente hoje ou adicionada no futuro. (Na política vigente, 
          +`alimentacao`,                                                
      260 +`transporte_urbano` e `representacao` são "dia".)             
      261 +**Origem:** política do RH, "limite por dia" + "despesas acima
          + do limite são reembolsadas parcialmente"; limite e periodicid
          +ade vindos da política externa (RN-004, RN-015, RN-016).      
      262 +**Aceite:** categoria "dia" com limite 75,00, 72,50 + 38,00 no
          + mesmo dia →                                                  
      263 +total aceito 110,50, reembolso 75,00; com limite 80,00, uma de
          +spesa aceita de                                               
      264 +100,00 no dia → reembolso 80,00.                              
      265  
      262 -### RN-003 — Teto de transporte urbano                        
      263 -**Regra:** `transporte_urbano` tem periodicidade "dia" (RN-016
          -): o teto (o                                                  
      264 -`limite` da categoria na política do centro de custo) incide s
          -obre a soma das                                               
      265 -despesas aceitas da categoria no dia civil. Reembolso do dia =
          - `min(soma_do_dia, limite)`.                                  
      266 -No conjunto `padrao` o limite é R$ 80,00.                     
      267 -**Origem:** política do RH, "Transporte urbano tem limite por 
          -dia"; valor vindo da política externa (RN-015).               
      268 -**Aceite:** com limite 80,00, uma corrida aceita de 100,00 no 
          -dia → reembolso 80,00.                                        
      266 +### RN-003 — Teto de periodicidade "diaria" (por registro)    
      267 +**Regra:** Para **qualquer** categoria cuja `periodicidade` na
          + política do centro                                           
      268 +de custo resolvido seja `"diaria"` (RN-016), o `limite` da cat
          +egoria (RN-004)                                               
      269 +incide **por registro individual**, independente de quantas di
          +árias o registro                                              
      270 +declare ou de quantos registros haja no dia (ver AMB-006). Ree
          +mbolso do registro =                                          
      271 +`min(valor, limite)`. A regra não conhece nem cita categoria a
          +lguma — aplica-se a                                           
      272 +toda categoria "diaria". (Na política vigente, `hospedagem` é 
          +"diaria".)                                                    
      273 +**Origem:** política do RH, "limite por diária" (reinterpretad
          +o — ver AMB-006); limite e periodicidade vindos da política ex
          +terna (RN-004, RN-015, RN-016).                               
      274 +**Aceite:** categoria "diaria" com limite 250,00, registro de 
          +480,00 ("2 diárias")                                          
      275 +→ reembolso 250,00; dois registros de 200,00 no mesmo dia → 20
          +0,00 + 200,00 (cada                                           
      276 +um sob seu próprio teto, sem agregar o dia).                  
      277  
      270 -### RN-004 — Teto de hospedagem por registro                  
      271 -**Regra:** `hospedagem` tem periodicidade "diaria" (RN-016): o
          - teto (o `limite`                                             
      272 -da categoria na política do centro de custo) incide **por regi
          -stro**,                                                       
      273 -independente da quantidade de diárias que o registro declare o
          -u de quantos                                                  
      274 -registros houver no dia. Reembolso do registro = `min(valor, l
          -imite)`. No                                                   
      275 -conjunto `padrao` o limite é R$ 250,00.                       
      276 -**Origem:** política do RH, "Hospedagem tem limite por diária"
          - (reinterpretado — ver AMB-006); valor vindo da política exter
          -na (RN-015).                                                  
      277 -**Aceite:** com limite 250,00, registro de 480,00 ("2 diárias"
          -) → reembolso 250,00.                                         
      278 +### RN-004 — Origem do teto (limite pela política, sem categor
          +ia privilegiada)                                              
      279 +**Regra:** O teto de uma categoria é sempre o `limite` da entr
          +ada dessa categoria                                           
      280 +na política do centro de custo resolvido (RN-015) — `politica[
          +<CC>][<categoria>].limite`.                                   
      281 +**Nenhuma categoria tem limite embutido no sistema**; não há v
          +alor padrão em código                                         
      282 +para `alimentacao`, `hospedagem` ou qualquer outra. Alterar o 
          +`limite` na política                                          
      283 +altera o teto sem mudança de regra; o conjunto `padrao` fornec
          +e o limite quando o                                           
      284 +centro de custo não existe em `centros_custo`. Aplicado o limi
          +te, a mecânica segue                                          
      285 +a periodicidade da categoria (RN-002 ou RN-003).              
      286 +**Origem:** requisito de política externa; generalização das r
          +egras de teto (2026-07-31).                                   
      287 +**Aceite:** `alimentacao` reembolsa com limite 60,00 no `padra
          +o`, 75,00 em                                                  
      288 +`CC-ENG-PLATAFORMA` e 45,00 em `CC-ADM`, apenas trocando o val
          +or na política; se a                                          
      289 +política passar `alimentacao` para limite 80,00, o teto vira 8
          +0,00 sem tocar no código.                                     
      290  
      291  ### RN-005 — Reembolso parcial no teto
      292  **Regra:** Quando o valor aceito ultrapassa o teto aplicável, 
           reembolsa-se apenas

● Now reconcile the AMB cross-references (the "dia" mechanic is now solely
  RN-002; the "diaria" mechanic moved to RN-003):

● Update(spec.md)
  ⎿  Added 1 line, removed 1 line
      394  **O que não está claro:** com duas despesas no mesmo dia soman
           do mais que o teto, reembolsa-se por despesa (e nesse caso, em
            que ordem?) ou agrega-se o dia?
      395  **Decisão:** o teto de categorias com periodicidade "dia" inci
           de sobre o **agregado do dia** por categoria. Reembolso do dia
            = `min(soma das aceitas do dia, limite)`. Como a saída é por 
           categoria, não é preciso ratear por despesa individual.
      396  **Justificativa:** o limite da política é diário, não por desp
           esa; agregar evita depender de ordenação arbitrária.
      397 -**Regra afetada:** RN-002, RN-003, RN-005, RN-016.            
      397 +**Regra afetada:** RN-002, RN-005, RN-016.                    
      398  
      399  ### AMB-002 — O campo `id` conta para definir duplicidade?
      400  **Texto original do RH:** "Duplicatas devem ser tratadas." (de
           cisão recebida: "todos os campos iguais")

● Update(spec.md)
  ⎿  Added 1 line, removed 1 line
      430  **O que não está claro:** um registro de 480,00 dizendo "2 diá
           rias" deveria ter teto de 2× o limite ou 1×?
      431  **Decisão:** para categorias de periodicidade "diaria", o teto
            é **por registro** (`min(valor, limite)`), independentemente 
           de quantas diárias o texto mencione. `d-010` reembolsa `min(48
           0,00, limite)`.
      432  **Justificativa:** o input não traz número de diárias de forma
            estruturada e confiável; contar diárias a partir da descrição
            seria adivinhação. Divergência da letra do RH registrada em `
           DECISIONS.md`.
      433 -**Regra afetada:** RN-004, RN-016.                            
      433 +**Regra afetada:** RN-003, RN-004, RN-016.                    
      434  
      435  ### AMB-007 — Precisão e arredondamento monetário (`33,333`)
      436  **Texto original do RH:** nada sobre casas decimais.

● Now Section 7 edge cases and Section 8 application order:
● Update(spec.md)
  ⎿  Added 1 line, removed 1 line
      514  | Data fora do período | `d-008` 2026-04-15 | recusada "data f
           ora da competência" | RN-007 |
      515  | Valor negativo | `d-009` -45,00 | recusada "valor inválido" 
           | RN-010 |
      516  | Registro malformado | despesa sem `data` ou `valor` não numé
           rico | recusada "registro inválido" em `reprovadas_sem_categor
           ia`; demais processados | RN-013 |
      517 -| Hospedagem acima do teto (várias diárias num registro) | `d-
          -010` 480,00 num centro com limite 250 | aceito 480,00; reembol
          -so 250,00 | RN-004, RN-016 |                                  
      517 +| Categoria "diaria" acima do teto (várias diárias num registr
          +o) | `d-010` 480,00 num centro com limite 250 | aceito 480,00;
          + reembolso 250,00 | RN-003, RN-004, RN-016 |                  
      518  | Mais de 2 casas decimais | `d-011` 33,333 | arredonda para 3
           3,33 | RN-011 |
      519  | Fim de semana | `d-012` sábado 47,20 | tratado como qualquer
            dia (sem regra de calendário) | Seção 3 |
      520  | Categoria em caixa alta | `d-014` `ALIMENTACAO` 61,00 | trat
           ada como `alimentacao` | RN-001 |

● Update(spec.md)
  ⎿  Added 1 line, removed 1 line
      503  
      504  | Caso | Entrada (exemplo) | Comportamento esperado | Regra |
      505  |---|---|---|---|
      506 -| Soma diária excede teto | `d-001` 72,50 + `d-002` 38,00 (ali
          -mentação, mesmo dia, `CC-ENG-PLATAFORMA` limite 75) | aceito 1
          -10,50; reembolso 75,00 | RN-002, RN-005, RN-016 |             
      506 +| Soma diária excede teto (periodicidade "dia") | `d-001` 72,5
          +0 + `d-002` 38,00 (categoria "dia", mesmo dia, `CC-ENG-PLATAFO
          +RMA` limite 75) | aceito 110,50; reembolso 75,00 | RN-002, RN-
          +004, RN-005, RN-016 |                                         
      507  | Valor exatamente no limiar de NF | `d-003` 100,00 sem NF | a
           ceita (NF não obrigatória) | RN-006 |
      508  | Valor um centavo acima do limiar | `d-004` 100,01 sem NF | r
           ecusada "sem nota fiscal obrigatória" | RN-006 |
      509  | Categoria fora do conjunto do centro | `d-005` `coworking` |
            recusada "categoria não aplicável" em `reprovadas_sem_categor
           ia` | RN-001, RN-012 |

● Update(spec.md)
  ⎿  Added 5 lines, removed 4 lines
      547  8. **Valor válido** — `valor > 0`; senão "valor inválido" (RN-
           010).
      548  9. **Nota fiscal** — se `valor > nota_fiscal_obrigatoria_acima
           _de`, exige NF;
      549     senão "sem nota fiscal obrigatória" (RN-006).
      550 -10. **Aplicação de teto** — as despesas que passaram de 1 a 9 
          -são **aceitas**;                                              
      551 -    calcula-se o reembolso conforme a periodicidade (RN-016): 
          -agregando por dia                                             
      552 -    civil (periodicidade "dia") ou por registro (periodicidade
          - "diaria"), sempre                                            
      553 -    aplicando `min(valor/soma, limite)` (RN-002..RN-005).     
      550 +10. **Aplicação de teto** — as despesas que passaram de 1 a 9 
          +são **aceitas**; o                                            
      551 +    `limite` vem da entrada da categoria na política do centro
          + resolvido (RN-004) e                                         
      552 +    a mecânica é escolhida pela `periodicidade` (RN-016): agre
          +gando por dia civil                                           
      553 +    quando "dia" (RN-002) ou por registro quando "diaria" (RN-
          +003), sempre                                                  
      554 +    aplicando `min(soma_ou_valor, limite)` com reembolso parci
          +al no excedente (RN-005).                                     
      555  11. **Agregação** — totais por categoria e total geral (RN-012
           ).
      556  
      557  ## 9. Critérios de aceite

● Now add an acceptance criterion capturing the resilience-to-policy-changes
  requirement:

● Update(spec.md)
  ⎿  Added 7 lines
      564  - [ ] Categorias, limites, periodicidade, limiar de NF e acrés
           cimo de viagem são
      565        lidos da política externa, não codificados; um centro de
            custo desconhecido
      566        cai em `padrao` (RN-015).
      567 +- [ ] Nenhuma categoria é conhecida ou privilegiada pelo siste
          +ma: o teto de cada                                            
      568 +      categoria vem de `politica[<CC>][<categoria>].limite` (R
          +N-004) e a mecânica                                           
      569 +      da `periodicidade` (RN-002/RN-003) é escolhida pelo valo
          +r lido da política,                                           
      570 +      não pelo nome da categoria. Adicionar uma categoria à po
          +lítica a torna                                                
      571 +      reembolsável, removê-la a torna "categoria não aplicável
          +", e mudar seu                                                
      572 +      `limite`/`periodicidade` muda o resultado — tudo **sem a
          +lterar regra ou                                               
      573 +      código** (RN-001, RN-004, RN-015, RN-016).              
      574  - [ ] Cada uma das 17 regras (RN-001..RN-017) tem ao menos um 
           teste com números.
      575  - [ ] A saída ecoa `colaborador` (`id`, `nome`, `centro_custo`
           ) e `periodo`
      576        (`inicio`, `fim`) do input.

● Let me verify consistency across the spec — check remaining RN-002/003/004
  references and any lingering category-hardcoding language:

  Ran 1 shell command (ctrl+o to expand)

● The RN section is coherent. Now let me handle the required spec-quality
  checklist and the project's DECISIONS.md convention:

  Read 2 files (ctrl+o to expand)

● I'll add a DECISIONS.md entry (project convention: one entry per spec change)
  and refresh the checklist note:

● Update(DECISIONS.md)
  ⎿  Added 55 lines
      10  
      11  ---
      12  
      13 +## D-006 — Regras de teto agnósticas de categoria (RN-002/003/0
         +04 por papel) · `2026-07-31`                                   
      14 +                                                               
      15 +**Gatilho:** pedido do usuário via `/speckit-specify`: o sistem
         +a não deve conhecer                                            
      16 +nem citar categorias específicas (`alimentacao`, `transporte_ur
         +bano`, `hospedagem`).                                          
      17 +Todas as categorias, limites e periodicidades devem sair de `po
         +litica-v4.json`, e o                                           
      18 +motor deve funcionar sem alteração diante de mudanças na políti
         +ca (limite/periodicidade                                       
      19 +alterados, categorias novas ou removidas).                     
      20 +                                                               
      21 +**Decisão de estrutura (escolhida com o usuário):** manter os t
         +rês IDs RN-002/003/004                                         
      22 +(mínimo impacto em `tasks.md` e nos testes nomeados por RN), re
         +escrevendo cada um por                                         
      23 +**papel**, sem nome de categoria:                              
      24 +- **RN-002 — Teto de periodicidade "dia"**: `min(soma_do_dia, l
         +imite)` para qualquer                                          
      25 +  categoria cuja `periodicidade` seja "dia". Absorve o antigo t
         +eto de transporte.                                             
      26 +- **RN-003 — Teto de periodicidade "diaria"**: `min(valor, limi
         +te)` por registro para                                         
      27 +  qualquer categoria "diaria". Deixa de ser "teto de transporte
         +" e passa a ser a                                              
      28 +  mecânica por registro (antes só em RN-004/hospedagem).       
      29 +- **RN-004 — Origem do teto**: o `limite` vem de `politica[<CC>
         +][<categoria>].limite`                                         
      30 +  (RN-015); nenhuma categoria tem limite embutido no código. De
         +ixa de ser "teto de                                            
      31 +  hospedagem".                                                 
      32 +                                                               
      33 +**O que mudou na spec (versão 1.2 → 1.3):**                    
      34 +- **RN-002/003/004** reescritas por papel (acima); nenhuma cita
         + categoria como regra —                                        
      35 +  só como exemplo do que a política vigente traz.              
      36 +- **RN-016** reposicionada como **classificação**: o valor de `
         +periodicidade` seleciona                                       
      37 +  a mecânica (RN-002 ou RN-003) sem o sistema conhecer o nome d
         +a categoria.                                                   
      38 +- **AMB-001** (agregação diária) → afeta RN-002 (não mais RN-00
         +3); **AMB-006**                                                
      39 +  (hospedagem por registro) → afeta RN-003/RN-004.             
      40 +- Seção 7 (bordas): linhas de teto reescritas por periodicidade
         +; Seção 8 (passo 10)                                           
      41 +  descreve limite via RN-004 + mecânica via RN-016 (RN-002/RN-0
         +03).                                                           
      42 +- Seção 9 (aceite): novo critério de que nenhuma categoria é co
         +nhecida/privilegiada e                                         
      43 +  que adicionar/remover/alterar categoria na política muda o re
         +sultado sem tocar código.                                      
      44 +- Clarifications: nova entrada Session 2026-07-31 registrando a
         + generalização.                                                
      45 +                                                               
      46 +**Por quê:** a v1.2 externalizou a política (RN-015/016/017), m
         +as RN-002/003/004 ainda                                        
      47 +enunciavam categorias fixas — uma inconsistência com o objetivo
         + de política dirigir tudo.                                     
      48 +Generalizar por papel remove o último acoplamento de regra a ca
         +tegoria.                                                       
      49 +                                                               
      50 +**O que isso invalida na implementação:** `politica.py` e `regr
         +as.py` ainda embutem                                           
      51 +`CATEGORIAS_VALIDAS`, `LIMITES_DIARIOS`, `LIMITE_HOSPEDAGEM`, `
         +ORDEM_CATEGORIAS` e                                            
      52 +funções separadas `aplica_teto_diario`/`aplica_teto_hospedagem`
         +, e **não leem**                                               
      53 +`politica-v4.json`. Tudo isso precisa passar a derivar da polít
         +ica (limite/periodicidade                                      
      54 +por categoria do CC resolvido) via `/speckit-plan` → `/speckit-
         +tasks` →                                                       
      55 +`/speckit-implement`. **Este passo alterou apenas `spec.md`, `c
         +hecklists/requirements.md`                                     
      56 +e este log.**                                                  
      57 +                                                               
      58 +**Tasks afetadas:** teto passa a ser dirigido por `periodicidad
         +e` da política (uma                                            
      59 +mecânica "dia", uma "diaria") sobre um conjunto **dinâmico** de
         + categorias; testes                                            
      60 +`test_rn_002/003/004` re-expressos por papel, não por categoria
         +; agregação/ordem de                                           
      61 +categorias na saída derivada da política, não de `ORDEM_CATEGOR
         +IAS` fixo.                                                     
      62 +                                                               
      63 +**Custo:** 3 arquivos (`spec.md`, `checklists/requirements.md`,
         + `DECISIONS.md`); na                                           
      64 +spec, ~9 blocos (RN-002/003/004, RN-016, AMB-001, AMB-006, Seçõ
         +es 7/8/9, Clarifications).                                     
      65 +                                                               
      66 +---                                                            
      67 +                                                               
      68  ## D-005 — Política externa por centro de custo (`politica-v4.j
          son`) · `2026-07-31`
      69  
      70  **Gatilho:** pedido do usuário via `/speckit-specify`: as categ
          orias, limites e o

● Now update the checklist (validation date + note on this change):

● Update(checklists\requirements.md)
  ⎿  Added 1 line, removed 1 line
      1  # Specification Quality Checklist: Motor de Cálculo de Reembolso
      2  
      3  **Purpose**: Validate specification completeness and quality bef
         ore proceeding to planning
      4 -**Created**: 2026-07-30 · **Atualizado**: 2026-07-31 (política e
        -xterna e centros de custo)                                      
      4 +**Created**: 2026-07-30 · **Atualizado**: 2026-07-31 (regras de 
        +teto agnósticas de categoria)                                   
      5  **Feature**: [spec.md](../spec.md)
      6  
      7  ## Content Quality

● Update(checklists\requirements.md)
  ⎿  Added 6 lines
      41    2026-07-31) e encodados em AMB-013, AMB-014 e AMB-015.
      42  - O exemplo da Seção 4 foi recalculado para `CC-ENG-PLATAFORMA`
           (alimentação
      43    limite 75, hospedagem limite 0): `total_reembolso_geral` = 35
          1,43.
      44 +- Atualização 2026-07-31 (spec 1.2 → 1.3, ver DECISIONS D-006):
         + RN-002/003/004                                                
      45 +  deixaram de citar categorias fixas e foram reescritas por **p
         +apel** — RN-002 teto                                           
      46 +  de periodicidade "dia", RN-003 teto de periodicidade "diaria"
         +, RN-004 origem do                                             
      47 +  teto (limite pela política). Nenhuma regra conhece nome de ca
         +tegoria; o conjunto,                                           
      48 +  limites e periodicidades vêm inteiramente de `politica-v4.jso
         +n` e mudam o resultado                                         
      49 +  sem alteração de código. Novo critério de aceite na Seção 9 c
         +obre essa resiliência.                                         
      50  - A divergência da letra do RH em hospedagem ("por diária" → "p
          or registro",
      51    AMB-006) deve ser registrada em `DECISIONS.md` na fase de pla
          no/implementação.
      52  - Items marked incomplete require spec updates before `/speckit
          -clarify` or `/speckit-plan`.

● All edits are in. Let me do a final coherence scan to make sure nothing still
  hardcodes categories as rules (vs. examples):

  Ran 1 shell command (ctrl+o to expand)

● The spec is coherent and the rule set stays at 17. No .specify/extensions.yml,
  so there are no pre/post hooks to run. Validation checklist passes (no [NEEDS
  CLARIFICATION] remain, all items testable with numeric acceptance examples).

  Concluído — spec atualizada

  SPECIFY_FEATURE_DIRECTORY: specs/001-motor-reembolso
  SPEC_FILE: specs/001-motor-reembolso/spec.md (versão 1.2 → 1.3)

  Reescrevi RN-002/003/004 por papel, eliminando qualquer categoria hardcoded
  (escolha que você confirmou):

  ┌────────┬────────────────┬───────────────────────────────────────────────┐
  │   RN   │     Antes      │                     Agora                     │
  ├────────┼────────────────┼───────────────────────────────────────────────┤
  │        │ Teto de        │ Teto de periodicidade "dia" —                 │
  │ RN-002 │ alimentação    │ min(soma_do_dia, limite) para qualquer        │
  │        │                │ categoria "dia"                               │
  ├────────┼────────────────┼───────────────────────────────────────────────┤
  │        │ Teto de        │ Teto de periodicidade "diaria" — min(valor,   │
  │ RN-003 │ transporte     │ limite) por registro                          │
  │        │ urbano         │                                               │
  ├────────┼────────────────┼───────────────────────────────────────────────┤
  │        │ Teto de        │ Origem do teto — limite vem de                │
  │ RN-004 │ hospedagem     │ politica[<CC>][<categoria>].limite; nenhuma   │
  │        │                │ categoria embutida no código                  │
  ├────────┼────────────────┼───────────────────────────────────────────────┤
  │        │ Periodicidade  │ Reposicionada como classificação: o valor de  │
  │ RN-016 │ (mecânica)     │ periodicidade seleciona RN-002/RN-003 sem o   │
  │        │                │ sistema conhecer o nome da categoria          │
  └────────┴────────────────┴───────────────────────────────────────────────┘

  Também ajustei os cross-refs (AMB-001 → RN-002; AMB-006 → RN-003/RN-004), as
  linhas de teto da Seção 7, o passo 10 da Seção 8, adicionei um critério de
  aceite na Seção 9 sobre resiliência a mudanças de política (categoria
  nova/removida/limite alterado sem tocar código), uma entrada em Clarifications
  (Session 2026-07-31) e o registro D-006 em DECISIONS.md.

  Checklist: todos os itens ✓ (Content Quality, Requirement Completeness,
  Feature Readiness). Sem marcadores de clarificação pendentes.

  Um ponto importante para a próxima fase: o código (src/politica.py,
  src/regras.py) ainda não lê politica-v4.json — ele embute CATEGORIAS_VALIDAS,
  LIMITES_DIARIOS, LIMITE_HOSPEDAGEM, ORDEM_CATEGORIAS e funções
  aplica_teto_diario/aplica_teto_hospedagem fixas. A spec agora exige o oposto.
  Registrei isso em D-006.

  Próximo passo recomendado: /speckit-plan (a spec está estável; não há
  clarificações abertas) para regenerar plan.md/tasks.md e alinhar a
  implementação — que hoje diverge da spec de forma significativa.

✻ Baked for 6m 9s

※ recap: Goal: make the reimbursement engine fully policy-driven with no hardcoded categories. I rewrote spec RN-002/003/004 by role (spec v1.3) and logged decision D-006. Next: run /speckit-plan to regenerate the plan and align the code, which still hardcodes categories. (disable recaps in /config)

❯ /speckit-specify Crie novas regras referentes a conversão de cambio conforme  
as instruidas abaixo:                                                           
- Informações de cambio e a conversão para cada moeda estão dispostas no        
arquivo informacoes_externas/cambio.json                                        
- No input de despesas, registros podem ou não ter a informação de cambio       
(exemplo de inputs: despesas-exemplo.json, despesas-envelope.json)              
- Para cada registro com parametro "moeda", o valor deve ser convertido         
considerando o valor da moeda disposto em cambio.json                           
- Se o registro não possuir o campo "moeda", deve ser considerado o valor de    
"moeda_base" do arquivo "cambio.json"                                           
- Registros do input com "moeda" igual a "moeda_base" de cambio.json não devem  
calcular conversão                                                              
- Para registros que possuem "moeda" diferente da moeda_base, deve ser          
calculado a conversão a partir da data registrada para o cambio. Exemplo:       
  1.Registro de despesa com data "26-07-24" deve considerar o cambio            
"2026-07-24": { "USD": 5.46, "EUR": 5.97 }" de cambio.json                      
- Se data de registro no input não possuir uma data de "taxas" exata, considere 
a data mais próxima, se tanto a data futura quanto passada tiverem a mesma      
distancia de tempo, considere o valor de conversão mais baixo entre as duas     
datas proximas                                                                  
- Se o campo "moeda" fornecer um valor que não existe em "taxas" para a data de 
registro, siga a regra da data mais proxima que possua esta moeda               
- Se o campo "moeda" fornecer um valor que não existe em nenhuma das "taxas" de 
cambio.json, recuse a despesa com a mensagem "cambio não identificado"          
- A validação de nota fiscal obrigatória deve ser realizada após a conversão de 
cambio.                                                                         
- a "moeda_base" considerada deve ser do arquivo cambio.json, a "moeda_base" do 
arquivo politica-v4.json não deve ser considerado                               
                                                                                
Altere as regras referentes a colaboradores "em viagem" seguindo as diretrizes: 
- Sistema não terá mais input opcional para "em viagem"                         
- Registros de despesas serão consideradas "em viagem" caso moeda do registro   
for diferente da "moeda_base" do arquivo cambio.json                            
- Um input pode ter registros com diferentes moedas, a validação de "em viagem" 
agora passa a ser por registro e não por input completo                         
- Se não houver "moeda" no registro, não é considerado em viagem                
- O acrescimo no limite em viagem, deve considerar o valor da despesa já        
convertido para a moeda base                                                    

● This is a substantial new feature (currency conversion + redefining "em
  viagem" by currency). Let me ground myself in the actual data files and the
  current spec sections this touches.

  Read 3 files, ran 1 shell command (ctrl+o to expand)

● Key finding: none of the records in despesas-exemplo.json has a moeda field,
  and despesas-envelope.json is empty. So under the new rules the golden example
  stays all-BRL / non-travel (numbers unchanged) — the real work is the new
  câmbio rules plus redefining "em viagem" per-record. That surfaces a few
  genuine decisions I can't safely default, because "em viagem" being per-record
  collides with the "dia" periodicity that aggregates a whole category-day
  against one limit.

  Let me settle these before writing:

● User declined to answer questions
  ⎿  · Com "em viagem" agora POR REGISTRO (moeda ≠ base), um mesmo dia+categoria
     de periodicidade "dia" (RN-002) pode misturar registros em viagem (limite 
     ×1,5) e não-viagem (limite base). Como aplicar o teto nesse dia misto? 
     (Ex.: CC-ENG-PLATAFORMA, alimentação, limite base 75 / viagem 112,50; no 
     dia: R1 BRL 80 não-viagem + R2 convertido 80 viagem, soma 160) (Amplia se 
     houver viagem / Baldes separados (Recomendado) / Amplia só se todos viagem)
     · Hoje a saída ecoa um campo de topo `em_viagem` (booleano do input). Como 
     o input `em_viagem` deixa de existir e viagem passa a ser por registro, o 
     que a saída deve fazer quanto a viagem/conversão? (Remover, totais em BRL 
     (Recomendado) / Remover + trilha de conversão / Manter flag derivada)
     · Um registro com `moeda` que não existe em NENHUMA data de `taxas` é 
     recusado com "cambio não identificado". Como reportá-lo, dado que seu valor
     não pode ser convertido para a base? (Sob a categoria, fora do total 
     (Recomendado) / Em reprovadas_sem_categoria)
● The user wants to clarify the questions first. What would you like to clarify
  or add before I finalize these decisions?

  To orient us, here's what each question is really about — tell me where you
  want to steer:

  1. Teto de dia misto (periodicidade "dia") — the core one. Now that "em
  viagem" is per-record, a single day+category (e.g. alimentacao) can hold both
  a BRL record (limit 75) and a converted foreign record (limit 112,50). Since
  RN-002 sums the whole day against one limit, I need to know how to combine
  them. Is my framing of the scenario right? Do you actually expect
  mixed-currency records in the same category on the same day, or is that a
  non-case for you?
  2. Campo em_viagem na saída — the input em_viagem is gone. Question is purely
  about the output: drop it, drop it but add a per-record conversion audit
  trail, or keep a derived top-level flag. Do you care about seeing which
  expenses were converted (and at what rate) in the result, or is a clean BRL
  total enough?
  3. "cambio não identificado" — where a rejected-for-unknown-currency expense
  lands in the output, since it has no BRL value to sum into total_despesas.

  A few other things I was going to default without asking — say if any of these
  should instead be a question:
  - Arredondamento da conversão: round foreign valor to 2 decimals, multiply by
  rate, round result to 2 decimals (half-up), per RN-011.
  - Duplicidade: add moeda to the business-key so two records differing only by
  currency aren't duplicates.
  - Ordem das regras (Seção 8): conversion happens right after normalization
  (before NF, período, valor, teto), because NF and travel-status both need the
  converted value.
  - Exemplo dourado: unchanged (total_reembolso_geral = 351,43) since no record
  has moeda.

  What would you like to adjust?

✻ Churned for 3m 7s

❯ O arquivo despesas-envelope.json agora está preenchido. Avalie o arquivo e    
  veja se a pergunta está esclarecida. Se algo ainda não estiver claro me       
  pergunte novamente.                                                           

  Read 1 file (ctrl+o to expand)

● Avaliei o despesas-envelope.json (CC-COMERCIAL). Ele confirma parte das
  dúvidas e ajuda a fechar outras, mas duas continuam genuinamente em aberto.
  Resumo do que o arquivo esclareceu:

  - e-006 GBP (07-21) → GBP não existe em nenhuma data de taxas (só há USD/EUR)
  ⇒ é exatamente o caso "cambio não identificado". A categoria (representacao) é
  válida no CC-COMERCIAL, então a recusa é de um registro de categoria válida.
  - e-004 EUR sábado (07-18) → sem taxa nesse dia; a regra da data mais próxima
  resolve (07-17, dist. 1, EUR 5,96 vs 07-20, dist. 2) — sem empate. A regra de
  desempate ("menor taxa") não é exercitada por este input, mas continua válida
  na spec.
  - e-010 sem moeda → base (BRL), não-viagem; e-009 coworking → categoria não
  aplicável no CC-COMERCIAL.
  - Nenhum dia mistura registros em viagem e não-viagem na mesma categoria: cada
  despesa em moeda estrangeira está sozinha no seu dia+categoria.

  Com isso, vou assumir por padrão (documentando como AMB reversível) — me
  corrija se discordar:

  - "cambio não identificado" (Q3): como e-006, fica sob a própria categoria
  (representacao.reprovadas[]) e é excluído de total_despesas (não há valor em
  base para somar) — mesmo princípio da exclusão por não-valorável já usada para
  valores ≤ 0.
  - Arredondamento: arredonda o valor estrangeiro a 2 casas → multiplica pela
  taxa → arredonda o resultado a 2 casas (half-up, RN-011).
  - Duplicidade: moeda entra na chave de negócio.
  - Ordem (Seção 8): conversão logo após a normalização (antes de NF, período,
  valor e teto).

  Restam duas decisões que o envelope não resolve:

● User answered Claude's questions:
  ⎿  · O envelope NÃO tem nenhum dia+categoria misturando registro em viagem e 
     não-viagem (cada moeda estrangeira está sozinha no seu dia). Mas para a 
     periodicidade "dia" (RN-002) a spec precisa de uma regra determinística 
     caso isso ocorra no futuro. Como definir? (Ex.: alimentação CC-COMERCIAL, 
     base 90 / viagem 135; dia com R1 BRL 80 + R2 convertido 80, soma 160) → 
     Baldes separados (Recomendado)
     · A saída hoje ecoa um `em_viagem` de topo (que deixa de existir) e não 
     lista despesas aceitas. Com o envelope cheio de conversões (EUR/USD), o que
     a saída deve mostrar sobre câmbio/viagem? → Remover, totais em BRL 
     (Recomendado)

● Decisions locked: baldes separados (Q1), remover em_viagem, totais em BRL
  (Q2), plus my defaults for câmbio-rejected/rounding/dup-key/order. Now let me
  re-read the current spec exactly so my edits match:

  Read 1 file (ctrl+o to expand)

● I have the exact text. This is a sizable change — I'll add three new rules
  (RN-018 câmbio conversion, RN-019 rate-by-date, RN-020 câmbio não
  identificado), rewrite RN-009 (travel per-record by currency), and thread the
  changes through every section. Let me work through it in batches.

  Batch 1 — header, objetivo, clarifications, fora de escopo:

● Update(spec.md)
  ⎿  Added 1 line, removed 1 line
      1  # Spec — Motor de Cálculo de Reembolso
      2  
      3 -**Versão:** 1.3 · **Status:** rascunho · **Última alteração:** `
        -2026-07-31`                                                     
      3 +**Versão:** 1.4 · **Status:** rascunho · **Última alteração:** `
        +2026-07-31`                                                     
      4  
      5  > **Regra de ouro deste arquivo:** ele descreve o QUÊ e o PORQUÊ
         . Nenhuma linha
      6  > aqui pode citar linguagem, biblioteca, classe, função ou estru
         tura de pasta.

● Update(spec.md)
  ⎿  Added 4 lines, removed 1 line
      26  reembolsável por categoria e por que cada despesa recusada foi 
          recusada. As
      27  categorias válidas, seus limites, o limiar de nota fiscal e o a
          créscimo de
      28  viagem passam a ser lidos de uma **política externa versionada*
          * e podem variar
      29 -por **centro de custo**.                                       
      29 +por **centro de custo**. Cada despesa pode ser lançada em **moe
         +da estrangeira**;                                              
      30 +o valor é convertido para a **moeda base** por uma **tabela de 
         +câmbio externa                                                 
      31 +versionada** antes de qualquer regra monetária, e a condição de
         + **viagem passa a                                              
      32 +ser derivada por registro** (moeda diferente da base), não mais
         + informada no input.                                           
      33  
      34  ## Clarifications
      35  

● Update(spec.md)
  ⎿  Added 7 lines
      46  - Q: Quais categorias aparecem no bloco `categorias` da saída, 
          agora que cada centro de custo tem seu próprio conjunto? → A: A
          penas as categorias válidas para o centro de custo que tenham a
          o menos uma despesa no input; não se emitem blocos zerados para
           categorias configuradas sem despesas.
      47  - Q: As regras de teto RN-002/RN-003/RN-004 ainda citavam categ
          orias fixas (alimentação, transporte, hospedagem). Como general
          izá-las para que o sistema não conheça categoria alguma? → A: R
          eescritas por **papel**, sem nome de categoria: RN-002 = teto d
          e periodicidade "dia" (`min(soma_do_dia, limite)`); RN-003 = te
          to de periodicidade "diaria" (`min(valor, limite)` por registro
          ); RN-004 = origem do teto (o `limite` vem da entrada da catego
          ria na política do centro de custo resolvido — nenhuma categori
          a é privilegiada). O conjunto de categorias, seus limites e per
          iodicidades saem inteiramente de `politica-v4.json`; novas cate
          gorias passam a ser reembolsáveis e categorias removidas deixam
           de ser aplicáveis sem qualquer mudança de regra ou código.
      48  
      49 +### Session 2026-07-31 (câmbio e viagem por moeda)             
      50 +                                                               
      51 +- Q: Num dia+categoria de periodicidade "dia", com registros em
         + viagem (limite ×fator) e não-viagem (limite base) misturados, 
         +como aplicar o teto? → A: **Baldes separados** — separa as acei
         +tas do dia em dois somatórios por status de viagem; cada balde 
         +é limitado pelo seu próprio teto (base para não-viagem, amplifi
         +cado para viagem) e o reembolso do dia é a soma dos dois.      
      52 +- Q: O input deixa de ter `em_viagem`; o que a saída faz com o 
         +antigo campo `em_viagem` e com a conversão? → A: **Remover** o 
         +`em_viagem` da saída; todos os valores de saída ficam na moeda 
         +base já convertidos; a saída permanece enxuta (totais + `reprov
         +adas[]` com `id` e `motivo`, sem trilha de conversão por regist
         +ro).                                                           
      53 +- Q: Um registro cuja `moeda` não existe em nenhuma data de `ta
         +xas` ("cambio não identificado") é reportado onde e entra em `t
         +otal_despesas`? → A: Se a categoria for válida, entra em `categ
         +orias.<cat>.reprovadas[]`; é **excluído de `total_despesas`** (
         +não há valor em base para somar), pelo mesmo princípio de não-v
         +alorável usado para valores ≤ 0.                               
      54 +- Q: Como e quando arredondar na conversão? → A: Arredonda o `v
         +alor` na moeda de origem a 2 casas (RN-011), multiplica pela ta
         +xa e arredonda o resultado a 2 casas (half-up); o valor convert
         +ido em base é o usado por todas as regras monetárias seguintes.
      55 +                                                               
      56  ## 3. Fora de escopo
      57  
      58  - Não calcula estornos, créditos ou saldos negativos — o sistem
          a só produz

● Update(spec.md)
  ⎿  Added 4 lines, removed 2 lines
      58  - Não calcula estornos, créditos ou saldos negativos — o sistem
          a só produz
      59    valores de reembolso maiores ou iguais a zero.
      60  - Não valida a autenticidade da nota fiscal; confia no campo `t
          em_nota_fiscal`.
      61 -- Não faz conversão de moeda; todos os valores são em BRL. (A p
         -olítica externa                                                
      62 -  declara `moeda_base` BRL; não há regra de câmbio nesta versão
         -.)                                                             
      61 +- Faz conversão de moeda a partir de uma tabela de câmbio exter
         +na (`cambio.json`,                                             
      62 +  ver RN-018..RN-020); a `moeda_base` de referência é a do **`c
         +ambio.json`** (a                                               
      63 +  `moeda_base` de `politica-v4.json` **não** é usada). Não busc
         +a cotações fora do                                             
      64 +  arquivo nem interpola taxas: usa a taxa da data ou da data ma
         +is próxima disponível.                                         
      65  - Não decide teto por diária individual de hospedagem quando um
           registro agrupa
      66    várias diárias (ver AMB-006); em categorias de periodicidade 
          "diaria" o teto é
      67    por registro.

● Batch 2 — Section 4 input intro, input table (remove em_viagem, add moeda), 
  câmbio external table, política row, output table:

● Update(spec.md)
  ⎿  Added 3 lines, removed 2 lines
      73  
      74  ## 4. Entrada e saída
      75  
      76 -**Entrada:** conforme `exemplos/despesas-exemplo.json`, acresci
         -da do indicador de                                             
      77 -viagem (ver AMB-008). Campos e significado:                    
      76 +**Entrada:** conforme `exemplos/despesas-exemplo.json` e `exemp
         +los/despesas-envelope.json`                                    
      77 +(este com despesas em moeda estrangeira). Não há mais campo de 
         +topo `em_viagem`                                               
      78 +(ver AMB-008/AMB-016). Campos e significado:                   
      79  
      80  | Campo | Tipo | Significado | Obrigatório |
      81  |---|---|---|---|

● Update(spec.md)
  ⎿  Added 3 lines, removed 3 lines
      85  | `periodo.competencia` | texto `YYYY-MM` | Rótulo da competênc
          ia | sim |
      86  | `periodo.inicio` | data `YYYY-MM-DD` | Primeiro dia elegível 
          (inclusive) | sim |
      87  | `periodo.fim` | data `YYYY-MM-DD` | Último dia elegível (incl
          usive) | sim |
      88 -| `em_viagem` | booleano | Se toda a competência deste input é 
         -em viagem (default `false` quando ausente) | não |             
      88  | `despesas[].id` | texto | Identificador do registro (não é ca
          mpo de negócio, ver AMB-002) | sim |
      90 -| `despesas[].data` | data `YYYY-MM-DD` | Dia civil da despesa 
         -| sim |                                                        
      89 +| `despesas[].data` | data `YYYY-MM-DD` | Dia civil da despesa;
         + também é a data usada para resolver a taxa de câmbio (RN-019) 
         +| sim |                                                        
      90  | `despesas[].categoria` | texto | Categoria declarada | sim |
      91  | `despesas[].descricao` | texto | Descrição livre | sim |
      92  | `despesas[].fornecedor` | texto | Fornecedor | sim |
      94 -| `despesas[].valor` | número | Valor em BRL | sim |           
      93 +| `despesas[].valor` | número | Valor **na moeda do registro** 
         +(ver `moeda`); convertido para a base antes das regras monetári
         +as (RN-018) | sim |                                            
      94 +| `despesas[].moeda` | texto | Moeda do `valor` (ex.: `USD`, `E
         +UR`). Ausente ou igual à `moeda_base` do câmbio → sem conversão
         + e **não** é viagem; diferente da base → convertido pela taxa e
         + marcado **em viagem** por registro (RN-018, RN-009) | não |   
      95  | `despesas[].tem_nota_fiscal` | booleano | Se há nota fiscal a
          nexada | sim |
      96  
      97  **Política externa (fonte da verdade de categorias e limites):*
          * um arquivo

● Update(spec.md)
  ⎿  Added 14 lines, removed 1 line
      109  | `<CC>.<categoria>.periodicidade` | `"dia"` (limite sobre a s
           oma da categoria por dia civil) ou `"diaria"` (limite por regi
           stro) — ver RN-016 |
      110  | `<CC>.<categoria>.observacao` | Texto opcional usado como mo
           tivo quando o limite ≤ 0 (RN-017) |
      111  | `nota_fiscal_obrigatoria_acima_de` | Valor acima do qual a n
           ota fiscal é obrigatória (RN-006) |
      112 -| `acrescimo_em_viagem_percentual` | Percentual de acréscimo a
          -plicado aos limites quando `em_viagem = true` (RN-009) |      
      112 +| `acrescimo_em_viagem_percentual` | Percentual de acréscimo a
          +plicado ao limite dos registros **em viagem** (RN-009) |      
      113  
      114 +**Câmbio externo (fonte da verdade de moeda base e taxas):** u
          +m arquivo versionado                                          
      115 +(`cambio.json`) fornece a `moeda_base` de referência e as taxa
          +s de conversão por data.                                      
      116 +Estrutura relevante:                                          
      117 +                                                              
      118 +| Elemento | Significado |                                    
      119 +|---|---|                                                     
      120 +| `moeda_base` | Moeda de referência do sistema (ex.: `BRL`). 
          +É esta, **não** a `moeda_base` da política, que define o que é
          + "sem conversão" e o que é "viagem" (RN-018) |                
      121 +| `taxas.<AAAA-MM-DD>` | Mapa de cotações daquela data: `<MOED
          +A> → fator` (quantas unidades de `moeda_base` por 1 unidade da
          + moeda). Ex.: `2026-07-24: { "USD": 5.46, "EUR": 5.97 }` |    
      122 +| `taxas.<data>.<moeda>` | Fator de conversão de `moeda` para 
          +`moeda_base` naquela data (RN-018, RN-019) |                  
      123 +                                                              
      124 +Cotações existem apenas em dias úteis; datas sem taxa (fins de
          + semana/feriados) são                                         
      125 +resolvidas pela data mais próxima que tenha a moeda (RN-019). 
      126 +                                                              
      127  **Saída:** definida por mim. Estrutura e significado de cada c
           ampo:
      128  
      129  | Campo | Tipo | Significado |

● Update(spec.md)
  ⎿  Added 2 lines, removed 3 lines
      134  | `competencia` | texto | Competência processada (eco do input
           ) |
      135  | `periodo.inicio` | data `YYYY-MM-DD` | Primeiro dia elegível
            (eco do input) |
      136  | `periodo.fim` | data `YYYY-MM-DD` | Último dia elegível (eco
            do input) |
      137 -| `em_viagem` | booleano | Indicador de viagem aplicado |     
      137  | `categorias.<cat>` | objeto | Um bloco por categoria **válid
           a para o centro de custo que tenha ao menos uma despesa no inp
           ut** (ver RN-016, AMB-015). Categorias com limite ≤ 0 também a
           parecem quando têm despesas, com totais aceito/reembolso zerad
           os (AMB-014) |
      139 -| `categorias.<cat>.total_despesas` | número | Soma do `valor`
          - de **todas** as despesas da categoria, aceitas **e** reprovad
          -as, **exceto valores ≤ 0** (após arredondamento). Vale a invar
          -iante `total_despesas ≥ total_aceito ≥ total_reembolso`. Ver A
          -MB-012, RN-014 |                                              
      140 -| `categorias.<cat>.total_aceito` | número | Soma do `valor` d
          -as despesas **aceitas** da categoria (após arredondamento) |  
      138 +| `categorias.<cat>.total_despesas` | número | Soma do `valor`
          + **já convertido para a moeda base** de **todas** as despesas 
          +da categoria, aceitas **e** reprovadas, **exceto valores ≤ 0 e
          + exceto "cambio não identificado"** (não conversível). Vale a 
          +invariante `total_despesas ≥ total_aceito ≥ total_reembolso`. 
          +Ver AMB-012, AMB-017, RN-014 |                                
      139 +| `categorias.<cat>.total_aceito` | número | Soma do `valor` c
          +onvertido das despesas **aceitas** da categoria (após arredond
          +amento) |                                                     
      140  | `categorias.<cat>.total_reembolso` | número | Soma efetivame
           nte reembolsável da categoria (após aplicação de limites) |
      141  | `categorias.<cat>.reprovadas[]` | lista | Despesas recusadas
            cuja categoria declarada é essa categoria válida, cada uma co
           m `id` e `motivo` |
      142  | `reprovadas_sem_categoria[]` | lista | Despesas recusadas po
           r categoria não aplicável (categoria que não pertence ao conju
           nto do centro de custo), com `id`, `categoria_informada` e `mo
           tivo` |

● Batch 3 — example caption/JSON, currency worked example note:

● Update(spec.md)
  ⎿  Added 5 lines, removed 3 lines
      143  | `total_reembolso_geral` | número | Soma de `total_reembolso`
            de **todas** as categorias presentes na saída |
      144  
      145  Exemplo de saída (para o input de `exemplos/despesas-exemplo.j
           son`, centro de
      146 -custo `CC-ENG-PLATAFORMA`, `em_viagem = false`). Na política v
          -igente esse centro                                            
      147 -tem `alimentacao` limite 75,00 (dia), `transporte_urbano` limi
          -te 80,00 (dia) e                                              
      148 -`hospedagem` limite 0,00 (diaria, `observacao` "nao reembolsav
          -el"):                                                         
      146 +custo `CC-ENG-PLATAFORMA`). Nenhum registro deste input traz `
          +moeda`, então todos                                           
      147 +ficam na moeda base e **nenhum é em viagem** (RN-018/RN-009) —
          + a saída é idêntica à                                         
      148 +da versão anterior. Na política vigente esse centro tem `alime
          +ntacao` limite 75,00                                          
      149 +(dia), `transporte_urbano` limite 80,00 (dia) e `hospedagem` l
          +imite 0,00 (diaria,                                           
      150 +`observacao` "nao reembolsavel"):                             
      151  
      152  ```json
      153  {

● Update(spec.md)
  ⎿  Removed 1 line
      161      "inicio": "2026-07-01",
      162      "fim": "2026-07-31"
      163    },
      164 -  "em_viagem": false,                                         
      164    "categorias": {
      165      "alimentacao": {
      166        "total_despesas": 402.83,

● Update(spec.md)
  ⎿  Added 9 lines
      213  > reembolso 75,00; 07-31: 61,00 → reembolso 61,00) e hospedage
           m ficou não
      214  > reembolsável (limite 0,00), reduzindo `total_reembolso_geral
           ` de 585,43 para
      215  > 351,43.
      216 +>                                                             
      217 +> **Nota sobre câmbio (input `exemplos/despesas-envelope.json`
          +, `CC-COMERCIAL`):**                                          
      218 +> ali há despesas em moeda estrangeira. Ex.: `e-002` `alimenta
          +cao` EUR 22,00 em                                             
      219 +> 2026-07-14 (taxa EUR 5,93) → 130,46 em base; como é viagem, 
          +o limite de                                                   
      220 +> `alimentacao` (90,00) vira 135,00 e a despesa é aceita. `e-0
          +06` `representacao`                                           
      221 +> GBP 55,00: GBP não existe em nenhuma data de `taxas` → recus
          +ada                                                           
      222 +> "cambio não identificado" sob `representacao`, fora de `tota
          +l_despesas` (AMB-017).                                        
      223 +> `e-010` sem `moeda` → base, não é viagem. O golden completo 
          +desse input é                                                 
      224 +> calculado na fase de plano/quickstart.                      
      225  
      226  ---
      227  
● Batch 4 — RN-006, RN-008, RN-009 (rewrite), RN-011, RN-002 (baldes note):

● Update(spec.md)
  ⎿  Added 4 lines, removed 1 line
      292  excedente não é reembolsado; o reembolso do dia é `min(soma_do
           _dia, limite)`. A
      293  regra não conhece nem cita categoria alguma — aplica-se a toda
            categoria "dia",
      294  existente hoje ou adicionada no futuro. (Na política vigente, 
           `alimentacao`,
      295 -`transporte_urbano` e `representacao` são "dia".)             
      295 +`transporte_urbano` e `representacao` são "dia".) Quando o dia
          + mistura registros em                                         
      296 +viagem e não-viagem (RN-009), o teto é aplicado em **baldes se
          +parados** por status de                                       
      297 +viagem — cada balde sob seu próprio limite — e o reembolso do 
          +dia é a soma dos baldes                                       
      298 +(AMB-016).                                                    
      299  **Origem:** política do RH, "limite por dia" + "despesas acima
            do limite são reembolsadas parcialmente"; limite e periodicid
           ade vindos da política externa (RN-004, RN-015, RN-016).
      300  **Aceite:** categoria "dia" com limite 75,00, 72,50 + 38,00 no
            mesmo dia →
      301  total aceito 110,50, reembolso 75,00; com limite 80,00, uma de
           spesa aceita de

● Update(spec.md)
  ⎿  Added 8 lines, removed 5 lines
      335  
      336  ### RN-006 — Nota fiscal obrigatória
      337  **Regra:** Nota fiscal é obrigatória para valores **estritamen
           te acima** do
      338 -parâmetro `nota_fiscal_obrigatoria_acima_de` da política (R$ 1
          -00,00 na v4). No                                              
      339 -valor exato do limiar não é necessária. Se obrigatória e ausen
          -te                                                            
      340 -(`tem_nota_fiscal = false`), a despesa é recusada com motivo "
          -sem nota fiscal                                               
      341 -obrigatória" e reembolsa 0 (ver AMB-004).                     
      338 +parâmetro `nota_fiscal_obrigatoria_acima_de` da política (R$ 1
          +00,00 na v4). A                                               
      339 +comparação usa o **valor já convertido para a moeda base** (RN
          +-018): a checagem de                                          
      340 +nota fiscal ocorre **após** a conversão de câmbio. No valor ex
          +ato do limiar não é                                           
      341 +necessária. Se obrigatória e ausente (`tem_nota_fiscal = false
          +`), a despesa é                                               
      342 +recusada com motivo "sem nota fiscal obrigatória" e reembolsa 
          +0 (ver AMB-004).                                              
      343  **Origem:** política do RH, "Nota fiscal é obrigatória acima d
           e um valor base"; valor vindo da política externa (RN-015).
      343 -**Aceite:** com limiar 100,00: 100,00 sem NF → aceita; 100,01 
          -sem NF → recusada.                                            
      344 +**Aceite:** com limiar 100,00: valor convertido 100,00 sem NF 
          +→ aceita; 100,01 sem                                          
      345 +NF → recusada. `e-005` USD 40,00 (07-20) converte a 220,00 → N
          +F obrigatória; sem NF →                                       
      346 +recusada.                                                     
      347  
      348  ### RN-007 — Período de competência
      349  **Regra:** Só são elegíveis despesas cuja `data` esteja no int
           ervalo

● Update(spec.md)
  ⎿  Added 3 lines, removed 1 line
      355  ### RN-008 — Duplicatas
      356  **Regra:** Dois registros são duplicados quando todos os campo
           s de negócio são
      357  iguais (`data`, `categoria` normalizada, `descricao`, `fornece
           dor`, `valor`,
      358 -`tem_nota_fiscal`), ignorando o `id`. Duplicatas colapsam em u
          -m único registro:                                             
      358 +`moeda` normalizada, `tem_nota_fiscal`), ignorando o `id`. Com
          +para-se o `valor` e a                                         
      359 +`moeda` **de origem** (antes da conversão), de modo que dois r
          +egistros iguais salvo a                                       
      360 +moeda **não** são duplicados. Duplicatas colapsam em um único 
          +registro:                                                     
      361  mantém-se a **primeira ocorrência na ordem do input** e cada c
           ópia seguinte é
      362  recusada com motivo "registro duplicado" (ver AMB-002).
      363  **Origem:** política do RH, "Duplicatas devem ser tratadas".

● Update(spec.md)
  ⎿  Added 19 lines, removed 10 lines
      363  **Origem:** política do RH, "Duplicatas devem ser tratadas".
      364  **Aceite:** `d-006` e `d-007` (idênticos exceto `id`) → `d-006
           ` (primeiro) é aceito, `d-007` é "registro duplicado".
      365  
      366 -### RN-009 — Limites ampliados em viagem                      
      367 -**Regra:** Se `em_viagem = true`, os limites de **todas as cat
          -egorias** do centro                                           
      368 -de custo são multiplicados por `(1 + acrescimo_em_viagem_perce
          -ntual / 100)` (na                                             
      369 -v4, +50% → ×1,5). O limiar de nota fiscal **não** é ampliado. 
          -Uma categoria com                                             
      370 -limite ≤ 0 permanece não reembolsável (0 × qualquer fator = 0)
          -. O indicador vale                                            
      371 -para todas as despesas do input (ver AMB-008).                
      372 -**Origem:** política do RH, "Colaborador em viagem tem limites
          - ampliados"; percentual vindo da política externa (RN-015).   
      373 -**Aceite:** em viagem, `CC-ENG-PLATAFORMA` alimentação 75,00 →
          - 112,50; transporte                                           
      374 -80,00 → 120,00; hospedagem 0,00 → 0,00 (permanece não reembols
          -ável); limiar de NF                                           
      375 -continua 100,00.                                              
      366 +### RN-009 — Limite ampliado em viagem (por registro, pela moe
          +da)                                                           
      367 +**Regra:** A condição de viagem é **por registro** e derivada 
          +da moeda: um registro                                         
      368 +está **em viagem** quando tem `moeda` diferente da `moeda_base
          +` do câmbio (RN-018).                                         
      369 +Um registro **sem** `moeda`, ou com `moeda` igual à base, **nã
          +o** é viagem. Não existe                                      
      370 +mais indicador `em_viagem` de input nem viagem por competência
          + inteira (ver AMB-016,                                        
      371 +que substitui AMB-008).                                       
      372 +Para um registro em viagem, o `limite` da sua categoria é mult
          +iplicado por                                                  
      373 +`(1 + acrescimo_em_viagem_percentual / 100)` (na v4, +50% → ×1
          +,5); para um registro                                         
      374 +não-viagem vale o `limite` base. O acréscimo compara-se sempre
          + contra o **valor já                                          
      375 +convertido** para a base (RN-018). O limiar de nota fiscal **n
          +ão** é ampliado. Uma                                          
      376 +categoria com limite ≤ 0 permanece não reembolsável (0 × qualq
          +uer fator = 0).                                               
      377 +Quando uma categoria de periodicidade "dia" (RN-002) tem, no m
          +esmo dia, registros em                                        
      378 +viagem e não-viagem, aplicam-se **baldes separados** (AMB-016)
          +: cada grupo é limitado                                       
      379 +pelo seu próprio teto e o reembolso do dia é a soma dos dois. 
      380 +**Origem:** política do RH, "Colaborador em viagem tem limites
          + ampliados"; percentual da política externa (RN-015); redefini
          +ção por moeda (2026-07-31, ver AMB-016).                      
      381 +**Aceite:** `alimentacao` em `CC-COMERCIAL` (limite base 90,00
          +): registro em EUR                                            
      382 +convertido a 130,46 é viagem → limite 135,00 → aceito 130,46; 
          +registro em BRL de                                            
      383 +95,00 na mesma categoria não é viagem → limite 90,00; registro
          + sem `moeda` nunca é                                          
      384 +viagem. Categoria com limite ≤ 0 continua não reembolsável mes
          +mo em viagem.                                                 
      385  
      386  ### RN-010 — Valores inválidos
      387  **Regra:** Valor menor ou igual a zero é inválido; a despesa é
            recusada com

● Update(spec.md)
  ⎿  Added 4 lines, removed 2 lines
      392  ### RN-011 — Precisão monetária
      393  **Regra:** Todo valor é tratado com 2 casas decimais. Entradas
            com mais casas são
      394  arredondadas para 2 casas por arredondamento meio-para-cima (_
           half up_, afastando
      395 -de zero) **antes** de qualquer cálculo. Toda saída tem 2 casas
          - (ver AMB-007).                                               
      395 +de zero) **antes** de qualquer cálculo. Toda saída tem 2 casas
          + (ver AMB-007). Na                                            
      396 +conversão de câmbio (RN-018) arredonda-se o valor de origem a 
          +2 casas, multiplica-se                                        
      397 +pela taxa e arredonda-se o resultado a 2 casas (half-up) — ver
          + AMB-018.                                                     
      398  **Origem:** decisão — moeda tem precisão de centavo.
      397 -**Aceite:** 33,333 → 33,33.                                   
      399 +**Aceite:** 33,333 → 33,33; EUR 22,00 × 5,93 = 130,46.        
      400  
      401  ### RN-013 — Registro estruturalmente inválido
      402  **Regra:** Um registro cujo formato impede a avaliação — campo
            obrigatório

● Batch 5 — add RN-018 / RN-019 / RN-020 (after RN-014):

● Update(spec.md)
  ⎿  Added 47 lines
      436  **Aceite:** em `transporte_urbano` do exemplo: 100,00 + 100,01
            = 200,01 (o estorno
      437  `d-009` de −45,00 é excluído da somatória), com `total_aceito`
            100,00.
      438  
      439 +### RN-018 — Conversão de moeda para a base                   
      440 +**Regra:** Antes de qualquer regra monetária (nota fiscal, val
          +or, teto), o `valor` de                                       
      441 +cada registro é expresso na `moeda_base` do **`cambio.json`**:
      442 +- registro **sem** `moeda`, ou com `moeda` igual à `moeda_base
          +`: valor permanece como                                       
      443 +  está, **sem** conversão, e o registro **não** é viagem (RN-0
          +09);                                                          
      444 +- registro com `moeda` **diferente** da `moeda_base`: `valor_b
          +ase = valor × taxa`,                                          
      445 +  onde `taxa` é o fator da moeda na `data` do registro (RN-019
          +). Arredonda-se o valor                                       
      446 +  de origem a 2 casas, multiplica-se pela taxa e arredonda-se 
          +o resultado a 2 casas                                         
      447 +  (half-up, RN-011). Esse `valor_base` é o usado por todas as 
          +regras seguintes, nos                                         
      448 +  totais e no reembolso; o registro é marcado **em viagem** (R
          +N-009).                                                       
      449 +                                                              
      450 +A `moeda_base` de referência é sempre a do `cambio.json`; a `m
          +oeda_base` de                                                 
      451 +`politica-v4.json` é ignorada. A conversão ocorre logo após a 
          +validade da categoria                                         
      452 +(Seção 8), de modo que toda despesa de categoria válida tem um
          + valor em base.                                               
      453 +**Origem:** nova regra de câmbio (2026-07-31).                
      454 +**Aceite:** USD 40,00 em 2026-07-20 (taxa 5,50) → 220,00 em ba
          +se; BRL 95,00 (= base) →                                      
      455 +95,00 sem conversão; registro sem `moeda` → valor inalterado, 
          +não é viagem.                                                 
      456 +                                                              
      457 +### RN-019 — Resolução da taxa por data                       
      458 +**Regra:** A taxa de um registro é buscada em `cambio.json` pe
          +la `moeda` do registro                                        
      459 +na sua `data`:                                                
      460 +- se há taxa para a moeda naquela data exata, usa-se essa taxa
          +;                                                             
      461 +- senão — data sem cotação (fim de semana/feriado) **ou** moed
          +a não cotada naquela                                          
      462 +  data — usa-se a **data mais próxima** (menor diferença absol
          +uta em dias) que                                              
      463 +  **contenha aquela moeda**;                                  
      464 +- em **empate** (uma data anterior e uma posterior à mesma dis
          +tância), usa-se a                                             
      465 +  **menor** das duas taxas para aquela moeda.                 
      466 +                                                              
      467 +A busca considera apenas as datas de `taxas` que contêm a moed
          +a do registro.                                                
      468 +**Origem:** nova regra de câmbio (2026-07-31, ver AMB-017).   
      469 +**Aceite:** EUR em 2026-07-18 (sábado, sem cotação) → datas co
          +m EUR mais próximas são                                       
      470 +07-17 (dist. 1) e 07-20 (dist. 2) → usa 07-17 (EUR 5,96). Num 
          +empate hipotético entre                                       
      471 +07-17 (5,96) e 07-19 (6,00), usaria 5,96 (a menor).           
      472 +                                                              
      473 +### RN-020 — Câmbio não identificado                          
      474 +**Regra:** Se a `moeda` de um registro (diferente da base) **n
          +ão existe em nenhuma                                          
      475 +data** de `taxas`, o valor não pode ser convertido e a despesa
          + é recusada com motivo                                        
      476 +"cambio não identificado", reembolso 0. Como a validade da cat
          +egoria é avaliada antes                                       
      477 +(Seção 8), se a categoria é válida a recusa vai **sob a própri
          +a categoria**                                                 
      478 +(`categorias.<cat>.reprovadas[]`) e o valor é **excluído de `t
          +otal_despesas`** (não há                                      
      479 +valor em base para somar — ver AMB-017); se a categoria não é 
          +aplicável, prevalece                                          
      480 +"categoria não aplicável" (RN-001). Este motivo prevalece sobr
          +e duplicata, período,                                         
      481 +valor e nota fiscal.                                          
      482 +**Origem:** nova regra de câmbio (2026-07-31, ver AMB-017).   
      483 +**Aceite:** `e-006` `representacao` GBP 55,00 (GBP ausente de 
          +todas as `taxas`) →                                           
      484 +"cambio não identificado" sob `representacao`, fora de `total_
          +despesas`.                                                    
      485 +                                                              
      486  ---
      487  
      488  ## 6. Ambiguidades identificadas e decisões

● Batch 6 — AMB-008 supersede note, AMB-010 range, add AMB-016/017/018:

● Update(spec.md)
  ⎿  Added 2 lines, removed 1 line
      545  **O que não está claro:** o exemplo não tem campo de viagem; o
           nde ele fica e se o limiar de NF também escala.
      546  **Decisão:** indicador é um campo booleano de topo `em_viagem`
            (default `false`), válido para todo o input; amplia os limite
           s de categoria pelo percentual `acrescimo_em_viagem_percentual
           `; o limiar de NF **não** escala. O exemplo representa uma com
           petência sem viagem.
      547  **Justificativa:** viagem amplia a tolerância de gasto, não a 
           obrigação fiscal.
      548 -**Regra afetada:** RN-009, RN-006.                            
      548 +**Substituída por AMB-016 (2026-07-31):** o campo de topo `em_
          +viagem` deixou de existir; viagem passou a ser **por registro*
          +*, derivada da moeda (moeda ≠ base). O acréscimo do percentual
          + e a não-ampliação do limiar de NF permanecem.                
      549 +**Regra afetada:** RN-009, RN-006 (histórico).                
      550  
      551  ### AMB-009 — Limites do período são inclusivos? Qual campo ma
           nda?
      552  **Texto original do RH:** "Despesas devem ser lançadas dentro 
           do período de competência."

● Update(spec.md)
  ⎿  Added 1 line, removed 1 line
      560  **O que não está claro:** `d-013` está no período mas é hosped
           agem não reembolsável e também sem NF; qual motivo reportar?
      561  **Decisão:** ordem fixa de avaliação (Seção 8); o **primeiro**
            portão que falha determina o motivo. A aplicabilidade da cate
           goria (existência + limite > 0) vem antes de duplicata/período
           /valor/NF; o teto só se aplica a despesas já aceitas.
      562  **Justificativa:** determinismo e auditabilidade — o mesmo inp
           ut sempre produz o mesmo motivo.
      563 -**Regra afetada:** RN-001..RN-017 (ordem de aplicação).       
      563 +**Regra afetada:** RN-001..RN-020 (ordem de aplicação).       
      564  
      565  ### AMB-011 — Onde reportar recusas de categoria não aplicável
      566  **Texto original do RH:** "para cada categoria válida ... desp
           esas reprovadas".

● Update(spec.md)
  ⎿  Added 23 lines
      599  **Justificativa:** mantém o comportamento anterior (a saída re
           flete o que foi lançado) e evita ruído de blocos vazios.
      600  **Regra afetada:** RN-012.
      601  
      602 +### AMB-016 — Viagem por moeda e teto de dia misto            
      603 +**Texto original da nova regra:** "Registros são em viagem se 
          +a moeda for diferente da `moeda_base` do `cambio.json`; a vali
          +dação de viagem passa a ser por registro; se não houver `moeda
          +`, não é viagem; o acréscimo considera o valor já convertido."
      604 +**O que não está claro:** numa categoria de periodicidade "dia
          +", um mesmo dia pode ter registros em viagem (limite ×fator) e
          + não-viagem (limite base); como aplicar um teto que é agregado
          + por dia se os limites diferem por registro? E o que a saída f
          +az com o antigo `em_viagem`?                                  
      605 +**Decisão:** (a) viagem é **por registro** (moeda ≠ base); sem
          + `moeda` ou moeda = base → não é viagem; (b) no teto "dia" com
          + dia misto, usam-se **baldes separados** — o dia é dividido po
          +r status de viagem, cada balde limitado pelo seu próprio teto 
          +(base ou amplificado) e o reembolso do dia é a soma dos baldes
          +; (c) a saída **remove** o campo `em_viagem` (era de input, ag
          +ora inexistente) e mantém todos os valores na moeda base conve
          +rtida, sem trilha de conversão por registro.                  
      606 +**Justificativa:** baldes preservam a semântica "cada gasto so
          +b o teto que lhe cabe" sem depender de ordenação; para registr
          +os únicos no dia (caso do envelope) o resultado coincide com a
          +plicar o limite do próprio registro. Remover `em_viagem` da sa
          +ída evita um agregado ambíguo agora que viagem é por registro.
      607 +**Alternativa considerada:** amplificar o limite do dia inteir
          +o se houver qualquer registro em viagem (ou só se todos forem)
          + — descartadas por premiar/punir o dia por causa de um único r
          +egistro de moeda estrangeira. Registrado em `DECISIONS.md`.   
      608 +**Regra afetada:** RN-009, RN-002, RN-018.                    
      609 +                                                              
      610 +### AMB-017 — Câmbio não identificado e resolução da data     
      611 +**Texto original da nova regra:** "Se a `moeda` não existir em
          + nenhuma `taxas`, recuse 'cambio não identificado'; se não hou
          +ver a data exata, use a mais próxima; empate → menor taxa; moe
          +da ausente na data → data mais próxima que a possua."         
      612 +**O que não está claro:** (a) onde reportar a despesa "cambio 
          +não identificado" e se ela entra em `total_despesas`, já que n
          +ão tem valor em base? (b) a busca da data mais próxima é irres
          +trita?                                                        
      613 +**Decisão:** (a) se a categoria é válida, a recusa vai **sob a
          + própria categoria** e o valor é **excluído de `total_despesas
          +`** (não é valorável em base — mesmo princípio de valores ≤ 0)
          +; se a categoria não é aplicável, prevalece "categoria não apl
          +icável"; (b) a busca da data mais próxima percorre todas as da
          +tas de `taxas` que contêm a moeda, sem janela; empate resolve 
          +pela **menor** taxa.                                          
      614 +**Justificativa:** manter a invariante `total_despesas ≥ total
          +_aceito` sem inventar um valor em base para algo inconversível
          +; a menor taxa no empate é conservadora para o reembolso.     
      615 +**Alternativa considerada:** reportar "cambio não identificado
          +" em `reprovadas_sem_categoria` — descartada quando a categori
          +a é de fato válida no centro de custo.                        
      616 +**Regra afetada:** RN-020, RN-019, RN-014.                    
      617 +                                                              
      618 +### AMB-018 — Arredondamento na conversão de câmbio           
      619 +**Texto original:** implícito — RN-011 fala em arredondar "ant
          +es de qualquer cálculo", mas a conversão é um cálculo intermed
          +iário.                                                        
      620 +**O que não está claro:** arredonda-se o valor de origem, o re
          +sultado, ou ambos? A taxa é arredondada?                      
      621 +**Decisão:** arredonda-se o **valor de origem** a 2 casas (RN-
          +011), multiplica-se pela **taxa cheia** do arquivo e arredonda
          +-se o **resultado** a 2 casas (half-up). Não se arredonda a ta
          +xa.                                                           
      622 +**Justificativa:** mantém precisão de centavo na entrada e na 
          +saída sem introduzir erro por arredondar a cotação; é o padrão
          + financeiro de conversão.                                     
      623 +**Regra afetada:** RN-018, RN-011.                            
      624 +                                                              
      625  ---
      626  
      627  ## 7. Casos de borda

● Batch 7 — Section 7 edge cases (replace travel row with per-record travel + 
  câmbio rows):

● Update(spec.md)
  ⎿  Added 8 lines, removed 1 line
      645  | Categoria em caixa alta | `d-014` `ALIMENTACAO` 61,00 | trat
           ada como `alimentacao` | RN-001 |
      646  | Data igual a `fim` | `d-014` 2026-07-31 | elegível (limite i
           nclusivo) | RN-007, RN-009 (AMB-009) |
      647  | Despesa aceita mas com reembolso 0 por teto já consumido | 3
           ª despesa de alimentação num dia já no teto | permanece **acei
           ta** (entra em `total_aceito`), reembolso 0 | RN-005 |
      648 -| Limites ampliados em viagem | `em_viagem = true`, alimentaçã
          -o 85,00 num dia (limite 75 → 112,50) | reembolso 85,00 | RN-00
          -9 |                                                           
      648 +| Registro em moeda estrangeira (viagem) | `e-002` EUR 22,00 e
          +m 07-14 (taxa 5,93), alimentação `CC-COMERCIAL` (limite 90 → v
          +iagem 135) | convertido 130,46; aceito 130,46 | RN-018, RN-009
          + |                                                            
      649 +| Registro em `moeda` = base | despesa BRL num sistema com `mo
          +eda_base` BRL | sem conversão; **não** é viagem | RN-018 |    
      650 +| Registro sem `moeda` | `e-010` sem campo `moeda` | valor ina
          +lterado; **não** é viagem | RN-018, RN-009 |                  
      651 +| Dia "dia" misto viagem/não-viagem | R1 BRL 80 (base) + R2 co
          +nvertido 80 (viagem), alimentação limite base 90 / viagem 135 
          +| baldes: min(80,90)+min(80,135) = 80+80 = 160 | RN-009, RN-00
          +2, AMB-016 |                                                  
      652 +| Data sem cotação (fim de semana) | EUR em 2026-07-18 (sábado
          +) | usa a data mais próxima com EUR: 07-17 (5,96) | RN-019 |  
      653 +| Empate de datas na taxa | data equidistante entre duas cotaç
          +ões da moeda | usa a **menor** das duas taxas | RN-019 |      
      654 +| Moeda ausente de todas as taxas | `e-006` `representacao` GB
          +P 55,00 | recusada "cambio não identificado" sob a categoria; 
          +fora de `total_despesas` | RN-020, AMB-017 |                  
      655 +| Nota fiscal avaliada após conversão | `e-005` USD 40,00 (07-
          +20 → 220,00) sem NF | recusada "sem nota fiscal obrigatória" (
          +220,00 > 100) | RN-006, RN-018 |                              
      656  
      657  ## 8. Ordem de aplicação das regras
      658  

● Batch 8 — Section 8 application order (insert câmbio step, per-record travel, 
  NF after conversion):

● Update(spec.md)
  ⎿  Added 23 lines, removed 15 lines
      665  2. **Resolução da política** — resolver o centro de custo (o d
           o input ou
      666     `padrao`) e carregar categorias, limites, periodicidades e 
           parâmetros globais
      667     (RN-015).
      668 -3. **Normalização** — arredondar `valor` para 2 casas (RN-011)
          -; aplicar `trim` e                                            
      669 -   caixa na `categoria` (RN-001); aplicar o acréscimo de viage
          -m aos limites se                                              
      670 -   `em_viagem` (RN-009).                                      
      668 +3. **Normalização** — arredondar o `valor` de origem para 2 ca
          +sas (RN-011); aplicar                                         
      669 +   `trim` e caixa na `categoria` (RN-001); determinar a `moeda
          +` e o **status de                                             
      670 +   viagem** do registro (moeda ≠ `moeda_base` do câmbio → viag
          +em; sem `moeda` ou moeda                                      
      671 +   = base → não-viagem) (RN-009, RN-018).                     
      672  4. **Categoria válida** — a categoria normalizada pertence ao 
           conjunto do centro
      673     de custo? senão "categoria não aplicável" (RN-001), em `rep
           rovadas_sem_categoria`.
      674  5. **Limite da categoria > 0** — se o `limite` da categoria fo
           r ≤ 0, recusa com
      675     motivo = `observacao` (ou "categoria não aplicável"), sob a
            própria categoria
      676     (RN-017).
      676 -6. **Deduplicação** — colapsar registros idênticos por campos 
          -de negócio,                                                   
      677 -   mantendo a primeira ocorrência; cada cópia seguinte → "regi
          -stro duplicado" (RN-008).                                     
      678 -7. **Período** — `data` em `[inicio, fim]`; senão "data fora d
          -a competência" (RN-007).                                      
      679 -8. **Valor válido** — `valor > 0`; senão "valor inválido" (RN-
          -010).                                                         
      680 -9. **Nota fiscal** — se `valor > nota_fiscal_obrigatoria_acima
          -_de`, exige NF;                                               
      681 -   senão "sem nota fiscal obrigatória" (RN-006).              
      682 -10. **Aplicação de teto** — as despesas que passaram de 1 a 9 
          -são **aceitas**; o                                            
      683 -    `limite` vem da entrada da categoria na política do centro
          - resolvido (RN-004) e                                         
      684 -    a mecânica é escolhida pela `periodicidade` (RN-016): agre
          -gando por dia civil                                           
      685 -    quando "dia" (RN-002) ou por registro quando "diaria" (RN-
          -003), sempre                                                  
      686 -    aplicando `min(soma_ou_valor, limite)` com reembolso parci
          -al no excedente (RN-005).                                     
      687 -11. **Agregação** — totais por categoria e total geral (RN-012
          -).                                                            
      677 +6. **Conversão de câmbio** — se `moeda` ≠ base, resolver a tax
          +a pela `data` (RN-019)                                        
      678 +   e converter o valor para a base (RN-018); se a moeda não ex
          +iste em nenhuma `taxas`                                       
      679 +   → "cambio não identificado" (RN-020), sob a própria categor
          +ia, fora de                                                   
      680 +   `total_despesas`. A partir daqui todo valor está na moeda b
          +ase.                                                          
      681 +7. **Deduplicação** — colapsar registros idênticos por campos 
          +de negócio (incluindo a                                       
      682 +   `moeda` de origem), mantendo a primeira ocorrência; cada có
          +pia seguinte →                                                
      683 +   "registro duplicado" (RN-008).                             
      684 +8. **Período** — `data` em `[inicio, fim]`; senão "data fora d
          +a competência" (RN-007).                                      
      685 +9. **Valor válido** — `valor > 0`; senão "valor inválido" (RN-
          +010).                                                         
      686 +10. **Nota fiscal** — usa o **valor convertido**; se `valor_ba
          +se > nota_fiscal_obrigatoria_acima_de`,                       
      687 +    exige NF; senão "sem nota fiscal obrigatória" (RN-006).   
      688 +11. **Aplicação de teto** — as despesas que passaram de 1 a 10
          + são **aceitas**; o                                           
      689 +    `limite` vem da entrada da categoria na política (RN-004),
          + **amplificado por                                            
      690 +    registro** quando em viagem (RN-009), e a mecânica é escol
          +hida pela                                                     
      691 +    `periodicidade` (RN-016): por dia civil quando "dia" (RN-0
          +02, com **baldes                                              
      692 +    separados** por status de viagem em dias mistos — AMB-016)
          + ou por registro quando                                       
      693 +    "diaria" (RN-003), sempre aplicando `min(soma_ou_valor, li
          +mite)` com reembolso                                          
      694 +    parcial no excedente (RN-005).                            
      695 +12. **Agregação** — totais por categoria e total geral, na moe
          +da base (RN-012).                                             
      696  
      697  ## 9. Critérios de aceite
      698  

● Batch 9 — Section 9 acceptance criteria:

● Update(spec.md)
  ⎿  Added 4 lines, removed 3 lines
      698  
      699  O sistema está pronto quando:
      700  
      701 -- [ ] Para o input de `exemplos/despesas-exemplo.json` (centro
          - `CC-ENG-PLATAFORMA`)                                         
      702 -      com `em_viagem = false`, a saída é exatamente a do exemp
          -lo da Seção 4                                                 
      703 -      (totais e recusas por categoria, `total_reembolso_geral 
          -= 351,43`).                                                   
      701 +- [ ] Para o input de `exemplos/despesas-exemplo.json` (centro
          + `CC-ENG-PLATAFORMA`),                                        
      702 +      cujos registros não têm `moeda` (todos na base, nenhum e
          +m viagem), a saída é                                          
      703 +      exatamente a do exemplo da Seção 4 (totais e recusas por
          + categoria,                                                   
      704 +      `total_reembolso_geral = 351,43`).                      
      705  - [ ] Categorias, limites, periodicidade, limiar de NF e acrés
           cimo de viagem são
      706        lidos da política externa, não codificados; um centro de
            custo desconhecido
      707        cai em `padrao` (RN-015).

● Update(spec.md)
  ⎿  Added 1 line, removed 1 line
      712        reembolsável, removê-la a torna "categoria não aplicável
           ", e mudar seu
      713        `limite`/`periodicidade` muda o resultado — tudo **sem a
           lterar regra ou
      714        código** (RN-001, RN-004, RN-015, RN-016).
      715 -- [ ] Cada uma das 17 regras (RN-001..RN-017) tem ao menos um 
          -teste com números.                                            
      715 +- [ ] Cada uma das 20 regras (RN-001..RN-020) tem ao menos um 
          +teste com números.                                            
      716  - [ ] A saída ecoa `colaborador` (`id`, `nome`, `centro_custo`
           ) e `periodo`
      717        (`inicio`, `fim`) do input.
      718  - [ ] Em toda categoria vale `total_despesas ≥ total_aceito ≥ 
           total_reembolso`, e

● Update(spec.md)
  ⎿  Added 2 lines, removed 2 lines
      726        uma despesa; categorias configuradas sem despesas não ap
           arecem.
      727  - [ ] Cada despesa recusada traz um dos motivos: "categoria nã
           o aplicável",
      728        "data fora da competência", "registro duplicado", "sem n
           ota fiscal
      729 -      obrigatória", "valor inválido", "registro inválido", ou 
          -a `observacao` da                                             
      730 -      categoria (limite ≤ 0).                                 
      729 +      obrigatória", "valor inválido", "registro inválido", "ca
          +mbio não identificado",                                       
      730 +      ou a `observacao` da categoria (limite ≤ 0).            
      731  - [ ] Um registro malformado é recusado ("registro inválido") 
           sem impedir o
      732        processamento das demais despesas do input.
      733  - [ ] Valor no limiar de NF sem NF é aceito e um centavo acima
            sem NF é recusado.

● Update(spec.md)  ⎿  Added 13 lines, removed 3 lines
      733  - [ ] Valor no limiar de NF sem NF é aceito e um centavo acima
            sem NF é recusado.
      734  - [ ] Uma despesa aceita cujo reembolso foi limitado pelo teto
            continua contando
      735        em `total_aceito` com seu valor cheio.
      736 -- [ ] Com `em_viagem = true`, os limites de cada categoria do 
          -centro escalam pelo                                           
      737 -      `acrescimo_em_viagem_percentual` (na v4, ×1,5) e o limia
          -r de NF permanece                                             
      738 -      inalterado; categorias com limite ≤ 0 continuam não reem
          -bolsáveis.                                                    
      736 +- [ ] Viagem é por registro: um registro com `moeda` ≠ base te
          +m o limite da sua                                             
      737 +      categoria ampliado pelo `acrescimo_em_viagem_percentual`
          + (na v4, ×1,5), o limiar                                      
      738 +      de NF **não** escala e categorias com limite ≤ 0 continu
          +am não reembolsáveis; um                                      
      739 +      registro sem `moeda` ou com moeda = base não é viagem. N
          +ão há mais `em_viagem`                                        
      740 +      no input nem na saída.                                  
      741 +- [ ] Num dia de categoria "dia" com registros em viagem e não
          +-viagem, o reembolso é a                                      
      742 +      soma de baldes separados (cada grupo sob seu próprio lim
          +ite).                                                         
      743 +- [ ] O valor de cada registro com `moeda` ≠ base é convertido
          + para a base (`cambio.json`)                                  
      744 +      usando a taxa da `data` ou da data mais próxima com aque
          +la moeda (empate → menor                                      
      745 +      taxa); a `moeda_base` é a do `cambio.json`, não a da pol
          +ítica; a NF é avaliada                                        
      746 +      sobre o valor convertido; e todos os totais de saída fic
          +am na base.                                                   
      747 +- [ ] Uma `moeda` ausente de todas as `taxas` gera recusa "cam
          +bio não identificado"                                         
      748 +      sob a categoria (se válida), fora de `total_despesas`.  
      749  - [ ] Todos os valores de saída têm exatamente 2 casas decimai
           s.
      750  - [ ] O resultado é determinístico: o mesmo input produz sempr
           e a mesma saída.
      751  

● Batch 10 — Section 10 open items (câmbio now in scope):

● Update(spec.md)
  ⎿  Added 6 lines, removed 4 lines
      761  - **Validação da política externa:** assume-se que o arquivo d
           e política está bem
      762    formado e vigente; não há verificação de consistência (limit
           es negativos além
      763    de 0, periodicidades desconhecidas, versão/vigência) nesta v
           ersão.
      764 -- **Câmbio:** a política declara `moeda_base` BRL e há um arqu
          -ivo de câmbio no                                              
      765 -  ambiente, mas conversão de moeda continua fora de escopo até
          - haver requisito.                                             
      766 -- **Moeda e fuso:** assume-se BRL e datas civis sem fuso horár
          -io; multi-moeda e                                             
      767 -  fuso ficam fora até haver requisito.                        
      764 +- **Validação do câmbio externo:** a conversão passa a ser fei
          +ta por `cambio.json`                                          
      765 +  (RN-018..RN-020), mas não há verificação de consistência do 
          +arquivo (taxas ≤ 0,                                           
      766 +  datas fora de ordem, moedas repetidas) nem busca de cotação 
          +fora dele; assume-se bem                                      
      767 +  formado. Uma moeda ausente de todas as datas é recusa de neg
          +ócio, não erro fatal.                                         
      768 +- **Fuso horário:** datas são civis, sem fuso; a taxa é resolv
          +ida pela `data` do                                            
      769 +  registro. Multi-fuso fica fora até haver requisito.         
      770  - **Vários inputs de uma mesma competência (viagem + não-viage
           m):** cada input é
      771    processado isoladamente; a consolidação entre inputs (se nec
           essária) não está
      772    especificada aqui.

● Now let me verify consistency across the whole spec — lingering em_viagem
  input references, rule-count, and câmbio wording:

  Ran 1 shell command (ctrl+o to expand)

● All references are consistent — remaining em_viagem mentions are the
  historical AMB-008, the AMB-016 explanation, the param name
  acrescimo_em_viagem_percentual, and the clarification log; no active
  input/output field remains. Rule count is now 20 (RN-001..RN-020).

  Now the DECISIONS.md entry and checklist refresh:

● Update(DECISIONS.md)
  ⎿  Added 59 lines
      10  
      11  ---
      12  
      13 +## D-007 — Conversão de câmbio (`cambio.json`) e viagem por moe
         +da · `2026-07-31`                                              
      14 +                                                               
      15 +**Gatilho:** pedido do usuário via `/speckit-specify`: despesas
         + podem vir em moeda                                            
      16 +estrangeira e devem ser convertidas para a moeda base por uma t
         +abela de câmbio externa                                        
      17 +(`src/informacoes_externas/cambio.json`); e a condição de "em v
         +iagem" deixa de ser um                                         
      18 +input e passa a ser derivada **por registro** (moeda ≠ base).  
      19 +                                                               
      20 +**O que mudou na spec (versão 1.3 → 1.4):**                    
      21 +- **Novas RN-018/019/020:** conversão para a base (RN-018), res
         +olução da taxa por data                                        
      22 +  com data mais próxima e desempate pela menor taxa (RN-019), e
         + recusa                                                        
      23 +  "cambio não identificado" para moeda ausente de todas as `tax
         +as` (RN-020). O conjunto                                       
      24 +  passou de 17 para **20 regras**.                             
      25 +- **RN-009 reescrita:** viagem é **por registro** (moeda ≠ `moe
         +da_base` do câmbio); some                                      
      26 +  o `em_viagem` de input; o acréscimo incide sobre o valor já c
         +onvertido; a `moeda_base`                                      
      27 +  de referência é a do `cambio.json` (a da política é ignorada)
         +.                                                              
      28 +- **RN-006:** o limiar de NF é comparado contra o **valor conve
         +rtido** (NF após conversão).                                   
      29 +- **RN-008:** a chave de duplicidade inclui a `moeda` de origem
         +.                                                              
      30 +- **RN-011:** arredondamento da conversão (origem → ×taxa → res
         +ultado, half-up).                                              
      31 +- **RN-002:** dia misto viagem/não-viagem usa **baldes separado
         +s**.                                                           
      32 +- **Seção 4:** nova coluna `despesas[].moeda` (opcional), remoç
         +ão do `em_viagem` de                                           
      33 +  input e de saída, nova tabela do `cambio.json`, totais declar
         +ados em moeda base, e                                          
      34 +  nota de conversão para o `despesas-envelope.json`.           
      35 +- **Seção 8:** novo passo 6 "Conversão de câmbio" (após validad
         +e da categoria/limite,                                         
      36 +  antes de duplicata/período/valor/NF), NF passa a usar o valor
         + convertido, teto com                                          
      37 +  limite amplificado por registro e baldes no "dia".           
      38 +- **Novas AMB-016/017/018** e **AMB-008 marcada como substituíd
         +a** (viagem por moeda).                                        
      39 +- **Seção 9:** critérios de câmbio, viagem por registro, baldes
         + e "cambio não                                                 
      40 +  identificado"; motivo novo na lista; contagem 17 → 20. **Seçã
         +o 10:** câmbio sai de                                          
      41 +  "em aberto" (agora implementado por `cambio.json`), resta a n
         +ão-validação do arquivo.                                       
      42 +                                                               
      43 +**Decisões tomadas com o usuário (Clarifications Session 2026-0
         +7-31 — câmbio e viagem):**                                     
      44 +- **AMB-016** — dia "dia" misto → **baldes separados**; saída *
         +*remove** `em_viagem`.                                         
      45 +- **AMB-017** — "cambio não identificado" fica **sob a categori
         +a** (se válida) e é                                            
      46 +  **excluído de `total_despesas`**; busca de data mais próxima 
         +irrestrita, empate → menor.                                    
      47 +- **AMB-018** — arredonda origem (2c) → × taxa cheia → arredond
         +a resultado (2c).                                              
      48 +                                                               
      49 +**Contexto do envelope:** o `despesas-envelope.json` (CC-COMERC
         +IAL) foi usado para                                            
      50 +validar: `e-006` GBP não está em nenhuma `taxas` (→ "cambio não
         + identificado"); `e-004`                                       
      51 +EUR num sábado (→ data mais próxima 07-17); `e-010` sem `moeda`
         + (→ base, não viagem).                                         
      52 +O arquivo **não** contém dia+categoria com moedas mistas, então
         + o teto de dia misto é                                         
      53 +uma regra de robustez (não exercitada pelos goldens atuais).   
      54 +                                                               
      55 +**O que isso invalida na implementação:** `io_json.py`/`cli.py`
         + não leem `cambio.json`                                        
      56 +nem aceitam `moeda`; `regras.py`/`politica.py` não convertem, t
         +ratam viagem como flag de                                      
      57 +input e não têm gate de câmbio; a saída ainda emite `em_viagem`
         +. Tudo isso precisa ser                                        
      58 +refeito via `/speckit-plan` → `/speckit-tasks` → `/speckit-impl
         +ement`. **Este passo                                           
      59 +alterou apenas `spec.md`, `checklists/requirements.md` e este l
         +og.**                                                          
      60 +                                                               
      61 +**Tasks afetadas:** leitura/validação do `cambio.json`; parsing
         + do campo `moeda`; gate de                                     
      62 +conversão e "cambio não identificado" na ordem nova; NF sobre v
         +alor convertido; viagem e                                      
      63 +teto por registro com baldes; remoção de `em_viagem` do contrat
         +o de saída; golden do                                          
      64 +`despesas-envelope.json` calculado no plano/quickstart.        
      65 +                                                               
      66 +**Custo:** 3 arquivos (`spec.md`, `checklists/requirements.md`,
         + `DECISIONS.md`); na spec,                                     
      67 +~20 blocos (3 RNs novas, 5 RNs reescritas, 3 AMBs novas + 1 sub
         +stituída, Seções 2/3/4/7/8/9/10                                
      68 +e o exemplo).                                                  
      69 +                                                               
      70 +---                                                            
      71 +                                                               
      72  ## D-006 — Regras de teto agnósticas de categoria (RN-002/003/0
          04 por papel) · `2026-07-31`
      73  
      74  **Gatilho:** pedido do usuário via `/speckit-specify`: o sistem
          a não deve conhecer

● Update(checklists\requirements.md)
  ⎿  Added 1 line, removed 1 line
      1  # Specification Quality Checklist: Motor de Cálculo de Reembolso
      2  
      3  **Purpose**: Validate specification completeness and quality bef
         ore proceeding to planning
      4 -**Created**: 2026-07-30 · **Atualizado**: 2026-07-31 (regras de 
        -teto agnósticas de categoria)                                   
      4 +**Created**: 2026-07-30 · **Atualizado**: 2026-07-31 (conversão 
        +de câmbio e viagem por moeda)                                   
      5  **Feature**: [spec.md](../spec.md)
      6  
      7  ## Content Quality

● Update(checklists\requirements.md)
  ⎿  Added 8 lines
      47    teto (limite pela política). Nenhuma regra conhece nome de ca
          tegoria; o conjunto,
      48    limites e periodicidades vêm inteiramente de `politica-v4.jso
          n` e mudam o resultado
      49    sem alteração de código. Novo critério de aceite na Seção 9 c
          obre essa resiliência.
      50 +- Atualização 2026-07-31 (spec 1.3 → 1.4, ver DECISIONS D-007):
         + novas RN-018/019/020                                          
      51 +  de câmbio (`cambio.json`) — conversão para a base, taxa por d
         +ata mais próxima                                               
      52 +  (empate → menor) e "cambio não identificado"; RN-009 reescrit
         +a para **viagem por                                            
      53 +  registro** (moeda ≠ base), sem `em_viagem` no input nem na sa
         +ída; NF avaliada após a                                        
      54 +  conversão; dia "dia" misto por **baldes separados**. Três dec
         +isões fechadas com o                                           
      55 +  usuário (AMB-016/017/018) e o `despesas-envelope.json` usado 
         +para validar os casos                                          
      56 +  (GBP não identificado, EUR em fim de semana, registro sem `mo
         +eda`). Conjunto de                                             
      57 +  regras 17 → 20.                                              
      58  - A divergência da letra do RH em hospedagem ("por diária" → "p
          or registro",
      59    AMB-006) deve ser registrada em `DECISIONS.md` na fase de pla
          no/implementação.
      60  - Items marked incomplete require spec updates before `/speckit
          -clarify` or `/speckit-plan`.

● Batch 11 — final consistency check:

  Ran 1 shell command (ctrl+o to expand)

● Tudo consistente. Sem .specify/extensions.yml → não há hooks de pré/pós
  execução. A validação de qualidade passa (sem marcadores [NEEDS 
  CLARIFICATION], requisitos testáveis com números, bordas cobertas, escopo
  delimitado, sem detalhes de implementação).

  Concluído — spec atualizada (câmbio + viagem por moeda)

  SPECIFY_FEATURE_DIRECTORY: specs/001-motor-reembolso
  SPEC_FILE: specs/001-motor-reembolso/spec.md (versão 1.3 → 1.4)

  3 regras novas (conjunto passou de 17 → 20):
  - RN-018 — Conversão para a base: registro com moeda ≠ base é convertido por
  cambio.json antes das regras monetárias; sem moeda ou moeda = base → sem
  conversão. A moeda_base é a do cambio.json (a da política é ignorada).
  - RN-019 — Taxa por data: data exata; senão a data mais próxima com aquela
  moeda; empate → menor taxa.
  - RN-020 — "cambio não identificado": moeda ausente de todas as taxas →
  recusa, sob a categoria (se válida), fora de total_despesas.

  Regras alteradas:
  - RN-009 reescrita: viagem por registro (moeda ≠ base); acabou o em_viagem de
  input/saída; acréscimo sobre o valor convertido; baldes separados em dias
  "dia" mistos.
  - RN-006 (NF sobre valor convertido), RN-008 (moeda na chave de duplicidade),
  RN-011 (arredondamento da conversão), RN-002 (nota de baldes).

  Decisões que você fechou: baldes separados (dia misto), remover em_viagem da
  saída com totais em BRL — registradas em AMB-016. Defaults que assumi e
  documentei: câmbio-não-identificado sob a categoria e fora do total (AMB-017),
  arredondamento origem→×taxa→resultado (AMB-018). AMB-008 marcada como
  substituída.

  Também atualizei Seções 3/4/7/8/9/10 (nova tabela do cambio.json, coluna
  despesas[].moeda, ordem de aplicação com o passo de conversão, bordas de
  EUR/USD/GBP/fim-de-semana, critérios de aceite), registrei D-007 em
  DECISIONS.md e a nota na checklist.

  Ponto que deixei explícito na spec: o despesas-exemplo.json não tem moeda → o
  golden segue 351,43 inalterado. O despesas-envelope.json (CC-COMERCIAL, com
  EUR/USD/GBP) foi usado para validar os casos, mas não tem dia+categoria com
  moedas mistas, então a regra de baldes é robustez não exercitada; o golden
  completo do envelope fica para a fase de plano/quickstart.

  Checklist: todos os itens ✓. Sem clarificações pendentes.

  Aviso de divergência (registrado em D-007): a implementação atual não lê
  cambio.json, não aceita moeda, trata viagem como flag de input e ainda emite
  em_viagem. A spec agora exige o contrário.

  Próximo passo recomendado: /speckit-plan para regenerar plan.md/tasks.md e
  alinhar a implementação (que hoje diverge em câmbio e viagem).

✻ Worked for 9m 26s

※ recap: You're evolving the reimbursement engine's spec via speckit. Spec v1.4 is done: added currency conversion rules (RN-018/019/020) and made "em viagem" per-record by currency. Next, run /speckit-plan to regenerate plan and tasks, since the code still diverges. (disable recaps in /config)

❯ /speckit-clarify                                                              

● I'll run the clarify workflow. First, the prerequisite check and loading the
  current spec.

  Ran 2 shell commands (ctrl+o to expand)

● No pwsh, but feature.json already gives me the paths. Let me load the
  constitution (it exists) and confirm the spec path.

  Read 1 file (ctrl+o to expand)

● The constitution is an unfilled template (no governance constraints);
  CLAUDE.md is the effective rulebook. I have the full v1.4 spec in context and
  ran a structured ambiguity scan. The pre-câmbio parts are heavily clarified
  (AMB-001..018). The scan surfaced genuine gaps only in the new câmbio/viagem 
  area: (1) how moeda is matched against moeda_base/taxas keys, (2) the failure
  contract when the câmbio file/lookup can't produce a rate, (3) handling of a
  malformed moeda value.

  I'll ask up to a few, one at a time.

  ---
  Question: Ao comparar o campo moeda de um registro com a moeda_base e com as
  chaves de moeda em taxas, o valor deve ser normalizado (remover espaços das
  pontas e ignorar maiúsculas/minúsculas) ou comparado exatamente como veio?

  Why it matters: decide se " usd " ou "usd" são reconhecidos como USD
  (convertidos normalmente) ou viram "cambio não identificado" — e o mesmo vale
  para reconhecer que a moeda é a base (sem conversão). Erro aqui recusa
  despesas legítimas ou dispara conversões indevidas.

  Recommended: Option A — normalizar (trim + uppercase). É coerente com a
  normalização que a categoria já recebe (RN-001/AMB-003): caixa e espaço são
  artefatos de digitação, não distinção de negócio; cambio.json usa chaves em
  caixa alta (USD, EUR).

  ┌────────┬─────────────────────────────────────────────────────────────────┐
  │ Option │                           Description                           │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │ A      │ Normalizar moeda: trim + caixa alta antes de comparar com       │
  │        │ moeda_base e com as chaves de taxas (ex.: " usd " → USD)        │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │        │ Comparação exata, sensível a caixa/espaços: só bate se idêntico │
  │ B      │  às chaves; qualquer variação vira "cambio não identificado"    │
  │        │ (ou não-base)                                                   │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │ Short  │ Provide a different short answer (≤5 words)                     │
  └────────┴─────────────────────────────────────────────────────────────────┘

  You can reply with the option letter (e.g., "A"), accept the recommendation by
  saying "yes" or "recommended", or provide your own short answer.

✻ Cogitated for 1m 28s

❯ A                                                                             

● A confirmed — normalize moeda (trim + uppercase). Integrating into the spec
  now.

● Update(spec.md)
  ⎿  Added 4 lines
      53  - Q: Um registro cuja `moeda` não existe em nenhuma data de `ta
          xas` ("cambio não identificado") é reportado onde e entra em `t
          otal_despesas`? → A: Se a categoria for válida, entra em `categ
          orias.<cat>.reprovadas[]`; é **excluído de `total_despesas`** (
          não há valor em base para somar), pelo mesmo princípio de não-v
          alorável usado para valores ≤ 0.
      54  - Q: Como e quando arredondar na conversão? → A: Arredonda o `v
          alor` na moeda de origem a 2 casas (RN-011), multiplica pela ta
          xa e arredonda o resultado a 2 casas (half-up); o valor convert
          ido em base é o usado por todas as regras monetárias seguintes.
      55  
      56 +### Session 2026-07-31 (clarify)                               
      57 +                                                               
      58 +- Q: Ao comparar `moeda` com a `moeda_base` e com as chaves de 
         +`taxas`, normaliza-se o valor ou compara-se exatamente? → A: **
         +Normalizar** — `trim` + caixa alta antes de qualquer comparação
         + (ex.: `" usd "` → `USD`), do mesmo modo que a `categoria` (AMB
         +-003). Só assim se decide "sem conversão" (= base), "converter"
         + (moeda válida nas taxas) ou "cambio não identificado".        
      59 +                                                               
      60  ## 3. Fora de escopo
      61  
      62  - Não calcula estornos, créditos ou saldos negativos — o sistem
          a só produz

● Update(spec.md)
  ⎿  Added 4 lines, removed 1 line
      442  
      443  ### RN-018 — Conversão de moeda para a base
      444  **Regra:** Antes de qualquer regra monetária (nota fiscal, val
           or, teto), o `valor` de
      445 -cada registro é expresso na `moeda_base` do **`cambio.json`**:
      445 +cada registro é expresso na `moeda_base` do **`cambio.json`**.
          + A `moeda` é                                                  
      446 +**normalizada** (remoção de espaços nas pontas e caixa alta, c
          +omo a categoria em                                            
      447 +AMB-003) antes de qualquer comparação; as comparações abaixo —
          + e a busca de taxa                                            
      448 +(RN-019) — usam a moeda normalizada:                          
      449  - registro **sem** `moeda`, ou com `moeda` igual à `moeda_base
           `: valor permanece como
      450    está, **sem** conversão, e o registro **não** é viagem (RN-0
           09);
      451  - registro com `moeda` **diferente** da `moeda_base`: `valor_b
           ase = valor × taxa`,

● Update(spec.md)  ⎿  Added 1 line, removed 1 line
       95  | `despesas[].descricao` | texto | Descrição livre | sim |
       96  | `despesas[].fornecedor` | texto | Fornecedor | sim |
       97  | `despesas[].valor` | número | Valor **na moeda do registro**
            (ver `moeda`); convertido para a base antes das regras monetá
           rias (RN-018) | sim |
       98 -| `despesas[].moeda` | texto | Moeda do `valor` (ex.: `USD`, `
          -EUR`). Ausente ou igual à `moeda_base` do câmbio → sem convers
          -ão e **não** é viagem; diferente da base → convertido pela tax
          -a e marcado **em viagem** por registro (RN-018, RN-009) | não 
          -|                                                             
       98 +| `despesas[].moeda` | texto | Moeda do `valor` (ex.: `USD`, `
          +EUR`); normalizada com `trim` + caixa alta (RN-018). Ausente o
          +u igual à `moeda_base` do câmbio → sem conversão e **não** é v
          +iagem; diferente da base → convertido pela taxa e marcado **em
          + viagem** por registro (RN-018, RN-009) | não |               
       99  | `despesas[].tem_nota_fiscal` | booleano | Se há nota fiscal 
           anexada | sim |
      100  
      101  **Política externa (fonte da verdade de categorias e limites):
           ** um arquivo

● A integrated into Clarifications, RN-018, and the input table.

  ---
  Question: Se o arquivo de câmbio (cambio.json) estiver ausente ou não parsear
  como JSON, o que o sistema deve fazer?

  Why it matters: define o contrato de erro — abortar tudo ou seguir
  processando. Sem a tabela (e sem saber a moeda_base dela), o sistema não
  consegue nem decidir o que é "base"/viagem nem converter; um teste de aceite
  precisa saber se isso é falha fatal ou degradação por registro. Nota: um
  arquivo bem-formado que apenas não tem uma moeda continua sendo "cambio não
  identificado" por registro (RN-020) — esta pergunta é só sobre o arquivo
  faltando/corrompido.

  Recommended: Option A — abortar a execução, como no JSON de topo inválido
  (RN-013). O cambio.json é um insumo de ambiente obrigatório (como a política);
  sem ele a moeda_base é desconhecida e nada pode ser valorado de forma
  determinística.

  ┌────────┬─────────────────────────────────────────────────────────────────┐
  │ Option │                           Description                           │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │ A      │ Abortar a execução com erro (nada é reembolsado), igual ao JSON │
  │        │  de topo inválido (RN-013)                                      │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │        │ Prosseguir: registros sem moeda são processados; qualquer       │
  │ B      │ registro que exija conversão é recusado "cambio não             │
  │        │ identificado"                                                   │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │ C      │ Prosseguir só se nenhum registro tiver moeda estrangeira; se    │
  │        │ houver algum, abortar                                           │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │ Short  │ Provide a different short answer (≤5 words)                     │
  └────────┴─────────────────────────────────────────────────────────────────┘

  You can reply with the option letter (e.g., "A"), accept the recommendation by
  saying "yes" or "recommended", or provide your own short answer.

✻ Cooked for 1m 3s

❯ A                                                                             

● A confirmed — abort on missing/unparseable câmbio file. Integrating.

● Update(spec.md)
  ⎿  Added 1 line
      56  ### Session 2026-07-31 (clarify)
      57  
      58  - Q: Ao comparar `moeda` com a `moeda_base` e com as chaves de 
          `taxas`, normaliza-se o valor ou compara-se exatamente? → A: **
          Normalizar** — `trim` + caixa alta antes de qualquer comparação
           (ex.: `" usd "` → `USD`), do mesmo modo que a `categoria` (AMB
          -003). Só assim se decide "sem conversão" (= base), "converter"
           (moeda válida nas taxas) ou "cambio não identificado".
      59 +- Q: Se o `cambio.json` estiver ausente ou não parsear como JSO
         +N, o que o sistema faz? → A: **Aborta** a execução com erro (na
         +da é reembolsado), como no JSON de topo inválido (RN-013) — sem
         + o arquivo a `moeda_base` é desconhecida. Distingue-se de "camb
         +io não identificado" (RN-020), que é recusa **por registro** co
         +m o arquivo presente e bem-formado.                            
      60  
      61  ## 3. Fora de escopo
      62  

● Update(spec.md)
  ⎿  Added 5 lines, removed 2 lines
      456    totais e no reembolso; o registro é marcado **em viagem** (R
           N-009).
      457  
      458  A `moeda_base` de referência é sempre a do `cambio.json`; a `m
           oeda_base` de
      459 -`politica-v4.json` é ignorada. A conversão ocorre logo após a 
          -validade da categoria                                         
      460 -(Seção 8), de modo que toda despesa de categoria válida tem um
          - valor em base.                                               
      459 +`politica-v4.json` é ignorada. Se o `cambio.json` estiver **au
          +sente ou não parsear**                                        
      460 +como JSON, a execução **aborta** (a `moeda_base` seria desconh
          +ecida), como no JSON de                                       
      461 +topo inválido (RN-013); isso difere de "cambio não identificad
          +o" (RN-020), que é                                            
      462 +recusa por registro com o arquivo presente. A conversão ocorre
          + logo após a validade da                                      
      463 +categoria (Seção 8), de modo que toda despesa de categoria vál
          +ida tem um valor em base.                                     
      464  **Origem:** nova regra de câmbio (2026-07-31).
      465  **Aceite:** USD 40,00 em 2026-07-20 (taxa 5,50) → 220,00 em ba
           se; BRL 95,00 (= base) →
      466  95,00 sem conversão; registro sem `moeda` → valor inalterado, 
           não é viagem.

● Update(spec.md)
  ⎿  Added 4 lines, removed 2 lines
      673  1. **Validação estrutural** — campos obrigatórios presentes e 
           tipados, `valor`
      674     numérico, `data` parseável; senão "registro inválido" (RN-0
           13). Se o JSON de
      675     topo não parseia, aborta a execução.
      676 -2. **Resolução da política** — resolver o centro de custo (o d
          -o input ou                                                    
      676 +2. **Resolução da política e do câmbio** — resolver o centro d
          +e custo (o do input ou                                        
      677     `padrao`) e carregar categorias, limites, periodicidades e 
           parâmetros globais
      678 -   (RN-015).                                                  
      678 +   (RN-015); carregar a tabela de câmbio (`cambio.json`) e sua
          + `moeda_base`. Se o                                           
      679 +   `cambio.json` estiver ausente ou não parsear, a execução ab
          +orta (RN-018), como no                                        
      680 +   JSON de topo inválido (RN-013).                            
      681  3. **Normalização** — arredondar o `valor` de origem para 2 ca
           sas (RN-011); aplicar
      682     `trim` e caixa na `categoria` (RN-001); determinar a `moeda
           ` e o **status de
      683     viagem** do registro (moeda ≠ `moeda_base` do câmbio → viag
           em; sem `moeda` ou moeda

● Update(spec.md)
  ⎿  Added 4 lines, removed 2 lines
      775    formado e vigente; não há verificação de consistência (limit
           es negativos além
      776    de 0, periodicidades desconhecidas, versão/vigência) nesta v
           ersão.
      777  - **Validação do câmbio externo:** a conversão passa a ser fei
           ta por `cambio.json`
      778 -  (RN-018..RN-020), mas não há verificação de consistência do 
          -arquivo (taxas ≤ 0,                                           
      778 +  (RN-018..RN-020), mas não há verificação de consistência do 
          +conteúdo (taxas ≤ 0,                                          
      779    datas fora de ordem, moedas repetidas) nem busca de cotação 
           fora dele; assume-se bem
      780 -  formado. Uma moeda ausente de todas as datas é recusa de neg
          -ócio, não erro fatal.                                         
      780 +  formado. Uma moeda ausente de todas as datas é recusa de neg
          +ócio ("cambio não                                             
      781 +  identificado"), não erro fatal; já um arquivo **ausente ou i
          +nparseável aborta** a                                         
      782 +  execução (RN-018).                                          
      783  - **Fuso horário:** datas são civis, sem fuso; a taxa é resolv
           ida pela `data` do
      784    registro. Multi-fuso fica fora até haver requisito.
      785  - **Vários inputs de uma mesma competência (viagem + não-viage
           m):** cada input é

● A integrated into Clarifications, RN-018, Section 8, and Section 10.

  ---
  Question: Quando o campo moeda está presente mas não é um texto de moeda 
  válido (por exemplo ""/só espaços, um número, true, ou null), como o registro
  deve ser tratado?

  Why it matters: define o alcance da validação estrutural (RN-013) para o novo
  campo e evita que um moeda "lixo" seja silenciosamente convertido ou recusado
  pelo motivo errado — o que muda os testes de borda e a ordem de portões.

  Recommended: Option A — ausente/null/vazio (após trim) conta como "sem moeda"
  (fica na base, sem conversão, não é viagem); um moeda presente de tipo errado
  (número, booleano, objeto) é "registro inválido" (RN-013). É consistente com o
  campo ser opcional (leniente no vazio) e com a tipagem estrita dos demais
  campos.

  ┌────────┬─────────────────────────────────────────────────────────────────┐
  │ Option │                           Description                           │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │        │ Ausente/null/""/espaços → "sem moeda" (base, sem conversão);    │
  │ A      │ tipo errado (número/booleano/objeto) → "registro inválido"      │
  │        │ (RN-013)                                                        │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │ B      │ Qualquer moeda presente que não seja texto não-vazio →          │
  │        │ "registro inválido" (RN-013), inclusive "" e null               │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │ C      │ Qualquer moeda presente que não bata com base nem com uma taxa  │
  │        │ → "cambio não identificado" (RN-020), inclusive ""/tipo errado  │
  ├────────┼─────────────────────────────────────────────────────────────────┤
  │ Short  │ Provide a different short answer (≤5 words)                     │
  └────────┴─────────────────────────────────────────────────────────────────┘

  You can reply with the option letter (e.g., "A"), accept the recommendation by
  saying "yes" or "recommended", or provide your own short answer.

✻ Churned for 58s

❯ A                                                                             

● A confirmed. Integrating — RN-013 gains the moeda-type check; empty/null is
  lenient (base).

● Update(spec.md)
  ⎿  Added 1 line
      57  
      58  - Q: Ao comparar `moeda` com a `moeda_base` e com as chaves de 
          `taxas`, normaliza-se o valor ou compara-se exatamente? → A: **
          Normalizar** — `trim` + caixa alta antes de qualquer comparação
           (ex.: `" usd "` → `USD`), do mesmo modo que a `categoria` (AMB
          -003). Só assim se decide "sem conversão" (= base), "converter"
           (moeda válida nas taxas) ou "cambio não identificado".
      59  - Q: Se o `cambio.json` estiver ausente ou não parsear como JSO
          N, o que o sistema faz? → A: **Aborta** a execução com erro (na
          da é reembolsado), como no JSON de topo inválido (RN-013) — sem
           o arquivo a `moeda_base` é desconhecida. Distingue-se de "camb
          io não identificado" (RN-020), que é recusa **por registro** co
          m o arquivo presente e bem-formado.
      60 +- Q: Como tratar `moeda` presente mas inválida (`""`/espaços, n
         +úmero, booleano, `null`)? → A: Ausente, `null` ou vazio após `t
         +rim` conta como **"sem moeda"** (fica na base, sem conversão, n
         +ão é viagem); `moeda` de **tipo não-textual** (número, booleano
         +, objeto) é **"registro inválido"** (RN-013).                  
      61  
      62  ## 3. Fora de escopo
      63  

● Update(spec.md)
  ⎿  Added 10 lines, removed 7 lines
      406  
      407  ### RN-013 — Registro estruturalmente inválido
      408  **Regra:** Um registro cujo formato impede a avaliação — campo
            obrigatório
      409 -ausente, `valor` não numérico, ou `data` que não parseia como 
          -`YYYY-MM-DD` — é                                              
      410 -recusado com motivo "registro inválido" e reportado em `reprov
          -adas_sem_categoria`                                           
      411 -(pois não pode ser classificado com confiança). Os demais regi
          -stros são                                                     
      412 -processados normalmente. Se o JSON de topo não puder ser parse
          -ado, a execução                                               
      413 -aborta com erro e nada é reembolsado.                         
      414 -**Origem:** decisão de esclarecimento (Clarifications 2026-07-
          -30).                                                          
      415 -**Aceite:** um registro sem `data` → recusado "registro inváli
          -do"; as demais                                                
      409 +ausente, `valor` não numérico, `data` que não parseia como `YY
          +YY-MM-DD`, ou `moeda`                                         
      410 +presente com **tipo não-textual** (número, booleano, objeto) —
          + é recusado com motivo                                        
      411 +"registro inválido" e reportado em `reprovadas_sem_categoria` 
          +(pois não pode ser                                            
      412 +classificado com confiança). Um `moeda` ausente, `null` ou **v
          +azio após `trim`**                                            
      413 +**não** é inválido: conta como "sem moeda" e o registro fica n
          +a base (RN-018). Os                                           
      414 +demais registros são processados normalmente. Se o JSON de top
          +o não puder ser                                               
      415 +parseado, a execução aborta com erro e nada é reembolsado.    
      416 +**Origem:** decisão de esclarecimento (Clarifications 2026-07-
          +30; `moeda` inválida 2026-07-31).                             
      417 +**Aceite:** um registro sem `data` → recusado "registro inváli
          +do"; `moeda` = 5 (número)                                     
      418 +→ "registro inválido"; `moeda` = `""` → tratado como sem moeda
          + (base). As demais                                            
      419  despesas do input continuam sendo avaliadas.
      420  
      421  ### RN-012 — Agregação por categoria

● Update(spec.md)
  ⎿  Added 3 lines, removed 2 lines
      451  **normalizada** (remoção de espaços nas pontas e caixa alta, c
           omo a categoria em
      452  AMB-003) antes de qualquer comparação; as comparações abaixo —
            e a busca de taxa
      453  (RN-019) — usam a moeda normalizada:
      454 -- registro **sem** `moeda`, ou com `moeda` igual à `moeda_base
          -`: valor permanece como                                       
      455 -  está, **sem** conversão, e o registro **não** é viagem (RN-0
          -09);                                                          
      454 +- registro **sem** `moeda` (ausente, `null` ou vazio após `tri
          +m`), ou com `moeda`                                           
      455 +  igual à `moeda_base`: valor permanece como está, **sem** con
          +versão, e o registro                                          
      456 +  **não** é viagem (RN-009);                                  
      457  - registro com `moeda` **diferente** da `moeda_base`: `valor_b
           ase = valor × taxa`,
      458    onde `taxa` é o fator da moeda na `data` do registro (RN-019
           ). Arredonda-se o valor
      459    de origem a 2 casas, multiplica-se pela taxa e arredonda-se 
           o resultado a 2 casas

● Three questions asked and integrated. Remaining ambiguity categories are Clear
  or plan-level — I'll stop here (3 of max 5). Final validation and checklist
  re-check:

  Ran 1 shell command (ctrl+o to expand)

● Três esclarecimentos integrados; a checklist de qualidade permanece 16/16 (as
  respostas reforçaram bordas e dependências — nenhum item mudou de estado). Sem
  .specify/extensions.yml → nenhum hook pós-execução.

  Relatório de conclusão — /speckit-clarify

  Perguntas feitas e respondidas: 3 (de máx. 5)
  1. Normalização de moeda (trim + caixa alta) → A (normalizar)
  2. cambio.json ausente/inparseável → A (abortar, como RN-013)
  3. moeda presente mas inválida → A (vazio/null = base; tipo errado = "registro
  inválido")

  Spec atualizada: specs/001-motor-reembolso/spec.md

  Seções tocadas:
  - ## Clarifications — nova subseção ### Session 2026-07-31 (clarify) com 3
  bullets
  - Seção 4 — linha despesas[].moeda (nota de normalização)
  - RN-018 — normalização da moeda + abort em arquivo ausente/inparseável
  - RN-013 — moeda de tipo não-textual é "registro inválido"; vazio/null = base
  - Seção 8 — passo 2 renomeado "Resolução da política e do câmbio" (carga do
  cambio.json + abort)
  - Seção 10 — distinção entre recusa de negócio e arquivo ausente (abort)

  Checklist de qualidade: 16/16 → 16/16 (sem mudanças de estado, sem
  regressões).

  Cobertura da varredura de ambiguidade:

  ┌──────────────────────────────────────┬──────────────────────────────────┐
  │              Categoria               │              Status              │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Functional Scope & Behavior          │ Clear                            │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Domain & Data Model (campo moeda,    │ Resolved                         │
  │ normalização, tipo)                  │                                  │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Interaction & UX Flow                │ Clear (CLI, sem UI)              │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Non-Functional (determinismo,        │ Clear                            │
  │ precisão)                            │                                  │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Integration & External Deps (falha   │ Resolved                         │
  │ do cambio.json)                      │                                  │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Edge Cases & Failure Handling (moeda │ Resolved                         │
  │  inválida, moeda desconhecida)       │                                  │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Constraints & Tradeoffs              │ Clear                            │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Terminology & Consistency            │ Clear                            │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Completion Signals (aceite testável) │ Clear — golden do envelope fica  │
  │                                      │ para o plano/quickstart          │
  ├──────────────────────────────────────┼──────────────────────────────────┤
  │ Misc / Placeholders                  │ Clear (sem TODOs/[NEEDS          │
  │                                      │ CLARIFICATION])                  │
  └──────────────────────────────────────┴──────────────────────────────────┘

  Nenhum item Outstanding/Deferred de alto impacto. A spec está pronta para a
  próxima fase.

  Próximo comando sugerido: /speckit-plan — para regenerar plan.md/tasks.md e
  alinhar a implementação (que ainda diverge: não lê cambio.json, não aceita
  moeda, trata viagem como flag de input).

✻ Baked for 1m 3s

❯ /context 
  ⎿  Context Usage
     ⛀ ⛁ ⛁ ⛁ ⛀ ⛀ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁   Opus 4.8
     ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁   claude-opus-4-8
     ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛀ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   255.7k/1m tokens (26%)
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ 
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   Estimated usage by category
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   ⛁ System prompt: 3.1k tokens (0.3%)
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   ⛁ System tools: 16.2k tokens (1.6%)
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   ⛁ Memory files: 1.2k tokens (0.1%)
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   ⛁ Skills: 2.4k tokens (0.2%)
     ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶   ⛁ Messages: 233.5k tokens (23.3%)
                                               ⛶ Free space: 743.6k (74.4%)

     Memory files · /memory
     └ 1 file · 1.2k tokens

     Skills · /skills
     └ 25 skills · 2.4k tokens

     /context all to expand

❯ /speckit-plan                                                                 

● I'll run the plan workflow. First, setup and load context. Since pwsh isn't
  available, let me check the setup script and gather the existing artifacts.

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● The plan.md is badly stale — it's at v1.1, predating external policy (política
  v4), category-agnostic rules (D-006), and the câmbio/travel changes (D-007).
  The spec is now 1.4. I need to regenerate the design artifacts. Let me read
  the current code and remaining artifacts to ground the new plan in reality.
  Read 4 files (ctrl+o to expand)

● Now I understand the full gap: the code is entirely on the old model
  (hardcoded categories, --em-viagem flag, no política/câmbio file loading). Let
  me check pyproject.toml and the contracts dir, then regenerate the artifacts
  for spec 1.4.

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● I now have the complete picture. The implementation is entirely on the old
  model; the plan and all design artifacts need regenerating for spec 1.4
  (external policy + câmbio + per-record travel). The constitution is an
  unfilled template, so there are no governance gates to fail.

  I've worked out the new architecture and computed the envelope golden. Let me
  regenerate the artifacts, starting with plan.md.

● Write(plan.md)
  ⎿  Added 175 lines, removed 133 lines
        1  # Plano Técnico — Motor de Cálculo de Reembolso
        2  
        3 -**Versão:** 1.1 · **Baseado na spec:** 1.1 (inclui Clarificati
          -ons 2026-07-30, D-003 e D-004)                                
        3 +**Versão:** 1.4 · **Baseado na spec:** 1.4 (Clarifications 202
          +6-07-30 e 2026-07-31;                                         
        4 +D-003..D-007). Substitui o plano 1.1, que assumia política emb
          +utida em código,                                              
        5 +categorias fixas e viagem por flag de CLI.                    
        6  
        7  > Aqui mora o COMO. Este arquivo pode e deve falar de linguage
           m, biblioteca e
        8  > arquitetura. O que ele **não** pode é introduzir regra de ne
           gócio nova — se
        9  > apareceu uma, ela pertence à `spec.md`.
       10  
        9 -**Constitution Check:** `.specify/memory/constitution.md` está
          - no estado de                                                 
       10 -template (sem princípios preenchidos). Não há gate de governan
          -ça a violar; se a                                             
       11 -constituição for ratificada depois, este plano deve ser reaval
          -iado.                                                         
       11 +**Constitution Check:** `.specify/memory/constitution.md` está
          + no estado de template                                        
       12 +(princípios não preenchidos). Não há gate de governança a viol
          +ar. As convenções                                             
       13 +efetivas vêm de `CLAUDE.md` (núcleo puro sem I/O; uma função p
          +or RN; um teste por RN;                                       
       14 +`Decimal` sempre; regra de negócio só na spec) e são respeitad
          +as por este plano. Se a                                       
       15 +constituição for ratificada depois, reavaliar.                
       16  
       17  ---
       18  
       19 +## 0. O que mudou desde o plano 1.1 (gap a fechar)            
       20 +                                                              
       21 +O código atual (`src/`) implementa a spec 1.0/1.1 e diverge da
          + spec 1.4 em cinco frentes:                                   
       22 +                                                              
       23 +| Frente | Hoje no código | Exigido pela spec 1.4 |           
       24 +|---|---|---|                                                 
       25 +| Política | `politica.py` com constantes fixas (`LIMITES_DIAR
          +IOS`, `CATEGORIAS_VALIDAS`, ...) | Ler `politica-v4.json`; cat
          +egorias/limites/periodicidade por centro de custo, com `padrao
          +` (RN-015/016/017); nenhuma categoria embutida (RN-001/004) | 
       26 +| Categorias | trio fixo `alimentacao/transporte_urbano/hosped
          +agem` (enum `Categoria`, `ORDEM_CATEGORIAS`) | conjunto **dinâ
          +mico** por CC; teto por **periodicidade**, não por nome (RN-00
          +2/003/004/016) |                                              
       27 +| Viagem | flag de CLI `--em-viagem`, por input inteiro; campo
          + `em_viagem` na saída | **por registro**, derivada da moeda (R
          +N-009); sem `--em-viagem`; sem `em_viagem` na saída |         
       28 +| Câmbio | inexistente | ler `cambio.json`; converter por data
          + (RN-018/019); "cambio não identificado" (RN-020) |           
       29 +| Nota fiscal | compara `valor` de entrada | compara **valor c
          +onvertido** (RN-006, após conversão) |                        
       30 +                                                              
       31 +Este plano redesenha as fronteiras para acomodar as duas fonte
          +s externas mantendo o                                         
       32 +núcleo puro.                                                  
       33 +                                                              
       34  ## 1. Stack
       35  
       17 -| Escolha | O quê | Por quê | O que descartei e por quê |     
       36 +| Escolha | O quê | Por quê | Descartado |                    
       37  |---|---|---|---|
       19 -| Linguagem | Python 3.13.x | Requisito do usuário; stdlib ric
          -a (`json`, `argparse`, `decimal`, `datetime`) cobre tudo sem d
          -ependências | — |                                             
       20 -| Testes | `pytest` | Parametrização ergonômica para mapear um
          - teste por `RN-NNN` e por caso de borda | `unittest` — mais ve
          -rboso para tabelas de casos |                                 
       21 -| Parsing/validação | stdlib `json` + `argparse`, validação ma
          -nual em módulo próprio | Zero dependências de runtime; control
          -e explícito das mensagens de recusa (a spec exige motivos text
          -uais precisos) | `pydantic` — esconderia a validação de regra 
          -que o usuário pediu para deixar explícita e separada |        
       22 -| Aritmética monetária | `decimal.Decimal`, `quantize(0.01, RO
          -UND_HALF_UP)` | Dinheiro não pode usar ponto flutuante binário
          -; `ROUND_HALF_UP` é exatamente a RN-011 | `float` — erro de ar
          -redondamento previsível; descartado |                         
       38 +| Linguagem | Python 3.13.x | Requisito; stdlib (`json`, `argp
          +arse`, `decimal`, `datetime`) cobre tudo sem dependências | — 
          +|                                                             
       39 +| Testes | `pytest` | Um teste por `RN-NNN` + tabela de bordas
          +; auditoria de cobertura de RN | `unittest` (verboso) |       
       40 +| Parsing/validação | stdlib `json` + `argparse`, validação ma
          +nual | Zero dependências; mensagens de recusa explícitas | `py
          +dantic` (esconderia a validação que é regra) |                
       41 +| Dinheiro | `decimal.Decimal`, `quantize(0.01, ROUND_HALF_UP)
          +`, JSON lido com `parse_float=Decimal` | RN-011; conversão de 
          +câmbio precisa de centavo exato | `float` (erro binário) |    
       42  
       24 -> **Detalhe crítico de aritmética:** os valores monetários são
          - lidos do JSON já                                             
       25 -> como `Decimal` (via `json.load(..., parse_float=Decimal)`), 
          -**nunca** como                                                
       26 -> `float`. Isso evita que `33.333` vire `33.33299999…` antes d
          -o `quantize`.                                                 
       43 +> **Aritmética crítica:** valores e **taxas** de câmbio são li
          +dos como `Decimal` (via                                       
       44 +> `parse_float=Decimal`), nunca `float`. A conversão (RN-018/A
          +MB-018) arredonda o valor                                     
       45 +> de origem a 2 casas, multiplica pela **taxa cheia** e arredo
          +nda o resultado a 2 casas.                                    
       46  
       47  ## 2. Arquitetura
       48  
       30 -Duas camadas: um **núcleo puro** de regra de negócio (sem I/O,
          - determinístico) e                                            
       31 -uma **casca de I/O** (CLI, leitura/escrita de arquivo, seriali
          -zação).                                                       
       49 +Duas camadas: **núcleo puro** (regra de negócio, determinístic
          +o, sem I/O) e **casca de                                      
       50 +I/O** (CLI, leitura de 3 arquivos JSON, serialização). As duas
          + fontes externas                                              
       51 +(`politica-v4.json`, `cambio.json`) são lidas na casca e **inj
          +etadas já parseadas** no                                      
       52 +núcleo — o núcleo nunca abre arquivo.                         
       53  
       54  ```
       34 -calcular --input --output [--em-viagem]                       
       55 +calcular --input despesas.json --output resultado.json        
       56 +         [--politica ...] [--cambio ...]                      
       57          │
       58          ▼
       37 -   cli.py (argparse)                 ── casca de I/O          
       59 +   cli.py (argparse)                         ── casca de I/O  
       60          │
       61          ▼
       40 -   io_json.py  ── lê JSON (parse_float=Decimal), valida estrut
          -ura, serializa saída                                          
       41 -        │  Despesa[] + contexto                               
       62 +   io_json.py  ── lê input, politica-v4.json e cambio.json (pa
          +rse_float=Decimal);                                           
       63 +        │         valida topo; ABORTA se input/política/câmbio
          + ausentes ou inparseáveis                                     
       64 +        │         (RN-013, RN-018); serializa a saída         
       65 +        │  Entrada{despesas_brutas, colaborador, periodo} + Po
          +litica + Cambio                                               
       66          ▼
       43 -   calculo.py (pipeline)             ── núcleo puro           
       44 -        │  normaliza → deduplica → aplica gates → aplica tetos
          - → agrega                                                     
       45 -        ├── regras.py   (uma função por RN: gates de validação
          - + tetos + total_despesas)                                    
       46 -        ├── politica.py (constantes: limites, limiar NF, multi
          -plicador viagem)                                              
       67 +   calculo.py (pipeline puro)                ── núcleo puro   
       68 +        │  estrutura → normaliza → categoria → limite>0 → CONV
          +ERSÃO →                                                       
       69 +        │  dedup → período → valor → NF(convertido) → teto(bal
          +des) → agrega                                                 
       70 +        ├── regras.py   (uma função por RN; gates, conversão, 
          +taxa, tetos, agregação)                                       
       71 +        ├── politica.py (dict → Politica/Cambio; resolução de 
          +CC; constantes)                                               
       72          └── modelo.py   (dataclasses + enums)
       48 -        │  Resultado                                          
       73 +        │  Resultado (sem em_viagem)                          
       74          ▼
       50 -   io_json.py → resultado.json                                
       75 +   io_json.py → resultado.json (2 casas, ensure_ascii=False, o
          +rdem determinística)                                          
       76  ```
       77  
       53 -**Fronteiras:** `calculo.py` + `regras.py` + `politica.py` + `
          -modelo.py` não                                                
       54 -importam nada de I/O e não conhecem arquivos nem `argparse` — 
          -recebem estruturas                                            
       55 -e devolvem estruturas. Todo contato com o mundo (ler arquivo, 
          -`print`, exit code)                                           
       56 -mora em `cli.py` e `io_json.py`. Essa linha é o que faz as ~14
          - regras testáveis                                             
       57 -sem tocar em disco e resistentes a troca de formato de entrada
          -.                                                             
       78 +**Fronteiras:** `calculo.py`, `regras.py`, `politica.py`, `mod
          +elo.py` não importam I/O e                                    
       79 +não conhecem caminhos de arquivo — recebem `Politica`/`Cambio`
          + já construídos. Todo                                         
       80 +contato com o mundo (abrir os 3 arquivos, `print`, exit code) 
          +mora em `cli.py`/`io_json.py`.                                
       81  
       59 -**Estrutura de pastas:**                                      
       82 +**Estrutura de pastas (inalterada; conteúdo dos módulos muda):
          +**                                                            
       83  
       84  ```
       85  src/
       86    __init__.py
       87    __main__.py     # python -m src ... (dev)
       65 -  cli.py          # argparse, main() → comando `calcular`; exi
          -t codes                                                       
       66 -  io_json.py      # leitura (parse_float=Decimal) + validação 
          -estrutural + serialização (ensure_ascii=False)                
       67 -  modelo.py       # dataclasses: Despesa, Reprovacao, Resultad
          -oCategoria, Resultado; enums Categoria, Motivo                
       68 -  politica.py     # constantes de política (Seção 4)          
       69 -  regras.py       # FUNÇÕES DE REGRA DE NEGÓCIO — arquivo próp
          -rio (requisito do usuário)                                    
       70 -  calculo.py      # pipeline puro que orquestra regras.py     
       88 +  cli.py          # argparse (SEM --em-viagem); resolve caminh
          +os de política/câmbio; exit codes                             
       89 +  io_json.py      # ler_entrada / ler_politica / ler_cambio + 
          +serialização                                                  
       90 +  modelo.py       # dataclasses: Despesa, CategoriaConfig, Pol
          +itica, Cambio, Reprovacao, ResultadoCategoria, Resultado; enum
          + Motivo                                                       
       91 +  politica.py     # politica_de_dict / cambio_de_dict (dict→es
          +trutura, puro); CASAS_DECIMAIS                                
       92 +  regras.py       # UMA FUNÇÃO POR RN (RN-001..RN-020)        
       93 +  calculo.py      # pipeline puro na ordem da Seção 8         
       94 +  informacoes_externas/                                       
       95 +    politica-v4.json                                          
       96 +    cambio.json                                               
       97  tests/
       72 -  test_regras.py       # 1 teste por RN                       
       73 -  test_calculo.py      # tetos, agregação, dedup, ordem       
       74 -  test_bordas.py       # casos da Seção 7 da spec             
       75 -  test_integracao.py   # golden: exemplos/despesas-exemplo.jso
          -n → saída da Seção 4                                          
       76 -  test_cli.py          # flags, arquivos, --em-viagem, exit co
          -des                                                           
       77 -pyproject.toml         # metadados + console_script `calcular`
          - + config do pytest                                           
       98 +  test_regras.py       # 1 teste por RN (RN-001..RN-020)      
       99 +  test_calculo.py      # dedup/ordem/tetos/baldes/agregação   
      100 +  test_bordas.py       # casos da Seção 7                     
      101 +  test_cambio.py       # RN-018/019/020: conversão, data mais 
          +próxima, empate, não identificado                             
      102 +  test_politica.py     # RN-015: resolução de CC, padrão, conj
          +unto dinâmico                                                 
      103 +  test_integracao.py   # goldens: despesas-exemplo.json e desp
          +esas-envelope.json                                            
      104 +  test_cobertura_rn.py # auditoria: nenhuma RN sem teste      
      105 +  test_cli.py          # flags, arquivos, exit codes, abort de
          + câmbio                                                       
      106 +  test_io.py           # serialização (2 casas, acentos, ordem
          +)                                                             
      107 +pyproject.toml                                                
      108  ```
      109  
      110  ## 3. Modelo de dados
      111  
       82 -Detalhe completo em [`data-model.md`](./data-model.md). Resumo
          -:                                                             
      112 +Detalhe em [`data-model.md`](./data-model.md). Mudanças-chave:
      113  
       84 -- **`Despesa`** (entrada normalizada): `id`, `data: date`, `ca
          -tegoria: str`,                                                
       85 -  `categoria_norm: str` (trim + lower), `descricao`, `forneced
          -or`,                                                          
       86 -  `valor: Decimal` (já em 2 casas), `tem_nota_fiscal: bool`.  
       87 -- **`Reprovacao`**: `id`, `motivo: Motivo`, e opcional `catego
          -ria_informada`                                                
       88 -  (usado só em `reprovadas_sem_categoria`).                   
       89 -- **`ResultadoCategoria`**: `total_despesas`, `total_aceito`, 
          -`total_reembolso`                                             
       90 -  (todos `Decimal`), `reprovadas: list[Reprovacao]`.          
       91 -- **`Resultado`**: `colaborador`, `competencia`, `periodo`, `e
          -m_viagem`,                                                    
       92 -  `categorias: dict[str, ResultadoCategoria]`, `reprovadas_sem
          -_categoria`,                                                  
       93 -  `total_reembolso_geral`.                                    
       94 -- **`Motivo`** (enum, texto exato da spec): `categoria não apl
          -icável`,                                                      
       95 -  `data fora da competência`, `registro duplicado`, `sem nota 
          -fiscal obrigatória`,                                          
       96 -  `valor inválido`, `registro inválido`.                      
      114 +- **`Despesa`** ganha câmbio e viagem: `moeda_norm: str | None
          +` (trim+upper; `None` =                                       
      115 +  sem moeda), `valor_origem: Decimal` (2 casas, na moeda de or
          +igem), `valor_base:                                           
      116 +  Decimal | None` (convertido; `None` até a conversão / se "ca
          +mbio não identificado"),                                      
      117 +  `em_viagem: bool`. A `categoria_norm` continua trim+lower.  
      118 +- **`CategoriaConfig`**: `limite: Decimal`, `periodicidade: st
          +r` (`"dia"`/`"diaria"`),                                      
      119 +  `observacao: str | None`.                                   
      120 +- **`Politica`**: `padrao: dict[str, CategoriaConfig]`, `centr
          +os_custo: dict[str,                                           
      121 +  dict[str, CategoriaConfig]]`, `limiar_nf: Decimal`, `acresci
          +mo_viagem_pct: Decimal`.                                      
      122 +- **`Cambio`**: `moeda_base: str` (normalizada), `taxas: dict[
          +date, dict[str, Decimal]]`.                                   
      123 +- **`Resultado`**: **remove** `em_viagem`; `categorias` é `dic
          +t[str, ResultadoCategoria]`                                   
      124 +  na ordem determinística (Seção 5, DT-011).                  
      125 +- **`Motivo`**: acrescenta `CAMBIO_NAO_IDENTIFICADO = "cambio 
          +não identificado"`. O enum                                    
      126 +  `Categoria` (trio fixo) é **removido** — não há mais categor
          +ia conhecida em código.                                       
      127  
       98 -A justificativa da recusa é carregada pelo próprio `Motivo` na
          - `Reprovacao`; uma                                            
       99 -despesa aceita não gera `Reprovacao` e contribui para os três 
          -totais.                                                       
      128 +## 4. Como as fontes externas são representadas               
      129  
      101 -## 4. Como a política é representada                          
      130 +Ambas viram estruturas puras construídas na casca e passadas a
          +o núcleo:                                                     
      131  
      103 -Os limites vivem como **constantes nomeadas** em `src/politica
          -.py`, não em arquivo                                          
      104 -de configuração externo:                                      
      132 +- `io_json.ler_politica(caminho) -> Politica` e `io_json.ler_c
          +ambio(caminho) -> Cambio`                                     
      133 +  abrem o arquivo (uma vez), leem com `parse_float=Decimal` e 
          +delegam a                                                     
      134 +  `politica.politica_de_dict` / `politica.cambio_de_dict` (pur
          +os: dict → dataclass).                                        
      135 +- **Localização:** por padrão os arquivos empacotados em      
      136 +  `src/informacoes_externas/{politica-v4.json,cambio.json}`, r
          +esolvidos relativos ao                                        
      137 +  pacote; sobrescrevíveis por `--politica`/`--cambio` (contrat
          +o em                                                          
      138 +  [`contracts/cli-contract.md`](./contracts/cli-contract.md)).
      139 +- **Abort:** input, política ou câmbio ausente/inparseável → `
          +ErroEntrada` → `stderr` +                                     
      140 +  exit 1 (RN-013 para o input; RN-018 para o câmbio; mesma cla
          +sse para a política).                                         
      141 +- **`moeda_base`:** sempre a do `cambio.json`; a `moeda_base` 
          +de `politica-v4.json` é                                       
      142 +  ignorada (RN-018).                                          
      143  
      106 -```                                                           
      107 -LIMITES_DIARIOS        = {"alimentacao": Decimal("60"), "trans
          -porte_urbano": Decimal("80")}                                 
      108 -LIMITE_HOSPEDAGEM      = Decimal("250")   # por registro (RN-0
          -04 / AMB-006)                                                 
      109 -LIMIAR_NOTA_FISCAL     = Decimal("100")   # NF exigida se valo
          -r > este limiar (RN-006)                                      
      110 -MULTIPLICADOR_VIAGEM   = Decimal("1.5")   # aplica-se só aos t
          -etos (RN-009)                                                 
      111 -CATEGORIAS_VALIDAS     = {"alimentacao", "transporte_urbano", 
          -"hospedagem"}                                                 
      112 -CASAS_DECIMAIS         = Decimal("0.01")                      
      113 -```                                                           
      114 -                                                              
      115 -**Por quê constantes e não config externa:** a política muda r
          -aramente, é versionada                                        
      116 -junto do código e cada valor é parte da regra testada. Um módu
          -lo único dá um ponto                                          
      117 -de mudança sem overhead de I/O ou de validar um arquivo de con
          -fig. **Trade-off:**                                           
      118 -mudar a política exige alterar o código e re-deploy — aceitáve
          -l para uma política                                           
      119 -que muda em ciclos de meses (é "v3"). Se um dia a política pre
          -cisar mudar sem                                               
      120 -deploy, este é o único ponto a externalizar.                  
      121 -                                                              
      144  ## 5. Decisões técnicas
      145  
      124 -### DT-001 — Dinheiro em `Decimal`, lido como `Decimal` desde 
          -o JSON                                                        
      125 -**Contexto:** RN-011 exige 2 casas e arredondamento half-up; h
          -á valor com 3 casas (`33.333`) e somas que precisam bater cent
          -avo a centavo no teste golden.                                
      126 -**Decisão:** todo valor é `Decimal`. O JSON é lido com `parse_
          -float=Decimal`; cada valor recebe `quantize(CASAS_DECIMAIS, RO
          -UND_HALF_UP)` na normalização; a saída é serializada com 2 cas
          -as.                                                           
      127 -**Alternativa descartada:** `float` — erro de ponto flutuante 
          -em dinheiro; e `Decimal(str(float))` depois de já ter perdido 
          -precisão.                                                     
      128 -**Consequência:** fácil: aritmética exata e testes determiníst
          -icos. Difícil: é preciso um encoder JSON que saiba serializar 
          -`Decimal` com 2 casas.                                        
      146 +Mantidas de 1.1: **DT-001** (dinheiro em `Decimal` desde o JSO
          +N), **DT-002** (regra em                                      
      147 +`regras.py`, uma função por RN), **DT-003** (CLI `argparse`, c
          +omando `calcular`),                                           
      148 +**DT-004** (pipeline explícito na ordem da Seção 8), **DT-005*
          +* (só stdlib no runtime),                                     
      149 +**DT-006** (erro de topo aborta; registro malformado é recusa 
          +individual),                                                  
      150 +**DT-007** (`total_despesas` exclui `valor ≤ 0`). Novas/altera
          +das:                                                          
      151  
      130 -### DT-002 — Regras de negócio isoladas em `regras.py`, como f
          -unções puras                                                  
      131 -**Contexto:** requisito do usuário — funções de validação de r
          -egra separadas, bem declaradas, em arquivo próprio.           
      132 -**Decisão:** `regras.py` concentra uma função por regra, nomea
          -da e documentada com o `RN-NNN`: gates de validação com assina
          -tura `def valida_<x>(despesa, contexto) -> Reprovacao | None` 
          -(retornam o motivo ou `None` se passa) e as funções de cálculo
          - de teto/`total_despesas`. `calculo.py` só orquestra.         
      133 -**Alternativa descartada:** regras espalhadas dentro do pipeli
          -ne em `calculo.py` — dificultaria o mapeamento 1:1 com a spec 
          -e a rastreabilidade nos testes.                               
      134 -**Consequência:** fácil: cada RN vira um teste unitário direto
          -; a spec e o código ficam rastreáveis. Difícil: exige discipli
          -na para não vazar regra para `calculo.py`.                    
      152 +### DT-003b — CLI sem `--em-viagem`; caminhos de política/câmb
          +io opcionais                                                  
      153 +**Contexto:** viagem virou por-registro (RN-009); o motor prec
          +isa de dois arquivos externos.                                
      154 +**Decisão:** remover `--em-viagem`. Manter `--input`/`--output
          +` obrigatórios e adicionar                                    
      155 +`--politica`/`--cambio` opcionais (default: arquivos empacotad
          +os). Sem regra de negócio na CLI.                             
      156 +**Consequência:** a assinatura de `CLAUDE.md` (`[--em-viagem]`
          +) fica desatualizada; sinalizar                               
      157 +para atualizar `CLAUDE.md`.                                   
      158  
      136 -### DT-003 — CLI com `argparse`, comando único `calcular`     
      137 -**Contexto:** invocação fixada pelo usuário: `calcular --input
          - despesas.json --output resultado.json [--em-viagem]`.        
      138 -**Decisão:** `argparse` com `--input` (obrigatório), `--output
          -` (obrigatório) e `--em-viagem` (flag booleana `store_true`, d
          -efault `False`). Exposto como `console_scripts` (`calcular = s
          -rc.cli:main`) no `pyproject.toml`; em dev, `python -m src ...`
          -. Contrato completo em [`contracts/cli-contract.md`](./contrac
          -ts/cli-contract.md).                                          
      139 -**Alternativa descartada:** `click`/`typer` — dependência exte
          -rna desnecessária para 3 argumentos.                          
      140 -**Consequência:** fácil: sem dependências; `--em-viagem` mapei
          -a direto para RN-009. Difícil: `argparse` dá menos açúcar para
          - subcomandos futuros (não é necessário agora).                
      159 +### DT-008 — Política e câmbio como dados injetados, não const
          +antes                                                         
      160 +**Contexto:** RN-015/018 externalizam política e câmbio; o núc
          +leo deve permanecer puro.                                     
      161 +**Decisão:** `politica.py` deixa de ter constantes de limite; 
          +passa a converter dict→`Politica`/`Cambio`                    
      162 +e a resolver o centro de custo (`conjunto_do_centro(politica, 
          +cc)` → `padrao` se ausente, RN-015).                          
      163 +Toda leitura de arquivo fica em `io_json.py`.                 
      164 +**Alternativa descartada:** ler os arquivos dentro do núcleo —
          + violaria a fronteira de I/O.                                 
      165 +**Consequência:** troca de política/câmbio não exige recompila
          +r regra; o núcleo é testável com                              
      166 +`Politica`/`Cambio` montados em memória.                      
      167  
      142 -### DT-004 — Pipeline explícito seguindo a ordem da Seção 8 da
          - spec                                                         
      143 -**Contexto:** RN/AMB-010 fixam a ordem de aplicação e o "prime
          -iro gate que falha define o motivo".                          
      144 -**Decisão:** `calculo.py` executa os passos na ordem exata da 
          -Seção 8: validação estrutural → normalização → deduplicação (m
          -antém 1ª ocorrência) → gates (categoria → período → valor → NF
          -) → tetos → agregação. Cada despesa aceita entra em `total_ace
          -ito`/`total_despesas`; cada recusa registra o motivo do primei
          -ro gate.                                                      
      145 -**Alternativa descartada:** avaliar todos os gates e escolher 
          -motivo por prioridade — mais código e mesmo resultado.        
      146 -**Consequência:** fácil: determinístico e auditável, espelha a
          - spec. Difícil: a ordem é acoplada à spec — mudou a spec, muda
          - o pipeline (correto).                                        
      168 +### DT-009 — Teto dirigido por periodicidade, sobre conjunto d
          +inâmico                                                       
      169 +**Contexto:** RN-002/003/004/016 — nenhuma categoria privilegi
          +ada; duas mecânicas.                                          
      170 +**Decisão:** `regras.py` expõe `aplica_teto_dia(aceitas, limit
          +e, fator_por_registro)` (baldes por                           
      171 +status de viagem) e `aplica_teto_diaria(aceitas, limite)`; `ca
          +lculo.py` escolhe pela                                        
      172 +`periodicidade` da `CategoriaConfig`. Sem `ORDEM_CATEGORIAS` f
          +ixo nem `hospedagem` hardcoded.                               
      173 +**Consequência:** categoria nova na política é reembolsada sem
          + tocar código (RN-004).                                       
      174  
      148 -### DT-005 — Sem dependências de runtime (stdlib apenas)      
      149 -**Contexto:** o problema é resolvível 100% com a biblioteca pa
          -drão.                                                         
      150 -**Decisão:** runtime usa só stdlib; `pytest` é dependência ape
          -nas de desenvolvimento.                                       
      151 -**Consequência:** fácil: instalação e reprodução triviais. Dif
          -ícil: nenhuma relevante.                                      
      175 +### DT-010 — Conversão de câmbio e resolução de taxa por data 
      176 +**Contexto:** RN-018/019/AMB-017/018.                         
      177 +**Decisão:** `regras.taxa_por_data(cambio, moeda, data) -> Dec
          +imal | None` percorre as datas de                             
      178 +`taxas` que contêm a moeda, escolhe a de **menor distância** a
          +bsoluta em dias e, em empate,                                 
      179 +a **menor** taxa; devolve `None` se a moeda não existe em nenh
          +uma data (→ RN-020).                                          
      180 +`regras.converte(valor_origem, taxa)` faz `quantize(valor)·tax
          +a` e `quantize` do resultado                                  
      181 +(AMB-018). A `moeda` é normalizada trim+upper (Clarify 2026-07
          +-31) antes de comparar com                                    
      182 +`moeda_base` e com as chaves de `taxas`.                      
      183 +**Consequência:** determinístico; datas de fim de semana caem 
          +na cotação mais próxima.                                      
      184  
      153 -### DT-006 — Tratamento de erro e códigos de saída            
      154 -**Contexto:** RN-013 — registro malformado é recusado individu
          -almente; JSON de topo inválido aborta.                        
      155 -**Decisão:** registro malformado vira `Reprovacao("registro in
          -válido")` em `reprovadas_sem_categoria`. Erros de topo (JSON i
          -nparseável, arquivo de entrada inexistente, campos de topo aus
          -entes) escrevem mensagem em `stderr` e saem com código ≠ 0 (su
          -cesso = 0). Códigos detalhados no contrato da CLI.            
      156 -**Consequência:** fácil: lote resiliente + falha clara para er
          -ro irrecuperável. Difícil: exige distinguir erro estrutural de
          - registro vs. erro de topo.                                   
      185 +### DT-011 — Ordem determinística das categorias na saída     
      186 +**Contexto:** categorias agora são dinâmicas; a saída precisa 
          +ser determinística (Seção 9 da spec).                         
      187 +**Decisão:** o bloco `categorias` segue a **ordem das chaves d
          +o conjunto do centro de custo                                 
      188 +resolvido** na política (ex.: `CC-ENG-PLATAFORMA` → alimentaca
          +o, transporte_urbano, hospedagem;                             
      189 +`CC-COMERCIAL` → alimentacao, transporte_urbano, hospedagem, r
          +epresentacao), emitindo só as que têm                         
      190 +≥1 despesa (AMB-015). `reprovadas_sem_categoria` segue a ordem
          + do input.                                                    
      191 +**Alternativa descartada:** ordem de 1ª aparição no input — ig
          +ual nos goldens atuais, mas acopla a                          
      192 +ordem da saída à ordem de digitação; a ordem da política é mai
          +s estável.                                                    
      193  
      158 -### DT-007 — `total_despesas` exclui valores ≤ 0 (exclusão por
          - valor)                                                       
      159 -**Contexto:** RN-014 revista em D-004 — `total_despesas` soma 
          -o `valor` das despesas de categoria válida (aceitas + reprovad
          -as), **exceto** as com `valor ≤ 0`; a exclusão é **por valor, 
          -não pelo motivo da recusa** (Clarifications 2026-07-30, opção 
          -A).                                                           
      160 -**Decisão:** a função de agregação em `regras.py` que compõe `
          -total_despesas` filtra `despesa.valor > 0` antes de acumular, 
          -independentemente de a despesa ter sido aceita ou recusada e d
          -e qual gate a recusou (duplicidade/período/NF/valor). Como a n
          -ormalização arredonda antes (RN-011), o teste `> 0` usa o `Dec
          -imal` já `quantize`ado.                                       
      161 -**Alternativa descartada:** excluir apenas as recusadas com mo
          -tivo "valor inválido" (exclusão por motivo) — diverge da opção
          - A para o caso raro de uma despesa negativa recusada antes do 
          -gate de valor (ex.: duplicata negativa).                      
      162 -**Consequência:** no exemplo, `transporte_urbano.total_despesa
          -s` passa de 155,01 para **200,01** (o estorno `d-009`, −45,00,
          - sai da somatória; segue recusado como "valor inválido" e list
          -ado em `reprovadas`). A invariante `total_despesas ≥ total_ace
          -ito ≥ total_reembolso` continua válida (fica mais folgada).   
      194 +### DT-012 — Pipeline reordenado com passo de conversão       
      195 +**Contexto:** Seção 8 da spec 1.4.                            
      196 +**Decisão:** ordem exata: estrutura(RN-013) → resolução políti
          +ca+câmbio(RN-015/018) →                                       
      197 +normalização(RN-011/001, moeda+viagem) → categoria válida(RN-0
          +01) → limite>0(RN-017) →                                      
      198 +**conversão(RN-018/019, falha→RN-020)** → dedup(RN-008, chave 
          +inclui moeda) → período(RN-007) →                             
      199 +valor>0(RN-010) → NF sobre valor convertido(RN-006) → teto(RN-
          +002/003/004/005/009/016, baldes) →                            
      200 +agregação(RN-012/014). Conversão **antes** de dedup/período/va
          +lor/NF garante `valor_base` para                              
      201 +todo reprovado que compõe `total_despesas`; "cambio não identi
          +ficado" não tem `valor_base` e é                              
      202 +excluído de `total_despesas` (AMB-017), como os `valor ≤ 0`.  
      203  
      204  ## 6. Estratégia de testes
      205  
      166 -- **Nível:** predominantemente unitário sobre `regras.py` (cad
          -a RN isolada), mais                                           
      167 -  testes de `calculo.py` (dedup/ordem/tetos/agregação) e um pu
          -nhado de integração                                           
      168 -  ponta a ponta pela CLI. Proporção alvo ≈ 75% unitário / 15% 
          -integração de núcleo                                          
      169 -  / 10% CLI.                                                  
      170 -- **Cada `RN-NNN` tem teste?** Sim, por convenção de nome: `te
          -st_rn_001_*`,                                                 
      171 -  `test_rn_002_*`, … `test_rn_014_*` em `test_regras.py`/`test
          -_calculo.py`. Um                                              
      172 -  teste de auditoria (`test_cobertura_rn`) garante que não fal
          -ta RN.                                                        
      173 -- **Casos de borda da Seção 7:** cada linha da tabela vira um 
          -teste em                                                      
      174 -  `test_bordas.py`, nomeado pelo `id` do exemplo (`test_borda_
          -d004_sem_nf`, …).                                             
      175 -- **Golden test:** `test_integracao.py` roda `exemplos/despesa
          -s-exemplo.json` (com                                          
      176 -  e sem `--em-viagem`) e compara com a saída da Seção 4 da spe
          -c, incluindo a                                                
      177 -  invariante `total_despesas ≥ total_aceito ≥ total_reembolso`
          - e                                                            
      178 -  `total_reembolso_geral == 585.43`.                          
      179 -- **Nomenclatura:** o nome do teste cita o `RN`/caso de borda,
          - fechando a                                                   
      180 -  rastreabilidade spec ↔ teste ↔ correção. Ver [`quickstart.md
          -`](./quickstart.md).                                          
      206 +- **Nível:** unitário sobre `regras.py` (cada RN isolada) + `c
          +alculo.py`                                                    
      207 +  (dedup/ordem/tetos/baldes/agregação) + `test_cambio.py`/`tes
          +t_politica.py` para as                                        
      208 +  regras externas + integração ponta a ponta pela CLI. ≈70% un
          +itário / 20% integração de                                    
      209 +  núcleo / 10% CLII/IO.                                       
      210 +- **Cobertura de RN:** `test_rn_001_*` … `test_rn_020_*`; `tes
          +t_cobertura_rn` audita que                                    
      211 +  nenhuma RN-NNN fica sem teste (RN-001..RN-020).             
      212 +- **Bordas (Seção 7):** cada linha vira um teste em `test_bord
          +as.py` (incl. moeda=base,                                     
      213 +  sem moeda, dia misto/baldes, fim de semana, empate, cambio n
          +ão identificado, NF pós-conversão).                           
      214 +- **Goldens (`test_integracao.py`):**                         
      215 +  - `exemplos/despesas-exemplo.json` (`CC-ENG-PLATAFORMA`, sem
          + `moeda`) →                                                   
      216 +    `total_reembolso_geral == 351.43` (Seção 4 da spec; inalte
          +rado).                                                        
      217 +  - `exemplos/despesas-envelope.json` (`CC-COMERCIAL`, com EUR
          +/USD/GBP) →                                                   
      218 +    `total_reembolso_geral == 1228.72` (valores completos em [
          +`quickstart.md`](./quickstart.md)),                           
      219 +    exercitando conversão, baldes, "cambio não identificado" e
          + NF sobre valor convertido.                                   
      220 +  - Invariante `total_despesas ≥ total_aceito ≥ total_reembols
          +o` em toda categoria.                                         
      221 +- **Determinismo:** mesmo input+política+câmbio → mesma saída;
          + ordem de categorias por DT-011.                              
      222  
      223  ## 7. Riscos
      224  
      184 -| Risco | Probabilidade | O que faço se acontecer |           
      225 +| Risco | Prob. | Mitigação |                                 
      226  |---|---|---|
      186 -| Ler valor como `float` antes de `Decimal` e perder precisão 
          -(`33.333`) | Média | `parse_float=Decimal` na leitura + teste 
          -específico de `d-011`; lint proibindo `float(` em valores |   
      187 -| Serializar `Decimal` quebra `json.dumps` | Alta (se esquecid
          -o) | Encoder custom/`default=` convertendo `Decimal`→número co
          -m 2 casas; teste golden pega |                                
      188 -| Acentos nos motivos ("não", "inválido") saem escapados | Méd
          -ia | `json.dump(..., ensure_ascii=False)` + arquivo UTF-8; ass
          -erção no teste de integração |                                
      189 -| Ordem de chaves/categorias não determinística quebra golden 
          -| Baixa | Ordem fixa de categorias e de chaves na serialização
          - |                                                            
      190 -| Stakeholder rejeita AMB-006 (hospedagem por registro ≠ "por 
          -diária" do RH) | Média | Decisão registrada em `DECISIONS.md`;
          - troca isolada em `politica.py`/`regras.py` |                 
      191 -| AMB-012 (`total_despesas` monetário vs. contagem) estar erra
          -da | Baixa/Média | Confirmar com usuário; troca isolada em `re
          -gras.py` + `data-model.md` |                                  
      192 -| `--em-viagem` interpretado por despesa em vez de por input |
          - Baixa | RN-009 é por input inteiro; um único booleano de cont
          -exto no pipeline; teste de CLI |                              
      227 +| Ler valor **ou taxa** como `float` e perder centavo | Média 
          +| `parse_float=Decimal` em input/câmbio; teste de `d-011` (33,
          +333) e de conversões do envelope |                            
      228 +| Arredondar na conversão em ordem errada (taxa arredondada, d
          +upla) | Média | `converte()` isolada testada por RN-018/AMB-01
          +8; goldens do envelope pegam |                                
      229 +| Ordem não determinística das categorias dinâmicas quebra gol
          +den | Média | DT-011 (ordem da política); `test_io`/golden ass
          +eguram |                                                      
      230 +| Passo de conversão fora de posição quebra `total_despesas` o
          +u motivo | Média | Ordem fixa DT-012; teste de precedência (ca
          +mbio não id vs período/NF) |                                  
      231 +| `moeda`/`categoria` não normalizadas recusam despesas legíti
          +mas | Média | normalização trim+upper/lower; testes de `" usd 
          +"`, `ALIMENTACAO` |                                           
      232 +| Câmbio/política ausente tratado como recusa em vez de abort 
          +| Baixa | `ErroEntrada` + exit 1; `test_cli` cobre arquivo fal
          +tando |                                                       
      233 +| Stakeholder rejeita AMB-006/016/017 | Baixa/Média | Decisões
          + em `DECISIONS.md`; trocas isoladas em `regras.py` |          
      234 +| `CLAUDE.md` cita `--em-viagem` (agora removido) | Alta | Atu
          +alizar `CLAUDE.md` na implementação (DT-003b) |               

● Now research.md (Phase 0) with the new câmbio/policy decisions:

● Write(research.md)
  ⎿  Error writing file

  Read 1 file (ctrl+o to expand)

● Write(research.md)
  ⎿  Added 90 lines, removed 41 lines
        1  # Research — Motor de Cálculo de Reembolso
        2  
        3 -Fase 0 do plano. Não havia `NEEDS CLARIFICATION` em aberto (st
          -ack e CLI foram                                               
        4 -fixados pelo usuário); este arquivo consolida as decisões técn
          -icas e as                                                     
        5 -alternativas avaliadas.                                       
        3 +Fase 0 do plano (spec 1.4). Não há `NEEDS CLARIFICATION` em ab
          +erto: stack e CLI foram                                       
        4 +fixados pelo usuário e as ambiguidades de negócio foram resolv
          +idas na spec                                                  
        5 +(AMB-001..018) e no `/speckit-clarify` de 2026-07-31. Este arq
          +uivo consolida as decisões                                    
        6 +técnicas e alternativas avaliadas. R-001..R-005 vêm do plano 1
          +.1 (atualizadas onde a spec                                   
        7 +mudou); R-006..R-011 cobrem política externa e câmbio.        
        8  
        9  ## R-001 — Representação de dinheiro em Python
       10  
        9 -- **Decisão:** `decimal.Decimal` com `quantize(Decimal("0.01")
          -, ROUND_HALF_UP)`.                                            
       10 -  Ler o JSON com `json.load(f, parse_float=Decimal)` para que 
          -os valores nunca                                              
       11 -  passem por `float`.                                         
       12 -- **Rationale:** RN-011 pede 2 casas e half-up; `float` binári
          -o não representa                                              
       13 -  `0.01` exatamente e produziria erros de centavo nas somas (o
          - teste golden exige                                           
       14 -  igualdade exata). `parse_float=Decimal` preserva a precisão 
          -original do texto                                             
       15 -  (`33.333`) até o `quantize` controlado.                     
       16 -- **Alternativas consideradas:** inteiros em centavos (funcion
          -a, mas exige                                                  
       17 -  conversão manual em toda leitura/escrita e complica valores 
          -com >2 casas antes                                            
       18 -  do arredondamento); `float` + `round()` (descartado — imprec
          -iso para dinheiro).                                           
       11 +- **Decisão:** `decimal.Decimal` com `quantize(Decimal("0.01")
          +, ROUND_HALF_UP)`; JSON lido                                  
       12 +  com `json.load(f, parse_float=Decimal)`. Vale também para as
          + **taxas** de `cambio.json`.                                  
       13 +- **Rationale:** RN-011 pede 2 casas half-up; `float` não repr
          +esenta `0.01` e produziria erro                               
       14 +  de centavo nas somas e conversões (goldens exigem igualdade 
          +exata). `parse_float=Decimal`                                 
       15 +  preserva a precisão do texto (`33.333`) até o `quantize` con
          +trolado.                                                      
       16 +- **Alternativas:** inteiros em centavos (conversão manual em 
          +toda leitura); `float`+`round()`                              
       17 +  (impreciso para dinheiro).                                  
       18  
       19  ## R-002 — Parsing e validação sem framework
       20  
       21  - **Decisão:** stdlib `json` para I/O e validação manual das r
           egras em `regras.py`.
       23 -- **Rationale:** o usuário pediu funções de validação de regra
          - separadas e                                                  
       24 -  explícitas; a spec exige mensagens de recusa com texto exato
          -. Validação manual                                            
       25 -  dá controle total sobre o motivo retornado e mantém a regra 
          -visível.                                                      
       26 -- **Alternativas consideradas:** `pydantic` (bom para validaçã
          -o estrutural, mas                                             
       27 -  esconderia a lógica de regra de negócio e adicionaria depend
          -ência); `jsonschema`                                          
       28 -  (cobre forma, não regra de negócio).                        
       22 +- **Rationale:** o usuário pediu funções de validação de regra
          + separadas e explícitas; a spec                               
       23 +  exige mensagens de recusa com texto exato. Validação manual 
          +dá controle total sobre o motivo.                             
       24 +- **Alternativas:** `pydantic` (esconderia a regra, dependênci
          +a); `jsonschema` (só forma).                                  
       25  
       26  ## R-003 — Interface de linha de comando
       27  
       32 -- **Decisão:** `argparse`, comando único `calcular` com `--inp
          -ut`, `--output`,                                              
       33 -  `--em-viagem` (flag). Console script `calcular = src.cli:mai
          -n` no `pyproject.toml`.                                       
       34 -- **Rationale:** invocação exata definida pelo usuário; `argpa
          -rse` é stdlib e                                               
       35 -  suficiente para 3 argumentos; `store_true` mapeia `--em-viag
          -em` direto para o                                             
       36 -  booleano de contexto da RN-009.                             
       37 -- **Alternativas consideradas:** `click`/`typer` (dependência 
          -desnecessária).                                               
       28 +- **Decisão:** `argparse`, comando único `calcular`; console s
          +cript `calcular = src.cli:main`.                              
       29 +- **Atualização 1.4:** remove `--em-viagem` (viagem virou por-
          +registro, RN-009); adiciona                                   
       30 +  `--politica`/`--cambio` opcionais (default: arquivos empacot
          +ados em `src/informacoes_externas`).                          
       31 +  Ver R-009. `CLAUDE.md` (que ainda cita `--em-viagem`) precis
          +a ser atualizado.                                             
       32 +- **Alternativas:** `click`/`typer` — dependência desnecessári
          +a.                                                            
       33  
       34  ## R-004 — Serialização determinística da saída
       35  
       41 -- **Decisão:** `json.dump(..., ensure_ascii=False, indent=2)` 
          -com um `default=`                                             
       42 -  que converte `Decimal` em número de 2 casas; ordem de catego
          -rias e chaves fixa.                                           
       43 -- **Rationale:** motivos contêm acentos ("não", "inválido"); a
          - saída precisa ser                                            
       44 -  byte-estável para o teste golden e legível para o usuário.  
       45 -- **Alternativas consideradas:** `ensure_ascii=True` (escapa a
          -centos, ilegível);                                            
       46 -  ordenar chaves alfabeticamente (mudaria a ordem semântica da
          - Seção 4).                                                    
       36 +- **Decisão:** `json.dumps(..., ensure_ascii=False, indent=2)`
          + com `default=` que injeta                                    
       37 +  `Decimal` como número de 2 casas; ordem de chaves fixa.     
       38 +- **Rationale:** motivos contêm acentos ("não", "inválido", "c
          +ambio não identificado"); a saída                             
       39 +  precisa ser byte-estável para os goldens e legível.         
       40 +- **Atualização 1.4:** a saída **não** tem mais `em_viagem`; a
          + ordem do bloco `categorias` passa                            
       41 +  a ser dinâmica — ver R-011.                                 
       42  
       43  ## R-005 — Testes
       44  
       50 -- **Decisão:** `pytest` com parametrização; um teste por `RN-N
          -NN` e por caso de                                             
       51 -  borda da Seção 7; teste golden sobre o exemplo oficial.     
       52 -- **Rationale:** rastreabilidade spec ↔ teste por nome; parame
          -trização reduz                                                
       53 -  boilerplate das tabelas de casos.                           
       54 -- **Alternativas consideradas:** `unittest` (mais verboso para
          - tabelas).                                                    
       45 +- **Decisão:** `pytest`; um teste por `RN-NNN` (agora RN-001..
          +RN-020) e por caso de borda; dois                             
       46 +  goldens (exemplo e envelope). `test_cobertura_rn` audita a c
          +obertura das 20 RNs.                                          
       47 +- **Rationale:** rastreabilidade spec↔teste por nome; parametr
          +ização reduz boilerplate.                                     
       48 +- **Alternativas:** `unittest` (mais verboso).                
       49  
       56 -## Itens herdados da spec (não são decisão técnica, são regra)
       50 +## R-006 — Política externa: onde parsear e como resolver o ce
          +ntro de custo                                                 
       51  
       58 -- Hospedagem por registro (AMB-006), `total_despesas` monetári
          -o (AMB-012) e com                                             
       59 -  exclusão de valores ≤ 0 por valor (RN-014/D-004), desempate 
          -de duplicata pela 1ª                                          
       60 -  ocorrência (D-002) e tratamento de registro inválido (RN-013
          -) já estão resolvidos                                         
       61 -  na spec e apenas são implementados aqui.                    
       52 +- **Decisão:** `io_json.ler_politica` abre o arquivo; `politic
          +a.politica_de_dict` converte                                  
       53 +  dict→`Politica` (puro). A resolução do CC usa `centros_custo
          +[cc]` se existir, senão `padrao`                              
       54 +  (RN-015). As categorias válidas são as **chaves** do CC reso
          +lvido (RN-001); limite/periodicidade/                         
       55 +  observacao vêm de cada `CategoriaConfig`. `nota_fiscal_obrig
          +atoria_acima_de` e                                            
       56 +  `acrescimo_em_viagem_percentual` são globais.               
       57 +- **Rationale:** mantém o núcleo puro (I/O só na casca); RN-01
          +5/016/017 exigem dados, não código.                           
       58 +- **Alternativas:** constantes em `politica.py` (modelo 1.1) —
          + viola RN-004/015.                                            
       59 +                                                              
       60 +## R-007 — Conversão de moeda para a base                     
       61 +                                                              
       62 +- **Decisão:** registro sem `moeda` (ausente/`null`/vazio após
          + `trim`) ou com `moeda` = `moeda_base`                        
       63 +  do **`cambio.json`**: sem conversão, não é viagem. Moeda dif
          +erente da base: `valor_base =                                 
       64 +  round2(round2(valor_origem) × taxa)` (AMB-018). A `moeda` é 
          +normalizada trim+upper antes de                               
       65 +  comparar com `moeda_base` e com as chaves de `taxas` (Clarif
          +y 2026-07-31). A `moeda_base` de                              
       66 +  `politica-v4.json` é ignorada.                              
       67 +- **Rationale:** RN-018; arredondar origem e resultado (não a 
          +taxa) preserva centavo.                                       
       68 +- **Alternativas:** arredondar a taxa/só o resultado — diverge
          +m do centavo esperado.                                        
       69 +                                                              
       70 +## R-008 — Resolução da taxa por data (mais próxima, empate → 
          +menor)                                                        
       71 +                                                              
       72 +- **Decisão:** entre as datas de `taxas` que **contêm a moeda*
          +*, escolher a de menor                                        
       73 +  `abs(data_taxa − data_registro)` em dias; em empate, a **men
          +or** taxa. Busca irrestrita.                                  
       74 +  `None` se a moeda não existe em nenhuma data → RN-020.      
       75 +- **Rationale:** RN-019/AMB-017; cotações só em dias úteis; me
          +nor taxa no empate é conservadora.                            
       76 +- **Validação (envelope):** EUR em 2026-07-18 (sábado) → 07-17
          + (dist. 1, 5,96) vence 07-20 (dist. 2).                       
       77 +- **Alternativas:** interpolar (inventaria cotação); exigir da
          +ta exata (não pedido).                                        
       78 +                                                              
       79 +## R-009 — Carregamento e falha das fontes externas           
       80 +                                                              
       81 +- **Decisão:** `input`, `politica-v4.json` e `cambio.json` lid
          +os na casca com `parse_float=Decimal`;                        
       82 +  ausência ou JSON inparseável de qualquer um → `ErroEntrada` 
          +→ `stderr` + exit 1 (abort).                                  
       83 +  Distingue-se de "cambio não identificado" (recusa por regist
          +ro com arquivo presente, RN-020).                             
       84 +- **Rationale:** RN-013 (input) e RN-018/Clarify (câmbio); sem
          + `moeda_base` nada é valorável.                               
       85 +  Não há validação de consistência do conteúdo (assume-se bem 
          +formado — Seção 10).                                          
       86 +- **Alternativas:** degradação parcial sem câmbio — rejeitada 
          +no Clarify (abort).                                           
       87 +                                                              
       88 +## R-010 — "cambio não identificado": reporte e efeito no tota
          +l                                                             
       89 +                                                              
       90 +- **Decisão:** moeda ausente de todas as `taxas` → "cambio não
          + identificado", reembolso 0; sob a                            
       91 +  própria categoria se válida; **excluído de `total_despesas`*
          +* (sem valor em base). Categoria não                          
       92 +  aplicável prevalece (avaliada antes, DT-012).               
       93 +- **Rationale:** RN-020/AMB-017; preserva `total_despesas ≥ to
          +tal_aceito`.                                                  
       94 +- **Validação (envelope):** `e-006` GBP → sob `representacao`,
          + fora de `total_despesas`.                                    
       95 +                                                              
       96 +## R-011 — Ordem determinística das categorias dinâmicas      
       97 +                                                              
       98 +- **Decisão:** `categorias` segue a ordem das chaves do conjun
          +to do CC resolvido, só as com ≥1                              
       99 +  despesa (AMB-015); `reprovadas_sem_categoria` na ordem do in
          +put.                                                          
      100 +- **Rationale:** determinismo (Seção 9) sem depender da ordem 
          +de digitação; reflete a política.                             
      101 +- **Validação:** `CC-ENG-PLATAFORMA` → alimentacao, transporte
          +_urbano, hospedagem (golden 1);                               
      102 +  `CC-COMERCIAL` → alimentacao, transporte_urbano, hospedagem,
          + representacao (golden 2).                                    
      103 +- **Alternativas:** 1ª aparição no input (equivalente nos gold
          +ens, menos estável); alfabética.                              
      104 +                                                              
      105 +## Itens herdados da spec (regra, não decisão técnica)        
      106 +                                                              
      107 +- Hospedagem/"diaria" por registro (AMB-006), `total_despesas`
          + monetário (AMB-012) com exclusão de                          
      108 +  `valor ≤ 0` por valor (RN-014/D-004), desempate de duplicata
          + pela 1ª ocorrência (D-002), registro                         
      109 +  inválido (RN-013), teto por papel/periodicidade (D-006) e vi
          +agem por moeda/baldes (D-007) já estão                        
      110 +  resolvidos na spec e apenas são implementados aqui.         

● Now data-model.md (Phase 1):

  Read 1 file (ctrl+o to expand)

● Write(data-model.md)
  ⎿  Added 88 lines, removed 54 lines
       1  # Modelo de Dados — Motor de Cálculo de Reembolso
       2  
       3 -Estruturas internas do núcleo. Todas puras (sem I/O). Valores m
         -onetários são                                                  
       4 -`Decimal` com 2 casas. Nomes de campo de saída seguem a Seção 4
         - da spec.                                                      
       3 +Estruturas internas do núcleo (spec 1.4). Todas puras (sem I/O)
         +. Valores monetários são                                       
       4 +`Decimal` com 2 casas. Nomes de campo de saída seguem a Seção 4
         + da spec. **Não há mais**                                      
       5 +enum `Categoria` (categorias são dinâmicas por centro de custo,
         + RN-001/015) nem campo                                         
       6 +`em_viagem` na saída (viagem é por registro, RN-009).          
       7  
       8  ## Enums
       9  
       8 -### `Categoria` (categorias válidas — RN-001)                  
       9 -`ALIMENTACAO = "alimentacao"`, `TRANSPORTE_URBANO = "transporte
         -_urbano"`,                                                     
      10 -`HOSPEDAGEM = "hospedagem"`.                                   
      11 -                                                               
      10  ### `Motivo` (motivos de recusa — texto exato da spec)
      11  `CATEGORIA_NAO_APLICAVEL = "categoria não aplicável"`,
      12  `DATA_FORA_COMPETENCIA = "data fora da competência"`,
      13  `REGISTRO_DUPLICADO = "registro duplicado"`,
      14  `SEM_NOTA_FISCAL = "sem nota fiscal obrigatória"`,
      15  `VALOR_INVALIDO = "valor inválido"`,
      18 -`REGISTRO_INVALIDO = "registro inválido"`.                     
      16 +`REGISTRO_INVALIDO = "registro inválido"`,                     
      17 +`CAMBIO_NAO_IDENTIFICADO = "cambio não identificado"` (novo, RN
         +-020).                                                         
      18  
      19 +> `motivo` de categoria com limite ≤ 0 (RN-017) **não** é um va
         +lor de enum: é a `observacao`                                  
      20 +> da `CategoriaConfig` (texto livre) ou, se ausente, `CATEGORIA
         +_NAO_APLICAVEL`.                                               
      21 +                                                               
      22 +## Entidades da política externa (`politica-v4.json` → puro)   
      23 +                                                               
      24 +### `CategoriaConfig`                                          
      25 +| Campo | Tipo | Regra |                                       
      26 +|---|---|---|                                                  
      27 +| `limite` | `Decimal` | teto da categoria no CC (RN-004); ≤ 0 
         +→ não reembolsável (RN-017) |                                  
      28 +| `periodicidade` | str | `"dia"` (RN-002) ou `"diaria"` (RN-00
         +3) (RN-016) |                                                  
      29 +| `observacao` | str \| None | motivo quando `limite ≤ 0` (RN-0
         +17) |                                                          
      30 +                                                               
      31 +### `Politica`                                                 
      32 +| Campo | Tipo | Regra |                                       
      33 +|---|---|---|                                                  
      34 +| `padrao` | dict[str, `CategoriaConfig`] | conjunto usado quan
         +do o CC não existe (RN-015) |                                  
      35 +| `centros_custo` | dict[str, dict[str, `CategoriaConfig`]] | c
         +onjunto por CC |                                               
      36 +| `limiar_nf` | `Decimal` | `nota_fiscal_obrigatoria_acima_de` 
         +(RN-006) |                                                     
      37 +| `acrescimo_viagem_pct` | `Decimal` | `acrescimo_em_viagem_per
         +centual` (RN-009) |                                            
      38 +                                                               
      39 +**Resolução do CC (RN-015):** `conjunto = centros_custo.get(cc,
         + padrao)`. Categorias válidas =                                
      40 +chaves de `conjunto` (comparadas trim+lower, RN-001/AMB-003).  
      41 +                                                               
      42 +## Entidade do câmbio externo (`cambio.json` → puro)           
      43 +                                                               
      44 +### `Cambio`                                                   
      45 +| Campo | Tipo | Regra |                                       
      46 +|---|---|---|                                                  
      47 +| `moeda_base` | str | normalizada trim+upper; referência de "s
         +em conversão"/"viagem" (RN-018) |                              
      48 +| `taxas` | dict[`date`, dict[str, `Decimal`]] | por data, `MOE
         +DA → fator` (chaves de moeda trim+upper) |                     
      49 +                                                               
      50 +> A `moeda_base` de `politica-v4.json` é ignorada (RN-018).    
      51 +                                                               
      52  ## Entidades de entrada
      53  
      54  ### `Colaborador`
      55  | Campo | Tipo | Origem |
      56  |---|---|---|
      25 -| `id` | str | input |                                         
      26 -| `nome` | str | input |                                       
      27 -| `centro_custo` | str | input |                               
      57 +| `id` / `nome` / `centro_custo` | str | input (eco) |         
      58  
      59  ### `Periodo`
      60  | Campo | Tipo | Regra |
      61  |---|---|---|
      62  | `competencia` | str `YYYY-MM` | eco |
      33 -| `inicio` | `date` | limite inferior inclusive (RN-007) |     
      34 -| `fim` | `date` | limite superior inclusive (RN-007) |        
      63 +| `inicio` / `fim` | `date` | limites inclusive (RN-007) |     
      64  
      36 -### `Despesa` (após normalização — RN-011, RN-001)             
      65 +### `Despesa` (após normalização — RN-011, RN-001, RN-018)     
      66  | Campo | Tipo | Observação |
      67  |---|---|---|
      39 -| `id` | str | identificador técnico; não conta para duplicidad
         -e (AMB-002) |                                                  
      40 -| `data` | `date` | dia civil |                                
      68 +| `id` | str | técnico; não conta para duplicidade (AMB-002) | 
      69 +| `data` | `date` | dia civil; também resolve a taxa (RN-019) |
      70  | `categoria` | str | valor original informado |
      42 -| `categoria_norm` | str | `categoria.strip().lower()` para com
         -paração (RN-001) |                                             
      43 -| `descricao` | str | |                                        
      44 -| `fornecedor` | str | |                                       
      45 -| `valor` | `Decimal` | já `quantize` a 2 casas (RN-011) |     
      46 -| `tem_nota_fiscal` | bool | |                                 
      71 +| `categoria_norm` | str | `categoria.strip().lower()` (RN-001)
         + |                                                             
      72 +| `descricao` / `fornecedor` | str | |                         
      73 +| `valor_origem` | `Decimal` | `quantize` a 2 casas, na moeda d
         +e origem (RN-011) |                                            
      74 +| `moeda_norm` | str \| None | `moeda.strip().upper()`; `None` 
         +se ausente/`null`/vazio (RN-018) |                             
      75 +| `valor_base` | `Decimal` \| None | convertido para a base; `N
         +one` até a conversão ou se "cambio não identificado" |         
      76 +| `em_viagem` | bool | `moeda_norm is not None and moeda_norm !
         += cambio.moeda_base` (RN-009) |                                
      77 +| `tem_nota_fiscal` | bool | avaliada sobre `valor_base` (RN-00
         +6) |                                                           
      78  
      79 +**Validação estrutural (RN-013):** `moeda`, quando presente, de
         +ve ser texto; tipo não-textual                                 
      80 +(número/booleano/objeto) → `REGISTRO_INVALIDO`. `moeda` ausente
         +/`null`/vazio após `trim` →                                    
      81 +`moeda_norm = None` (não inválido).                            
      82 +                                                               
      83  **Chave de duplicidade (RN-008):** tupla
      49 -`(data, categoria_norm, descricao, fornecedor, valor, tem_nota_
         -fiscal)` —                                                     
      50 -**sem** `id`. Mantém-se a 1ª ocorrência na ordem do input (D-00
         -2); as demais                                                  
      51 -viram `REGISTRO_DUPLICADO`.                                    
      84 +`(data, categoria_norm, descricao, fornecedor, valor_origem, mo
         +eda_norm, tem_nota_fiscal)` — **sem**                          
      85 +`id`, com `valor`/`moeda` de **origem**. Mantém-se a 1ª ocorrên
         +cia (D-002); as demais →                                       
      86 +`REGISTRO_DUPLICADO`.                                          
      87  
      53 -**Chave de agregação diária (RN-002/003):** `(categoria_norm, d
         -ata)` para                                                     
      54 -`alimentacao` e `transporte_urbano`. `hospedagem` é por registr
         -o (RN-004).                                                    
      88 +**Agregação de teto:** periodicidade `"dia"` agrega por `(categ
         +oria_norm, data)` com **baldes por                             
      89 +`em_viagem`** (RN-002/009); `"diaria"` é por registro (RN-003).
      90  
      91  ## Entidades de saída
      92  
     ...
       94  | Campo | Tipo | Observação |
       95  |---|---|---|
       96  | `id` | str | id da despesa recusada |
       62 -| `motivo` | `Motivo` | |                                     
       63 -| `categoria_informada` | str \| None | preenchido só em `repr
          -ovadas_sem_categoria` |                                       
       97 +| `motivo` | str | valor de `Motivo` **ou** a `observacao` da 
          +categoria (RN-017) |                                          
       98 +| `categoria_informada` | str \| None | só em `reprovadas_sem_
          +categoria` |                                                  
       99  
      100  ### `ResultadoCategoria`
      101  | Campo | Tipo | Regra |
      102  |---|---|---|
       68 -| `total_despesas` | `Decimal` | soma do `valor` de aceitas + 
          -reprovadas da categoria, **exceto valores ≤ 0** (RN-014, D-004
          -) |                                                           
       69 -| `total_aceito` | `Decimal` | soma do `valor` das aceitas (RN
          --012) |                                                       
       70 -| `total_reembolso` | `Decimal` | soma após tetos (RN-002..RN-
          -005) |                                                        
       71 -| `reprovadas` | list[`Reprovacao`] | recusas cuja categoria d
          -eclarada é válida |                                           
      103 +| `total_despesas` | `Decimal` | soma do `valor_base` de aceit
          +as + reprovadas da categoria, **exceto `valor ≤ 0` e exceto "c
          +ambio não identificado"** (RN-014, AMB-017) |                 
      104 +| `total_aceito` | `Decimal` | soma do `valor_base` das aceita
          +s (RN-012) |                                                  
      105 +| `total_reembolso` | `Decimal` | soma após teto/periodicidade
          +/baldes (RN-002..005/009) |                                   
      106 +| `reprovadas` | list[`Reprovacao`] | recusas cuja categoria d
          +eclarada é válida (incl. limite ≤ 0 e cambio não identificado)
          + |                                                            
      107  
      108  Invariante: `total_despesas ≥ total_aceito ≥ total_reembolso` 
           (AMB-012).
      109  
     ...
      113  | `colaborador` | `Colaborador` |
      114  | `competencia` | str |
      115  | `periodo` | `{inicio, fim}` |
       81 -| `em_viagem` | bool |                                        
       82 -| `categorias` | dict[str, `ResultadoCategoria`] (as 3 válidas
          -, sempre presentes) |                                         
       83 -| `reprovadas_sem_categoria` | list[`Reprovacao`] (categoria n
          -ão aplicável + registro inválido) |                           
       84 -| `total_reembolso_geral` | `Decimal` |                       
      116 +| `categorias` | dict[str, `ResultadoCategoria`] — só as válid
          +as do CC **com ≥1 despesa** (AMB-015), na ordem das chaves do 
          +CC (DT-011) |                                                 
      117 +| `reprovadas_sem_categoria` | list[`Reprovacao`] (categoria n
          +ão aplicável + registro inválido), ordem do input |           
      118 +| `total_reembolso_geral` | `Decimal` (soma de `total_reembols
          +o` das categorias presentes) |                                
      119  
       86 -> As três categorias válidas aparecem sempre em `categorias`, 
          -mesmo com totais                                              
       87 -> zerados (nenhuma despesa naquela categoria) — mantém a saída
          - previsível.                                                  
      120 +> Sem campo `em_viagem`. Categorias configuradas sem despesas 
          +**não** aparecem (AMB-015).                                   
      121  
       89 -## Fluxo de transformação (pipeline — Seção 8 da spec)        
      122 +## Fluxo de transformação (pipeline — Seção 8 da spec 1.4)    
      123  
      124  ```
       92 -JSON bruto                                                    
       93 -  → validação estrutural (por registro)         → REGISTRO_INV
          -ALIDO (sem_categoria)                                         
       94 -  → normalização (Decimal 2 casas, categoria_norm, multiplicad
          -or de viagem nos tetos)                                       
       95 -  → deduplicação (1ª ocorrência vence)          → REGISTRO_DUP
          -LICADO                                                        
       96 -  → gate categoria válida                        → CATEGORIA_N
          -AO_APLICAVEL (sem_categoria)                                  
       97 -  → gate período [inicio, fim]                   → DATA_FORA_C
          -OMPETENCIA                                                    
       98 -  → gate valor > 0                               → VALOR_INVAL
          -IDO                                                           
       99 -  → gate nota fiscal (valor > 100 exige NF)      → SEM_NOTA_FI
          -SCAL                                                          
      100 -  → aceitas: aplica teto (dia p/ alim/transp, registro p/ hosp
          -edagem)                                                       
      101 -  → agrega por categoria (total_despesas, total_aceito, total_
          -reembolso) + total geral                                      
      102 -Resultado                                                     
      125 +JSON bruto (input) + Politica + Cambio (já carregados; abort s
          +e qualquer arquivo falta/inválido)                            
      126 +  → validação estrutural (por registro)          → REGISTRO_IN
          +VALIDO (sem_categoria)                                        
      127 +  → normalização (valor 2 casas; categoria_norm; moeda_norm; e
          +m_viagem)                                                     
      128 +  → gate categoria válida (chaves do CC)          → CATEGORIA_
          +NAO_APLICAVEL (sem_categoria)                                 
      129 +  → gate limite > 0                               → observacao
          + / CATEGORIA_NAO_APLICAVEL (sob a categoria)                  
      130 +  → CONVERSÃO (taxa por data; valor_base)         → CAMBIO_NAO
          +_IDENTIFICADO (sob a categoria; fora do total)                
      131 +  → deduplicação (1ª ocorrência; chave inclui moeda) → REGISTR
          +O_DUPLICADO                                                   
      132 +  → gate período [inicio, fim]                    → DATA_FORA_
          +COMPETENCIA                                                   
      133 +  → gate valor > 0                                → VALOR_INVA
          +LIDO                                                          
      134 +  → gate nota fiscal (valor_base > limiar exige NF) → SEM_NOTA
          +_FISCAL                                                       
      135 +  → aceitas: teto por periodicidade (dia c/ baldes de viagem; 
          +diaria por registro)                                          
      136 +  → agrega por categoria + total geral                        
      137 +Resultado (sem em_viagem)                                     
      138  ```
      139  
      105 -`total_despesas` acumula o `valor` das despesas com categoria 
          -válida (aceitas e                                             
      106 -reprovadas por duplicidade/período/NF) **cujo `valor > 0`** — 
          -valores ≤ 0 ficam                                             
      107 -fora da somatória por valor, não por motivo (RN-014, D-004; ex
          -.: `d-009` −45,00).                                           
      108 -Registros inválidos e categoria não aplicável não entram em ne
          -nhuma categoria                                               
      109 -(vão para `reprovadas_sem_categoria`).                        
      140 +`total_despesas` acumula o `valor_base` das despesas de catego
          +ria válida (aceitas e reprovadas por                          
      141 +limite ≤ 0 / duplicidade / período / NF) **cujo `valor > 0`**;
          + exclui `valor ≤ 0` (por valor, não por                       
      142 +motivo — RN-014/D-004) e "cambio não identificado" (sem `valor
          +_base` — AMB-017). Registros inválidos e                      
      143 +categoria não aplicável vão para `reprovadas_sem_categoria`.  

● Now the CLI contract:

  Read 1 file (ctrl+o to expand)

● Write(contracts\cli-contract.md)
  ⎿  Added 36 lines, removed 30 lines
       1  # Contrato da CLI — `calcular`
       2  
       3 -Interface pública do sistema. É o único ponto de contato com o 
         -usuário.                                                       
       3 +Interface pública do sistema (spec 1.4). Único ponto de contato
         + com o usuário.                                                
       4 +Mudanças desde 1.1: **removido `--em-viagem`** (viagem é por re
         +gistro, RN-009);                                               
       5 +**adicionados** `--politica`/`--cambio` (opcionais); a saída **
         +não** tem mais `em_viagem`;                                    
       6 +o câmbio ausente/inválido **aborta**.                          
       7  
       8  ## Invocação
       9  
      10  ```
       8 -calcular --input <arquivo.json> --output <arquivo.json> [--em-v
         -iagem]                                                         
      11 +calcular --input <arquivo.json> --output <arquivo.json> [--poli
         +tica <arquivo.json>] [--cambio <arquivo.json>]                 
      12  ```
      13  
      14  Em desenvolvimento (sem instalar o console script):
      15  
      16  ```
      14 -python -m src --input <arquivo.json> --output <arquivo.json> [-
         --em-viagem]                                                    
      17 +python -m src --input <arquivo.json> --output <arquivo.json> [-
         +-politica ...] [--cambio ...]                                  
      18  ```
      19  
      20  ## Argumentos
      21  
      22  | Argumento | Obrigatório | Tipo | Default | Significado |
      23  |---|---|---|---|---|
      21 -| `--input` | sim | caminho | — | Arquivo JSON de entrada com c
         -olaborador, período e despesas |                               
      22 -| `--output` | sim | caminho | — | Arquivo JSON a ser escrito c
         -om o resultado |                                               
      23 -| `--em-viagem` | não | flag booleana | `false` | Se presente, 
         -aplica limites ampliados em 50% (RN-009) a todas as despesas do
         - input |                                                       
      24 +| `--input` | sim | caminho | — | JSON de entrada: colaborador,
         + período e despesas |                                          
      25 +| `--output` | sim | caminho | — | JSON a ser escrito com o res
         +ultado |                                                       
      26 +| `--politica` | não | caminho | `src/informacoes_externas/poli
         +tica-v4.json` | Política externa de categorias/limites por CC (
         +RN-015) |                                                      
      27 +| `--cambio` | não | caminho | `src/informacoes_externas/cambio
         +.json` | Tabela de câmbio: `moeda_base` + `taxas` por data (RN-
         +018) |                                                         
      28  
      25 -- `--em-viagem` é `store_true`: presença = `true`, ausência = `
         -false`. Não recebe valor.                                      
      26 -- O valor de `--em-viagem` sobrepõe/define `em_viagem`; se o in
         -put também trouxer                                             
      27 -  `em_viagem`, a flag da CLI é a fonte de verdade (o usuário in
         -forma em viagem —                                              
      28 -  AMB-008). *(Decisão de plano; se preferir que o campo do JSON
         - vença, é troca de 1 linha.)*                                  
      29 +- Sem regra de negócio na CLI. Os defaults resolvem os arquivos
         + empacotados relativos ao pacote `src`.                        
      30 +- Não há mais flag `--em-viagem`; a condição de viagem é deriva
         +da por registro pela `moeda` (RN-009).                         
      31  
      32  ## Entrada (arquivo `--input`)
      33  
      32 -Estrutura conforme `exemplos/despesas-exemplo.json` e Seção 4 d
         -a spec:                                                        
      34 +Conforme `exemplos/despesas-exemplo.json`, `exemplos/despesas-e
         +nvelope.json` e Seção 4:                                       
      35  `colaborador{id,nome,centro_custo}`, `periodo{competencia,inici
          o,fim}`,
      34 -`despesas[]{id,data,categoria,descricao,fornecedor,valor,tem_no
         -ta_fiscal}`.                                                   
      35 -O campo de topo `em_viagem` é opcional.                        
      36 +`despesas[]{id,data,categoria,descricao,fornecedor,valor,tem_no
         +ta_fiscal, moeda?}`.                                           
      37 +O campo `despesas[].moeda` é **opcional** (ausente/`null`/vazio
         + = moeda base, sem conversão).                                 
      38 +**Não** há mais campo de topo `em_viagem`.                     
      39  
      40  ## Saída (arquivo `--output`)
      41  
      39 -JSON conforme o exemplo da Seção 4 da spec. Contrato resumido: 
      42 +JSON conforme os exemplos das Seções 4 da spec. Contrato resumi
         +do (categorias **dinâmicas** por CC):                          
      43  
      44  ```json
      45  {
      46    "colaborador": { "id": "…", "nome": "…", "centro_custo": "…" 
          },
      47    "competencia": "YYYY-MM",
      48    "periodo": { "inicio": "YYYY-MM-DD", "fim": "YYYY-MM-DD" },
      46 -  "em_viagem": false,                                          
      49    "categorias": {
      48 -    "alimentacao":       { "total_despesas": 0.00, "total_aceit
         -o": 0.00, "total_reembolso": 0.00, "reprovadas": [ { "id": "…",
         - "motivo": "…" } ] },                                          
      49 -    "transporte_urbano": { "total_despesas": 0.00, "total_aceit
         -o": 0.00, "total_reembolso": 0.00, "reprovadas": [] },         
      50 -    "hospedagem":        { "total_despesas": 0.00, "total_aceit
         -o": 0.00, "total_reembolso": 0.00, "reprovadas": [] }          
      50 +    "<categoria válida do CC com ≥1 despesa>": {               
      51 +      "total_despesas": 0.00, "total_aceito": 0.00, "total_reem
         +bolso": 0.00,                                                  
      52 +      "reprovadas": [ { "id": "…", "motivo": "…" } ]           
      53 +    }                                                          
      54    },
      55    "reprovadas_sem_categoria": [ { "id": "…", "categoria_informa
          da": "…", "motivo": "…" } ],
      56    "total_reembolso_geral": 0.00
      57  }
      58  ```
      59  
      57 -- Todos os valores monetários com **exatamente 2 casas decimais
         -**.                                                            
      60 +- **Sem** campo `em_viagem`.                                   
      61 +- Todos os valores monetários com **exatamente 2 casas decimais
         +**, na **moeda base** (BRL) já convertida.                     
      62  - Acentos preservados (UTF-8, sem escape).
      59 -- As três categorias válidas sempre presentes, mesmo com totais
         - zerados.                                                      
      60 -- Motivos possíveis: `categoria não aplicável`, `data fora da c
         -ompetência`,                                                   
      61 -  `registro duplicado`, `sem nota fiscal obrigatória`, `valor i
         -nválido`,                                                      
      62 -  `registro inválido`.                                         
      63 +- O bloco `categorias` lista **só** as categorias válidas do CC
         + com ≥1 despesa (AMB-015), na ordem das                        
      64 +  chaves do CC resolvido na política (DT-011). Categorias confi
         +guradas sem despesas não aparecem.                             
      65 +- Motivos possíveis: `categoria não aplicável`, `data fora da c
         +ompetência`, `registro duplicado`,                             
      66 +  `sem nota fiscal obrigatória`, `valor inválido`, `registro in
         +válido`, `cambio não identificado`, ou a                       
      67 +  `observacao` da categoria (limite ≤ 0).                      
      68  
      69  ## Códigos de saída
      70  
      71  | Código | Situação |
      72  |---|---|
      68 -| `0` | Sucesso: resultado escrito em `--output` (mesmo que haj
         -a despesas reprovadas) |                                       
      69 -| `2` | Erro de uso: argumento obrigatório ausente/ inválido (p
         -adrão do `argparse`) |                                         
      70 -| `1` | Erro irrecuperável de entrada: arquivo `--input` inexis
         -tente, JSON de topo inparseável, ou campos de topo obrigatórios
         - ausentes (RN-013). Mensagem em `stderr`, nada escrito em `--ou
         -tput` |                                                        
      73 +| `0` | Sucesso: resultado escrito em `--output` (mesmo com des
         +pesas reprovadas) |                                            
      74 +| `2` | Erro de uso: argumento obrigatório ausente/inválido (pa
         +drão do `argparse`) |                                          
      75 +| `1` | Erro irrecuperável: `--input`, `--politica` ou `--cambi
         +o` inexistente ou com JSON inparseável; JSON de topo do input i
         +nválido; ou campos de topo obrigatórios ausentes (RN-013, RN-01
         +8). Mensagem em `stderr`, nada escrito em `--output` |         
      76  
      72 -- Registro de despesa malformado **não** aborta: vira `registro
         - inválido` em                                                  
      73 -  `reprovadas_sem_categoria` e a execução termina com código `0
         -` (RN-013).                                                    
      74 -- Erros e mensagens vão para `stderr`; `stdout` fica livre (a s
         -aída de dados vai                                              
      75 -  para o arquivo `--output`).                                  
      77 +- Registro de despesa malformado **não** aborta: vira `registro
         + inválido` em `reprovadas_sem_categoria`,                      
      78 +  execução termina com `0` (RN-013).                           
      79 +- Uma `moeda` sem taxa em todo o câmbio **não** aborta: vira `c
         +ambio não identificado` por registro                           
      80 +  (RN-020). Já o **arquivo** de câmbio ausente/inparseável abor
         +ta com `1` (RN-018).                                           
      81 +- Erros vão para `stderr`; `stdout` fica livre (dados vão para 
         +`--output`).                                                   

● Now quickstart.md with both goldens (including the envelope golden I
  computed):

  Read 1 file (ctrl+o to expand)

● Write(quickstart.md)
  ⎿  Added 62 lines, removed 23 lines
      1  # Quickstart — Motor de Cálculo de Reembolso
      2  
      3 -Guia de execução e validação. Detalhes de regra estão na [`spec.
        -md`](./spec.md),                                                
      3 +Guia de execução e validação (spec 1.4). Detalhes de regra na [`
        +spec.md`](./spec.md),                                           
      4  de arquitetura no [`plan.md`](./plan.md) e da CLI em
      5  [`contracts/cli-contract.md`](./contracts/cli-contract.md).
      6  
     ...
       20  ## Rodar
       21  
       22  ```bash
       23 -# com o console script instalado                              
       23 +# console script instalado (usa política/câmbio empacotados em
          + src/informacoes_externas/)                                   
       24  calcular --input exemplos/despesas-exemplo.json --output resul
           tado.json
       25  
       26 -# ou, sem instalar, direto do repositório                     
       26 +# sem instalar, direto do repositório                         
       27  python -m src --input exemplos/despesas-exemplo.json --output 
           resultado.json
       28  
       29 -# marcando toda a competência como em viagem (limites +50%)   
       30 -calcular --input exemplos/despesas-exemplo.json --output resul
          -tado.json --em-viagem                                         
       29 +# input com moedas estrangeiras (converte via cambio.json; via
          +gem por registro)                                             
       30 +calcular --input exemplos/despesas-envelope.json --output resu
          +ltado.json                                                    
       31 +                                                              
       32 +# apontando política/câmbio alternativos                      
       33 +calcular --input in.json --output out.json --politica outra-po
          +litica.json --cambio outro-cambio.json                        
       34  ```
       35  
       36 +> Não há mais `--em-viagem`: viagem é derivada por registro (m
          +oeda ≠ base, RN-009).                                         
       37 +                                                              
       38  ## Validação ponta a ponta (aceite)
       39  
       35 -Rodar sobre `exemplos/despesas-exemplo.json` **sem** `--em-via
          -gem` deve produzir a                                          
       36 -saída da Seção 4 da spec. Verificações-chave:                 
       40 +### Golden 1 — `exemplos/despesas-exemplo.json` (`CC-ENG-PLATA
          +FORMA`, sem `moeda`)                                          
       41  
       42 +Todos os registros na base (sem `moeda`) → nenhum é viagem; a 
          +saída é a da Seção 4 da spec.                                 
       43 +                                                              
       44  | O que conferir | Esperado |
       45  |---|---|
       40 -| `total_reembolso_geral` | `585.00`? Não — **`585.43`** |    
       41 -| `alimentacao` | `total_despesas 402.83`, `total_aceito 306.9
          -3`, `total_reembolso 255.43` |                                
       46 +| `total_reembolso_geral` | **`351.43`** |                    
       47 +| `alimentacao` | `total_despesas 402.83`, `total_aceito 306.9
          +3`, `total_reembolso 271.43` |                                
       48  | `transporte_urbano` | `total_despesas 200.01` (exclui `d-009
           ` −45,00, RN-014/D-004), `total_aceito 100.00`, `total_reembol
           so 80.00` |
       43 -| `hospedagem` | `total_despesas 1170.00`, `total_aceito 480.0
          -0`, `total_reembolso 250.00` |                                
       44 -| Reprovadas | `d-004` sem NF, `d-007` duplicado, `d-008` fora
          - competência, `d-009` valor inválido, `d-013` sem NF, `d-005` 
          -categoria não aplicável |                                     
       45 -| Invariante | `total_despesas ≥ total_aceito ≥ total_reembols
          -o` em toda categoria |                                        
       46 -| Casas decimais | todo valor com 2 casas |                   
       47 -| Acentos | motivos legíveis ("não", "inválido"), sem escape |
       49 +| `hospedagem` | limite 0,00 → não reembolsável: `total_despes
          +as 1170.00`, `total_aceito 0.00`, `total_reembolso 0.00`; `d-0
          +10`/`d-013` motivo `nao reembolsavel` |                       
       50 +| Reprovadas | `d-004` sem NF, `d-007` duplicado, `d-008` fora
          + competência, `d-009` valor inválido; `d-005` coworking em `re
          +provadas_sem_categoria` |                                     
       51 +| Sem `em_viagem` | a chave `em_viagem` **não** aparece na saí
          +da |                                                          
       52  
       53 +### Golden 2 — `exemplos/despesas-envelope.json` (`CC-COMERCIA
          +L`, moedas EUR/USD/GBP)                                       
       54 +                                                              
       55 +Política `CC-COMERCIAL`: alimentacao 90 (dia), transporte_urba
          +no 150 (dia), hospedagem 400 (diaria),                        
       56 +representacao 300 (dia); NF > 100; viagem +50%. Conversões usa
          +das: EUR 07-14 = 5,93; EUR 07-15 = 5,88;                      
       57 +EUR 07-18 (sábado) → 07-17 = 5,96; USD 07-20 = 5,50; GBP inexi
          +stente.                                                       
       58 +                                                              
       59 +| Registro | Cálculo | Resultado |                            
       60 +|---|---|---|                                                 
       61 +| `e-001` representacao BRL 340 (07-13) | base, não-viagem; mi
          +n(340, 300) | aceito 340,00; reembolso 300,00 |               
       62 +| `e-002` alimentacao EUR 22 (07-14) | 22×5,93 = 130,46; viage
          +m (limite 135); NF ok | aceito 130,46; reembolso 130,46 |     
       63 +| `e-003` alimentacao EUR 14,50 (07-15) | 14,50×5,88 = 85,26; 
          +85,26 ≤ 100 → NF dispensada | aceito 85,26; reembolso 85,26 | 
       64 +| `e-004` alimentacao EUR 30 (07-18 sáb) | 30×5,96 = 178,80; v
          +iagem (limite 135); min(178,80, 135) | aceito 178,80; reembols
          +o 135,00 |                                                    
       65 +| `e-005` transporte USD 40 (07-20) | 40×5,50 = 220,00 > 100 e
          + sem NF | recusado `sem nota fiscal obrigatória` |            
       66 +| `e-006` representacao GBP 55 (07-21) | GBP ausente das taxas
          + | recusado `cambio não identificado`; fora de `total_despesas
          +` |                                                           
       67 +| `e-007` hospedagem BRL 1200 (07-22) | diaria; min(1200, 400)
          + | aceito 1200,00; reembolso 400,00 |                         
       68 +| `e-008` alimentacao BRL 95 (07-23) | base; min(95, 90) | ace
          +ito 95,00; reembolso 90,00 |                                  
       69 +| `e-009` coworking BRL 120 (07-24) | fora do conjunto do CC |
          + recusado `categoria não aplicável` (sem_categoria) |         
       70 +| `e-010` alimentacao BRL 88 (07-27) | sem `moeda` → base; min
          +(88, 90) | aceito 88,00; reembolso 88,00 |                    
       71 +                                                              
       72 +Totais esperados (cada despesa de alimentação está num dia dis
          +tinto, então cada dia é seu próprio balde):                   
       73 +                                                              
       74 +| Categoria | total_despesas | total_aceito | total_reembolso 
          +| reprovadas |                                                
       75 +|---|---|---|---|---|                                         
       76 +| `alimentacao` | 577.52 | 577.52 | **528.72** | — |          
       77 +| `transporte_urbano` | 220.00 | 0.00 | 0.00 | `e-005` sem not
          +a fiscal obrigatória |                                        
       78 +| `hospedagem` | 1200.00 | 1200.00 | 400.00 | — |             
       79 +| `representacao` | 340.00 | 340.00 | 300.00 | `e-006` cambio 
          +não identificado |                                            
       80 +| `reprovadas_sem_categoria` | — | — | — | `e-009` categoria n
          +ão aplicável (coworking) |                                    
       81 +                                                              
       82 +- `total_reembolso_geral` = 528,72 + 0 + 400,00 + 300,00 = **`
          +1228.72`**.                                                   
       83 +- `alimentacao.total_reembolso` = 130,46 + 85,26 + 135,00 + 90
          +,00 + 88,00 = 528,72.                                         
       84 +- Ordem do bloco `categorias` (DT-011): alimentacao, transport
          +e_urbano, hospedagem, representacao.                          
       85 +- Invariante `total_despesas ≥ total_aceito ≥ total_reembolso`
          + vale em todas.                                               
       86 +                                                              
       87  ## Testes
       88  
       89  ```bash
       52 -pytest                 # tudo                                 
       53 -pytest tests/test_regras.py         # 1 teste por RN          
       54 -pytest tests/test_integracao.py     # golden test do exemplo o
          -ficial                                                        
       55 -pytest -k rn_006                    # foco numa regra         
       90 +pytest                              # tudo                    
       91 +pytest tests/test_regras.py         # 1 teste por RN (RN-001..
          +RN-020)                                                       
       92 +pytest tests/test_cambio.py         # conversão, data mais pró
          +xima, empate, cambio não identificado                         
       93 +pytest tests/test_integracao.py     # goldens: exemplo (351.43
          +) e envelope (1228.72)                                        
       94 +pytest -k rn_018                    # foco numa regra         
       95  ```
       96  
       58 -Convenção: cada teste cita o `RN-NNN` ou o caso de borda da Se
          -ção 7 no nome,                                                
       59 -fechando a rastreabilidade spec ↔ teste. Um teste de auditoria
          - garante que toda                                             
       60 -`RN-001..RN-014` tem cobertura.                               
       97 +Convenção: cada teste cita o `RN-NNN` ou o caso de borda da Se
          +ção 7 no nome. `test_cobertura_rn`                            
       98 +garante que toda `RN-001..RN-020` tem cobertura.              
       99  
      100  ## Cenários de erro (ver contrato da CLI)
      101  
      102  | Cenário | Resultado |
      103  |---|---|
       66 -| `--input` inexistente ou JSON de topo inválido | mensagem em
          - `stderr`, código de saída `1`, nada escrito |                
      104 +| `--input`/`--politica`/`--cambio` inexistente ou JSON inpars
          +eável | mensagem em `stderr`, código `1`, nada escrito |      
      105  | Falta `--input` ou `--output` | erro de uso do `argparse`, c
           ódigo `2` |
       68 -| Um registro de despesa malformado | recusado como `registro 
          -inválido`; os demais processados; código `0` |                
      106 +| Registro de despesa malformado (ex.: `moeda` numérica) | `re
          +gistro inválido`; os demais processados; código `0` |         
      107 +| `moeda` sem taxa em todo o câmbio (ex.: GBP) | `cambio não i
          +dentificado` **por registro**; código `0` |                   

● All Phase 0 and Phase 1 artifacts are regenerated for spec 1.4. No
  .specify/extensions.yml → no post-plan hooks. Post-design constitution
  re-check: the constitution is still an unfilled template (no gates); the
  design honors the CLAUDE.md conventions (pure core with I/O only in the casca,
  one function per RN, Decimal throughout, no business rules introduced in the
  plan).

  Plan concluído — spec 1.4

  Branch: main (feature dir specs/001-motor-reembolso via .specify/feature.json)
  IMPL_PLAN: specs/001-motor-reembolso/plan.md (v1.1 → v1.4)

  Artefatos gerados/atualizados:
  - plan.md — nova arquitetura: casca de I/O lê os 3 JSON (input,
  politica-v4.json, cambio.json) e injeta Politica/Cambio já parseados no núcleo
  puro; pipeline reordenado (DT-012) com passo de conversão; DT-008
  (política/câmbio como dados), DT-009 (teto por periodicidade sobre conjunto
  dinâmico), DT-010 (conversão + taxa por data), DT-011 (ordem determinística
  das categorias), DT-003b (CLI sem --em-viagem, com --politica/--cambio).
  Inclui uma tabela do gap código-atual × spec 1.4.
  - research.md — R-006..R-011 para política externa, conversão, taxa por data,
  "cambio não identificado", carregamento/abort e ordenação dinâmica.
  - data-model.md — remove enum Categoria e campo em_viagem; adiciona
  CategoriaConfig, Politica, Cambio, Motivo.CAMBIO_NAO_IDENTIFICADO, e campos de
  câmbio/viagem em Despesa (moeda_norm, valor_origem, valor_base, em_viagem).
  - contracts/cli-contract.md — remove --em-viagem, adiciona
  --politica/--cambio, saída sem em_viagem e categorias dinâmicas, abort no
  câmbio ausente/inválido.
  - quickstart.md — dois goldens com números conferidos: exemplo (351.43) e
  envelope (1228.72) — computei o golden completo do despesas-envelope.json
  (conversões EUR/USD, GBP → "cambio não identificado", NF pós-conversão,
  baldes), que a spec havia deixado para esta fase.

  Pontos a sinalizar para a próxima fase (/speckit-tasks → /speckit-implement):
  1. tasks.md está desatualizado (ainda no modelo 1.1) — precisa ser regenerado
  por /speckit-tasks.
  2. CLAUDE.md ainda documenta calcular ... [--em-viagem]; a task de CLI deve
  atualizá-lo (DT-003b).
  3. O código atual (politica.py com constantes, enum Categoria, --em-viagem,
  em_viagem na saída, sem câmbio) será substancialmente reescrito — a tabela de
  gap na Seção 0 do plan.md lista as cinco frentes.

  Próximo comando sugerido: /speckit-tasks para gerar a lista de tarefas
  ordenada a partir deste plano.

✻ Baked for 7m 21s

※ recap: You're evolving the reimbursement engine spec via Spec Kit; the spec is now at v1.4 (external policy, currency conversion, per-record travel) and all design artifacts are regenerated. Next: run /speckit-tasks to regenerate the stale tasks.md. (disable recaps in /config)

❯ /speckit-tasks                                                                

● I'll generate tasks.md from the updated design. First let me read the current
  tasks.md (to replace) and the spec's user-story structure, plus confirm the
  tasks template.

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● The existing tasks.md records completed work through Fase 5 (D-004) — but the
  code sits at that D-004 state and the whole of D-005 (política externa), D-006
  (regras agnósticas) and D-007 (câmbio + viagem) is untasked and unbuilt.
  Following this file's established convention (append phases, continue
  numbering, don't renumber), I'll add Fase 6–10 for the unbuilt spec-1.4 work.
  No .specify/extensions.yml → no hooks.

  There are no P1/P2/P3 user stories (single deterministic engine — the file
  notes this), so tasks stay phase-organized in the file's existing rich style,
  continuing from T-028.

● Update(tasks.md)
  ⎿  Added 139 lines, removed 3 lines
      177    - **Aceite:** `pytest tests/test_integracao.py` passa contra
            a saída atualizada da Seção 4 da spec
      178    - **Commit:** `test(T-027): golden com transporte_urbano 200
           ,01 (D-004)`
      179  
      180 -*(Candidatas ainda em aberto, não acionadas: confirmar AMB-006
          - hospedagem por                                               
      181 -registro vs. por diária; precedência `--em-viagem` da CLI vs. 
          -campo `em_viagem`                                             
      182 -do JSON.)*                                                    
      180 +*(A candidata "AMB-006 hospedagem por registro" foi confirmada
          +; a de precedência                                            
      181 +`--em-viagem` da CLI foi **superada** por D-007 — a flag deixa
          + de existir.)*                                                
      182  
      183  ---
      184  
      185 +## Fase 6 — Fundação da política e câmbio externos (D-005 + D-
          +007)                                                          
      186 +                                                              
      187 +> Origem: `/speckit-specify` D-005 (política externa `politica
          +-v4.json`, spec 1.2),                                         
      188 +> D-006 (regras de teto agnósticas de categoria, spec 1.3), D-
          +007 (câmbio `cambio.json`                                     
      189 +> + viagem por moeda, spec 1.4) e `/speckit-clarify` 2026-07-3
          +1 (normalização de `moeda`,                                   
      190 +> abort de câmbio ausente, `moeda` inválida). **Nada disso foi
          + construído** — o código                                      
      191 +> está no estado D-004. As Fases 6–10 escrevem direto para a s
          +pec 1.4 e **superam**                                         
      192 +> partes de T-003/004/005/007/008/011/012/013/014/015/016/018/
          +019/020/022/023 (ver                                          
      193 +> "Superadas" abaixo). Numeração continua de T-027; tasks anti
          +gas não são renumeradas.                                      
      194 +                                                              
      195 +- [ ] **T-028** [P] — Reescrever `src/modelo.py`: **remover** 
          +o enum `Categoria`; adicionar `Motivo.CAMBIO_NAO_IDENTIFICADO 
          += "cambio não identificado"` (7º motivo); novas dataclasses `C
          +ategoriaConfig(limite, periodicidade, observacao)`, `Politica(
          +padrao, centros_custo, limiar_nf, acrescimo_viagem_pct)`, `Cam
          +bio(moeda_base, taxas: dict[date, dict[str, Decimal]])`; esten
          +der `Despesa` com `valor_origem`, `moeda_norm`, `valor_base`, 
          +`em_viagem`; **remover** `em_viagem` de `Resultado`. Supera T-
          +004.                                                          
      196 +  - **Atende:** RN-015/016/017/018/020, `data-model.md`, DT-00
          +8                                                             
      197 +  - **Aceite:** `tests/test_modelo.py::test_motivos_texto_exat
          +o` cobre os 7 motivos (incl. "cambio não identificado"); `::te
          +st_resultado_sem_em_viagem`; `::test_despesa_campos_cambio`   
      198 +  - **Commit:** `feat(T-028): modelo com politica/cambio e via
          +gem por registro`                                             
      199 +                                                              
      200 +- [ ] **T-029** [P] — Reescrever `src/politica.py`: **remover*
          +* constantes fixas (`LIMITES_DIARIOS`, `LIMITE_HOSPEDAGEM`, `C
          +ATEGORIAS_VALIDAS`, `MULTIPLICADOR_VIAGEM`, `LIMIAR_NOTA_FISCA
          +L`); adicionar `politica_de_dict(d) -> Politica` e `cambio_de_
          +dict(d) -> Cambio` (puros: dict→estrutura, datas como `date`, 
          +taxas/limites como `Decimal`); manter `CASAS_DECIMAIS`. Supera
          + T-003.                                                       
      201 +  - **Atende:** RN-015/018, DT-008                            
      202 +  - **Aceite:** `tests/test_politica.py::test_politica_de_dict
          +` e `::test_cambio_de_dict` constroem as estruturas a partir d
          +e `src/informacoes_externas/{politica-v4,cambio}.json`        
      203 +  - **Commit:** `feat(T-029): politica/cambio como estruturas 
          +puras`                                                        
      204 +                                                              
      205 +- [ ] **T-030** — `src/io_json.py`: adicionar `ler_politica(ca
          +minho) -> Politica` e `ler_cambio(caminho) -> Cambio` (abrem c
          +om `parse_float=Decimal`, delegam a `politica.py`); levantar `
          +ErroEntrada` (abort, exit 1) se ausente/inparseável. Em `ler_e
          +ntrada`, **parar de ler** `em_viagem` do topo e manter `despes
          +as_brutas` cru (com `moeda`). Supera T-018.                   
      206 +  - **Atende:** RN-018 (abort câmbio), RN-013, Clarify (câmbio
          + abort), DT-012 passo 2                                       
      207 +  - **Aceite:** `tests/test_io.py::test_cambio_ausente_aborta`
          +, `::test_politica_ausente_aborta`, `::test_le_taxas_decimal` 
      208 +  - **Commit:** `feat(T-030): carga de politica e cambio com a
          +bort`                                                         
      209 +                                                              
      210 +## Fase 7 — Política, categoria e teto agnósticos de categoria
          + (D-005/D-006)                                                
      211 +                                                              
      212 +> Funções puras em `src/regras.py`, uma por RN. Editam o mesmo
          + arquivo → sequenciais;                                       
      213 +> testes em `tests/test_regras.py`/`test_politica.py` podem pr
          +eceder (TDD).                                                 
      214 +                                                              
      215 +- [ ] **T-031** — `resolve_conjunto(politica, centro_custo) ->
          + dict[str, CategoriaConfig]` em `src/regras.py`: `centros_cust
          +o.get(cc, padrao)` (RN-015).                                  
      216 +  - **Atende:** RN-015, AMB-013                               
      217 +  - **Aceite:** `tests/test_politica.py::test_rn_015_fallback_
          +padrao` (CC inexistente → `padrao`) e `::test_rn_015_cc_especi
          +fico` (`CC-ENG-PLATAFORMA`)                                   
      218 +  - **Commit:** `feat(T-031): resolucao de centro de custo (RN
          +-015)`                                                        
      219 +                                                              
      220 +- [ ] **T-032** — `valida_categoria(despesa, conjunto)` em `sr
          +c/regras.py`: `categoria_norm ∈ chaves(conjunto)`? senão `Moti
          +vo.CATEGORIA_NAO_APLICAVEL`. Sem `CATEGORIAS_VALIDAS` fixo. Su
          +pera T-008.                                                   
      221 +  - **Atende:** RN-001 (dinâmico), AMB-003, AMB-011           
      222 +  - **Aceite:** `tests/test_regras.py::test_rn_001_coworking_i
          +nvalida`, `::test_rn_001_uppercase_valida`, `::test_rn_001_rep
          +resentacao_so_comercial`                                      
      223 +  - **Commit:** `feat(T-032): categorias validas dinamicas (RN
          +-001)`                                                        
      224 +                                                              
      225 +- [ ] **T-033** — `valida_limite_categoria(despesa, config)` e
          +m `src/regras.py`: se `config.limite ≤ 0` → recusa com `motivo
          + = config.observacao or "categoria não aplicável"`, sob a próp
          +ria categoria (RN-017).                                       
      226 +  - **Atende:** RN-017, AMB-014                               
      227 +  - **Aceite:** `tests/test_regras.py::test_rn_017_limite_zero
          +_nao_reembolsavel` (hospedagem `CC-ENG-PLATAFORMA` → "nao reem
          +bolsavel", prevalece sobre sem NF)                            
      228 +  - **Commit:** `feat(T-033): categoria com limite <= 0 (RN-01
          +7)`                                                           
      229 +                                                              
      230 +- [ ] **T-034** — Tetos por periodicidade em `src/regras.py`: 
          +`aplica_teto_dia(aceitas, limite, fator)` com **baldes** por `
          +em_viagem` (RN-002/009), `aplica_teto_diaria(aceitas, limite, 
          +fator)` por registro (RN-003); limite efetivo por registro = `
          +limite × fator` se `em_viagem`. **Remover** `tetos_efetivos`, 
          +`aplica_teto_diario`, `aplica_teto_hospedagem`, `ORDEM_CATEGOR
          +IAS`. Supera T-012/013/014.                                   
      231 +  - **Atende:** RN-002/003/004/005/009/016, AMB-016           
      232 +  - **Aceite:** `tests/test_regras.py::test_rn_002_baldes_dia_
          +misto` (BRL 80 + convertido 80, limite base 90/viagem 135 → 80
          ++80=160), `::test_rn_003_diaria_por_registro`, `::test_rn_009_
          +viagem_por_registro`                                          
      233 +  - **Commit:** `feat(T-034): teto por periodicidade com balde
          +s (RN-002/003/009)`                                           
      234 +                                                              
      235 +## Fase 8 — Câmbio e gates dependentes de conversão (D-007 + C
          +larify)                                                       
      236 +                                                              
      237 +- [ ] **T-035** — Estender `normaliza_despesa` e `valida_estru
          +tura` em `src/regras.py`: `moeda_norm = moeda.strip().upper() 
          +or None`; `valor_origem` arredondado a 2 casas; `em_viagem = m
          +oeda_norm not in (None, cambio.moeda_base)`; `moeda` de tipo n
          +ão-textual → `REGISTRO_INVALIDO`; `""`/`null`/ausente → sem mo
          +eda. Supera T-005/006.                                        
      238 +  - **Atende:** RN-018 (normalização), RN-009, RN-013 (moeda),
          + RN-011, Clarify (normalização/tipo de `moeda`)               
      239 +  - **Aceite:** `tests/test_regras.py::test_rn_018_moeda_norma
          +lizada` (`" usd "`→`USD`), `::test_rn_013_moeda_numerica_inval
          +ida`, `::test_rn_018_moeda_base_sem_conversao`                
      240 +  - **Commit:** `feat(T-035): normalizacao de moeda e validaca
          +o de tipo (RN-018/013)`                                       
      241 +                                                              
      242 +- [ ] **T-036** — `taxa_por_data(cambio, moeda_norm, data) -> 
          +Decimal | None` em `src/regras.py` (RN-019): entre datas de `t
          +axas` que contêm a moeda, menor `abs(data_taxa − data)`; empat
          +e → menor taxa; `None` se a moeda não existe em nenhuma data. 
      243 +  - **Atende:** RN-019, AMB-017                               
      244 +  - **Aceite:** `tests/test_cambio.py::test_rn_019_data_exata`
          +, `::test_rn_019_fim_de_semana_mais_proxima` (07-18→07-17, 5,9
          +6), `::test_rn_019_empate_menor_taxa`                         
      245 +  - **Commit:** `feat(T-036): resolucao de taxa por data (RN-0
          +19)`                                                          
      246 +                                                              
      247 +- [ ] **T-037** — `converte(valor_origem, taxa)` (arredonda or
          +igem → × taxa cheia → arredonda resultado; AMB-018) e gate `va
          +lida_cambio(despesa, cambio)` em `src/regras.py`: se em viagem
          + e `taxa_por_data` é `None` → `Motivo.CAMBIO_NAO_IDENTIFICADO`
          +; senão preenche `valor_base` (registro base/sem moeda → `valo
          +r_base = valor_origem`).                                      
      248 +  - **Atende:** RN-018/020, AMB-017/018                       
      249 +  - **Aceite:** `tests/test_cambio.py::test_rn_018_converte_eu
          +r` (22×5,93=130,46), `::test_rn_020_cambio_nao_identificado` (
          +GBP), `::test_rn_018_arredondamento`                          
      250 +  - **Commit:** `feat(T-037): conversao e cambio nao identific
          +ado (RN-018/020)`                                             
      251 +                                                              
      252 +- [ ] **T-038** — Incluir `moeda_norm` na chave de duplicidade
          + (`Despesa.chave_duplicidade` em `src/modelo.py`) usando `valo
          +r_origem` (RN-008). Supera T-007.                             
      253 +  - **Atende:** RN-008 (moeda na chave)                       
      254 +  - **Aceite:** `tests/test_regras.py::test_rn_008_mantem_prim
          +eira` (inalterado) e `::test_rn_008_moeda_diferencia` (iguais 
          +salvo `moeda` não são duplicados)                             
      255 +  - **Commit:** `feat(T-038): moeda na chave de duplicidade (R
          +N-008)`                                                       
      256 +                                                              
      257 +- [ ] **T-039** — `valida_nota_fiscal(despesa, limiar)` em `sr
          +c/regras.py` passa a comparar `valor_base` (RN-006, após conve
          +rsão). Supera T-011.                                          
      258 +  - **Atende:** RN-006 (valor convertido)                     
      259 +  - **Aceite:** `tests/test_regras.py::test_rn_006_sobre_valor
          +_convertido` (`e-005` USD 40→220 sem NF → recusada) e `::test_
          +rn_006_limiar_exato`                                          
      260 +  - **Commit:** `feat(T-039): nota fiscal sobre valor converti
          +do (RN-006)`                                                  
      261 +                                                              
      262 +## Fase 9 — Pipeline, saída e CLI (integração)                
      263 +                                                              
      264 +- [ ] **T-040** — Reescrever `src/calculo.py` na ordem da Seçã
          +o 8/DT-012: estrutura → resolução política+câmbio → normalizaç
          +ão → categoria válida → limite>0 → **conversão** → dedup → per
          +íodo → valor → NF(convertido) → teto(baldes/periodicidade) → a
          +gregação. Assinatura `calcula(despesas_brutas, colaborador, pe
          +riodo, politica, cambio)` (sem `em_viagem`); conjunto **dinâmi
          +co** de categorias; `agrega_categoria` usa `valor_base` e excl
          +ui de `total_despesas` os `valor ≤ 0` **e** os "cambio não ide
          +ntificado". Supera T-015/016.                                 
      265 +  - **Atende:** DT-012, RN-012/014, AMB-010/015/017; integra R
          +N-001..RN-020                                                 
      266 +  - **Aceite:** `tests/test_calculo.py::test_ordem_gates_cambi
          +o`, `::test_agrega_exclui_cambio_nao_id`, `::test_categorias_d
          +inamicas_so_com_despesa`                                      
      267 +  - **Commit:** `feat(T-040): pipeline spec 1.4 com conversao 
          +e categorias dinamicas`                                       
      268 +                                                              
      269 +- [ ] **T-041** — Serialização em `src/io_json.py`: **remover*
          +* `em_viagem`; emitir só as categorias válidas do CC com ≥1 de
          +spesa, na **ordem das chaves do CC** (DT-011); suportar motivo
          + "cambio não identificado". Supera T-019.                     
      270 +  - **Atende:** RN-012, AMB-015, DT-011                       
      271 +  - **Aceite:** `tests/test_io.py::test_saida_sem_em_viagem`, 
          +`::test_ordem_categorias_por_politica`                        
      272 +  - **Commit:** `feat(T-041): saida sem em_viagem e categorias
          + dinamicas ordenadas`                                         
      273 +                                                              
      274 +- [ ] **T-042** — CLI `src/cli.py`: **remover** `--em-viagem`;
          + adicionar `--politica`/`--cambio` (default: `src/informacoes_
          +externas/{politica-v4,cambio}.json` resolvidos pelo pacote); l
          +igar leitura das 3 fontes → `calculo.calcula` → escrita; exit 
          +1 se input/política/câmbio ausente ou inválido. Supera T-020. 
          +Atualizar `src/cli.py` docstring de exit codes.               
      275 +  - **Atende:** DT-003b, RN-018 (abort)                       
      276 +  - **Aceite:** `tests/test_cli.py::test_cli_sem_em_viagem`, `
          +::test_cli_cambio_ausente_exit1`, `::test_cli_defaults_empacot
          +ados`                                                         
      277 +  - **Commit:** `feat(T-042): CLI com --politica/--cambio, sem
          + --em-viagem`                                                 
      278 +                                                              
      279 +- [ ] **T-043** [P] — Atualizar `CLAUDE.md`: assinatura `calcu
          +lar --input ... --output ... [--politica ...] [--cambio ...]` 
          +(sem `--em-viagem`); nota de que categorias/limites/limiar/via
          +gem vêm de `politica-v4.json` e o câmbio de `cambio.json`. Sup
          +era T-024.                                                    
      280 +  - **Atende:** DT-003b, documentação                         
      281 +  - **Aceite:** `CLAUDE.md` não menciona `--em-viagem`; cita a
          +s duas fontes externas                                        
      282 +  - **Commit:** `docs(tasks): atualiza comando da CLI no CLAUD
          +E.md`                                                         
      283 +                                                              
      284 +## Fase 10 — Testes, goldens e cobertura                      
      285 +                                                              
      286 +- [ ] **T-044** [P] — `tests/test_politica.py`: RN-015 (fallba
          +ck `padrao` / CC específico), construção de `Politica`/`Catego
          +riaConfig` a partir do arquivo real; conjuntos por CC.        
      287 +  - **Atende:** RN-015, RN-016                                
      288 +  - **Aceite:** `pytest tests/test_politica.py` verde         
      289 +  - **Commit:** `test(T-044): testes de politica externa (RN-0
          +15/016)`                                                      
      290 +                                                              
      291 +- [ ] **T-045** [P] — `tests/test_cambio.py`: RN-018/019/020 —
          + conversão, normalização de moeda, data mais próxima, empate →
          + menor, "cambio não identificado", e abort de arquivo ausente/
          +inparseável.                                                  
      292 +  - **Atende:** RN-018/019/020, Clarify                       
      293 +  - **Aceite:** `pytest tests/test_cambio.py` verde           
      294 +  - **Commit:** `test(T-045): testes de cambio (RN-018/019/020
          +)`                                                            
      295 +                                                              
      296 +- [ ] **T-046** — Reescrever `tests/test_regras.py` e `tests/t
          +est_bordas.py` para a spec 1.4: **remover** testes de `--em-vi
          +agem`/categorias fixas/`tetos_efetivos`; cobrir RN-002 baldes,
          + RN-003 diaria, RN-009 por registro, RN-017, RN-006 sobre conv
          +ertido; e as novas linhas da Seção 7 (moeda=base, sem moeda, d
          +ia misto, fim de semana, empate, cambio não identificado, NF p
          +ós-conversão). Supera T-017.                                  
      297 +  - **Atende:** RN-001..RN-020 (bordas), Seção 7              
      298 +  - **Aceite:** `pytest tests/test_regras.py tests/test_bordas
          +.py` verde                                                    
      299 +  - **Commit:** `test(T-046): testes de regra e bordas para sp
          +ec 1.4`                                                       
      300 +                                                              
      301 +- [ ] **T-047** [P] — Atualizar `tests/test_cobertura_rn.py`: 
          +auditar **RN-001..RN-020** (não mais RN-001..RN-014). Supera T
          +-023.                                                         
      302 +  - **Atende:** rastreabilidade (CLAUDE.md)                   
      303 +  - **Aceite:** `pytest tests/test_cobertura_rn.py` falha se f
          +altar teste de qualquer RN até RN-020                         
      304 +  - **Commit:** `test(T-047): cobertura ate RN-020`           
      305 +                                                              
      306 +- [ ] **T-048** — Goldens em `tests/test_integracao.py`: (a) `
          +exemplos/despesas-exemplo.json` (`CC-ENG-PLATAFORMA`) → `total
          +_reembolso_geral == 351.43`, **sem** `em_viagem`, `hospedagem`
          + não reembolsável (0,00), `alimentacao` 402.83/306.93/271.43, 
          +`transporte_urbano` 200.01/100.00/80.00; (b) `exemplos/despesa
          +s-envelope.json` (`CC-COMERCIAL`) → `total_reembolso_geral == 
          +1228.72` com os totais do `quickstart.md`. Supera T-022/027.  
      307 +  - **Atende:** RN-001..RN-020 ponta a ponta; quickstart (2 go
          +ldens)                                                        
      308 +  - **Aceite:** `pytest tests/test_integracao.py` bate exatame
          +nte os dois goldens                                           
      309 +  - **Commit:** `test(T-048): goldens exemplo (351,43) e envel
          +ope (1228,72)`                                                
      310 +                                                              
      311 +- [ ] **T-049** [P] — Ajustar `tests/test_modelo.py`, `tests/t
          +est_io.py`, `tests/test_cli.py` remanescentes ao modelo 1.4 (s
          +em enum `Categoria`, sem `em_viagem`); remover asserts obsolet
          +os.                                                           
      312 +  - **Atende:** consistência dos testes                       
      313 +  - **Aceite:** `pytest` inteiro verde, sem referências a `Cat
          +egoria`/`em_viagem`/`--em-viagem`                             
      314 +  - **Commit:** `test(T-049): ajusta testes remanescentes ao m
          +odelo 1.4`                                                    
      315 +                                                              
      316 +### Superadas pelas Fases 6–10 (código D-004 → spec 1.4)      
      317 +                                                              
      318 +T-003 (constantes fixas) → T-029; T-004 (enum/modelo) → T-028;
          + T-005/006 (normalização/estrutura) → T-035; T-007 (dedup) → T
          +-038; T-008 (categoria) → T-032; T-011 (NF) → T-039; T-012/013
          +/014 (tetos) → T-034; T-015/016 (agrega/pipeline) → T-040; T-0
          +18 (leitura) → T-030; T-019 (serialização) → T-041; T-020 (CLI
          +) → T-042; T-022/027 (golden) → T-048; T-023 (cobertura) → T-0
          +47; T-024 (CLAUDE.md) → T-043. As demais (T-001/002/009/010/01
          +7/021/025/026) permanecem válidas ou têm seus testes reescrito
          +s por T-046.                                                  
      319 +                                                              
      320 +---                                                           
      321 +                                                              
      322  ## Dependências e ordem
      323  
      324  - **Fundação primeiro:** T-001..T-004. T-001–T-004 são `[P]` e
           ntre si (arquivos distintos).
● Now update the Dependências, Paralelização, and Cobertura sections for the new
  phases:

● Update(tasks.md)
  ⎿  Added 12 lines
      331    T-023 e T-024 são `[P]` (independentes).
      332  - **Fase 5 (D-004):** T-025 altera `agrega_categoria()` (revis
           a T-015); T-026 (testes
      333    de regra, `[P]`) e T-027 (golden, revisa T-022) validam T-02
           5 e dependem dele.
      334 +- **Fases 6–10 (D-005/D-006/D-007 + Clarify):**               
      335 +  - **Fase 6** primeiro: T-028 (`modelo.py`) e T-029 (`politic
          +a.py`) são `[P]`; T-030                                       
      336 +    (`io_json.py` carga) depende de T-028+T-029.              
      337 +  - **Fase 7** depende de T-028/029: T-031..T-034 editam `regr
          +as.py` → sequenciais.                                         
      338 +  - **Fase 8** depende da Fase 7: T-035 (normalização/estrutur
          +a) antes de T-036/037                                         
      339 +    (câmbio); T-036 antes de T-037; T-038 (dedup) e T-039 (NF)
          + dependem de T-035.                                           
      340 +  - **Fase 9:** T-040 (`calculo.py`) depende de toda a Fase 7+
          +8; T-041 (serialização) e                                     
      341 +    T-042 (CLI) dependem de T-040; T-043 (`CLAUDE.md`) é `[P]`
          +.                                                             
      342 +  - **Fase 10:** T-044/045 `[P]` (arquivos de teste novos); T-
          +046 depende das Fases 7–8;                                    
      343 +    T-047 `[P]`; T-048 (goldens) depende de T-040..T-042; T-04
          +9 `[P]`.                                                      
      344 +  - **Ordem entre decisões:** D-005/D-006 (Fases 6–7) vêm ante
          +s de D-007 (Fase 8), pois a                                   
      345 +    conversão e a viagem por moeda assentam sobre a política e
          +xterna e o teto por periodicidade.                            
      346  
      347  ## Exemplos de paralelização
      348  

● Update(tasks.md)
  ⎿  Added 3 lines
      350  - Escrita de testes: os `test_rn_0NN` de `tests/test_regras.py
           ` podem ser escritos
      351    em paralelo (TDD) antes das funções de `regras.py`.
      352  - Fechamento: **T-023** e **T-024** em paralelo com T-022.
      353 +- Fases 6–10 — Rodada A: **T-028, T-029** juntos. Rodada B (te
          +stes novos, TDD):                                             
      354 +  **T-044, T-045, T-047** podem ser escritos antes das funções
          +. Fechamento: **T-043,                                        
      355 +  T-049** em paralelo com T-048.                              
      356  
      357  ---
      358  

● Finally, extend the coverage matrix with the spec-1.4 rules (RN-015..RN-020
  and the revised RNs):

● Update(tasks.md)
  ⎿  Added 29 lines
      389  | AMB-011 (recusa sem categoria) | T-008, T-019 | `test_rn_001
           _coworking_invalida` |
      390  | AMB-012 (total_despesas monetário) | T-015 | `test_rn_014_to
           tal_despesas`, `test_invariante_totais` |
      391  | D-004 (total_despesas exclui valor ≤ 0) | T-025, T-026, T-02
           7 | `test_rn_014_exclui_valor_nao_positivo`, golden `transport
           e_urbano` 200,01 |
      392 +                                                              
      393 +### Cobertura spec 1.4 (Fases 6–10 — substitui as linhas acima
          + onde a regra mudou)                                          
      394 +                                                              
      395 +| Regra da spec | Task | Teste |                              
      396 +|---|---|---|                                                 
      397 +| RN-001 (categorias dinâmicas por CC) | T-032 | `test_rn_001_
          +coworking_invalida`, `test_rn_001_representacao_so_comercial` 
          +|                                                             
      398 +| RN-002 (teto "dia", baldes) | T-034 | `test_rn_002_baldes_di
          +a_misto` |                                                    
      399 +| RN-003 (teto "diaria") | T-034 | `test_rn_003_diaria_por_reg
          +istro` |                                                      
      400 +| RN-004 (origem do teto/limite pela política) | T-031, T-034 
          +| `test_rn_015_cc_especifico`, `test_rn_003_diaria_por_registr
          +o` |                                                          
      401 +| RN-006 (NF sobre valor convertido) | T-039 | `test_rn_006_so
          +bre_valor_convertido` |                                       
      402 +| RN-008 (moeda na chave de duplicidade) | T-038 | `test_rn_00
          +8_moeda_diferencia` |                                         
      403 +| RN-009 (viagem por registro/moeda) | T-034, T-035 | `test_rn
          +_009_viagem_por_registro` |                                   
      404 +| RN-012/014 (agrega em valor_base; exclui cambio não id) | T-
          +040 | `test_agrega_exclui_cambio_nao_id` |                    
      405 +| RN-015 (política externa + resolução de CC) | T-031, T-030 |
          + `test_rn_015_fallback_padrao`, `test_rn_015_cc_especifico` | 
      406 +| RN-016 (periodicidade seleciona mecânica) | T-034 | `test_rn
          +_002_baldes_dia_misto`, `test_rn_003_diaria_por_registro` |   
      407 +| RN-017 (categoria com limite ≤ 0) | T-033 | `test_rn_017_lim
          +ite_zero_nao_reembolsavel` |                                  
      408 +| RN-018 (conversão para a base) | T-035, T-037 | `test_rn_018
          +_converte_eur`, `test_rn_018_moeda_normalizada`, `test_rn_018_
          +arredondamento` |                                             
      409 +| RN-019 (taxa por data mais próxima) | T-036 | `test_rn_019_f
          +im_de_semana_mais_proxima`, `test_rn_019_empate_menor_taxa` | 
      410 +| RN-020 (cambio não identificado) | T-037 | `test_rn_020_camb
          +io_nao_identificado` |                                        
      411 +| AMB-013 (CC ausente → padrão) | T-031 | `test_rn_015_fallbac
          +k_padrao` |                                                   
      412 +| AMB-014 (limite ≤ 0: precedência/reporte) | T-033 | `test_rn
          +_017_limite_zero_nao_reembolsavel` |                          
      413 +| AMB-015 (só categorias com despesa, ordem do CC) | T-041 | `
          +test_ordem_categorias_por_politica`, `test_categorias_dinamica
          +s_so_com_despesa` |                                           
      414 +| AMB-016 (viagem por moeda; baldes; saída sem em_viagem) | T-
          +034, T-041 | `test_rn_002_baldes_dia_misto`, `test_saida_sem_e
          +m_viagem` |                                                   
      415 +| AMB-017 (cambio não id: reporte/total; data mais próxima) | 
          +T-036, T-037, T-040 | `test_rn_019_*`, `test_agrega_exclui_cam
          +bio_nao_id` |                                                 
      416 +| AMB-018 (arredondamento da conversão) | T-037 | `test_rn_018
          +_arredondamento` |                                            
      417 +| Clarify (normalização/tipo de `moeda`; abort de câmbio) | T-
          +035, T-030 | `test_rn_018_moeda_normalizada`, `test_rn_013_moe
          +da_numerica_invalida`, `test_cambio_ausente_aborta` |         
      418 +| D-005 (política externa por CC) | T-028..T-034, T-044 | `pyt
          +est tests/test_politica.py` |                                 
      419 +| D-006 (regras de teto agnósticas) | T-032, T-034 | `test_rn_
          +001_*`, `test_rn_002_baldes_dia_misto` |                      
      420 +| D-007 (câmbio + viagem por moeda) | T-035..T-042, T-045, T-0
          +48 | `pytest tests/test_cambio.py`, golden envelope `1228,72` 
          +|                                                             

● Let me verify the new tasks are well-formed and complete:

  Ran 1 shell command (ctrl+o to expand)

● All 22 new tasks (T-028…T-049) are present and well-formed — each has a
  checkbox, ID, [P] where parallelizable, a description with explicit file path,
  and Atende/Aceite/Commit sub-bullets consistent with the file's existing
  style. No .specify/extensions.yml → no post-tasks hooks.

  Tasks concluído — spec 1.4

  Arquivo: specs/001-motor-reembolso/tasks.md

  Contexto: o tasks.md já registrava T-001…T-027 (concluídas, estado do código =
  D-004). Toda a evolução D-005 (política externa), D-006 (regras agnósticas) e
  D-007 (câmbio + viagem por moeda) — mais os esclarecimentos de 2026-07-31 —
  estava sem tasks e sem código. Seguindo a convenção do arquivo (anexar fases,
  continuar a numeração, não renumerar), acrescentei Fases 6–10 (T-028…T-049).

  Contagem: 22 tasks novas (total no arquivo: 49). 7 paralelizáveis [P].

  Distribuição por fase (não há histórias P1/P2/P3 — motor único e
  determinístico, como o arquivo já registra):

  ┌────────────────────┬─────────────┬──────────────────────────────────────┐
  │        Fase        │    Tasks    │                 Foco                 │
  ├────────────────────┼─────────────┼──────────────────────────────────────┤
  │ 6 — Fundação       │ T-028…T-030 │ modelo.py, politica.py, carga+abort  │
  │ política/câmbio    │             │ em io_json.py                        │
  ├────────────────────┼─────────────┼──────────────────────────────────────┤
  │ 7 — Categoria e    │ T-031…T-034 │ RN-015/001/017 + teto por            │
  │ teto agnósticos    │             │ periodicidade com baldes             │
  ├────────────────────┼─────────────┼──────────────────────────────────────┤
  │ 8 — Câmbio e gates │ T-035…T-039 │ RN-018/019/020, RN-009 por registro, │
  │  dependentes       │             │  RN-006/008 revisados                │
  ├────────────────────┼─────────────┼──────────────────────────────────────┤
  │ 9 — Pipeline,      │ T-040…T-043 │ pipeline Seção 8, saída sem          │
  │ saída, CLI         │             │ em_viagem, CLI sem --em-viagem       │
  ├────────────────────┼─────────────┼──────────────────────────────────────┤
  │ 10 — Testes e      │             │ test_politica/test_cambio, cobertura │
  │ goldens            │ T-044…T-049 │  RN-001..020, goldens 351,43 e       │
  │                    │             │ 1228,72                              │
  └────────────────────┴─────────────┴──────────────────────────────────────┘

  Oportunidades de paralelismo: Rodada A T-028 + T-029; testes TDD T-044/045/047
  antes das funções; fechamento T-043 + T-049 com T-048.

  Critério de teste independente por fase: cada fase fecha com um comando pytest
  verde declarado no Aceite (ex.: Fase 8 → pytest tests/test_cambio.py; Fase 10
  → os dois goldens batendo 351.43 e 1228.72).

  MVP sugerido: Fases 6→9 (T-028…T-042) já produzem a saída correta da spec 1.4
  para ambos os exemplos; a Fase 10 endurece e prova (cobertura + goldens).

  Também atualizei Dependências/ordem, Paralelização e estendi a matriz de
  Cobertura com RN-015..RN-020, os RNs revisados e AMB-013..018, além de uma
  tabela "Superadas pelas Fases 6–10" mapeando cada task antiga (T-003→T-029,
  T-020→T-042, etc.) à sua substituta.

  Próximo passo sugerido: /speckit-analyze (checagem de consistência
  spec↔plan↔tasks antes de codar) ou /speckit-implement para executar as Fases
  6–10.

✻ Baked for 4m 31s

※ recap: We're evolving the reimbursement engine spec through Spec Kit; spec 1.4 (external policy, currency conversion, per-record travel) is done, and I just regenerated plan, design docs, and tasks (added Fases 6–10, T-028 to T-049). Next: run /speckit-implement or /speckit-analyze.

❯ /speckit-analyze                                                              

● This is a read-only consistency analysis across spec.md (1.4), plan.md (1.4),
  and tasks.md (Fases 1–10). No .specify/extensions.yml → no hooks. The
  constitution is an unfilled template → no constitution gates. I have all three
  artifacts in context, but let me grep for stale values that could have leaked
  across the many edits (highest-signal check).

  Ran 1 shell command (ctrl+o to expand)

● The grep confirms the key facts. Crucially, the 585,43 / 14 regras /
  --em-viagem hits inside tasks.md are all in the completed [x] T-001…T-027 
  history (the file's convention preserves prior work verbatim, with ⚠️ revision
  notes and a "Superadas" map) — those are intentional record, not drift. The
  live issues are elsewhere. Here's the analysis.

  Specification Analysis Report

  Scope: spec.md (v1.4), plan.md (v1.4), tasks.md (Fases 1–10). Constitution =
  unfilled template (no enforceable principles). No .specify/extensions.yml.

  ID: M1
  Category: Coverage / Inconsistency
  Severity: MEDIUM
  Location(s): tasks.md T-047 vs T-046; test_cobertura_rn.py (def 
  test_rn_(\d{3}))
  Summary: The RN-coverage audit matches tests by literal name test_rn_NNN.
  Several RNs have no test_rn_NNN-named test in the Fase 7–10 Aceites: RN-004,
  RN-005, RN-007, RN-010, RN-012, RN-014, RN-016 are mapped to tests named
  after other RNs (e.g. RN-004 → test_rn_015_cc_especifico; RN-016 →
  test_rn_002…). T-046's rewrite could also drop the surviving
  test_rn_005/007/010/012/014. → T-047 audit would fail.
  Recommendation: In T-046, explicitly require ≥1
  test_rn_004/005/007/010/012/014/016_* test; or note in T-047 that the audit
  maps via the coverage matrix, not raw names.
  ────────────────────────────────────────
  ID: M2
  Category: Inconsistency (project doc)
  Severity: MEDIUM
  Location(s): CLAUDE.md:38-39 and CLAUDE.md "Fora de escopo" ("Sem conversão de

  moeda")
  Summary: CLAUDE.md (read every session) still documents [--em-viagem] and
  declares currency conversion out of scope — both contradict spec 1.4. T-043
  fixes only the command line, not the scope note.
  Recommendation: Extend T-043 to also correct the "Fora de escopo" bullet
  (câmbio now in scope) and the runtime command.
  ────────────────────────────────────────
  ID: L1
  Category: Traceability
  Severity: LOW
  Location(s): tasks.md T-022/T-027 ([x])
  Summary: Completed tasks cite golden 585,43 and --em-viagem; correct as
  history
  but potentially confusing.
  Recommendation: Already mitigated by the "Superadas pelas Fases 6–10" table →
  T-048; no change needed.
  ────────────────────────────────────────
  ID: L2
  Category: Underspecification (verify)
  Severity: LOW
  Location(s): plan.md §6; quickstart.md; tasks.md T-048
  Summary: Envelope golden 1228,72 is a computed oracle (spec deferred it). It's

  self-consistent across the 3 files, but it is the test's source of truth.
  Recommendation: Re-derive during T-048 against the real cambio.json/política
  before locking the golden.
  ────────────────────────────────────────
  ID: L3
  Category: Duplication (style)
  Severity: LOW
  Location(s): spec.md Clarifications
  Summary: Three ### Session 2026-07-31 (…) subheadings (same date,
  parenthetical
  suffixes) deviate slightly from the plain ### Session YYYY-MM-DD convention.
  Recommendation: Cosmetic; optionally merge under one dated heading.
  ────────────────────────────────────────
  ID: L4
  Category: Terminology (intentional)
  Severity: LOW
  Location(s): política data vs spec text
  Summary: nao reembolsavel (unaccented, from observacao data) vs cambio não 
  identificado (accented motivo).
  Recommendation: Intentional — observacao is echoed verbatim from the file. No
  action.

  Coverage Summary (RN-001…RN-020 → tasks): 20/20 rules have ≥1 task = 100%.

  ┌──────────────────────────┬────────┬────────────────┬───────────────────┐
  │       Requirement        │  Has   │    Task IDs    │       Notes       │
  │                          │ Task?  │                │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-001 categorias        │ ✅     │ T-032          │                   │
  │ dinâmicas                │        │                │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-002 teto "dia"/baldes │ ✅     │ T-034          │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-003 teto "diaria"     │ ✅     │ T-034          │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-004 origem do teto    │ ✅     │ T-031, T-034   │ test-name gap     │
  │                          │        │                │ (M1)              │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │                          │        │                │ via min;          │
  │ RN-005 parcial no teto   │ ✅     │ T-034          │ test-name gap     │
  │                          │        │                │ (M1)              │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-006 NF sobre          │ ✅     │ T-039          │                   │
  │ convertido               │        │                │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │                          │        │ T-009          │ test-name gap     │
  │ RN-007 competência       │ ✅     │ (válida),      │ (M1)              │
  │                          │        │ T-040          │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-008 duplicidade +     │ ✅     │ T-038          │                   │
  │ moeda                    │        │                │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-009 viagem por        │ ✅     │ T-034, T-035   │                   │
  │ registro                 │        │                │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │                          │        │ T-010          │ test-name gap     │
  │ RN-010 valor inválido    │ ✅     │ (válida),      │ (M1)              │
  │                          │        │ T-040          │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-011 precisão          │ ✅     │ T-035, T-037   │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-012 agregação         │ ✅     │ T-040          │ test-name gap     │
  │                          │        │                │ (M1)              │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-013 registro inválido │ ✅     │ T-035          │                   │
  │  + moeda                 │        │                │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-014 total_despesas    │ ✅     │ T-040          │ test-name gap     │
  │                          │        │                │ (M1)              │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-015                   │ ✅     │ T-030, T-031   │                   │
  │ política/resolução CC    │        │                │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-016 periodicidade     │ ✅     │ T-034          │ test-name gap     │
  │                          │        │                │ (M1)              │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-017 limite ≤ 0        │ ✅     │ T-033          │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-018 conversão         │ ✅     │ T-035, T-037   │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-019 taxa por data     │ ✅     │ T-036          │                   │
  ├──────────────────────────┼────────┼────────────────┼───────────────────┤
  │ RN-020 cambio não        │ ✅     │ T-037          │                   │
  │ identificado             │        │                │                   │
  └──────────────────────────┴────────┴────────────────┴───────────────────┘

  Constitution Alignment: No violations — .specify/memory/constitution.md is an
  unpopulated template. The effective conventions in CLAUDE.md (pure core; one
  function/one test per RN; Decimal; rules only in spec) are honored by
  plan/tasks — except CLAUDE.md's own stale content (M2).

  Unmapped Tasks: None. All T-028…T-049 trace to an RN or decision
  (D-005/006/007 / Clarify).

  Cross-artifact number consistency (verified): 351.43, 1228.72, RN-001..RN-020,
  pipeline order (spec §8 = plan DT-012 = tasks T-040), category ordering
  (DT-011 = both goldens), em_viagem removal, 7-value Motivo enum — all 
  consistent across spec/plan/tasks/quickstart/contract.

  Metrics:
  - Total requirements (RN): 20 (+ AMB-001…018, D-001…007 supporting)
  - Total tasks: 49 (22 active for spec 1.4: T-028…T-049)
  - Requirement coverage: 100% (≥1 task each)
  - Ambiguity count: 0 (spec heavily clarified through AMB-001…018 + Clarify
  session)
  - Substantive duplication: 0
  - Critical issues: 0

  Next Actions

  No CRITICAL or HIGH issues — you may proceed to /speckit-implement. Two MEDIUM
  items are worth tightening first, both cheap:

  1. M1 — before/while running Fase 10, ensure every RN-001…020 has a
  test_rn_NNN-named test (or relax the audit). Otherwise T-047 fails on
  RN-004/005/007/010/012/014/016.
  2. M2 — fold the "Fora de escopo / Sem conversão de moeda" fix into T-043 (not
  just the command signature).

  Both are tasks.md/CLAUDE.md edits; neither blocks starting implementation, but
  M1 will surface as a red audit test late in Fase 10 if ignored.

  ---
  Would you like me to suggest concrete remediation edits for M1 and M2 (e.g.,
  revised wording for T-046/T-047 and T-043)? I won't apply anything without
  your go-ahead.

✻ Sautéed for 3m 7s

❯ Suggest me concrete recomendation for m1 and m2                               

● Here are concrete, drop-in edits for both. I'm showing the exact replacement
  text — say the word and I'll apply them.

  M1 — guarantee a test_rn_NNN for every rule (so T-047's audit passes)

  The audit (test_cobertura_rn.py) matches def test_rn_(\d{3}) literally, so
  each of RN-004/005/007/010/012/014/016 needs a test whose name carries its own
  number. Fix it in the two tasks that own the test suite.

  T-046 — replace the description + Aceite with:

  - [ ] **T-046** — Reescrever `tests/test_regras.py` e `tests/test_bordas.py`
  para a spec 1.4: **remover** testes de `--em-viagem`/categorias
  fixas/`tetos_efetivos`; cobrir RN-002 baldes, RN-003 diaria, RN-009 por
  registro, RN-017, RN-006 sobre convertido; e as novas linhas da Seção 7
  (moeda=base, sem moeda, dia misto, fim de semana, empate, cambio não
  identificado, NF pós-conversão). **Garantir que toda RN-001..RN-020 tenha ao 
  menos um teste cujo nome contenha o próprio número** (`def test_rn_NNN_*`) —
  em especial criar/preservar `test_rn_004_*` (origem do teto/limite pela
  política), `test_rn_005_*` (parcial no teto), `test_rn_007_*` (competência),
  `test_rn_010_*` (valor inválido), `test_rn_012_*` (agregação), `test_rn_014_*`
  (total_despesas exclui ≤0 e cambio não id) e `test_rn_016_*` (periodicidade),
  que não têm task dedicada nas Fases 7–8. Supera T-017.
    - **Atende:** RN-001..RN-020 (bordas), Seção 7
    - **Aceite:** `pytest tests/test_regras.py tests/test_bordas.py` verde **e**
  `pytest tests/test_cobertura_rn.py` passa (todo `test_rn_NNN` de 001 a 020 
  existe)
    - **Commit:** `test(T-046): testes de regra e bordas para spec 1.4`

  T-047 — replace the description with (make the naming contract explicit):

  - [ ] **T-047** [P] — Atualizar `tests/test_cobertura_rn.py`: auditar
  **RN-001..RN-020** (não mais RN-001..RN-014). A auditoria exige um `def
  test_rn_NNN_*` para **cada** número de 001 a 020 (convenção de nome literal);
  um teste nomeado por outra RN **não** conta pela regra que cobre. Supera
  T-023.
    - **Atende:** rastreabilidade (CLAUDE.md)
    - **Aceite:** `pytest tests/test_cobertura_rn.py` falha se faltar
  `test_rn_NNN` de qualquer RN até RN-020
    - **Commit:** `test(T-047): cobertura ate RN-020`

  Coverage matrix — add the three rows that only had superseded entries (insert
  into the "Cobertura spec 1.4" table, after the RN-004 row):

  | RN-005 (parcial no teto) | T-034 | `test_rn_005_parcial_no_teto` |
  | RN-007 (competência) | T-009, T-040 | `test_rn_007_fora`,
  `test_rn_007_limite_inclusivo` |
  | RN-010 (valor inválido) | T-010, T-040 | `test_rn_010_negativo` |

  M2 — extend T-043 to also fix CLAUDE.md's stale scope note

  CLAUDE.md is wrong in two places, not one: the runtime command ([--em-viagem])
  and "Fora de escopo → Sem conversão de moeda (tudo em BRL)". T-043 currently
  only mentions the command.

  T-043 — replace the description + Aceite with:

  - [ ] **T-043** [P] — Atualizar `CLAUDE.md` em **dois** pontos: (a) seção
  "Stack e comandos" — assinatura `calcular --input ... --output ... [--politica
  ...] [--cambio ...]` (sem `--em-viagem`), citando `politica-v4.json`
  (categorias/limites/limiar/viagem) e `cambio.json`; (b) seção "Fora de escopo"
  — **remover** "Sem conversão de moeda (tudo em BRL)" (câmbio agora está em
  escopo via RN-018..RN-020) e ajustar para "Sem regra de calendário (dia
  útil/feriado só afeta a data da taxa de câmbio)". Supera T-024.
    - **Atende:** DT-003b, documentação; consistência com spec 1.4
    - **Aceite:** `CLAUDE.md` não menciona `--em-viagem` nem "Sem conversão de
  moeda"; cita as duas fontes externas e câmbio em escopo
    - **Commit:** `docs(tasks): atualiza comando e escopo de cambio no
  CLAUDE.md`

  ---
  These are all tasks.md edits except that T-043 describes a future CLAUDE.md
  change (the actual CLAUDE.md edit happens when T-043 runs during
  /speckit-implement). None touches spec or plan — the consistency is already
  sound there.

  Want me to apply the four tasks.md edits now (M1: T-046, T-047, matrix rows;
  M2: T-043)?

✻ Crunched for 36s

❯ yes, apply the edits                                                          

● I'll apply the four edits to tasks.md.

● Update(tasks.md)
  ⎿  Added 2 lines, removed 2 lines
      293    - **Aceite:** `pytest tests/test_cambio.py` verde
      294    - **Commit:** `test(T-045): testes de cambio (RN-018/019/020
           )`
      295  
      296 -- [ ] **T-046** — Reescrever `tests/test_regras.py` e `tests/t
          -est_bordas.py` para a spec 1.4: **remover** testes de `--em-vi
          -agem`/categorias fixas/`tetos_efetivos`; cobrir RN-002 baldes,
          - RN-003 diaria, RN-009 por registro, RN-017, RN-006 sobre conv
          -ertido; e as novas linhas da Seção 7 (moeda=base, sem moeda, d
          -ia misto, fim de semana, empate, cambio não identificado, NF p
          -ós-conversão). Supera T-017.                                  
      296 +- [ ] **T-046** — Reescrever `tests/test_regras.py` e `tests/t
          +est_bordas.py` para a spec 1.4: **remover** testes de `--em-vi
          +agem`/categorias fixas/`tetos_efetivos`; cobrir RN-002 baldes,
          + RN-003 diaria, RN-009 por registro, RN-017, RN-006 sobre conv
          +ertido; e as novas linhas da Seção 7 (moeda=base, sem moeda, d
          +ia misto, fim de semana, empate, cambio não identificado, NF p
          +ós-conversão). **Garantir que toda RN-001..RN-020 tenha ao men
          +os um teste cujo nome contenha o próprio número** (`def test_r
          +n_NNN_*`) — em especial criar/preservar `test_rn_004_*` (orige
          +m do teto/limite pela política), `test_rn_005_*` (parcial no t
          +eto), `test_rn_007_*` (competência), `test_rn_010_*` (valor in
          +válido), `test_rn_012_*` (agregação), `test_rn_014_*` (total_d
          +espesas exclui ≤0 e cambio não id) e `test_rn_016_*` (periodic
          +idade), que não têm task dedicada nas Fases 7–8. Supera T-017.
      297    - **Atende:** RN-001..RN-020 (bordas), Seção 7
      298 -  - **Aceite:** `pytest tests/test_regras.py tests/test_bordas
          -.py` verde                                                    
      298 +  - **Aceite:** `pytest tests/test_regras.py tests/test_bordas
          +.py` verde **e** `pytest tests/test_cobertura_rn.py` passa (to
          +do `test_rn_NNN` de 001 a 020 existe)                         
      299    - **Commit:** `test(T-046): testes de regra e bordas para sp
           ec 1.4`
      300  
      301  - [ ] **T-047** [P] — Atualizar `tests/test_cobertura_rn.py`: 
           auditar **RN-001..RN-020** (não mais RN-001..RN-014). Supera T
           -023.

● Update(tasks.md)
  ⎿  Added 2 lines, removed 2 lines
      298    - **Aceite:** `pytest tests/test_regras.py tests/test_bordas
           .py` verde **e** `pytest tests/test_cobertura_rn.py` passa (to
           do `test_rn_NNN` de 001 a 020 existe)
      299    - **Commit:** `test(T-046): testes de regra e bordas para sp
           ec 1.4`
      300  
      301 -- [ ] **T-047** [P] — Atualizar `tests/test_cobertura_rn.py`: 
          -auditar **RN-001..RN-020** (não mais RN-001..RN-014). Supera T
          --023.                                                         
      301 +- [ ] **T-047** [P] — Atualizar `tests/test_cobertura_rn.py`: 
          +auditar **RN-001..RN-020** (não mais RN-001..RN-014). A audito
          +ria exige um `def test_rn_NNN_*` para **cada** número de 001 a
          + 020 (convenção de nome literal); um teste nomeado por outra R
          +N **não** conta pela regra que cobre. Supera T-023.           
      302    - **Atende:** rastreabilidade (CLAUDE.md)
      303 -  - **Aceite:** `pytest tests/test_cobertura_rn.py` falha se f
          -altar teste de qualquer RN até RN-020                         
      303 +  - **Aceite:** `pytest tests/test_cobertura_rn.py` falha se f
          +altar `test_rn_NNN` de qualquer RN até RN-020                 
      304    - **Commit:** `test(T-047): cobertura ate RN-020`
      305  
      306  - [ ] **T-048** — Goldens em `tests/test_integracao.py`: (a) `
           exemplos/despesas-exemplo.json` (`CC-ENG-PLATAFORMA`) → `total
           _reembolso_geral == 351.43`, **sem** `em_viagem`, `hospedagem`
            não reembolsável (0,00), `alimentacao` 402.83/306.93/271.43, 
           `transporte_urbano` 200.01/100.00/80.00; (b) `exemplos/despesa
           s-envelope.json` (`CC-COMERCIAL`) → `total_reembolso_geral == 
           1228.72` com os totais do `quickstart.md`. Supera T-022/027.

● Update(tasks.md)
  ⎿  Added 4 lines, removed 1 line
      397  | RN-001 (categorias dinâmicas por CC) | T-032 | `test_rn_001_
           coworking_invalida`, `test_rn_001_representacao_so_comercial` 
           |
      398  | RN-002 (teto "dia", baldes) | T-034 | `test_rn_002_baldes_di
           a_misto` |
      399  | RN-003 (teto "diaria") | T-034 | `test_rn_003_diaria_por_reg
           istro` |
      400 -| RN-004 (origem do teto/limite pela política) | T-031, T-034 
          -| `test_rn_015_cc_especifico`, `test_rn_003_diaria_por_registr
          -o` |                                                          
      400 +| RN-004 (origem do teto/limite pela política) | T-031, T-034 
          +| `test_rn_004_limite_pela_politica` |                        
      401 +| RN-005 (parcial no teto) | T-034 | `test_rn_005_parcial_no_t
          +eto` |                                                        
      402  | RN-006 (NF sobre valor convertido) | T-039 | `test_rn_006_so
           bre_valor_convertido` |
      403 +| RN-007 (competência) | T-009, T-040 | `test_rn_007_fora`, `t
          +est_rn_007_limite_inclusivo` |                                
      404 +| RN-010 (valor inválido) | T-010, T-040 | `test_rn_010_negati
          +vo` |                                                         
      405  | RN-008 (moeda na chave de duplicidade) | T-038 | `test_rn_00
           8_moeda_diferencia` |
      406  | RN-009 (viagem por registro/moeda) | T-034, T-035 | `test_rn
           _009_viagem_por_registro` |
      407  | RN-012/014 (agrega em valor_base; exclui cambio não id) | T-
           040 | `test_agrega_exclui_cambio_nao_id` |

● Update(tasks.md)
  ⎿  Added 1 line, removed 1 line
      406  | RN-009 (viagem por registro/moeda) | T-034, T-035 | `test_rn
           _009_viagem_por_registro` |
      407  | RN-012/014 (agrega em valor_base; exclui cambio não id) | T-
           040 | `test_agrega_exclui_cambio_nao_id` |
      408  | RN-015 (política externa + resolução de CC) | T-031, T-030 |
            `test_rn_015_fallback_padrao`, `test_rn_015_cc_especifico` |
      409 -| RN-016 (periodicidade seleciona mecânica) | T-034 | `test_rn
          -_002_baldes_dia_misto`, `test_rn_003_diaria_por_registro` |   
      409 +| RN-016 (periodicidade seleciona mecânica) | T-034 | `test_rn
          +_016_seleciona_mecanica` |                                    
      410  | RN-017 (categoria com limite ≤ 0) | T-033 | `test_rn_017_lim
           ite_zero_nao_reembolsavel` |
      411  | RN-018 (conversão para a base) | T-035, T-037 | `test_rn_018
           _converte_eur`, `test_rn_018_moeda_normalizada`, `test_rn_018_
           arredondamento` |
      412  | RN-019 (taxa por data mais próxima) | T-036 | `test_rn_019_f
           im_de_semana_mais_proxima`, `test_rn_019_empate_menor_taxa` |

● Update(tasks.md)
  ⎿  Added 4 lines, removed 4 lines
      276    - **Aceite:** `tests/test_cli.py::test_cli_sem_em_viagem`, `
           ::test_cli_cambio_ausente_exit1`, `::test_cli_defaults_empacot
           ados`
      277    - **Commit:** `feat(T-042): CLI com --politica/--cambio, sem
            --em-viagem`
      278  
      279 -- [ ] **T-043** [P] — Atualizar `CLAUDE.md`: assinatura `calcu
          -lar --input ... --output ... [--politica ...] [--cambio ...]` 
          -(sem `--em-viagem`); nota de que categorias/limites/limiar/via
          -gem vêm de `politica-v4.json` e o câmbio de `cambio.json`. Sup
          -era T-024.                                                    
      280 -  - **Atende:** DT-003b, documentação                         
      281 -  - **Aceite:** `CLAUDE.md` não menciona `--em-viagem`; cita a
          -s duas fontes externas                                        
      282 -  - **Commit:** `docs(tasks): atualiza comando da CLI no CLAUD
          -E.md`                                                         
      279 +- [ ] **T-043** [P] — Atualizar `CLAUDE.md` em **dois** pontos
          +: (a) seção "Stack e comandos" — assinatura `calcular --input 
          +... --output ... [--politica ...] [--cambio ...]` (sem `--em-v
          +iagem`), citando `politica-v4.json` (categorias/limites/limiar
          +/viagem) e `cambio.json`; (b) seção "Fora de escopo" — **remov
          +er** "Sem conversão de moeda (tudo em BRL)" (câmbio agora está
          + em escopo via RN-018..RN-020) e ajustar para "Sem regra de ca
          +lendário (dia útil/feriado só afeta a data da taxa de câmbio)"
          +. Supera T-024.                                               
      280 +  - **Atende:** DT-003b, documentação; consistência com spec 1
          +.4                                                            
      281 +  - **Aceite:** `CLAUDE.md` não menciona `--em-viagem` nem "Se
          +m conversão de moeda"; cita as duas fontes externas e câmbio e
          +m escopo                                                      
      282 +  - **Commit:** `docs(tasks): atualiza comando e escopo de cam
          +bio no CLAUDE.md`                                             
      283  
      284  ## Fase 10 — Testes, goldens e cobertura
      285  

● All edits applied. Let me verify consistency of the new test names between
  T-046 and the coverage matrix:
  Ran 1 shell command (ctrl+o to expand)

● One loose end: the combined RN-012/014 matrix row still cites
  test_agrega_exclui_cambio_nao_id, but T-046 now mandates
  test_rn_012_*/test_rn_014_*. Let me align it:

● Update(tasks.md)
  ⎿  Added 2 lines, removed 1 line
      404  | RN-010 (valor inválido) | T-010, T-040 | `test_rn_010_negati
           vo` |
      405  | RN-008 (moeda na chave de duplicidade) | T-038 | `test_rn_00
           8_moeda_diferencia` |
      406  | RN-009 (viagem por registro/moeda) | T-034, T-035 | `test_rn
           _009_viagem_por_registro` |
      407 -| RN-012/014 (agrega em valor_base; exclui cambio não id) | T-
          -040 | `test_agrega_exclui_cambio_nao_id` |                    
      407 +| RN-012 (agregação em valor_base) | T-040 | `test_rn_012_agre
          +ga_valor_base` |                                              
      408 +| RN-014 (total_despesas exclui ≤0 e cambio não id) | T-040 | 
          +`test_rn_014_exclui_cambio_nao_id` |                          
      409  | RN-015 (política externa + resolução de CC) | T-031, T-030 |
            `test_rn_015_fallback_padrao`, `test_rn_015_cc_especifico` |
      410  | RN-016 (periodicidade seleciona mecânica) | T-034 | `test_rn
           _016_seleciona_mecanica` |
      411  | RN-017 (categoria com limite ≤ 0) | T-033 | `test_rn_017_lim
           ite_zero_nao_reembolsavel` |

● Done. All remediation edits are applied and internally consistent.

  Applied — M1 & M2 remediation (tasks.md only)

  M1 — RN-coverage audit will now pass:
  - T-046 now explicitly requires a test_rn_NNN_* for every RN-001…020, naming
  the seven that had no dedicated Fase 7–8 task
  (RN-004/005/007/010/012/014/016); its Aceite adds pytest 
  tests/test_cobertura_rn.py passing.
  - T-047 spells out the naming contract (a test named after a different RN
  doesn't count).
  - Coverage matrix gained per-RN rows with self-numbered test names:
  test_rn_004_limite_pela_politica, test_rn_005_parcial_no_teto, test_rn_007_*,
  test_rn_010_negativo, test_rn_012_agrega_valor_base,
  test_rn_014_exclui_cambio_nao_id, test_rn_016_seleciona_mecanica (replacing
  the cross-named references that would have slipped past the audit).

  M2 — CLAUDE.md staleness fully scoped:
  - T-043 now fixes CLAUDE.md in two places — the runtime command (drop
  --em-viagem, add --politica/--cambio) and the "Fora de escopo" bullet ("Sem
  conversão de moeda" is now false); its Aceite checks both.

  Verification: the seven self-numbered test names are present and consistent
  between T-046's mandate and the coverage matrix; T-043 covers both CLAUDE.md
  sections. No spec or plan changes were needed — those were already consistent.

  Both MEDIUM findings are closed. With no CRITICAL/HIGH items remaining, the
  artifacts are ready — next step: /speckit-implement to execute Fases 6–10
  (T-028…T-049). Note that T-043's actual CLAUDE.md edit happens during
  implementation, not now.

✻ Worked for 1m 7s