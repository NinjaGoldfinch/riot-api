# Setup

## Local Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `RIOT_API_KEY` in `.env`.

## Run Locally

```bash
scripts/dev.sh
```

The development script uses `.venv` automatically when it exists. Override host or port when needed:

```bash
HOST=127.0.0.1 PORT=8080 scripts/dev.sh
```

## Docker Compose

```bash
docker compose up --build
```

Compose starts:

- `postgres`: Postgres 16 with persistent local Docker volume storage.
- `riot-api`: the FastAPI app.

Postgres first-boot SQL files in `database/init` are mounted into `/docker-entrypoint-initdb.d`. These scripts only run when the Postgres data volume is created for the first time.

## Database Configuration

```env
DATABASE_URL=postgresql+asyncpg://riot_api:riot_api@localhost:5432/riot_api
DATABASE_AUTO_MIGRATE=true
DATABASE_ECHO=false
```

If `DATABASE_URL` is empty, database startup is skipped. If `DATABASE_URL` is set and `DATABASE_AUTO_MIGRATE=true`, the API runs `alembic upgrade head` during startup before serving requests.

Use `DATABASE_ECHO=true` only when you need SQL logging while debugging.

## Migrations

Create a new migration after changing the schema:

```bash
source .venv/bin/activate
alembic revision -m "describe change"
```

Edit the generated file in `migrations/versions`, then apply it:

```bash
scripts/db-migrate.sh
```

The manual script requires `DATABASE_URL` in the environment. With `.env` loaded through Docker Compose, migrations are also applied automatically by the API when `DATABASE_AUTO_MIGRATE=true`.

## First-Boot SQL vs Migrations

Use `database/init` for database-level setup that should exist before migrations, such as extensions or database defaults.

Use Alembic migrations for tables, indexes, constraints, and schema changes. This keeps additions and refactors reviewable, ordered, and reversible.

## Tests And Lint

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
```
