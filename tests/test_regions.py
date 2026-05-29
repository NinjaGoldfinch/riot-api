import pytest

from app.core.errors import InvalidRegionError
from app.core.regions import parse_platform_region, parse_routing_region


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
