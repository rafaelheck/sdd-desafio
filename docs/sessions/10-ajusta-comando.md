 ▐▛███▜▌   Claude Code v2.1.220
▝▜█████▛▘  Opus 4.8 · Claude Pro
  ▘▘ ▝▝    ~\Área de Trabalho\Teste SDD\sdd-desafio


❯ /speckit-plan Ajuste o planejamento existente para que se utilize o arg parse 
"calcular", para que possa rodar o sistema através dele                         
                                                                                
Exemplo de comando que deve funcionar:                                          
python -m src.cli calcular --input exemplos\despesas-exemplo.json --output      
resultado.json                                                                  

● I'll start by running the pre-execution checks and setup for the plan
  workflow.

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● No extension hooks. Let me run the setup script.

  Read 2 files, ran 1 shell command (ctrl+o to expand)

● The plan mentions calcular as the installed console-script, invoked via python
  -m src. The user wants calcular to be an argparse subcommand runnable as
  python -m src.cli calcular .... Let me look at the current CLI and contract.

  Read 2 files (ctrl+o to expand)

● Let me see the supporting files that define invocation so I adjust the plan
  consistently.

  Read 3 files (ctrl+o to expand)

● I have the full picture. Currently calcular is the installed console-script 
  name (pyproject [project.scripts], prog="calcular"), with --input/--output/...
  as top-level flags; dev runs via python -m src. Your request turns calcular
  into an argparse subcommand so python -m src.cli calcular --input ... --output
  ... works.

  The one design point that changes pyproject.toml and the CLI contract — and is
  genuinely your call — is what happens to the existing installed calcular
  console-script once calcular becomes a subcommand.

● User answered Claude's questions:
  ⎿  · Ao tornar `calcular` um subcomando do argparse (rodável via `python -m 
     src.cli calcular ...`), o que fazer com o console-script `calcular` 
     instalado hoje (pyproject `[project.scripts]`), cuja invocação atual é 
     `calcular --input ...`? → Preservar via wrapper

● Decision recorded: preserve the console-script via a wrapper. Now I'll update
  the design artifacts. Let me check where invocation forms appear across the
  specs so I keep them consistent.

  Searched for 2 patterns, read 2 files, listed 1 directory, ran 1 shell command (ctrl+o to expand)

● DECISIONS.md lives in the spec dir. Let me read it.

  Read 1 file (ctrl+o to expand)

● This is a CLI-invocation change with no new business rule, so
  spec.md/DECISIONS.md stay untouched — the plan and CLI contract are the right
  artifacts. The design I'll record (per your choice):

  - cli.py: argparse gains add_subparsers(dest="comando", required=True) with a
  calcular subparser holding --input/--output/--politica/--cambio.
  - cli.main_console wrapper injects calcular so the installed calcular --input 
  … stays one word; pyproject points the script at it.
  - python -m src.cli calcular … (your target) and python -m src calcular … both
  call cli.main.

  Let me apply the edits.

● Update(specs\001-motor-reembolso\plan.md)
  ⎿  Added 6 lines, removed 3 lines
       1  # Plano Técnico — Motor de Cálculo de Reembolso
       2  
       3 -**Versão:** 1.4 · **Baseado na spec:** 1.4 (Clarifications 2026
         --07-30 e 2026-07-31;                                           
       4 -D-003..D-007). Substitui o plano 1.1, que assumia política embu
         -tida em código,                                                
       5 -categorias fixas e viagem por flag de CLI.                     
       3 +**Versão:** 1.5 · **Baseado na spec:** 1.4 (Clarifications 2026
         +-07-30 e 2026-07-31;                                           
       4 +D-003..D-007). O plano 1.5 ajusta apenas a *forma de invocação*
         + da CLI — `calcular`                                           
       5 +passa a ser um **subcomando** do `argparse`, rodável por       
       6 +`python -m src.cli calcular --input ... --output ...`, sem toca
         +r em regra de negócio.                                         
       7 +Substitui o plano 1.1, que assumia política embutida em código,
         + categorias fixas e                                            
       8 +viagem por flag de CLI.                                        
       9  
      10  > Aqui mora o COMO. Este arquivo pode e deve falar de linguagem
          , biblioteca e
      11  > arquitetura. O que ele **não** pode é introduzir regra de neg
          ócio nova — se

● Update(specs\001-motor-reembolso\plan.md)
  ⎿  Added 4 lines, removed 4 lines
      55  núcleo — o núcleo nunca abre arquivo.
      56  
      57  ```
      58 -calcular --input despesas.json --output resultado.json         
      59 -         [--politica ...] [--cambio ...]                       
      60 -        │                                                      
      58 +python -m src.cli calcular --input despesas.json --output resul
         +tado.json                                                      
      59 +                           [--politica ...] [--cambio ...]     
      60 +        │  (subcomando `calcular`; console script `calcular ...
         +` chega aqui via wrapper)                                      
      61          ▼
      62 -   cli.py (argparse)                         ── casca de I/O   
      62 +   cli.py (argparse + subparser `calcular`)  ── casca de I/O   
      63          │
      64          ▼
      65     io_json.py  ── lê input, politica-v4.json e cambio.json (par
          se_float=Decimal);

● Update(specs\001-motor-reembolso\plan.md)
  ⎿  Added 2 lines, removed 2 lines
      87  ```
      88  src/
      89    __init__.py
      90 -  __main__.py     # python -m src ... (dev)                    
      91 -  cli.py          # argparse (SEM --em-viagem); resolve caminho
         -s de política/câmbio; exit codes                               
      90 +  __main__.py     # python -m src calcular ... (dev; delega a c
         +li.main)                                                       
      91 +  cli.py          # argparse c/ subcomando `calcular` (SEM --em
         +-viagem); wrapper main_console; caminhos de política/câmbio; ex
         +it codes                                                       
      92    io_json.py      # ler_entrada / ler_politica / ler_cambio + s
          erialização
      93    modelo.py       # dataclasses: Despesa, CategoriaConfig, Poli
          tica, Cambio, Reprovacao, ResultadoCategoria, Resultado; enum M
          otivo
      94    politica.py     # politica_de_dict / cambio_de_dict (dict→est
          rutura, puro); CASAS_DECIMAIS

● Update(specs\001-motor-reembolso\plan.md)
  ⎿  Added 1 line
      148  
      149  Mantidas de 1.1: **DT-001** (dinheiro em `Decimal` desde o JSO
           N), **DT-002** (regra em
      150  `regras.py`, uma função por RN), **DT-003** (CLI `argparse`, c
           omando `calcular`),
      151 +**DT-003** (CLI `argparse`; `calcular` agora como **subcomando
          +** — ver DT-003b),                                            
      152  **DT-004** (pipeline explícito na ordem da Seção 8), **DT-005*
           * (só stdlib no runtime),
      153  **DT-006** (erro de topo aborta; registro malformado é recusa 
           individual),
      154  **DT-007** (`total_despesas` exclui `valor ≤ 0`). Novas/altera
           das:

