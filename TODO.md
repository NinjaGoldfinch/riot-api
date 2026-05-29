# TODO

## Stage 5: Account Lookup

- [x] Add a default Account-V1 lookup route that uses configured routing.
- [x] Normalize explicit Account-V1 region input to `americas`, `asia`, or `europe`.
- [x] Verify OCE defaults use `asia` for Account-V1.
- [x] Add route tests for default lookup, explicit lookup, and OCE platform normalization.
- [x] Document the default account lookup endpoint.

## Stage 6: Summoner Profile Lookup

- [x] Keep explicit Summoner-V4 platform routing.
- [x] Reject regional routing values like `sea` when a platform region is required.
- [x] Add route tests for default lookup, explicit lookup, and invalid platform rejection.
- [x] Add service normalization coverage.
- [x] Document the default summoner lookup endpoint.

## Stage 7: Ranked Data Lookup

- [x] Add ranked lookup by PUUID.
- [x] Keep legacy encrypted summoner ID lookup under an explicit path.
- [x] Reject regional routing values like `sea` when a platform region is required.
- [x] Add route tests for default lookup, explicit lookup, invalid platform rejection, and legacy lookup.
- [x] Add service normalization coverage.
- [x] Document the PUUID-first ranked endpoints.

## Stage 8: Match History Lookup

- [x] Keep explicit Match-V5 regional routing.
- [x] Normalize platform routing values like `oc1` to the correct Match-V5 routing region.
- [x] Pass `start` and `count` query params through to Riot.
- [x] Add route tests for default lookup, explicit lookup, region normalization, and query params.
- [x] Add service normalization coverage.
- [x] Document the default match history endpoint.

## Stage 9: Match Detail Normalization

- [x] Keep explicit Match-V5 detail routing.
- [x] Normalize platform routing values like `oc1` to the correct Match-V5 routing region.
- [x] Add richer match metadata fields.
- [x] Add richer participant fields.
- [x] Compute KDA safely, including zero-death games.
- [x] Tolerate missing optional Riot participant fields.
- [x] Add route and service tests.
- [x] Document the default match detail endpoint.

## Stage 10: App Rate Limiting

- [x] Add configurable in-memory per-client rate limiting.
- [x] Add separate application, service, and method buckets.
- [x] Exclude `/health` from rate limiting.
- [x] Return `429` with retry, limit type, and rate-limit status headers.
- [x] Support disabling rate limiting through config.
- [x] Add tests for allowed requests, bucket-specific blocked requests, reset behavior, excluded paths, and disabled mode.
- [x] Document rate-limit settings.
- [x] Capture and forward Riot's live upstream rate-limit headers separately from local limits.

## Stage 11: Response Caching

- [x] Add an in-memory async TTL cache.
- [x] Add configurable TTLs per resource type.
- [x] Cache Account-V1 Riot ID lookups.
- [x] Cache Summoner-V4 PUUID lookups.
- [x] Cache Ranked PUUID and legacy summoner ID lookups.
- [x] Cache Match-V5 history lookups.
- [x] Cache Match-V5 detail lookups with a long TTL.
- [x] Add cache unit tests and service cache tests.
- [x] Document cache settings.

## Stage 12: Player Summary

- [x] Add a composite player summary schema.
- [x] Add a player summary service that composes account, summoner, ranked, and recent match data.
- [x] Add an explicit platform v2 player summary endpoint.
- [x] Normalize platform input into Account-V1 and Match-V5 routing.
- [x] Keep player summary out of v1 resource endpoints.

## Stage 13: Explicit Region Routing

- [x] Keep default routing only for Account-V1 Riot ID lookup.
- [x] Remove default platform endpoints for Summoner-V4, Ranked, Match-V5, and v2 Player Summary.
- [x] Remove `DEFAULT_PLATFORM_REGION` config.
- [x] Update docs and tests to require explicit platform/routing outside Account-V1.
- [x] Add route and service tests.
- [x] Document player summary endpoints.

## Stage 14: Observability Basics

- [x] Add request ID middleware.
- [x] Preserve incoming `X-Request-ID` when provided.
- [x] Return `X-Request-ID` on responses.
- [x] Log request completion with request ID, method, path, status, and duration.
- [x] Add `/version` endpoint.
- [x] Add tests and docs.

## Stage 15: Deployment Readiness

- [x] Add configurable CORS support.
- [x] Keep CORS disabled unless origins are configured.
- [x] Expose request and rate-limit headers through CORS.
- [x] Add Dockerfile.
- [x] Add Docker Compose setup.
- [x] Add Docker ignore rules.
- [x] Add CORS tests.
- [x] Update docs.

## Stage 16: Persistence Foundation

- [x] Add Postgres configuration.
- [x] Add Docker Compose Postgres service.
- [x] Add first-boot database init SQL.
- [x] Add Alembic migration scaffold.
- [x] Add an initial operational schema migration.
- [x] Run migrations automatically on API startup when `DATABASE_URL` is configured.
- [x] Add a manual migration script.
- [x] Add architecture documentation with Mermaid.
- [x] Add setup documentation covering database and migration workflow.
- [x] Add lifecycle/config tests.

## Upcoming Stages

- Future: optional Riot rate-limit discovery cache that learns observed limits by region, service, and method from live Riot response headers.
- Future: stale-while-revalidate caching for hot player data so stale values can be served briefly while Riot refreshes in the background.
- Future: tune hot endpoint TTLs lower for ranked data, summoner details, and match history while keeping completed match details long-lived.
