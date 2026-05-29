import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_default_account_routing_region() -> None:
    settings = Settings(_env_file=None)

    assert settings.default_routing_region == "asia"


def test_settings_normalize_region_defaults() -> None:
    settings = Settings(
        _env_file=None,
        default_routing_region="ASIA",
    )

    assert settings.default_routing_region == "asia"


def test_settings_normalize_sea_default_routing_region_to_asia() -> None:
    settings = Settings(_env_file=None, default_routing_region="SEA")

    assert settings.default_routing_region == "asia"


def test_settings_reject_invalid_default_routing_region() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, default_routing_region="oc1")


def test_settings_reject_negative_cache_ttl() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cache_ttl_seconds=-1)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, champion_rotation_cache_ttl_seconds=-1)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, status_cache_ttl_seconds=-1)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, spectator_active_game_cache_ttl_seconds=-1)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, spectator_featured_games_cache_ttl_seconds=-1)


def test_settings_reject_invalid_rate_limit_values() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, rate_limit_requests=0)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, rate_limit_window_seconds=0)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, rate_limit_service_requests=0)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, rate_limit_service_window_seconds=0)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, rate_limit_method_requests=0)

    with pytest.raises(ValidationError):
        Settings(_env_file=None, rate_limit_method_window_seconds=0)


def test_settings_database_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.database_url == ""
    assert settings.database_auto_migrate is True
    assert settings.database_echo is False
