# Task 08 — Central Bank Comms Ingestion (Fed First)

**Epic:** 3 — Ingestion Pipelines (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-04.md`  
**Spec references:** `spec.md` section 5.2

## Objective

Ingest FOMC communications (statements/minutes/speeches) into `central_bank_comms` with basic change detection.

## Deliverables

- Scheduled fetcher for the Federal Reserve website (start with one comm type)
- Parser that extracts:
  - `published_at`
  - `full_text`
  - `comm_type`
- Basic “diff vs previous” field population (`change_vs_previous`)

## Acceptance Criteria

- New comms are persisted and queryable.
- Change detection works for sequential documents of the same type.

## Notes / Risks

- HTML formats change; keep parsing logic isolated and test with saved fixtures.

## Out of Scope

- ECB/BOJ/BOE ingestion (later tasks can extend).
- Hawkish/dovish sentiment scoring (later in analysis tasks).

