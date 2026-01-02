# Repo Conventions

These conventions keep the codebase predictable while it grows.

## Naming
- Python modules and packages: snake_case (e.g., `event_scoring.py`).
- API routes and folders: lowercase, use underscores for multi-word module names.
- Frontend components: PascalCase files (e.g., `MacroRadar.tsx`).
- Docs and tasks: kebab-case filenames (e.g., `task-01.md`).

## Environment Variables
- Use uppercase names.
- Backend variables use the `MERIDIAN_` prefix (e.g., `MERIDIAN_ENV`,
  `MERIDIAN_DATABASE_URL`).
- Frontend public vars must use `NEXT_PUBLIC_` and are read from `.env.local`.
- Never commit secrets; use local `.env` files.

## Code Locations
- Ingestion: `backend/app/ingestion/`
- Analysis and scoring: `backend/app/analysis/`
- API routes: `backend/app/api/`
- UI routes: `frontend/src/app/`
- Shared UI components: `frontend/src/components/`
