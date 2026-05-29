from app.services.match_service import MatchService


class FakeRiotClient:
    def __init__(self) -> None:
        self.match_id_calls = 0
        self.match_detail_calls = 0

    async def get_match_ids(
        self,
        region: str,
        puuid: str,
        start: int,
        count: int,
    ) -> list[str]:
        self.match_id_calls += 1
        return ["OC1_1", "OC1_2"]

    async def get_match(self, region: str, match_id: str) -> dict:
        self.match_detail_calls += 1
        return {
            "metadata": {"matchId": match_id},
            "info": {
                "gameCreation": 1710000000000,
                "gameDuration": 1800,
                "gameMode": "CLASSIC",
                "queueId": 420,
                "mapId": 11,
                "gameVersion": "15.10.1",
                "teams": [
                    {"teamId": 100, "win": False},
                    {"teamId": 200, "win": True},
                ],
                "participants": [
                    {
                        "puuid": "puuid-1",
                        "riotIdGameName": "NinjaGoldfinch",
                        "riotIdTagline": "OCENZ",
                        "summonerName": "",
                        "championName": "Yone",
                        "championId": 777,
                        "teamId": 200,
                        "teamPosition": "MIDDLE",
                        "kills": 10,
                        "deaths": 0,
                        "assists": 5,
                        "win": True,
                        "goldEarned": 13000,
                        "totalDamageDealtToChampions": 25000,
                        "visionScore": 22,
                        "item0": 3006,
                        "item1": 3031,
                        "item2": 0,
                    },
                    {
                        "puuid": "puuid-2",
                        "kills": 2,
                        "deaths": 4,
                        "assists": 6,
                    },
                ],
            },
        }


async def test_match_service_normalizes_match_ids_response() -> None:
    service = MatchService(FakeRiotClient())

    response = await service.get_match_ids("sea", "fake-puuid", start=0, count=20)

    assert response.match_ids == ["OC1_1", "OC1_2"]


async def test_match_service_reuses_cached_match_history_response() -> None:
    riot_client = FakeRiotClient()
    service = MatchService(riot_client)

    first = await service.get_match_ids("sea", "cached-puuid", start=0, count=20)
    second = await service.get_match_ids("sea", "cached-puuid", start=0, count=20)

    assert first == second
    assert riot_client.match_id_calls == 1


async def test_match_service_normalizes_match_detail_response() -> None:
    service = MatchService(FakeRiotClient())

    response = await service.get_match_detail("sea", "OC1_1")

    assert response.match_id == "OC1_1"
    assert response.map_id == 11
    assert response.game_version == "15.10.1"
    assert response.winning_team_id == 200
    assert len(response.participants) == 2

    participant = response.participants[0]
    assert participant.riot_id_game_name == "NinjaGoldfinch"
    assert participant.riot_id_tagline == "OCENZ"
    assert participant.summoner_name == "NinjaGoldfinch"
    assert participant.champion_id == 777
    assert participant.team_position == "MIDDLE"
    assert participant.kda == 15.0
    assert participant.items == [3006, 3031]


async def test_match_service_handles_missing_optional_participant_fields() -> None:
    service = MatchService(FakeRiotClient())

    response = await service.get_match_detail("sea", "OC1_1")

    participant = response.participants[1]
    assert participant.champion_name is None
    assert participant.kda == 2.0
    assert participant.items == []


async def test_match_service_reuses_cached_match_detail_response() -> None:
    riot_client = FakeRiotClient()
    service = MatchService(riot_client)

    first = await service.get_match_detail("sea", "OC1_CACHE")
    second = await service.get_match_detail("sea", "OC1_CACHE")

    assert first == second
    assert riot_client.match_detail_calls == 1
