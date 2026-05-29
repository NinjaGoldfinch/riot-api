from app.services.status_service import StatusService


class FakeRiotClient:
    def __init__(self) -> None:
        self.calls = 0

    async def get_lol_status(self, platform: str) -> dict:
        self.calls += 1
        return {
            "id": platform,
            "name": "Oceania",
            "locales": ["en_AU"],
            "maintenances": [],
            "incidents": [],
        }


async def test_status_service_normalizes_platform_data_response() -> None:
    riot_client = FakeRiotClient()
    service = StatusService(riot_client)

    response = await service.get_platform_data("oc1")

    assert response.id == "oc1"
    assert response.name == "Oceania"
    assert response.locales == ["en_AU"]


async def test_status_service_reuses_cached_response() -> None:
    riot_client = FakeRiotClient()
    service = StatusService(riot_client)

    first = await service.get_platform_data("oc1")
    second = await service.get_platform_data("oc1")

    assert first == second
    assert riot_client.calls == 1
