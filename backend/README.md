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

## Dashboard API (Market Context)
The dashboard provides a real-time view of market conditions for position sizing decisions.

- `GET /dashboard`: Returns the latest market context with regime classifications
- `GET /dashboard/today`: Returns today's context; warns if stale
- `POST /dashboard/refresh`: Triggers fresh ingestion of market data
- `GET /dashboard/instruments`: Returns all watched instruments with metadata
- `GET /dashboard/ratios`: Returns calculated ratio definitions

### Regime Classifications
The dashboard classifies markets into four regimes:
- **Volatility**: calm, normal, elevated, fear, crisis (based on VIX)
- **Dollar**: weak, neutral, strong (based on DXY)
- **Curve**: steep, normal, flat, inverted (based on 2s10s spread)
- **Credit**: tight, normal, wide, stressed, crisis (based on HY spread)

### Position Sizing
The `suggested_size_multiplier` (0.25-1.0) indicates recommended position size
based on current volatility and credit conditions. Use this to scale positions
during elevated risk periods.

## Market context ingestion
- Run once to snapshot current market conditions:
  `python -m app.ingestion.market_context_poller`
- Poll on an interval (seconds):
  `python -m app.ingestion.market_context_poller --interval 3600`
- Preview without DB writes:
  `python -m app.ingestion.market_context_poller --dry-run`
- Verbose output:
  `python -m app.ingestion.market_context_poller --verbose`

The poller fetches from two sources:
- **Yahoo Finance**: 21 symbols including VIX, DXY, SPX, Gold, Oil, BTC, and more
- **FRED API**: 7 series including Treasury yields, breakevens, and HY spreads

Requires `MERIDIAN_FRED_API_KEY` in `backend/.env` for FRED data.

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
- List configured feeds:
  `python -m app.ingestion.rss_poller --list-feeds`
- Override with a single feed:
  `python -m app.ingestion.rss_poller --source custom --url https://example.com/rss`

### Default feeds
The poller uses Google News RSS filtered for specific sources and topics:
- **Wire services**: Reuters, AP, Bloomberg (via `allinurl:` filter)
- **Topic feeds**: Central banks, commodities, geopolitical, inflation

Rate limiting: The poller includes automatic retry with exponential backoff
and delays between feeds to avoid rate limiting from Google News.

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
- Enable dynamic asset discovery via transmission channels:
  `python -m app.analysis.macro_event_analysis --with-discovery`

### Dynamic Asset Discovery
When `--with-discovery` is enabled, the analyzer:
1. Matches the event to transmission channels (oil supply, Fed policy, etc.)
2. Extracts primary and secondary assets from matched channels
3. Injects discovered assets into the LLM prompt
4. Requests asset-specific trading opportunities in the response

The 24 transmission channels span:
- **Commodity Supply**: Oil, gas, metals, agricultural disruptions
- **Currency/FX**: Dollar strength/weakness, EM stress, carry trades
- **Rates/Liquidity**: Fed policy, yield curve, credit conditions
- **Risk Sentiment**: Risk-off/on moves, VIX spikes
- **Sanctions/Controls**: Trade wars, capital controls, export bans
- **Inflation**: CPI spikes, deflation, wage pressures

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

## Telegram bot
The bot provides Telegram-based access to daily digests, events, and thesis management.

### Configuration
Set in `backend/.env`:
- `MERIDIAN_TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `MERIDIAN_TELEGRAM_ALLOWED_CHAT_IDS`: Comma-separated list of allowed chat IDs (empty = allow all, for dev only)

### Running the bot
- Local development (polling mode):
  `python -m app.integrations.telegram.bot`
- Production (webhook mode):
  `python -m app.integrations.telegram.bot --webhook --url https://your-domain.com --port 8443`
- Verbose logging:
  `python -m app.integrations.telegram.bot --verbose`

### Commands
- `/today` - Daily briefing with market context, events, metals, calendar, and theses
- `/events` - List recent priority macro events with significance scores
- `/thesis` - List active theses
- `/note <thesis_id> <text>` - Add an update note to a thesis
- `/help` - Show available commands

## Background Scheduler
The scheduler runs all ingestion and digest jobs on configurable intervals, making Meridian "always on" without manual triggering.

### Running the scheduler
- Run with all jobs executing immediately on startup:
  `python -m app.scheduler`
- Run without initial job execution:
  `python -m app.scheduler --no-initial`
- List configured jobs and their schedules:
  `python -m app.scheduler --list-jobs`

### Scheduled Jobs
| Job | Default Interval | Description |
|-----|------------------|-------------|
| RSS ingestion | Every 10 min | Poll RSS feeds for new macro events |
| Calendar sync | Every 6 hours | Sync economic calendar from Forex Factory |
| Fed communications | Every 60 min | Ingest FOMC statements and Fed releases |
| Price ingestion | Daily (1440 min) | Pull daily prices for core metals |
| Market context | Every 60 min | Fetch VIX, DXY, yields, spreads |
| Digest generation | Daily at 06:00 | Generate daily briefing digest |

### Configuration
Set in `backend/.env`:
- `MERIDIAN_SCHEDULER_TIMEZONE`: Timezone for cron jobs (default: UTC)
- `MERIDIAN_SCHEDULER_RSS_INTERVAL`: Minutes between RSS polls (default: 10)
- `MERIDIAN_SCHEDULER_CALENDAR_INTERVAL`: Minutes between calendar syncs (default: 360)
- `MERIDIAN_SCHEDULER_FED_INTERVAL`: Minutes between Fed syncs (default: 60)
- `MERIDIAN_SCHEDULER_PRICES_INTERVAL`: Minutes between price pulls (default: 1440)
- `MERIDIAN_SCHEDULER_DIGEST_HOUR`: Hour to generate digest (default: 6)
- `MERIDIAN_SCHEDULER_DIGEST_MINUTE`: Minute to generate digest (default: 0)

### Observability
All jobs log their start, completion, and any errors:
```
INFO:app.scheduler.jobs:Starting RSS ingestion job
INFO:app.scheduler.jobs:RSS ingestion complete: total=15 events
```

### Idempotency
All jobs are idempotent - safe to re-run without creating duplicates:
- RSS uses upsert on (source, external_id)
- Calendar uses upsert on (event_name, event_date, region)
- Prices use upsert on (symbol, price_date)
- Digest uses upsert on (digest_date)

## Layout (planned)
- `app/core/`: settings, logging, feature flags.
- `app/data/`: static data definitions (watchlists, instrument metadata).
- `app/db/`: schema, migrations, models, repositories.
- `app/api/`: HTTP routes (events, theses, metals, crypto, digests, dashboard).
- `app/ingestion/`: external sources -> normalized records.
- `app/analysis/`: scoring, synthesis, transmission, prompts, market context.
- `app/services/`: higher-level workflows (digests, exports).
- `app/integrations/`: LLM providers, Telegram, external APIs.
- `app/scheduler/`: APScheduler jobs and background scheduling.
- `app/tests/`: unit and integration tests.

## Conventions
See `../CONVENTIONS.md` for naming and env var standards.
