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

- [x] **T-001** [P] — Criar `pyproject.toml`: projeto Python 3.13, `console_scripts` `calcular = src.cli:main`, extra `dev` com `pytest`, config do `pytest` (`testpaths = ["tests"]`)
  - **Atende:** DT-003, DT-005
  - **Aceite:** `pip install -e ".[dev]"` cria o comando `calcular`; `pytest` coleta sem erro
  - **Commit:** `<hash>`

- [x] **T-002** [P] — Criar esqueleto do pacote em `src/` (`src/__init__.py`) e `tests/` (`tests/__init__.py`, `tests/conftest.py` com fixture do caminho de `exemplos/despesas-exemplo.json`)
  - **Atende:** DT-002 (estrutura de pastas)
  - **Aceite:** `import src` funciona; `pytest` enxerga `tests/`
  - **Commit:** `<hash>`

- [x] **T-003** [P] — Definir constantes de política em `src/politica.py` (limites diários alim/transporte, `LIMITE_HOSPEDAGEM` por registro, `LIMIAR_NOTA_FISCAL`, `MULTIPLICADOR_VIAGEM`, `CATEGORIAS_VALIDAS`, `CASAS_DECIMAIS`), todas em `Decimal`
  - **Atende:** RN-001, RN-002, RN-003, RN-004, RN-006, RN-009, RN-011, AMB-006
  - **Aceite:** `tests/test_politica.py::test_valores_politica` confere cada constante
  - **Commit:** `<hash>`

- [x] **T-004** [P] — Definir modelo em `src/modelo.py`: enums `Categoria` e `Motivo` (texto exato da spec) e dataclasses `Despesa`, `Reprovacao`, `ResultadoCategoria`, `Resultado`
  - **Atende:** base de RN-012, RN-014; motivos de RN-006/007/008/010/013 e AMB-011
  - **Aceite:** `tests/test_modelo.py::test_motivos_texto_exato` — os 6 motivos batem com a spec ("categoria não aplicável", "data fora da competência", "registro duplicado", "sem nota fiscal obrigatória", "valor inválido", "registro inválido")
  - **Commit:** `<hash>`

## Fase 2 — Regras de negócio

> Todas as funções vivem em `src/regras.py` (arquivo próprio, requisito do usuário),
> puras, uma por regra, documentadas com o `RN-NNN`. Como compartilham o mesmo
> arquivo, entram em sequência; os respectivos testes em `tests/test_regras.py`
> podem ser escritos em paralelo antes (TDD). `src/calculo.py` só orquestra.

- [x] **T-005** — `normaliza_despesa()` em `src/regras.py`: arredonda `valor` para 2 casas (`ROUND_HALF_UP`) e deriva `categoria_norm` (`strip().lower()`)
  - **Atende:** RN-011, RN-001 (normalização), AMB-003, AMB-007
  - **Aceite:** `tests/test_regras.py::test_rn_011_arredonda_33_333` (33,333→33,33) e `::test_rn_001_normaliza_caixa` (`ALIMENTACAO`→`alimentacao`)
  - **Commit:** `<hash>`

- [x] **T-006** — `valida_estrutura()` em `src/regras.py`: campos obrigatórios presentes e tipados, `valor` numérico, `data` parseável → `Motivo.REGISTRO_INVALIDO` ou `None`
  - **Atende:** RN-013
  - **Aceite:** `tests/test_regras.py::test_rn_013_registro_sem_data` → "registro inválido"
  - **Commit:** `<hash>`

- [x] **T-007** — `deduplica()` em `src/regras.py`: colapsa por chave de negócio (sem `id`), mantendo a 1ª ocorrência; demais → `Motivo.REGISTRO_DUPLICADO`
  - **Atende:** RN-008, AMB-002, D-002
  - **Aceite:** `tests/test_regras.py::test_rn_008_mantem_primeira` (`d-006` aceito, `d-007` duplicado)
  - **Commit:** `<hash>`

- [x] **T-008** — `valida_categoria()` em `src/regras.py`: `categoria_norm ∈ CATEGORIAS_VALIDAS`? senão `Motivo.CATEGORIA_NAO_APLICAVEL`
  - **Atende:** RN-001, AMB-003, AMB-011
  - **Aceite:** `tests/test_regras.py::test_rn_001_coworking_invalida` e `::test_rn_001_uppercase_valida`
  - **Commit:** `<hash>`

- [x] **T-009** — `valida_periodo()` em `src/regras.py`: `inicio ≤ data ≤ fim` (inclusive)? senão `Motivo.DATA_FORA_COMPETENCIA`
  - **Atende:** RN-007, AMB-009
  - **Aceite:** `tests/test_regras.py::test_rn_007_fora` (`d-008`) e `::test_rn_007_limite_inclusivo` (`d-014` em `fim`)
  - **Commit:** `<hash>`

