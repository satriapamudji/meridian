# Task 16 — API: Thesis Workspace (CRUD + Updates + Export)

**Epic:** 5 — Dashboard UI (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-04.md`  
**Spec references:** `spec.md` Appendix C

## Objective

Implement the thesis workspace backend primitives so the UI/bot can create, update, and export theses.

## Deliverables

- CRUD endpoints:
  - `GET /theses`
  - `POST /theses`
  - `GET /theses/{id}`
  - `PATCH /theses/{id}`
- Updates log endpoint:
  - `POST /theses/{id}/updates`
- Export endpoint:
  - `GET /theses/{id}/export.md`

## Acceptance Criteria

- Thesis includes mandatory bear/counter-case and invalidation fields (can enforce at status transition).
- Export renders a clean markdown doc aligned with Appendix C.

## Notes / Risks

- Avoid mixing “position taken” vs “watching” data; keep optional fields nullable and explicit.

## Out of Scope

- Performance analytics and learning loop.

