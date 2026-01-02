# Task 09 — Economic Calendar Ingestion + Surprise Detection

**Epic:** 3 — Ingestion Pipelines (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-04.md`  
**Spec references:** `spec.md` section 5.3

## Objective

Sync the economic calendar and compute basic “surprise” once actuals are available.

## Deliverables

- Daily sync job for upcoming events (high/medium/low impact)
- Store in `economic_events`:
  - expected/previous values
  - actual values when available
  - surprise direction + magnitude fields

## Acceptance Criteria

- Calendar data is queryable for “today” and “next N days”.
- Surprise calculation is deterministic and logged.

## Notes / Risks

- Free sources vary in schema and reliability; build with adapter pattern.

## Out of Scope

- Historical metal impact modeling.

