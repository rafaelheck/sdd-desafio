# Spec Quality Checklist: Motor de Cálculo de Reembolso

**Purpose**: Gate formal de release — validar a *qualidade dos requisitos* (completude, clareza, consistência, mensurabilidade, cobertura) da spec antes de implementar. Testa o que está **escrito** na spec, não o comportamento do código.
**Created**: 2026-07-31
**Executed**: 2026-07-31 (contra spec.md v1.4)
**Feature**: [spec.md](../spec.md) (v1.4)
**Audience**: Autor revisando a própria spec

> Cada item pergunta se o requisito está bem escrito, não se o sistema funciona.
> `[x]` = requisito adequado · `[ ]` = lacuna aberta (ver nota inline).

## Resultado da execução

**39/42 adequados.** A spec está madura e internamente muito consistente. Achados:

- **1 lacuna aberta na spec** (CHK001): obrigatoriedade dos campos de política não formalizada.
- **2 observações menores** (CHK016, CHK033): requisito correto, mas com precedência implícita / exemplo de borda ausente.
- **1 conflito cross-artifact fora da spec** (CHK041): `CLAUDE.md` está desatualizado e contradiz as regras de câmbio/viagem — **corrigir antes de implementar**.

---

## Requirement Completeness

- [ ] CHK001 - A estrutura completa de `politica-v4.json` está especificada, incluindo quais campos de categoria (`limite`, `periodicidade`, `observacao`) são obrigatórios e quais opcionais? [Completeness, Spec §4] — **LACUNA (menor):** §4 marca só `observacao` como opcional; a obrigatoriedade de `limite`/`periodicidade` não é declarada. Mitigado por §10 ("assume política bem formada"), mas para um gate formal vale explicitar quais campos são obrigatórios ou remeter explicitamente a §10.
- [x] CHK002 - A estrutura completa de `cambio.json` está especificada (chave `moeda_base` e mapa `taxas.<data>.<moeda>`), incluindo o tipo do fator de taxa? [Completeness, Spec §4] — Tabela de §4 define `moeda_base`, `taxas.<AAAA-MM-DD>` e o fator (numérico, "unidades de `moeda_base` por 1 unidade da moeda") com exemplo.
- [x] CHK003 - Todas as condições que **abortam** a execução estão enumeradas de forma exaustiva (JSON de topo inparseável, `cambio.json` ausente/inparseável) e distintas das recusas por registro? [Completeness, Spec §5 RN-013/RN-018, §8] — §8 passos 1–2, RN-013 e RN-018 enumeram e distinguem explicitamente de RN-020.
- [x] CHK004 - Todos os motivos de recusa possíveis estão enumerados em um único ponto autoritativo, e a lista casa com os motivos citados nas RNs individuais? [Completeness, Spec §9] — §9 lista os 8 motivos; batem com RN-001/006/007/008/010/013/017/020.
- [x] CHK005 - Os parâmetros globais da política (`nota_fiscal_obrigatoria_acima_de`, `acrescimo_em_viagem_percentual`) têm origem, unidade e aplicabilidade (valem para qualquer centro) documentadas? [Completeness, Spec §4, RN-015] — §4 + RN-015 ("valem para qualquer centro"); percentual com exemplo (+50% → ×1,5).
- [x] CHK006 - O comportamento de cada campo de saída está definido, incluindo quando um bloco de categoria é ou não emitido e o conteúdo de `reprovadas_sem_categoria`? [Completeness, Spec §4, RN-012, AMB-015] — §4 (tabela + `id`/`categoria_informada`/`motivo`), RN-012 e AMB-015 (só categorias com ≥1 despesa).
- [x] CHK007 - O requisito de eco dos campos de identificação do input na saída (`colaborador.id/nome/centro_custo`, `competencia`, `periodo`) está especificado por completo? [Completeness, Spec §4, RN-012] — Tabela de saída em §4 e RN-012 cobrem todos os campos ecoados.

## Requirement Clarity

