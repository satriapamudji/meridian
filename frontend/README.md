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

## Conventions
See `../CONVENTIONS.md` for naming and env var standards.
