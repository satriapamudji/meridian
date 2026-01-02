# Task 12 — LLM Provider Abstraction + Macro Event Analysis Pipeline

**Epic:** 4 — LLM Analysis + Scoring (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-11.md`, `task-05.md`, `task-06.md`  
**Spec references:** `spec.md` Appendix G, section 0.4, section 6.3

## Objective

Given a priority macro event, generate structured analysis (raw facts, impacts, precedent, counter-case, transmission, thesis seed) and store it without mixing raw/interpreted.

## Deliverables

- Provider abstraction interface (supports OpenAI/Claude/local later)
- Macro event analysis workflow:
  - Input: event + relevant metals KB + relevant historical cases
  - Output persisted into `macro_events` fields:
    - `raw_facts[]` (uninterpreted)
    - `metal_impacts` (interpreted but structured)
    - `historical_precedent` (interpreted, cite case IDs)
    - `counter_case`
    - `crypto_transmission`
- Guardrails:
  - Clearly separate “raw facts” from “interpretation” in both storage and API shape

## Acceptance Criteria

- Analysis can be re-run for an event (versioning or overwrite strategy defined).
- No field mixes raw facts and interpretation.

## Notes / Risks

- Keep prompts in code as templates and store rendered prompts for debugging (optional, but helpful).

## Out of Scope

- Thesis auto-creation (can be manual “Create Thesis” in UI first).

