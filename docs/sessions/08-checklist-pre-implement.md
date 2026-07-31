 ▐▛███▜▌   Claude Code v2.1.220
▝▜█████▛▘  Opus 4.8 · Claude Pro
  ▘▘ ▝▝    ~\Área de Trabalho\Teste SDD\sdd-desafio


❯ /speckit-checklist                                                            

● I'll start by running the setup script and checking for extension hooks.

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● No extension hooks. Let me load the feature context.

  Read 3 files (ctrl+o to expand)

● Let me read the rest of the spec.

  Read 1 file (ctrl+o to expand)

● This is a mature, detailed spec (v1.4) — recently extended with câmbio
  (currency conversion, RN-018..RN-020) and centro-de-custo/política-externa
  rules. Before generating the checklist, let me confirm scope and depth so the
  items are useful.

● User answered Claude's questions:
  ⎿  · Qual área da spec o checklist deve validar (qualidade dos requisitos, não
     a implementação)? → Câmbio e viagem por moeda, Política externa e centro 
     de custo, Spec inteira (RN-001..RN-020), Saída e total_despesas
     · Qual o nível de rigor pretendido para este checklist? → Gate formal de 
     release
     · Quem vai usar este checklist e quando? → Autor revisando a própria spec

● Understood — comprehensive checklist covering the whole spec as a formal 
  release gate, for you (the author) validating your own spec before
  implementation. Given the four focus areas selected, I'll organize by
  requirement-quality dimension and cover câmbio/viagem,
  política/centro-de-custo, saída/totais, and the cross-cutting rules.

● Write(specs\001-motor-reembolso\checklists\spec-gate.md)
  ⎿  Wrote 84 lines to specs\001-motor-reembolso\checklists\spec-gate.md
      1 # Spec Quality Checklist: Motor de Cálculo de Reembolso
      3 **Purpose**: Gate formal de release — validar a *qualidade dos re
        quisitos* (completude, clareza, consistência, mensurabilidade, co
        bertura) da spec antes de implementar. Testa o que está **escrito
      4 **Created**: 2026-07-31
      5 **Feature**: [spec.md](../spec.md) (v1.4)
      7 
      8 > Cada item pergunta se o requisito está bem escrito, não se o si
        stema funciona.
        a inline quando não.
     … +187 lines (ctrl+o to expand)

● No extension hooks configured (.specify/extensions.yml absent), so nothing to
  run post-generation.

  Checklist gerado

  Arquivo: specs/001-motor-reembolso/checklists/spec-gate.md (novo)
  Itens: 42 (CHK001–CHK042)
  Rastreabilidade: todos os itens referenciam seção da spec, RN/AMB, ou marcador
  [Gap]/[Ambiguity]/[Conflict]/[Assumption] (>80%).

  Parâmetros aplicados:
  - Foco: as quatro áreas selecionadas — câmbio/viagem por moeda, política
  externa/centro de custo, spec inteira (RN-001..RN-020), e
  saída/total_despesas.
  - Profundidade: gate formal de release (cobertura ampla, incluindo
  ambiguidades, conflitos e itens em aberto).
  - Público: autor revisando a própria spec.

  Organização por dimensão de qualidade de requisito:
  - Completeness (7) · Clarity (7) · Consistency (7) · Acceptance
  Criteria/Measurabilidade (4) · Scenario Coverage (6) · Edge Case Coverage (4)
  · Non-Functional (2) · Dependencies & Assumptions (2) · Ambiguities &
  Conflicts (3)

  Cada item testa se o requisito está bem escrito (completo, claro, consistente,
  mensurável), não se o sistema funciona. Pontos de maior risco cobertos:
  resolução de taxa por data e empates (CHK010/CHK030/CHK036), baldes separados
  em dia misto (CHK014/CHK027), exclusão de não-valoráveis de total_despesas
  (CHK019/CHK020), distinção abortar-vs-recusar (CHK003/CHK038), e resquícios do
  antigo em_viagem de topo (CHK018/CHK041).

  Quer que eu execute o checklist agora — isto é, avalie a spec item a item e
  marque o que já está adequado e o que tem lacuna? Ou prefere revisar/ajustar o
  escopo primeiro?

✻ Cooked for 1m 57s

❯ Execute o checklist                                                           

● I have the full spec loaded. I'll evaluate each of the 42 items against what
  the spec actually says, mark the results in the file, and annotate the gaps I
  found.

  Read 1 file (ctrl+o to expand)

● Confirmed the cross-artifact issue. Now I'll write the executed checklist with
  results and annotations.

