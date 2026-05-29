from app.services.spectator_service import SpectatorService


class FakeRiotClient:
    def __init__(self) -> None:
        self.active_calls = 0
        self.featured_calls = 0

    async def get_active_game_by_puuid(self, platform: str, puuid: str) -> dict:
        self.active_calls += 1
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
            "participants": [{"puuid": puuid}],
            "observers": {"encryptionKey": "key"},
        }

    async def get_featured_games(self, platform: str) -> dict:
        self.featured_calls += 1
        return {
            "gameList": [{"platformId": platform.upper()}],
            "clientRefreshInterval": 300,
        }


async def test_spectator_service_normalizes_active_game_response() -> None:
    riot_client = FakeRiotClient()
    service = SpectatorService(riot_client)

    response = await service.get_active_game_by_puuid("oc1", "fake-puuid")

    assert response.game_id == 123
    assert response.platform_id == "OC1"
    assert response.participants == [{"puuid": "fake-puuid"}]


async def test_spectator_service_reuses_cached_active_game_response() -> None:
    riot_client = FakeRiotClient()
    service = SpectatorService(riot_client)

    first = await service.get_active_game_by_puuid("oc1", "cached-puuid")
    second = await service.get_active_game_by_puuid("oc1", "cached-puuid")

    assert first == second
    assert riot_client.active_calls == 1


async def test_spectator_service_normalizes_featured_games_response() -> None:
    riot_client = FakeRiotClient()
    service = SpectatorService(riot_client)

    response = await service.get_featured_games("oc1")

    assert response.game_list == [{"platformId": "OC1"}]
    assert response.client_refresh_interval == 300


async def test_spectator_service_reuses_cached_featured_games_response() -> None:
    riot_client = FakeRiotClient()
    service = SpectatorService(riot_client)

    first = await service.get_featured_games("oc1")
    second = await service.get_featured_games("oc1")

    assert first == second
    assert riot_client.featured_calls == 1
