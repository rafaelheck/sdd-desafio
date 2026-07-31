# Tasks — Motor de Cálculo de Reembolso

> Cada task é pequena o bastante para virar **um commit**. Se você não consegue
> descrever o critério de aceite como "o teste X passa", a task está grande demais.
>
> Marque `[x]` conforme conclui — ao longo do caminho, não tudo no fim. O histórico
> de quando cada task foi marcada é lido na correção.

**Formato do commit:** `feat(T-003): <descrição>` · `test(T-003): <descrição>`

**Organização:** a spec não tem histórias de usuário (P1/P2/P3) — é um motor único
e determinístico. As tasks seguem as fases do template (Fundação → Regras →
Bordas → Saída/CLI). `[P]` marca tasks que podem correr em paralelo (arquivos
distintos, sem dependência pendente). Toda regra vem com teste (CLAUDE.md).

**MVP:** Fase 1 + Fase 2 + T-018..T-020 (ler → calcular → escrever) já produzem a
saída correta para o exemplo oficial. Fases 3 e o restante da 4 endurecem e provam.

---

## Fase 1 — Fundação

- [ ] **T-001** [P] — Criar `pyproject.toml`: projeto Python 3.13, `console_scripts` `calcular = src.cli:main`, extra `dev` com `pytest`, config do `pytest` (`testpaths = ["tests"]`)
  - **Atende:** DT-003, DT-005
  - **Aceite:** `pip install -e ".[dev]"` cria o comando `calcular`; `pytest` coleta sem erro
  - **Commit:** `<hash>`

- [ ] **T-002** [P] — Criar esqueleto do pacote em `src/` (`src/__init__.py`) e `tests/` (`tests/__init__.py`, `tests/conftest.py` com fixture do caminho de `exemplos/despesas-exemplo.json`)
  - **Atende:** DT-002 (estrutura de pastas)
  - **Aceite:** `import src` funciona; `pytest` enxerga `tests/`
  - **Commit:** `<hash>`

- [ ] **T-003** [P] — Definir constantes de política em `src/politica.py` (limites diários alim/transporte, `LIMITE_HOSPEDAGEM` por registro, `LIMIAR_NOTA_FISCAL`, `MULTIPLICADOR_VIAGEM`, `CATEGORIAS_VALIDAS`, `CASAS_DECIMAIS`), todas em `Decimal`
  - **Atende:** RN-001, RN-002, RN-003, RN-004, RN-006, RN-009, RN-011, AMB-006
  - **Aceite:** `tests/test_politica.py::test_valores_politica` confere cada constante
  - **Commit:** `<hash>`

- [ ] **T-004** [P] — Definir modelo em `src/modelo.py`: enums `Categoria` e `Motivo` (texto exato da spec) e dataclasses `Despesa`, `Reprovacao`, `ResultadoCategoria`, `Resultado`
  - **Atende:** base de RN-012, RN-014; motivos de RN-006/007/008/010/013 e AMB-011
  - **Aceite:** `tests/test_modelo.py::test_motivos_texto_exato` — os 6 motivos batem com a spec ("categoria não aplicável", "data fora da competência", "registro duplicado", "sem nota fiscal obrigatória", "valor inválido", "registro inválido")
  - **Commit:** `<hash>`

## Fase 2 — Regras de negócio

> Todas as funções vivem em `src/regras.py` (arquivo próprio, requisito do usuário),
> puras, uma por regra, documentadas com o `RN-NNN`. Como compartilham o mesmo
> arquivo, entram em sequência; os respectivos testes em `tests/test_regras.py`
> podem ser escritos em paralelo antes (TDD). `src/calculo.py` só orquestra.

- [ ] **T-005** — `normaliza_despesa()` em `src/regras.py`: arredonda `valor` para 2 casas (`ROUND_HALF_UP`) e deriva `categoria_norm` (`strip().lower()`)
  - **Atende:** RN-011, RN-001 (normalização), AMB-003, AMB-007
  - **Aceite:** `tests/test_regras.py::test_rn_011_arredonda_33_333` (33,333→33,33) e `::test_rn_001_normaliza_caixa` (`ALIMENTACAO`→`alimentacao`)
  - **Commit:** `<hash>`

