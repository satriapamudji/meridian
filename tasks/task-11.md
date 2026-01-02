# Task 11 — Significance Scoring Engine (0–100)

**Epic:** 4 — LLM Analysis + Scoring (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-07.md`  
**Spec references:** `spec.md` section 7.1

## Objective

Implement Meridian’s macro event significance score (0–100) and the trigger thresholds (⚡ PRIORITY ≥ 65).

## Deliverables

- Scoring module that produces:
  - total score
  - per-component subscores (structural, transmission, historical, attention)
- Update `macro_events` with:
  - `significance_score`
  - `score_components`
  - `priority_flag`
- Clear trigger rules:
  - ≥65: deep analysis candidate
  - 50–64: monitoring
  - <50: logged

## Acceptance Criteria

- Score is reproducible for the same input.
- All weights match the spec’s intent.

## Notes / Risks

- You can start with heuristic scoring; later swap in model-assisted scoring without changing persisted fields.

## Out of Scope

- LLM synthesis of impacts/counter-case (next tasks).

