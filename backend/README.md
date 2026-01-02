# Backend (FastAPI)

This folder will hold the FastAPI + Celery backend.

## Local run (planned)
- Create a virtualenv.
- Install dependencies (added in task-03).
- Start the API: `uvicorn app.main:app --reload`.

## Layout (planned)
- `app/core/`: settings, logging, feature flags.
- `app/db/`: schema, migrations, models, repositories.
- `app/api/`: HTTP routes (events, theses, metals, crypto, digests).
- `app/ingestion/`: external sources -> normalized records.
- `app/analysis/`: scoring, synthesis, transmission, prompts.
- `app/services/`: higher-level workflows (digests, exports).
- `app/integrations/`: LLM providers, Telegram, external APIs.
- `app/workers/`: Celery tasks + schedules.
- `app/tests/`: unit and integration tests.

## Conventions
See `../CONVENTIONS.md` for naming and env var standards.
