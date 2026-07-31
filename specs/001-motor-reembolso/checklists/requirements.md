# Specification Quality Checklist: Motor de Cálculo de Reembolso

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-30 · **Atualizado**: 2026-07-31 (conversão de câmbio e viagem por moeda)
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- As ambiguidades da política de RH foram resolvidas por decisão própria (conforme
  o enunciado do desafio) e registradas na Seção 6 (AMB-001..AMB-011), em vez de
  virarem marcadores [NEEDS CLARIFICATION].
- Atualização 2026-07-31: novas regras de política externa (`politica-v4.json`) e
  centros de custo adicionaram RN-015 (fonte externa + fallback `padrao`), RN-016
  (periodicidade "dia"/"diaria") e RN-017 (limite ≤ 0 não reembolsável). Três
  pontos ambíguos foram resolvidos com o usuário (Clarifications Session
  2026-07-31) e encodados em AMB-013, AMB-014 e AMB-015.
- O exemplo da Seção 4 foi recalculado para `CC-ENG-PLATAFORMA` (alimentação
  limite 75, hospedagem limite 0): `total_reembolso_geral` = 351,43.
- Atualização 2026-07-31 (spec 1.2 → 1.3, ver DECISIONS D-006): RN-002/003/004
  deixaram de citar categorias fixas e foram reescritas por **papel** — RN-002 teto
  de periodicidade "dia", RN-003 teto de periodicidade "diaria", RN-004 origem do
  teto (limite pela política). Nenhuma regra conhece nome de categoria; o conjunto,
  limites e periodicidades vêm inteiramente de `politica-v4.json` e mudam o resultado
  sem alteração de código. Novo critério de aceite na Seção 9 cobre essa resiliência.
- Atualização 2026-07-31 (spec 1.3 → 1.4, ver DECISIONS D-007): novas RN-018/019/020
  de câmbio (`cambio.json`) — conversão para a base, taxa por data mais próxima
  (empate → menor) e "cambio não identificado"; RN-009 reescrita para **viagem por
  registro** (moeda ≠ base), sem `em_viagem` no input nem na saída; NF avaliada após a
  conversão; dia "dia" misto por **baldes separados**. Três decisões fechadas com o
  usuário (AMB-016/017/018) e o `despesas-envelope.json` usado para validar os casos
  (GBP não identificado, EUR em fim de semana, registro sem `moeda`). Conjunto de
  regras 17 → 20.
- A divergência da letra do RH em hospedagem ("por diária" → "por registro",
  AMB-006) deve ser registrada em `DECISIONS.md` na fase de plano/implementação.
- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`.