● I created a duplicate DT-003. Let me fix that — the original already lists
  DT-003.

  Read 1 file (ctrl+o to expand)
● Update(specs\001-motor-reembolso\plan.md)
  ⎿  Added 2 lines, removed 3 lines
      147  ## 5. Decisões técnicas
      148  
      149  Mantidas de 1.1: **DT-001** (dinheiro em `Decimal` desde o JSO
           N), **DT-002** (regra em
      150 -`regras.py`, uma função por RN), **DT-003** (CLI `argparse`, c
          -omando `calcular`),                                           
      151 -**DT-003** (CLI `argparse`; `calcular` agora como **subcomando
          -** — ver DT-003b),                                            
      152 -**DT-004** (pipeline explícito na ordem da Seção 8), **DT-005*
          -* (só stdlib no runtime),                                     
      150 +`regras.py`, uma função por RN), **DT-003** (CLI `argparse`; `
          +calcular` agora como                                          
      151 +**subcomando** — ver DT-003b), **DT-004** (pipeline explícito 
          +na ordem da Seção 8), **DT-005** (só stdlib no runtime),      
      152  **DT-006** (erro de topo aborta; registro malformado é recusa 
           individual),
      153  **DT-007** (`total_despesas` exclui `valor ≤ 0`). Novas/altera
           das:
      154  

● Now the DT-003b decision block:

● Update(specs\001-motor-reembolso\plan.md)
  ⎿  Added 16 lines, removed 6 lines
      152  **DT-006** (erro de topo aborta; registro malformado é recusa 
           individual),
      153  **DT-007** (`total_despesas` exclui `valor ≤ 0`). Novas/altera
           das:
      154  
      155 -### DT-003b — CLI sem `--em-viagem`; caminhos de política/câmb
          -io opcionais                                                  
      156 -**Contexto:** viagem virou por-registro (RN-009); o motor prec
          -isa de dois arquivos externos.                                
      157 -**Decisão:** remover `--em-viagem`. Manter `--input`/`--output
          -` obrigatórios e adicionar                                    
      158 -`--politica`/`--cambio` opcionais (default: arquivos empacotad
          -os). Sem regra de negócio na CLI.                             
      159 -**Consequência:** a assinatura de `CLAUDE.md` (`[--em-viagem]`
          -) fica desatualizada; sinalizar                               
      160 -para atualizar `CLAUDE.md`.                                   
      155 +### DT-003b — CLI: subcomando `calcular`, wrapper de console, 
          +sem `--em-viagem`, caminhos opcionais                         
      156 +**Contexto:** viagem virou por-registro (RN-009); o motor prec
          +isa de dois arquivos externos;                                
      157 +e a execução deve ser possível sem instalar, por `python -m sr
          +c.cli calcular ...`.                                          
      158 +**Decisão:** `calcular` deixa de ser só o nome do console scri
          +pt e passa a ser um **subcomando**                            
      159 +do `argparse` em `cli.py` (`add_subparsers(dest="comando", req
          +uired=True)`). O subcomando carrega                           
      160 +`--input`/`--output` (obrigatórios) e `--politica`/`--cambio` 
          +(opcionais, default: arquivos                                 
      161 +empacotados); `--em-viagem` continua removido. Sem regra de ne
          +gócio na CLI. As três formas de                               
      162 +execução são equivalentes e todas chamam `cli.main`:          
      163 +- `python -m src.cli calcular --input ... --output ...` — alvo
          + do pedido; roda sem instalar;                                
      164 +- `python -m src calcular --input ... --output ...` — `__main_
          +_.py` delega a `cli.main`;                                    
      165 +- `calcular --input ... --output ...` — console script instala
          +do, preservado por um **wrapper**                             
      166 +  `cli.main_console` que injeta o subcomando (`main(["calcular
          +", *argv])`); a linha instalada                               
      167 +  continua com uma só palavra. `pyproject` aponta `calcular = 
          +"src.cli:main_console"`.                                      
      168 +**Consequência:** a forma antiga `python -m src --input ...` (
          +sem subcomando) deixa de valer — passa                        
      169 +a exigir `calcular`. `CLAUDE.md` (que cita `python -m src --in
          +put ...` e a assinatura `[--em-viagem]`)                      
      170 +fica desatualizado; sinalizar para atualizar. Contrato em [`co
          +ntracts/cli-contract.md`](./contracts/cli-contract.md).       
      171  
      172  ### DT-008 — Política e câmbio como dados injetados, não const
           antes
      173  **Contexto:** RN-015/018 externalizam política e câmbio; o núc
           leo deve permanecer puro.

● Now the CLI contract — the invocation section:

● Update(specs\001-motor-reembolso\contracts\cli-contract.md)
  ⎿  Added 12 lines, removed 6 lines
       3  Interface pública do sistema (spec 1.4). Único ponto de contato
           com o usuário.
       4  Mudanças desde 1.1: **removido `--em-viagem`** (viagem é por re
          gistro, RN-009);
       5  **adicionados** `--politica`/`--cambio` (opcionais); a saída **
          não** tem mais `em_viagem`;
       6 -o câmbio ausente/inválido **aborta**.                          
       6 +o câmbio ausente/inválido **aborta**; **`calcular` é um subcoma
         +ndo do `argparse`** (plano 1.5).                               
       7  
       8  ## Invocação
       9  
      10 +`calcular` é um **subcomando** do `argparse`. Formas equivalent
         +es (todas chamam `cli.main`):                                  
      11 +                                                               
      12  ```
      11 -calcular --input <arquivo.json> --output <arquivo.json> [--poli
         -tica <arquivo.json>] [--cambio <arquivo.json>]                 
      12 -```                                                            
      13 +# sem instalar, direto do repositório (forma primária)         
      14 +python -m src.cli calcular --input <arquivo.json> --output <arq
         +uivo.json> [--politica <arquivo.json>] [--cambio <arquivo.json>
         +]                                                              
      15  
      14 -Em desenvolvimento (sem instalar o console script):            
      16 +# equivalente via pacote                                       
      17 +python -m src calcular --input <arquivo.json> --output <arquivo
         +.json> [--politica ...] [--cambio ...]                         
      18  
      19 +# console script instalado (pip install -e .) — o wrapper injet
         +a o subcomando, então fica com uma só palavra                  
      20 +calcular --input <arquivo.json> --output <arquivo.json> [--poli
         +tica ...] [--cambio ...]                                       
      21  ```
      17 -python -m src --input <arquivo.json> --output <arquivo.json> [-
         --politica ...] [--cambio ...]                                  
      18 -```                                                            
      22  
      23 +> A forma antiga sem subcomando (`python -m src --input ...`) *
         +*não** vale mais: o subcomando                                 
      24 +> `calcular` é obrigatório. Faltar o subcomando é erro de uso d
         +o `argparse` (código `2`).                                     
      25 +                                                               
      26  ## Argumentos
      27  
      28  | Argumento | Obrigatório | Tipo | Default | Significado |

