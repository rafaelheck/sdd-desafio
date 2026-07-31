 ▐▛███▜▌   Claude Code v2.1.220
▝▜█████▛▘  Opus 4.8 · Claude Pro
  ▘▘ ▝▝    ~\Área de Trabalho\Teste SDD\sdd-desafio


❯ /speckit-implement                                                            

● I'll start by following the speckit-implement workflow. Let me check for
  extension hooks and run the prerequisites script.

  Read 1 file (ctrl+o to expand)

● No extensions file, so I'll skip hook checking. Let me run the prerequisites
  script.

  Ran 1 shell command (ctrl+o to expand)

● Let me check for checklists and load the key implementation docs.

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● Let me check the checklists status and read the key design documents.

  Read 2 files (ctrl+o to expand)

● Now let me tally the checklist status.

  Checklist status:

  ┌─────────────────┬───────┬───────────┬────────────┬────────┐
  │    Checklist    │ Total │ Completed │ Incomplete │ Status │
  ├─────────────────┼───────┼───────────┼────────────┼────────┤
  │ requirements.md │ 16    │ 16        │ 0          │ ✓ PASS │
  ├─────────────────┼───────┼───────────┼────────────┼────────┤
  │ spec-gate.md    │ 42    │ 41        │ 1          │ ✗ FAIL │
  └─────────────────┴───────┴───────────┴────────────┴────────┘

  The one incomplete item is CHK001 in spec-gate.md — a minor, 
  consciously-documented gap: the obligatoriness of politica-v4.json category
  fields (limite/periodicidade) isn't formally declared in spec §4, but it's
  mitigated by §10 ("assume política bem formada"). It doesn't block
  implementation.

  There's also a flagged CHK041 action (marked [x] but noted as high-priority):
  CLAUDE.md was said to be outdated re: câmbio/--em-viagem. Reading the current
  CLAUDE.md, it has already been corrected — it now documents
  --politica/--cambio, câmbio via cambio.json (RN-018..RN-020), and viagem por
  registro. So that action is resolved.

  Per the workflow, since a checklist has an incomplete item, I need to check
  with you before proceeding.

● User answered Claude's questions:
  ⎿  · spec-gate.md has 1 incomplete item (CHK001 — a documented minor gap about
     política field obligatoriness, already mitigated by spec §10). Proceed 
     with implementing Fases 6–10 (T-028..T-049)? → Proceed with implementation

● Proceeding. Let me load the full implementation context and the current source
  code.

  Read 3 files (ctrl+o to expand)

● Let me read the rest of the spec plus the remaining design docs and current
  source.

  Read 2 files (ctrl+o to expand)

● Now the contracts and the current source code.

  Searched for 3 patterns, read 2 files (ctrl+o to expand)

● The external data files and envelope example already exist. Let me read the
  current source code and the external data files.

  Read 7 files (ctrl+o to expand)

● Now the external data files and example inputs.

  Read 3 files (ctrl+o to expand)

● Now the existing tests and the exemplo input, plus the test helper.

  Read 4 files (ctrl+o to expand)

● Let me read the remaining test files to understand what needs rewriting.

  Read 8 files (ctrl+o to expand)

● I now have the complete picture. This is a substantial rewrite from spec
  1.1/D-004 state to spec 1.4 (external política + câmbio). Let me check
  pyproject.toml and verify the test baseline before starting.
  Read 1 file, ran 1 shell command (ctrl+o to expand)

● Python isn't on PATH under that name. Let me locate it.

  Ran 2 shell commands (ctrl+o to expand)

● Found Python 3.13.14. Let me set up a convenient variable and run the baseline
  tests.

  Ran 3 shell commands (ctrl+o to expand)

● Baseline is green (72 passed) at the D-004 state. I've now fully absorbed the
  spec, plan, data-model, contracts, quickstart, and current code.

  The work is Fases 6–10 (T-028..T-049): a rewrite from
  fixed-constants/--em-viagem to external politica-v4.json + cambio.json,
  dynamic categories, per-record travel by currency, and currency conversion. I
  verified both goldens by hand against my planned design (exemplo → 351.43;
  envelope → 1228.72). Let me set up task tracking and begin implementing.

  Let me start with the foundation — T-028 modelo.py and T-029 politica.py.

