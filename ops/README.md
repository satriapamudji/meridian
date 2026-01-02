# Ops

Local development and deployment helpers.

## Layout (planned)
- `scripts/`: dev and deployment scripts.

## Local dev services
- Start: `docker compose -f ops/docker-compose.yml up -d`
- Stop: `docker compose -f ops/docker-compose.yml down`
- Extensions are created on first boot via `ops/db/init/01-extensions.sql`.
