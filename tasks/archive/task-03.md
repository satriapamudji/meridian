# Task 03 — Backend Bootstrap (FastAPI + Settings + Health)

**Epic:** 1 — Repo + Dev Environment  
**Phase:** 1 (MVP)  
**Depends on:** `task-01.md`, `task-02.md`  
**Spec references:** `spec.md` sections 4, 9

## Objective

Create a working FastAPI service with a minimal but solid foundation (config, logging, health endpoint) to support future ingestion + API work.

## Deliverables

- `backend/app/main.py` FastAPI entrypoint
- Settings system (env var driven): DB URL, Redis URL, log level
- Health endpoints:
  - `GET /health` (process OK)
  - `GET /ready` (DB connectivity check)

## Acceptance Criteria

- Backend starts locally with the dev environment from `task-02.md`.
- `/ready` fails clearly if DB is unavailable.

## Notes / Risks

- Avoid adding domain models in this task; keep it foundation-only.

## Out of Scope

- Any Meridian business endpoints (events/theses/digests).

