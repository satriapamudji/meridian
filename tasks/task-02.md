# Task 02 — Local Dev Environment (Postgres + Redis)

**Epic:** 1 — Repo + Dev Environment  
**Phase:** 1 (MVP)  
**Depends on:** `task-01.md`  
**Spec references:** `spec.md` section 9, Appendix F

## Objective

Provide a one-command local environment for development: Postgres (with pgvector) + Redis (for background jobs/caching).

## Deliverables

- `ops/docker-compose.yml` with:
  - Postgres + pgvector enabled
  - Redis
- Example env files (e.g., `.env.example`) for backend/frontend
- Documented local run steps in `backend/README.md` and `frontend/README.md`

## Acceptance Criteria

- A developer can start Postgres + Redis locally without manual setup.
- Postgres is configured for extensions used by the spec (at minimum `pgcrypto`, `vector`).

## Notes / Risks

- Keep secrets out of committed files; include examples only.

## Out of Scope

- Production deployment.
- LLM keys, Telegram tokens, or external API keys.

