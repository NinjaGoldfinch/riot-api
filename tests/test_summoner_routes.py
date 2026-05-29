from httpx import ASGITransport, AsyncClient

from app.clients.riot import get_riot_client
from app.main import app


class FakeRiotClient:
    def __init__(self) -> None:
        self.summoner_calls: list[tuple[str, str]] = []

    async def get_summoner_by_puuid(self, platform: str, puuid: str) -> dict:
        self.summoner_calls.append((platform, puuid))
        return {
            "id": "summoner-id",
            "accountId": "account-id",
            "puuid": puuid,
            "profileIconId": 29,
            "revisionDate": 1710000000000,
            "summonerLevel": 123,
        }


async def test_summoner_route_accepts_explicit_platform_region() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/summoner/OC1/fake-puuid")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.summoner_calls == [("oc1", "fake-puuid")]


async def test_summoner_route_rejects_routing_region_as_platform() -> None:
    async def fake_riot_client() -> object:
        return object()

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/summoner/SEA/fake-puuid")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REGION"


async def test_summoner_route_requires_explicit_platform_region() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/summoner/fake-puuid")

    assert response.status_code == 404
