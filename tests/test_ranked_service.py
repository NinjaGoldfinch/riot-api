from app.services.ranked_service import RankedService


class FakeRiotClient:
    def __init__(self) -> None:
        self.puuid_calls = 0

    async def get_ranked_entries_by_puuid(self, platform: str, puuid: str) -> list[dict]:
        self.puuid_calls += 1
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
        return []


async def test_ranked_service_normalizes_puuid_response() -> None:
    service = RankedService(FakeRiotClient())

    response = await service.get_by_puuid("oc1", "fake-puuid")

    assert len(response.queues) == 1
    queue = response.queues[0]
    assert queue.queue_type == "RANKED_SOLO_5x5"
    assert queue.league_points == 74
    assert queue.win_rate == 52.5


async def test_ranked_service_reuses_cached_puuid_response() -> None:
    riot_client = FakeRiotClient()
    service = RankedService(riot_client)

    first = await service.get_by_puuid("oc1", "cached-puuid")
    second = await service.get_by_puuid("oc1", "cached-puuid")

    assert first == second
    assert riot_client.puuid_calls == 1