- [x] **T-010** — `valida_valor()` em `src/regras.py`: `valor > 0`? senão `Motivo.VALOR_INVALIDO`
  - **Atende:** RN-010, AMB-005
  - **Aceite:** `tests/test_regras.py::test_rn_010_negativo` (`d-009` -45 → "valor inválido")
  - **Commit:** `<hash>`

- [x] **T-011** — `valida_nota_fiscal()` em `src/regras.py`: se `valor > LIMIAR_NOTA_FISCAL` exige `tem_nota_fiscal`; senão `Motivo.SEM_NOTA_FISCAL`
  - **Atende:** RN-006, AMB-004
  - **Aceite:** `tests/test_regras.py::test_rn_006_100_ok` (`d-003` 100,00 sem NF aceita) e `::test_rn_006_100_01_recusa` (`d-004`)
  - **Commit:** `<hash>`

- [x] **T-012** — `tetos_efetivos()` em `src/regras.py`: aplica `MULTIPLICADOR_VIAGEM` aos tetos quando `em_viagem`, sem alterar o limiar de NF
  - **Atende:** RN-009, AMB-008
  - **Aceite:** `tests/test_regras.py::test_rn_009_tetos_viagem` (90/120/375) e `::test_rn_009_nf_nao_escala`
  - **Commit:** `<hash>`

- [x] **T-013** — `aplica_teto_diario()` em `src/regras.py`: agrega aceitas por `(categoria_norm, data)` e reembolsa `min(soma_dia, teto)` para alimentação e transporte
  - **Atende:** RN-002, RN-003, RN-005
  - **Aceite:** `tests/test_regras.py::test_rn_002_soma_dia` (72,50+38→60) e `::test_rn_003_transporte` (100→80)
  - **Commit:** `<hash>`

- [x] **T-014** — `aplica_teto_hospedagem()` em `src/regras.py`: reembolsa `min(valor, LIMITE_HOSPEDAGEM)` por registro
  - **Atende:** RN-004, RN-005, AMB-006
  - **Aceite:** `tests/test_regras.py::test_rn_004_por_registro` (`d-010` 480→250)
  - **Commit:** `<hash>`

- [x] **T-015** — `agrega_categoria()` em `src/regras.py`: calcula `total_despesas` (aceitas + reprovadas da categoria), `total_aceito` e `total_reembolso`, garantindo a invariante
  - **Atende:** RN-012, RN-014, AMB-012
  - **Aceite:** `tests/test_regras.py::test_rn_014_total_despesas` (transporte 100+100,01−45 = 155,01) e `::test_invariante_totais` — ⚠️ **revisto por T-025/D-004: agora exclui o −45 → 200,01**
  - **Commit:** `<hash>`

- [x] **T-016** — Orquestrar o pipeline em `src/calculo.py` na ordem da Seção 8 (estrutura → normalização → dedup → categoria → período → valor → NF → tetos → agregação), montando o `Resultado`; primeiro gate que falha define o motivo
  - **Atende:** AMB-010, DT-004; integra RN-001..RN-014
  - **Aceite:** `tests/test_calculo.py::test_ordem_primeiro_gate` (registro que viola vários motivos reporta o do primeiro gate) e `::test_categorias_sempre_presentes`
  - **Commit:** `<hash>`

## Fase 3 — Casos de borda

- [x] **T-017** [P] — Cobrir toda a tabela da Seção 7 em `tests/test_bordas.py`, um teste por linha nomeado pelo `id` do exemplo (inclui: aceita com reembolso 0 por teto já consumido; sábado sem regra de calendário; `data == fim` inclusive; `100,00` vs `100,01`)
  - **Atende:** RN-002/004/006/007/008/010/013 (bordas), AMB-003
  - **Aceite:** `pytest tests/test_bordas.py` — todos passam
  - **Commit:** `<hash>`

## Fase 4 — Saída e CLI

- [x] **T-018** — Leitura de entrada em `src/io_json.py`: `json.load(parse_float=Decimal)`, montar contexto (colaborador, período, `em_viagem`); erro de topo (arquivo inexistente, JSON inparseável, campos de topo ausentes) → exceção tratável
  - **Atende:** RN-013 (abort de topo), DT-001, DT-006
  - **Aceite:** `tests/test_io.py::test_leitura_decimal` (valor vira `Decimal`, não `float`) e `::test_json_topo_invalido_erro`
  - **Commit:** `<hash>`

- [x] **T-019** — Serialização em `src/io_json.py`: escrever `Resultado` com `Decimal` em 2 casas, `ensure_ascii=False`, ordem de chaves/categorias fixa, as 3 categorias sempre presentes
  - **Atende:** RN-012, AMB-011, DT-001
  - **Aceite:** `tests/test_io.py::test_serializa_2_casas` e `::test_acentos_preservados`
  - **Commit:** `<hash>`

- [x] **T-020** — CLI em `src/cli.py`: `argparse` com `--input`, `--output`, `--em-viagem` (`store_true`); ligar leitura → `calculo` → escrita; exit codes (0 sucesso, 1 erro de topo, 2 uso). `--em-viagem` da CLI é a fonte de verdade de `em_viagem`
  - **Atende:** DT-003, DT-006, AMB-008
  - **Aceite:** `tests/test_cli.py::test_cli_gera_saida`, `::test_cli_em_viagem`, `::test_cli_exit_code_input_inexistente`
  - **Commit:** `<hash>`

