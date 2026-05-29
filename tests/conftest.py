import pytest

from app.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache_between_tests() -> None:
    cache.clear()
