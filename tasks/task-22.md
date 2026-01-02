# Task 22 — Telegram Bot Bootstrap + Command Router

**Epic:** 6 — Telegram Bot + Daily Digest (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-03.md`, `task-17.md`  
**Spec references:** `spec.md` section 11.3

## Objective

Stand up a Telegram bot that can respond to Phase 1 commands by calling the same backend services used by the dashboard.

## Deliverables

- Telegram bot integration module (token via env)
- Command router supporting at least:
  - `/today`
  - `/events`
  - `/thesis`
  - `/note`
- Message rendering aligned with the spec’s daily briefing format

## Acceptance Criteria

- Bot can be run locally and respond in a test chat.
- `/today` output matches backend digest content (no duplicated logic).

## Notes / Risks

- Prefer webhook in production, polling locally; isolate transport choice behind an interface.

## Out of Scope

- Phase 2 crypto commands.

