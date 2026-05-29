from typing import Literal

from app.core.errors import InvalidRegionError

type PlatformRegion = Literal[
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
type AccountRoutingRegion = Literal["americas", "asia", "europe"]
type RoutingRegion = Literal["americas", "asia", "europe", "sea"]

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
ACCOUNT_ROUTING_REGIONS: set[str] = {"americas", "asia", "europe"}
PLATFORM_TO_ROUTING_REGION: dict[str, RoutingRegion] = {
    "br1": "americas",
    "eun1": "europe",
    "euw1": "europe",
    "jp1": "asia",
    "kr": "asia",
    "la1": "americas",
    "la2": "americas",
    "me1": "europe",
    "na1": "americas",
    "oc1": "sea",
    "ph2": "sea",
    "ru": "europe",
    "sg2": "sea",
    "th2": "sea",
    "tr1": "europe",
    "tw2": "sea",
    "vn2": "sea",
}
PLATFORM_TO_ACCOUNT_ROUTING_REGION: dict[str, AccountRoutingRegion] = {
    "br1": "americas",
    "eun1": "europe",
    "euw1": "europe",
    "jp1": "asia",
    "kr": "asia",
    "la1": "americas",
    "la2": "americas",
    "me1": "europe",
    "na1": "americas",
    "oc1": "asia",
    "ph2": "asia",
    "ru": "europe",
    "sg2": "asia",
    "th2": "asia",
    "tr1": "europe",
    "tw2": "asia",
    "vn2": "asia",
}


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


def parse_account_routing_region(region: str) -> AccountRoutingRegion:
    normalized = region.lower()
    if normalized not in ACCOUNT_ROUTING_REGIONS:
        raise InvalidRegionError(
            f"Invalid Account-V1 routing region '{region}'. "
            f"Expected one of: {sorted(ACCOUNT_ROUTING_REGIONS)}."
        )
    return normalized  # type: ignore[return-value]


def routing_region_for_platform(region: str) -> RoutingRegion:
    platform_region = parse_platform_region(region)
    return PLATFORM_TO_ROUTING_REGION[platform_region]


def normalize_account_routing_region(region: str) -> AccountRoutingRegion:
    normalized = region.lower()
    if normalized in ACCOUNT_ROUTING_REGIONS:
        return normalized  # type: ignore[return-value]
    if normalized == "sea":
        return "asia"
    if normalized in PLATFORM_REGIONS:
        return PLATFORM_TO_ACCOUNT_ROUTING_REGION[normalized]
    raise InvalidRegionError(
        f"Invalid Account-V1 region '{region}'. Expected an account routing region "
        f"({sorted(ACCOUNT_ROUTING_REGIONS)}) or platform region ({sorted(PLATFORM_REGIONS)})."
    )


def normalize_match_routing_region(region: str) -> RoutingRegion:
    normalized = region.lower()
    if normalized in ROUTING_REGIONS:
        return normalized  # type: ignore[return-value]
    if normalized in PLATFORM_REGIONS:
        return PLATFORM_TO_ROUTING_REGION[normalized]
    raise InvalidRegionError(
        f"Invalid Match-V5 region '{region}'. Expected a routing region "
        f"({sorted(ROUTING_REGIONS)}) or platform region ({sorted(PLATFORM_REGIONS)})."
    )