● Write(specs\001-motor-reembolso\checklists\spec-gate.md)
  ⎿  Added 61 lines, removed 43 lines
        2  
        3  **Purpose**: Gate formal de release — validar a *qualidade dos
            requisitos* (completude, clareza, consistência, mensurabilida
           de, cobertura) da spec antes de implementar. Testa o que está 
           **escrito** na spec, não o comportamento do código.
        4  **Created**: 2026-07-31
        5 +**Executed**: 2026-07-31 (contra spec.md v1.4)                
        6  **Feature**: [spec.md](../spec.md) (v1.4)
        7  **Audience**: Autor revisando a própria spec
        8  
        9  > Cada item pergunta se o requisito está bem escrito, não se o
            sistema funciona.
        9 -> Marque `[x]` quando o requisito estiver adequado; anote a la
          -cuna inline quando não.                                       
       10 +> `[x]` = requisito adequado · `[ ]` = lacuna aberta (ver nota
          + inline).                                                     
       11  
       12 +## Resultado da execução                                      
       13 +                                                              
       14 +**39/42 adequados.** A spec está madura e internamente muito c
          +onsistente. Achados:                                          
       15 +                                                              
       16 +- **1 lacuna aberta na spec** (CHK001): obrigatoriedade dos ca
          +mpos de política não formalizada.                             
       17 +- **2 observações menores** (CHK016, CHK033): requisito corret
          +o, mas com precedência implícita / exemplo de borda ausente.  
       18 +- **1 conflito cross-artifact fora da spec** (CHK041): `CLAUDE
          +.md` está desatualizado e contradiz as regras de câmbio/viagem
          + — **corrigir antes de implementar**.                         
       19 +                                                              
       20 +---                                                           
       21 +                                                              
       22  ## Requirement Completeness
       23  
       13 -- [ ] CHK001 - A estrutura completa de `politica-v4.json` está
          - especificada, incluindo quais campos de categoria (`limite`, 
          -`periodicidade`, `observacao`) são obrigatórios e quais opcion
          -ais? [Completeness, Spec §4]                                  
       14 -- [ ] CHK002 - A estrutura completa de `cambio.json` está espe
          -cificada (chave `moeda_base` e mapa `taxas.<data>.<moeda>`), i
          -ncluindo o tipo do fator de taxa? [Completeness, Spec §4]     
       15 -- [ ] CHK003 - Todas as condições que **abortam** a execução e
          -stão enumeradas de forma exaustiva (JSON de topo inparseável, 
          -`cambio.json` ausente/inparseável) e distintas das recusas por
          - registro? [Completeness, Spec §5 RN-013/RN-018, §8]          
       16 -- [ ] CHK004 - Todos os motivos de recusa possíveis estão enum
          -erados em um único ponto autoritativo, e a lista casa com os m
          -otivos citados nas RNs individuais? [Completeness, Spec §9]   
       17 -- [ ] CHK005 - Os parâmetros globais da política (`nota_fiscal
          -_obrigatoria_acima_de`, `acrescimo_em_viagem_percentual`) têm 
          -origem, unidade e aplicabilidade (valem para qualquer centro) 
          -documentadas? [Completeness, Spec §4, RN-015]                 
       18 -- [ ] CHK006 - O comportamento de cada campo de saída está def
          -inido, incluindo quando um bloco de categoria é ou não emitido
          - e o conteúdo de `reprovadas_sem_categoria`? [Completeness, Sp
          -ec §4, RN-012, AMB-015]                                       
       19 -- [ ] CHK007 - O requisito de eco dos campos de identificação 
          -do input na saída (`colaborador.id/nome/centro_custo`, `compet
          -encia`, `periodo`) está especificado por completo? [Completene
          -ss, Spec §4, RN-012]                                          
       24 +- [ ] CHK001 - A estrutura completa de `politica-v4.json` está
          + especificada, incluindo quais campos de categoria (`limite`, 
          +`periodicidade`, `observacao`) são obrigatórios e quais opcion
          +ais? [Completeness, Spec §4] — **LACUNA (menor):** §4 marca só
          + `observacao` como opcional; a obrigatoriedade de `limite`/`pe
          +riodicidade` não é declarada. Mitigado por §10 ("assume políti
          +ca bem formada"), mas para um gate formal vale explicitar quai
          +s campos são obrigatórios ou remeter explicitamente a §10.    
       25 +- [x] CHK002 - A estrutura completa de `cambio.json` está espe
          +cificada (chave `moeda_base` e mapa `taxas.<data>.<moeda>`), i
          +ncluindo o tipo do fator de taxa? [Completeness, Spec §4] — Ta
          +bela de §4 define `moeda_base`, `taxas.<AAAA-MM-DD>` e o fator
          + (numérico, "unidades de `moeda_base` por 1 unidade da moeda")
          + com exemplo.                                                 
       26 +- [x] CHK003 - Todas as condições que **abortam** a execução e
          +stão enumeradas de forma exaustiva (JSON de topo inparseável, 
          +`cambio.json` ausente/inparseável) e distintas das recusas por
          + registro? [Completeness, Spec §5 RN-013/RN-018, §8] — §8 pass
          +os 1–2, RN-013 e RN-018 enumeram e distinguem explicitamente d
          +e RN-020.                                                     
       27 +- [x] CHK004 - Todos os motivos de recusa possíveis estão enum
          +erados em um único ponto autoritativo, e a lista casa com os m
          +otivos citados nas RNs individuais? [Completeness, Spec §9] — 
          +§9 lista os 8 motivos; batem com RN-001/006/007/008/010/013/01
          +7/020.                                                        
       28 +- [x] CHK005 - Os parâmetros globais da política (`nota_fiscal
          +_obrigatoria_acima_de`, `acrescimo_em_viagem_percentual`) têm 
          +origem, unidade e aplicabilidade (valem para qualquer centro) 
          +documentadas? [Completeness, Spec §4, RN-015] — §4 + RN-015 ("
          +valem para qualquer centro"); percentual com exemplo (+50% → ×
          +1,5).                                                         
       29 +- [x] CHK006 - O comportamento de cada campo de saída está def
          +inido, incluindo quando um bloco de categoria é ou não emitido
          + e o conteúdo de `reprovadas_sem_categoria`? [Completeness, Sp
          +ec §4, RN-012, AMB-015] — §4 (tabela + `id`/`categoria_informa
          +da`/`motivo`), RN-012 e AMB-015 (só categorias com ≥1 despesa)
          +.                                                             
       30 +- [x] CHK007 - O requisito de eco dos campos de identificação 
          +do input na saída (`colaborador.id/nome/centro_custo`, `compet
          +encia`, `periodo`) está especificado por completo? [Completene
          +ss, Spec §4, RN-012] — Tabela de saída em §4 e RN-012 cobrem t
          +odos os campos ecoados.                                       
       31  
       32  ## Requirement Clarity
       33  
       23 -- [ ] CHK008 - A normalização de `moeda` e `categoria` (`trim`
          - + caixa alta) está definida de forma única e sem ambiguidade 
          -sobre *quando* ocorre em relação às comparações? [Clarity, Spe
          -c §5 RN-001/RN-018, AMB-003]                                  
       24 -- [ ] CHK009 - A distinção entre "sem moeda" (ausente/`null`/v
          -azio após `trim` → base, não-viagem) e "moeda inválida" (tipo 
          -não-textual → registro inválido) está quantificada por tipo/va
          -lor, sem zona cinzenta? [Clarity, Spec §5 RN-013/RN-018, Clari
          -fications 2026-07-31]                                         
       25 -- [ ] CHK010 - O critério de "data mais próxima" na resolução 
          -de taxa está definido de forma inequívoca (menor diferença abs
          -oluta em dias; empate → menor taxa; só datas que contêm a moed
          -a)? [Clarity, Spec §5 RN-019]                                 
       26 -- [ ] CHK011 - A ordem e o número de arredondamentos na conver
          -são de câmbio estão explícitos (arredonda origem → multiplica 
          -pela taxa cheia → arredonda resultado), sem deixar dúvida sobr
          -e arredondar a taxa? [Clarity, Spec §5 RN-011/RN-018, AMB-018]
       27 -- [ ] CHK012 - O critério de comparação da nota fiscal (estrit
          -amente acima do limiar, sobre o valor **já convertido**) está 
          -inequívoco quanto ao valor exato do limiar? [Clarity, Spec §5 
          -RN-006]                                                       
       28 -- [ ] CHK013 - Os campos de negócio que definem duplicidade es
          -tão listados de forma completa e sem ambiguidade sobre usar `v
          -alor`/`moeda` de origem (antes da conversão)? [Clarity, Spec §
          -5 RN-008]                                                     
       29 -- [ ] CHK014 - A mecânica de "baldes separados" por status de 
          -viagem em dia misto está definida de modo que o resultado seja
          - único e independente de ordenação? [Clarity, Spec §5 RN-002/R
          -N-009, AMB-016]                                               
       34 +- [x] CHK008 - A normalização de `moeda` e `categoria` (`trim`
          + + caixa alta) está definida de forma única e sem ambiguidade 
          +sobre *quando* ocorre em relação às comparações? [Clarity, Spe
          +c §5 RN-001/RN-018, AMB-003] — RN-001, RN-018, AMB-003 e §8 pa
          +sso 3 ("antes de qualquer comparação"); Clarifications 2026-07
          +-31 fecham o "quando".                                        
       35 +- [x] CHK009 - A distinção entre "sem moeda" (ausente/`null`/v
          +azio após `trim` → base, não-viagem) e "moeda inválida" (tipo 
          +não-textual → registro inválido) está quantificada por tipo/va
          +lor, sem zona cinzenta? [Clarity, Spec §5 RN-013/RN-018] — RN-
          +013 + RN-018 + Clarifications 2026-07-31 cobrem os casos por t
          +ipo/valor.                                                    
       36 +- [x] CHK010 - O critério de "data mais próxima" na resolução 
          +de taxa está definido de forma inequívoca (menor diferença abs
          +oluta em dias; empate → menor taxa; só datas que contêm a moed
          +a)? [Clarity, Spec §5 RN-019] — RN-019 define os três aspectos
          + com exemplo e caso de empate.                                
       37 +- [x] CHK011 - A ordem e o número de arredondamentos na conver
          +são de câmbio estão explícitos (arredonda origem → multiplica 
          +pela taxa cheia → arredonda resultado), sem deixar dúvida sobr
          +e arredondar a taxa? [Clarity, Spec §5 RN-011/RN-018, AMB-018]
          + — AMB-018 é explícita: não arredonda a taxa.                 
       38 +- [x] CHK012 - O critério de comparação da nota fiscal (estrit
          +amente acima do limiar, sobre o valor **já convertido**) está 
          +inequívoco quanto ao valor exato do limiar? [Clarity, Spec §5 
          +RN-006] — RN-006: "estritamente acima"; "No valor exato do lim
          +iar não é necessária"; usa valor convertido.                  
       39 +- [x] CHK013 - Os campos de negócio que definem duplicidade es
          +tão listados de forma completa e sem ambiguidade sobre usar `v
          +alor`/`moeda` de origem (antes da conversão)? [Clarity, Spec §
          +5 RN-008] — RN-008 lista os campos e fixa `valor`/`moeda` de o
          +rigem.                                                        
       40 +- [x] CHK014 - A mecânica de "baldes separados" por status de 
          +viagem em dia misto está definida de modo que o resultado seja
          + único e independente de ordenação? [Clarity, Spec §5 RN-002/R
          +N-009, AMB-016] — AMB-016 justifica a independência de ordenaç
          +ão.                                                           
       41  
       42  ## Requirement Consistency
       43  
       33 -- [ ] CHK015 - A definição de `moeda_base` é consistente em to
          -da a spec (sempre a do `cambio.json`; a da política é explicit
          -amente ignorada), sem contradição entre §3, §4 e RN-018? [Cons
          -istency, Spec §3/§4, RN-018]                                  
       34 -- [ ] CHK016 - A ordem de aplicação das regras (§8) é consiste
          -nte com as precedências afirmadas em cada RN/AMB (ex.: limite 
          -≤ 0 antes de duplicata/período/valor/NF; câmbio antes de dedup
          -)? [Consistency, Spec §8, RN-017/RN-020, AMB-010/AMB-014]     
       35 -- [ ] CHK017 - As regras de teto RN-002/RN-003/RN-004 estão co
          -nsistentemente redigidas por **papel/periodicidade**, sem cita
          -r nome de categoria fixa? [Consistency, Spec §5 RN-002/RN-003/
          -RN-004, Clarifications 2026-07-31]                            
       36 -- [ ] CHK018 - A definição de "viagem" é consistente entre RN-
          -009, RN-018 e AMB-016 (por registro, derivada de moeda ≠ base)
          -, sem resquício do antigo `em_viagem` de topo (AMB-008)? [Cons
          -istency, Spec §5 RN-009/RN-018, AMB-008/AMB-016]              
       37 -- [ ] CHK019 - O tratamento de itens não-valoráveis em `total_
          -despesas` é consistente entre valores ≤ 0 e "cambio não identi
          -ficado" (ambos excluídos pelo mesmo princípio)? [Consistency, 
          -Spec §5 RN-014/RN-020, AMB-017]                               
       38 -- [ ] CHK020 - A invariante `total_despesas ≥ total_aceito ≥ t
          -otal_reembolso` é afirmada de forma consistente e compatível c
          -om as exclusões definidas (≤ 0, câmbio não identificado)? [Con
          -sistency, Spec §4, RN-014, AMB-012]                           
       39 -- [ ] CHK021 - O exemplo de saída da §4 é numericamente consis
          -tente com as regras citadas (limites de `CC-ENG-PLATAFORMA`, e
          -xclusão do estorno `d-009`, `total_reembolso_geral = 351,43`)?
          - [Consistency, Spec §4]                                       
       44 +- [x] CHK015 - A definição de `moeda_base` é consistente em to
          +da a spec (sempre a do `cambio.json`; a da política é explicit
          +amente ignorada), sem contradição entre §3, §4 e RN-018? [Cons
          +istency, Spec §3/§4, RN-018] — §3, §4 e RN-018 repetem que a `
          +moeda_base` da política é ignorada.                           
       45 +- [x] CHK016 - A ordem de aplicação das regras (§8) é consiste
          +nte com as precedências afirmadas em cada RN/AMB (ex.: limite 
          +≤ 0 antes de duplicata/período/valor/NF; câmbio antes de dedup
          +)? [Consistency, Spec §8, RN-017/RN-020, AMB-010/AMB-014] — Co
          +nsistente. **Observação:** §8 coloca "limite > 0" (passo 5) an
          +tes da conversão de câmbio (passo 6), logo "nao reembolsavel" 
          +prevalece sobre "cambio não identificado"; RN-020 só lista pre
          +valência sobre duplicata/período/valor/NF. A precedência limit
          +e≤0 × câmbio fica implícita na §8 — considere citá-la em RN-01
          +7 ou RN-020.                                                  
       46 +- [x] CHK017 - As regras de teto RN-002/RN-003/RN-004 estão co
          +nsistentemente redigidas por **papel/periodicidade**, sem cita
          +r nome de categoria fixa? [Consistency, Spec §5 RN-002/RN-003/
          +RN-004] — Nomes de categoria aparecem só como exemplo parentét
          +ico da política vigente; a regra afirma explicitamente não con
          +hecer categoria.                                              
       47 +- [x] CHK018 - A definição de "viagem" é consistente entre RN-
          +009, RN-018 e AMB-016 (por registro, derivada de moeda ≠ base)
          +, sem resquício do antigo `em_viagem` de topo (AMB-008)? [Cons
          +istency, Spec §5 RN-009/RN-018, AMB-008/AMB-016] — Dentro da s
          +pec, coerente: §4 remove o campo, RN-009 nega o indicador anti
          +go, AMB-008 marcada "Substituída por AMB-016". (Resíduo fora d
          +a spec: ver CHK041.)                                          
       48 +- [x] CHK019 - O tratamento de itens não-valoráveis em `total_
          +despesas` é consistente entre valores ≤ 0 e "cambio não identi
          +ficado" (ambos excluídos pelo mesmo princípio)? [Consistency, 
          +Spec §5 RN-014/RN-020, AMB-017] — RN-020/AMB-017 invocam "o me
          +smo princípio de não-valorável usado para valores ≤ 0".       
       49 +- [x] CHK020 - A invariante `total_despesas ≥ total_aceito ≥ t
          +otal_reembolso` é afirmada de forma consistente e compatível c
          +om as exclusões definidas (≤ 0, câmbio não identificado)? [Con
          +sistency, Spec §4, RN-014, AMB-012] — Afirmada em §4, RN-014 e
          + AMB-012; as exclusões preservam a invariante.                
       50 +- [x] CHK021 - O exemplo de saída da §4 é numericamente consis
          +tente com as regras citadas (limites de `CC-ENG-PLATAFORMA`, e
          +xclusão do estorno `d-009`, `total_reembolso_geral = 351,43`)?
          + [Consistency, Spec §4] — Confere: 271,43 + 80,00 + 0,00 = 351
          +,43; `transporte_urbano` 100,00 + 100,01 = 200,01 sem o estorn
          +o −45,00.                                                     
       51  
       52  ## Acceptance Criteria Quality (Measurabilidade)
       53  
       43 -- [ ] CHK022 - Cada critério de aceite (§9) é objetivamente ve
          -rificável com números ou entradas concretas, e não com termos 
          -vagos? [Measurability, Spec §9]                               
       44 -- [ ] CHK023 - O requisito "nenhuma categoria é conhecida/priv
          -ilegiada pelo sistema" é enunciado de forma testável (mudar po
          -lítica muda resultado sem mudar código)? [Measurability, Spec 
          -§9, RN-004/RN-015/RN-016]                                     
       45 -- [ ] CHK024 - O critério de cobertura de testes (cada RN-001.
          -.RN-020 com ao menos um teste com números) é mensurável e rast
          -reável a IDs de regra? [Measurability, Traceability, Spec §9] 
       46 -- [ ] CHK025 - Os casos de borda da §7 trazem entrada e result
          -ado esperado concretos suficientes para servir de critério de 
          -verificação? [Measurability, Spec §7]                         
       54 +- [x] CHK022 - Cada critério de aceite (§9) é objetivamente ve
          +rificável com números ou entradas concretas, e não com termos 
          +vagos? [Measurability, Spec §9] — Os critérios trazem números/
          +entradas concretas ou condições binárias verificáveis.        
       55 +- [x] CHK023 - O requisito "nenhuma categoria é conhecida/priv
          +ilegiada pelo sistema" é enunciado de forma testável (mudar po
          +lítica muda resultado sem mudar código)? [Measurability, Spec 
          +§9, RN-004/RN-015/RN-016] — §9 enuncia adicionar/remover/alter
          +ar categoria "sem alterar regra ou código".                   
       56 +- [x] CHK024 - O critério de cobertura de testes (cada RN-001.
          +.RN-020 com ao menos um teste com números) é mensurável e rast
          +reável a IDs de regra? [Measurability, Traceability, Spec §9] 
          +— §9 exige um teste com números por RN; rastreável por ID (ref
          +orçado pelo teste de auditoria em CLAUDE.md).                 
       57 +- [x] CHK025 - Os casos de borda da §7 trazem entrada e result
          +ado esperado concretos suficientes para servir de critério de 
          +verificação? [Measurability, Spec §7] — Cada linha traz entrad
          +a-exemplo, comportamento esperado e regra.                    
       58  
       59  ## Scenario Coverage
       60  
       50 -- [ ] CHK026 - Existe requisito para o cenário de fallback de 
          -centro de custo desconhecido (`padrao`), com os limites result
          -antes especificados? [Coverage, Spec §5 RN-015, AMB-013]      
       51 -- [ ] CHK027 - Existe requisito para o dia de categoria "dia" 
          -**misto** (registros em viagem e não-viagem no mesmo dia+categ
          -oria)? [Coverage, Spec §5 RN-002/RN-009, AMB-016]             
       52 -- [ ] CHK028 - Existe requisito para categoria válida no CC ma
          -s com `limite ≤ 0`, incluindo onde reportar e a precedência do
          - motivo? [Coverage, Spec §5 RN-017, AMB-014]                  
       53 -- [ ] CHK029 - Existe requisito para a mesma categoria ser vál
          -ida em um CC e não aplicável em outro (`representacao` em `CC-
          -COMERCIAL` vs. demais)? [Coverage, Spec §5 RN-001/RN-015, §7] 
       54 -- [ ] CHK030 - Estão cobertos os fluxos de exceção de câmbio: 
          -data sem cotação (fim de semana/feriado), empate de datas, e m
          -oeda ausente de todas as `taxas`? [Coverage, Exception Flow, S
          -pec §5 RN-019/RN-020]                                         
       55 -- [ ] CHK031 - O requisito de continuidade em falha parcial (u
          -m "registro inválido" não impede o processamento dos demais) e
          -stá especificado? [Coverage, Recovery, Spec §5 RN-013, §9]    
       61 +- [x] CHK026 - Existe requisito para o cenário de fallback de 
          +centro de custo desconhecido (`padrao`), com os limites result
          +antes especificados? [Coverage, Spec §5 RN-015, AMB-013] — RN-
          +015 (aceite com limites do `padrao`) + AMB-013.               
       62 +- [x] CHK027 - Existe requisito para o dia de categoria "dia" 
          +**misto** (registros em viagem e não-viagem no mesmo dia+categ
          +oria)? [Coverage, Spec §5 RN-002/RN-009, AMB-016] — RN-002/RN-
          +009, AMB-016 e caso de borda dedicado na §7.                  
       63 +- [x] CHK028 - Existe requisito para categoria válida no CC ma
          +s com `limite ≤ 0`, incluindo onde reportar e a precedência do
          + motivo? [Coverage, Spec §5 RN-017, AMB-014] — RN-017 + AMB-01
          +4 (sob a própria categoria; precede sem NF/período).          
       64 +- [x] CHK029 - Existe requisito para a mesma categoria ser vál
          +ida em um CC e não aplicável em outro (`representacao` em `CC-
          +COMERCIAL` vs. demais)? [Coverage, Spec §5 RN-001/RN-015, §7] 
          +— RN-001/RN-015 + caso de borda na §7.                        
       65 +- [x] CHK030 - Estão cobertos os fluxos de exceção de câmbio: 
          +data sem cotação (fim de semana/feriado), empate de datas, e m
          +oeda ausente de todas as `taxas`? [Coverage, Exception Flow, S
          +pec §5 RN-019/RN-020] — RN-019 (data ausente + empate) e RN-02
          +0 (moeda ausente), com casos na §7.                           
       66 +- [x] CHK031 - O requisito de continuidade em falha parcial (u
          +m "registro inválido" não impede o processamento dos demais) e
          +stá especificado? [Coverage, Recovery, Spec §5 RN-013, §9] — R
          +N-013 ("os demais registros são processados normalmente") + cr
          +itério em §9.                                                 
       67  
       68  ## Edge Case Coverage
       69  
       59 -- [ ] CHK032 - Estão definidos os limites de fronteira monetár
          -ia: valor exatamente no limiar de NF vs. um centavo acima, e a
          -rredondamento de valor com >2 casas? [Edge Case, Spec §7, RN-0
          -06/RN-011]                                                    
       60 -- [ ] CHK033 - Estão definidos os limites de fronteira de perí
          -odo: `data` igual a `inicio`/`fim` (inclusivo) e data fora do 
          -intervalo? [Edge Case, Spec §7, RN-007, AMB-009]              
       61 -- [ ] CHK034 - Está definido o caso de despesa aceita cujo ree
          -mbolso é 0 por teto já consumido (permanece em `total_aceito` 
          -com valor cheio)? [Edge Case, Spec §7, RN-005]                
       62 -- [ ] CHK035 - Está definido o comportamento para `moeda` = `m
          -oeda_base` (sem conversão, não-viagem) versus `moeda` ausente,
          - como casos distintos e ambos cobertos? [Edge Case, Spec §7, R
          -N-018]                                                        
       70 +- [x] CHK032 - Estão definidos os limites de fronteira monetár
          +ia: valor exatamente no limiar de NF vs. um centavo acima, e a
          +rredondamento de valor com >2 casas? [Edge Case, Spec §7, RN-0
          +06/RN-011] — §7 (100,00 vs 100,01; 33,333 → 33,33) + RN-006/RN
          +-011.                                                         
       71 +- [x] CHK033 - Estão definidos os limites de fronteira de perí
          +odo: `data` igual a `inicio`/`fim` (inclusivo) e data fora do 
          +intervalo? [Edge Case, Spec §7, RN-007, AMB-009] — Requisito c
          +laro (RN-007 + AMB-009: `[inicio, fim]` inclusive). **Observaç
          +ão:** a §7 exemplifica só a fronteira `fim` (`d-014`); a front
          +eira `inicio` não tem caso concreto na tabela — considere adic
          +ionar um exemplo simétrico.                                   
       72 +- [x] CHK034 - Está definido o caso de despesa aceita cujo ree
          +mbolso é 0 por teto já consumido (permanece em `total_aceito` 
          +com valor cheio)? [Edge Case, Spec §7, RN-005] — Caso de borda
          + dedicado na §7 + RN-005.                                     
       73 +- [x] CHK035 - Está definido o comportamento para `moeda` = `m
          +oeda_base` (sem conversão, não-viagem) versus `moeda` ausente,
          + como casos distintos e ambos cobertos? [Edge Case, Spec §7, R
          +N-018] — §7 traz os dois casos separados; RN-018 os distingue.
       74  
       75  ## Non-Functional Requirements
       76  
       66 -- [ ] CHK036 - O requisito de **determinismo** (mesmo input → 
          -mesma saída) está declarado e é o suficientemente forte para c
          -obrir empates de câmbio e ordenação de duplicatas? [Non-Functi
          -onal, Spec §9, RN-008/RN-019]                                 
       67 -- [ ] CHK037 - A precisão monetária (2 casas, half-up) está es
          -pecificada de forma uniforme para entrada, cálculos intermediá
          -rios (câmbio) e saída? [Non-Functional, Spec §5 RN-011, AMB-01
          -8]                                                            
       77 +- [x] CHK036 - O requisito de **determinismo** (mesmo input → 
          +mesma saída) está declarado e é o suficientemente forte para c
          +obrir empates de câmbio e ordenação de duplicatas? [Non-Functi
          +onal, Spec §9, RN-008/RN-019] — §9 declara determinismo; RN-00
          +8 (primeira ocorrência) e RN-019 (empate → menor taxa) removem
          + as fontes de não-determinismo.                               
       78 +- [x] CHK037 - A precisão monetária (2 casas, half-up) está es
          +pecificada de forma uniforme para entrada, cálculos intermediá
          +rios (câmbio) e saída? [Non-Functional, Spec §5 RN-011, AMB-01
          +8] — RN-011 + AMB-018 cobrem entrada, conversão e saída.      
       79  
       80  ## Dependencies & Assumptions
       81  
       71 -- [ ] CHK038 - Os pressupostos sobre arquivos externos bem for
          -mados (política e câmbio) estão explicitamente documentados co
          -mo fora de escopo de validação, distinguindo "recusa de negóci
          -o" de "erro fatal"? [Assumption, Spec §3/§10, RN-018/RN-020]  
       72 -- [ ] CHK039 - As dependências entre a resolução da política/c
          -âmbio e as regras seguintes estão documentadas na ordem de apl
          -icação (§8), sem passo faltante? [Dependency, Spec §8]        
       82 +- [x] CHK038 - Os pressupostos sobre arquivos externos bem for
          +mados (política e câmbio) estão explicitamente documentados co
          +mo fora de escopo de validação, distinguindo "recusa de negóci
          +o" de "erro fatal"? [Assumption, Spec §3/§10, RN-018/RN-020] —
          + §3/§10 documentam; §10 distingue moeda ausente (recusa) de ar
          +quivo inparseável (aborta).                                   
       83 +- [x] CHK039 - As dependências entre a resolução da política/c
          +âmbio e as regras seguintes estão documentadas na ordem de apl
          +icação (§8), sem passo faltante? [Dependency, Spec §8] — §8 li
          +sta os 12 passos, da carga de política/câmbio à agregação.    
       84  
       85  ## Ambiguities & Conflicts
       86  
       76 -- [ ] CHK040 - Todas as ambiguidades resolvidas (AMB-001..AMB-
          -018) têm decisão, justificativa e regra afetada, sem nenhuma d
          -ecisão de câmbio/viagem resolvida apenas no código sem registr
          -o correspondente? [Ambiguity, Spec §6]                        
       77 -- [ ] CHK041 - Existe algum conflito residual entre o texto hi
          -stórico substituído (ex.: AMB-008) e as regras vigentes que po
          -ssa induzir implementação errada? [Conflict, Spec §6 AMB-008/A
          -MB-016]                                                       
       78 -- [ ] CHK042 - Os itens deixados "em aberto" na §10 (diárias r
          -eais, duplicata parcial, validação de política/câmbio, fuso, m
          -últiplos inputs) estão claramente marcados como não-requisitos
          - desta versão, sem virarem comportamento implícito? [Ambiguity
          -, Spec §10]                                                   
       87 +- [x] CHK040 - Todas as ambiguidades resolvidas (AMB-001..AMB-
          +018) têm decisão, justificativa e regra afetada, sem nenhuma d
          +ecisão de câmbio/viagem resolvida apenas no código sem registr
          +o correspondente? [Ambiguity, Spec §6] — As AMBs de câmbio/via
          +gem (016/017/018) têm decisão, justificativa e regra afetada. 
       88 +- [x] CHK041 - Existe algum conflito residual entre o texto hi
          +stórico substituído (ex.: AMB-008) e as regras vigentes que po
          +ssa induzir implementação errada? [Conflict, Spec §6 AMB-008/A
          +MB-016] — Dentro da spec, não (AMB-008 marcada como substituíd
          +a). **CONFLITO CROSS-ARTIFACT (fora da spec):** `CLAUDE.md` es
          +tá desatualizado e contradiz a spec vigente — (1) "Fora de esc
          +opo" diz *"Sem conversão de moeda (tudo em BRL)"*, mas RN-018.
          +.RN-020 introduziram câmbio; (2) o comando ainda mostra a flag
          + `[--em-viagem]`, removida por AMB-016/§4. Corrigir `CLAUDE.md
          +` antes de implementar para não induzir código errado.        
       89 +- [x] CHK042 - Os itens deixados "em aberto" na §10 (diárias r
          +eais, duplicata parcial, validação de política/câmbio, fuso, m
          +últiplos inputs) estão claramente marcados como não-requisitos
          + desta versão, sem virarem comportamento implícito? [Ambiguity
          +, Spec §10] — §10 lista cada item como explicitamente em abert
          +o, com decisão provisória quando aplicável.                   
       90  
       91  ## Notes
       92  
       93  - Marque itens concluídos: `[x]`
       94  - Anote lacunas e decisões inline, e promova qualquer lacuna r
           eal a uma clarificação na spec ou a uma entrada em `DECISIONS.
           md`.
       95  - Este checklist valida a spec, não a implementação — nenhum i
           tem deve ser "testado rodando o sistema".
       96 +                                                              
       97 +### Ações sugeridas (por prioridade)                          
       98 +                                                              
       99 +1. **CHK041 — `CLAUDE.md` desatualizado (fora da spec, alta pr
          +ioridade):** remover "Sem conversão de moeda (tudo em BRL)" e 
          +a flag `--em-viagem` do bloco de comandos; alinhar com RN-018.
          +.RN-020 e AMB-016.                                            
      100 +2. **CHK001 — Política (lacuna menor):** declarar em §4 quais 
          +campos de categoria são obrigatórios, ou remeter explicitament
          +e a §10.                                                      
      101 +3. **CHK016 — Precedência (observação):** citar em RN-017/RN-0
          +20 que "limite ≤ 0" prevalece sobre "cambio não identificado".
      102 +4. **CHK033 — Exemplo de borda (observação):** acrescentar à §
          +7 um caso concreto de `data == inicio`.                       

