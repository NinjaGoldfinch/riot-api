from httpx import ASGITransport, AsyncClient

from app.clients.riot import get_riot_client
from app.main import app


class FakeRiotClient:
    def __init__(self) -> None:
        self.match_id_calls: list[tuple[str, str, int, int]] = []
        self.match_detail_calls: list[tuple[str, str]] = []

    async def get_match_ids(
        self,
        region: str,
        puuid: str,
        start: int,
        count: int,
    ) -> list[str]:
        self.match_id_calls.append((region, puuid, start, count))
        return ["OC1_1", "OC1_2"]

    async def get_match(self, region: str, match_id: str) -> dict:
        self.match_detail_calls.append((region, match_id))
        return {
            "metadata": {"matchId": match_id},
            "info": {
                "gameDuration": 1800,
                "participants": [],
                "teams": [{"teamId": 100, "win": True}],
            },
        }


async def test_match_history_route_accepts_explicit_routing_region_and_query_params() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/matches/SEA/fake-puuid?start=5&count=10")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.match_id_calls == [("sea", "fake-puuid", 5, 10)]


async def test_match_history_route_maps_platform_region_to_routing_region() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/matches/OC1/fake-puuid")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.match_id_calls == [("sea", "fake-puuid", 0, 20)]


async def test_match_detail_route_maps_platform_region_to_routing_region() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/matches/OC1/detail/OC1_1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.match_detail_calls == [("sea", "OC1_1")]


async def test_match_history_route_requires_explicit_region() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/matches/fake-puuid")

    assert response.status_code == 404


async def test_match_detail_route_requires_explicit_region() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/matches/detail/OC1_1")

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REGION"
