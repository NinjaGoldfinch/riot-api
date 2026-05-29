# Riot API

FastAPI service for fetching League of Legends data through the Riot Games API with
[Pulsefire](https://pulsefire.ianhco.dev/).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Add your Riot development key to `.env`.

More detailed setup notes are in [docs/setup.md](docs/setup.md). The service architecture is
documented in [docs/architecture.md](docs/architecture.md).

The default region configuration is set for OCE:

```env
DEFAULT_ROUTING_REGION=asia
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DATABASE_URL=postgresql+asyncpg://riot_api:riot_api@localhost:5432/riot_api
DATABASE_AUTO_MIGRATE=true
DATABASE_ECHO=false
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_SERVICE_REQUESTS=30
RATE_LIMIT_SERVICE_WINDOW_SECONDS=60
RATE_LIMIT_METHOD_REQUESTS=20
RATE_LIMIT_METHOD_WINDOW_SECONDS=60
ACCOUNT_CACHE_TTL_SECONDS=300
SUMMONER_CACHE_TTL_SECONDS=300
RANKED_CACHE_TTL_SECONDS=120
MATCH_HISTORY_CACHE_TTL_SECONDS=60
MATCH_DETAIL_CACHE_TTL_SECONDS=86400
```

Only Account-V1 has a default routing region. Other endpoints require explicit platform or
routing input so calls go to the correct Riot host. Account-V1 calls normalize OCE platform
input such as `oc1` to `asia`; Match-V5 calls normalize OCE platform input to `sea`.

## Run

```bash
uvicorn app.main:app --reload
```

Or use the helper scripts:

```bash
scripts/dev.sh
scripts/prod.sh
```

Both scripts use `.venv` automatically when it exists. You can override the host or port:

```bash
HOST=127.0.0.1 PORT=8080 scripts/dev.sh
HOST=0.0.0.0 PORT=8000 WEB_CONCURRENCY=2 scripts/prod.sh
```

Or run the containerized service:

```bash
docker compose up --build
```

Docker Compose starts Postgres, runs any first-boot SQL in `database/init`, waits for the
database to become healthy, and then starts the API. When `DATABASE_URL` is configured and
`DATABASE_AUTO_MIGRATE=true`, the API runs Alembic migrations on startup.

Open:

- API docs: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>
- Version: <http://127.0.0.1:8000/version>

## Initial Endpoints

- `GET /health`
- `GET /version`
- `GET /api/v1/account/{game_name}/{tag_line}`
- `GET /api/v1/account/{region}/{game_name}/{tag_line}`
- `GET /api/v1/summoner/{platform}/{puuid}`
- `GET /api/v1/ranked/{platform}/{puuid}`
- `GET /api/v1/ranked/summoner-id/{platform}/{summoner_id}`
- `GET /api/v1/matches/{region}/{puuid}`
- `GET /api/v1/matches/{region}/detail/{match_id}`
- `GET /api/v2/player/{platform}/{game_name}/{tag_line}/summary`

Region-like path values are normalized per endpoint. For example, `/api/v1/account/oc1/...`
uses Account-V1 routing `asia`, while `/api/v1/matches/oc1/...` uses Match-V5 routing `sea`.

## Rate Limiting

Every HTTP response includes `X-Request-ID`. If the request provides an `X-Request-ID`
header, the API preserves it; otherwise it generates one. Request completion is logged with
the request ID, method, path, status, and duration.

CORS is disabled unless `CORS_ALLOWED_ORIGINS` is set. Configure it with a comma-separated
list of frontend origins:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

When CORS is enabled, browsers can read `X-Request-ID`, local rate-limit status headers, and
forwarded `X-Riot-*` rate-limit headers.

The API includes in-memory per-client application, service, and method rate limits before
Riot-backed routes. `/health` is excluded. Configure them with:

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_SERVICE_REQUESTS=30
RATE_LIMIT_SERVICE_WINDOW_SECONDS=60
RATE_LIMIT_METHOD_REQUESTS=20
RATE_LIMIT_METHOD_WINDOW_SECONDS=60
```

Successful responses include status headers for each bucket:

- `X-RateLimit-Application-*`
- `X-RateLimit-Service-*`
- `X-RateLimit-Method-*`

Limited responses return `429` with `Retry-After`, `X-RateLimit-Type`, and the same bucket
status headers. `X-RateLimit-Type` is one of `application`, `service`, or `method`.

Riot's live upstream rate-limit headers are forwarded separately when Riot includes them:

- `X-Riot-App-Rate-Limit`
- `X-Riot-App-Rate-Limit-Count`
- `X-Riot-Method-Rate-Limit`
- `X-Riot-Method-Rate-Limit-Count`
- `X-Riot-Service-Rate-Limit`
- `X-Riot-Service-Rate-Limit-Count`
- `X-Riot-Rate-Limit-Type`
- `X-Riot-Retry-After`

These `X-Riot-*` headers are the source of truth for Riot's current application, method, and
service limits. Riot may omit service or "other limit" details on some 429 responses.

## Caching

Riot-backed service responses are cached in memory to reduce repeated Riot calls:

```env
ACCOUNT_CACHE_TTL_SECONDS=300
SUMMONER_CACHE_TTL_SECONDS=300
RANKED_CACHE_TTL_SECONDS=120
MATCH_HISTORY_CACHE_TTL_SECONDS=60
MATCH_DETAIL_CACHE_TTL_SECONDS=86400
```

Set a TTL to `0` to disable caching for that resource. Match details use a long TTL because
completed matches do not normally change.

The Riot-backed endpoints are scaffolded through a thin internal client wrapper so route and
service code do not depend directly on Pulsefire.

## Database

Database support is optional until a persistence-backed feature needs it. Configure:

```env
DATABASE_URL=postgresql+asyncpg://riot_api:riot_api@localhost:5432/riot_api
DATABASE_AUTO_MIGRATE=true
DATABASE_ECHO=false
```

Postgres first-boot setup SQL lives in `database/init`. Schema changes live in Alembic
migrations under `migrations/versions`. Run migrations manually with:

```bash
scripts/db-migrate.sh
```

## Riot Client Wrapper

[app/clients/riot.py](app/clients/riot.py) owns Pulsefire setup, async session lifecycle, and
translation of Riot/Pulsefire failures into application errors:

- `404` -> `RIOT_NOT_FOUND`
- `401` / `403` -> `RIOT_FORBIDDEN`
- `429` -> `RIOT_RATE_LIMITED`
- Riot `5xx`, timeouts, and connection failures -> `RIOT_UNAVAILABLE`