- [ ] **T-006** — `valida_estrutura()` em `src/regras.py`: campos obrigatórios presentes e tipados, `valor` numérico, `data` parseável → `Motivo.REGISTRO_INVALIDO` ou `None`
  - **Atende:** RN-013
  - **Aceite:** `tests/test_regras.py::test_rn_013_registro_sem_data` → "registro inválido"
  - **Commit:** `<hash>`

- [ ] **T-007** — `deduplica()` em `src/regras.py`: colapsa por chave de negócio (sem `id`), mantendo a 1ª ocorrência; demais → `Motivo.REGISTRO_DUPLICADO`
  - **Atende:** RN-008, AMB-002, D-002
  - **Aceite:** `tests/test_regras.py::test_rn_008_mantem_primeira` (`d-006` aceito, `d-007` duplicado)
  - **Commit:** `<hash>`

- [ ] **T-008** — `valida_categoria()` em `src/regras.py`: `categoria_norm ∈ CATEGORIAS_VALIDAS`? senão `Motivo.CATEGORIA_NAO_APLICAVEL`
  - **Atende:** RN-001, AMB-003, AMB-011
  - **Aceite:** `tests/test_regras.py::test_rn_001_coworking_invalida` e `::test_rn_001_uppercase_valida`
  - **Commit:** `<hash>`

- [ ] **T-009** — `valida_periodo()` em `src/regras.py`: `inicio ≤ data ≤ fim` (inclusive)? senão `Motivo.DATA_FORA_COMPETENCIA`
  - **Atende:** RN-007, AMB-009
  - **Aceite:** `tests/test_regras.py::test_rn_007_fora` (`d-008`) e `::test_rn_007_limite_inclusivo` (`d-014` em `fim`)
  - **Commit:** `<hash>`

- [ ] **T-010** — `valida_valor()` em `src/regras.py`: `valor > 0`? senão `Motivo.VALOR_INVALIDO`
  - **Atende:** RN-010, AMB-005
  - **Aceite:** `tests/test_regras.py::test_rn_010_negativo` (`d-009` -45 → "valor inválido")
  - **Commit:** `<hash>`

- [ ] **T-011** — `valida_nota_fiscal()` em `src/regras.py`: se `valor > LIMIAR_NOTA_FISCAL` exige `tem_nota_fiscal`; senão `Motivo.SEM_NOTA_FISCAL`
  - **Atende:** RN-006, AMB-004
  - **Aceite:** `tests/test_regras.py::test_rn_006_100_ok` (`d-003` 100,00 sem NF aceita) e `::test_rn_006_100_01_recusa` (`d-004`)
  - **Commit:** `<hash>`

- [ ] **T-012** — `tetos_efetivos()` em `src/regras.py`: aplica `MULTIPLICADOR_VIAGEM` aos tetos quando `em_viagem`, sem alterar o limiar de NF
  - **Atende:** RN-009, AMB-008
  - **Aceite:** `tests/test_regras.py::test_rn_009_tetos_viagem` (90/120/375) e `::test_rn_009_nf_nao_escala`
  - **Commit:** `<hash>`

- [ ] **T-013** — `aplica_teto_diario()` em `src/regras.py`: agrega aceitas por `(categoria_norm, data)` e reembolsa `min(soma_dia, teto)` para alimentação e transporte
  - **Atende:** RN-002, RN-003, RN-005
  - **Aceite:** `tests/test_regras.py::test_rn_002_soma_dia` (72,50+38→60) e `::test_rn_003_transporte` (100→80)
  - **Commit:** `<hash>`

- [ ] **T-014** — `aplica_teto_hospedagem()` em `src/regras.py`: reembolsa `min(valor, LIMITE_HOSPEDAGEM)` por registro
  - **Atende:** RN-004, RN-005, AMB-006
  - **Aceite:** `tests/test_regras.py::test_rn_004_por_registro` (`d-010` 480→250)
  - **Commit:** `<hash>`

- [ ] **T-015** — `agrega_categoria()` em `src/regras.py`: calcula `total_despesas` (aceitas + reprovadas da categoria), `total_aceito` e `total_reembolso`, garantindo a invariante
  - **Atende:** RN-012, RN-014, AMB-012
  - **Aceite:** `tests/test_regras.py::test_rn_014_total_despesas` (transporte 100+100,01−45 = 155,01) e `::test_invariante_totais`
  - **Commit:** `<hash>`