- [x] **T-021** [P] — `src/__main__.py` chamando `cli.main()` para permitir `python -m src ...`
  - **Atende:** DT-003
  - **Aceite:** `tests/test_cli.py::test_python_m_src` roda o exemplo por `python -m src`
  - **Commit:** `<hash>`

- [x] **T-022** — Teste golden de integração em `tests/test_integracao.py`: rodar `exemplos/despesas-exemplo.json` (com e sem `--em-viagem`) e comparar com a saída da Seção 4 (`total_reembolso_geral == 585,43`, totais por categoria, reprovadas, 2 casas, acentos) — ⚠️ **`transporte_urbano.total_despesas` revisto para 200,01 por T-027/D-004**
  - **Atende:** RN-012, RN-014, valida o conjunto; quickstart
  - **Aceite:** `pytest tests/test_integracao.py` passa exatamente contra a saída da spec
  - **Commit:** `<hash>`

- [x] **T-023** [P] — Teste de auditoria `tests/test_cobertura_rn.py`: falha se alguma `RN-001..RN-014` não tiver teste correspondente (por convenção de nome)
  - **Atende:** rastreabilidade (CLAUDE.md: nenhuma regra sem teste)
  - **Aceite:** `pytest tests/test_cobertura_rn.py` verde com as 14 regras cobertas
  - **Commit:** `<hash>`

- [x] **T-024** [P] — Preencher `CLAUDE.md` (seção "Stack e comandos" e "Valores monetários") com Python 3.13, `calcular`/`python -m src`, `pytest`, `Decimal`
  - **Atende:** documentação de projeto (plan §1)
  - **Aceite:** `CLAUDE.md` sem placeholders `<...>` na seção de stack
  - **Commit:** `<hash>`

---

## Fase 5 — Mudança de requisito D-004: `total_despesas` exclui valores ≤ 0

