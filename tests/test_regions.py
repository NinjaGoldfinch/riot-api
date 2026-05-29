import pytest

from app.core.errors import InvalidRegionError
from app.core.regions import (
    normalize_account_routing_region,
    normalize_match_routing_region,
    parse_account_routing_region,
    parse_platform_region,
    parse_routing_region,
    routing_region_for_platform,
)


def test_parse_platform_region_normalizes_value() -> None:
    assert parse_platform_region("NA1") == "na1"


def test_parse_platform_region_rejects_routing_region() -> None:
    with pytest.raises(InvalidRegionError):
        parse_platform_region("americas")


def test_parse_routing_region_normalizes_value() -> None:
    assert parse_routing_region("AMERICAS") == "americas"


def test_parse_routing_region_rejects_platform_region() -> None:
    with pytest.raises(InvalidRegionError):
        parse_routing_region("na1")


def test_parse_account_routing_region_normalizes_value() -> None:
    assert parse_account_routing_region("ASIA") == "asia"


def test_parse_account_routing_region_rejects_sea() -> None:
    with pytest.raises(InvalidRegionError):
        parse_account_routing_region("sea")


def test_normalize_account_region_maps_oce_platform_to_asia() -> None:
    assert normalize_account_routing_region("oc1") == "asia"


def test_normalize_account_region_maps_sea_to_asia() -> None:
    assert normalize_account_routing_region("sea") == "asia"


def test_normalize_match_region_maps_oce_platform_to_sea() -> None:
    assert normalize_match_routing_region("oc1") == "sea"


def test_oce_platform_maps_to_sea_routing_region() -> None:
    assert routing_region_for_platform("oc1") == "sea"
