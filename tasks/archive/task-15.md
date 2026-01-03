# Task 15 — API: Macro Events + Analysis

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-07.md`, `task-11.md`, `task-12.md`  
**Spec references:** `spec.md` section 11.2 (event card format)

## Objective

Expose macro events and their analysis to the frontend (and later Telegram) via stable API endpoints.

## Deliverables

- `GET /events` with filters:
  - priority only
  - score range
  - status
  - date range
- `GET /events/{id}` returning:
  - raw fields
  - `raw_facts`
  - interpretation fields (impacts, precedent, counter-case, transmission)
- `POST /events/{id}/analyze` (or async trigger) for priority events

## Acceptance Criteria

- Response shape supports strict raw-vs-interpretation rendering in the UI.
- Analyze endpoint is safe to retry and is idempotent per chosen strategy.

## Notes / Risks

- Consider async analysis to avoid long HTTP request times.

## Out of Scope

- Frontend pages.

