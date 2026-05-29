from typing import Literal, TypeAlias

from app.core.errors import InvalidRegionError

PlatformRegion: TypeAlias = Literal[
    "br1",
    "eun1",
    "euw1",
    "jp1",
    "kr",
    "la1",
    "la2",
    "me1",
    "na1",
    "oc1",
    "ph2",
    "ru",
    "sg2",
    "th2",
    "tr1",
    "tw2",
    "vn2",
]
RoutingRegion: TypeAlias = Literal["americas", "asia", "europe", "sea"]

PLATFORM_REGIONS: set[str] = {
    "br1",
    "eun1",
    "euw1",
    "jp1",
    "kr",
    "la1",
    "la2",
    "me1",
    "na1",
    "oc1",
    "ph2",
    "ru",
    "sg2",
    "th2",
    "tr1",
    "tw2",
    "vn2",
}
ROUTING_REGIONS: set[str] = {"americas", "asia", "europe", "sea"}


def parse_platform_region(region: str) -> PlatformRegion:
    normalized = region.lower()
    if normalized not in PLATFORM_REGIONS:
        raise InvalidRegionError(
            f"Invalid platform region '{region}'. Expected one of: {sorted(PLATFORM_REGIONS)}."
        )
    return normalized  # type: ignore[return-value]


def parse_routing_region(region: str) -> RoutingRegion:
    normalized = region.lower()
    if normalized not in ROUTING_REGIONS:
        raise InvalidRegionError(
            f"Invalid routing region '{region}'. Expected one of: {sorted(ROUTING_REGIONS)}."
        )
    return normalized  # type: ignore[return-value]
