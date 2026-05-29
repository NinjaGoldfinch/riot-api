import asyncio
from unittest.mock import AsyncMock

import aiohttp
import pytest

from app.clients import riot
from app.clients.riot import RiotClient
from app.core.errors import (
    ConfigurationError,
    RiotAPIError,
    RiotForbiddenError,
    RiotNotFoundError,
    RiotRateLimitError,
    RiotUnavailableError,
)


def test_riot_client_configures_certifi_bundle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)

    RiotClient("test-key", pulsefire_client=FakePulsefireClient(default_headers={}))

    assert "certifi" in riot.os.environ["SSL_CERT_FILE"]


class FakePulsefireClient:
    def __init__(self, *, default_headers: dict[str, str]) -> None:
        self.default_headers = default_headers
        self.session = None

    async def get_account_v1_by_riot_id(self, **kwargs):
        if self.session is None:
            raise RuntimeError("session is None, cannot perform HTTP request")
        return kwargs


class FakeClientSession:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def make_response_error(status: int) -> aiohttp.ClientResponseError:
    return aiohttp.ClientResponseError(
        request_info=None,
        history=(),
        status=status,
        message="Riot API error",
    )


def test_riot_client_rejects_missing_api_key() -> None:
    with pytest.raises(ConfigurationError):
        RiotClient("")


async def test_riot_client_opens_pulsefire_before_request(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client: FakePulsefireClient | None = None
    fake_session = FakeClientSession()

    def create_fake_client(*, default_headers: dict[str, str], **_: object) -> FakePulsefireClient:
        nonlocal fake_client
        fake_client = FakePulsefireClient(default_headers=default_headers)
        return fake_client

    monkeypatch.setattr(riot, "RiotAPIClient", create_fake_client)
    monkeypatch.setattr(riot, "create_client_session", lambda: fake_session)

    client = RiotClient("test-key")

    response = await client.get_account_by_riot_id("asia", "NinjaGoldfinch", "OCENZ")

    assert response == {
        "region": "asia",
        "game_name": "NinjaGoldfinch",
        "tag_line": "OCENZ",
    }
    assert fake_client is not None
    assert fake_client.default_headers == {"X-Riot-Token": "test-key"}
    assert fake_client.session is fake_session

    await client.close()

    assert fake_session.closed is True
    assert fake_client.session is None


async def test_riot_client_open_is_concurrency_safe(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client: FakePulsefireClient | None = None
    created_sessions: list[FakeClientSession] = []

    def create_fake_client(*, default_headers: dict[str, str], **_: object) -> FakePulsefireClient:
        nonlocal fake_client
        fake_client = FakePulsefireClient(default_headers=default_headers)
        return fake_client

    def create_fake_session() -> FakeClientSession:
        session = FakeClientSession()
        created_sessions.append(session)
        return session

    monkeypatch.setattr(riot, "RiotAPIClient", create_fake_client)
    monkeypatch.setattr(riot, "create_client_session", create_fake_session)

    client = RiotClient("test-key")

    await asyncio.gather(client.open(), client.open())

    assert fake_client is not None
    assert len(created_sessions) == 1
    assert fake_client.session is created_sessions[0]

    await client.close()


async def test_riot_client_translates_closed_session_runtime_error() -> None:
    client = RiotClient("test-key", pulsefire_client=FakePulsefireClient(default_headers={}))

    with pytest.raises(RiotUnavailableError):
        await client.get_account_by_riot_id("asia", "NinjaGoldfinch", "OCENZ")


async def test_get_summoner_by_puuid_calls_pulsefire_method() -> None:
    pulsefire_client = AsyncMock()
    pulsefire_client.get_lol_summoner_v4_by_puuid.return_value = {"puuid": "puuid"}
    client = RiotClient("test-key", pulsefire_client=pulsefire_client)

    await client.get_summoner_by_puuid("oc1", "puuid")

    pulsefire_client.get_lol_summoner_v4_by_puuid.assert_awaited_once_with(
        region="oc1",
        puuid="puuid",
    )


async def test_get_ranked_entries_by_summoner_id_calls_pulsefire_method() -> None:
    pulsefire_client = AsyncMock()
    pulsefire_client.get_lol_league_v4_entries_by_summoner.return_value = []
    client = RiotClient("test-key", pulsefire_client=pulsefire_client)

    await client.get_ranked_entries_by_summoner_id("oc1", "summoner-id")

    pulsefire_client.get_lol_league_v4_entries_by_summoner.assert_awaited_once_with(
        region="oc1",
        summoner_id="summoner-id",
    )


async def test_get_match_ids_calls_pulsefire_method_with_queries() -> None:
    pulsefire_client = AsyncMock()
    pulsefire_client.get_lol_match_v5_match_ids_by_puuid.return_value = ["OC1_1"]
    client = RiotClient("test-key", pulsefire_client=pulsefire_client)

    result = await client.get_match_ids("sea", "puuid", start=5, count=10)

    assert result == ["OC1_1"]
    pulsefire_client.get_lol_match_v5_match_ids_by_puuid.assert_awaited_once_with(
        region="sea",
        puuid="puuid",
        queries={"start": 5, "count": 10},
    )


async def test_get_match_calls_pulsefire_method() -> None:
    pulsefire_client = AsyncMock()
    pulsefire_client.get_lol_match_v5_match.return_value = {"metadata": {"matchId": "OC1_1"}}
    client = RiotClient("test-key", pulsefire_client=pulsefire_client)

    await client.get_match("sea", "OC1_1")

    pulsefire_client.get_lol_match_v5_match.assert_awaited_once_with(region="sea", id="OC1_1")


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (404, RiotNotFoundError),
        (403, RiotForbiddenError),
        (429, RiotRateLimitError),
        (500, RiotUnavailableError),
        (400, RiotAPIError),
    ],
)
async def test_riot_http_errors_are_translated(
    status_code: int,
    expected_error: type[RiotAPIError],
) -> None:
    pulsefire_client = AsyncMock()
    pulsefire_client.get_lol_match_v5_match.side_effect = make_response_error(status_code)
    client = RiotClient("test-key", pulsefire_client=pulsefire_client)

    with pytest.raises(expected_error):
        await client.get_match("sea", "OC1_1")


async def test_connection_errors_are_translated() -> None:
    pulsefire_client = AsyncMock()
    pulsefire_client.get_lol_match_v5_match.side_effect = aiohttp.ClientConnectionError()
    client = RiotClient("test-key", pulsefire_client=pulsefire_client)

    with pytest.raises(RiotUnavailableError):
        await client.get_match("sea", "OC1_1")
