# Task 07 — RSS Macro News Ingestion (Events)

**Epic:** 3 — Ingestion Pipelines (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-04.md`  
**Spec references:** `spec.md` section 5.1

## Objective

Ingest macro news via RSS and store normalized events in `macro_events`.

## Deliverables

- RSS poller (scheduled job) for:
  - Reuters RSS
  - AP RSS
  - Backup feed (e.g., Google News) if desired
- Dedupe strategy:
  - Canonical key based on normalized headline + published timestamp + source
  - Handles reposts/updates gracefully
- Store in `macro_events` with `status='new'` (no analysis yet)

## Acceptance Criteria

- Ingestion is idempotent (re-running doesn’t create duplicates).
- Events have enough fields populated to support later scoring/analysis.

## Notes / Risks

- RSS feeds can be noisy; avoid triggering expensive analysis directly in the poller.

## Out of Scope

- LLM analysis or significance scoring.

