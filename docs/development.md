# Development Guide

## Project Layout

```text
app/
  api/routes/       HTTP route declarations and versioned URL shape
  clients/          Riot/Pulsefire client wrapper
  core/             Config, errors, CORS, regions, headers, rate limits
  db/               Optional database lifecycle and sessions
  schemas/          Pydantic response models
  services/         Riot workflows, normalization, and cache use
database/init/      Postgres first-boot SQL
migrations/         Alembic migration environment and versions
scripts/            Local operational helper scripts
tests/              Pytest suite
docs/               Human and machine-readable documentation
```

## Common Commands

Create a local environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Run the API:

```bash
scripts/dev.sh
```

Run tests and lint:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
```

Run migrations:

```bash
scripts/db-migrate.sh
```

Export OpenAPI:

```bash
scripts/export-openapi.sh
```

## Endpoint Conventions

- Add normalized Riot resource endpoints under `/api/v1`.
- Add composed or product-oriented endpoints under `/api/v2`.
- Keep route modules focused on HTTP concerns: path/query parameters,
  dependency injection, response model declaration, and versioned URL shape.
- Put Riot workflow composition, normalization, and caching in services.
- Keep direct Pulsefire usage inside `app/clients/riot.py`.

## Schema Conventions

- Response models live in `app/schemas`.
- Prefer stable, frontend-friendly field names over leaking upstream Riot shape.
- Keep Riot's camelCase names only where preserving upstream compatibility is
  intentional, such as `gameName`, `tagLine`, and `profileIconId`.
- Regenerate `docs/openapi.json` when route signatures or response schemas
  change.

## Testing Conventions

- Route tests should override `get_riot_client` with a fake client instead of
  calling Riot.
- Service tests should validate cache keys, region mapping, and response
  normalization behavior.
- Region behavior deserves explicit tests because platform routing and Account-V1
  routing are intentionally different for OCE/SEA.
- Add migration tests when persistence-backed behavior starts depending on new
  tables, indexes, or constraints.
