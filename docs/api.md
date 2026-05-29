# API Reference

This service exposes normalized League of Legends data from Riot Games through a
small FastAPI surface. The canonical machine-readable contract is
[`docs/openapi.json`](openapi.json), generated from the running FastAPI app.

Interactive docs are also available when the service is running:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Base URLs

Local development defaults to:

```text
http://127.0.0.1:8000
```

The API currently has two endpoint groups:

- `/api/v1`: normalized Riot resource endpoints.
- `/api/v2`: composed product endpoints that combine multiple v1 resources.

## Health

### `GET /health`

Returns basic service readiness information.

```json
{
  "status": "ok",
  "environment": "development"
}
```

### `GET /version`

Returns app identity, version, and environment.

```json
{
  "name": "Riot API",
  "version": "0.1.0",
  "environment": "development"
}
```

## Accounts

### `GET /api/v1/account/{game_name}/{tag_line}`

Looks up a Riot account by Riot ID using `DEFAULT_ROUTING_REGION`.

Example:

```bash
curl http://127.0.0.1:8000/api/v1/account/NinjaGoldfinch/OCENZ
```

Response:

```json
{
  "puuid": "string",
  "gameName": "NinjaGoldfinch",
  "tagLine": "OCENZ"
}
```

### `GET /api/v1/account/{region}/{game_name}/{tag_line}`

Looks up a Riot account by Riot ID using an explicit Account-V1 routing region.
The `region` path parameter accepts account routing regions or platform regions.
Platform regions are mapped to the correct Account-V1 routing region.

Example:

```bash
curl http://127.0.0.1:8000/api/v1/account/oc1/NinjaGoldfinch/OCENZ
```

For OCE, `oc1` and `sea` normalize to Account-V1 routing region `asia`.

## Summoner

### `GET /api/v1/summoner/{platform}/{puuid}`

Fetches summoner profile data by PUUID. The `platform` parameter must be a Riot
platform region such as `oc1`, `na1`, `euw1`, or `kr`.

Example:

```bash
curl http://127.0.0.1:8000/api/v1/summoner/oc1/{puuid}
```

Response:

```json
{
  "id": "string",
  "accountId": "string",
  "puuid": "string",
  "profileIconId": 29,
  "revisionDate": 1710000000000,
  "summonerLevel": 123
}
```

## Ranked

### `GET /api/v1/ranked/{platform}/{puuid}`

Fetches ranked entries by PUUID for a platform region.

Example:

```bash
curl http://127.0.0.1:8000/api/v1/ranked/oc1/{puuid}
```

Response:

```json
{
  "queues": [
    {
      "queue_type": "RANKED_SOLO_5x5",
      "tier": "GOLD",
      "rank": "II",
      "league_points": 74,
      "wins": 42,
      "losses": 38,
      "win_rate": 52.5
    }
  ]
}
```

### `GET /api/v1/ranked/summoner-id/{platform}/{summoner_id}`

Legacy lookup path for ranked entries by encrypted summoner ID.

## Matches

### `GET /api/v1/matches/{region}/{puuid}`

Fetches recent match IDs by PUUID. The `region` parameter accepts routing regions
or platform regions. Platform regions are mapped to the correct Match-V5 routing
region.

Query parameters:

| Name | Default | Bounds | Description |
| --- | ---: | --- | --- |
| `start` | `0` | `>= 0` | Offset into the match history. |
| `count` | `20` | `1..100` | Number of match IDs to return. |

Example:

```bash
curl "http://127.0.0.1:8000/api/v1/matches/oc1/{puuid}?start=0&count=10"
```

Response:

```json
{
  "match_ids": ["OC1_1234567890"]
}
```

### `GET /api/v1/matches/{region}/detail/{match_id}`

Fetches and normalizes match details for a match ID.

Example:

```bash
curl http://127.0.0.1:8000/api/v1/matches/oc1/detail/OC1_1234567890
```

Response fields include match metadata, winning team ID, and normalized
participant stats including KDA and non-empty item slots.

## Player Summary

### `GET /api/v2/player/{platform}/{game_name}/{tag_line}/summary`

Composes account, summoner, ranked, and recent match history data into one
product-oriented response. The `platform` parameter must be a Riot platform
region. The service maps that platform to the correct Account-V1 and Match-V5
routing regions internally.

Query parameters:

| Name | Default | Bounds | Description |
| --- | ---: | --- | --- |
| `match_start` | `0` | `>= 0` | Offset into the player match history. |
| `match_count` | `5` | `1..20` | Number of recent match IDs to include. |

Example:

```bash
curl "http://127.0.0.1:8000/api/v2/player/oc1/NinjaGoldfinch/OCENZ/summary?match_count=10"
```

Response:

```json
{
  "account": {
    "puuid": "string",
    "gameName": "NinjaGoldfinch",
    "tagLine": "OCENZ"
  },
  "summoner": {
    "id": "string",
    "accountId": "string",
    "puuid": "string",
    "profileIconId": 29,
    "revisionDate": 1710000000000,
    "summonerLevel": 123
  },
  "ranked": {
    "queues": []
  },
  "recent_matches": {
    "match_ids": []
  }
}
```

## Region Rules

Platform regions:

```text
br1, eun1, euw1, jp1, kr, la1, la2, me1, na1, oc1, ph2, ru, sg2, th2, tr1, tw2, vn2
```

Routing regions:

```text
americas, asia, europe, sea
```

Account-V1 routing regions:

```text
americas, asia, europe
```

Important OCE behavior:

- Account-V1 maps `oc1` and `sea` to `asia`.
- Match-V5 maps `oc1` to `sea`.
- Platform-only endpoints reject routing regions such as `sea`.

## Errors

Application errors use a consistent JSON shape:

```json
{
  "detail": {
    "code": "INVALID_REGION",
    "message": "Invalid platform region 'SEA'. Expected one of: [...]"
  }
}
```

Known error codes:

| Code | Status | Meaning |
| --- | ---: | --- |
| `INVALID_REGION` | `422` | A platform or routing region path value is invalid for the endpoint. |
| `CONFIGURATION_ERROR` | `500` | Required application configuration is missing or invalid. |
| `RIOT_NOT_FOUND` | `404` | Riot returned not found for the upstream resource. |
| `RIOT_FORBIDDEN` | `502` | Riot rejected the request because credentials are missing or forbidden. |
| `RIOT_RATE_LIMITED` | `429` | Riot returned an upstream rate-limit response. |
| `RIOT_UNAVAILABLE` | `503` | Riot is unavailable, timed out, or returned a server error. |

FastAPI validation errors use FastAPI's standard validation response body.

## Headers

Every response includes `X-Request-ID`. If the caller supplies this header, the
service preserves it; otherwise a request ID is generated.

Local rate-limit responses include:

- `X-RateLimit-Application-*`
- `X-RateLimit-Service-*`
- `X-RateLimit-Method-*`
- `X-RateLimit-Type`
- `Retry-After`

Riot upstream rate-limit headers are forwarded with an `X-Riot-*` prefix when
Riot includes them.
