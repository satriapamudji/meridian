# Task 06 — Seed Historical Cases + Embeddings Plumbing

**Epic:** 2 — Database + Seed Data  
**Phase:** 1 (MVP)  
**Depends on:** `task-04.md`  
**Spec references:** `spec.md` section 10.1, Appendix B

## Objective

Load the cold-start historical case base and set up the mechanics for semantic search (pgvector).

## Deliverables

- `data/cases/` seed format aligned to Appendix B
- Seed command/script:
  - Validates case shape
  - Inserts/updates `historical_cases`
- Embeddings plumbing:
  - A place to compute/store embeddings (even if initially stubbed / manual)
  - A simple “similar cases” query by vector distance

## Acceptance Criteria

- Historical cases can be loaded from disk into DB.
- There is a documented, repeatable way to (eventually) populate embeddings.

## Notes / Risks

- Embeddings generation may require network/paid API; plan for offline-friendly scaffolding first.

## Out of Scope

- Automatically generating embeddings at ingest time (can be later).