● Update(specs\001-motor-reembolso\contracts\cli-contract.md)
  ⎿  Added 1 line, removed 1 line
      77  | Código | Situação |
      78  |---|---|
      79  | `0` | Sucesso: resultado escrito em `--output` (mesmo com des
          pesas reprovadas) |
      80 -| `2` | Erro de uso: argumento obrigatório ausente/inválido (pa
         -drão do `argparse`) |                                          
      80 +| `2` | Erro de uso: subcomando `calcular` ausente ou argumento
         + obrigatório ausente/inválido (padrão do `argparse`) |         
      81  | `1` | Erro irrecuperável: `--input`, `--politica` ou `--cambi
          o` inexistente ou com JSON inparseável; JSON de topo do input i
          nválido; ou campos de topo obrigatórios ausentes (RN-013, RN-01
          8). Mensagem em `stderr`, nada escrito em `--output` |
      82  
      83  - Registro de despesa malformado **não** aborta: vira `registro
           inválido` em `reprovadas_sem_categoria`,

● Now quickstart.md — the Setup and Rodar sections:

● Update(specs\001-motor-reembolso\quickstart.md)
  ⎿  Added 11 lines, removed 5 lines
      19  
      20  ## Rodar
      21  
      22 +`calcular` é um **subcomando** do `argparse`; as três formas ab
         +aixo são equivalentes.                                         
      23 +                                                               
      24  ```bash
      25 +# sem instalar, direto do repositório (forma primária)         
      26 +python -m src.cli calcular --input exemplos/despesas-exemplo.js
         +on --output resultado.json                                     
      27 +                                                               
      28 +# equivalente via pacote                                       
      29 +python -m src calcular --input exemplos/despesas-exemplo.json -
         +-output resultado.json                                         
      30 +                                                               
      31  # console script instalado (usa política/câmbio empacotados em 
          src/informacoes_externas/)
      32  calcular --input exemplos/despesas-exemplo.json --output result
          ado.json
      33  
      26 -# sem instalar, direto do repositório                          
      27 -python -m src --input exemplos/despesas-exemplo.json --output r
         -esultado.json                                                  
      28 -                                                               
      34  # input com moedas estrangeiras (converte via cambio.json; viag
          em por registro)
      30 -calcular --input exemplos/despesas-envelope.json --output resul
         -tado.json                                                      
      35 +python -m src.cli calcular --input exemplos/despesas-envelope.j
         +son --output resultado.json                                    
      36  
      37  # apontando política/câmbio alternativos
      33 -calcular --input in.json --output out.json --politica outra-pol
         -itica.json --cambio outro-cambio.json                          
      38 +python -m src.cli calcular --input in.json --output out.json --
         +politica outra-politica.json --cambio outro-cambio.json        
      39  ```
      40  
      41 +> `calcular` é obrigatório: `python -m src --input ...` (sem o 
         +subcomando) não vale mais.                                     
      42  > Não há mais `--em-viagem`: viagem é derivada por registro (mo
          eda ≠ base, RN-009).
      43  
      44  ## Validação ponta a ponta (aceite)

● Update(specs\001-motor-reembolso\quickstart.md)
  ⎿  Added 1 line, removed 1 line
      108  | Cenário | Resultado |
      109  |---|---|
      110  | `--input`/`--politica`/`--cambio` inexistente ou JSON inpars
           eável | mensagem em `stderr`, código `1`, nada escrito |
      111 -| Falta `--input` ou `--output` | erro de uso do `argparse`, c
          -ódigo `2` |                                                   
      111 +| Falta o subcomando `calcular`, ou falta `--input`/`--output`
          + | erro de uso do `argparse`, código `2` |                    
      112  | Registro de despesa malformado (ex.: `moeda` numérica) | `re
           gistro inválido`; os demais processados; código `0` |
      113  | `moeda` sem taxa em todo o câmbio (ex.: GBP) | `cambio não i
           dentificado` **por registro**; código `0` |

● Now the research.md R-003 decision:

● Update(specs\001-motor-reembolso\research.md)
  ⎿  Added 4 lines, removed 2 lines
      25  
      26  ## R-003 — Interface de linha de comando
      27  
      28 -- **Decisão:** `argparse`, comando único `calcular`; console sc
         -ript `calcular = src.cli:main`.                                
      28 +- **Decisão:** `argparse` com **subcomando** `calcular` (`pytho
         +n -m src.cli calcular ...`); console                           
      29 +  script `calcular = src.cli:main_console`, um wrapper que inje
         +ta o subcomando para a linha                                   
      30 +  instalada seguir com uma só palavra (`calcular --input ...`).
         + Ver DT-003b no plano.                                         
      31  - **Atualização 1.4:** remove `--em-viagem` (viagem virou por-r
          egistro, RN-009); adiciona
      32    `--politica`/`--cambio` opcionais (default: arquivos empacota
          dos em `src/informacoes_externas`).
      31 -  Ver R-009. `CLAUDE.md` (que ainda cita `--em-viagem`) precisa
         - ser atualizado.                                               
      33 +  Ver R-009. `CLAUDE.md` (que ainda cita `--em-viagem` e `pytho
         +n -m src --input ...`) precisa ser atualizado.                 
      34  - **Alternativas:** `click`/`typer` — dependência desnecessária
          .
      35  
      36  ## R-004 — Serialização determinística da saída

● Design artifacts updated. data-model.md is unaffected (no data-model change).
  Let me check tasks.md so I can point to where a task must be added — the plan
  command doesn't itself write tasks.

  Searched for 3 patterns (ctrl+o to expand)

