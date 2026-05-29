from httpx import ASGITransport, AsyncClient

from app.clients.riot import get_riot_client
from app.main import app


class FakeRiotClient:
    def __init__(self) -> None:
        self.rotation_calls: list[str] = []

    async def get_champion_rotation(self, platform: str) -> dict:
        self.rotation_calls.append(platform)
        return {
            "freeChampionIds": [1, 2, 3],
            "freeChampionIdsForNewPlayers": [4, 5],
            "maxNewPlayerLevel": 10,
        }


async def test_champion_rotation_route_accepts_explicit_platform_region() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/champion/OC1/rotation")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "freeChampionIds": [1, 2, 3],
        "freeChampionIdsForNewPlayers": [4, 5],
        "maxNewPlayerLevel": 10,
    }
    assert fake_client.rotation_calls == ["oc1"]


async def test_champion_rotation_route_rejects_routing_region_as_platform() -> None:
    async def fake_riot_client() -> object:
        return object()

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/champion/SEA/rotation")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REGION"
