# Task 19 — UI: Macro Radar (List + Filters)

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-15.md`, `task-18.md`  
**Spec references:** `spec.md` section 11.2

## Objective

Implement the Macro Radar list view that surfaces events by significance and priority.

## Deliverables

- Events list page:
  - Priority section (⚡ ≥ 65)
  - Monitoring section (50–64)
  - Logged section (<50) optional
- Filters: score, date, source, status

## Acceptance Criteria

- List clearly shows score, source, published time, and analysis status.
- Clicking an event navigates to the event detail route.

## Notes / Risks

- Ensure “priority” is driven by persisted score, not recalculated in the UI.

## Out of Scope

- Event deep-dive rendering (next task).

