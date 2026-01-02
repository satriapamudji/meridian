# Backend (FastAPI)

This folder will hold the FastAPI + Celery backend.

## Local run
- From the repo root, start Postgres + Redis:
  `docker compose -f ops/docker-compose.yml up -d`.
- Copy `backend/.env.example` to `backend/.env` and adjust as needed.
- Create a virtualenv.
- Install dependencies: `python -m pip install -e .[dev]`.
- Start the API: `uvicorn app.main:app --reload`.

## Health checks
- `GET /health`: process OK
- `GET /ready`: DB connectivity check

## Migrations
- Apply schema: `alembic upgrade head`
- The initial migration sets the `vector(1536)` embedding dimension. If you
  change embedding models later, add a migration to adjust the column.

## Seed metals knowledge
- Start services: `docker compose -f ops/docker-compose.yml up -d`
- Run: `python -m app.db.seed_metals`

## Seed historical cases
- Run: `python -m app.db.seed_cases`

## Embeddings plumbing
- Apply embeddings from a JSON file:
  `python -m app.db.embeddings --embeddings-file path/to/embeddings.json`
- Query similar cases by vector distance:
  `python -m app.db.similar_cases --embedding-file path/to/embedding.json`

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
