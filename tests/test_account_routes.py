from httpx import ASGITransport, AsyncClient

from app.clients.riot import get_riot_client
from app.main import app


class FakeRiotClient:
    def __init__(self) -> None:
        self.account_calls: list[tuple[str, str, str]] = []

    async def get_account_by_riot_id(
        self,
        region: str,
        game_name: str,
        tag_line: str,
    ) -> dict[str, str]:
        self.account_calls.append((region, game_name, tag_line))
        return {
            "puuid": "fake-puuid",
            "gameName": game_name,
            "tagLine": tag_line,
        }


async def test_account_route_uses_default_asia_routing_region() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/account/NinjaGoldfinch/OCENZ")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "puuid": "fake-puuid",
        "gameName": "NinjaGoldfinch",
        "tagLine": "OCENZ",
    }
    assert fake_client.account_calls == [("asia", "NinjaGoldfinch", "OCENZ")]


async def test_account_route_accepts_explicit_account_routing_region() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/account/ASIA/NinjaGoldfinch/OCENZ")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.account_calls == [("asia", "NinjaGoldfinch", "OCENZ")]


async def test_account_route_maps_sea_to_asia() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/account/SEA/NinjaGoldfinch/OCENZ")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.account_calls == [("asia", "NinjaGoldfinch", "OCENZ")]


async def test_account_route_maps_oce_platform_to_asia() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/account/OC1/NinjaGoldfinch/OCENZ")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.account_calls == [("asia", "NinjaGoldfinch", "OCENZ")]
