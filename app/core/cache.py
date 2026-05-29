from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from time import monotonic
from typing import TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry[T]:
    value: T
    expires_at: float


class AsyncTTLCache:
    def __init__(self, *, clock: Callable[[], float] = monotonic) -> None:
        self._clock = clock
        self._entries: dict[str, CacheEntry] = {}

    async def get_or_set(
        self,
        key: str,
        ttl_seconds: int,
        factory: Callable[[], Awaitable[T]],
    ) -> T:
        if ttl_seconds <= 0:
            return await factory()

        now = self._clock()
        entry = self._entries.get(key)
        if entry is not None and entry.expires_at > now:
            return entry.value

        value = await factory()
        self._entries[key] = CacheEntry(value=value, expires_at=now + ttl_seconds)
        return value

    def clear(self) -> None:
        self._entries.clear()


cache = AsyncTTLCache()
