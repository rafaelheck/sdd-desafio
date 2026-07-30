# Log de Decisões e Mudanças de Spec

> Uma entrada **toda vez** que a spec mudar. Este arquivo é a prova de que a spec
> foi tratada como artefato vivo e não como cerimônia de abertura.
>
> Spec que não muda em dois dias é spec que ninguém consultou. Mudança não é
> demérito — mudança não registrada é.

Ordem cronológica inversa: a mais recente primeiro.

---

## D-002 — Desempate de duplicatas: mantém a primeira ocorrência · `2026-07-30`

**Gatilho:** pergunta de `/speckit-clarify`. A RN-008 dizia que duplicatas exatas
colapsam em um registro, mas não fixava **qual** cópia sobrevive. Como a spec
exige saída determinística (Seção 9), o teste de aceite não tinha um `id`
previsível para verificar entre duas duplicatas.

**O que mudou na spec:**
- RN-008: de "um sobrevive, o outro é duplicado" → "mantém-se a **primeira
  ocorrência na ordem do input**; cada cópia seguinte é recusada". Aceite fixado
  em `d-006` aceito / `d-007` duplicado.
- Seção 8 (ordem de aplicação), passo 3 de deduplicação: explicitado "mantendo a
  primeira ocorrência".
- Registrado em `## Clarifications → Session 2026-07-30`.

**Por quê:** saída determinística exige survivor previsível; "primeira ocorrência"
é o critério mais intuitivo e já era o assumido no exemplo da Seção 4.

**O que isso invalidou:** nada implementado ainda — apenas fixou um ponto antes
ambíguo. Nenhuma decisão técnica anterior caiu.

**Tasks afetadas:** nenhuma ainda (`tasks.md` não gerado). A futura task de
deduplicação deve testar explicitamente a ordem de entrada.

**Custo:** 1 arquivo (`spec.md`), 3 edições pontuais.

---

## D-001 — Tratamento de registro estruturalmente inválido · `2026-07-30`

**Gatilho:** pergunta de `/speckit-clarify`. A spec só previa `valor ≤ 0` (RN-010),
mas não dizia nada sobre registros malformados: campo obrigatório ausente,
`valor` não numérico ou `data` que não parseia como `YYYY-MM-DD`.

**O que mudou na spec:**
- Nova **RN-013 — Registro estruturalmente inválido**: recusa apenas o registro
  com motivo "registro inválido", reportado em `reprovadas_sem_categoria`; os
  demais registros seguem sendo processados; JSON de topo inparseável aborta a
  execução.
- Seção 8 (ordem de aplicação): novo passo 1 "Validação estrutural" à frente da
  normalização; os demais passos foram renumerados (2..9).
- Seção 7 (casos de borda): nova linha "Registro malformado".
- Seção 9 (critérios de aceite): "registro inválido" somado à lista de motivos e
  novo critério de que um registro malformado não impede os demais.
- Registrado em `## Clarifications → Session 2026-07-30`.

**Por quê:** processamento em lote resiliente — uma linha ruim não deve bloquear
o reembolso das despesas válidas do colaborador, e mantém rastro auditável do
problema em vez de descartá-lo silenciosamente.

**O que isso invalidou:** nada implementado ainda; ampliou o contrato de erro do
sistema (antes implícito).

**Tasks afetadas:** nenhuma ainda (`tasks.md` não gerado). A futura task de
parsing/validação de entrada deve cobrir os três casos malformados e o abort de
JSON de topo.

**Custo:** 1 arquivo (`spec.md`), 5 seções tocadas.
