# Task 05 — Seed Loader Framework + Metals Knowledge Import

**Epic:** 2 — Database + Seed Data  
**Phase:** 1 (MVP)  
**Depends on:** `task-04.md`  
**Spec references:** `spec.md` section 6.2, section 10.2

## Objective

Create a repeatable way to load curated knowledge (metals KB) into Postgres.

## Deliverables

- `data/metals/` seed format (YAML or JSON) for gold/silver/copper categories
- Backend seed command/script:
  - Validates structure
  - Upserts into `metals_knowledge` by `(metal, category)`

## Acceptance Criteria

- Running the seed command twice is idempotent.
- Metals KB is queryable by metal + category for event analysis.

## Notes / Risks

- Keep KB structured (not freeform markdown) so it can be used in prompts predictably.

## Out of Scope

- Historical cases.
- Any “live” KB updating logic.

