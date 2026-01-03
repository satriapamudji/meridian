# Backend (FastAPI)

This folder will hold the FastAPI + Celery backend.

## Local run
- From the repo root, start Postgres + Redis:
  `docker compose -f ops/docker-compose.yml up -d`.
- Copy `backend/.env.example` to `backend/.env` and adjust as needed.
- Settings auto-load `backend/.env` when present.
- Create a virtualenv.
- Install dependencies: `python -m pip install -e .[dev]`.
- Start the API: `uvicorn app.main:app --reload`.

## Health checks
- `GET /health`: process OK
- `GET /ready`: DB connectivity check

## Macro events API
- List events with filters:
  `GET /events?priority_only=true&score_min=65&status=new&start_date=2026-02-01&end_date=2026-02-07`
- Get event detail:
  `GET /events/{id}`
- Trigger analysis (idempotent unless `overwrite=true`):
  `POST /events/{id}/analyze`

## Thesis workspace API
- `GET /theses`
- `POST /theses`
- `GET /theses/{id}`
- `PATCH /theses/{id}`
- `POST /theses/{id}/updates`
- `GET /theses/{id}/export.md`

## Daily digest API
- `GET /digest/today`

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

## Historical matching
- Use `app.analysis.historical.find_historical_cases` to retrieve similar cases by
  embedding when available, falling back to keyword/event-type matching.

## Crypto transmission evaluation
- `app.analysis.transmission.evaluate_transmission` provides a lightweight
  fallback for macro-to-crypto paths.
- `app.analysis.transmission.normalize_crypto_transmission` ensures the payload
  includes `exists`, `path`, `strength`, and `relevant_assets`.

## RSS ingestion
- Run once with default feeds:
  `python -m app.ingestion.rss_poller`
- Poll on an interval (seconds):
  `python -m app.ingestion.rss_poller --interval 900`
- Override with a single feed:
  `python -m app.ingestion.rss_poller --source reuters --url https://feeds.reuters.com/reuters/topNews`

## Significance scoring
- Score unscored macro events:
  `python -m app.analysis.significance`
- Preview scoring without DB updates:
  `python -m app.analysis.significance --dry-run`

## Macro event analysis
- Analyze priority events with the local heuristic provider:
  `python -m app.analysis.macro_event_analysis`
- Use OpenRouter (set `MERIDIAN_OPENROUTER_API_KEY` in `backend/.env`):
  `python -m app.analysis.macro_event_analysis --provider openrouter`
- Override the OpenRouter model:
  `python -m app.analysis.macro_event_analysis --provider openrouter --model openai/gpt-4o-mini`
- Re-run analysis and overwrite existing fields:
  `python -m app.analysis.macro_event_analysis --overwrite`
- Analyze a specific event by id:
  `python -m app.analysis.macro_event_analysis --event-id <uuid>`

## Economic calendar ingestion
- Sync upcoming events from JSON fixtures:
  `python -m app.ingestion.economic_calendar --data-dir ../data/calendar --days 7`
- Poll daily (seconds):
  `python -m app.ingestion.economic_calendar --data-dir ../data/calendar --interval 86400`
- Sync from the free Forex Factory feed:
  `python -m app.ingestion.economic_calendar --source forex_factory --days 7`
- Sync from FRED (requires `MERIDIAN_FRED_API_KEY` in `backend/.env`):
  `python -m app.ingestion.economic_calendar --source fred --days 14`
- Note: FRED release dates do not include forecasts or actuals, so surprise fields
  remain empty. Observe FRED's API rate limits in their docs.

## Price ingestion
- Run once with core metals:
  `python -m app.ingestion.prices_poller`
- Include optional ETFs/miners:
  `python -m app.ingestion.prices_poller --include-optional`
- Poll on an interval (seconds):
  `python -m app.ingestion.prices_poller --interval 86400`
- Override symbols:
  `python -m app.ingestion.prices_poller --symbols GC=F,SI=F,HG=F`

## Fed communications ingestion
- Run once with the default FOMC statement index (pulls from the Fed press releases index):
  `python -m app.ingestion.central_banks.fed`
- Poll on an interval (seconds):
  `python -m app.ingestion.central_banks.fed_poller --interval 900`
- Override the index URL:
  `python -m app.ingestion.central_banks.fed_poller --index-url https://www.federalreserve.gov/newsevents/pressreleases/2024-press-fomc.htm`

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
