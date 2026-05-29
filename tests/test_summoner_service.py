from app.services.summoner_service import SummonerService


class FakeRiotClient:
    def __init__(self) -> None:
        self.calls = 0

    async def get_summoner_by_puuid(self, platform: str, puuid: str) -> dict:
        self.calls += 1
        return {
            "id": "summoner-id",
            "accountId": "account-id",
            "puuid": puuid,
            "profileIconId": 29,
            "revisionDate": 1710000000000,
            "summonerLevel": 123,
        }


async def test_summoner_service_normalizes_riot_response() -> None:
    riot_client = FakeRiotClient()
    service = SummonerService(riot_client)

    response = await service.get_by_puuid("oc1", "fake-puuid")

    assert response.id == "summoner-id"
    assert response.account_id == "account-id"
    assert response.profile_icon_id == 29
    assert response.summoner_level == 123


async def test_summoner_service_reuses_cached_response() -> None:
    riot_client = FakeRiotClient()
    service = SummonerService(riot_client)

    first = await service.get_by_puuid("oc1", "cached-puuid")
    second = await service.get_by_puuid("oc1", "cached-puuid")

    assert first == second
    assert riot_client.calls == 1


class FakeCurrentRiotClient:
    async def get_summoner_by_puuid(self, platform: str, puuid: str) -> dict:
        return {
            "puuid": puuid,
            "profileIconId": 29,
            "revisionDate": 1710000000000,
            "summonerLevel": 123,
        }


async def test_summoner_service_accepts_current_response_without_legacy_ids() -> None:
    service = SummonerService(FakeCurrentRiotClient())

    response = await service.get_by_puuid("oc1", "fake-puuid")

    assert response.id is None
    assert response.account_id is None
    assert response.puuid == "fake-puuid"
    assert response.summoner_level == 123
