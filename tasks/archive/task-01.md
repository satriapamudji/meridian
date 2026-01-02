# Task 01 — Establish Repo Skeleton

**Epic:** 1 — Repo + Dev Environment  
**Phase:** 1 (MVP)  
**Depends on:** none  
**Spec references:** `spec.md` sections 4, 8, 9, Appendix H

## Objective

Create a clean, conventional project layout for a Python/FastAPI backend + Next.js frontend + seed data + ops scripts.

## Deliverables

- Directory scaffolding: `backend/`, `frontend/`, `data/`, `ops/`
- Minimal README stubs in `backend/` and `frontend/` describing how to run locally
- Conventions documented (naming, env vars, where ingestion/analysis lives)

## Acceptance Criteria

- A new contributor can infer where to add: ingestion code, scoring logic, API routes, UI routes.
- No business logic implemented yet; this is structure only.

## Notes / Risks

- Keep “raw facts” vs “interpretation” separation in mind when naming DB/API fields (avoid “summary” that mixes both).

## Out of Scope

- Docker/dev services, migrations, or any ingestion/analysis implementation.

