# Task 13 — Historical Matching (pgvector Similarity Search)

**Epic:** 4 — LLM Analysis + Scoring (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-06.md`  
**Spec references:** `spec.md` sections 4, 10.1

## Objective

Given an event (or event text), retrieve the most relevant historical cases to provide precedent and counter-examples.

## Deliverables

- Function/service that returns top K cases by similarity
- Query uses `historical_cases.embedding` with pgvector distance
- Fallback matching (keyword/event_type) if embeddings are not available yet

## Acceptance Criteria

- System can return “relevant historical cases” even in cold start.
- Retrieval is fast enough for interactive use (dashboard event click).

## Notes / Risks

- Build a deterministic fallback path so the system still works without embeddings during early dev.

## Out of Scope

- Full RAG/citation rendering in UI (separate task).

