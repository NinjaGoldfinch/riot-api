from httpx import ASGITransport, AsyncClient

from app.clients.riot import get_riot_client
from app.main import app


class FakeRiotClient:
    def __init__(self) -> None:
        self.puuid_calls: list[tuple[str, str]] = []
        self.summoner_id_calls: list[tuple[str, str]] = []

    async def get_ranked_entries_by_puuid(self, platform: str, puuid: str) -> list[dict]:
        self.puuid_calls.append((platform, puuid))
        return [
            {
                "queueType": "RANKED_SOLO_5x5",
                "tier": "GOLD",
                "rank": "II",
                "leaguePoints": 74,
                "wins": 42,
                "losses": 38,
            }
        ]

    async def get_ranked_entries_by_summoner_id(
        self,
        platform: str,
        summoner_id: str,
    ) -> list[dict]:
        self.summoner_id_calls.append((platform, summoner_id))
        return []


async def test_ranked_route_accepts_explicit_platform_for_puuid() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/ranked/OC1/fake-puuid")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.puuid_calls == [("oc1", "fake-puuid")]
    assert fake_client.summoner_id_calls == []


async def test_ranked_route_rejects_routing_region_as_platform() -> None:
    async def fake_riot_client() -> object:
        return object()

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/ranked/SEA/fake-puuid")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REGION"


async def test_ranked_route_keeps_legacy_summoner_id_lookup() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/ranked/summoner-id/OC1/summoner-id")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.summoner_id_calls == [("oc1", "summoner-id")]


async def test_ranked_route_requires_explicit_platform_region() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ranked/fake-puuid")

    assert response.status_code == 404