- [ ] **T-016** — Orquestrar o pipeline em `src/calculo.py` na ordem da Seção 8 (estrutura → normalização → dedup → categoria → período → valor → NF → tetos → agregação), montando o `Resultado`; primeiro gate que falha define o motivo
  - **Atende:** AMB-010, DT-004; integra RN-001..RN-014
  - **Aceite:** `tests/test_calculo.py::test_ordem_primeiro_gate` (registro que viola vários motivos reporta o do primeiro gate) e `::test_categorias_sempre_presentes`
  - **Commit:** `<hash>`

## Fase 3 — Casos de borda

- [ ] **T-017** [P] — Cobrir toda a tabela da Seção 7 em `tests/test_bordas.py`, um teste por linha nomeado pelo `id` do exemplo (inclui: aceita com reembolso 0 por teto já consumido; sábado sem regra de calendário; `data == fim` inclusive; `100,00` vs `100,01`)
  - **Atende:** RN-002/004/006/007/008/010/013 (bordas), AMB-003
  - **Aceite:** `pytest tests/test_bordas.py` — todos passam
  - **Commit:** `<hash>`

## Fase 4 — Saída e CLI

- [ ] **T-018** — Leitura de entrada em `src/io_json.py`: `json.load(parse_float=Decimal)`, montar contexto (colaborador, período, `em_viagem`); erro de topo (arquivo inexistente, JSON inparseável, campos de topo ausentes) → exceção tratável
  - **Atende:** RN-013 (abort de topo), DT-001, DT-006
  - **Aceite:** `tests/test_io.py::test_leitura_decimal` (valor vira `Decimal`, não `float`) e `::test_json_topo_invalido_erro`
  - **Commit:** `<hash>`

- [ ] **T-019** — Serialização em `src/io_json.py`: escrever `Resultado` com `Decimal` em 2 casas, `ensure_ascii=False`, ordem de chaves/categorias fixa, as 3 categorias sempre presentes
  - **Atende:** RN-012, AMB-011, DT-001
  - **Aceite:** `tests/test_io.py::test_serializa_2_casas` e `::test_acentos_preservados`
  - **Commit:** `<hash>`

- [ ] **T-020** — CLI em `src/cli.py`: `argparse` com `--input`, `--output`, `--em-viagem` (`store_true`); ligar leitura → `calculo` → escrita; exit codes (0 sucesso, 1 erro de topo, 2 uso). `--em-viagem` da CLI é a fonte de verdade de `em_viagem`
  - **Atende:** DT-003, DT-006, AMB-008
  - **Aceite:** `tests/test_cli.py::test_cli_gera_saida`, `::test_cli_em_viagem`, `::test_cli_exit_code_input_inexistente`
  - **Commit:** `<hash>`

- [ ] **T-021** [P] — `src/__main__.py` chamando `cli.main()` para permitir `python -m src ...`
  - **Atende:** DT-003
  - **Aceite:** `tests/test_cli.py::test_python_m_src` roda o exemplo por `python -m src`
  - **Commit:** `<hash>`

- [ ] **T-022** — Teste golden de integração em `tests/test_integracao.py`: rodar `exemplos/despesas-exemplo.json` (com e sem `--em-viagem`) e comparar com a saída da Seção 4 (`total_reembolso_geral == 585,43`, totais por categoria, reprovadas, 2 casas, acentos)
  - **Atende:** RN-012, RN-014, valida o conjunto; quickstart
  - **Aceite:** `pytest tests/test_integracao.py` passa exatamente contra a saída da spec
  - **Commit:** `<hash>`

- [ ] **T-023** [P] — Teste de auditoria `tests/test_cobertura_rn.py`: falha se alguma `RN-001..RN-014` não tiver teste correspondente (por convenção de nome)
  - **Atende:** rastreabilidade (CLAUDE.md: nenhuma regra sem teste)
  - **Aceite:** `pytest tests/test_cobertura_rn.py` verde com as 14 regras cobertas
  - **Commit:** `<hash>`

- [ ] **T-024** [P] — Preencher `CLAUDE.md` (seção "Stack e comandos" e "Valores monetários") com Python 3.13, `calcular`/`python -m src`, `pytest`, `Decimal`
  - **Atende:** documentação de projeto (plan §1)
  - **Aceite:** `CLAUDE.md` sem placeholders `<...>` na seção de stack
  - **Commit:** `<hash>`

---

## Fase 5 — Envelope (criar no Dia 2)

