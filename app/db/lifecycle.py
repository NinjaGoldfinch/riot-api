import asyncio

from app.core.config import Settings
from app.db.migrations import run_migrations
from app.db.session import dispose_engine


async def startup_database(settings: Settings) -> None:
    if not settings.database_url or not settings.database_auto_migrate:
        return

    await asyncio.to_thread(run_migrations, settings)


async def shutdown_database() -> None:
    await dispose_engine()
