from app.services.player_service import PlayerService


class FakeRiotClient:
    async def get_account_by_riot_id(
        self,
        region: str,
        game_name: str,
        tag_line: str,
    ) -> dict[str, str]:
        return {
            "puuid": "fake-puuid",
            "gameName": game_name,
            "tagLine": tag_line,
        }

    async def get_summoner_by_puuid(self, platform: str, puuid: str) -> dict:
        return {
            "puuid": puuid,
            "profileIconId": 29,
            "revisionDate": 1710000000000,
            "summonerLevel": 123,
        }

    async def get_ranked_entries_by_puuid(self, platform: str, puuid: str) -> list[dict]:
        return []

    async def get_match_ids(
        self,
        region: str,
        puuid: str,
        start: int,
        count: int,
    ) -> list[str]:
        return ["OC1_1"]


async def test_player_service_composes_summary() -> None:
    service = PlayerService(FakeRiotClient())

    response = await service.get_summary(
        account_region="asia",
        platform_region="oc1",
        match_region="sea",
        game_name="NinjaGoldfinch",
        tag_line="OCENZ",
        match_start=0,
        match_count=5,
    )

    assert response.account.puuid == "fake-puuid"
    assert response.summoner.summoner_level == 123
    assert response.ranked.queues == []
    assert response.recent_matches.match_ids == ["OC1_1"]
