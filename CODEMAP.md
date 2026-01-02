# Code Map & Scopes (Meridian)

This document turns `spec.md` into an implementation-oriented map: where code will
live, how spec areas map to modules, and the build scopes that become future tasks.

## Goals

- Provide a clear, shared repo layout for contributors.
- Map each major spec area -> code location(s) -> responsibilities.
- Define epics (workstreams) and a task backlog that breaks them into smaller,
  sequential task files.

## How Tasks Work (Option B)

- Epics/workstreams are the big scopes (e.g., "Ingestion Pipelines").
- Tasks (`task-01.md`, `task-02.md`, ...) are smaller, buildable increments that
  roll up into an epic.
- Task numbering is a suggested sequence, not a hard dependency graph (use each
  task's "Depends on" field).

## Proposed Repo Layout (target end-state)

> Current repo is docs-only. This is the intended structure once development starts.

```
trading/
  spec.md
  SCQA_Trading_System.md          # archived reference
  CODEMAP.md
  tasks/
    task-00.md

  backend/                        # Python 3.11+ / FastAPI / Celery
    pyproject.toml
    README.md
    app/
      main.py                     # FastAPI entrypoint
      core/                       # settings, logging, time, feature flags
      db/                         # schema/migrations, models, repositories
      api/                        # HTTP routes (events, theses, metals, crypto, digests)
      ingestion/                  # pull external sources -> normalized records
      analysis/                   # scoring, synthesis, transmission, prompts
      services/                   # higher-level workflows (digests, exports)
      integrations/               # LLM providers, Telegram, external APIs
      workers/                    # Celery tasks + schedules
      tests/

  frontend/                       # Next.js 14 (App Router)
    package.json
    next.config.js
    src/
      app/                        # route pages (macro radar, event detail, thesis)
      components/                 # shared UI components
      lib/                        # API client, formatting, constants
      styles/

  data/                           # seed data (cold start)
    metals/                       # knowledge base YAML/JSON
    cases/                        # historical case YAML/JSON
    calendar/                     # optional seed events / mappings

  ops/                            # local dev + deployment
    docker-compose.yml            # Postgres + Redis (dev)
    scripts/                      # deploy/run helpers
```

## Domain Model (what the system stores)

Derived from `spec.md` + Appendix F:

- `macro_events`: raw event + classification + significance score + analysis output
  (raw facts, impacts, precedent, counter-case, crypto transmission)
- `metals_knowledge`: curated structured KB (supply chain, use cases, patterns,
  correlations, actors)
- `historical_cases`: curated event library + embeddings for similarity search
- `theses`: thesis workspace (core thesis, bull/bear, invalidation, updates log,
  status)
- `central_bank_comms`: stored comms + change detection + sentiment
- `economic_events`: calendar entries + surprises
- `daily_digests`: cached daily briefings (Telegram + dashboard)

These tables are the spine of the app: ingestion populates them, analysis enriches
them, UI/bot reads them.

## Code Map (spec -> code areas)

### Macro Intelligence Layer (Phase 1 core)

- Spec: sections 4-7, 8 (Phase 1), 11, Appendices F/G/H
- Code
  - `backend/app/ingestion/rss/` -- Reuters/AP/backup RSS ingestion + dedupe
  - `backend/app/ingestion/central_banks/` -- FOMC/ECB/BOJ fetch + parse + diff
  - `backend/app/ingestion/econ_calendar/` -- calendar sync + surprises
  - `backend/app/ingestion/prices/` -- daily OHLCV pull + caching
  - `backend/app/analysis/scoring/` -- significance score computation + thresholds
    (`>=65`)
  - `backend/app/analysis/metals/` -- apply KB + produce metal impacts
  - `backend/app/analysis/historical/` -- retrieve similar cases (pgvector) +
    citation set
  - `backend/app/analysis/transmission/` -- macro -> crypto transmission evaluation
  - `backend/app/api/` -- endpoints for Macro Radar + event detail
  - `frontend/src/app/(macro)/` -- Macro Radar UI + event deep-dive view

### Thesis Workspace (Phase 1 core)

- Spec: sections 8 (Phase 1), Appendix C, Appendix F
- Code
  - `backend/app/api/theses/` -- CRUD + updates log + export
  - `backend/app/services/thesis_export/` -- render thesis -> markdown (and later
    PDF)
  - `frontend/src/app/thesis/` -- thesis list/detail/edit UI

### Daily Check-in + Telegram Bot (Phase 1 core)

- Spec: sections 11.3-11.4, section 8 (Phase 1), Appendices F/H
- Code
  - `backend/app/services/digests/` -- assemble daily digest (events + prices +
    calendar + thesis)
  - `backend/app/integrations/telegram/` -- bot commands + message rendering
  - `backend/app/workers/schedules.py` -- cron-like schedule for daily digest +
    ingestion cadence

### Crypto-Native Layer (Phase 2)

- Spec: sections 5.5, 7.2-7.3, 8 (Phase 2), 11 (commands)
- Code
  - `backend/app/ingestion/cryptopanic/` -- ingest crypto news + sentiment
  - `backend/app/analysis/narratives/` -- narrative detection + lifecycle +
    crowding score
  - `backend/app/ingestion/telegram_signals/` -- parse forwarded signals + enrich
    (CoinGecko)
  - `frontend/src/app/(crypto)/` -- Crypto Radar UI (narratives + signal inbox)

### Learning & Advanced (Phase 3)

- Spec: section 8 (Phase 3), 12 (metrics/failure modes), Appendix G
- Code
  - `backend/app/analysis/performance/` -- outcome tracking + dashboards
  - `backend/app/analysis/counter_thesis/` -- scheduled challenges +
    invalidation proximity
  - `frontend/src/app/performance/` -- performance + learning UI

## Epics / Workstreams (what we will build)

Use these as the canonical workstreams. Tasks live in separate `task-XX.md`
files and roll up into these epics.

1. Repo + Dev Environment
   - Add `backend/`, `frontend/`, `ops/` scaffolding, local Postgres/Redis,
     env var conventions.
2. Database + Seed Data
   - Implement schema/migrations + seed loaders for metals KB + historical cases
     (`data/`).
3. Ingestion Pipelines (Phase 1)
   - RSS macro news, central bank comms, economic calendar, daily prices
     (idempotent + deduped).
4. LLM Analysis + Scoring (Phase 1)
   - Implement significance scoring, macro event analysis prompt workflow, and
     persistence of outputs.
5. Dashboard UI (Phase 1)
   - Macro Radar, event detail, Metals Intelligence view, Thesis Workspace
     (mobile-first).
6. Telegram Bot + Daily Digest (Phase 1)
   - `/today`, `/events`, metals commands, thesis notes, daily scheduled briefing.
7. Crypto Layer (Phase 2)
   - CryptoPanic ingestion, narrative lifecycle + crowding, signal inbox parsing,
     crypto radar UI.
8. Transmission Layer (Phase 2)
   - Macro->crypto mapping surfaces in both macro event detail and crypto radar.
9. Learning Loop (Phase 3)
   - Outcome tracking, performance metrics, counter-thesis engine + scheduled
     challenges.

## Backlog Index (tasks)

| Task | Title | Epic | Phase |
|------|-------|------|-------|
| `task-01.md` | Establish Repo Skeleton | 1 | 1 |
| `task-02.md` | Local Dev Environment (Postgres + Redis) | 1 | 1 |
| `task-03.md` | Backend Bootstrap (FastAPI + Settings + Health) | 1 | 1 |
| `task-04.md` | Database Migrations + Core Schema | 2 | 1 |
| `task-05.md` | Seed Loader Framework + Metals Knowledge Import | 2 | 1 |
| `task-06.md` | Seed Historical Cases + Embeddings Plumbing | 2 | 1 |
| `task-07.md` | RSS Macro News Ingestion (Events) | 3 | 1 |
| `task-08.md` | Central Bank Comms Ingestion (Fed First) | 3 | 1 |
| `task-09.md` | Economic Calendar Ingestion + Surprise Detection | 3 | 1 |
| `task-10.md` | Price Ingestion (Metals + ETFs + Ratio) | 3 | 1 |
| `task-11.md` | Significance Scoring Engine (0-100) | 4 | 1 |
| `task-12.md` | LLM Provider Abstraction + Macro Event Analysis Pipeline | 4 | 1 |
| `task-13.md` | Historical Matching (pgvector Similarity Search) | 4 | 1 |
| `task-14.md` | Macro -> Crypto Transmission Evaluation | 4 | 1 |
| `task-15.md` | API: Macro Events + Analysis | 5 | 1 |
| `task-16.md` | API: Thesis Workspace (CRUD + Updates + Export) | 5 | 1 |
| `task-17.md` | API: Daily Digest + Metals Snapshot | 6 | 1 |
| `task-18.md` | Frontend Bootstrap (Next.js + Layout + API Client) | 5 | 1 |
| `task-19.md` | UI: Macro Radar (List + Filters) | 5 | 1 |
| `task-20.md` | UI: Event Detail (Raw vs Interpretation) | 5 | 1 |
| `task-21.md` | UI: Thesis Workspace | 5 | 1 |
| `task-22.md` | Telegram Bot Bootstrap + Command Router | 6 | 1 |
| `task-23.md` | Scheduler + Daily Jobs (Ingestion + Digest) | 6 | 1 |

## Key Interfaces (contracts between parts)

Keep these stable to avoid rework:

- Ingestion writes raw-ish records -> `macro_events` / `central_bank_comms` /
  `economic_events` / price snapshots.
- Analysis reads those records + KB/cases -> writes enrichment fields back to
  `macro_events` (facts, impacts, counter-case, transmission).
- UI/Bot read from DB via API only (no direct external fetches from the frontend).
- Raw facts and interpretation remain separate fields end-to-end
  (DB -> API -> UI -> digest).

## Notes / Constraints (from spec)

- Thesis-building > reactive execution; daily OHLCV is acceptable.
- LLM usage is scoped: heavy model for synthesis, cheap/local model for
  extraction/classification.
- Priority gating (`>=65`) drives attention model and alerting.
