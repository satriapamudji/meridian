# Task 20 — UI: Event Detail (Raw vs Interpretation)

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-15.md`, `task-19.md`  
**Spec references:** `spec.md` section 11.2, Appendix G

## Objective

Implement the event deep-dive view that shows raw facts first, then interpretation, with clear separation.

## Deliverables

- Event detail page sections:
  - Raw facts (bulleted, uninterpreted)
  - Significance scoring breakdown
  - Metal impacts (per metal)
  - Historical precedent (link to case IDs)
  - Counter-case (mandatory)
  - Crypto transmission path
- “Analyze” action (calls backend analyze trigger) when analysis missing

## Acceptance Criteria

- Raw facts and interpretation are visually and structurally separated.
- Page can render partial data (event ingested but not analyzed yet).

## Notes / Risks

- Avoid “pretty summaries” that recombine raw + interpreted content into a single block.

## Out of Scope

- Thesis creation from event (optional later).