- [x] CHK008 - A normalização de `moeda` e `categoria` (`trim` + caixa alta) está definida de forma única e sem ambiguidade sobre *quando* ocorre em relação às comparações? [Clarity, Spec §5 RN-001/RN-018, AMB-003] — RN-001, RN-018, AMB-003 e §8 passo 3 ("antes de qualquer comparação"); Clarifications 2026-07-31 fecham o "quando".
- [x] CHK009 - A distinção entre "sem moeda" (ausente/`null`/vazio após `trim` → base, não-viagem) e "moeda inválida" (tipo não-textual → registro inválido) está quantificada por tipo/valor, sem zona cinzenta? [Clarity, Spec §5 RN-013/RN-018] — RN-013 + RN-018 + Clarifications 2026-07-31 cobrem os casos por tipo/valor.
- [x] CHK010 - O critério de "data mais próxima" na resolução de taxa está definido de forma inequívoca (menor diferença absoluta em dias; empate → menor taxa; só datas que contêm a moeda)? [Clarity, Spec §5 RN-019] — RN-019 define os três aspectos com exemplo e caso de empate.
- [x] CHK011 - A ordem e o número de arredondamentos na conversão de câmbio estão explícitos (arredonda origem → multiplica pela taxa cheia → arredonda resultado), sem deixar dúvida sobre arredondar a taxa? [Clarity, Spec §5 RN-011/RN-018, AMB-018] — AMB-018 é explícita: não arredonda a taxa.
- [x] CHK012 - O critério de comparação da nota fiscal (estritamente acima do limiar, sobre o valor **já convertido**) está inequívoco quanto ao valor exato do limiar? [Clarity, Spec §5 RN-006] — RN-006: "estritamente acima"; "No valor exato do limiar não é necessária"; usa valor convertido.
- [x] CHK013 - Os campos de negócio que definem duplicidade estão listados de forma completa e sem ambiguidade sobre usar `valor`/`moeda` de origem (antes da conversão)? [Clarity, Spec §5 RN-008] — RN-008 lista os campos e fixa `valor`/`moeda` de origem.
- [x] CHK014 - A mecânica de "baldes separados" por status de viagem em dia misto está definida de modo que o resultado seja único e independente de ordenação? [Clarity, Spec §5 RN-002/RN-009, AMB-016] — AMB-016 justifica a independência de ordenação.

## Requirement Consistency

- [x] CHK015 - A definição de `moeda_base` é consistente em toda a spec (sempre a do `cambio.json`; a da política é explicitamente ignorada), sem contradição entre §3, §4 e RN-018? [Consistency, Spec §3/§4, RN-018] — §3, §4 e RN-018 repetem que a `moeda_base` da política é ignorada.
- [x] CHK016 - A ordem de aplicação das regras (§8) é consistente com as precedências afirmadas em cada RN/AMB (ex.: limite ≤ 0 antes de duplicata/período/valor/NF; câmbio antes de dedup)? [Consistency, Spec §8, RN-017/RN-020, AMB-010/AMB-014] — Consistente. **Observação:** §8 coloca "limite > 0" (passo 5) antes da conversão de câmbio (passo 6), logo "nao reembolsavel" prevalece sobre "cambio não identificado"; RN-020 só lista prevalência sobre duplicata/período/valor/NF. A precedência limite≤0 × câmbio fica implícita na §8 — considere citá-la em RN-017 ou RN-020.
- [x] CHK017 - As regras de teto RN-002/RN-003/RN-004 estão consistentemente redigidas por **papel/periodicidade**, sem citar nome de categoria fixa? [Consistency, Spec §5 RN-002/RN-003/RN-004] — Nomes de categoria aparecem só como exemplo parentético da política vigente; a regra afirma explicitamente não conhecer categoria.
- [x] CHK018 - A definição de "viagem" é consistente entre RN-009, RN-018 e AMB-016 (por registro, derivada de moeda ≠ base), sem resquício do antigo `em_viagem` de topo (AMB-008)? [Consistency, Spec §5 RN-009/RN-018, AMB-008/AMB-016] — Dentro da spec, coerente: §4 remove o campo, RN-009 nega o indicador antigo, AMB-008 marcada "Substituída por AMB-016". (Resíduo fora da spec: ver CHK041.)
- [x] CHK019 - O tratamento de itens não-valoráveis em `total_despesas` é consistente entre valores ≤ 0 e "cambio não identificado" (ambos excluídos pelo mesmo princípio)? [Consistency, Spec §5 RN-014/RN-020, AMB-017] — RN-020/AMB-017 invocam "o mesmo princípio de não-valorável usado para valores ≤ 0".
- [x] CHK020 - A invariante `total_despesas ≥ total_aceito ≥ total_reembolso` é afirmada de forma consistente e compatível com as exclusões definidas (≤ 0, câmbio não identificado)? [Consistency, Spec §4, RN-014, AMB-012] — Afirmada em §4, RN-014 e AMB-012; as exclusões preservam a invariante.
- [x] CHK021 - O exemplo de saída da §4 é numericamente consistente com as regras citadas (limites de `CC-ENG-PLATAFORMA`, exclusão do estorno `d-009`, `total_reembolso_geral = 351,43`)? [Consistency, Spec §4] — Confere: 271,43 + 80,00 + 0,00 = 351,43; `transporte_urbano` 100,00 + 100,01 = 200,01 sem o estorno −45,00.