● Write(src\modelo.py)
  ⎿  Added 77 lines, removed 18 lines
       1 -"""Modelo de dados do nucleo puro (dataclasses + enums).       
       1 +"""Modelo de dados do nucleo puro (dataclasses + enums) — spec 
         +1.4.                                                           
       2  
       3  Valores monetarios sao `Decimal` com 2 casas. Nomes de campo de
           saida seguem a
       4  Secao 4 da spec. Ver `data-model.md`.
       5 +                                                               
       6 +Nao ha mais enum `Categoria`: as categorias sao dinamicas por c
         +entro de custo                                                 
       7 +(RN-001/RN-015), lidas da politica externa. Tambem nao ha mais 
         +campo `em_viagem`                                              
       8 +na saida: viagem e por registro, derivada da moeda (RN-009).   
       9  """
      10  
      11  from __future__ import annotations
     ...
      16  from enum import Enum
      17  
      18  
      15 -class Categoria(str, Enum):                                    
      16 -    """Categorias validas (RN-001)."""                         
      17 -                                                               
      18 -    ALIMENTACAO = "alimentacao"                                
      19 -    TRANSPORTE_URBANO = "transporte_urbano"                    
      20 -    HOSPEDAGEM = "hospedagem"                                  
      21 -                                                               
      22 -                                                               
      19  class Motivo(str, Enum):
      24 -    """Motivos de recusa — texto exato da spec (RN-006/007/008/
         -010/013, AMB-011)."""                                          
      20 +    """Motivos de recusa — texto exato da spec.                
      21  
      22 +    O motivo de categoria com limite <= 0 (RN-017) NAO e um val
         +or deste enum: e a                                             
      23 +    `observacao` da `CategoriaConfig` (texto livre) ou, na ause
         +ncia dela,                                                     
      24 +    `CATEGORIA_NAO_APLICAVEL`.                                 
      25 +    """                                                        
      26 +                                                               
      27      CATEGORIA_NAO_APLICAVEL = "categoria não aplicável"
      28      DATA_FORA_COMPETENCIA = "data fora da competência"
      29      REGISTRO_DUPLICADO = "registro duplicado"
      30      SEM_NOTA_FISCAL = "sem nota fiscal obrigatória"
      31      VALOR_INVALIDO = "valor inválido"
      32      REGISTRO_INVALIDO = "registro inválido"
      33 +    CAMBIO_NAO_IDENTIFICADO = "cambio não identificado"  # RN-0
         +20                                                             
      34  
      35  
      36 +def motivo_texto(motivo: Motivo | str) -> str:                 
      37 +    """Texto do motivo, seja ele um `Motivo` (enum) ou a `obser
         +vacao` (str) da                                                
      38 +    categoria com limite <= 0 (RN-017)."""                     
      39 +    return motivo.value if isinstance(motivo, Motivo) else moti
         +vo                                                             
      40 +                                                               
      41 +                                                               
      42 +# -------------------------------------------------------------
         +-------------- #                                               
      43 +# Entidades da politica externa (politica-v4.json -> puro)     
      44 +# -------------------------------------------------------------
         +-------------- #                                               
      45 +@dataclass(frozen=True)                                        
      46 +class CategoriaConfig:                                         
      47 +    """Configuracao de uma categoria num centro de custo (RN-00
         +4/RN-016/RN-017)."""                                           
      48 +                                                               
      49 +    limite: Decimal                                            
      50 +    periodicidade: str  # "dia" (RN-002) ou "diaria" (RN-003)  
      51 +    observacao: str | None = None                              
      52 +                                                               
      53 +                                                               
      54 +@dataclass(frozen=True)                                        
      55 +class Politica:                                                
      56 +    """Politica externa versionada (RN-015)."""                
      57 +                                                               
      58 +    padrao: dict[str, CategoriaConfig]                         
      59 +    centros_custo: dict[str, dict[str, CategoriaConfig]]       
      60 +    limiar_nf: Decimal  # nota_fiscal_obrigatoria_acima_de (RN-
         +006)                                                           
      61 +    acrescimo_viagem_pct: Decimal  # acrescimo_em_viagem_percen
         +tual (RN-009)                                                  
      62 +                                                               
      63 +                                                               
      64 +# -------------------------------------------------------------
         +-------------- #                                               
      65 +# Entidade do cambio externo (cambio.json -> puro)             
      66 +# -------------------------------------------------------------
         +-------------- #                                               
      67 +@dataclass(frozen=True)                                        
      68 +class Cambio:                                                  
      69 +    """Tabela de cambio externa (RN-018/RN-019)."""            
      70 +                                                               
      71 +    moeda_base: str  # normalizada trim+upper                  
      72 +    taxas: dict[date, dict[str, Decimal]]  # data -> {MOEDA: fa
         +tor}                                                           
      73 +                                                               
      74 +                                                               
      75 +# -------------------------------------------------------------
         +-------------- #                                               
      76 +# Entidades de entrada                                         
      77 +# -------------------------------------------------------------
         +-------------- #                                               
      78  @dataclass
      79  class Colaborador:
      80      """Identificacao do colaborador (eco do input)."""
     ...
       95  
       96  @dataclass
       97  class Despesa:
       54 -    """Despesa normalizada (RN-011, RN-001)."""               
       98 +    """Despesa normalizada (RN-011, RN-001, RN-018).          
       99  
      100 +    `valor_origem` e o valor na moeda do registro (2 casas); `
          +valor_base` e o valor                                         
      101 +    ja convertido para a `moeda_base` do cambio (`None` ate a 
          +conversao, ou se                                              
      102 +    "cambio não identificado"). `em_viagem` deriva da moeda (R
          +N-009).                                                       
      103 +    """                                                       
      104 +                                                              
      105      id: str
      106      data: date
      107      categoria: str
      108      categoria_norm: str
      109      descricao: str
      110      fornecedor: str
       62 -    valor: Decimal                                            
      111 +    valor_origem: Decimal                                     
      112 +    moeda_norm: str | None                                    
      113      tem_nota_fiscal: bool
      114 +    em_viagem: bool = False                                   
      115 +    valor_base: Decimal | None = None                         
      116  
      117      def chave_duplicidade(self) -> tuple:
       66 -        """Chave de negocio para duplicidade (RN-008) — sem `i
          -d` (AMB-002)."""                                              
      118 +        """Chave de negocio para duplicidade (RN-008) — sem `i
          +d` (AMB-002), com                                             
      119 +        `valor`/`moeda` de ORIGEM (antes da conversao)."""    
      120          return (
      121              self.data,
      122              self.categoria_norm,
      123              self.descricao,
      124              self.fornecedor,
       72 -            self.valor,                                       
      125 +            self.valor_origem,                                
      126 +            self.moeda_norm,                                  
      127              self.tem_nota_fiscal,
      128          )
      129  
      130  
      131 +# ------------------------------------------------------------
          +--------------- #                                             
      132 +# Entidades de saida                                          
      133 +# ------------------------------------------------------------
          +--------------- #                                             
      134  @dataclass
      135  class Reprovacao:
       79 -    """Despesa recusada, com o motivo do primeiro gate que fal
          -hou."""                                                       
      136 +    """Despesa recusada, com o motivo do primeiro gate que fal
          +hou.                                                          
      137  
      138 +    `motivo` e um `Motivo` (enum) ou a `observacao` (str) da c
          +ategoria com limite                                           
      139 +    <= 0 (RN-017)."""                                         
      140 +                                                              
      141      id: str
       82 -    motivo: Motivo                                            
      142 +    motivo: Motivo | str                                      
      143      categoria_informada: str | None = None
      144  
      145  
     ...
      156  
      157  @dataclass
      158  class Resultado:
       99 -    """Raiz da saida (Secao 4 da spec)."""                    
      159 +    """Raiz da saida (Secao 4 da spec 1.4). Sem campo `em_viag
          +em`."""                                                       
      160  
      161      colaborador: Colaborador
      162      competencia: str
      163      periodo: Periodo
      104 -    em_viagem: bool                                           
      164      categorias: dict[str, ResultadoCategoria]
      165      reprovadas_sem_categoria: list[Reprovacao]
      166      total_reembolso_geral: Decimal

● Write(src\politica.py)
  ⎿  Added 55 lines, removed 21 lines
       1 -"""Constantes de politica de reembolso (Secao 4 da spec / plan.
         -md secao 4).                                                   
       1 +"""Construcao das fontes externas como estruturas puras (spec 1
         +.4 / DT-008).                                                  
       2  
       3 -A politica muda em ciclos de meses e e versionada junto do codi
         -go; por isso vive                                              
       4 -como constantes nomeadas, nao como config externa. Todos os val
         -ores monetarios                                                
       5 -sao `Decimal` para aritmetica exata (DT-001).                  
       3 +Nao ha mais constantes de limite/categoria embutidas: categoria
         +s, limites,                                                    
       4 +periodicidade, limiar de NF e acrescimo de viagem vem de `polit
         +ica-v4.json`                                                   
       5 +(RN-015); moeda base e taxas vem de `cambio.json` (RN-018). Est
         +as funcoes sao                                                 
       6 +puras (dict -> estrutura); a leitura de arquivo vive em `io_jso
         +n.py`.                                                         
       7 +                                                               
       8 +Todos os valores monetarios e taxas sao `Decimal` (lidos com   
       9 +`parse_float=Decimal`), nunca `float` (DT-001).                
      10  """
      11  
      12 +from __future__ import annotations                             
      13 +                                                               
      14 +from datetime import date                                      
      15  from decimal import Decimal
      16  
      10 -# Tetos diarios por categoria agregada (RN-002, RN-003).       
      11 -LIMITES_DIARIOS: dict[str, Decimal] = {                        
      12 -    "alimentacao": Decimal("60"),                              
      13 -    "transporte_urbano": Decimal("80"),                        
      14 -}                                                              
      17 +from src.modelo import Cambio, CategoriaConfig, Politica       
      18  
      16 -# Teto de hospedagem por registro, nao por diaria (RN-004 / AMB
         --006).                                                         
      17 -LIMITE_HOSPEDAGEM = Decimal("250")                             
      19 +# Precisao monetaria: 2 casas (RN-011).                        
      20 +CASAS_DECIMAIS = Decimal("0.01")                               
      21  
      19 -# Nota fiscal exigida para valores estritamente acima deste lim
         -iar (RN-006).                                                  
      20 -LIMIAR_NOTA_FISCAL = Decimal("100")                            
      22  
      22 -# Multiplicador aplicado somente aos tetos quando em viagem (RN
         --009).                                                         
      23 -MULTIPLICADOR_VIAGEM = Decimal("1.5")                          
      23 +def _categoria_de_dict(bruto: dict) -> CategoriaConfig:        
      24 +    """Converte um objeto de categoria da politica em `Categori
         +aConfig`."""                                                   
      25 +    observacao = bruto.get("observacao")                       
      26 +    return CategoriaConfig(                                    
      27 +        limite=Decimal(bruto["limite"]),                       
      28 +        periodicidade=bruto["periodicidade"],                  
      29 +        observacao=observacao if isinstance(observacao, str) el
         +se None,                                                       
      30 +    )                                                          
      31  
      25 -# Categorias reembolsaveis (RN-001).                           
      26 -CATEGORIAS_VALIDAS: frozenset[str] = frozenset(                
      27 -    {"alimentacao", "transporte_urbano", "hospedagem"}         
      28 -)                                                              
      32  
      30 -# Precisao monetaria: 2 casas (RN-011).                        
      31 -CASAS_DECIMAIS = Decimal("0.01")                               
      33 +def _conjunto_de_dict(bruto: dict) -> dict[str, CategoriaConfig
         +]:                                                             
      34 +    """Converte um conjunto de categorias (padrao ou de um cent
         +ro) em dict."""                                                
      35 +    return {nome: _categoria_de_dict(cfg) for nome, cfg in brut
         +o.items()}                                                     
      36 +                                                               
      37 +                                                               
      38 +def politica_de_dict(dados: dict) -> Politica:                 
      39 +    """RN-015 — constroi a `Politica` a partir do dict de `poli
         +tica-v4.json`.                                                 
      40 +                                                               
      41 +    A `moeda_base` de `politica-v4.json`, se houver, e ignorada
         + (RN-018): a moeda                                             
      42 +    base de referencia e sempre a do `cambio.json`."""         
      43 +    padrao = _conjunto_de_dict(dados["padrao"])                
      44 +    centros_custo = {                                          
      45 +        cc: _conjunto_de_dict(conjunto)                        
      46 +        for cc, conjunto in dados.get("centros_custo", {}).item
         +s()                                                            
      47 +    }                                                          
      48 +    return Politica(                                           
      49 +        padrao=padrao,                                         
      50 +        centros_custo=centros_custo,                           
      51 +        limiar_nf=Decimal(dados["nota_fiscal_obrigatoria_acima_
         +de"]),                                                         
      52 +        acrescimo_viagem_pct=Decimal(dados["acrescimo_em_viagem
         +_percentual"]),                                                
      53 +    )                                                          
      54 +                                                               
      55 +                                                               
      56 +def cambio_de_dict(dados: dict) -> Cambio:                     
      57 +    """RN-018 — constroi o `Cambio` a partir do dict de `cambio
         +.json`.                                                        
      58 +                                                               
      59 +    Datas viram `date`; moedas sao normalizadas trim+upper; tax
         +as ficam `Decimal`."""                                         
      60 +    taxas: dict[date, dict[str, Decimal]] = {}                 
      61 +    for data_str, cotacoes in dados.get("taxas", {}).items():  
      62 +        taxas[date.fromisoformat(data_str)] = {                
      63 +            moeda.strip().upper(): Decimal(fator) for moeda, fa
         +tor in cotacoes.items()                                        
      64 +        }                                                      
      65 +    return Cambio(moeda_base=dados["moeda_base"].strip().upper(
         +), taxas=taxas)                                                

● Now the core rules — T-031..T-039 in regras.py (rewritten for spec 1.4):

● Write(src\regras.py)
  ⎿  Added 175 lines, removed 82 lines
       1 -"""Regras de negocio — uma funcao pura por RN (DT-002).        
       1 +"""Regras de negocio — uma funcao pura por RN (DT-002), spec 1.
         +4.                                                             
       2  
       3 -Os gates de validacao retornam `Motivo | None` (motivo da recus
         -a, ou `None` se a                                              
       4 -despesa passa). As funcoes de teto e agregacao calculam valores
         - monetarios. Nada                                              
       5 -aqui faz I/O; `calculo.py` apenas orquestra estas funcoes na or
         -dem da Secao 8.                                                
       3 +Os gates de validacao retornam `Motivo | str | None` (motivo da
         + recusa, ou `None`                                             
       4 +se a despesa passa). As funcoes de conversao, taxa, teto e agre
         +gacao calculam                                                 
       5 +valores monetarios. Nada aqui faz I/O; `calculo.py` apenas orqu
         +estra estas funcoes                                            
       6 +na ordem da Secao 8. Categorias, limites e taxas vem sempre de 
         +`Politica`/`Cambio`                                            
       7 +injetados (RN-004/RN-015/RN-018) — nenhuma categoria e conhecid
         +a em codigo.                                                   
       8  """
       9  
      10  from __future__ import annotations
     ...
      12  from datetime import date
      13  from decimal import ROUND_HALF_UP, Decimal
      14  
      13 -from src.modelo import Despesa, Motivo, Periodo, Reprovacao, Re
         -sultadoCategoria                                               
      14 -from src.politica import (                                     
      15 -    CASAS_DECIMAIS,                                            
      16 -    CATEGORIAS_VALIDAS,                                        
      17 -    LIMIAR_NOTA_FISCAL,                                        
      18 -    LIMITE_HOSPEDAGEM,                                         
      19 -    LIMITES_DIARIOS,                                           
      20 -    MULTIPLICADOR_VIAGEM,                                      
      15 +from src.modelo import (                                       
      16 +    Cambio,                                                    
      17 +    CategoriaConfig,                                           
      18 +    Despesa,                                                   
      19 +    Motivo,                                                    
      20 +    Periodo,                                                   
      21 +    Politica,                                                  
      22 +    ResultadoCategoria,                                        
      23  )
      24 +from src.politica import CASAS_DECIMAIS                        
      25  
      26  # Campos de negocio obrigatorios em cada registro de despesa (R
          N-013).
      27  CAMPOS_OBRIGATORIOS: tuple[str, ...] = (
     ...
      34      "tem_nota_fiscal",
      35  )
      36  
      34 -# Ordem fixa das categorias na saida (determinismo — R-004).   
      35 -ORDEM_CATEGORIAS: tuple[str, ...] = (                          
      36 -    "alimentacao",                                             
      37 -    "transporte_urbano",                                       
      38 -    "hospedagem",                                              
      39 -)                                                              
      37  
      41 -                                                               
      38  def _quantiza(valor: Decimal) -> Decimal:
      39      """Arredonda para 2 casas, meio-para-cima (RN-011)."""
      40      return valor.quantize(CASAS_DECIMAIS, ROUND_HALF_UP)
     ...
      45  # -------------------------------------------------------------
          -------------- #
      46  def valida_estrutura(bruto: object) -> Motivo | None:
      47      """RN-013 — campos obrigatorios presentes e tipados, `valor
          ` numerico, `data`
      52 -    parseavel. Retorna `Motivo.REGISTRO_INVALIDO` ou `None`."""
      48 +    parseavel, `moeda` (se presente) textual. Retorna `REGISTRO
         +_INVALIDO` ou `None`.                                          
      49 +                                                               
      50 +    `moeda` ausente, `null` ou vazio apos `trim` NAO e invalido
         + (conta como sem                                               
      51 +    moeda, RN-018); `moeda` de tipo nao-textual (numero, boolea
         +no, objeto) e                                                  
      52 +    "registro inválido"."""                                    
      53      if not isinstance(bruto, dict):
      54          return Motivo.REGISTRO_INVALIDO
      55  
     ...
      69      if isinstance(valor, bool) or not isinstance(valor, (int, f
          loat, Decimal)):
      70          return Motivo.REGISTRO_INVALIDO
      71  
      72 +    # `moeda` e opcional; se presente e nao-nula, deve ser text
         +o (RN-013/RN-018).                                             
      73 +    moeda = bruto.get("moeda")                                 
      74 +    if moeda is not None and not isinstance(moeda, str):       
      75 +        return Motivo.REGISTRO_INVALIDO                        
      76 +                                                               
      77      try:
      78          date.fromisoformat(bruto["data"])
      79      except (ValueError, TypeError):
     ...
       83  
       84  
       85  # ------------------------------------------------------------
           --------------- #
       81 -# Passo 2 — Normalizacao (RN-011, RN-001)                     
       86 +# Passo 3 — Normalizacao (RN-011, RN-001, RN-018)             
       87  # ------------------------------------------------------------
           --------------- #
       83 -def normaliza_despesa(bruto: dict) -> Despesa:                
       84 -    """RN-011/RN-001 — arredonda `valor` a 2 casas (half-up) e
          - deriva                                                       
       85 -    `categoria_norm` (`strip().lower()`). Assume estrutura ja 
          -validada."""                                                  
       88 +def _norma_moeda(bruto: dict) -> str | None:                  
       89 +    """Moeda normalizada trim+upper; `None` se ausente/`null`/
          +vazio (RN-018)."""                                            
       90 +    moeda = bruto.get("moeda")                                
       91 +    if not isinstance(moeda, str):                            
       92 +        return None                                           
       93 +    return moeda.strip().upper() or None                      
       94 +                                                              
       95 +                                                              
       96 +def normaliza_despesa(bruto: dict, cambio: Cambio) -> Despesa:
       97 +    """RN-011/RN-001/RN-018 — arredonda `valor` a 2 casas (hal
          +f-up), deriva                                                 
       98 +    `categoria_norm` (`strip().lower()`), `moeda_norm` (`strip
          +().upper()`) e o                                              
       99 +    status de viagem (moeda != base -> viagem, RN-009). Assume
          + estrutura validada.                                          
      100 +                                                              
      101 +    Nao converte o valor: `valor_base` e preenchido depois por
          + `valida_cambio`."""                                          
      102      valor_bruto = bruto["valor"]
      103      if isinstance(valor_bruto, float):
      104          # Guarda-costas: valores devem chegar como Decimal (pa
           rse_float=Decimal),
      105          # mas se vier float converte via texto para nao herdar
            erro binario.
      106          valor_bruto = Decimal(str(valor_bruto))
       91 -    valor = _quantiza(Decimal(valor_bruto))                   
      107 +    valor_origem = _quantiza(Decimal(valor_bruto))            
      108  
      109 +    moeda_norm = _norma_moeda(bruto)                          
      110 +    em_viagem = moeda_norm is not None and moeda_norm != cambi
          +o.moeda_base                                                  
      111 +                                                              
      112      categoria = bruto["categoria"]
      113      return Despesa(
      114          id=bruto["id"],
     ...
      117          categoria_norm=categoria.strip().lower(),
      118          descricao=bruto["descricao"],
      119          fornecedor=bruto["fornecedor"],
      101 -        valor=valor,                                          
      120 +        valor_origem=valor_origem,                            
      121 +        moeda_norm=moeda_norm,                                
      122          tem_nota_fiscal=bruto["tem_nota_fiscal"],
      123 +        em_viagem=em_viagem,                                  
      124      )
      125  
      126  
      127  # ------------------------------------------------------------
           --------------- #
      107 -# Passo 3 — Deduplicacao (RN-008, AMB-002, D-002)             
      128 +# Passo 2/4 — Resolucao do centro de custo e categoria valida 
          +(RN-015, RN-001)                                              
      129  # ------------------------------------------------------------
           --------------- #
      109 -def deduplica(despesas: list[Despesa]) -> list[tuple[Despesa, 
          -Motivo | None]]:                                              
      110 -    """RN-008 — colapsa por chave de negocio (sem `id`), mante
          -ndo a 1a ocorrencia.                                          
      111 -    Cada copia seguinte recebe `Motivo.REGISTRO_DUPLICADO`."""
      112 -    vistas: set[tuple] = set()                                
      113 -    resultado: list[tuple[Despesa, Motivo | None]] = []       
      114 -    for despesa in despesas:                                  
      115 -        chave = despesa.chave_duplicidade()                   
      116 -        if chave in vistas:                                   
      117 -            resultado.append((despesa, Motivo.REGISTRO_DUPLICA
          -DO))                                                          
      118 -        else:                                                 
      119 -            vistas.add(chave)                                 
      120 -            resultado.append((despesa, None))                 
      121 -    return resultado                                          
      130 +def resolve_conjunto(                                         
      131 +    politica: Politica, centro_custo: str                     
      132 +) -> dict[str, CategoriaConfig]:                              
      133 +    """RN-015 — conjunto de categorias do centro de custo, ou 
          +`padrao` se o centro                                          
      134 +    nao existe na politica (AMB-013)."""                      
      135 +    return politica.centros_custo.get(centro_custo, politica.p
          +adrao)                                                        
      136  
      137  
      138 +def valida_categoria(                                         
      139 +    despesa: Despesa, conjunto: dict[str, CategoriaConfig]    
      140 +) -> Motivo | None:                                           
      141 +    """RN-001 — `categoria_norm` deve ser uma chave do conjunt
          +o do centro de custo                                          
      142 +    resolvido. Senao "categoria não aplicável"."""            
      143 +    if despesa.categoria_norm not in conjunto:                
      144 +        return Motivo.CATEGORIA_NAO_APLICAVEL                 
      145 +    return None                                               
      146 +                                                              
      147 +                                                              
      148  # ------------------------------------------------------------
           --------------- #
      125 -# Passos 4-7 — Gates por despesa                              
      149 +# Passo 5 — Limite da categoria > 0 (RN-017)                  
      150  # ------------------------------------------------------------
           --------------- #
      127 -def valida_categoria(despesa: Despesa) -> Motivo | None:      
      128 -    """RN-001 — `categoria_norm` deve estar entre as categoria
          -s validas."""                                                 
      129 -    if despesa.categoria_norm not in CATEGORIAS_VALIDAS:      
      130 -        return Motivo.CATEGORIA_NAO_APLICAVEL                 
      151 +def valida_limite_categoria(                                  
      152 +    despesa: Despesa, config: CategoriaConfig                 
      153 +) -> Motivo | str | None:                                     
      154 +    """RN-017 — se `limite <= 0`, recusa com motivo = `observa
          +cao` (ou                                                      
      155 +    "categoria não aplicável" se nao houver). Reportado sob a 
          +propria categoria                                             
      156 +    (AMB-014). Senao `None`."""                               
      157 +    if config.limite <= 0:                                    
      158 +        return config.observacao or Motivo.CATEGORIA_NAO_APLIC
          +AVEL                                                          
      159      return None
      160  
      161  
      162 +# ------------------------------------------------------------
          +--------------- #                                             
      163 +# Passo 6 — Conversao de cambio (RN-018, RN-019, RN-020, AMB-0
          +18)                                                           
      164 +# ------------------------------------------------------------
          +--------------- #                                             
      165 +def taxa_por_data(                                            
      166 +    cambio: Cambio, moeda_norm: str, data: date               
      167 +) -> Decimal | None:                                          
      168 +    """RN-019 — fator de `moeda_norm` na `data`, ou na data ma
          +is proxima que                                                
      169 +    contenha a moeda (menor `abs(dist)` em dias; empate -> men
          +or taxa). `None` se a                                         
      170 +    moeda nao existe em nenhuma data de `taxas` (-> RN-020).""
          +"                                                             
      171 +    candidatas = [                                            
      172 +        (abs((data_taxa - data).days), cotacoes[moeda_norm])  
      173 +        for data_taxa, cotacoes in cambio.taxas.items()       
      174 +        if moeda_norm in cotacoes                             
      175 +    ]                                                         
      176 +    if not candidatas:                                        
      177 +        return None                                           
      178 +    # Menor distancia; em empate, menor taxa (a tupla (dist, t
          +axa) ordena assim).                                           
      179 +    return min(candidatas)[1]                                 
      180 +                                                              
      181 +                                                              
      182 +def converte(valor_origem: Decimal, taxa: Decimal) -> Decimal:
      183 +    """RN-018/AMB-018 — arredonda a origem a 2 casas, multipli
          +ca pela taxa cheia e                                          
      184 +    arredonda o resultado a 2 casas (half-up). A taxa NAO e ar
          +redondada."""                                                 
      185 +    return _quantiza(_quantiza(valor_origem) * taxa)          
      186 +                                                              
      187 +                                                              
      188 +def valida_cambio(despesa: Despesa, cambio: Cambio) -> Motivo 
          +| None:                                                       
      189 +    """RN-018/RN-020 — preenche `despesa.valor_base`. Registro
          + sem moeda ou com                                             
      190 +    moeda = base fica com `valor_base = valor_origem`. Em viag
          +em, converte pela taxa                                        
      191 +    da data (RN-019); se a moeda nao existe em nenhuma data, r
          +etorna                                                        
      192 +    `CAMBIO_NAO_IDENTIFICADO` (e `valor_base` permanece `None`
          +)."""                                                         
      193 +    if not despesa.em_viagem:                                 
      194 +        despesa.valor_base = despesa.valor_origem             
      195 +        return None                                           
      196 +    taxa = taxa_por_data(cambio, despesa.moeda_norm, despesa.d
          +ata)                                                          
      197 +    if taxa is None:                                          
      198 +        return Motivo.CAMBIO_NAO_IDENTIFICADO                 
      199 +    despesa.valor_base = converte(despesa.valor_origem, taxa) 
      200 +    return None                                               
      201 +                                                              
      202 +                                                              
      203 +# ------------------------------------------------------------
          +--------------- #                                             
      204 +# Passo 8 — Periodo (RN-007)                                  
      205 +# ------------------------------------------------------------
          +--------------- #                                             
      206  def valida_periodo(despesa: Despesa, periodo: Periodo) -> Moti
           vo | None:
      207      """RN-007 — `inicio <= data <= fim` inclusive (AMB-009).""
           "
      208      if periodo.inicio <= despesa.data <= periodo.fim:
     ...
      210      return Motivo.DATA_FORA_COMPETENCIA
      211  
      212  
      213 +# ------------------------------------------------------------
          +--------------- #                                             
      214 +# Passo 9 — Valor valido (RN-010)                             
      215 +# ------------------------------------------------------------
          +--------------- #                                             
      216  def valida_valor(despesa: Despesa) -> Motivo | None:
      142 -    """RN-010 — `valor > 0` (AMB-005)."""                     
      143 -    if despesa.valor > 0:                                     
      217 +    """RN-010 — `valor_origem > 0` (AMB-005)."""              
      218 +    if despesa.valor_origem > 0:                              
      219          return None
      220      return Motivo.VALOR_INVALIDO
      221  
      222  
      148 -def valida_nota_fiscal(despesa: Despesa) -> Motivo | None:    
      149 -    """RN-006 — se `valor > LIMIAR_NOTA_FISCAL`, exige nota fi
          -scal (AMB-004)."""                                            
      150 -    if despesa.valor > LIMIAR_NOTA_FISCAL and not despesa.tem_
          -nota_fiscal:                                                  
      223 +# ------------------------------------------------------------
          +--------------- #                                             
      224 +# Passo 10 — Nota fiscal (RN-006), sobre o valor JA convertido
      225 +# ------------------------------------------------------------
          +--------------- #                                             
      226 +def valida_nota_fiscal(despesa: Despesa, limiar: Decimal) -> M
          +otivo | None:                                                 
      227 +    """RN-006 — se o valor convertido (`valor_base`) e estrita
          +mente maior que o                                             
      228 +    limiar, exige nota fiscal. O limiar NAO escala em viagem (
          +AMB-008/AMB-016)."""                                          
      229 +    if despesa.valor_base > limiar and not despesa.tem_nota_fi
          +scal:                                                         
      230          return Motivo.SEM_NOTA_FISCAL
      231      return None
      232  
      233  
      234  # ------------------------------------------------------------
           --------------- #
      156 -# Passo 8 — Tetos (RN-002..RN-005, RN-009)                    
      235 +# Passo 11 — Tetos por periodicidade (RN-002/003/004/005/009/0
          +16)                                                           
      236  # ------------------------------------------------------------
           --------------- #
      158 -def tetos_efetivos(em_viagem: bool) -> dict[str, Decimal]:    
      159 -    """RN-009 — aplica o multiplicador de viagem aos tres teto
          -s quando                                                      
      160 -    `em_viagem`. O limiar de nota fiscal NAO escala (AMB-008).
          -"""                                                           
      161 -    mult = MULTIPLICADOR_VIAGEM if em_viagem else Decimal("1")
      162 -    return {                                                  
      163 -        "alimentacao": _quantiza(LIMITES_DIARIOS["alimentacao"
          -] * mult),                                                    
      164 -        "transporte_urbano": _quantiza(LIMITES_DIARIOS["transp
          -orte_urbano"] * mult),                                        
      165 -        "hospedagem": _quantiza(LIMITE_HOSPEDAGEM * mult),    
      166 -    }                                                         
      237 +def _limite_viagem(limite: Decimal, fator: Decimal) -> Decimal
          +:                                                             
      238 +    return _quantiza(limite * fator)                          
      239  
      240  
      169 -def aplica_teto_diario(aceitas: list[Despesa], teto: Decimal) 
          --> Decimal:                                                   
      170 -    """RN-002/RN-003/RN-005 — agrega aceitas por dia civil e r
          -eembolsa                                                      
      171 -    `min(soma_do_dia, teto)`. Usado por alimentacao e transpor
          -te."""                                                        
      172 -    por_dia: dict[date, Decimal] = {}                         
      241 +def aplica_teto_dia(                                          
      242 +    aceitas: list[Despesa], limite: Decimal, fator: Decimal   
      243 +) -> Decimal:                                                 
      244 +    """RN-002/RN-005/RN-009/AMB-016 — periodicidade "dia": agr
          +ega por dia civil com                                         
      245 +    BALDES SEPARADOS por status de viagem. Cada balde e limita
          +do pelo seu teto                                              
      246 +    (base para nao-viagem, `limite * fator` para viagem) e o r
          +eembolso do dia e a                                           
      247 +    soma dos dois baldes."""                                  
      248 +    limite_viagem = _limite_viagem(limite, fator)             
      249 +    por_dia: dict[date, dict[bool, Decimal]] = {}             
      250      for despesa in aceitas:
      174 -        por_dia[despesa.data] = por_dia.get(despesa.data, Deci
          -mal("0")) + despesa.valor                                     
      251 +        baldes = por_dia.setdefault(despesa.data, {False: Deci
          +mal("0"), True: Decimal("0")})                                
      252 +        baldes[despesa.em_viagem] += despesa.valor_base       
      253      total = Decimal("0")
      176 -    for soma_dia in por_dia.values():                         
      177 -        total += min(soma_dia, teto)                          
      254 +    for baldes in por_dia.values():                           
      255 +        total += min(baldes[False], limite) + min(baldes[True]
          +, limite_viagem)                                              
      256      return total
      257  
      258  
      181 -def aplica_teto_hospedagem(aceitas: list[Despesa], teto: Decim
          -al) -> Decimal:                                               
      182 -    """RN-004/RN-005/AMB-006 — reembolsa `min(valor, teto)` po
          -r registro."""                                                
      259 +def aplica_teto_diaria(                                       
      260 +    aceitas: list[Despesa], limite: Decimal, fator: Decimal   
      261 +) -> Decimal:                                                 
      262 +    """RN-003/RN-005/RN-009/AMB-006 — periodicidade "diaria": 
          +teto por registro                                             
      263 +    individual, `min(valor_base, limite_efetivo)`, com `limite
          +_efetivo = limite *                                           
      264 +    fator` quando o registro esta em viagem."""               
      265      total = Decimal("0")
      266 +    limite_viagem = _limite_viagem(limite, fator)             
      267      for despesa in aceitas:
      185 -        total += min(despesa.valor, teto)                     
      268 +        teto = limite_viagem if despesa.em_viagem else limite 
      269 +        total += min(despesa.valor_base, teto)                
      270      return total
      271  
      272  
      273  # ------------------------------------------------------------
           --------------- #
      190 -# Passo 9 — Agregacao por categoria (RN-012, RN-014, AMB-012) 
      274 +# Passo 12 — Agregacao por categoria (RN-012, RN-014, AMB-012,
          + AMB-017)                                                     
      275  # ------------------------------------------------------------
           --------------- #
      276  def agrega_categoria(
      277      aceitas: list[Despesa],
      194 -    reprovadas: list[tuple[Despesa, Motivo]],                 
      278 +    reprovadas: list[tuple[Despesa, Motivo | str]],           
      279      total_reembolso: Decimal,
      280  ) -> ResultadoCategoria:
      197 -    """RN-012/RN-014 — calcula `total_aceito` (aceitas), `tota
          -l_despesas`                                                   
      198 -    (aceitas + reprovadas da categoria, EXCETO valores <= 0) e
          - monta a lista de                                             
      199 -    reprovadas. Vale a invariante `total_despesas >= total_ace
          -ito >= total_reembolso`.                                      
      281 +    """RN-012/RN-014 — `total_aceito` (aceitas), `total_despes
          +as` (aceitas +                                                
      282 +    reprovadas da categoria em `valor_base`, EXCETO `valor <= 
          +0` e EXCETO                                                   
      283 +    "cambio não identificado") e a lista de reprovadas. Vale a
          + invariante                                                   
      284 +    `total_despesas >= total_aceito >= total_reembolso`.      
      285  
      201 -    RN-014/D-004: `total_despesas` exclui despesas com `valor 
          -<= 0` — exclusao                                              
      202 -    POR VALOR, nao pelo motivo da recusa (Clarifications 2026-
          -07-30, opcao A).                                              
      203 -    Aceitas ja tem `valor > 0` (passaram no gate RN-010); o fi
          -ltro incide sobre as                                          
      204 -    reprovadas, para que uma negativa recusada por qualquer ga
          -te (duplicidade,                                              
      205 -    periodo, NF ou valor) nunca entre na somatoria."""        
      206 -    total_aceito = sum((d.valor for d in aceitas), Decimal("0"
          -))                                                            
      207 -    total_reprovadas = sum((d.valor for d, _ in reprovadas if 
          -d.valor > 0), Decimal("0"))                                   
      286 +    Exclusoes (mesmo principio de nao-valoravel):             
      287 +    - `valor_origem <= 0`: exclusao POR VALOR, nao pelo motivo
          + (RN-014/D-004);                                              
      288 +    - `valor_base is None` (cambio não identificado): sem valo
          +r em base para somar                                          
      289 +      (AMB-017)."""                                           
      290 +    total_aceito = sum((d.valor_base for d in aceitas), Decima
          +l("0"))                                                       
      291 +    total_reprovadas = sum(                                   
      292 +        (                                                     
      293 +            d.valor_base                                      
      294 +            for d, _ in reprovadas                            
      295 +            if d.valor_origem > 0 and d.valor_base is not None
      296 +        ),                                                    
      297 +        Decimal("0"),                                         
      298 +    )                                                         
      299      total_despesas = total_aceito + total_reprovadas
      300 +    from src.modelo import Reprovacao                         
      301 +                                                              
      302      return ResultadoCategoria(
      303          total_despesas=total_despesas,
      304          total_aceito=total_aceito,

● Let me fix the inline import in agrega_categoria — move Reprovacao to the
  top-level imports.

● Update(src\regras.py)
  ⎿  Added 1 line
      19      Motivo,
      20      Periodo,
      21      Politica,
      22 +    Reprovacao,                                                
      23      ResultadoCategoria,
      24  )
      25  from src.politica import CASAS_DECIMAIS

● Update(src\regras.py)
  ⎿  Removed 2 lines
      298          Decimal("0"),
      299      )
      300      total_despesas = total_aceito + total_reprovadas
      301 -    from src.modelo import Reprovacao                         
      302 -                                                              
      301      return ResultadoCategoria(
      302          total_despesas=total_despesas,
      303          total_aceito=total_aceito,

● Now T-040 — rewrite calculo.py (the pipeline):

● Write(src\calculo.py)
  ⎿  Added 93 lines, removed 78 lines
       1 -"""Pipeline puro que orquestra as regras na ordem da Secao 8 da
         - spec (DT-004).                                                
       1 +"""Pipeline puro que orquestra as regras na ordem da Secao 8 da
         + spec 1.4 (DT-012).                                            
       2  
       3 -estrutura -> normalizacao -> deduplicacao -> categoria -> perio
         -do -> valor ->                                                 
       4 -nota fiscal -> tetos -> agregacao. O primeiro gate que falha de
         -fine o motivo da                                               
       5 -recusa (AMB-010). Nao faz I/O.                                 
       3 +estrutura -> resolucao politica+cambio -> normalizacao -> categ
         +oria valida ->                                                 
       4 +limite > 0 -> conversao -> deduplicacao -> periodo -> valor -> 
         +nota fiscal (sobre                                             
       5 +valor convertido) -> tetos (baldes/periodicidade) -> agregacao.
         + O primeiro gate que                                           
       6 +falha define o motivo da recusa (AMB-010). Categorias sao dinam
         +icas por centro de                                             
       7 +custo; nenhuma e conhecida em codigo. Nao faz I/O.             
       8  """
       9  
      10  from __future__ import annotations
     ...
       13  
       14  from src import regras
       15  from src.modelo import (
       16 +    Cambio,                                                   
       17 +    CategoriaConfig,                                          
       18      Colaborador,
       19      Despesa,
       20      Motivo,
       21      Periodo,
       22 +    Politica,                                                 
       23      Reprovacao,
       24      Resultado,
       25      ResultadoCategoria,
       26  )
       22 -from src.politica import CATEGORIAS_VALIDAS                   
       23 -from src.regras import ORDEM_CATEGORIAS                       
       27  
       28  
       29  def calcula(
       30      despesas_brutas: list,
       31      colaborador: Colaborador,
       32      periodo: Periodo,
       30 -    em_viagem: bool,                                          
       33 +    politica: Politica,                                       
       34 +    cambio: Cambio,                                           
       35  ) -> Resultado:
       32 -    """Executa o pipeline completo e devolve o `Resultado` agr
          -egado."""                                                     
       33 -    tetos = regras.tetos_efetivos(em_viagem)                  
       36 +    """Executa o pipeline completo e devolve o `Resultado` agr
          +egado (sem                                                    
       37 +    `em_viagem`). O conjunto de categorias e resolvido pelo ce
          +ntro de custo."""                                             
       38 +    conjunto = regras.resolve_conjunto(politica, colaborador.c
          +entro_custo)                                                  
       39 +    fator = Decimal("1") + politica.acrescimo_viagem_pct / Dec
          +imal("100")                                                   
       40  
       41      reprovadas_sem_categoria: list[Reprovacao] = []
       36 -    aceitas_por_cat: dict[str, list[Despesa]] = {c: [] for c i
          -n ORDEM_CATEGORIAS}                                           
       37 -    reprovadas_por_cat: dict[str, list[tuple[Despesa, Motivo]]
          -] = {                                                         
       38 -        c: [] for c in ORDEM_CATEGORIAS                       
       42 +    aceitas_por_cat: dict[str, list[Despesa]] = {c: [] for c i
          +n conjunto}                                                   
       43 +    reprovadas_por_cat: dict[str, list[tuple[Despesa, Motivo |
          + str]]] = {                                                   
       44 +        c: [] for c in conjunto                               
       45      }
       46 +    vistas: set[tuple] = set()                                
       47  
       41 -    # Passo 1 — validacao estrutural (por registro).          
       42 -    validos: list[dict] = []                                  
       48      for bruto in despesas_brutas:
       44 -        motivo = regras.valida_estrutura(bruto)               
       45 -        if motivo is not None:                                
       49 +        # 1 — validacao estrutural.                           
       50 +        if regras.valida_estrutura(bruto) is not None:        
       51              reprovadas_sem_categoria.append(
       52                  Reprovacao(
       53                      id=_id_bruto(bruto),
       49 -                    motivo=motivo,                            
       54 +                    motivo=Motivo.REGISTRO_INVALIDO,          
       55                      categoria_informada=_categoria_bruta(bruto
           ),
       56                  )
       57              )
       53 -        else:                                                 
       54 -            validos.append(bruto)                             
       58 +            continue                                          
       59  
       56 -    # Passo 2 — normalizacao.                                 
       57 -    normalizadas = [regras.normaliza_despesa(b) for b in valid
          -os]                                                           
       60 +        # 3 — normalizacao (valor, categoria, moeda, viagem). 
       61 +        despesa = regras.normaliza_despesa(bruto, cambio)     
       62  
       59 -    # Passo 3 — deduplicacao (mantem 1a ocorrencia).          
       60 -    dedup = regras.deduplica(normalizadas)                    
       61 -                                                              
       62 -    # Passos 4-7 — gates. O primeiro que falha define o motivo
          -.                                                             
       63 -    for despesa, motivo_dedup in dedup:                       
       64 -        motivo = motivo_dedup                                 
       65 -        if motivo is None:                                    
       66 -            motivo = regras.valida_categoria(despesa)         
       67 -            if motivo is Motivo.CATEGORIA_NAO_APLICAVEL:      
       68 -                reprovadas_sem_categoria.append(              
       69 -                    Reprovacao(                               
       70 -                        id=despesa.id,                        
       71 -                        motivo=motivo,                        
       72 -                        categoria_informada=despesa.categoria,
       73 -                    )                                         
       63 +        # 4 — categoria valida (chaves do conjunto do CC).    
       64 +        if regras.valida_categoria(despesa, conjunto) is not N
          +one:                                                          
       65 +            reprovadas_sem_categoria.append(                  
       66 +                Reprovacao(                                   
       67 +                    id=despesa.id,                            
       68 +                    motivo=Motivo.CATEGORIA_NAO_APLICAVEL,    
       69 +                    categoria_informada=despesa.categoria,    
       70                  )
       75 -                continue                                      
       76 -            if motivo is None:                                
       77 -                motivo = regras.valida_periodo(despesa, period
          -o)                                                            
       78 -            if motivo is None:                                
       79 -                motivo = regras.valida_valor(despesa)         
       80 -            if motivo is None:                                
       81 -                motivo = regras.valida_nota_fiscal(despesa)   
       71 +            )                                                 
       72 +            continue                                          
       73  
       83 -        _classifica(                                          
       84 -            despesa, motivo, reprovadas_por_cat, aceitas_por_c
          -at, reprovadas_sem_categoria                                  
       85 -        )                                                     
       74 +        cat = despesa.categoria_norm                          
       75 +        config = conjunto[cat]                                
       76  
       87 -    # Passos 8-9 — tetos e agregacao, em ordem fixa de categor
          -ia.                                                           
       77 +        # 6 — conversao de cambio (calculada aqui para dar `va
          +lor_base` inclusive                                           
       78 +        # aos reprovados por limite <= 0 que compoem `total_de
          +spesas`); a RECUSA                                            
       79 +        # por cambio nao identificado so e emitida apos o gate
          + de limite (precedencia                                       
       80 +        # da Secao 8), abaixo.                                
       81 +        motivo_cambio = regras.valida_cambio(despesa, cambio) 
       82 +                                                              
       83 +        # 5 — limite da categoria > 0 (prevalece sobre cambio 
          +nao identificado).                                            
       84 +        motivo_limite = regras.valida_limite_categoria(despesa
          +, config)                                                     
       85 +        if motivo_limite is not None:                         
       86 +            reprovadas_por_cat[cat].append((despesa, motivo_li
          +mite))                                                        
       87 +            continue                                          
       88 +                                                              
       89 +        # 6 (recusa) — cambio nao identificado.               
       90 +        if motivo_cambio is not None:                         
       91 +            reprovadas_por_cat[cat].append((despesa, motivo_ca
          +mbio))                                                        
       92 +            continue                                          
       93 +                                                              
       94 +        # 7 — deduplicacao (1a ocorrencia; chave inclui valor/
          +moeda de origem).                                             
       95 +        chave = despesa.chave_duplicidade()                   
       96 +        if chave in vistas:                                   
       97 +            reprovadas_por_cat[cat].append((despesa, Motivo.RE
          +GISTRO_DUPLICADO))                                            
       98 +            continue                                          
       99 +        vistas.add(chave)                                     
      100 +                                                              
      101 +        # 8 — periodo.                                        
      102 +        if regras.valida_periodo(despesa, periodo) is not None
          +:                                                             
      103 +            reprovadas_por_cat[cat].append((despesa, Motivo.DA
          +TA_FORA_COMPETENCIA))                                         
      104 +            continue                                          
      105 +                                                              
      106 +        # 9 — valor valido.                                   
      107 +        if regras.valida_valor(despesa) is not None:          
      108 +            reprovadas_por_cat[cat].append((despesa, Motivo.VA
          +LOR_INVALIDO))                                                
      109 +            continue                                          
      110 +                                                              
      111 +        # 10 — nota fiscal (sobre o valor convertido).        
      112 +        if regras.valida_nota_fiscal(despesa, politica.limiar_
          +nf) is not None:                                              
      113 +            reprovadas_por_cat[cat].append((despesa, Motivo.SE
          +M_NOTA_FISCAL))                                               
      114 +            continue                                          
      115 +                                                              
      116 +        # Passou de 1 a 10 -> aceita.                         
      117 +        aceitas_por_cat[cat].append(despesa)                  
      118 +                                                              
      119 +    # 11-12 — tetos e agregacao, na ordem das chaves do CC; so
          + categorias com >= 1                                          
      120 +    # despesa aparecem (AMB-015).                             
      121      categorias: dict[str, ResultadoCategoria] = {}
      122      total_geral = Decimal("0")
       90 -    for cat in ORDEM_CATEGORIAS:                              
      123 +    for cat, config in conjunto.items():                      
      124          aceitas = aceitas_por_cat[cat]
       92 -        if cat == "hospedagem":                               
       93 -            reembolso = regras.aplica_teto_hospedagem(aceitas,
          - tetos[cat])                                                  
       94 -        else:                                                 
       95 -            reembolso = regras.aplica_teto_diario(aceitas, tet
          -os[cat])                                                      
       96 -        categorias[cat] = regras.agrega_categoria(            
       97 -            aceitas, reprovadas_por_cat[cat], reembolso       
       98 -        )                                                     
      125 +        reprovadas = reprovadas_por_cat[cat]                  
      126 +        if not aceitas and not reprovadas:                    
      127 +            continue  # categoria sem despesa nao e emitida.  
      128 +        reembolso = _reembolso_categoria(aceitas, config, fato
          +r)                                                            
      129 +        categorias[cat] = regras.agrega_categoria(aceitas, rep
          +rovadas, reembolso)                                           
      130          total_geral += reembolso
      131  
      132      return Resultado(
      133          colaborador=colaborador,
      134          competencia=periodo.competencia,
      135          periodo=periodo,
      105 -        em_viagem=em_viagem,                                  
      136          categorias=categorias,
      137          reprovadas_sem_categoria=reprovadas_sem_categoria,
      138          total_reembolso_geral=total_geral,
      139      )
      140  
      141  
      112 -def _classifica(                                              
      113 -    despesa: Despesa,                                         
      114 -    motivo: Motivo | None,                                    
      115 -    reprovadas_por_cat: dict[str, list[tuple[Despesa, Motivo]]
          -],                                                            
      116 -    aceitas_por_cat: dict[str, list[Despesa]],                
      117 -    reprovadas_sem_categoria: list[Reprovacao],               
      118 -) -> None:                                                    
      119 -    """Coloca a despesa no balde certo. Recusas com categoria 
          -valida ficam sob a                                            
      120 -    categoria; recusas sem categoria valida vao para `reprovad
          -as_sem_categoria`."""                                         
      121 -    if motivo is None:                                        
      122 -        aceitas_por_cat[despesa.categoria_norm].append(despesa
          -)                                                             
      123 -        return                                                
      124 -    if despesa.categoria_norm in CATEGORIAS_VALIDAS:          
      125 -        reprovadas_por_cat[despesa.categoria_norm].append((des
          -pesa, motivo))                                                
      126 -    else:                                                     
      127 -        reprovadas_sem_categoria.append(                      
      128 -            Reprovacao(                                       
      129 -                id=despesa.id,                                
      130 -                motivo=motivo,                                
      131 -                categoria_informada=despesa.categoria,        
      132 -            )                                                 
      133 -        )                                                     
      142 +def _reembolso_categoria(                                     
      143 +    aceitas: list[Despesa], config: CategoriaConfig, fator: De
          +cimal                                                         
      144 +) -> Decimal:                                                 
      145 +    """Aplica o teto conforme a `periodicidade` (RN-016)."""  
      146 +    if config.periodicidade == "diaria":                      
      147 +        return regras.aplica_teto_diaria(aceitas, config.limit
          +e, fator)                                                     
      148 +    return regras.aplica_teto_dia(aceitas, config.limite, fato
          +r)                                                            
      149  
      150  
      151  def _id_bruto(bruto: object) -> str | None:

● Now T-030 + T-041 — rewrite io_json.py (loaders for política/câmbio, and
  serialization without em_viagem, dynamic categories):

● Write(src\io_json.py)
  ⎿  Added 57 lines, removed 25 lines
      1 -"""Casca de I/O: leitura da entrada e serializacao da saida (DT-
        -001, DT-006).                                                   
      1 +"""Casca de I/O: leitura das 3 fontes e serializacao da saida (D
        +T-001/DT-006/DT-008).                                           
      2  
      3 -Le o JSON com `parse_float=Decimal` para nunca passar valores po
        -r `float`.                                                      
      4 -Serializa a saida com acentos preservados (`ensure_ascii=False`)
        -, ordem de chaves                                               
      5 -fixa e todo valor monetario com exatamente 2 casas decimais.    
      3 +Le os JSON com `parse_float=Decimal` para nunca passar valores n
        +em taxas por                                                    
      4 +`float`. Serializa a saida com acentos preservados (`ensure_asci
        +i=False`), ordem de                                             
      5 +chaves fixa e todo valor monetario com exatamente 2 casas decima
        +is. A saida nao tem                                             
      6 +mais `em_viagem` e as categorias sao dinamicas (spec 1.4).      
      7  """
      8  
      9  from __future__ import annotations
     ...
      14  from datetime import date
      15  from decimal import ROUND_HALF_UP, Decimal
      16  
      16 -from src.modelo import Colaborador, Periodo, Resultado, Resulta
         -doCategoria                                                    
      17 -from src.politica import CASAS_DECIMAIS                        
      18 -from src.regras import ORDEM_CATEGORIAS                        
      17 +from src.modelo import (                                       
      18 +    Cambio,                                                    
      19 +    Colaborador,                                               
      20 +    Periodo,                                                   
      21 +    Politica,                                                  
      22 +    Resultado,                                                 
      23 +    ResultadoCategoria,                                        
      24 +    motivo_texto,                                              
      25 +)                                                              
      26 +from src.politica import CASAS_DECIMAIS, cambio_de_dict, politi
         +ca_de_dict                                                     
      27  
      28  
      29  class ErroEntrada(Exception):
      30      """Erro irrecuperavel de entrada (arquivo inexistente, JSON
           de topo invalido,
      23 -    campos de topo ausentes) — aborta a execucao com codigo 1 (
         -DT-006)."""                                                    
      31 +    campos de topo ausentes) — aborta a execucao com codigo 1 (
         +DT-006, RN-018)."""                                            
      32  
      33  
      34  @dataclass
     ...
      38      colaborador: Colaborador
      39      periodo: Periodo
      40      despesas_brutas: list
      33 -    em_viagem: bool                                            
      41  
      42  
      43  # -------------------------------------------------------------
          -------------- #
      44  # Leitura
      45  # -------------------------------------------------------------
          -------------- #
      39 -def ler_entrada(caminho) -> Entrada:                           
      40 -    """Le e valida a estrutura de topo do input. Levanta `ErroE
         -ntrada` em erro                                                
      41 -    irrecuperavel. Registros de despesa individuais NAO sao val
         -idados aqui — isso                                             
      42 -    e responsabilidade do nucleo (RN-013)."""                  
      46 +def _carrega_json(caminho, rotulo: str) -> object:             
      47 +    """Abre e parseia um JSON com `parse_float=Decimal`; erros 
         +viram `ErroEntrada`."""                                        
      48      try:
      49          with open(caminho, encoding="utf-8") as arquivo:
      45 -            dados = json.load(arquivo, parse_float=Decimal)    
      50 +            return json.load(arquivo, parse_float=Decimal)     
      51      except FileNotFoundError as erro:
      47 -        raise ErroEntrada(f"arquivo de entrada nao encontrado: 
         -{caminho}") from erro                                          
      52 +        raise ErroEntrada(f"{rotulo} nao encontrado: {caminho}"
         +) from erro                                                    
      53      except json.JSONDecodeError as erro:
      49 -        raise ErroEntrada(f"JSON de entrada invalido: {erro}") 
         -from erro                                                      
      54 +        raise ErroEntrada(f"{rotulo} com JSON invalido: {erro}"
         +) from erro                                                    
      55      except OSError as erro:
      51 -        raise ErroEntrada(f"nao foi possivel ler {caminho}: {er
         -ro}") from erro                                                
      56 +        raise ErroEntrada(f"nao foi possivel ler {rotulo} ({cam
         +inho}): {erro}") from erro                                     
      57  
      58 +                                                               
      59 +def ler_entrada(caminho) -> Entrada:                           
      60 +    """Le e valida a estrutura de topo do input. Levanta `ErroE
         +ntrada` em erro                                                
      61 +    irrecuperavel. Registros de despesa individuais NAO sao val
         +idados aqui — isso                                             
      62 +    e responsabilidade do nucleo (RN-013). Nao ha mais campo de
         + topo `em_viagem`."""                                          
      63 +    dados = _carrega_json(caminho, "arquivo de entrada")       
      64 +                                                               
      65      if not isinstance(dados, dict):
      66          raise ErroEntrada("JSON de topo deve ser um objeto")
      67  
     ...
       72      if not isinstance(despesas, list):
       73          raise ErroEntrada("campo 'despesas' ausente ou nao e u
           ma lista")
       74  
       63 -    em_viagem = dados.get("em_viagem", False)                 
       64 -    if not isinstance(em_viagem, bool):                       
       65 -        raise ErroEntrada("campo 'em_viagem' deve ser booleano
          -")                                                            
       75 +    return Entrada(colaborador, periodo, despesas)            
       76  
       67 -    return Entrada(colaborador, periodo, despesas, em_viagem) 
       77  
       78 +def ler_politica(caminho) -> Politica:                        
       79 +    """RN-015 — le `politica-v4.json` e constroi a `Politica`.
          + Aborta se ausente ou                                         
       80 +    inparseavel."""                                           
       81 +    dados = _carrega_json(caminho, "arquivo de politica")     
       82 +    if not isinstance(dados, dict):                           
       83 +        raise ErroEntrada("politica: JSON de topo deve ser um 
          +objeto")                                                      
       84 +    try:                                                      
       85 +        return politica_de_dict(dados)                        
       86 +    except (KeyError, TypeError, ValueError, ArithmeticError) 
          +as erro:                                                      
       87 +        raise ErroEntrada(f"politica mal formada: {erro}") fro
          +m erro                                                        
       88  
       89 +                                                              
       90 +def ler_cambio(caminho) -> Cambio:                            
       91 +    """RN-018 — le `cambio.json` e constroi o `Cambio`. Aborta
          + se ausente ou                                                
       92 +    inparseavel (sem o arquivo a `moeda_base` seria desconheci
          +da)."""                                                       
       93 +    dados = _carrega_json(caminho, "arquivo de cambio")       
       94 +    if not isinstance(dados, dict):                           
       95 +        raise ErroEntrada("cambio: JSON de topo deve ser um ob
          +jeto")                                                        
       96 +    try:                                                      
       97 +        return cambio_de_dict(dados)                          
       98 +    except (KeyError, TypeError, ValueError, ArithmeticError, 
          +AttributeError) as erro:                                      
       99 +        raise ErroEntrada(f"cambio mal formado: {erro}") from 
          +erro                                                          
      100 +                                                              
      101 +                                                              
      102  def _le_colaborador(dados: dict) -> Colaborador:
      103      bruto = dados.get("colaborador")
      104      if not isinstance(bruto, dict):
     ...
      175              "inicio": resultado.periodo.inicio.isoformat(),
      176              "fim": resultado.periodo.fim.isoformat(),
      177          },
      146 -        "em_viagem": resultado.em_viagem,                     
      178          "categorias": {
      148 -            cat: _categoria_dict(resultado.categorias[cat]) fo
          -r cat in ORDEM_CATEGORIAS                                     
      179 +            cat: _categoria_dict(rc) for cat, rc in resultado.
          +categorias.items()                                            
      180          },
      181          "reprovadas_sem_categoria": [
      182              {
      183                  "id": rep.id,
      184                  "categoria_informada": rep.categoria_informada
           ,
      154 -                "motivo": rep.motivo.value,                   
      185 +                "motivo": motivo_texto(rep.motivo),           
      186              }
      187              for rep in resultado.reprovadas_sem_categoria
      188          ],
     ...
      196          "total_aceito": _quantiza(categoria.total_aceito),
      197          "total_reembolso": _quantiza(categoria.total_reembolso
           ),
      198          "reprovadas": [
      168 -            {"id": rep.id, "motivo": rep.motivo.value} for rep
          - in categoria.reprovadas                                      
      199 +            {"id": rep.id, "motivo": motivo_texto(rep.motivo)}
      200 +            for rep in categoria.reprovadas                   
      201          ],
      202      }

● Now T-042 — rewrite cli.py (remove --em-viagem, add --politica/--cambio with
  packaged defaults) and update __main__.py:

● Write(src\cli.py)
  ⎿  Added 23 lines, removed 9 lines
       1 -"""Interface de linha de comando `calcular` (DT-003).          
       1 +"""Interface de linha de comando `calcular` (DT-003, DT-003b). 
       2  
       3 -Liga leitura -> pipeline -> escrita. Exit codes: 0 sucesso, 1 e
         -rro irrecuperavel                                              
       4 -de entrada, 2 erro de uso (padrao do argparse). Ver `contracts/
         -cli-contract.md`.                                              
       3 +Liga leitura das 3 fontes (input, politica, cambio) -> pipeline
         + -> escrita. Sem                                               
       4 +regra de negocio na CLI. Exit codes: 0 sucesso, 1 erro irrecupe
         +ravel de entrada                                               
       5 +(input/politica/cambio ausente ou inparseavel; topo invalido), 
         +2 erro de uso                                                  
       6 +(padrao do argparse). Ver `contracts/cli-contract.md`.         
       7  """
       8  
       9  from __future__ import annotations
      10  
      11  import argparse
      12  import sys
      13 +from pathlib import Path                                       
      14  
      15  from src import calculo, io_json
      16  
      17 +# Arquivos empacotados, resolvidos relativos ao pacote `src` (D
         +T-003b).                                                       
      18 +_INFO = Path(__file__).resolve().parent / "informacoes_externas
         +"                                                              
      19 +_POLITICA_PADRAO = _INFO / "politica-v4.json"                  
      20 +_CAMBIO_PADRAO = _INFO / "cambio.json"                         
      21  
      22 +                                                               
      23  def _parser() -> argparse.ArgumentParser:
      24      parser = argparse.ArgumentParser(
      25          prog="calcular",
     ...
      28      parser.add_argument("--input", required=True, help="arquivo
           JSON de entrada")
      29      parser.add_argument("--output", required=True, help="arquiv
          o JSON de saida")
      30      parser.add_argument(
      23 -        "--em-viagem",                                         
      24 -        action="store_true",                                   
      25 -        dest="em_viagem",                                      
      26 -        help="aplica limites ampliados em 50%% a todas as despe
         -sas do input (RN-009)",                                        
      31 +        "--politica",                                          
      32 +        default=str(_POLITICA_PADRAO),                         
      33 +        help="politica externa de categorias/limites por centro
         + de custo (RN-015)",                                           
      34      )
      35 +    parser.add_argument(                                       
      36 +        "--cambio",                                            
      37 +        default=str(_CAMBIO_PADRAO),                           
      38 +        help="tabela de cambio: moeda_base + taxas por data (RN
         +-018)",                                                        
      39 +    )                                                          
      40      return parser
      41  
      42  
     ...
      46  
      47      try:
      48          entrada = io_json.ler_entrada(args.input)
      49 +        politica = io_json.ler_politica(args.politica)         
      50 +        cambio = io_json.ler_cambio(args.cambio)               
      51      except io_json.ErroEntrada as erro:
      52          print(f"erro: {erro}", file=sys.stderr)
      53          return 1
      54  
      41 -    # A flag da CLI e a fonte de verdade de `em_viagem` (AMB-00
         -8).                                                            
      55      resultado = calculo.calcula(
      56          entrada.despesas_brutas,
      57          entrada.colaborador,
      58          entrada.periodo,
      46 -        args.em_viagem,                                        
      59 +        politica,                                              
      60 +        cambio,                                                
      61      )
      62      io_json.escrever_saida(resultado, args.output)
      63      return 0

● Update(src\__main__.py)
  ⎿  Added 1 line, removed 1 line
      1 -"""Permite `python -m src --input ... --output ... [--em-viagem]
        -` (DT-003)."""                                                  
      1 +"""Permite `python -m src --input ... --output ... [--politica .
        +..] [--cambio ...]` (DT-003)."""                                
      2  
      3  import sys
      4  

● Source code is complete. Before rewriting tests, let me smoke-test the CLI
  end-to-end against both examples to verify the goldens.

  Ran 1 shell command (ctrl+o to expand)
● Exemplo golden matches exactly (351.43, all category totals). Now the
  envelope:

  Ran 1 shell command (ctrl+o to expand)

● Both goldens match exactly. The implementation is correct. Now I'll rewrite
  the test suite for spec 1.4 (T-044..T-049). Starting with the shared helpers
  and fixtures:

● Write(tests\_apoio.py)
  ⎿  Added 60 lines, removed 6 lines
       1 -"""Fabricas de apoio para os testes (registros brutos, despesas
         -, periodo)."""                                                 
       1 +"""Fabricas de apoio para os testes (registros brutos, despesas
         +, politica, cambio).                                           
       2  
       3 +Modelo spec 1.4: `normaliza_despesa` recebe um `Cambio`; despes
         +as tem `valor_origem`                                          
       4 +/`valor_base`/`moeda_norm`/`em_viagem`. `CAMBIO_PADRAO` tem `mo
         +eda_base` BRL e algumas                                        
       5 +taxas para exercitar conversao/viagem sem depender dos arquivos
         + empacotados.                                                  
       6 +"""                                                            
       7 +                                                               
       8  from __future__ import annotations
       9  
      10  from datetime import date
      11  from decimal import Decimal
      12  
       8 -from src.modelo import Periodo                                 
       9 -from src.regras import normaliza_despesa                       
      13 +from src.modelo import Cambio, CategoriaConfig, Despesa, Period
         +o, Politica                                                    
      14 +from src.regras import normaliza_despesa, valida_cambio        
      15  
      16 +# Cambio de teste: base BRL, com USD/EUR em algumas datas (e um
         + empate proposital).                                           
      17 +CAMBIO_PADRAO = Cambio(                                        
      18 +    moeda_base="BRL",                                          
      19 +    taxas={                                                    
      20 +        date(2026, 7, 14): {"USD": Decimal("5.44"), "EUR": Deci
         +mal("5.93")},                                                  
      21 +        date(2026, 7, 15): {"USD": Decimal("5.39"), "EUR": Deci
         +mal("5.88")},                                                  
      22 +        date(2026, 7, 17): {"USD": Decimal("5.47"), "EUR": Deci
         +mal("5.96")},                                                  
      23 +        date(2026, 7, 20): {"USD": Decimal("5.50"), "EUR": Deci
         +mal("6.01")},                                                  
      24 +    },                                                         
      25 +)                                                              
      26 +                                                               
      27  _PADRAO_BRUTO = {
      28      "id": "d-x",
      29      "data": "2026-07-10",
     ...
      42      return registro
      43  
      44  
      29 -def despesa(**over):                                           
      30 -    """Despesa ja normalizada a partir de um registro cru."""  
      31 -    return normaliza_despesa(bruto(**over))                    
      45 +def despesa(cambio: Cambio = CAMBIO_PADRAO, **over) -> Despesa:
      46 +    """Despesa normalizada e convertida (valor_base preenchido)
         + a partir de um cru."""                                        
      47 +    d = normaliza_despesa(bruto(**over), cambio)               
      48 +    valida_cambio(d, cambio)                                   
      49 +    return d                                                   
      50  
      51  
      52 +def aceita(                                                    
      53 +    valor_base, *, data: str = "2026-07-03", em_viagem: bool = 
         +False, **over                                                  
      54 +) -> Despesa:                                                  
      55 +    """Despesa ja aceita com `valor_base` explicito (util para 
         +testes de teto)."""                                            
      56 +    valor = Decimal(str(valor_base))                           
      57 +    d = despesa(valor=valor, data=data, **over)                
      58 +    d.em_viagem = em_viagem                                    
      59 +    d.valor_base = valor                                       
      60 +    return d                                                   
      61 +                                                               
      62 +                                                               
      63 +def config(limite, periodicidade="dia", observacao=None) -> Cat
         +egoriaConfig:                                                  
      64 +    return CategoriaConfig(                                    
      65 +        limite=Decimal(str(limite)), periodicidade=periodicidad
         +e, observacao=observacao                                       
      66 +    )                                                          
      67 +                                                               
      68 +                                                               
      69 +def politica(                                                  
      70 +    conjunto: dict[str, CategoriaConfig] | None = None,        
      71 +    *,                                                         
      72 +    padrao: dict[str, CategoriaConfig] | None = None,          
      73 +    centros: dict[str, dict[str, CategoriaConfig]] | None = Non
         +e,                                                             
      74 +    limiar_nf="100",                                           
      75 +    acrescimo_viagem_pct="50",                                 
      76 +) -> Politica:                                                 
      77 +    """Politica de teste; `conjunto` vira o objeto `padrao` se 
         +`padrao` nao for dado."""                                      
      78 +    if padrao is None:                                         
      79 +        padrao = conjunto or {"alimentacao": config("60")}     
      80 +    return Politica(                                           
      81 +        padrao=padrao,                                         
      82 +        centros_custo=centros or {},                           
      83 +        limiar_nf=Decimal(str(limiar_nf)),                     
      84 +        acrescimo_viagem_pct=Decimal(str(acrescimo_viagem_pct))
         +,                                                              
      85 +    )                                                          
      86 +                                                               
      87 +                                                               
      88  def periodo(
      89      inicio: str = "2026-07-01",
      90      fim: str = "2026-07-31",

● Now update conftest.py with fixtures for the envelope path, política and
  câmbio:

● Write(tests\conftest.py)
  ⎿  Added 33 lines, removed 2 lines
       1 -"""Fixtures compartilhadas dos testes."""                      
       1 +"""Fixtures compartilhadas dos testes (spec 1.4)."""           
       2  
       3  from pathlib import Path
       4  
       5  import pytest
       6  
       7 +from src import io_json                                        
       8 +                                                               
       9  _RAIZ = Path(__file__).resolve().parent.parent
      10 +_INFO = _RAIZ / "src" / "informacoes_externas"                 
      11  
      12  
      13  @pytest.fixture(scope="session")
      14  def caminho_exemplo() -> Path:
      12 -    """Caminho do input oficial `exemplos/despesas-exemplo.json
         -`."""                                                          
      15 +    """Caminho do input `exemplos/despesas-exemplo.json` (CC-EN
         +G-PLATAFORMA)."""                                              
      16      return _RAIZ / "exemplos" / "despesas-exemplo.json"
      17 +                                                               
      18 +                                                               
      19 +@pytest.fixture(scope="session")                               
      20 +def caminho_envelope() -> Path:                                
      21 +    """Caminho do input `exemplos/despesas-envelope.json` (CC-C
         +OMERCIAL, moedas)."""                                          
      22 +    return _RAIZ / "exemplos" / "despesas-envelope.json"       
      23 +                                                               
      24 +                                                               
      25 +@pytest.fixture(scope="session")                               
      26 +def caminho_politica() -> Path:                                
      27 +    return _INFO / "politica-v4.json"                          
      28 +                                                               
      29 +                                                               
      30 +@pytest.fixture(scope="session")                               
      31 +def caminho_cambio() -> Path:                                  
      32 +    return _INFO / "cambio.json"                               
      33 +                                                               
      34 +                                                               
      35 +@pytest.fixture(scope="session")                               
      36 +def politica_v4(caminho_politica):                             
      37 +    """`Politica` construida a partir do arquivo empacotado."""
      38 +    return io_json.ler_politica(caminho_politica)              
      39 +                                                               
      40 +                                                               
      41 +@pytest.fixture(scope="session")                               
      42 +def cambio_real(caminho_cambio):                               
      43 +    """`Cambio` construido a partir do arquivo empacotado."""  
      44 +    return io_json.ler_cambio(caminho_cambio)                  

● Now the test files. T-028/T-049 test_modelo.py:

● Write(tests\test_modelo.py)
  ⎿  Added 43 lines, removed 3 lines
       1 -"""Testes do modelo de dados (T-004)."""                       
       1 +"""Testes do modelo de dados (T-028), spec 1.4."""             
       2  
       3 -from src.modelo import Motivo                                  
       3 +import dataclasses                                             
       4 +from decimal import Decimal                                    
       5  
       6 +from src.modelo import Despesa, Motivo, Resultado, motivo_texto
       7  
       8 +                                                               
       9  def test_motivos_texto_exato():
       7 -    """Os 6 motivos batem com o texto exato da spec."""        
      10 +    """Os 7 motivos batem com o texto exato da spec (inclui cam
         +bio nao identificado)."""                                      
      11      assert Motivo.CATEGORIA_NAO_APLICAVEL.value == "categoria n
          ão aplicável"
      12      assert Motivo.DATA_FORA_COMPETENCIA.value == "data fora da 
          competência"
      13      assert Motivo.REGISTRO_DUPLICADO.value == "registro duplica
          do"
      14      assert Motivo.SEM_NOTA_FISCAL.value == "sem nota fiscal obr
          igatória"
      15      assert Motivo.VALOR_INVALIDO.value == "valor inválido"
      16      assert Motivo.REGISTRO_INVALIDO.value == "registro inválido
          "
      17 +    assert Motivo.CAMBIO_NAO_IDENTIFICADO.value == "cambio não 
         +identificado"                                                  
      18 +                                                               
      19 +                                                               
      20 +def test_resultado_sem_em_viagem():                            
      21 +    """O `Resultado` nao tem mais campo `em_viagem` (viagem e p
         +or registro, RN-009)."""                                       
      22 +    campos = {f.name for f in dataclasses.fields(Resultado)}   
      23 +    assert "em_viagem" not in campos                           
      24 +                                                               
      25 +                                                               
      26 +def test_despesa_campos_cambio():                              
      27 +    """A `Despesa` carrega os campos de cambio/viagem da spec 1
         +.4."""                                                         
      28 +    campos = {f.name for f in dataclasses.fields(Despesa)}     
      29 +    assert {"valor_origem", "moeda_norm", "valor_base", "em_via
         +gem"} <= campos                                                
      30 +    assert "valor" not in campos  # renomeado para valor_origem
         +/valor_base                                                    
      31 +                                                               
      32 +                                                               
      33 +def test_motivo_texto_aceita_str_da_observacao():              
      34 +    """`motivo_texto` devolve a observacao (str) intacta e o `.
         +value` do enum."""                                             
      35 +    assert motivo_texto("nao reembolsavel") == "nao reembolsave
         +l"                                                             
      36 +    assert motivo_texto(Motivo.VALOR_INVALIDO) == "valor inváli
         +do"                                                            
      37 +                                                               
      38 +                                                               
      39 +def test_chave_duplicidade_inclui_moeda_e_valor_origem():      
      40 +    d = Despesa(                                               
      41 +        id="a",                                                
      42 +        data=None,                                             
      43 +        categoria="Alimentacao",                               
      44 +        categoria_norm="alimentacao",                          
      45 +        descricao="d",                                         
      46 +        fornecedor="f",                                        
      47 +        valor_origem=Decimal("10.00"),                         
      48 +        moeda_norm="USD",                                      
      49 +        tem_nota_fiscal=True,                                  
      50 +    )                                                          
      51 +    chave = d.chave_duplicidade()                              
      52 +    assert Decimal("10.00") in chave and "USD" in chave        
      53 +    assert "a" not in chave  # id nao entra (AMB-002)          

● Now T-029/T-031/T-044 test_politica.py (política construction + RN-015
  resolution):

● Write(tests\test_politica.py)
  ⎿  Added 60 lines, removed 21 lines
       1 -"""Testes das constantes de politica (T-003)."""               
       1 +"""Testes da politica externa: construcao e resolucao de centro
         + de custo (T-029/T-031/T-044).                                 
       2  
       3 +Cobre RN-015 (fonte externa + fallback `padrao`) e RN-016 (peri
         +odicidade lida da                                              
       4 +politica). Usa o arquivo empacotado `politica-v4.json`.        
       5 +"""                                                            
       6 +                                                               
       7  from decimal import Decimal
       8  
       5 -from src import politica                                       
       9 +from src import regras                                         
      10 +from src.modelo import CategoriaConfig                         
      11 +from src.politica import politica_de_dict                      
      12  
      13  
       8 -def test_valores_politica():                                   
       9 -    assert politica.LIMITES_DIARIOS["alimentacao"] == Decimal("
         -60")                                                           
      10 -    assert politica.LIMITES_DIARIOS["transporte_urbano"] == Dec
         -imal("80")                                                     
      11 -    assert politica.LIMITE_HOSPEDAGEM == Decimal("250")        
      12 -    assert politica.LIMIAR_NOTA_FISCAL == Decimal("100")       
      13 -    assert politica.MULTIPLICADOR_VIAGEM == Decimal("1.5")     
      14 -    assert politica.CATEGORIAS_VALIDAS == {                    
      15 -        "alimentacao",                                         
      16 -        "transporte_urbano",                                   
      17 -        "hospedagem",                                          
      18 -    }                                                          
      19 -    assert politica.CASAS_DECIMAIS == Decimal("0.01")          
      14 +def test_politica_de_dict(politica_v4):                        
      15 +    """`politica_de_dict` constroi limites/periodicidade/parame
         +tros globais."""                                               
      16 +    assert politica_v4.limiar_nf == Decimal("100.00")          
      17 +    assert politica_v4.acrescimo_viagem_pct == Decimal("50")   
      18 +    eng = politica_v4.centros_custo["CC-ENG-PLATAFORMA"]       
      19 +    assert eng["alimentacao"] == CategoriaConfig(Decimal("75.00
         +"), "dia", None)                                               
      20 +    assert eng["hospedagem"].limite == Decimal("0.00")         
      21 +    assert eng["hospedagem"].observacao == "nao reembolsavel"  
      22 +    assert isinstance(eng["alimentacao"].limite, Decimal)      
      23  
      24  
      22 -def test_todos_valores_sao_decimal():                          
      23 -    for limite in politica.LIMITES_DIARIOS.values():           
      24 -        assert isinstance(limite, Decimal)                     
      25 -    assert isinstance(politica.LIMITE_HOSPEDAGEM, Decimal)     
      26 -    assert isinstance(politica.LIMIAR_NOTA_FISCAL, Decimal)    
      27 -    assert isinstance(politica.MULTIPLICADOR_VIAGEM, Decimal)  
      28 -    assert isinstance(politica.CASAS_DECIMAIS, Decimal)        
      25 +def test_cambio_de_dict(cambio_real):                          
      26 +    """`cambio_de_dict` constroi moeda_base e taxas por data co
         +mo Decimal."""                                                 
      27 +    from datetime import date                                  
      28 +                                                               
      29 +    assert cambio_real.moeda_base == "BRL"                     
      30 +    assert cambio_real.taxas[date(2026, 7, 14)]["EUR"] == Decim
         +al("5.93")                                                     
      31 +    assert isinstance(cambio_real.taxas[date(2026, 7, 20)]["USD
         +"], Decimal)                                                   
      32 +                                                               
      33 +                                                               
      34 +def test_rn_015_fallback_padrao(politica_v4):                  
      35 +    """RN-015/AMB-013 — centro de custo inexistente cai no conj
         +unto `padrao`."""                                              
      36 +    conjunto = regras.resolve_conjunto(politica_v4, "CC-INEXIST
         +ENTE")                                                         
      37 +    assert conjunto is politica_v4.padrao                      
      38 +    assert conjunto["alimentacao"].limite == Decimal("60.00")  
      39 +    assert conjunto["hospedagem"].limite == Decimal("250.00")  
      40 +                                                               
      41 +                                                               
      42 +def test_rn_015_cc_especifico(politica_v4):                    
      43 +    """RN-015 — centro existente usa o proprio conjunto."""    
      44 +    conjunto = regras.resolve_conjunto(politica_v4, "CC-ENG-PLA
         +TAFORMA")                                                      
      45 +    assert conjunto["alimentacao"].limite == Decimal("75.00")  
      46 +    assert "representacao" not in conjunto  # so existe em CC-C
         +OMERCIAL                                                       
      47 +                                                               
      48 +                                                               
      49 +def test_rn_016_periodicidade_lida_da_politica(politica_v4):   
      50 +    """RN-016 — a periodicidade vem da politica, nao do nome da
         + categoria."""                                                 
      51 +    comercial = regras.resolve_conjunto(politica_v4, "CC-COMERC
         +IAL")                                                          
      52 +    assert comercial["alimentacao"].periodicidade == "dia"     
      53 +    assert comercial["hospedagem"].periodicidade == "diaria"   
      54 +    assert comercial["representacao"].periodicidade == "dia"   
      55 +                                                               
      56 +                                                               
      57 +def test_moeda_base_da_politica_ignorada():                    
      58 +    """RN-018 — a `moeda_base` de `politica-v4.json` nao entra 
         +na `Politica`."""                                              
      59 +    pol = politica_de_dict(                                    
      60 +        {                                                      
      61 +            "moeda_base": "USD",  # deve ser ignorada          
      62 +            "padrao": {"alimentacao": {"limite": 60.0, "periodi
         +cidade": "dia"}},                                              
      63 +            "nota_fiscal_obrigatoria_acima_de": 100.0,         
      64 +            "acrescimo_em_viagem_percentual": 50,              
      65 +        }                                                      
      66 +    )                                                          
      67 +    assert not hasattr(pol, "moeda_base")                      

● Now T-045/T-030 test_cambio.py (RN-018/019/020 + abort):

● Write(tests\test_cambio.py)
  ⎿  Wrote 117 lines to tests\test_cambio.py
       1 """Testes de cambio (T-045/T-030): conversao, taxa por data, cam
         bio nao identificado.
       3 Cobre RN-018 (conversao/normalizacao), RN-019 (data mais proxima
         , empate -> menor) e
       4 RN-020 (cambio nao identificado), alem do abort de arquivo ausen
       5 """
       6 
       7 from datetime import date
       9 
      10 import pytest
     … +135 lines (ctrl+o to expand)

● Now T-046 test_regras.py (one test per RN, spec 1.4):

● Write(tests\test_regras.py)
  ⎿  Added 136 lines, removed 122 lines
       1 -"""Um teste por regra de negocio (RN) sobre `src.regras` (Fase 
         -2)."""                                                         
       1 +"""Um teste por regra de negocio (RN) sobre `src.regras` (T-046
         +), spec 1.4.                                                   
       2  
       3 +RN-012/RN-015/RN-016/RN-018/RN-019/RN-020 sao cobertas em `test
         +_calculo.py`,                                                  
       4 +`test_politica.py` e `test_cambio.py` (com testes cujo nome con
         +tem o proprio RN).                                             
       5 +"""                                                            
       6 +                                                               
       7  from decimal import Decimal
       8  
       9  from src import regras
      10  from src.modelo import Motivo
       7 -from tests._apoio import bruto, despesa, periodo               
      11 +from tests._apoio import aceita, config, despesa, periodo      
      12  
      13  
      14  # -------------------------------------------------------------
          -------------- #
      11 -# RN-011 — precisao / RN-001 — normalizacao (T-005)            
      15 +# RN-011 — precisao                                            
      16  # -------------------------------------------------------------
          -------------- #
      17  def test_rn_011_arredonda_33_333():
      18      d = despesa(valor=Decimal("33.333"))
      15 -    assert d.valor == Decimal("33.33")                         
      19 +    assert d.valor_origem == Decimal("33.33")                  
      20  
      21  
      18 -def test_rn_001_normaliza_caixa():                             
      19 -    d = despesa(categoria="ALIMENTACAO")                       
      20 -    assert d.categoria_norm == "alimentacao"                   
      21 -                                                               
      22 -                                                               
      22  # -------------------------------------------------------------
          -------------- #
      24 -# RN-013 — validacao estrutural (T-006)                        
      23 +# RN-013 — validacao estrutural (inclui tipo de `moeda`)       
      24  # -------------------------------------------------------------
          -------------- #
      25  def test_rn_013_registro_sem_data():
      26 +    from tests._apoio import bruto                             
      27 +                                                               
      28      registro = bruto()
      29      del registro["data"]
      30      assert regras.valida_estrutura(registro) is Motivo.REGISTRO
          _INVALIDO
      31  
      32  
      32 -def test_rn_013_valor_nao_numerico():                          
      33 -    assert regras.valida_estrutura(bruto(valor="abc")) is Motiv
         -o.REGISTRO_INVALIDO                                            
      33 +def test_rn_013_moeda_numerica_invalida():                     
      34 +    from tests._apoio import bruto                             
      35  
      36 +    assert regras.valida_estrutura(bruto(moeda=5)) is Motivo.RE
         +GISTRO_INVALIDO                                                
      37  
      36 -def test_rn_013_data_nao_parseavel():                          
      37 -    assert regras.valida_estrutura(bruto(data="2026-13-40")) is
         - Motivo.REGISTRO_INVALIDO                                      
      38  
      39 +def test_rn_013_moeda_vazia_nao_e_invalida():                  
      40 +    from tests._apoio import bruto                             
      41  
      40 -def test_rn_013_registro_valido_passa():                       
      41 -    assert regras.valida_estrutura(bruto()) is None            
      42 +    # "" e vazio apos trim -> sem moeda (base), nao invalido.  
      43 +    assert regras.valida_estrutura(bruto(moeda="")) is None    
      44 +    assert regras.valida_estrutura(bruto(moeda=None)) is None  
      45  
      46  
      47  # -------------------------------------------------------------
          -------------- #
      45 -# RN-008 — duplicatas (T-007)                                  
      48 +# RN-001 — categoria valida por centro de custo (dinamica)     
      49  # -------------------------------------------------------------
          -------------- #
      47 -def test_rn_008_mantem_primeira():                             
      48 -    d006 = despesa(id="d-006", descricao="Almoco", valor=Decima
         -l("54.90"))                                                    
      49 -    d007 = despesa(id="d-007", descricao="Almoco", valor=Decima
         -l("54.90"))                                                    
      50 -    resultado = regras.deduplica([d006, d007])                 
      51 -    assert resultado[0] == (d006, None)                        
      52 -    assert resultado[1] == (d007, Motivo.REGISTRO_DUPLICADO)   
      50 +def test_rn_001_coworking_invalida():                          
      51 +    conjunto = {"alimentacao": config("60")}                   
      52 +    assert regras.valida_categoria(despesa(categoria="coworking
         +"), conjunto) is (                                             
      53 +        Motivo.CATEGORIA_NAO_APLICAVEL                         
      54 +    )                                                          
      55  
      56  
      55 -def test_rn_008_id_nao_conta_para_duplicidade():               
      56 -    a = despesa(id="a")                                        
      57 -    b = despesa(id="b")                                        
      58 -    resultado = regras.deduplica([a, b])                       
      59 -    assert resultado[1][1] is Motivo.REGISTRO_DUPLICADO        
      57 +def test_rn_001_uppercase_valida():                            
      58 +    conjunto = {"alimentacao": config("60")}                   
      59 +    assert regras.valida_categoria(despesa(categoria="ALIMENTAC
         +AO"), conjunto) is None                                        
      60  
      61  
      62 +def test_rn_001_representacao_so_comercial():                  
      63 +    eng = {"alimentacao": config("75")}                        
      64 +    comercial = {"alimentacao": config("90"), "representacao": 
         +config("300")}                                                 
      65 +    d = despesa(categoria="representacao")                     
      66 +    assert regras.valida_categoria(d, eng) is Motivo.CATEGORIA_
         +NAO_APLICAVEL                                                  
      67 +    assert regras.valida_categoria(d, comercial) is None       
      68 +                                                               
      69 +                                                               
      70  # -------------------------------------------------------------
          -------------- #
      63 -# RN-001 — categoria valida (T-008)                            
      71 +# RN-017 — categoria com limite <= 0 (nao reembolsavel)        
      72  # -------------------------------------------------------------
          -------------- #
      65 -def test_rn_001_coworking_invalida():                          
      66 -    assert regras.valida_categoria(despesa(categoria="coworking
         -")) is (                                                       
      73 +def test_rn_017_limite_zero_nao_reembolsavel():                
      74 +    # limite 0 com observacao -> motivo e a observacao (prevale
         +ce sobre sem NF).                                              
      75 +    cfg = config("0", periodicidade="diaria", observacao="nao r
         +eembolsavel")                                                  
      76 +    d = despesa(valor=Decimal("690.00"), tem_nota_fiscal=False)
      77 +    assert regras.valida_limite_categoria(d, cfg) == "nao reemb
         +olsavel"                                                       
      78 +                                                               
      79 +                                                               
      80 +def test_rn_017_limite_zero_sem_observacao():                  
      81 +    cfg = config("0")                                          
      82 +    assert regras.valida_limite_categoria(despesa(), cfg) is ( 
      83          Motivo.CATEGORIA_NAO_APLICAVEL
      84      )
      85  
      86  
      71 -def test_rn_001_uppercase_valida():                            
      72 -    assert regras.valida_categoria(despesa(categoria="ALIMENTAC
         -AO")) is None                                                  
      87 +def test_rn_017_limite_positivo_passa():                       
      88 +    assert regras.valida_limite_categoria(despesa(), config("60
         +")) is None                                                    
      89  
      90  
      91  # -------------------------------------------------------------
          -------------- #
      76 -# RN-007 — periodo (T-009)                                     
      92 +# RN-007 — periodo                                             
      93  # -------------------------------------------------------------
          -------------- #
      94  def test_rn_007_fora():
      95      d = despesa(data="2026-04-15")
     ...
      102  
      103  
      104  # ------------------------------------------------------------
           --------------- #
       89 -# RN-010 — valor invalido (T-010)                             
      105 +# RN-010 — valor invalido                                     
      106  # ------------------------------------------------------------
           --------------- #
      107  def test_rn_010_negativo():
       92 -    d = despesa(valor=Decimal("-45.00"))                      
       93 -    assert regras.valida_valor(d) is Motivo.VALOR_INVALIDO    
      108 +    assert regras.valida_valor(despesa(valor=Decimal("-45.00")
          +)) is Motivo.VALOR_INVALIDO                                   
      109  
      110  
      111  def test_rn_010_zero_invalido():
     ...
      113  
      114  
      115  # ------------------------------------------------------------
           --------------- #
      101 -# RN-006 — nota fiscal (T-011)                                
      116 +# RN-006 — nota fiscal sobre o valor convertido               
      117  # ------------------------------------------------------------
           --------------- #
      103 -def test_rn_006_100_ok():                                     
      104 -    d = despesa(valor=Decimal("100.00"), tem_nota_fiscal=False
          -)                                                             
      105 -    assert regras.valida_nota_fiscal(d) is None               
      118 +def test_rn_006_sobre_valor_convertido():                     
      119 +    # USD 40 em 07-20 (taxa 5,50) -> 220,00 > 100 e sem NF -> 
          +recusada.                                                     
      120 +    d = despesa(                                              
      121 +        moeda="USD", data="2026-07-20", valor=Decimal("40.00")
          +, tem_nota_fiscal=False                                       
      122 +    )                                                         
      123 +    assert d.valor_base == Decimal("220.00")                  
      124 +    assert regras.valida_nota_fiscal(d, Decimal("100")) is Mot
          +ivo.SEM_NOTA_FISCAL                                           
      125  
      126  
      108 -def test_rn_006_100_01_recusa():                              
      109 -    d = despesa(valor=Decimal("100.01"), tem_nota_fiscal=False
          -)                                                             
      110 -    assert regras.valida_nota_fiscal(d) is Motivo.SEM_NOTA_FIS
          -CAL                                                           
      127 +def test_rn_006_limiar_exato():                               
      128 +    d = despesa(valor=Decimal("100.00"), tem_nota_fiscal=False
          +)  # base, valor_base 100                                     
      129 +    assert regras.valida_nota_fiscal(d, Decimal("100")) is Non
          +e                                                             
      130 +    acima = despesa(valor=Decimal("100.01"), tem_nota_fiscal=F
          +alse)                                                         
      131 +    assert regras.valida_nota_fiscal(acima, Decimal("100")) is
          + Motivo.SEM_NOTA_FISCAL                                       
      132  
      133  
      134  # ------------------------------------------------------------
           --------------- #
      114 -# RN-009 — tetos de viagem (T-012)                            
      135 +# RN-008 — duplicatas (chave inclui moeda/valor de origem, ign
          +ora id)                                                       
      136  # ------------------------------------------------------------
           --------------- #
      116 -def test_rn_009_tetos_viagem():                               
      117 -    tetos = regras.tetos_efetivos(em_viagem=True)             
      118 -    assert tetos["alimentacao"] == Decimal("90.00")           
      119 -    assert tetos["transporte_urbano"] == Decimal("120.00")    
      120 -    assert tetos["hospedagem"] == Decimal("375.00")           
      137 +def test_rn_008_mantem_primeira():                            
      138 +    a = despesa(id="d-006", descricao="Almoco", valor=Decimal(
          +"54.90"))                                                     
      139 +    b = despesa(id="d-007", descricao="Almoco", valor=Decimal(
          +"54.90"))                                                     
      140 +    assert a.chave_duplicidade() == b.chave_duplicidade()  # s
          +ao duplicatas                                                 
      141  
      142  
      123 -def test_rn_009_nf_nao_escala():                              
      124 -    # O limiar de NF continua 100 mesmo em viagem: 100,01 sem 
          -NF ainda recusa.                                              
      125 -    d = despesa(valor=Decimal("100.01"), tem_nota_fiscal=False
          -)                                                             
      126 -    assert regras.valida_nota_fiscal(d) is Motivo.SEM_NOTA_FIS
          -CAL                                                           
      143 +def test_rn_008_moeda_diferencia():                           
      144 +    # Iguais salvo a moeda NAO sao duplicados (RN-008 usa moed
          +a de origem).                                                 
      145 +    brl = despesa(valor=Decimal("50.00"), data="2026-07-14")  
      146 +    usd = despesa(valor=Decimal("50.00"), data="2026-07-14", m
          +oeda="USD")                                                   
      147 +    assert brl.chave_duplicidade() != usd.chave_duplicidade() 
      148  
      149  
      129 -def test_rn_009_sem_viagem_tetos_base():                      
      130 -    tetos = regras.tetos_efetivos(em_viagem=False)            
      131 -    assert tetos["alimentacao"] == Decimal("60.00")           
      132 -    assert tetos["transporte_urbano"] == Decimal("80.00")     
      133 -    assert tetos["hospedagem"] == Decimal("250.00")           
      134 -                                                              
      135 -                                                              
      150  # ------------------------------------------------------------
           --------------- #
      137 -# RN-002 / RN-003 — tetos diarios (T-013)                     
      151 +# RN-002 — teto de periodicidade "dia" (baldes por viagem)    
      152  # ------------------------------------------------------------
           --------------- #
      153  def test_rn_002_soma_dia():
      154      aceitas = [
      141 -        despesa(data="2026-07-03", valor=Decimal("72.50")),   
      142 -        despesa(data="2026-07-03", valor=Decimal("38.00")),   
      155 +        aceita("72.50", data="2026-07-03"),                   
      156 +        aceita("38.00", data="2026-07-03"),                   
      157      ]
      144 -    assert regras.aplica_teto_diario(aceitas, Decimal("60")) =
          -= Decimal("60.00")                                            
      158 +    # min(110,50, 75) = 75 (nao-viagem).                      
      159 +    assert regras.aplica_teto_dia(aceitas, Decimal("75"), Deci
          +mal("1.5")) == Decimal("75.00")                               
      160  
      161  
      147 -def test_rn_003_transporte():                                 
      148 -    aceitas = [despesa(data="2026-07-06", valor=Decimal("100.0
          -0"))]                                                         
      149 -    assert regras.aplica_teto_diario(aceitas, Decimal("80")) =
          -= Decimal("80.00")                                            
      150 -                                                              
      151 -                                                              
      152 -def test_rn_002_dias_distintos_somam():                       
      162 +def test_rn_002_baldes_dia_misto():                           
      163 +    # BRL 80 (base) + convertido 80 (viagem) no mesmo dia; lim
          +ite base 90 / viagem 135.                                     
      164      aceitas = [
      154 -        despesa(data="2026-07-03", valor=Decimal("50.00")),   
      155 -        despesa(data="2026-07-04", valor=Decimal("50.00")),   
      165 +        aceita("80.00", data="2026-07-14", em_viagem=False),  
      166 +        aceita("80.00", data="2026-07-14", em_viagem=True),   
      167      ]
      157 -    assert regras.aplica_teto_diario(aceitas, Decimal("60")) =
          -= Decimal("100.00")                                           
      168 +    # min(80,90) + min(80,135) = 80 + 80 = 160.               
      169 +    assert regras.aplica_teto_dia(aceitas, Decimal("90"), Deci
          +mal("1.5")) == Decimal("160.00")                              
      170  
      171  
      172  # ------------------------------------------------------------
           --------------- #
      161 -# RN-004 — teto de hospedagem por registro (T-014)            
      173 +# RN-003 — teto de periodicidade "diaria" (por registro)      
      174  # ------------------------------------------------------------
           --------------- #
      163 -def test_rn_004_por_registro():                               
      164 -    aceitas = [despesa(id="d-010", valor=Decimal("480.00"))]  
      165 -    assert regras.aplica_teto_hospedagem(aceitas, Decimal("250
          -")) == Decimal("250.00")                                      
      175 +def test_rn_003_diaria_por_registro():                        
      176 +    aceitas = [aceita("480.00", data="2026-07-14")]           
      177 +    assert regras.aplica_teto_diaria(aceitas, Decimal("250"), 
          +Decimal("1.5")) == Decimal("250.00")                          
      178  
      179  
      168 -def test_rn_004_dois_registros_no_dia_nao_agregam():          
      169 -    aceitas = [                                               
      170 -        despesa(valor=Decimal("200.00")),                     
      171 -        despesa(valor=Decimal("200.00")),                     
      172 -    ]                                                         
      173 -    # Cada registro tem seu proprio teto de 250: 200 + 200 = 4
          -00.                                                           
      174 -    assert regras.aplica_teto_hospedagem(aceitas, Decimal("250
          -")) == Decimal("400.00")                                      
      180 +def test_rn_003_dois_registros_no_dia_nao_agregam():          
      181 +    aceitas = [aceita("200.00"), aceita("200.00")]            
      182 +    assert regras.aplica_teto_diaria(aceitas, Decimal("250"), 
          +Decimal("1.5")) == Decimal("400.00")                          
      183  
      184  
      185  # ------------------------------------------------------------
           --------------- #
      178 -# RN-005 — reembolso parcial no teto (T-013)                  
      186 +# RN-004 — origem do teto (limite pela politica, sem categoria
          + privilegiada)                                                
      187  # ------------------------------------------------------------
           --------------- #
      180 -def test_rn_005_reembolso_parcial_mantem_aceito_cheio():      
      181 -    aceitas = [despesa(valor=Decimal("100.00"))]              
      182 -    reembolso = regras.aplica_teto_diario(aceitas, Decimal("80
          -"))                                                           
      188 +def test_rn_004_limite_pela_politica():                       
      189 +    aceitas = [aceita("100.00", data="2026-07-05")]           
      190 +    # Mesmas aceitas, so muda o `limite` argumento -> muda o t
          +eto (vem da politica).                                        
      191 +    assert regras.aplica_teto_dia(aceitas, Decimal("60"), Deci
          +mal("1.5")) == Decimal("60.00")                               
      192 +    assert regras.aplica_teto_dia(aceitas, Decimal("80"), Deci
          +mal("1.5")) == Decimal("80.00")                               
      193 +                                                              
      194 +                                                              
      195 +# ------------------------------------------------------------
          +--------------- #                                             
      196 +# RN-009 — limite ampliado em viagem (por registro)           
      197 +# ------------------------------------------------------------
          +--------------- #                                             
      198 +def test_rn_009_viagem_por_registro():                        
      199 +    viagem = [aceita("1200.00", em_viagem=True)]              
      200 +    nao = [aceita("1200.00", em_viagem=False)]                
      201 +    # diaria: limite 400; viagem -> 400 x 1,5 = 600.          
      202 +    assert regras.aplica_teto_diaria(viagem, Decimal("400"), D
          +ecimal("1.5")) == Decimal("600.00")                           
      203 +    assert regras.aplica_teto_diaria(nao, Decimal("400"), Deci
          +mal("1.5")) == Decimal("400.00")                              
      204 +                                                              
      205 +                                                              
      206 +# ------------------------------------------------------------
          +--------------- #                                             
      207 +# RN-005 — reembolso parcial no teto (aceita com valor cheio) 
      208 +# ------------------------------------------------------------
          +--------------- #                                             
      209 +def test_rn_005_parcial_no_teto():                            
      210 +    aceitas = [aceita("100.00", data="2026-07-05")]           
      211 +    reembolso = regras.aplica_teto_dia(aceitas, Decimal("80"),
          + Decimal("1.5"))                                              
      212      rc = regras.agrega_categoria(aceitas, [], reembolso)
      213      assert rc.total_aceito == Decimal("100.00")  # aceita com 
           valor cheio
      214      assert rc.total_reembolso == Decimal("80.00")  # limitada 
           ao teto
      215  
      216  
      217  # ------------------------------------------------------------
           --------------- #
      189 -# RN-014 / RN-012 — agregacao (T-015)                         
      218 +# RN-014 — total_despesas exclui valor <= 0 e cambio nao ident
          +ificado                                                       
      219  # ------------------------------------------------------------
           --------------- #
      191 -def test_rn_014_total_despesas():                             
      192 -    # RN-014/D-004: total_despesas soma aceitas + reprovadas, 
          -mas exclui valores                                            
      193 -    # <= 0. O estorno d-009 (-45,00) NAO entra: 100,00 + 100,0
          -1 = 200,01.                                                   
      194 -    aceitas = [despesa(id="d-003", valor=Decimal("100.00"))]  
      195 -    reprovadas = [                                            
      196 -        (despesa(id="d-004", valor=Decimal("100.01")), Motivo.
          -SEM_NOTA_FISCAL),                                             
      197 -        (despesa(id="d-009", valor=Decimal("-45.00")), Motivo.
          -VALOR_INVALIDO),                                              
      198 -    ]                                                         
      199 -    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal(
          -"80.00"))                                                     
      200 -    assert rc.total_despesas == Decimal("200.01")             
      201 -    assert rc.total_aceito == Decimal("100.00")               
      202 -                                                              
      203 -                                                              
      220  def test_rn_014_exclui_valor_nao_positivo():
      205 -    # D-004 (opcao A): a exclusao e POR VALOR, nao pelo motivo
          -. Uma despesa                                                 
      206 -    # negativa recusada por um gate anterior ao de valor (ex.:
          - duplicidade)                                                 
      207 -    # tambem fica fora de total_despesas.                     
      208 -    aceitas = [despesa(valor=Decimal("50.00"))]               
      221 +    aceitas = [aceita("50.00")]                               
      222      reprovadas = [
      210 -        (despesa(valor=Decimal("-10.00")), Motivo.REGISTRO_DUP
          -LICADO),                                                      
      211 -        (despesa(valor=Decimal("0.00")), Motivo.DATA_FORA_COMP
          -ETENCIA),                                                     
      212 -        (despesa(valor=Decimal("30.00")), Motivo.SEM_NOTA_FISC
          -AL),                                                          
      223 +        (aceita("-10.00"), Motivo.REGISTRO_DUPLICADO),        
      224 +        (aceita("0.00"), Motivo.DATA_FORA_COMPETENCIA),       
      225 +        (aceita("30.00"), Motivo.SEM_NOTA_FISCAL),            
      226      ]
      227      rc = regras.agrega_categoria(aceitas, reprovadas, Decimal(
           "50.00"))
      215 -    # 50,00 (aceita) + 30,00 (reprovada positiva); -10,00 e 0,
          -00 excluidos.                                                 
      228 +    # 50 (aceita) + 30 (reprovada positiva); -10 e 0 excluidos
          + por valor.                                                   
      229      assert rc.total_despesas == Decimal("80.00")
      230      assert rc.total_aceito == Decimal("50.00")
      231  
      232  
      233 +def test_rn_014_exclui_cambio_nao_id():                       
      234 +    aceitas = [aceita("100.00")]                              
      235 +    gbp = despesa(moeda="GBP", data="2026-07-14", valor=Decima
          +l("55.00"))                                                   
      236 +    regras.valida_cambio(gbp, __import__("tests._apoio", froml
          +ist=["CAMBIO_PADRAO"]).CAMBIO_PADRAO)                         
      237 +    reprovadas = [(gbp, Motivo.CAMBIO_NAO_IDENTIFICADO)]      
      238 +    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal(
          +"100.00"))                                                    
      239 +    assert gbp.valor_base is None                             
      240 +    assert rc.total_despesas == Decimal("100.00")  # gbp fora 
          +do total (AMB-017)                                            
      241 +                                                              
      242 +                                                              
      243  def test_invariante_totais():
      221 -    aceitas = [despesa(valor=Decimal("100.00"))]              
      222 -    reprovadas = [(despesa(valor=Decimal("100.01")), Motivo.SE
          -M_NOTA_FISCAL)]                                               
      244 +    aceitas = [aceita("100.00")]                              
      245 +    reprovadas = [(aceita("100.01"), Motivo.SEM_NOTA_FISCAL)] 
      246      rc = regras.agrega_categoria(aceitas, reprovadas, Decimal(
           "80.00"))
      247      assert rc.total_despesas >= rc.total_aceito >= rc.total_re
           embolso
      225 -                                                              
      226 -                                                              
      227 -def test_rn_012_agrega_aceitas_e_reprovadas():                
      228 -    aceitas = [despesa(valor=Decimal("50.00"))]               
      229 -    reprovadas = [(despesa(valor=Decimal("30.00")), Motivo.REG
          -ISTRO_DUPLICADO)]                                             
      230 -    rc = regras.agrega_categoria(aceitas, reprovadas, Decimal(
          -"50.00"))                                                     
      231 -    assert rc.total_aceito == Decimal("50.00")                
      232 -    assert rc.total_despesas == Decimal("80.00")              
      233 -    assert [r.id for r in rc.reprovadas] == ["d-x"]           

● Let me clean up that awkward __import__ in test_rn_014_exclui_cambio_nao_id:

● Update(tests\test_regras.py)
  ⎿  Added 1 line, removed 1 line
       8  
       9  from src import regras
      10  from src.modelo import Motivo
      11 -from tests._apoio import aceita, config, despesa, periodo      
      11 +from tests._apoio import CAMBIO_PADRAO, aceita, config, despesa
         +, periodo                                                      
      12  
      13  
      14  # -------------------------------------------------------------
          -------------- #

● Update(tests\test_regras.py)
  ⎿  Added 1 line, removed 1 line
      233  def test_rn_014_exclui_cambio_nao_id():
      234      aceitas = [aceita("100.00")]
      235      gbp = despesa(moeda="GBP", data="2026-07-14", valor=Decima
           l("55.00"))
      236 -    regras.valida_cambio(gbp, __import__("tests._apoio", froml
          -ist=["CAMBIO_PADRAO"]).CAMBIO_PADRAO)                         
      236 +    regras.valida_cambio(gbp, CAMBIO_PADRAO)                  
      237      reprovadas = [(gbp, Motivo.CAMBIO_NAO_IDENTIFICADO)]
      238      rc = regras.agrega_categoria(aceitas, reprovadas, Decimal(
           "100.00"))
      239      assert gbp.valor_base is None

● Now T-040 test_calculo.py (pipeline, including RN-012 and RN-016):

● Write(tests\test_calculo.py)
  ⎿  Added 90 lines, removed 45 lines
        1 -"""Testes do pipeline `src.calculo` (ordem dos gates, dedup, c
          -ategorias) (T-016)."""                                        
        1 +"""Testes do pipeline `src.calculo` (T-040), spec 1.4.        
        2  
        3 +Ordem dos gates (com conversao), exclusao de cambio nao identi
          +ficado, categorias                                            
        4 +dinamicas e agregacao em valor_base. Cobre RN-012 e RN-016.   
        5 +"""                                                           
        6 +                                                              
        7  from decimal import Decimal
        8  
        9  from src.calculo import calcula
       10  from src.modelo import Colaborador, Motivo
        7 -from src.regras import ORDEM_CATEGORIAS                       
        8 -from tests._apoio import bruto, periodo                       
       11 +from src.modelo import motivo_texto                           
       12 +from tests._apoio import CAMBIO_PADRAO, bruto, config, periodo
          +, politica                                                    
       13  
       10 -COLAB = Colaborador(id="c-1", nome="Fulano", centro_custo="CC-
          -1")                                                           
       14 +COLAB = Colaborador(id="c-1", nome="Fulano", centro_custo="CC-
          +X")                                                           
       15  
       16  
       13 -def _calcula(despesas, em_viagem=False):                      
       14 -    return calcula(despesas, COLAB, periodo(), em_viagem)     
       17 +def _calcula(despesas, pol):                                  
       18 +    return calcula(despesas, COLAB, periodo(), pol, CAMBIO_PAD
          +RAO)                                                          
       19  
       20  
       17 -def test_ordem_primeiro_gate():                               
       18 -    # d-013 esta no periodo mas e sem NF e acima do teto: o pr
          -imeiro gate que                                               
       19 -    # falha (NF) define o motivo, nao o teto.                 
       20 -    r = _calcula([bruto(categoria="hospedagem", valor=Decimal(
          -"690.00"),                                                    
       21 -                        tem_nota_fiscal=False, data="2026-07-2
          -2")])                                                         
       22 -    assert r.categorias["hospedagem"].reprovadas[0].motivo is 
          -Motivo.SEM_NOTA_FISCAL                                        
       21 +def test_ordem_gates_cambio():                                
       22 +    # GBP (cambio nao id) numa categoria valida, tambem fora d
          +o periodo: o gate de                                          
       23 +    # cambio (6) vem antes de periodo (8) -> reporta cambio na
          +o identificado.                                               
       24 +    pol = politica(padrao={"representacao": config("300")})   
       25 +    r = _calcula(                                             
       26 +        [bruto(categoria="representacao", moeda="GBP", data="2
          +026-04-01", valor=Decimal("55.00"))],                         
       27 +        pol,                                                  
       28 +    )                                                         
       29 +    assert r.categorias["representacao"].reprovadas[0].motivo 
          +is (                                                          
       30 +        Motivo.CAMBIO_NAO_IDENTIFICADO                        
       31 +    )                                                         
       32  
       33  
       25 -def test_ordem_periodo_antes_de_nf():                         
       26 -    # Fora do periodo E sem NF acima de 100: deve reportar "da
          -ta fora da                                                    
       27 -    # competencia" (periodo e gate anterior a NF).            
       28 -    r = _calcula([bruto(categoria="transporte_urbano", valor=D
          -ecimal("150.00"),                                             
       29 -                        tem_nota_fiscal=False, data="2026-04-0
          -1")])                                                         
       30 -    assert r.categorias["transporte_urbano"].reprovadas[0].mot
          -ivo is (                                                      
       31 -        Motivo.DATA_FORA_COMPETENCIA                          
       34 +def test_limite_zero_prevalece_sobre_nf_e_cambio():           
       35 +    # hospedagem limite 0: "nao reembolsavel" (gate 5) prevale
          +ce sobre sem NF e                                             
       36 +    # sobre cambio nao identificado (GBP).                    
       37 +    pol = politica(padrao={"hospedagem": config("0", "diaria",
          + "nao reembolsavel")})                                        
       38 +    r = _calcula(                                             
       39 +        [bruto(categoria="hospedagem", moeda="GBP", data="2026
          +-07-14", valor=Decimal("690.00"), tem_nota_fiscal=False)],    
       40 +        pol,                                                  
       41      )
       42 +    rep = r.categorias["hospedagem"].reprovadas[0]            
       43 +    assert motivo_texto(rep.motivo) == "nao reembolsavel"     
       44  
       45  
       35 -def test_categorias_sempre_presentes():                       
       36 -    r = _calcula([])                                          
       37 -    assert set(r.categorias.keys()) == set(ORDEM_CATEGORIAS)  
       38 -    for cat in ORDEM_CATEGORIAS:                              
       39 -        rc = r.categorias[cat]                                
       40 -        assert rc.total_despesas == Decimal("0")              
       41 -        assert rc.total_aceito == Decimal("0")                
       42 -        assert rc.total_reembolso == Decimal("0")             
       46 +def test_agrega_exclui_cambio_nao_id():                       
       47 +    # e-006-like: GBP em categoria valida -> reprovada, fora d
          +e total_despesas.                                             
       48 +    pol = politica(padrao={"representacao": config("300")})   
       49 +    r = _calcula(                                             
       50 +        [                                                     
       51 +            bruto(id="ok", categoria="representacao", data="20
          +26-07-13", valor=Decimal("340.00")),                          
       52 +            bruto(id="gbp", categoria="representacao", moeda="
          +GBP", data="2026-07-14", valor=Decimal("55.00")),             
       53 +        ],                                                    
       54 +        pol,                                                  
       55 +    )                                                         
       56 +    rep = r.categorias["representacao"]                       
       57 +    assert rep.total_despesas == Decimal("340.00")  # gbp excl
          +uido                                                          
       58 +    assert any(x.id == "gbp" and x.motivo is Motivo.CAMBIO_NAO
          +_IDENTIFICADO for x in rep.reprovadas)                        
       59  
       60  
       45 -def test_ordem_categorias_fixa():                             
       46 -    r = _calcula([])                                          
       47 -    assert list(r.categorias.keys()) == list(ORDEM_CATEGORIAS)
       61 +def test_categorias_dinamicas_so_com_despesa():               
       62 +    # Politica com 2 categorias, input so com uma -> so ela ap
          +arece (AMB-015).                                              
       63 +    pol = politica(padrao={"alimentacao": config("60"), "trans
          +porte_urbano": config("80")})                                 
       64 +    r = _calcula([bruto(categoria="alimentacao", valor=Decimal
          +("40.00"))], pol)                                             
       65 +    assert list(r.categorias.keys()) == ["alimentacao"]       
       66  
       67  
       50 -def test_categoria_invalida_vai_para_sem_categoria():         
       51 -    r = _calcula([bruto(id="d-005", categoria="coworking", val
          -or=Decimal("89.00"))])                                        
       52 -    assert len(r.reprovadas_sem_categoria) == 1               
       53 -    rep = r.reprovadas_sem_categoria[0]                       
       54 -    assert rep.id == "d-005"                                  
       55 -    assert rep.categoria_informada == "coworking"             
       56 -    assert rep.motivo is Motivo.CATEGORIA_NAO_APLICAVEL       
       68 +def test_rn_012_agrega_valor_base():                          
       69 +    # RN-012 — a agregacao usa o valor JA convertido para a ba
          +se (EUR -> BRL).                                              
       70 +    pol = politica(padrao={"alimentacao": config("200")})     
       71 +    r = _calcula(                                             
       72 +        [bruto(categoria="alimentacao", moeda="EUR", data="202
          +6-07-14", valor=Decimal("22.00"), tem_nota_fiscal=True)],     
       73 +        pol,                                                  
       74 +    )                                                         
       75 +    # 22,00 x 5,93 = 130,46 (base).                           
       76 +    assert r.categorias["alimentacao"].total_aceito == Decimal
          +("130.46")                                                    
       77 +    assert r.categorias["alimentacao"].total_reembolso == Deci
          +mal("130.46")                                                 
       78  
       79  
       80 +def test_rn_016_seleciona_mecanica():                         
       81 +    # RN-016 — a periodicidade escolhe a mecanica; o nome da c
          +ategoria nao influi.                                          
       82 +    despesas = [                                              
       83 +        bruto(id="a", categoria="alimentacao", descricao="cafe
          +", data="2026-07-05", valor=Decimal("100.00")),               
       84 +        bruto(id="b", categoria="alimentacao", descricao="jant
          +ar", data="2026-07-05", valor=Decimal("100.00")),             
       85 +    ]                                                         
       86 +    dia = _calcula(despesas, politica(padrao={"alimentacao": c
          +onfig("150", "dia")}))                                        
       87 +    diaria = _calcula(despesas, politica(padrao={"alimentacao"
          +: config("150", "diaria")}))                                  
       88 +    # "dia": min(200,150)=150; "diaria": min(100,150)+min(100,
          +150)=200.                                                     
       89 +    assert dia.categorias["alimentacao"].total_reembolso == De
          +cimal("150.00")                                               
       90 +    assert diaria.categorias["alimentacao"].total_reembolso ==
          + Decimal("200.00")                                            
       91 +                                                              
       92 +                                                              
       93  def test_registro_invalido_nao_aborta_lote():
       94      invalido = bruto(id="d-bad")
       95      del invalido["data"]
       62 -    valido = bruto(id="d-ok", valor=Decimal("40.00"))         
       63 -    r = _calcula([invalido, valido])                          
       96 +    valido = bruto(id="d-ok", categoria="alimentacao", valor=D
          +ecimal("40.00"))                                              
       97 +    r = _calcula([invalido, valido], politica(padrao={"aliment
          +acao": config("60")}))                                        
       98      assert any(x.motivo is Motivo.REGISTRO_INVALIDO for x in r
           .reprovadas_sem_categoria)
       99      assert r.categorias["alimentacao"].total_aceito == Decimal
           ("40.00")
      100  
      101  
      102 +def test_categoria_invalida_vai_para_sem_categoria():         
      103 +    r = _calcula(                                             
      104 +        [bruto(id="d-005", categoria="coworking", valor=Decima
          +l("89.00"))],                                                 
      105 +        politica(padrao={"alimentacao": config("60")}),       
      106 +    )                                                         
      107 +    assert len(r.reprovadas_sem_categoria) == 1               
      108 +    rep = r.reprovadas_sem_categoria[0]                       
      109 +    assert rep.id == "d-005"                                  
      110 +    assert rep.categoria_informada == "coworking"             
      111 +    assert rep.motivo is Motivo.CATEGORIA_NAO_APLICAVEL       
      112 +                                                              
      113 +                                                              
      114  def test_dedup_no_pipeline_mantem_primeira():
      115      d1 = bruto(id="d-006", valor=Decimal("54.90"))
      116      d2 = bruto(id="d-007", valor=Decimal("54.90"))
       71 -    r = _calcula([d1, d2])                                    
      117 +    r = _calcula([d1, d2], politica(padrao={"alimentacao": con
          +fig("60")}))                                                  
      118      alim = r.categorias["alimentacao"]
      119      assert alim.total_aceito == Decimal("54.90")
      120      assert alim.reprovadas[0].id == "d-007"
      121      assert alim.reprovadas[0].motivo is Motivo.REGISTRO_DUPLIC
           ADO
      122  
      123  
       78 -def test_em_viagem_amplia_teto():                             
       79 -    d = bruto(categoria="alimentacao", valor=Decimal("85.00"),
          - data="2026-07-05")                                           
       80 -    r = _calcula([d], em_viagem=True)                         
       81 -    # 85 <= 90 (teto ampliado) -> reembolso integral.         
       82 -    assert r.categorias["alimentacao"].total_reembolso == Deci
          -mal("85.00")                                                  
      124 +def test_sem_despesa_nenhuma_categoria():                     
      125 +    r = _calcula([], politica(padrao={"alimentacao": config("6
          +0")}))                                                        
      126 +    assert r.categorias == {}                                 
      127 +    assert r.total_reembolso_geral == Decimal("0")            

● Now T-046 test_bordas.py (Section 7 cases across both goldens):

● Write(tests\test_bordas.py)
  ⎿  Added 89 lines, removed 60 lines
      1 -"""Casos de borda da Secao 7 da spec, um teste por linha (T-017)
        -.                                                               
      1 +"""Casos de borda da Secao 7 da spec 1.4, um teste por linha (T-
        +046).                                                           
      2  
      3 -Roda o pipeline sobre o exemplo oficial e verifica o comportamen
        -to de cada `id`.                                                
      3 +Roda o pipeline sobre os inputs oficiais (exemplo em CC-ENG-PLAT
        +AFORMA sem moeda;                                               
      4 +envelope em CC-COMERCIAL com EUR/USD/GBP) e verifica o comportam
        +ento de cada `id`.                                              
      5  """
      6  
      7  from decimal import Decimal
     ...
      10  
      11  from src import io_json
      12  from src.calculo import calcula
      12 -from src.modelo import Motivo                                  
      13 +from src.modelo import Motivo, motivo_texto                    
      14  
      15  
      16  @pytest.fixture(scope="module")
      16 -def resultado(caminho_exemplo):                                
      17 +def exemplo(caminho_exemplo, politica_v4, cambio_real):        
      18      entrada = io_json.ler_entrada(caminho_exemplo)
      19      return calcula(
      19 -        entrada.despesas_brutas, entrada.colaborador, entrada.p
         -eriodo, em_viagem=False                                        
      20 +        entrada.despesas_brutas, entrada.colaborador, entrada.p
         +eriodo, politica_v4, cambio_real                               
      21      )
      22  
      23  
      24 +@pytest.fixture(scope="module")                                
      25 +def envelope(caminho_envelope, politica_v4, cambio_real):      
      26 +    entrada = io_json.ler_entrada(caminho_envelope)            
      27 +    return calcula(                                            
      28 +        entrada.despesas_brutas, entrada.colaborador, entrada.p
         +eriodo, politica_v4, cambio_real                               
      29 +    )                                                          
      30 +                                                               
      31 +                                                               
      32  def _reprovada(resultado, id_):
      24 -    """Localiza a `Reprovacao` de um id em qualquer balde de re
         -cusa."""                                                       
      33      for cat in resultado.categorias.values():
      34          for rep in cat.reprovadas:
      35              if rep.id == id_:
     ...
       46      return ids
       47  
       48  
       41 -def test_borda_soma_diaria_excede_teto(resultado):            
       42 -    # d-001 72,50 + d-002 38,00 no mesmo dia: aceito 110,50; r
          -eembolso do dia 60.                                           
       43 -    alim = resultado.categorias["alimentacao"]                
       44 -    assert "d-001" not in _ids_reprovados(resultado)          
       45 -    assert "d-002" not in _ids_reprovados(resultado)          
       46 -    # 07-03 contribui exatamente com o teto de 60 dentro do to
          -tal_reembolso.                                                
       47 -    assert alim.total_reembolso == Decimal("255.43")          
       49 +# ------------------------------------------------------------
          +--------------- #                                             
       50 +# Exemplo (CC-ENG-PLATAFORMA)                                 
       51 +# ------------------------------------------------------------
          +--------------- #                                             
       52 +def test_borda_soma_diaria_excede_teto(exemplo):              
       53 +    # d-001 72,50 + d-002 38,00 no mesmo dia; limite 75 -> ree
          +mbolso do dia 75.                                             
       54 +    assert "d-001" not in _ids_reprovados(exemplo)            
       55 +    assert "d-002" not in _ids_reprovados(exemplo)            
       56 +    assert exemplo.categorias["alimentacao"].total_reembolso =
          += Decimal("271.43")                                           
       57  
       58  
       50 -def test_borda_d003_limiar_nf_exato(resultado):               
       51 -    # 100,00 sem NF -> aceita.                                
       52 -    assert "d-003" not in _ids_reprovados(resultado)          
       59 +def test_borda_d003_limiar_nf_exato(exemplo):                 
       60 +    assert "d-003" not in _ids_reprovados(exemplo)  # 100,00 s
          +em NF -> aceita                                               
       61  
       62  
       55 -def test_borda_d004_um_centavo_acima(resultado):              
       56 -    # 100,01 sem NF -> recusada por falta de NF.              
       57 -    assert _reprovada(resultado, "d-004").motivo is Motivo.SEM
          -_NOTA_FISCAL                                                  
       63 +def test_borda_d004_um_centavo_acima(exemplo):                
       64 +    assert _reprovada(exemplo, "d-004").motivo is Motivo.SEM_N
          +OTA_FISCAL                                                    
       65  
       66  
       60 -def test_borda_d005_categoria_fora(resultado):                
       61 -    rep = _reprovada(resultado, "d-005")                      
       67 +def test_borda_d005_categoria_fora(exemplo):                  
       68 +    rep = _reprovada(exemplo, "d-005")                        
       69      assert rep.motivo is Motivo.CATEGORIA_NAO_APLICAVEL
       63 -    assert rep in resultado.reprovadas_sem_categoria          
       70 +    assert rep in exemplo.reprovadas_sem_categoria            
       71  
       72  
       66 -def test_borda_d006_d007_duplicata(resultado):                
       67 -    assert "d-006" not in _ids_reprovados(resultado)          
       68 -    assert _reprovada(resultado, "d-007").motivo is Motivo.REG
          -ISTRO_DUPLICADO                                               
       73 +def test_borda_d006_d007_duplicata(exemplo):                  
       74 +    assert "d-006" not in _ids_reprovados(exemplo)            
       75 +    assert _reprovada(exemplo, "d-007").motivo is Motivo.REGIS
          +TRO_DUPLICADO                                                 
       76  
       77  
       71 -def test_borda_d008_data_fora(resultado):                     
       72 -    assert _reprovada(resultado, "d-008").motivo is Motivo.DAT
          -A_FORA_COMPETENCIA                                            
       78 +def test_borda_d008_data_fora(exemplo):                       
       79 +    assert _reprovada(exemplo, "d-008").motivo is Motivo.DATA_
          +FORA_COMPETENCIA                                              
       80  
       81  
       75 -def test_borda_d009_valor_negativo(resultado):                
       76 -    assert _reprovada(resultado, "d-009").motivo is Motivo.VAL
          -OR_INVALIDO                                                   
       82 +def test_borda_d009_valor_negativo(exemplo):                  
       83 +    assert _reprovada(exemplo, "d-009").motivo is Motivo.VALOR
          +_INVALIDO                                                     
       84  
       85  
       79 -def test_borda_d010_hospedagem_acima_teto(resultado):         
       80 -    # 480,00 aceito; reembolso limitado a 250.                
       81 -    assert "d-010" not in _ids_reprovados(resultado)          
       82 -    assert resultado.categorias["hospedagem"].total_reembolso 
          -== Decimal("250.00")                                          
       86 +def test_borda_d010_d013_limite_zero(exemplo):                
       87 +    # hospedagem limite 0 em CC-ENG -> "nao reembolsavel" sob 
          +a categoria.                                                  
       88 +    assert motivo_texto(_reprovada(exemplo, "d-010").motivo) =
          += "nao reembolsavel"                                          
       89 +    assert motivo_texto(_reprovada(exemplo, "d-013").motivo) =
          += "nao reembolsavel"                                          
       90 +    hosp = exemplo.categorias["hospedagem"]                   
       91 +    assert hosp.total_aceito == Decimal("0.00")               
       92 +    assert hosp.total_reembolso == Decimal("0.00")            
       93 +    assert hosp.total_despesas == Decimal("1170.00")  # valore
          +s > 0 somam                                                   
       94  
       95  
       85 -def test_borda_d011_mais_de_2_casas(resultado):               
       86 -    # 33,333 -> 33,33; entra em total_aceito de alimentacao.  
       87 -    assert "d-011" not in _ids_reprovados(resultado)          
       88 -    assert resultado.categorias["alimentacao"].total_aceito ==
          - Decimal("306.93")                                            
       96 +def test_borda_d011_mais_de_2_casas(exemplo):                 
       97 +    assert "d-011" not in _ids_reprovados(exemplo)  # 33,333 -
          +> 33,33                                                       
       98 +    assert exemplo.categorias["alimentacao"].total_aceito == D
          +ecimal("306.93")                                              
       99  
      100  
       91 -def test_borda_d012_fim_de_semana_sem_regra(resultado):       
       92 -    # Sabado tratado como qualquer dia -> aceito.             
       93 -    assert "d-012" not in _ids_reprovados(resultado)          
      101 +def test_borda_d012_fim_de_semana_sem_regra(exemplo):         
      102 +    assert "d-012" not in _ids_reprovados(exemplo)  # sabado t
          +ratado como qualquer dia                                      
      103  
      104  
       96 -def test_borda_d013_sem_nf(resultado):                        
       97 -    assert _reprovada(resultado, "d-013").motivo is Motivo.SEM
          -_NOTA_FISCAL                                                  
      105 +def test_borda_d014_caixa_alta_e_data_fim(exemplo):           
      106 +    assert "d-014" not in _ids_reprovados(exemplo)  # ALIMENTA
          +CAO; data == fim elegivel                                     
      107  
      108  
      100 -def test_borda_d014_caixa_alta_e_data_fim(resultado):         
      101 -    # ALIMENTACAO tratada como alimentacao; data == fim e eleg
          -ivel.                                                         
      102 -    assert "d-014" not in _ids_reprovados(resultado)          
      109 +# ------------------------------------------------------------
          +--------------- #                                             
      110 +# Envelope (CC-COMERCIAL, moedas estrangeiras)                
      111 +# ------------------------------------------------------------
          +--------------- #                                             
      112 +def test_borda_e002_moeda_estrangeira_viagem(envelope):       
      113 +    # EUR 22 (07-14, taxa 5,93) -> 130,46; viagem (limite 90 -
          +> 135); aceito integral.                                      
      114 +    assert "e-002" not in _ids_reprovados(envelope)           
      115 +    assert envelope.categorias["alimentacao"].total_aceito >= 
          +Decimal("130.46")                                             
      116  
      117  
      105 -def test_borda_aceita_com_reembolso_zero_por_teto():          
      106 -    # 3a despesa de alimentacao num dia ja no teto: permanece 
          -aceita, reembolso 0.                                          
      107 -    from src.modelo import Colaborador                        
      108 -    from tests._apoio import bruto, periodo                   
      118 +def test_borda_e004_fim_de_semana_taxa_mais_proxima(envelope):
      119 +    # EUR 30 (07-18 sabado -> 07-17 5,96) = 178,80; viagem lim
          +ite 135 -> reembolso 135.                                     
      120 +    assert "e-004" not in _ids_reprovados(envelope)           
      121  
      110 -    # Descricoes distintas para nao serem tratadas como duplic
          -atas (RN-008).                                                
      111 -    despesas = [                                              
      112 -        bruto(id="a", descricao="cafe", valor=Decimal("40.00")
          -, data="2026-07-05"),                                         
      113 -        bruto(id="b", descricao="almoco", valor=Decimal("40.00
          -"), data="2026-07-05"),                                       
      114 -        bruto(id="c", descricao="jantar", valor=Decimal("40.00
          -"), data="2026-07-05"),                                       
      115 -    ]                                                         
      116 -    r = calcula(despesas, Colaborador("c", "n", "cc"), periodo
          -(), em_viagem=False)                                          
      117 -    alim = r.categorias["alimentacao"]                        
      118 -    assert alim.total_aceito == Decimal("120.00")  # todas ace
          -itas com valor cheio                                          
      119 -    assert alim.total_reembolso == Decimal("60.00")  # teto do
          - dia                                                          
      120 -    assert _ids_reprovados(r) == set()                        
      122 +                                                              
      123 +def test_borda_e005_nf_apos_conversao(envelope):              
      124 +    # USD 40 (07-20 5,50) = 220 > 100 e sem NF -> recusada.   
      125 +    assert _reprovada(envelope, "e-005").motivo is Motivo.SEM_
          +NOTA_FISCAL                                                   
      126 +                                                              
      127 +                                                              
      128 +def test_borda_e006_cambio_nao_identificado(envelope):        
      129 +    # GBP ausente de todas as taxas -> cambio nao identificado
          + sob representacao.                                           
      130 +    rep = _reprovada(envelope, "e-006")                       
      131 +    assert rep.motivo is Motivo.CAMBIO_NAO_IDENTIFICADO       
      132 +    # Fora de total_despesas (AMB-017).                       
      133 +    assert envelope.categorias["representacao"].total_despesas
          + == Decimal("340.00")                                         
      134 +                                                              
      135 +                                                              
      136 +def test_borda_e009_categoria_fora_do_cc(envelope):           
      137 +    rep = _reprovada(envelope, "e-009")                       
      138 +    assert rep.motivo is Motivo.CATEGORIA_NAO_APLICAVEL       
      139 +    assert rep in envelope.reprovadas_sem_categoria           
      140 +                                                              
      141 +                                                              
      142 +def test_borda_e010_sem_moeda_nao_e_viagem(envelope):         
      143 +    # e-010 sem `moeda` -> base, nao viagem; aceito.          
      144 +    assert "e-010" not in _ids_reprovados(envelope)           
      145 +                                                              
      146 +                                                              
      147 +def test_borda_e008_moeda_base_sem_conversao(envelope):       
      148 +    # e-008 BRL 95 (= base) -> sem conversao, nao viagem; min(
          +95,90)=90.                                                    
      149 +    assert "e-008" not in _ids_reprovados(envelope)           

● Now T-049/T-041 test_io.py (serialization without em_viagem, dynamic category
  order):
● Write(tests\test_io.py)
  ⎿  Added 43 lines, removed 15 lines
      1 -"""Testes de leitura e serializacao (`src.io_json`) (T-018, T-01
        -9)."""                                                          
      1 +"""Testes de leitura e serializacao (`src.io_json`) (T-030/T-041
        +/T-049), spec 1.4."""                                           
      2  
      3  import json
      4  from decimal import Decimal
     ...
      10  
      11  
      12  @pytest.fixture
      13 -def resultado_exemplo(caminho_exemplo):                        
      13 +def resultado_exemplo(caminho_exemplo, politica_v4, cambio_real
         +):                                                             
      14      entrada = io_json.ler_entrada(caminho_exemplo)
      15      return calcula(
      16 -        entrada.despesas_brutas, entrada.colaborador, entrada.p
         -eriodo, em_viagem=False                                        
      16 +        entrada.despesas_brutas, entrada.colaborador, entrada.p
         +eriodo, politica_v4, cambio_real                               
      17      )
      18  
      19  
      20 +@pytest.fixture                                                
      21 +def resultado_envelope(caminho_envelope, politica_v4, cambio_re
         +al):                                                           
      22 +    entrada = io_json.ler_entrada(caminho_envelope)            
      23 +    return calcula(                                            
      24 +        entrada.despesas_brutas, entrada.colaborador, entrada.p
         +eriodo, politica_v4, cambio_real                               
      25 +    )                                                          
      26 +                                                               
      27 +                                                               
      28  # -------------------------------------------------------------
          -------------- #
      21 -# Leitura (T-018)                                              
      29 +# Leitura                                                      
      30  # -------------------------------------------------------------
          -------------- #
      31  def test_leitura_decimal(caminho_exemplo):
      32      entrada = io_json.ler_entrada(caminho_exemplo)
      33      for registro in entrada.despesas_brutas:
      34          assert isinstance(registro["valor"], (Decimal, int))
      35          assert not isinstance(registro["valor"], float)
      28 -    # d-011 tem 3 casas: precisa chegar como Decimal preservand
         -o o texto.                                                     
      36      d011 = next(r for r in entrada.despesas_brutas if r["id"] =
          = "d-011")
      37      assert d011["valor"] == Decimal("33.333")
      38  
      39  
      40 +def test_ler_entrada_nao_le_em_viagem(caminho_exemplo):        
      41 +    entrada = io_json.ler_entrada(caminho_exemplo)             
      42 +    assert not hasattr(entrada, "em_viagem")                   
      43 +                                                               
      44 +                                                               
      45  def test_json_topo_invalido_erro(tmp_path):
      46      ruim = tmp_path / "ruim.json"
      47      ruim.write_text("{ isto nao e json", encoding="utf-8")
     ...
      62  
      63  
      64  # -------------------------------------------------------------
          -------------- #
      53 -# Serializacao (T-019)                                         
      65 +# Serializacao                                                 
      66  # -------------------------------------------------------------
          -------------- #
      67 +def test_saida_sem_em_viagem(resultado_exemplo):               
      68 +    dados = json.loads(io_json.serializa(resultado_exemplo))   
      69 +    assert "em_viagem" not in dados                            
      70 +                                                               
      71 +                                                               
      72  def test_serializa_2_casas(resultado_exemplo):
      73      texto = io_json.serializa(resultado_exemplo)
      57 -    # Todo numero monetario aparece com exatamente 2 casas.    
      58 -    assert '"total_reembolso_geral": 585.43' in texto          
      74 +    assert '"total_reembolso_geral": 351.43' in texto          
      75      assert '"total_aceito": 100.00' in texto
      60 -    assert '"total_reembolso": 250.00' in texto                
      61 -    # Parse de volta confere igualdade numerica.               
      76      dados = json.loads(texto)
      63 -    assert dados["total_reembolso_geral"] == 585.43            
      77 +    assert dados["total_reembolso_geral"] == 351.43            
      78  
      79  
      80  def test_acentos_preservados(resultado_exemplo):
     ...
       83      assert "\\u00" not in texto  # sem escape unicode
       84  
       85  
       86 +def test_ordem_categorias_por_politica(resultado_envelope):   
       87 +    # DT-011 — ordem das chaves do CC-COMERCIAL na politica.  
       88 +    dados = json.loads(io_json.serializa(resultado_envelope)) 
       89 +    assert list(dados["categorias"].keys()) == [              
       90 +        "alimentacao",                                        
       91 +        "transporte_urbano",                                  
       92 +        "hospedagem",                                         
       93 +        "representacao",                                      
       94 +    ]                                                         
       95 +                                                              
       96 +                                                              
       97 +def test_cambio_nao_identificado_serializado(resultado_envelop
          +e):                                                           
       98 +    texto = io_json.serializa(resultado_envelope)             
       99 +    assert "cambio não identificado" in texto                 
      100 +                                                              
      101 +                                                              
      102  def test_reprovada_sem_categoria_tem_categoria_informada(resul
           tado_exemplo):
       73 -    texto = io_json.serializa(resultado_exemplo)              
       74 -    dados = json.loads(texto)                                 
      103 +    dados = json.loads(io_json.serializa(resultado_exemplo))  
      104      rep = dados["reprovadas_sem_categoria"][0]
      105      assert rep["id"] == "d-005"
      106      assert rep["categoria_informada"] == "coworking"
     ...
      108  
      109  
      110  def test_reprovadas_de_categoria_so_id_e_motivo(resultado_exem
           plo):
       82 -    texto = io_json.serializa(resultado_exemplo)              
       83 -    dados = json.loads(texto)                                 
      111 +    dados = json.loads(io_json.serializa(resultado_exemplo))  
      112      for rep in dados["categorias"]["transporte_urbano"]["repro
           vadas"]:
      113          assert set(rep.keys()) == {"id", "motivo"}

● Now T-042/T-049 test_cli.py (no --em-viagem, --politica/--cambio, abort on
  missing câmbio):

● Write(tests\test_cli.py)
  ⎿  Added 52 lines, removed 21 lines
      1 -"""Testes da CLI `calcular` (T-020, T-021)."""                  
      1 +"""Testes da CLI `calcular` (T-042/T-049), spec 1.4."""         
      2  
      3  import json
      4  import subprocess
     ...
      17      codigo = cli.main(["--input", str(caminho_exemplo), "--outp
          ut", str(saida)])
      18      assert codigo == 0
      19      dados = json.loads(saida.read_text(encoding="utf-8"))
      20 -    assert dados["em_viagem"] is False                         
      21 -    assert dados["total_reembolso_geral"] == 585.43            
      20 +    assert dados["total_reembolso_geral"] == 351.43            
      21  
      22  
      24 -def test_cli_em_viagem(caminho_exemplo, tmp_path):             
      23 +def test_cli_sem_em_viagem(caminho_exemplo, tmp_path):         
      24 +    # Nao ha mais flag --em-viagem; a saida nao tem o campo em_
         +viagem.                                                        
      25      saida = tmp_path / "resultado.json"
      26 -    codigo = cli.main(                                         
      27 -        ["--input", str(caminho_exemplo), "--output", str(saida
         -), "--em-viagem"]                                              
      28 -    )                                                          
      26 +    codigo = cli.main(["--input", str(caminho_exemplo), "--outp
         +ut", str(saida)])                                              
      27      assert codigo == 0
      28      dados = json.loads(saida.read_text(encoding="utf-8"))
      31 -    assert dados["em_viagem"] is True                          
      29 +    assert "em_viagem" not in dados                            
      30  
      31  
      34 -def test_cli_exit_code_input_inexistente(tmp_path, capsys):    
      32 +def test_cli_em_viagem_flag_rejeitada(caminho_exemplo, tmp_path
         +):                                                             
      33      saida = tmp_path / "resultado.json"
      34 +    with pytest.raises(SystemExit) as exc:                     
      35 +        cli.main(["--input", str(caminho_exemplo), "--output", 
         +str(saida), "--em-viagem"])                                    
      36 +    assert exc.value.code == 2  # argparse: argumento desconhec
         +ido                                                            
      37 +                                                               
      38 +                                                               
      39 +def test_cli_defaults_empacotados(caminho_envelope, tmp_path): 
      40 +    # Sem --politica/--cambio usa os arquivos empacotados em sr
         +c/informacoes_externas.                                        
      41 +    saida = tmp_path / "resultado.json"                        
      42 +    codigo = cli.main(["--input", str(caminho_envelope), "--out
         +put", str(saida)])                                             
      43 +    assert codigo == 0                                         
      44 +    dados = json.loads(saida.read_text(encoding="utf-8"))      
      45 +    assert dados["total_reembolso_geral"] == 1228.72           
      46 +                                                               
      47 +                                                               
      48 +def test_cli_cambio_ausente_exit1(caminho_exemplo, tmp_path, ca
         +psys):                                                         
      49 +    saida = tmp_path / "resultado.json"                        
      50      codigo = cli.main(
      37 -        ["--input", str(tmp_path / "nao-existe.json"), "--outpu
         -t", str(saida)]                                                
      51 +        [                                                      
      52 +            "--input", str(caminho_exemplo),                   
      53 +            "--output", str(saida),                            
      54 +            "--cambio", str(tmp_path / "nao-existe.json"),     
      55 +        ]                                                      
      56      )
      57      assert codigo == 1
      58      assert not saida.exists()
      41 -    assert capsys.readouterr().err  # mensagem em stderr       
      59 +    assert capsys.readouterr().err                             
      60  
      61  
      62 +def test_cli_politica_ausente_exit1(caminho_exemplo, tmp_path):
      63 +    saida = tmp_path / "resultado.json"                        
      64 +    codigo = cli.main(                                         
      65 +        [                                                      
      66 +            "--input", str(caminho_exemplo),                   
      67 +            "--output", str(saida),                            
      68 +            "--politica", str(tmp_path / "nao-existe.json"),   
      69 +        ]                                                      
      70 +    )                                                          
      71 +    assert codigo == 1                                         
      72 +    assert not saida.exists()                                  
      73 +                                                               
      74 +                                                               
      75 +def test_cli_exit_code_input_inexistente(tmp_path, capsys):    
      76 +    saida = tmp_path / "resultado.json"                        
      77 +    codigo = cli.main(["--input", str(tmp_path / "nao-existe.js
         +on"), "--output", str(saida)])                                 
      78 +    assert codigo == 1                                         
      79 +    assert not saida.exists()                                  
      80 +    assert capsys.readouterr().err                             
      81 +                                                               
      82 +                                                               
      83  def test_cli_falta_argumento_exit_2(caminho_exemplo):
      84      with pytest.raises(SystemExit) as exc:
      85          cli.main(["--input", str(caminho_exemplo)])  # falta --
          output
     ...
      89  def test_python_m_src(caminho_exemplo, tmp_path):
      90      saida = tmp_path / "resultado.json"
      91      proc = subprocess.run(
      53 -        [                                                      
      54 -            sys.executable,                                    
      55 -            "-m",                                              
      56 -            "src",                                             
      57 -            "--input",                                         
      58 -            str(caminho_exemplo),                              
      59 -            "--output",                                        
      60 -            str(saida),                                        
      61 -        ],                                                     
      92 +        [sys.executable, "-m", "src", "--input", str(caminho_ex
         +emplo), "--output", str(saida)],                               
      93          cwd=_RAIZ,
      94          capture_output=True,
      95          text=True,
      96      )
      97      assert proc.returncode == 0, proc.stderr
      98      dados = json.loads(saida.read_text(encoding="utf-8"))
      68 -    assert dados["total_reembolso_geral"] == 585.43            
      99 +    assert dados["total_reembolso_geral"] == 351.43            

● Now T-048 test_integracao.py (both goldens, full JSON comparison):

● Write(tests\test_integracao.py)
  ⎿  Added 62 lines, removed 50 lines
      1 -"""Golden test ponta a ponta contra a saida da Secao 4 da spec (
        -T-022)."""                                                      
      1 +"""Goldens ponta a ponta contra a spec 1.4 (T-048).             
      2  
      3 +Golden 1: `despesas-exemplo.json` (CC-ENG-PLATAFORMA, sem moeda)
        + -> 351,43 (Secao 4).                                           
      4 +Golden 2: `despesas-envelope.json` (CC-COMERCIAL, EUR/USD/GBP) -
        +> 1228,72 (quickstart).                                         
      5 +"""                                                             
      6 +                                                                
      7  import json
      8  from decimal import Decimal
      9  
     ...
       12  from src import io_json
       13  from src.calculo import calcula
       14  
       11 -# Saida esperada exata da Secao 4 da spec (em_viagem = false).
       12 -_ESPERADO_SEM_VIAGEM = """                                    
       15 +_GOLDEN_EXEMPLO = """                                         
       16  {
       14 -  "colaborador": {                                            
       15 -    "id": "c-0417",                                           
       16 -    "nome": "Marina Volpi",                                   
       17 -    "centro_custo": "CC-ENG-PLATAFORMA"                       
       18 -  },                                                          
       17 +  "colaborador": { "id": "c-0417", "nome": "Marina Volpi", "ce
          +ntro_custo": "CC-ENG-PLATAFORMA" },                           
       18    "competencia": "2026-07",
       20 -  "periodo": {                                                
       21 -    "inicio": "2026-07-01",                                   
       22 -    "fim": "2026-07-31"                                       
       23 -  },                                                          
       24 -  "em_viagem": false,                                         
       19 +  "periodo": { "inicio": "2026-07-01", "fim": "2026-07-31" }, 
       20    "categorias": {
       21      "alimentacao": {
       27 -      "total_despesas": 402.83,                               
       28 -      "total_aceito": 306.93,                                 
       29 -      "total_reembolso": 255.43,                              
       22 +      "total_despesas": 402.83, "total_aceito": 306.93, "total
          +_reembolso": 271.43,                                          
       23        "reprovadas": [
       24          { "id": "d-007", "motivo": "registro duplicado" },
       25          { "id": "d-008", "motivo": "data fora da competência" 
           }
       26        ]
       27      },
       28      "transporte_urbano": {
       36 -      "total_despesas": 200.01,                               
       37 -      "total_aceito": 100.00,                                 
       38 -      "total_reembolso": 80.00,                               
       29 +      "total_despesas": 200.01, "total_aceito": 100.00, "total
          +_reembolso": 80.00,                                           
       30        "reprovadas": [
       31          { "id": "d-004", "motivo": "sem nota fiscal obrigatóri
           a" },
       32          { "id": "d-009", "motivo": "valor inválido" }
       33        ]
       34      },
       35      "hospedagem": {
       45 -      "total_despesas": 1170.00,                              
       46 -      "total_aceito": 480.00,                                 
       47 -      "total_reembolso": 250.00,                              
       36 +      "total_despesas": 1170.00, "total_aceito": 0.00, "total_
          +reembolso": 0.00,                                             
       37        "reprovadas": [
       49 -        { "id": "d-013", "motivo": "sem nota fiscal obrigatóri
          -a" }                                                          
       38 +        { "id": "d-010", "motivo": "nao reembolsavel" },      
       39 +        { "id": "d-013", "motivo": "nao reembolsavel" }       
       40        ]
       41      }
       42    },
       43    "reprovadas_sem_categoria": [
       44      { "id": "d-005", "categoria_informada": "coworking", "moti
           vo": "categoria não aplicável" }
       45    ],
       56 -  "total_reembolso_geral": 585.43                             
       46 +  "total_reembolso_geral": 351.43                             
       47  }
       48  """
       49  
       50 +_GOLDEN_ENVELOPE = """                                        
       51 +{                                                             
       52 +  "colaborador": { "id": "c-0912", "nome": "Rafael Nkemelu", "
          +centro_custo": "CC-COMERCIAL" },                              
       53 +  "competencia": "2026-07",                                   
       54 +  "periodo": { "inicio": "2026-07-01", "fim": "2026-07-31" }, 
       55 +  "categorias": {                                             
       56 +    "alimentacao": {                                          
       57 +      "total_despesas": 577.52, "total_aceito": 577.52, "total
          +_reembolso": 528.72,                                          
       58 +      "reprovadas": []                                        
       59 +    },                                                        
       60 +    "transporte_urbano": {                                    
       61 +      "total_despesas": 220.00, "total_aceito": 0.00, "total_r
          +eembolso": 0.00,                                              
       62 +      "reprovadas": [ { "id": "e-005", "motivo": "sem nota fis
          +cal obrigatória" } ]                                          
       63 +    },                                                        
       64 +    "hospedagem": {                                           
       65 +      "total_despesas": 1200.00, "total_aceito": 1200.00, "tot
          +al_reembolso": 400.00,                                        
       66 +      "reprovadas": []                                        
       67 +    },                                                        
       68 +    "representacao": {                                        
       69 +      "total_despesas": 340.00, "total_aceito": 340.00, "total
          +_reembolso": 300.00,                                          
       70 +      "reprovadas": [ { "id": "e-006", "motivo": "cambio não i
          +dentificado" } ]                                              
       71 +    }                                                         
       72 +  },                                                          
       73 +  "reprovadas_sem_categoria": [                               
       74 +    { "id": "e-009", "categoria_informada": "coworking", "moti
          +vo": "categoria não aplicável" }                              
       75 +  ],                                                          
       76 +  "total_reembolso_geral": 1228.72                            
       77 +}                                                             
       78 +"""                                                           
       79  
       61 -def _produz(caminho, em_viagem):                              
       80 +                                                              
       81 +def _produz(caminho, politica, cambio):                       
       82      entrada = io_json.ler_entrada(caminho)
       83      resultado = calcula(
       64 -        entrada.despesas_brutas, entrada.colaborador, entrada.
          -periodo, em_viagem                                            
       84 +        entrada.despesas_brutas, entrada.colaborador, entrada.
          +periodo, politica, cambio                                     
       85      )
       66 -    # Parse com Decimal dos dois lados para comparacao exata d
          -e centavos.                                                   
       86      return json.loads(io_json.serializa(resultado), parse_floa
           t=Decimal)
       87  
       88  
       70 -def test_golden_sem_viagem(caminho_exemplo):                  
       71 -    produzido = _produz(caminho_exemplo, em_viagem=False)     
       72 -    esperado = json.loads(_ESPERADO_SEM_VIAGEM, parse_float=De
          -cimal)                                                        
       89 +def test_golden_exemplo(caminho_exemplo, politica_v4, cambio_r
          +eal):                                                         
       90 +    produzido = _produz(caminho_exemplo, politica_v4, cambio_r
          +eal)                                                          
       91 +    esperado = json.loads(_GOLDEN_EXEMPLO, parse_float=Decimal
          +)                                                             
       92      assert produzido == esperado
       93  
       94  
       76 -def test_golden_invariante_por_categoria(caminho_exemplo):    
       77 -    produzido = _produz(caminho_exemplo, em_viagem=False)     
       95 +def test_golden_envelope(caminho_envelope, politica_v4, cambio
          +_real):                                                       
       96 +    produzido = _produz(caminho_envelope, politica_v4, cambio_
          +real)                                                         
       97 +    esperado = json.loads(_GOLDEN_ENVELOPE, parse_float=Decima
          +l)                                                            
       98 +    assert produzido == esperado                              
       99 +                                                              
      100 +                                                              
      101 +@pytest.mark.parametrize("caminho", ["caminho_exemplo", "camin
          +ho_envelope"])                                                
      102 +def test_invariante_por_categoria(caminho, request, politica_v
          +4, cambio_real):                                              
      103 +    produzido = _produz(request.getfixturevalue(caminho), poli
          +tica_v4, cambio_real)                                         
      104      for cat in produzido["categorias"].values():
      105          assert cat["total_despesas"] >= cat["total_aceito"] >=
            cat["total_reembolso"]
      106  
      107  
       82 -def test_em_viagem_amplia_tetos_mas_nao_nf(caminho_exemplo):  
       83 -    produzido = _produz(caminho_exemplo, em_viagem=True)      
       84 -    cats = produzido["categorias"]                            
       85 -    # Tetos ampliados (90/120/375):                           
       86 -    assert cats["alimentacao"]["total_reembolso"] == Decimal("
          -286.43")                                                      
       87 -    assert cats["transporte_urbano"]["total_reembolso"] == Dec
          -imal("100.00")                                                
       88 -    assert cats["hospedagem"]["total_reembolso"] == Decimal("3
          -75.00")                                                       
       89 -    assert produzido["total_reembolso_geral"] == Decimal("761.
          -43")                                                          
       90 -    # Limiar de NF NAO escala: d-004 e d-013 continuam recusad
          -os.                                                           
       91 -    ids_recusados = {                                         
       92 -        r["id"] for c in cats.values() for r in c["reprovadas"
          -]                                                             
       93 -    } | {r["id"] for r in produzido["reprovadas_sem_categoria"
          -]}                                                            
       94 -    assert {"d-004", "d-013"} <= ids_recusados                
       95 -                                                              
       96 -                                                              
       97 -@pytest.mark.parametrize("em_viagem", [False, True])          
       98 -def test_determinismo(caminho_exemplo, em_viagem):            
       99 -    assert _produz(caminho_exemplo, em_viagem) == _produz(cami
          -nho_exemplo, em_viagem)                                       
      108 +def test_determinismo(caminho_envelope, politica_v4, cambio_re
          +al):                                                          
      109 +    a = _produz(caminho_envelope, politica_v4, cambio_real)   
      110 +    b = _produz(caminho_envelope, politica_v4, cambio_real)   
      111 +    assert a == b                                             

● Now T-047 test_cobertura_rn.py (audit RN-001..RN-020):

● Write(tests\test_cobertura_rn.py)
  ⎿  Added 5 lines, removed 4 lines
      1 -"""Auditoria de rastreabilidade: toda RN-001..RN-014 tem teste (
        -T-023).                                                         
      1 +"""Auditoria de rastreabilidade: toda RN-001..RN-020 tem teste (
        +T-047).                                                         
      2  
      3 -Falha se alguma regra da spec nao possuir ao menos um teste nome
        -ado pela                                                        
      4 -convencao `test_rn_0NN_*` (CLAUDE.md: nenhuma regra sem teste). 
      3 +Falha se alguma regra da spec 1.4 nao possuir ao menos um teste 
        +nomeado pela                                                    
      4 +convencao `test_rn_0NN_*` (CLAUDE.md: nenhuma regra sem teste). 
        +Um teste nomeado por                                            
      5 +outra RN NAO conta pela regra que cobre — a convencao e o numero
        + literal no nome.                                               
      6  """
      7  
      8  import re
     ...
      21  
      22  
      23  def test_todas_rns_tem_teste():
      23 -    esperadas = set(range(1, 15))  # RN-001..RN-014            
      24 +    esperadas = set(range(1, 21))  # RN-001..RN-020            
      25      faltando = sorted(esperadas - _rns_com_teste())
      26      assert not faltando, f"RNs sem teste correspondente: {falta
          ndo}"

● Now let me run the full test suite.

  Ran 1 shell command (ctrl+o to expand)

● All 108 tests pass. Let me verify no leftover references to removed APIs
  remain, and confirm RN coverage.

  Searched for 1 pattern (ctrl+o to expand)

● All remaining references are legitimate (per-record Despesa.em_viagem,
  negative-assertion tests, and the flag-rejection test). No stale APIs remain.
  Let me confirm the RN coverage explicitly:

  Ran 1 shell command (ctrl+o to expand)

● All 20 RNs have named tests. Now let me verify CLAUDE.md (T-043) is already
  aligned, then mark the tasks complete.

  Ran 1 shell command (ctrl+o to expand)

● CLAUDE.md is already aligned (T-043 done in earlier docs commits). Now mark
  the completed tasks. Let me verify the unchecked set first:

  Ran 1 shell command (ctrl+o to expand)

● The unchecked set is exactly T-028..T-049. Let me mark them all complete:

  Ran 1 shell command (ctrl+o to expand)

● All unchecked tasks are now marked (grep found 0 remaining). Let me run the
  full suite one final time to confirm everything is green after the edits, plus
  a compile check:

  Ran 1 shell command (ctrl+o to expand)

● Everything is green: 108 tests pass, both goldens match exactly, all 20 RNs
  covered. No .specify/extensions.yml exists, so there are no post-execution
  hooks to dispatch.

  Let me save one non-obvious environment fact for future sessions (the Python
  interpreter isn't on PATH under python/py).

  Listed 1 directory, wrote 2 memories (ctrl+o to expand)

● Implementation complete ✅

  I executed Fases 6–10 (T-028..T-049) of tasks.md — the full rewrite from the
  D-004 state (fixed constants, --em-viagem) to spec 1.4 (external
  politica-v4.json + cambio.json, dynamic categories, per-record travel by
  currency, currency conversion). All 22 tasks are now marked [x].

  What changed

  Núcleo (source):
  - modelo.py — removed the Categoria enum; added Motivo.CAMBIO_NAO_IDENTIFICADO
  (7th motivo), CategoriaConfig/Politica/Cambio dataclasses; Despesa now
  carries valor_origem/moeda_norm/valor_base/em_viagem; Resultado dropped
  em_viagem; dedup key includes moeda + origin value.
  - politica.py — dropped fixed constants; politica_de_dict/cambio_de_dict build
  pure structures (política's moeda_base ignored per RN-018).
  - regras.py — one pure function per RN: resolve_conjunto (RN-015), dynamic
  valida_categoria (RN-001), valida_limite_categoria (RN-017), taxa_por_data
  (RN-019, nearest-date/tie→lowest), converte/valida_cambio (RN-018/020), NF
  over converted value (RN-006), aplica_teto_dia with travel buckets +
  aplica_teto_diaria per registro (RN-002/003/009), agrega_categoria excluding
  ≤0 and cambio-não-id.
  - calculo.py — pipeline reordered per DT-012 (estrutura → conversão → dedup →
  … → teto), dynamic category set, emits only categories with ≥1 despesa in
  policy order.
  - io_json.py — ler_politica/ler_cambio with abort-on-missing; serialization
  without em_viagem, dynamic ordered categories, free-text motivos.
  - cli.py — removed --em-viagem; added --politica/--cambio with packaged
  defaults.

  Tests — rewrote all 10 test modules for spec 1.4; coverage audit now spans
  RN-001..RN-020.

  Validation

  - 108 tests pass (py_compile clean).
  - Golden 1 (despesas-exemplo.json, CC-ENG-PLATAFORMA) → total_reembolso_geral 
  351.43, hospedagem non-reimbursable (nao reembolsavel), exact per spec §4.
  - Golden 2 (despesas-envelope.json, CC-COMERCIAL, EUR/USD/GBP) → 1228.72; EUR
  conversion + weekend-nearest-rate, GBP cambio não identificado excluded from
  total_despesas, NF evaluated post-conversion — exact per quickstart.
  - All 20 RNs have a test_rn_NNN_*; invariant total_despesas ≥ total_aceito ≥ 
  total_reembolso holds in every category.

  Notes

  - T-043 (CLAUDE.md) was already aligned by the earlier docs commits (command
  signature, câmbio in scope, no --em-viagem) — no change needed.
  - No .specify/extensions.yml exists, so pre/post-execution hooks were skipped
  per the workflow.
  - I did not commit — per project rules I only commit when you ask. The
  suggested commits are named in each task. Want me to commit these (one per
  task, or grouped by phase)?

  One heads-up: pyproject.toml uses packages = ["src"] without package_data for
  informacoes_externas/*.json. Everything works in editable install (pip install
  -e), which is how the quickstart runs it, but a built wheel wouldn't bundle
  the JSON. There's no task covering wheel packaging, so I left it untouched —
  flag it if you want that hardened.

✻ Cooked for 16m 39s