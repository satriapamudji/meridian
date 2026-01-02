# Task 17 — API: Daily Digest + Metals Snapshot

**Epic:** 6 — Telegram Bot + Daily Digest (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-07.md`, `task-09.md`, `task-10.md`, `task-16.md`  
**Spec references:** `spec.md` section 11.3

## Objective

Create a single backend “daily briefing” output that both the dashboard and Telegram bot can reuse.

## Deliverables

- Digest builder service that composes:
  - priority events summary
  - metals snapshot (prices + ratio)
  - today’s high-impact calendar
  - active thesis updates
- Persist digest in `daily_digests` (cached)
- API endpoints:
  - `GET /digest/today`

## Acceptance Criteria

- Digest output is deterministic for a given day/time window.
- It can be rendered in both UI and Telegram without reformatting logic duplicated.

## Notes / Risks

- Define “day boundary” and timezone early (store UTC; render local).

## Out of Scope

- Telegram bot implementation (next tasks).