> Origem: `/speckit-specify` (D-004) + `/speckit-clarify` 2026-07-30 (opção A —
> exclusão **por valor**, não por motivo). `total_despesas` deixa de somar despesas
> com `valor ≤ 0`; no exemplo, `transporte_urbano` passa de 155,01 para **200,01**
> (o estorno `d-009` −45,00 sai da somatória, mas continua recusado como "valor
> inválido" e listado em `reprovadas`). Ver RN-014, DT-007. Numeração continua de
> T-024; as tasks antigas não são renumeradas.

- [x] **T-025** — Alterar `agrega_categoria()` em `src/regras.py`: excluir de `total_despesas` toda despesa com `valor ≤ 0`, independentemente do motivo da recusa (exclusão **por valor**, não por motivo); `total_aceito` e `total_reembolso` inalterados. Revisa T-015.
  - **Atende:** RN-014 (revista), D-004, DT-007
  - **Aceite:** `tests/test_regras.py::test_rn_014_total_despesas` passa a esperar `transporte_urbano` 100,00 + 100,01 = **200,01**; a invariante `total_despesas ≥ total_aceito ≥ total_reembolso` continua válida
  - **Commit:** `feat(T-025): total_despesas exclui valores <= 0 (D-004)`

- [x] **T-026** [P] — Atualizar e estender os testes de RN-014 em `tests/test_regras.py`: ajustar `test_rn_014_total_despesas` para 200,01 e adicionar `test_rn_014_exclui_valor_nao_positivo`, provando que uma despesa com `valor ≤ 0` recusada por um gate **anterior** ao de valor (ex.: duplicata ou fora da competência com valor negativo) também fica fora de `total_despesas` — exclusão por valor, não por motivo
  - **Atende:** RN-014, D-004 (Clarifications 2026-07-30, opção A)
  - **Aceite:** ambos os testes passam; o novo caso falharia sob a leitura "exclusão por motivo"
  - **Commit:** `test(T-026): exclusao por valor em total_despesas`

- [x] **T-027** — Atualizar o golden em `tests/test_integracao.py`: `transporte_urbano.total_despesas == 200.01`; confirmar que `total_reembolso_geral` permanece `585.43` e as demais categorias (`alimentacao` 402.83, `hospedagem` 1170.00) não mudam. Revisa T-022
  - **Atende:** RN-014, D-004; revisa T-022
  - **Aceite:** `pytest tests/test_integracao.py` passa contra a saída atualizada da Seção 4 da spec
  - **Commit:** `test(T-027): golden com transporte_urbano 200,01 (D-004)`

*(A candidata "AMB-006 hospedagem por registro" foi confirmada; a de precedência
`--em-viagem` da CLI foi **superada** por D-007 — a flag deixa de existir.)*

---

## Fase 6 — Fundação da política e câmbio externos (D-005 + D-007)

> Origem: `/speckit-specify` D-005 (política externa `politica-v4.json`, spec 1.2),
> D-006 (regras de teto agnósticas de categoria, spec 1.3), D-007 (câmbio `cambio.json`
> + viagem por moeda, spec 1.4) e `/speckit-clarify` 2026-07-31 (normalização de `moeda`,
> abort de câmbio ausente, `moeda` inválida). **Nada disso foi construído** — o código
> está no estado D-004. As Fases 6–10 escrevem direto para a spec 1.4 e **superam**
> partes de T-003/004/005/007/008/011/012/013/014/015/016/018/019/020/022/023 (ver
> "Superadas" abaixo). Numeração continua de T-027; tasks antigas não são renumeradas.

- [ ] **T-028** [P] — Reescrever `src/modelo.py`: **remover** o enum `Categoria`; adicionar `Motivo.CAMBIO_NAO_IDENTIFICADO = "cambio não identificado"` (7º motivo); novas dataclasses `CategoriaConfig(limite, periodicidade, observacao)`, `Politica(padrao, centros_custo, limiar_nf, acrescimo_viagem_pct)`, `Cambio(moeda_base, taxas: dict[date, dict[str, Decimal]])`; estender `Despesa` com `valor_origem`, `moeda_norm`, `valor_base`, `em_viagem`; **remover** `em_viagem` de `Resultado`. Supera T-004.
  - **Atende:** RN-015/016/017/018/020, `data-model.md`, DT-008
  - **Aceite:** `tests/test_modelo.py::test_motivos_texto_exato` cobre os 7 motivos (incl. "cambio não identificado"); `::test_resultado_sem_em_viagem`; `::test_despesa_campos_cambio`
  - **Commit:** `feat(T-028): modelo com politica/cambio e viagem por registro`

- [ ] **T-029** [P] — Reescrever `src/politica.py`: **remover** constantes fixas (`LIMITES_DIARIOS`, `LIMITE_HOSPEDAGEM`, `CATEGORIAS_VALIDAS`, `MULTIPLICADOR_VIAGEM`, `LIMIAR_NOTA_FISCAL`); adicionar `politica_de_dict(d) -> Politica` e `cambio_de_dict(d) -> Cambio` (puros: dict→estrutura, datas como `date`, taxas/limites como `Decimal`); manter `CASAS_DECIMAIS`. Supera T-003.
  - **Atende:** RN-015/018, DT-008
  - **Aceite:** `tests/test_politica.py::test_politica_de_dict` e `::test_cambio_de_dict` constroem as estruturas a partir de `src/informacoes_externas/{politica-v4,cambio}.json`
  - **Commit:** `feat(T-029): politica/cambio como estruturas puras`

- [ ] **T-030** — `src/io_json.py`: adicionar `ler_politica(caminho) -> Politica` e `ler_cambio(caminho) -> Cambio` (abrem com `parse_float=Decimal`, delegam a `politica.py`); levantar `ErroEntrada` (abort, exit 1) se ausente/inparseável. Em `ler_entrada`, **parar de ler** `em_viagem` do topo e manter `despesas_brutas` cru (com `moeda`). Supera T-018.
  - **Atende:** RN-018 (abort câmbio), RN-013, Clarify (câmbio abort), DT-012 passo 2
  - **Aceite:** `tests/test_io.py::test_cambio_ausente_aborta`, `::test_politica_ausente_aborta`, `::test_le_taxas_decimal`
  - **Commit:** `feat(T-030): carga de politica e cambio com abort`

## Fase 7 — Política, categoria e teto agnósticos de categoria (D-005/D-006)

> Funções puras em `src/regras.py`, uma por RN. Editam o mesmo arquivo → sequenciais;
> testes em `tests/test_regras.py`/`test_politica.py` podem preceder (TDD).

- [ ] **T-031** — `resolve_conjunto(politica, centro_custo) -> dict[str, CategoriaConfig]` em `src/regras.py`: `centros_custo.get(cc, padrao)` (RN-015).
  - **Atende:** RN-015, AMB-013
  - **Aceite:** `tests/test_politica.py::test_rn_015_fallback_padrao` (CC inexistente → `padrao`) e `::test_rn_015_cc_especifico` (`CC-ENG-PLATAFORMA`)
  - **Commit:** `feat(T-031): resolucao de centro de custo (RN-015)`

- [ ] **T-032** — `valida_categoria(despesa, conjunto)` em `src/regras.py`: `categoria_norm ∈ chaves(conjunto)`? senão `Motivo.CATEGORIA_NAO_APLICAVEL`. Sem `CATEGORIAS_VALIDAS` fixo. Supera T-008.
  - **Atende:** RN-001 (dinâmico), AMB-003, AMB-011
  - **Aceite:** `tests/test_regras.py::test_rn_001_coworking_invalida`, `::test_rn_001_uppercase_valida`, `::test_rn_001_representacao_so_comercial`
  - **Commit:** `feat(T-032): categorias validas dinamicas (RN-001)`

- [ ] **T-033** — `valida_limite_categoria(despesa, config)` em `src/regras.py`: se `config.limite ≤ 0` → recusa com `motivo = config.observacao or "categoria não aplicável"`, sob a própria categoria (RN-017).
  - **Atende:** RN-017, AMB-014
  - **Aceite:** `tests/test_regras.py::test_rn_017_limite_zero_nao_reembolsavel` (hospedagem `CC-ENG-PLATAFORMA` → "nao reembolsavel", prevalece sobre sem NF)
  - **Commit:** `feat(T-033): categoria com limite <= 0 (RN-017)`

- [ ] **T-034** — Tetos por periodicidade em `src/regras.py`: `aplica_teto_dia(aceitas, limite, fator)` com **baldes** por `em_viagem` (RN-002/009), `aplica_teto_diaria(aceitas, limite, fator)` por registro (RN-003); limite efetivo por registro = `limite × fator` se `em_viagem`. **Remover** `tetos_efetivos`, `aplica_teto_diario`, `aplica_teto_hospedagem`, `ORDEM_CATEGORIAS`. Supera T-012/013/014.
  - **Atende:** RN-002/003/004/005/009/016, AMB-016
  - **Aceite:** `tests/test_regras.py::test_rn_002_baldes_dia_misto` (BRL 80 + convertido 80, limite base 90/viagem 135 → 80+80=160), `::test_rn_003_diaria_por_registro`, `::test_rn_009_viagem_por_registro`
  - **Commit:** `feat(T-034): teto por periodicidade com baldes (RN-002/003/009)`

## Fase 8 — Câmbio e gates dependentes de conversão (D-007 + Clarify)

- [ ] **T-035** — Estender `normaliza_despesa` e `valida_estrutura` em `src/regras.py`: `moeda_norm = moeda.strip().upper() or None`; `valor_origem` arredondado a 2 casas; `em_viagem = moeda_norm not in (None, cambio.moeda_base)`; `moeda` de tipo não-textual → `REGISTRO_INVALIDO`; `""`/`null`/ausente → sem moeda. Supera T-005/006.
  - **Atende:** RN-018 (normalização), RN-009, RN-013 (moeda), RN-011, Clarify (normalização/tipo de `moeda`)
  - **Aceite:** `tests/test_regras.py::test_rn_018_moeda_normalizada` (`" usd "`→`USD`), `::test_rn_013_moeda_numerica_invalida`, `::test_rn_018_moeda_base_sem_conversao`
  - **Commit:** `feat(T-035): normalizacao de moeda e validacao de tipo (RN-018/013)`

- [ ] **T-036** — `taxa_por_data(cambio, moeda_norm, data) -> Decimal | None` em `src/regras.py` (RN-019): entre datas de `taxas` que contêm a moeda, menor `abs(data_taxa − data)`; empate → menor taxa; `None` se a moeda não existe em nenhuma data.
  - **Atende:** RN-019, AMB-017
  - **Aceite:** `tests/test_cambio.py::test_rn_019_data_exata`, `::test_rn_019_fim_de_semana_mais_proxima` (07-18→07-17, 5,96), `::test_rn_019_empate_menor_taxa`
  - **Commit:** `feat(T-036): resolucao de taxa por data (RN-019)`

- [ ] **T-037** — `converte(valor_origem, taxa)` (arredonda origem → × taxa cheia → arredonda resultado; AMB-018) e gate `valida_cambio(despesa, cambio)` em `src/regras.py`: se em viagem e `taxa_por_data` é `None` → `Motivo.CAMBIO_NAO_IDENTIFICADO`; senão preenche `valor_base` (registro base/sem moeda → `valor_base = valor_origem`).
  - **Atende:** RN-018/020, AMB-017/018
  - **Aceite:** `tests/test_cambio.py::test_rn_018_converte_eur` (22×5,93=130,46), `::test_rn_020_cambio_nao_identificado` (GBP), `::test_rn_018_arredondamento`
  - **Commit:** `feat(T-037): conversao e cambio nao identificado (RN-018/020)`

- [ ] **T-038** — Incluir `moeda_norm` na chave de duplicidade (`Despesa.chave_duplicidade` em `src/modelo.py`) usando `valor_origem` (RN-008). Supera T-007.
  - **Atende:** RN-008 (moeda na chave)
  - **Aceite:** `tests/test_regras.py::test_rn_008_mantem_primeira` (inalterado) e `::test_rn_008_moeda_diferencia` (iguais salvo `moeda` não são duplicados)
  - **Commit:** `feat(T-038): moeda na chave de duplicidade (RN-008)`

- [ ] **T-039** — `valida_nota_fiscal(despesa, limiar)` em `src/regras.py` passa a comparar `valor_base` (RN-006, após conversão). Supera T-011.
  - **Atende:** RN-006 (valor convertido)
  - **Aceite:** `tests/test_regras.py::test_rn_006_sobre_valor_convertido` (`e-005` USD 40→220 sem NF → recusada) e `::test_rn_006_limiar_exato`
  - **Commit:** `feat(T-039): nota fiscal sobre valor convertido (RN-006)`

## Fase 9 — Pipeline, saída e CLI (integração)

- [ ] **T-040** — Reescrever `src/calculo.py` na ordem da Seção 8/DT-012: estrutura → resolução política+câmbio → normalização → categoria válida → limite>0 → **conversão** → dedup → período → valor → NF(convertido) → teto(baldes/periodicidade) → agregação. Assinatura `calcula(despesas_brutas, colaborador, periodo, politica, cambio)` (sem `em_viagem`); conjunto **dinâmico** de categorias; `agrega_categoria` usa `valor_base` e exclui de `total_despesas` os `valor ≤ 0` **e** os "cambio não identificado". Supera T-015/016.
  - **Atende:** DT-012, RN-012/014, AMB-010/015/017; integra RN-001..RN-020
  - **Aceite:** `tests/test_calculo.py::test_ordem_gates_cambio`, `::test_agrega_exclui_cambio_nao_id`, `::test_categorias_dinamicas_so_com_despesa`
  - **Commit:** `feat(T-040): pipeline spec 1.4 com conversao e categorias dinamicas`

- [ ] **T-041** — Serialização em `src/io_json.py`: **remover** `em_viagem`; emitir só as categorias válidas do CC com ≥1 despesa, na **ordem das chaves do CC** (DT-011); suportar motivo "cambio não identificado". Supera T-019.
  - **Atende:** RN-012, AMB-015, DT-011
  - **Aceite:** `tests/test_io.py::test_saida_sem_em_viagem`, `::test_ordem_categorias_por_politica`
  - **Commit:** `feat(T-041): saida sem em_viagem e categorias dinamicas ordenadas`

- [ ] **T-042** — CLI `src/cli.py`: **remover** `--em-viagem`; adicionar `--politica`/`--cambio` (default: `src/informacoes_externas/{politica-v4,cambio}.json` resolvidos pelo pacote); ligar leitura das 3 fontes → `calculo.calcula` → escrita; exit 1 se input/política/câmbio ausente ou inválido. Supera T-020. Atualizar `src/cli.py` docstring de exit codes.
  - **Atende:** DT-003b, RN-018 (abort)
  - **Aceite:** `tests/test_cli.py::test_cli_sem_em_viagem`, `::test_cli_cambio_ausente_exit1`, `::test_cli_defaults_empacotados`
  - **Commit:** `feat(T-042): CLI com --politica/--cambio, sem --em-viagem`

- [ ] **T-043** [P] — Atualizar `CLAUDE.md` em **dois** pontos: (a) seção "Stack e comandos" — assinatura `calcular --input ... --output ... [--politica ...] [--cambio ...]` (sem `--em-viagem`), citando `politica-v4.json` (categorias/limites/limiar/viagem) e `cambio.json`; (b) seção "Fora de escopo" — **remover** "Sem conversão de moeda (tudo em BRL)" (câmbio agora está em escopo via RN-018..RN-020) e ajustar para "Sem regra de calendário (dia útil/feriado só afeta a data da taxa de câmbio)". Supera T-024.
  - **Atende:** DT-003b, documentação; consistência com spec 1.4
  - **Aceite:** `CLAUDE.md` não menciona `--em-viagem` nem "Sem conversão de moeda"; cita as duas fontes externas e câmbio em escopo
  - **Commit:** `docs(tasks): atualiza comando e escopo de cambio no CLAUDE.md`

## Fase 10 — Testes, goldens e cobertura

- [ ] **T-044** [P] — `tests/test_politica.py`: RN-015 (fallback `padrao` / CC específico), construção de `Politica`/`CategoriaConfig` a partir do arquivo real; conjuntos por CC.
  - **Atende:** RN-015, RN-016
  - **Aceite:** `pytest tests/test_politica.py` verde
  - **Commit:** `test(T-044): testes de politica externa (RN-015/016)`

- [ ] **T-045** [P] — `tests/test_cambio.py`: RN-018/019/020 — conversão, normalização de moeda, data mais próxima, empate → menor, "cambio não identificado", e abort de arquivo ausente/inparseável.
  - **Atende:** RN-018/019/020, Clarify
  - **Aceite:** `pytest tests/test_cambio.py` verde
  - **Commit:** `test(T-045): testes de cambio (RN-018/019/020)`

- [ ] **T-046** — Reescrever `tests/test_regras.py` e `tests/test_bordas.py` para a spec 1.4: **remover** testes de `--em-viagem`/categorias fixas/`tetos_efetivos`; cobrir RN-002 baldes, RN-003 diaria, RN-009 por registro, RN-017, RN-006 sobre convertido; e as novas linhas da Seção 7 (moeda=base, sem moeda, dia misto, fim de semana, empate, cambio não identificado, NF pós-conversão). **Garantir que toda RN-001..RN-020 tenha ao menos um teste cujo nome contenha o próprio número** (`def test_rn_NNN_*`) — em especial criar/preservar `test_rn_004_*` (origem do teto/limite pela política), `test_rn_005_*` (parcial no teto), `test_rn_007_*` (competência), `test_rn_010_*` (valor inválido), `test_rn_012_*` (agregação), `test_rn_014_*` (total_despesas exclui ≤0 e cambio não id) e `test_rn_016_*` (periodicidade), que não têm task dedicada nas Fases 7–8. Supera T-017.
  - **Atende:** RN-001..RN-020 (bordas), Seção 7
  - **Aceite:** `pytest tests/test_regras.py tests/test_bordas.py` verde **e** `pytest tests/test_cobertura_rn.py` passa (todo `test_rn_NNN` de 001 a 020 existe)
  - **Commit:** `test(T-046): testes de regra e bordas para spec 1.4`

- [ ] **T-047** [P] — Atualizar `tests/test_cobertura_rn.py`: auditar **RN-001..RN-020** (não mais RN-001..RN-014). A auditoria exige um `def test_rn_NNN_*` para **cada** número de 001 a 020 (convenção de nome literal); um teste nomeado por outra RN **não** conta pela regra que cobre. Supera T-023.
  - **Atende:** rastreabilidade (CLAUDE.md)
  - **Aceite:** `pytest tests/test_cobertura_rn.py` falha se faltar `test_rn_NNN` de qualquer RN até RN-020
  - **Commit:** `test(T-047): cobertura ate RN-020`

- [ ] **T-048** — Goldens em `tests/test_integracao.py`: (a) `exemplos/despesas-exemplo.json` (`CC-ENG-PLATAFORMA`) → `total_reembolso_geral == 351.43`, **sem** `em_viagem`, `hospedagem` não reembolsável (0,00), `alimentacao` 402.83/306.93/271.43, `transporte_urbano` 200.01/100.00/80.00; (b) `exemplos/despesas-envelope.json` (`CC-COMERCIAL`) → `total_reembolso_geral == 1228.72` com os totais do `quickstart.md`. Supera T-022/027.
  - **Atende:** RN-001..RN-020 ponta a ponta; quickstart (2 goldens)
  - **Aceite:** `pytest tests/test_integracao.py` bate exatamente os dois goldens
  - **Commit:** `test(T-048): goldens exemplo (351,43) e envelope (1228,72)`

- [ ] **T-049** [P] — Ajustar `tests/test_modelo.py`, `tests/test_io.py`, `tests/test_cli.py` remanescentes ao modelo 1.4 (sem enum `Categoria`, sem `em_viagem`); remover asserts obsoletos.
  - **Atende:** consistência dos testes
  - **Aceite:** `pytest` inteiro verde, sem referências a `Categoria`/`em_viagem`/`--em-viagem`
  - **Commit:** `test(T-049): ajusta testes remanescentes ao modelo 1.4`

### Superadas pelas Fases 6–10 (código D-004 → spec 1.4)

T-003 (constantes fixas) → T-029; T-004 (enum/modelo) → T-028; T-005/006 (normalização/estrutura) → T-035; T-007 (dedup) → T-038; T-008 (categoria) → T-032; T-011 (NF) → T-039; T-012/013/014 (tetos) → T-034; T-015/016 (agrega/pipeline) → T-040; T-018 (leitura) → T-030; T-019 (serialização) → T-041; T-020 (CLI) → T-042; T-022/027 (golden) → T-048; T-023 (cobertura) → T-047; T-024 (CLAUDE.md) → T-043. As demais (T-001/002/009/010/017/021/025/026) permanecem válidas ou têm seus testes reescritos por T-046.

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
- **Fase 5 (D-004):** T-025 altera `agrega_categoria()` (revisa T-015); T-026 (testes
  de regra, `[P]`) e T-027 (golden, revisa T-022) validam T-025 e dependem dele.
- **Fases 6–10 (D-005/D-006/D-007 + Clarify):**
  - **Fase 6** primeiro: T-028 (`modelo.py`) e T-029 (`politica.py`) são `[P]`; T-030
    (`io_json.py` carga) depende de T-028+T-029.
  - **Fase 7** depende de T-028/029: T-031..T-034 editam `regras.py` → sequenciais.
  - **Fase 8** depende da Fase 7: T-035 (normalização/estrutura) antes de T-036/037
    (câmbio); T-036 antes de T-037; T-038 (dedup) e T-039 (NF) dependem de T-035.
  - **Fase 9:** T-040 (`calculo.py`) depende de toda a Fase 7+8; T-041 (serialização) e
    T-042 (CLI) dependem de T-040; T-043 (`CLAUDE.md`) é `[P]`.
  - **Fase 10:** T-044/045 `[P]` (arquivos de teste novos); T-046 depende das Fases 7–8;
    T-047 `[P]`; T-048 (goldens) depende de T-040..T-042; T-049 `[P]`.
  - **Ordem entre decisões:** D-005/D-006 (Fases 6–7) vêm antes de D-007 (Fase 8), pois a
    conversão e a viagem por moeda assentam sobre a política externa e o teto por periodicidade.

## Exemplos de paralelização

- Rodada 1: **T-001, T-002, T-003, T-004** juntos.
- Escrita de testes: os `test_rn_0NN` de `tests/test_regras.py` podem ser escritos
  em paralelo (TDD) antes das funções de `regras.py`.
- Fechamento: **T-023** e **T-024** em paralelo com T-022.
- Fases 6–10 — Rodada A: **T-028, T-029** juntos. Rodada B (testes novos, TDD):
  **T-044, T-045, T-047** podem ser escritos antes das funções. Fechamento: **T-043,
  T-049** em paralelo com T-048.

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
| RN-014 (total_despesas) | T-015, **T-025** | `test_rn_014_total_despesas` (200,01), `test_rn_014_exclui_valor_nao_positivo` |
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
| D-004 (total_despesas exclui valor ≤ 0) | T-025, T-026, T-027 | `test_rn_014_exclui_valor_nao_positivo`, golden `transporte_urbano` 200,01 |

### Cobertura spec 1.4 (Fases 6–10 — substitui as linhas acima onde a regra mudou)

| Regra da spec | Task | Teste |
|---|---|---|
| RN-001 (categorias dinâmicas por CC) | T-032 | `test_rn_001_coworking_invalida`, `test_rn_001_representacao_so_comercial` |
| RN-002 (teto "dia", baldes) | T-034 | `test_rn_002_baldes_dia_misto` |
| RN-003 (teto "diaria") | T-034 | `test_rn_003_diaria_por_registro` |
| RN-004 (origem do teto/limite pela política) | T-031, T-034 | `test_rn_004_limite_pela_politica` |
| RN-005 (parcial no teto) | T-034 | `test_rn_005_parcial_no_teto` |
| RN-006 (NF sobre valor convertido) | T-039 | `test_rn_006_sobre_valor_convertido` |
| RN-007 (competência) | T-009, T-040 | `test_rn_007_fora`, `test_rn_007_limite_inclusivo` |
| RN-010 (valor inválido) | T-010, T-040 | `test_rn_010_negativo` |
| RN-008 (moeda na chave de duplicidade) | T-038 | `test_rn_008_moeda_diferencia` |
| RN-009 (viagem por registro/moeda) | T-034, T-035 | `test_rn_009_viagem_por_registro` |
| RN-012 (agregação em valor_base) | T-040 | `test_rn_012_agrega_valor_base` |
| RN-014 (total_despesas exclui ≤0 e cambio não id) | T-040 | `test_rn_014_exclui_cambio_nao_id` |
| RN-015 (política externa + resolução de CC) | T-031, T-030 | `test_rn_015_fallback_padrao`, `test_rn_015_cc_especifico` |
| RN-016 (periodicidade seleciona mecânica) | T-034 | `test_rn_016_seleciona_mecanica` |
| RN-017 (categoria com limite ≤ 0) | T-033 | `test_rn_017_limite_zero_nao_reembolsavel` |
| RN-018 (conversão para a base) | T-035, T-037 | `test_rn_018_converte_eur`, `test_rn_018_moeda_normalizada`, `test_rn_018_arredondamento` |
| RN-019 (taxa por data mais próxima) | T-036 | `test_rn_019_fim_de_semana_mais_proxima`, `test_rn_019_empate_menor_taxa` |
| RN-020 (cambio não identificado) | T-037 | `test_rn_020_cambio_nao_identificado` |
| AMB-013 (CC ausente → padrão) | T-031 | `test_rn_015_fallback_padrao` |
| AMB-014 (limite ≤ 0: precedência/reporte) | T-033 | `test_rn_017_limite_zero_nao_reembolsavel` |
| AMB-015 (só categorias com despesa, ordem do CC) | T-041 | `test_ordem_categorias_por_politica`, `test_categorias_dinamicas_so_com_despesa` |
| AMB-016 (viagem por moeda; baldes; saída sem em_viagem) | T-034, T-041 | `test_rn_002_baldes_dia_misto`, `test_saida_sem_em_viagem` |
| AMB-017 (cambio não id: reporte/total; data mais próxima) | T-036, T-037, T-040 | `test_rn_019_*`, `test_agrega_exclui_cambio_nao_id` |
| AMB-018 (arredondamento da conversão) | T-037 | `test_rn_018_arredondamento` |
| Clarify (normalização/tipo de `moeda`; abort de câmbio) | T-035, T-030 | `test_rn_018_moeda_normalizada`, `test_rn_013_moeda_numerica_invalida`, `test_cambio_ausente_aborta` |
| D-005 (política externa por CC) | T-028..T-034, T-044 | `pytest tests/test_politica.py` |
| D-006 (regras de teto agnósticas) | T-032, T-034 | `test_rn_001_*`, `test_rn_002_baldes_dia_misto` |
| D-007 (câmbio + viagem por moeda) | T-035..T-042, T-045, T-048 | `pytest tests/test_cambio.py`, golden envelope `1228,72` |