## Acceptance Criteria Quality (Measurabilidade)

- [x] CHK022 - Cada critério de aceite (§9) é objetivamente verificável com números ou entradas concretas, e não com termos vagos? [Measurability, Spec §9] — Os critérios trazem números/entradas concretas ou condições binárias verificáveis.
- [x] CHK023 - O requisito "nenhuma categoria é conhecida/privilegiada pelo sistema" é enunciado de forma testável (mudar política muda resultado sem mudar código)? [Measurability, Spec §9, RN-004/RN-015/RN-016] — §9 enuncia adicionar/remover/alterar categoria "sem alterar regra ou código".
- [x] CHK024 - O critério de cobertura de testes (cada RN-001..RN-020 com ao menos um teste com números) é mensurável e rastreável a IDs de regra? [Measurability, Traceability, Spec §9] — §9 exige um teste com números por RN; rastreável por ID (reforçado pelo teste de auditoria em CLAUDE.md).
- [x] CHK025 - Os casos de borda da §7 trazem entrada e resultado esperado concretos suficientes para servir de critério de verificação? [Measurability, Spec §7] — Cada linha traz entrada-exemplo, comportamento esperado e regra.

## Scenario Coverage

- [x] CHK026 - Existe requisito para o cenário de fallback de centro de custo desconhecido (`padrao`), com os limites resultantes especificados? [Coverage, Spec §5 RN-015, AMB-013] — RN-015 (aceite com limites do `padrao`) + AMB-013.
- [x] CHK027 - Existe requisito para o dia de categoria "dia" **misto** (registros em viagem e não-viagem no mesmo dia+categoria)? [Coverage, Spec §5 RN-002/RN-009, AMB-016] — RN-002/RN-009, AMB-016 e caso de borda dedicado na §7.
- [x] CHK028 - Existe requisito para categoria válida no CC mas com `limite ≤ 0`, incluindo onde reportar e a precedência do motivo? [Coverage, Spec §5 RN-017, AMB-014] — RN-017 + AMB-014 (sob a própria categoria; precede sem NF/período).
- [x] CHK029 - Existe requisito para a mesma categoria ser válida em um CC e não aplicável em outro (`representacao` em `CC-COMERCIAL` vs. demais)? [Coverage, Spec §5 RN-001/RN-015, §7] — RN-001/RN-015 + caso de borda na §7.
- [x] CHK030 - Estão cobertos os fluxos de exceção de câmbio: data sem cotação (fim de semana/feriado), empate de datas, e moeda ausente de todas as `taxas`? [Coverage, Exception Flow, Spec §5 RN-019/RN-020] — RN-019 (data ausente + empate) e RN-020 (moeda ausente), com casos na §7.
- [x] CHK031 - O requisito de continuidade em falha parcial (um "registro inválido" não impede o processamento dos demais) está especificado? [Coverage, Recovery, Spec §5 RN-013, §9] — RN-013 ("os demais registros são processados normalmente") + critério em §9.

## Edge Case Coverage

- [x] CHK032 - Estão definidos os limites de fronteira monetária: valor exatamente no limiar de NF vs. um centavo acima, e arredondamento de valor com >2 casas? [Edge Case, Spec §7, RN-006/RN-011] — §7 (100,00 vs 100,01; 33,333 → 33,33) + RN-006/RN-011.
- [x] CHK033 - Estão definidos os limites de fronteira de período: `data` igual a `inicio`/`fim` (inclusivo) e data fora do intervalo? [Edge Case, Spec §7, RN-007, AMB-009] — Requisito claro (RN-007 + AMB-009: `[inicio, fim]` inclusive). **Observação:** a §7 exemplifica só a fronteira `fim` (`d-014`); a fronteira `inicio` não tem caso concreto na tabela — considere adicionar um exemplo simétrico.
- [x] CHK034 - Está definido o caso de despesa aceita cujo reembolso é 0 por teto já consumido (permanece em `total_aceito` com valor cheio)? [Edge Case, Spec §7, RN-005] — Caso de borda dedicado na §7 + RN-005.
- [x] CHK035 - Está definido o comportamento para `moeda` = `moeda_base` (sem conversão, não-viagem) versus `moeda` ausente, como casos distintos e ambos cobertos? [Edge Case, Spec §7, RN-018] — §7 traz os dois casos separados; RN-018 os distingue.

