# Task 23 — Scheduler + Daily Jobs (Ingestion + Digest)

**Epic:** 6 — Telegram Bot + Daily Digest (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-07.md`, `task-08.md`, `task-09.md`, `task-10.md`, `task-17.md`  
**Spec references:** `spec.md` section 11.4, Appendix H

## Objective

Run ingestion and digest generation on schedules so Meridian is “always on” without manual triggering.

## Deliverables

- Background worker + scheduler (Celery beat / APScheduler / cron + runner)
- Scheduled jobs:
  - RSS ingestion (e.g., every 5–15 min)
  - Calendar sync (daily + around releases)
  - Central bank sync (daily + around meetings)
  - Price pull (daily)
  - Digest generation (daily at configured time)

## Acceptance Criteria

- Jobs are observable (logs + failure alerts hooks).
- Re-running jobs is safe (idempotent; no duplicates).

## Notes / Risks

- Keep schedules configurable; don’t hardcode to one timezone.

## Out of Scope

- High-frequency/real-time pipelines.