● Checklist executado contra spec.md v1.4.

  Resultado: 39/42 adequados

  A spec está madura e internamente muito consistente — as regras de câmbio e
  centro de custo estão bem amarradas (ordem de aplicação §8, precedências,
  invariantes e exclusões de total_despesas batem entre RNs, AMBs e critérios de
  aceite). Achei 4 pontos:

  1. CHK041 — CLAUDE.md desatualizado (alta prioridade, fora da spec)
  A spec está limpa, mas o CLAUDE.md contradiz as regras vigentes:
  - Linha 59: "Sem conversão de moeda (tudo em BRL)" — mas RN-018..RN-020
  introduziram câmbio.
  - Bloco de comandos ainda mostra a flag [--em-viagem] — removida por
  AMB-016/§4 (viagem agora é derivada da moeda, por registro).

  Isso é o achado mais acionável: um agente lendo o CLAUDE.md no início da
  sessão pode implementar contra regras revogadas. Vale corrigir antes de
  implementar.

  2. CHK001 — lacuna menor na spec
  §4 só marca observacao como opcional; a obrigatoriedade de
  limite/periodicidade não é declarada. Mitigado por §10 ("assume política bem
  formada"), mas para um gate formal vale explicitar ou remeter a §10.

  3. CHK016 — observação (precedência implícita)
  A §8 coloca "limite > 0" (passo 5) antes da conversão (passo 6), logo "nao
  reembolsavel" prevalece sobre "cambio não identificado" — correto e
  consistente, mas RN-020 não cita essa precedência. Considere adicioná-la.

  4. CHK033 — observação (exemplo de borda)
  A regra de período inclusivo [inicio, fim] está clara, mas a §7 só exemplifica
  a fronteira fim (d-014). Um caso simétrico de data == inicio deixaria a
  tabela completa.

  Os 3 primeiros itens têm ações sugeridas gravadas no fim do checklist. Nenhum
  deles é bloqueante para a corretude da spec em si — o único de fato acionável
  agora é a atualização do CLAUDE.md.

  Quer que eu já atualize o CLAUDE.md para remover as duas linhas obsoletas
  (câmbio + --em-viagem)?

✻ Sautéed for 3m 13s

❯ Atualize CLAUDE.md                                                            

  Read 1 file (ctrl+o to expand)

● Let me check the actual CLI contract before editing, so I don't invent flags.

  Read 1 file, listed 1 directory (ctrl+o to expand)

● The real CLI (per quickstart.md/cli-contract.md): --input, --output, optional
  --politica/--cambio (defaulting to packaged files), no --em-viagem. I'll align
  CLAUDE.md to that.
● Update(CLAUDE.md)
  ⎿  Added 4 lines, removed 2 lines
      35  ## Stack e comandos
      36  
      37  - Linguagem: Python 3.13 (somente stdlib em runtime; sem depend
          ências externas)
      38 -- Rodar: `calcular --input despesas.json --output resultado.jso
         -n [--em-viagem]`                                               
      39 -  (em dev, sem instalar: `python -m src --input ... --output ..
         -. [--em-viagem]`)                                              
      38 +- Rodar: `calcular --input despesas.json --output resultado.jso
         +n [--politica p.json] [--cambio c.json]`                       
      39 +  (em dev, sem instalar: `python -m src --input ... --output ..
         +.`). Sem `--politica`/`--cambio`,                              
      40 +  usa a política e o câmbio empacotados em `src/informacoes_ext
         +ernas/`. Não há mais `--em-viagem`:                            
      41 +  viagem é derivada por registro (moeda ≠ base, RN-009).       
      42  - Instalar (dev): `pip install -e ".[dev]"` (cria o comando `ca
          lcular` e instala `pytest`)
      43  - Testes: `pytest`
      44  - Lint/format: não há ferramenta configurada; siga PEP 8

● Update(CLAUDE.md)
  ⎿  Added 2 lines, removed 1 line
      58  
      59  - Sem estornos, créditos ou saldos negativos; reembolso é sempr
          e ≥ 0.
      60  - Não valida autenticidade de nota fiscal (confia em `tem_nota_
          fiscal`).
      61 -- Sem conversão de moeda (tudo em BRL) e sem regra de calendári
         -o (dia útil/feriado).                                          
      61 +- Converte moeda via `cambio.json` (RN-018..RN-020); a `moeda_b
         +ase` é a do câmbio e não se                                    
      62 +  buscam cotações fora do arquivo. Sem regra de calendário (dia
         + útil/feriado).                                                
      63  - Não persiste dados nem expõe interface além de ler um input e
           emitir um output.

● CLAUDE.md atualizado — duas correções, alinhadas ao contrato real da CLI
  (quickstart.md/cli-contract.md):

  1. Bloco de comandos (Stack e comandos)
  - Removida a flag --em-viagem (viagem agora é por registro, RN-009).
  - Adicionadas as flags reais [--politica] / [--cambio], com a nota de que, sem
  elas, usa a política e o câmbio empacotados em src/informacoes_externas/.

  2. Fora de escopo
  - Trocado "Sem conversão de moeda (tudo em BRL)" por: converte moeda via
  cambio.json (RN-018..RN-020), moeda_base vinda do câmbio, sem buscar cotações
  fora do arquivo.
  - Mantida a parte que continua verdadeira: sem regra de calendário (dia
  útil/feriado).

  Com isso, o achado CHK041 do checklist está resolvido — o CLAUDE.md não
  contradiz mais as regras de câmbio/viagem da spec v1.4. Os outros três itens
  (CHK001, CHK016, CHK033) são ajustes opcionais na própria spec; me avise se
  quer que eu aplique algum deles.

  Nota: essas mudanças são de documentação, então o commit segue a convenção
  docs: do projeto (ex.: docs: alinha CLAUDE.md às regras de câmbio e viagem por
  registro) — quer que eu faça o commit?

✻ Brewed for 36s