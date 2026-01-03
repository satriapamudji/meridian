# Task 21 — UI: Thesis Workspace

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-16.md`, `task-18.md`  
**Spec references:** `spec.md` Appendix C

## Objective

Implement thesis list + thesis detail/edit UI with updates log and markdown export.

## Deliverables

- Thesis list page (watching/active/closed)
- Thesis editor/detail page:
  - core thesis + trigger + precedent
  - bull case + bear/counter-case (required for “active”)
  - key levels (entry/target/invalidation)
  - updates log (add entries)
  - export link

## Acceptance Criteria

- User can create a thesis, add updates, and export markdown.
- Required fields are enforced at the UI boundary (and validated server-side too).

## Notes / Risks

- Keep thesis workflow friction low but make invalidation/counter-case unavoidable for “active” status.

## Out of Scope

- Linking to executed trades (Phase 3).

