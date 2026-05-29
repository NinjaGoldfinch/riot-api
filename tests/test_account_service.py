from app.services.account_service import AccountService


class FakeRiotClient:
    def __init__(self) -> None:
        self.calls = 0

    async def get_account_by_riot_id(
        self,
        region: str,
        game_name: str,
        tag_line: str,
    ) -> dict[str, str]:
        self.calls += 1
        return {
            "puuid": "fake-puuid",
            "gameName": game_name,
            "tagLine": tag_line,
        }


async def test_account_service_reuses_cached_response() -> None:
    riot_client = FakeRiotClient()
    service = AccountService(riot_client)

    first = await service.get_by_riot_id("asia", "NinjaGoldfinch", "OCENZ")
    second = await service.get_by_riot_id("asia", "ninjagoldfinch", "ocenz")

    assert first.puuid == "fake-puuid"
    assert second.puuid == "fake-puuid"
    assert riot_client.calls == 1
