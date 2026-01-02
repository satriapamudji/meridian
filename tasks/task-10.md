# Task 10 — Price Ingestion (Metals + ETFs + Ratio)

**Epic:** 3 — Ingestion Pipelines (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-04.md`  
**Spec references:** `spec.md` section 5.4, section 6.1

## Objective

Ingest daily prices for core metals (and optionally ETFs/miners) and compute basic derived indicators like gold/silver ratio.

## Deliverables

- Scheduled job to pull daily OHLCV for:
  - Gold (GC=F), Silver (SI=F), Copper (HG=F)
  - Optional: GLD, SLV, COPX, NEM, GOLD, FCX
- Store snapshots in a DB table (new table if needed) OR embed into `daily_digests` snapshot payload
- Compute and store gold/silver ratio

## Acceptance Criteria

- Daily prices available for dashboard + digest.
- Ratio calculation is stable and uses the same timestamp basis for both legs.

## Notes / Risks

- Decide early where time-series lives (separate table vs digest snapshots) to avoid rework.

## Out of Scope

- Intraday pricing.
- Trade execution.