<Novas tasks a partir da mudança de requisito. Numeração continua de onde parou —
não reinicie e não renumere as antigas: a numeração é o eixo da rastreabilidade.>

*(Reservada. Candidatas já sinalizadas: confirmar AMB-012 `total_despesas`
monetário vs. contagem; confirmar AMB-006 hospedagem por registro vs. por diária;
precedência `--em-viagem` da CLI vs. campo `em_viagem` do JSON.)*

---

## Dependências e ordem

- **Fundação primeiro:** T-001..T-004. T-001–T-004 são `[P]` entre si (arquivos distintos).
- **Fase 2 depende de** `politica.py` (T-003) e `modelo.py` (T-004). T-005..T-015
  editam o mesmo `regras.py` → sequenciais; seus testes podem ser escritos antes.
  T-016 (`calculo.py`) depende de T-005..T-015.
- **Fase 3** (T-017) depende do pipeline (T-016).
- **Fase 4:** T-018/T-019 (`io_json.py`) dependem de `modelo.py`; T-020 (`cli.py`)
  depende de T-016+T-018+T-019; T-021 depende de T-020; T-022 depende de T-020;
  T-023 e T-024 são `[P]` (independentes).

## Exemplos de paralelização

- Rodada 1: **T-001, T-002, T-003, T-004** juntos.
- Escrita de testes: os `test_rn_0NN` de `tests/test_regras.py` podem ser escritos
  em paralelo (TDD) antes das funções de `regras.py`.
- Fechamento: **T-023** e **T-024** em paralelo com T-022.

---

## Cobertura

Preencha ao fechar cada fase. É a sua própria checagem de rastreabilidade — e é
exatamente a matriz que a correção vai montar.

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 (categorias) | T-003, T-005, T-008 | `test_rn_001_normaliza_caixa`, `test_rn_001_coworking_invalida` |
| RN-002 (teto alimentação) | T-013 | `test_rn_002_soma_dia` |
| RN-003 (teto transporte) | T-013 | `test_rn_003_transporte` |
| RN-004 (teto hospedagem) | T-014 | `test_rn_004_por_registro` |
| RN-005 (parcial no teto) | T-013, T-014 | `test_rn_002_soma_dia`, `test_rn_004_por_registro` |
| RN-006 (nota fiscal) | T-011 | `test_rn_006_100_ok`, `test_rn_006_100_01_recusa` |
| RN-007 (competência) | T-009 | `test_rn_007_fora`, `test_rn_007_limite_inclusivo` |
| RN-008 (duplicatas) | T-007 | `test_rn_008_mantem_primeira` |
| RN-009 (viagem) | T-012 | `test_rn_009_tetos_viagem`, `test_rn_009_nf_nao_escala` |
| RN-010 (valor inválido) | T-010 | `test_rn_010_negativo` |
| RN-011 (precisão) | T-005 | `test_rn_011_arredonda_33_333` |
| RN-012 (agregação) | T-015, T-019 | `test_rn_012_*`, `test_serializa_2_casas` |
| RN-013 (registro inválido) | T-006, T-018 | `test_rn_013_registro_sem_data`, `test_json_topo_invalido_erro` |
| RN-014 (total_despesas) | T-015 | `test_rn_014_total_despesas` |
| AMB-002 (id na duplicidade) | T-007 | `test_rn_008_mantem_primeira` |
| AMB-003 (caixa da categoria) | T-005, T-008 | `test_rn_001_uppercase_valida` |
| AMB-004 (NF ausente = recusa) | T-011 | `test_rn_006_100_01_recusa` |
| AMB-005 (valor negativo) | T-010 | `test_rn_010_negativo` |
| AMB-006 (hospedagem por registro) | T-014 | `test_rn_004_por_registro` |
| AMB-007 (arredondamento) | T-005 | `test_rn_011_arredonda_33_333` |
| AMB-008 (viagem por input) | T-012, T-020 | `test_rn_009_*`, `test_cli_em_viagem` |
| AMB-009 (competência inclusiva) | T-009 | `test_rn_007_limite_inclusivo` |
| AMB-010 (ordem dos gates) | T-016 | `test_ordem_primeiro_gate` |
| AMB-011 (recusa sem categoria) | T-008, T-019 | `test_rn_001_coworking_invalida` |
| AMB-012 (total_despesas monetário) | T-015 | `test_rn_014_total_despesas`, `test_invariante_totais` |
