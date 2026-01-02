# Task 04 — Database Migrations + Core Schema

**Epic:** 2 — Database + Seed Data  
**Phase:** 1 (MVP)  
**Depends on:** `task-03.md`  
**Spec references:** `spec.md` Appendix F (schema draft)

## Objective

Implement migrations for the “spine” tables so ingestion/analysis/UI can evolve without hand-editing SQL in prod.

## Deliverables

- Migration tool setup (e.g., Alembic) in `backend/`
- Initial migration creating:
  - `theses`
  - `macro_events`
  - `metals_knowledge`
  - `historical_cases` (including `embedding` vector column)
  - `central_bank_comms`
  - `economic_events`
  - `daily_digests`
- Enable required Postgres extensions (`pgcrypto`, `vector`)

## Acceptance Criteria

- Fresh DB can be created and migrated from zero to latest with one command.
- Schema matches Appendix F fields sufficiently to support Phase 1 features.

## Notes / Risks

- Choose embedding dimension intentionally (ties to the embedding model); don’t hardcode future assumptions in many places.

## Out of Scope

- Any seed data loading.
- Any ingestion pipelines.