● Design updates complete. No extension hooks are registered
  (.specify/extensions.yml absent), so post-execution hooks are skipped.

  Plano ajustado — calcular como subcomando do argparse

  Branch: 001-motor-reembolso · Plano: specs/001-motor-reembolso/plan.md (bump
  1.4 → 1.5; spec permanece 1.4 — nenhuma regra de negócio mudou)

  Constitution Check: a constituição segue no estado de template (princípios não
  preenchidos) — sem gate de governança a violar. As convenções efetivas de
  CLAUDE.md (núcleo puro sem I/O; sem regra na CLI) são respeitadas: a mudança é
  só na forma de invocação.

  Artefatos de design atualizados

  - plan.md — cabeçalho 1.5; diagrama da Seção 2 com python -m src.cli calcular 
  …; comentários da estrutura de pastas (cli.py/__main__.py); DT-003b reescrita
  cobrindo o subcomando, o wrapper main_console e as três formas equivalentes;
  referência de DT-003 na Seção 5.
  - contracts/cli-contract.md — seção Invocação com as três formas; nota de que
  o subcomando é obrigatório; linha de exit code 2 incluindo subcomando ausente.
  - quickstart.md — bloco Rodar e tabela de cenários de erro.
  - research.md — R-003 (subcomando + console script via wrapper).
  - data-model.md — inalterado (a mudança não toca o modelo de dados).

  Design registrado (a implementar depois)

  - cli.py: add_subparsers(dest="comando", required=True) com subparser calcular
  carregando --input/--output/--politica/--cambio; wrapper main_console(argv)
  que injeta "calcular" para o console script seguir com uma só palavra.
  - pyproject.toml: calcular = "src.cli:main_console".
  - Formas válidas: python -m src.cli calcular … (alvo do pedido), python -m src
  calcular …, calcular … (instalado). A forma antiga python -m src --input …
  deixa de valer.

  ⚠️ Ação necessária antes de implementar

  Conforme CLAUDE.md (nada entra sem task), nenhuma task cobre isto: as tasks
  existentes vão até T-049 (todas [x]), e a última de CLI (T-042) desenha
  --input/--output como flags de topo, sem subcomando nem wrapper. O comando
  /speckit-plan encerra na fase de design e não gera tasks.

  Próximos passos: rodar /speckit-tasks para acrescentar uma task (subcomando
  calcular + main_console + pyproject + testes test_cli das três formas), depois
  /speckit-implement. CLAUDE.md também precisa ser atualizado (cita python -m 
  src --input … e a assinatura antiga [--em-viagem]) — já sinalizado na
  consequência de DT-003b.

  Quer que eu siga para /speckit-tasks com essa task?

✻ Baked for 5m 11s

※ recap: Goal: make the reembolso CLI runnable as `python -m src.cli calcular --input ... --output ...`. I updated the plan and design docs to make `calcular` an argparse subcommand. Next: run /speckit-tasks to add the implementation task, then implement. (disable recaps in /config)

❯ sim, siga para /speckit-tasks                                                 

● Skill(speckit-tasks)
  ⎿  Successfully loaded skill

● I'll run the pre-execution checks and setup.

  Ran 2 shell commands (ctrl+o to expand)

● No hooks. This project's tasks.md already has an established format (T-0NN,
  phases appended without renumbering, **Atende**/**Aceite**/**Commit** lines).
  Rather than regenerate, I'll append a new phase. Let me read the tail to match
  the exact conventions.

  Read 1 file (ctrl+o to expand)

● The last task is T-049; the file appends new phases without renumbering and
  uses its own conventions (T-0NN, [P], **Atende**/**Aceite**/**Commit**, ### 
  Superadas notes) rather than the generic [US1] template. I'll match the
  existing artifact and add Fase 11.

● Update(specs\001-motor-reembolso\tasks.md)  ⎿  Added 36 lines
      317  
      318  T-003 (constantes fixas) → T-029; T-004 (enum/modelo) → T-028;
            T-005/006 (normalização/estrutura) → T-035; T-007 (dedup) → T
           -038; T-008 (categoria) → T-032; T-011 (NF) → T-039; T-012/013
           /014 (tetos) → T-034; T-015/016 (agrega/pipeline) → T-040; T-0
           18 (leitura) → T-030; T-019 (serialização) → T-041; T-020 (CLI
           ) → T-042; T-022/027 (golden) → T-048; T-023 (cobertura) → T-0
           47; T-024 (CLAUDE.md) → T-043. As demais (T-001/002/009/010/01
           7/021/025/026) permanecem válidas ou têm seus testes reescrito
           s por T-046.
      319  
      320 +## Fase 11 — Invocação por subcomando `calcular` (plano 1.5, D
          +T-003b)                                                       
      321 +                                                              
      322 +> Ajuste **só de forma de invocação**, sem regra de negócio no
          +va (plano 1.5). `calcular`                                    
      323 +> passa a ser um **subcomando** do `argparse`, rodável por    
      324 +> `python -m src.cli calcular --input ... --output ...`; o con
          +sole script instalado segue                                   
      325 +> com uma só palavra via wrapper `main_console`. Numeração con
          +tinua de T-049; tasks antigas                                 
      326 +> não são renumeradas.                                        
      327 +                                                              
      328 +- [ ] **T-050** — `src/cli.py`: transformar `calcular` em **su
          +bcomando**. Trocar o parser plano por `add_subparsers(dest="co
          +mando", required=True)` com um subparser `calcular` que carreg
          +a `--input`/`--output` (obrigatórios) e `--politica`/`--cambio
          +` (opcionais, defaults empacotados inalterados); `main(argv)` 
          +despacha quando `args.comando == "calcular"`. Adicionar `main_
          +console(argv=None)` que injeta o subcomando (`main(["calcular"
          +, *(argv if argv is not None else sys.argv[1:])])`). Atualizar
          + a docstring de exit codes (uso `2` também quando falta o subc
          +omando). Supera a parte de forma de invocação de T-042 (mantém
          + `--politica`/`--cambio`/abort).                              
      329 +  - **Atende:** DT-003b, DT-003; `contracts/cli-contract.md`  
      330 +  - **Aceite:** `python -m src.cli calcular --input exemplos/d
          +espesas-exemplo.json --output out.json` gera a saída; faltar o
          + subcomando → exit `2`                                        
      331 +  - **Commit:** `feat(T-050): calcular como subcomando do argp
          +arse (DT-003b)`                                               
      332 +                                                              
      333 +- [ ] **T-051** [P] — `pyproject.toml`: `[project.scripts]` pa
          +ssa a `calcular = "src.cli:main_console"` (era `src.cli:main`)
          +. Supera a parte de console script de T-001.                  
      334 +  - **Atende:** DT-003b                                       
      335 +  - **Aceite:** após `pip install -e .`, `calcular --input ...
          + --output ...` (uma palavra) funciona via wrapper             
      336 +  - **Commit:** `feat(T-051): console script aponta para main_
          +console`                                                      
      337 +                                                              
      338 +- [ ] **T-052** [P] — `src/__main__.py`: atualizar a docstring
          + para `python -m src calcular ... [--politica ...] [--cambio .
          +..]` (delega a `cli.main`); sem mudança de comportamento (o su
          +bcomando agora é obrigatório). Supera a docstring de T-021.   
      339 +  - **Atende:** DT-003b                                       
      340 +  - **Aceite:** `python -m src calcular --input ... --output .
          +..` funciona; `python -m src --input ...` dá erro de uso (`2`)
      341 +  - **Commit:** `docs(T-052): __main__ documenta subcomando ca
          +lcular`                                                       
      342 +                                                              
      343 +- [ ] **T-053** — `tests/test_cli.py`: cobrir as **três** form
          +as equivalentes (`python -m src.cli calcular ...`, `python -m 
          +src calcular ...`, e o wrapper `main_console(["--input", ...])
          +`) gerando a mesma saída, e o **erro de uso** (`main([])` / se
          +m subcomando → `SystemExit(2)`). Atualizar/superar `::test_pyt
          +hon_m_src` (T-021) e os asserts de CLI de T-042/T-049 que assu
          +miam flags de topo sem subcomando.                            
      344 +  - **Atende:** DT-003b; contrato da CLI (formas de invocação,
          + exit `2`)                                                    
      345 +  - **Aceite:** `pytest tests/test_cli.py` verde cobrindo as 3
          + formas + o exit `2`                                          
      346 +  - **Commit:** `test(T-053): tres formas de invocacao e exit 
          +2 sem subcomando`                                             
      347 +                                                              
      348 +- [ ] **T-054** [P] — `CLAUDE.md`: na seção "Stack e comandos"
          +, trocar a linha de execução para o subcomando — `python -m sr
          +c.cli calcular --input ... --output ... [--politica ...] [--ca
          +mbio ...]` como forma primária, citando as equivalentes (`pyth
          +on -m src calcular ...`; console `calcular ...` via wrapper) e
          + removendo `python -m src --input ...`. Supera a linha de exec
          +ução de T-043.                                                
      349 +  - **Atende:** DT-003b; consistência com plano 1.5           
      350 +  - **Aceite:** `CLAUDE.md` não cita mais `python -m src --inp
          +ut ...`; descreve o subcomando `calcular`                     
      351 +  - **Commit:** `docs(T-054): CLAUDE.md usa subcomando calcula
          +r`                                                            
      352 +                                                              
      353 +### Superadas pela Fase 11                                    
      354 +T-001 (console_scripts `= src.cli:main`) → T-051; T-020/T-042 
          +(CLI com flags de topo, forma de invocação) → T-050 + T-053; T
          +-021 (`__main__`, `python -m src ...`) → T-052; T-043 (linha d
          +e execução no `CLAUDE.md`) → T-054. As partes de T-042 sobre `
          +--politica`/`--cambio` e abort permanecem válidas; não há RN n
          +ova (mudança só de invocação).                                
      355 +                                                              
      356  ---
      357  
      358  ## Dependências e ordem

