from app.services.champion_service import ChampionService


class FakeRiotClient:
    def __init__(self) -> None:
        self.calls = 0

    async def get_champion_rotation(self, platform: str) -> dict:
        self.calls += 1
        return {
            "freeChampionIds": [1, 2],
            "freeChampionIdsForNewPlayers": [3],
            "maxNewPlayerLevel": 10,
        }


async def test_champion_service_normalizes_rotation_response() -> None:
    riot_client = FakeRiotClient()
    service = ChampionService(riot_client)

    response = await service.get_rotation("oc1")

    assert response.free_champion_ids == [1, 2]
    assert response.free_champion_ids_for_new_players == [3]
    assert response.max_new_player_level == 10


async def test_champion_service_reuses_cached_response() -> None:
    riot_client = FakeRiotClient()
    service = ChampionService(riot_client)

    first = await service.get_rotation("oc1")
    second = await service.get_rotation("oc1")

    assert first == second
    assert riot_client.calls == 1
