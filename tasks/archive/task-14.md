# Task 14 — Macro → Crypto Transmission Evaluation

**Epic:** 4 — LLM Analysis + Scoring (Phase 1)  
**Phase:** 1 (MVP)  
**Depends on:** `task-12.md`  
**Spec references:** `spec.md` sections 4 (Transmission Layer), Appendix G

## Objective

For analyzed macro events, determine whether a crypto transmission path exists and store it consistently.

## Deliverables

- Transmission schema in `macro_events.crypto_transmission`:
  - `exists` (bool)
  - `path` (string)
  - `strength` (enum-ish string: strong/moderate/weak/none)
  - `relevant_assets` (list)
- Logic to populate this during macro event analysis (LLM-assisted is fine)

## Acceptance Criteria

- Every analyzed event has a transmission payload (even if `exists=false`).
- UI and Telegram can render a consistent line item (“Crypto Path: …”).

## Notes / Risks

- Avoid “BTC pumps” style language; keep it thesis-supportive, not signal-bot tone.

## Out of Scope

- Crypto-native narrative detection (Phase 2).