● Now update the Dependências and Paralelização sections:

● Update(specs\001-motor-reembolso\tasks.md)
  ⎿  Added 4 lines
      379      T-047 `[P]`; T-048 (goldens) depende de T-040..T-042; T-04
           9 `[P]`.
      380    - **Ordem entre decisões:** D-005/D-006 (Fases 6–7) vêm ante
           s de D-007 (Fase 8), pois a
      381      conversão e a viagem por moeda assentam sobre a política e
           xterna e o teto por periodicidade.
      382 +- **Fase 11 (plano 1.5, subcomando `calcular`):** T-050 (`cli.
          +py`) primeiro; T-051 (`pyproject`),                           
      383 +  T-052 (`__main__` docstring) e T-054 (`CLAUDE.md`) são `[P]`
          + entre si; T-053 (testes) depende de                          
      384 +  T-050 (e de T-051 para exercitar a forma instalada). Não blo
          +queia nem é bloqueada pelas Fases 6–10                        
      385 +  (código de regra já pronto).                                
      386  
      387  ## Exemplos de paralelização
      388  

● Update(specs\001-motor-reembolso\tasks.md)
  ⎿  Added 1 line
      393  - Fases 6–10 — Rodada A: **T-028, T-029** juntos. Rodada B (te
           stes novos, TDD):
      394    **T-044, T-045, T-047** podem ser escritos antes das funções
           . Fechamento: **T-043,
      395    T-049** em paralelo com T-048.
      396 +- Fase 11 — após T-050: **T-051, T-052, T-054** em paralelo; T
          +-053 fecha validando as três formas.                          
      397  
      398  ---
      399  

● No post-execution hooks (.specify/extensions.yml absent) — skipped.

  /speckit-tasks concluído — Fase 11 acrescentada

  Arquivo: specs/001-motor-reembolso/tasks.md (append; nenhuma task renumerada)

  Nova fase

  Fase 11 — Invocação por subcomando calcular (plano 1.5, DT-003b) — 5 tasks
  novas, T-050 → T-054:

  ┌───────┬───────────────────┬────────────────────────────────────────┬─────┐
  │ Task  │      Arquivo      │                 O quê                  │ [P] │
  ├───────┼───────────────────┼────────────────────────────────────────┼─────┤
  │       │                   │ subparser calcular (dest="comando",    │     │
  │ T-050 │ src/cli.py        │ required=True) + wrapper main_console; │ —   │
  │       │                   │  docstring de exit codes               │     │
  ├───────┼───────────────────┼────────────────────────────────────────┼─────┤
  │ T-051 │ pyproject.toml    │ calcular = "src.cli:main_console"      │ ✅  │
  ├───────┼───────────────────┼────────────────────────────────────────┼─────┤
  │ T-052 │ src/__main__.py   │ docstring → python -m src calcular …   │ ✅  │
  ├───────┼───────────────────┼────────────────────────────────────────┼─────┤
  │ T-053 │ tests/test_cli.py │ 3 formas equivalentes + exit 2 sem     │ —   │
  │       │                   │ subcomando                             │     │
  ├───────┼───────────────────┼────────────────────────────────────────┼─────┤
  │ T-054 │ CLAUDE.md         │ linha de execução usa o subcomando     │ ✅  │
  └───────┴───────────────────┴────────────────────────────────────────┴─────┘

  Contagem e organização

  - Total no arquivo: 54 tasks (T-001…T-054); novas nesta rodada: 5.
  - Organização: por fase, seguindo a convenção já estabelecida no tasks.md (IDs
  T-0NN, marcador [P], blocos **Atende**/**Aceite**/**Commit**, seção ### 
  Superadas). Não apliquei os rótulos genéricos [US1] do template porque este
  artefato não usa histórias de usuário — mantive consistência com o arquivo
  existente.
  - Atualizei também Dependências e ordem, Exemplos de paralelização e a nota
  Superadas pela Fase 11 (T-001→T-051, T-020/T-042→T-050+T-053, T-021→T-052,
  T-043→T-054).

  Paralelismo

  Após T-050 (mudança central), T-051 · T-052 · T-054 rodam em paralelo
  (arquivos distintos); T-053 fecha validando as três formas de invocação. A
  Fase 11 é independente das Fases 6–10 (o código de regra já está pronto).

  Critério de teste independente

  python -m src.cli calcular --input exemplos/despesas-exemplo.json --output 
  resultado.json gera a saída esperada; python -m src calcular … e o console
  calcular … (via wrapper) produzem o mesmo resultado; faltar o subcomando →
  exit 2. Sem RN nova — nada a acrescentar na matriz de Cobertura.

  Escopo sugerido (MVP da mudança)

  T-050 + T-051 já entregam o alvo do pedido (python -m src.cli calcular … e o
  console script preservado). T-052/T-053/T-054 completam docstring, testes e
  docs.

  Validação de formato

  Todas as 5 tasks seguem o checklist do projeto: - [ ] + ID T-0NN + [P] quando
  paralelizável + descrição com caminho de arquivo. ✅

  Próximo passo: /speckit-implement para executar a Fase 11. Quer que eu siga?

