from app.core.cache import AsyncTTLCache


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


async def test_cache_reuses_value_before_ttl_expires() -> None:
    clock = FakeClock()
    cache = AsyncTTLCache(clock=clock)
    calls = 0

    async def factory() -> str:
        nonlocal calls
        calls += 1
        return f"value-{calls}"

    first = await cache.get_or_set("key", 60, factory)
    second = await cache.get_or_set("key", 60, factory)

    assert first == "value-1"
    assert second == "value-1"
    assert calls == 1


async def test_cache_refreshes_value_after_ttl_expires() -> None:
    clock = FakeClock()
    cache = AsyncTTLCache(clock=clock)
    calls = 0

    async def factory() -> str:
        nonlocal calls
        calls += 1
        return f"value-{calls}"

    first = await cache.get_or_set("key", 60, factory)
    clock.advance(60)
    second = await cache.get_or_set("key", 60, factory)

    assert first == "value-1"
    assert second == "value-2"


async def test_cache_bypasses_when_ttl_is_zero() -> None:
    cache = AsyncTTLCache()
    calls = 0

    async def factory() -> str:
        nonlocal calls
        calls += 1
        return f"value-{calls}"

    first = await cache.get_or_set("key", 0, factory)
    second = await cache.get_or_set("key", 0, factory)

    assert first == "value-1"
    assert second == "value-2"
