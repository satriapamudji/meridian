# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI + Celery service; entrypoint in `backend/app/main.py`; DB and ingestion code in `backend/app/`.
- `backend/tests/`: pytest suite (`test_*.py`) plus shared fixtures.
- `frontend/`: Next.js app (App Router) planned; source lives in `frontend/src/`.
- `ops/`: local dev helpers and `ops/docker-compose.yml` for Postgres/Redis.
- `data/`: seed data (`metals/`, `cases/`, `calendar/`).
- `tasks/`: task files; completed work moves to `tasks/archive/`.
- Docs: `spec.md`, `CODEMAP.md`, `CONVENTIONS.md`.

## Build, Test, and Development Commands
- `docker compose -f ops/docker-compose.yml up -d` starts Postgres + Redis for local dev.
- `python -m pip install -e .[dev]` installs backend dev deps (pytest/ruff/mypy).
- `uvicorn app.main:app --reload` runs the FastAPI API locally (from `backend/`).
- `alembic upgrade head` applies database migrations.
- `python -m app.db.seed_metals` and `python -m app.db.seed_cases` load seed data.
- `python -m app.ingestion.rss_poller` runs RSS ingestion once; add `--interval` to poll.
- `python -m pytest` runs backend tests.
- Frontend commands are described in `frontend/README.md` once the package setup lands.

## Coding Style & Naming Conventions
- Python modules and packages use `snake_case`; API routes and folders are lowercase with underscores.
- Frontend components use PascalCase filenames (e.g., `MacroRadar.tsx`).
- Docs and tasks use kebab-case filenames (e.g., `task-07.md`).
- Python targets 3.11; ruff enforces `line-length = 100`. Keep type hints where practical.
- Env vars are uppercase; backend uses `MERIDIAN_` prefix and frontend public vars use `NEXT_PUBLIC_`.

## Testing Guidelines
- Tests live under `backend/tests/` and use pytest; name files `test_*.py`.
- Fixtures are in `backend/tests/fixtures/`.
- No explicit coverage threshold yet; add tests for new ingestion, DB, or API behavior.

## Commit & Pull Request Guidelines
- Recent history uses Conventional Commits like `feat: add rss ingestion pipeline`; follow the same pattern.
- Use descriptive branches such as `feature/task-07-rss-ingestion` when relevant to a task file.
- PRs should include a brief summary, linked task (from `tasks/`), and test results.
- Include screenshots for UI changes once the frontend is active.

## Security & Configuration Tips
- Copy `.env.example` to `.env` or `.env.local` and keep secrets out of git.
- Local services boot via `ops/docker-compose.yml`; extensions are created on first boot.
