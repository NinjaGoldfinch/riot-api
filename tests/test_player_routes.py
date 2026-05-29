from httpx import ASGITransport, AsyncClient

from app.clients.riot import get_riot_client
from app.main import app


class FakeRiotClient:
    def __init__(self) -> None:
        self.account_calls: list[tuple[str, str, str]] = []
        self.summoner_calls: list[tuple[str, str]] = []
        self.ranked_calls: list[tuple[str, str]] = []
        self.match_calls: list[tuple[str, str, int, int]] = []

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

    async def get_summoner_by_puuid(self, platform: str, puuid: str) -> dict:
        self.summoner_calls.append((platform, puuid))
        return {
            "puuid": puuid,
            "profileIconId": 29,
            "revisionDate": 1710000000000,
            "summonerLevel": 123,
        }

    async def get_ranked_entries_by_puuid(self, platform: str, puuid: str) -> list[dict]:
        self.ranked_calls.append((platform, puuid))
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

    async def get_match_ids(
        self,
        region: str,
        puuid: str,
        start: int,
        count: int,
    ) -> list[str]:
        self.match_calls.append((region, puuid, start, count))
        return ["OC1_1", "OC1_2"]


async def test_player_summary_route_accepts_explicit_platform_and_match_params() -> None:
    fake_client = FakeRiotClient()

    async def fake_riot_client() -> FakeRiotClient:
        return fake_client

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v2/player/OC1/NinjaGoldfinch/OCENZ/summary?match_start=5&match_count=10"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert fake_client.account_calls == [("asia", "NinjaGoldfinch", "OCENZ")]
    assert fake_client.summoner_calls == [("oc1", "fake-puuid")]
    assert fake_client.ranked_calls == [("oc1", "fake-puuid")]
    assert fake_client.match_calls == [("sea", "fake-puuid", 5, 10)]


async def test_player_summary_route_rejects_non_platform_region() -> None:
    async def fake_riot_client() -> object:
        return object()

    app.dependency_overrides[get_riot_client] = fake_riot_client
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v2/player/SEA/NinjaGoldfinch/OCENZ/summary")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_REGION"


async def test_player_summary_is_not_exposed_under_v1() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/player/NinjaGoldfinch/OCENZ/summary")

    assert response.status_code == 404


async def test_player_summary_requires_explicit_platform_region() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v2/player/NinjaGoldfinch/OCENZ/summary")

    assert response.status_code == 404