## Non-Functional Requirements

- [x] CHK036 - O requisito de **determinismo** (mesmo input → mesma saída) está declarado e é o suficientemente forte para cobrir empates de câmbio e ordenação de duplicatas? [Non-Functional, Spec §9, RN-008/RN-019] — §9 declara determinismo; RN-008 (primeira ocorrência) e RN-019 (empate → menor taxa) removem as fontes de não-determinismo.
- [x] CHK037 - A precisão monetária (2 casas, half-up) está especificada de forma uniforme para entrada, cálculos intermediários (câmbio) e saída? [Non-Functional, Spec §5 RN-011, AMB-018] — RN-011 + AMB-018 cobrem entrada, conversão e saída.

## Dependencies & Assumptions

- [x] CHK038 - Os pressupostos sobre arquivos externos bem formados (política e câmbio) estão explicitamente documentados como fora de escopo de validação, distinguindo "recusa de negócio" de "erro fatal"? [Assumption, Spec §3/§10, RN-018/RN-020] — §3/§10 documentam; §10 distingue moeda ausente (recusa) de arquivo inparseável (aborta).
- [x] CHK039 - As dependências entre a resolução da política/câmbio e as regras seguintes estão documentadas na ordem de aplicação (§8), sem passo faltante? [Dependency, Spec §8] — §8 lista os 12 passos, da carga de política/câmbio à agregação.

## Ambiguities & Conflicts

- [x] CHK040 - Todas as ambiguidades resolvidas (AMB-001..AMB-018) têm decisão, justificativa e regra afetada, sem nenhuma decisão de câmbio/viagem resolvida apenas no código sem registro correspondente? [Ambiguity, Spec §6] — As AMBs de câmbio/viagem (016/017/018) têm decisão, justificativa e regra afetada.
- [x] CHK041 - Existe algum conflito residual entre o texto histórico substituído (ex.: AMB-008) e as regras vigentes que possa induzir implementação errada? [Conflict, Spec §6 AMB-008/AMB-016] — Dentro da spec, não (AMB-008 marcada como substituída). **CONFLITO CROSS-ARTIFACT (fora da spec):** `CLAUDE.md` está desatualizado e contradiz a spec vigente — (1) "Fora de escopo" diz *"Sem conversão de moeda (tudo em BRL)"*, mas RN-018..RN-020 introduziram câmbio; (2) o comando ainda mostra a flag `[--em-viagem]`, removida por AMB-016/§4. Corrigir `CLAUDE.md` antes de implementar para não induzir código errado.
- [x] CHK042 - Os itens deixados "em aberto" na §10 (diárias reais, duplicata parcial, validação de política/câmbio, fuso, múltiplos inputs) estão claramente marcados como não-requisitos desta versão, sem virarem comportamento implícito? [Ambiguity, Spec §10] — §10 lista cada item como explicitamente em aberto, com decisão provisória quando aplicável.

## Notes

- Marque itens concluídos: `[x]`
- Anote lacunas e decisões inline, e promova qualquer lacuna real a uma clarificação na spec ou a uma entrada em `DECISIONS.md`.
- Este checklist valida a spec, não a implementação — nenhum item deve ser "testado rodando o sistema".

### Ações sugeridas (por prioridade)

1. **CHK041 — `CLAUDE.md` desatualizado (fora da spec, alta prioridade):** remover "Sem conversão de moeda (tudo em BRL)" e a flag `--em-viagem` do bloco de comandos; alinhar com RN-018..RN-020 e AMB-016.
2. **CHK001 — Política (lacuna menor):** declarar em §4 quais campos de categoria são obrigatórios, ou remeter explicitamente a §10.
3. **CHK016 — Precedência (observação):** citar em RN-017/RN-020 que "limite ≤ 0" prevalece sobre "cambio não identificado".
4. **CHK033 — Exemplo de borda (observação):** acrescentar à §7 um caso concreto de `data == inicio`.
