# Frontend (Next.js)

Next.js 14 App Router shell with a minimal API client.

## Local run
- Copy `frontend/.env.example` to `frontend/.env.local`.
- Install dependencies: `npm install`.
- Start the dev server: `npm run dev`.
- Visit `http://localhost:3000` and confirm the health badge updates.

## API base URL
- `NEXT_PUBLIC_API_BASE_URL` defaults to `http://localhost:8000`.
- Update `frontend/.env.local` if the backend runs elsewhere.

## Layout
- `src/app/`: route pages (macro radar, metals, theses).
- `src/lib/`: API client, formatting, constants.
- `src/styles/`: global styles.

## Macro Radar
- `/macro-radar` lists events from `/events` with score/date/source/status filters.
- `/macro-radar/[eventId]` shows raw facts first, then interpretation, and can trigger analysis.

## Thesis Workspace
- `/theses` is a single-page workspace with three status sections: **Watching**, **Active**, **Closed**.
- Click a thesis card to load it in the editor panel (query param `?selected=<id>`).
- Use `?mode=new` or the "+ New Thesis" button to create a new thesis.
- **Bull case** and **bear case** are edited as multi-line textareas (one bullet per line).
- **Invalidation** and **bear case** are always shown but required when status is `active`.
- **Updates log** displays existing notes; use the "Add Update" form to append entries.
- **Export**: Each thesis can be exported as Markdown via the backend endpoint.

### Route handlers
- `POST /api/theses` — create a new thesis (redirects to `/theses?selected=<id>`)
- `POST /api/theses/[thesisId]` — update an existing thesis (proxies to backend PATCH)
- `POST /api/theses/[thesisId]/updates` — add an update entry to a thesis

## Conventions
See `../CONVENTIONS.md` for naming and env var standards.
