from httpx import ASGITransport, AsyncClient

from app.clients.riot import get_riot_client
from app.main import app


class FakeRiotClient:
    def __init__(self) -> None:
        self.active_calls: list[tuple[str, str]] = []
        self.featured_calls: list[str] = []

    async def get_active_game_by_puuid(self, platform: str, puuid: str) -> dict:
        self.active_calls.append((platform, puuid))
        return {
            "gameId": 123,
            "gameType": "MATCHED_GAME",
            "gameStartTime": 1710000000000,
            "mapId": 11,
            "gameLength": 120,
            "platformId": platform.upper(),
            "gameMode": "CLASSIC",
            "bannedChampions": [],
            "gameQueueConfigId": 420,
            "participants": [],
            "observers": {"encryptionKey": "key"},
        }

    async def get_featured_games(self, platform: str) -> dict:
        self.featured_calls.append(platform)
        return {
            "gameList": [],
            "clientRefreshInterval": 300,
        }


async def test_spectator_active_game_route_accepts_explicit_platform_region() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/spectator/OC1/active/fake-puuid")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["gameId"] == 123
    assert fake_client.active_calls == [("oc1", "fake-puuid")]


async def test_spectator_featured_games_route_accepts_explicit_platform_region() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/spectator/OC1/featured")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "gameList": [],
        "clientRefreshInterval": 300,
    }
    assert fake_client.featured_calls == ["oc1"]


async def test_spectator_routes_reject_routing_region_as_platform() -> None:
    async def fake_riot_client() -> object:
        return object()

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            active_response = await client.get("/api/v1/spectator/SEA/active/fake-puuid")
            featured_response = await client.get("/api/v1/spectator/SEA/featured")
    finally:
        app.dependency_overrides.clear()

    assert active_response.status_code == 422
    assert active_response.json()["detail"]["code"] == "INVALID_REGION"
    assert featured_response.status_code == 422
    assert featured_response.json()["detail"]["code"] == "INVALID_REGION"