✻ Baked for 2m 10s

❯ siga para /speckit-implement                                                  

● Skill(speckit-implement)
  ⎿  Successfully loaded skill

● I'll run the pre-execution checks and prerequisites.

  Ran 2 shell commands (ctrl+o to expand)

● No extension hooks. Let me check the checklists status before implementing.

  Ran 1 shell command (ctrl+o to expand)

● spec-gate.md has 1 incomplete item. Let me see what it is before deciding.

  Searched for 1 pattern (ctrl+o to expand)

● User answered Claude's questions:
  ⎿  · O gate de spec tem 1 item incompleto (CHK001 — lacuna menor sobre quais 
     campos de `politica-v4.json` são obrigatórios), **não relacionado** à 
     mudança de invocação da CLI (Fase 11). Prossigo com a implementação da Fase
     11 mesmo assim? → Prosseguir (Recommended)

● Proceeding. Let me look at the current test_cli.py and .gitignore before
  implementing.

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● All patterns present, .gitignore fine. Now implementing Fase 11. Starting with
  T-050 (src/cli.py):

● Write(src\cli.py)
  ⎿  Added 40 lines, removed 10 lines
       1  """Interface de linha de comando `calcular` (DT-003, DT-003b).
       2  
       3 +`calcular` e um subcomando do argparse. Formas equivalentes (to
         +das chamam `main`):                                            
       4 +  - `python -m src.cli calcular --input ... --output ...`  (sem
         + instalar; forma primaria)                                     
       5 +  - `python -m src calcular --input ... --output ...`       (vi
         +a pacote; `__main__` delega)                                   
       6 +  - `calcular --input ... --output ...`                     (co
         +nsole script; wrapper `main_console`)                          
       7 +                                                               
       8  Liga leitura das 3 fontes (input, politica, cambio) -> pipeline
           -> escrita. Sem
       9  regra de negocio na CLI. Exit codes: 0 sucesso, 1 erro irrecupe
          ravel de entrada
      10  (input/politica/cambio ausente ou inparseavel; topo invalido), 
          2 erro de uso
       6 -(padrao do argparse). Ver `contracts/cli-contract.md`.         
      11 +(subcomando `calcular` ausente ou argumento obrigatorio ausente
         +; padrao do argparse).                                         
      12 +Ver `contracts/cli-contract.md`.                               
      13  """
      14  
      15  from __future__ import annotations
     ...
      28  
      29  def _parser() -> argparse.ArgumentParser:
      30      parser = argparse.ArgumentParser(
      25 -        prog="calcular",                                       
      31          description="Motor de calculo de reembolso de despesas 
          corporativas.",
      32      )
      28 -    parser.add_argument("--input", required=True, help="arquivo
         - JSON de entrada")                                             
      29 -    parser.add_argument("--output", required=True, help="arquiv
         -o JSON de saida")                                              
      30 -    parser.add_argument(                                       
      33 +    sub = parser.add_subparsers(dest="comando", required=True) 
      34 +    calcular = sub.add_parser(                                 
      35 +        "calcular",                                            
      36 +        help="calcula o reembolso de um arquivo de despesas",  
      37 +        description="Calcula o reembolso de um arquivo de despe
         +sas.",                                                         
      38 +    )                                                          
      39 +    calcular.add_argument("--input", required=True, help="arqui
         +vo JSON de entrada")                                           
      40 +    calcular.add_argument("--output", required=True, help="arqu
         +ivo JSON de saida")                                            
      41 +    calcular.add_argument(                                     
      42          "--politica",
      43          default=str(_POLITICA_PADRAO),
      44          help="politica externa de categorias/limites por centro
           de custo (RN-015)",
      45      )
      35 -    parser.add_argument(                                       
      46 +    calcular.add_argument(                                     
      47          "--cambio",
      48          default=str(_CAMBIO_PADRAO),
      49          help="tabela de cambio: moeda_base + taxas por data (RN
          -018)",
     ...
      51      return parser
      52  
      53  
      43 -def main(argv: list[str] | None = None) -> int:                
      44 -    """Ponto de entrada. Retorna o codigo de saida."""         
      45 -    args = _parser().parse_args(argv)  # argparse sai com codig
         -o 2 em erro de uso.                                            
      46 -                                                               
      54 +def _executa_calcular(args: argparse.Namespace) -> int:        
      55      try:
      56          entrada = io_json.ler_entrada(args.input)
      57          politica = io_json.ler_politica(args.politica)
     ...
      71      return 0
      72  
      73  
      74 +def main(argv: list[str] | None = None) -> int:                
      75 +    """Ponto de entrada. Retorna o codigo de saida.            
      76 +                                                               
      77 +    `argv` deve comecar pelo subcomando (`["calcular", "--input
         +", ...]`); a ausencia                                          
      78 +    do subcomando e erro de uso do argparse (SystemExit codigo 
         +2).                                                            
      79 +    """                                                        
      80 +    args = _parser().parse_args(argv)  # argparse sai com codig
         +o 2 em erro de uso.                                            
      81 +    # Ha um unico subcomando (`calcular`); `required=True` gara
         +nte que args.comando existe.                                   
      82 +    return _executa_calcular(args)                             
      83 +                                                               
      84 +                                                               
      85 +def main_console(argv: list[str] | None = None) -> int:        
      86 +    """Wrapper do console script: injeta o subcomando `calcular
         +`.                                                             
      87 +                                                               
      88 +    Permite que a linha instalada siga com uma so palavra      
      89 +    (`calcular --input ... --output ...`) enquanto `main` exige
         + o subcomando.                                                 
      90 +    """                                                        
      91 +    if argv is None:                                           
      92 +        argv = sys.argv[1:]                                    
      93 +    return main(["calcular", *argv])                           
      94 +                                                               
      95 +                                                               
      96  if __name__ == "__main__":
      97      sys.exit(main())

● Now T-051 (pyproject.toml) and T-052 (src/__main__.py) — parallel, distinct
  files:

● Update(pyproject.toml)
  ⎿  Added 1 line, removed 1 line
      13  dev = ["pytest>=8"]
      14  
      15  [project.scripts]
      16 -calcular = "src.cli:main"                                      
      16 +calcular = "src.cli:main_console"                              
      17  
      18  [tool.setuptools]
      19  packages = ["src"]

● Write(src\__main__.py)
  ⎿  Added 6 lines, removed 1 line
       1 -"""Permite `python -m src --input ... --output ... [--politica 
         -...] [--cambio ...]` (DT-003)."""                              
       1 +"""Permite `python -m src calcular --input ... --output ... [--
         +politica ...] [--cambio ...]` (DT-003b).                       
       2  
       3 +O subcomando `calcular` e obrigatorio; delega a `cli.main` (mes
         +ma logica de                                                   
       4 +`python -m src.cli calcular ...`). A forma antiga `python -m sr
         +c --input ...` (sem                                            
       5 +o subcomando) passa a ser erro de uso do argparse (codigo 2).  
       6 +"""                                                            
       7 +                                                               
       8  import sys
       9  
      10  from src.cli import main

● Now T-053 — rewrite tests/test_cli.py for the subcommand + three forms + exit
  2:

● Write(tests\test_cli.py)
  ⎿  Added 66 lines, removed 11 lines
      1 -"""Testes da CLI `calcular` (T-042/T-049), spec 1.4."""         
      1 +"""Testes da CLI `calcular` (T-042/T-049/T-053), spec 1.4 + plan
        +o 1.5.                                                          
      2  
      3 +`calcular` e um subcomando do argparse: `main(["calcular", ...])
        +`. O wrapper                                                    
      4 +`main_console(["--input", ...])` injeta o subcomando para a linh
        +a instalada.                                                    
      5 +"""                                                             
      6 +                                                                
      7  import json
      8  import subprocess
      9  import sys
     ...
      18  
      19  def test_cli_gera_saida(caminho_exemplo, tmp_path):
      20      saida = tmp_path / "resultado.json"
      17 -    codigo = cli.main(["--input", str(caminho_exemplo), "--outp
         -ut", str(saida)])                                              
      21 +    codigo = cli.main(["calcular", "--input", str(caminho_exemp
         +lo), "--output", str(saida)])                                  
      22      assert codigo == 0
      23      dados = json.loads(saida.read_text(encoding="utf-8"))
      24      assert dados["total_reembolso_geral"] == 351.43
     ...
      27  def test_cli_sem_em_viagem(caminho_exemplo, tmp_path):
      28      # Nao ha mais flag --em-viagem; a saida nao tem o campo em_
          viagem.
      29      saida = tmp_path / "resultado.json"
      26 -    codigo = cli.main(["--input", str(caminho_exemplo), "--outp
         -ut", str(saida)])                                              
      30 +    codigo = cli.main(["calcular", "--input", str(caminho_exemp
         +lo), "--output", str(saida)])                                  
      31      assert codigo == 0
      32      dados = json.loads(saida.read_text(encoding="utf-8"))
      33      assert "em_viagem" not in dados
     ...
      36  def test_cli_em_viagem_flag_rejeitada(caminho_exemplo, tmp_path
          ):
      37      saida = tmp_path / "resultado.json"
      38      with pytest.raises(SystemExit) as exc:
      35 -        cli.main(["--input", str(caminho_exemplo), "--output", 
         -str(saida), "--em-viagem"])                                    
      39 +        cli.main(                                              
      40 +            ["calcular", "--input", str(caminho_exemplo), "--ou
         +tput", str(saida), "--em-viagem"]                              
      41 +        )                                                      
      42      assert exc.value.code == 2  # argparse: argumento desconhec
          ido
      43  
      44  
      45  def test_cli_defaults_empacotados(caminho_envelope, tmp_path):
      46      # Sem --politica/--cambio usa os arquivos empacotados em sr
          c/informacoes_externas.
      47      saida = tmp_path / "resultado.json"
      42 -    codigo = cli.main(["--input", str(caminho_envelope), "--out
         -put", str(saida)])                                             
      48 +    codigo = cli.main(["calcular", "--input", str(caminho_envel
         +ope), "--output", str(saida)])                                 
      49      assert codigo == 0
      50      dados = json.loads(saida.read_text(encoding="utf-8"))
      51      assert dados["total_reembolso_geral"] == 1228.72
     ...
      55      saida = tmp_path / "resultado.json"
      56      codigo = cli.main(
      57          [
      58 +            "calcular",                                        
      59              "--input", str(caminho_exemplo),
      60              "--output", str(saida),
      61              "--cambio", str(tmp_path / "nao-existe.json"),
     ...
      70      saida = tmp_path / "resultado.json"
      71      codigo = cli.main(
      72          [
      73 +            "calcular",                                        
      74              "--input", str(caminho_exemplo),
      75              "--output", str(saida),
      76              "--politica", str(tmp_path / "nao-existe.json"),
     ...
      82  
      83  def test_cli_exit_code_input_inexistente(tmp_path, capsys):
      84      saida = tmp_path / "resultado.json"
      77 -    codigo = cli.main(["--input", str(tmp_path / "nao-existe.js
         -on"), "--output", str(saida)])                                 
      85 +    codigo = cli.main(                                         
      86 +        ["calcular", "--input", str(tmp_path / "nao-existe.json
         +"), "--output", str(saida)]                                    
      87 +    )                                                          
      88      assert codigo == 1
      89      assert not saida.exists()
      90      assert capsys.readouterr().err
     ...
       92  
       93  def test_cli_falta_argumento_exit_2(caminho_exemplo):
       94      with pytest.raises(SystemExit) as exc:
       85 -        cli.main(["--input", str(caminho_exemplo)])  # falta -
          --output                                                       
       95 +        cli.main(["calcular", "--input", str(caminho_exemplo)]
          +)  # falta --output                                           
       96      assert exc.value.code == 2
       97  
       98  
       89 -def test_python_m_src(caminho_exemplo, tmp_path):             
       99 +def test_cli_sem_subcomando_exit_2(caminho_exemplo, tmp_path):
      100 +    # Faltar o subcomando `calcular` e erro de uso do argparse
          + (codigo 2).                                                  
      101      saida = tmp_path / "resultado.json"
      102 +    with pytest.raises(SystemExit) as exc:                    
      103 +        cli.main(["--input", str(caminho_exemplo), "--output",
          + str(saida)])                                                 
      104 +    assert exc.value.code == 2                                
      105 +    with pytest.raises(SystemExit) as exc_vazio:              
      106 +        cli.main([])                                          
      107 +    assert exc_vazio.value.code == 2                          
      108 +                                                              
      109 +                                                              
      110 +def test_main_console_injeta_subcomando(caminho_exemplo, tmp_p
          +ath):                                                         
      111 +    # O wrapper aceita a linha com uma so palavra (sem "calcul
          +ar") e injeta o subcomando.                                   
      112 +    saida = tmp_path / "resultado.json"                       
      113 +    codigo = cli.main_console(["--input", str(caminho_exemplo)
          +, "--output", str(saida)])                                    
      114 +    assert codigo == 0                                        
      115 +    dados = json.loads(saida.read_text(encoding="utf-8"))     
      116 +    assert dados["total_reembolso_geral"] == 351.43           
      117 +                                                              
      118 +                                                              
      119 +def _total_via_subprocess(modulo: str, caminho_exemplo, saida:
          + Path) -> float:                                              
      120      proc = subprocess.run(
       92 -        [sys.executable, "-m", "src", "--input", str(caminho_e
          -xemplo), "--output", str(saida)],                             
      121 +        [                                                     
      122 +            sys.executable, "-m", modulo, "calcular",         
      123 +            "--input", str(caminho_exemplo), "--output", str(s
          +aida),                                                        
      124 +        ],                                                    
      125          cwd=_RAIZ,
      126          capture_output=True,
      127          text=True,
      128      )
      129      assert proc.returncode == 0, proc.stderr
       98 -    dados = json.loads(saida.read_text(encoding="utf-8"))     
       99 -    assert dados["total_reembolso_geral"] == 351.43           
      130 +    return json.loads(saida.read_text(encoding="utf-8"))["tota
          +l_reembolso_geral"]                                           
      131 +                                                              
      132 +                                                              
      133 +def test_python_m_src_cli(caminho_exemplo, tmp_path):         
      134 +    # Forma primaria do pedido: `python -m src.cli calcular --
          +input ... --output ...`.                                      
      135 +    total = _total_via_subprocess("src.cli", caminho_exemplo, 
          +tmp_path / "resultado.json")                                  
      136 +    assert total == 351.43                                    
      137 +                                                              
      138 +                                                              
      139 +def test_python_m_src(caminho_exemplo, tmp_path):             
      140 +    # Forma equivalente via pacote: `python -m src calcular ..
          +.`.                                                           
      141 +    total = _total_via_subprocess("src", caminho_exemplo, tmp_
          +path / "resultado.json")                                      
      142 +    assert total == 351.43                                    
      143 +                                                              
      144 +                                                              
      145 +def test_tres_formas_mesma_saida(caminho_exemplo, tmp_path):  
      146 +    # main(subcomando), main_console(wrapper) e `python -m src
          +.cli calcular` coincidem.                                     
      147 +    s1 = tmp_path / "s1.json"                                 
      148 +    s2 = tmp_path / "s2.json"                                 
      149 +    s3 = tmp_path / "s3.json"                                 
      150 +    assert cli.main(["calcular", "--input", str(caminho_exempl
          +o), "--output", str(s1)]) == 0                                
      151 +    assert cli.main_console(["--input", str(caminho_exemplo), 
          +"--output", str(s2)]) == 0                                    
      152 +    _total_via_subprocess("src.cli", caminho_exemplo, s3)     
      153 +    a = s1.read_text(encoding="utf-8")                        
      154 +    assert a == s2.read_text(encoding="utf-8") == s3.read_text
          +(encoding="utf-8")                                            

● Now T-054 — update CLAUDE.md. Let me read the exact run-command lines.

  Read 1 file (ctrl+o to expand)
● Update(CLAUDE.md)
  ⎿  Added 4 lines, removed 2 lines
      35  ## Stack e comandos
      36  
      37  - Linguagem: Python 3.13 (somente stdlib em runtime; sem depend
          ências externas)
      38 -- Rodar: `calcular --input despesas.json --output resultado.jso
         -n [--politica p.json] [--cambio c.json]`                       
      39 -  (em dev, sem instalar: `python -m src --input ... --output ..
         -.`). Sem `--politica`/`--cambio`,                              
      38 +- Rodar (dev, sem instalar): `python -m src.cli calcular --inpu
         +t despesas.json --output resultado.json [--politica p.json] [--
         +cambio c.json]`                                                
      39 +  — `calcular` é um **subcomando** do argparse. Equivalentes: `
         +python -m src calcular ...` e, se                              
      40 +  instalado, o console script `calcular --input ... --output ..
         +.` (wrapper injeta o subcomando).                              
      41 +  A forma antiga `python -m src --input ...` (sem o subcomando)
         + não vale mais. Sem `--politica`/`--cambio`,                   
      42    usa a política e o câmbio empacotados em `src/informacoes_ext
          ernas/`. Não há mais `--em-viagem`:
      43    viagem é derivada por registro (moeda ≠ base, RN-009).
      44  - Instalar (dev): `pip install -e ".[dev]"` (cria o comando `ca
          lcular` e instala `pytest`)

● Now let me run the test suite to validate. First find the working Python
  interpreter (memory notes the Store stubs are broken).

  Ran 1 shell command (ctrl+o to expand)

● All 13 CLI tests pass. Now the full suite to confirm nothing else broke:

  Ran 1 shell command (ctrl+o to expand)

● Full suite green (112 passed). Let me verify the user's exact target command
  works end-to-end:

  Ran 1 shell command (ctrl+o to expand)

● The target command works (exit 0, total_reembolso_geral = 351.43); missing
  subcommand yields exit 2 as designed. Now marking T-050…T-054 complete in
  tasks.md:

  Ran 1 shell command (ctrl+o to expand)

● All tasks done and marked [X]. No post-execution hooks
  (.specify/extensions.yml absent) — skipped.

  /speckit-implement concluído — Fase 11 implementada

  O sistema agora roda pelo subcomando calcular, exatamente como pedido:

  python -m src.cli calcular --input exemplos\despesas-exemplo.json --output
  resultado.json
  → exit 0, total_reembolso_geral = 351.43. Sem o subcomando → erro de uso (exit
  2).

  Tarefas concluídas (T-050 → T-054)

  Task: T-050
  Arquivo: src/cli.py
  Mudança: add_subparsers(dest="comando", required=True) + subparser calcular
  (com --input/--output/--politica/--cambio); _executa_calcular; wrapper
  main_console que injeta o subcomando; docstring de exit codes
  ────────────────────────────────────────
  Task: T-051
  Arquivo: pyproject.toml
  Mudança: calcular = "src.cli:main_console"
  ────────────────────────────────────────
  Task: T-052
  Arquivo: src/__main__.py
  Mudança: docstring → python -m src calcular … (delega a cli.main)
  ────────────────────────────────────────
  Task: T-053
  Arquivo: tests/test_cli.py
  Mudança: 13 testes: 3 formas equivalentes, wrapper, exit 2 sem subcomando,
  equivalência de saída; testes antigos migrados para o subcomando
  ────────────────────────────────────────
  Task: T-054
  Arquivo: CLAUDE.md
  Mudança: seção "Stack e comandos" usa o subcomando; removida a forma python -m
   
  src --input …

  Validação

  - pytest completo: 112 passed (13 em test_cli.py).
  - As três formas produzem saída idêntica: python -m src.cli calcular …
  (primária), python -m src calcular …, e o console calcular … via wrapper
  (main_console).
  - Núcleo puro intacto — a mudança ficou toda na casca de I/O
  (cli.py/__main__.py); nenhuma regra de negócio tocada (sem RN nova).

  Arquivos alterados nesta rodada

  src/cli.py, src/__main__.py, pyproject.toml, tests/test_cli.py, CLAUDE.md,
  specs/001-motor-reembolso/tasks.md (+ artefatos de plano já ajustados antes:
  plan.md, contracts/cli-contract.md, quickstart.md, research.md).

  Cada task tem um **Commit** sugerido no tasks.md (ex.: feat(T-050): calcular 
  como subcomando do argparse (DT-003b)). Não commitei — quer que eu crie os
  commits (um por task, ou um único feat(T-050 - T-054))?

✻ Brewed for 2m 57s