# Configuration

The app reads configuration from environment variables and `.env` through
Pydantic settings. Copy `.env.example` to `.env` for local development.

```bash
cp .env.example .env
```

## Required For Riot Calls

| Variable | Default | Description |
| --- | --- | --- |
| `RIOT_API_KEY` | empty | Riot development or production API key. Required for Riot-backed endpoints. |

## Application

| Variable | Default | Description |
| --- | --- | --- |
| `APP_NAME` | `Riot API` | FastAPI app name and OpenAPI title. |
| `APP_ENV` | `development` | Runtime environment: `development`, `test`, or `production`. |
| `DEFAULT_ROUTING_REGION` | `asia` | Default Account-V1 routing region for `/api/v1/account/{game_name}/{tag_line}`. |

`DEFAULT_ROUTING_REGION` accepts Riot routing regions. `sea` is normalized to
`asia` because Account-V1 does not expose a `sea` routing host.

## CORS

| Variable | Default | Description |
| --- | --- | --- |
| `CORS_ALLOWED_ORIGINS` | empty | Comma-separated frontend origins. CORS is disabled when empty. |

Example:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Database

Database support is optional. If `DATABASE_URL` is empty, database startup is
skipped.

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | empty | SQLAlchemy async database URL. |
| `DATABASE_AUTO_MIGRATE` | `true` | Run Alembic migrations during app startup. |
| `DATABASE_ECHO` | `false` | Enable SQLAlchemy SQL logging. |

Local Postgres URL used by Docker Compose:

```env
DATABASE_URL=postgresql+asyncpg://riot_api:riot_api@localhost:5432/riot_api
```

## Cache TTLs

All cache values are in seconds. Set a resource TTL to `0` to disable caching for
that resource.

| Variable | Default | Description |
| --- | ---: | --- |
| `CACHE_TTL_SECONDS` | `300` | Shared fallback TTL reserved for generic cache use. |
| `ACCOUNT_CACHE_TTL_SECONDS` | `300` | Account lookup cache TTL. |
| `SUMMONER_CACHE_TTL_SECONDS` | `300` | Summoner lookup cache TTL. |
| `RANKED_CACHE_TTL_SECONDS` | `120` | Ranked entries cache TTL. |
| `MATCH_HISTORY_CACHE_TTL_SECONDS` | `60` | Match history ID cache TTL. |
| `MATCH_DETAIL_CACHE_TTL_SECONDS` | `86400` | Match detail cache TTL. |

## Local Rate Limits

These limits apply before Riot-backed route handlers. `/health` is excluded.

| Variable | Default | Description |
| --- | ---: | --- |
| `RATE_LIMIT_ENABLED` | `true` | Enable or disable local in-memory rate limiting. |
| `RATE_LIMIT_REQUESTS` | `60` | Per-client application bucket request limit. |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Application bucket window. |
| `RATE_LIMIT_SERVICE_REQUESTS` | `30` | Per-client service bucket request limit. |
| `RATE_LIMIT_SERVICE_WINDOW_SECONDS` | `60` | Service bucket window. |
| `RATE_LIMIT_METHOD_REQUESTS` | `20` | Per-client method bucket request limit. |
| `RATE_LIMIT_METHOD_WINDOW_SECONDS` | `60` | Method bucket window. |

## Production Notes

- Use a production Riot API key and keep it out of source control.
- Set `APP_ENV=production`.
- Set explicit `CORS_ALLOWED_ORIGINS` for known frontend domains.
- Prefer managed Postgres or another durable persistence layer when persisted
  cache or observation tables become runtime dependencies.
- The current local cache and rate limiter are process-local. Multiple worker
  processes do not share in-memory state.
