from app.core.config import Settings
from app.db.lifecycle import startup_database


async def test_startup_database_skips_without_database_url() -> None:
    settings = Settings(_env_file=None, database_url="")

    await startup_database(settings)


async def test_startup_database_skips_when_auto_migrate_disabled() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+asyncpg://user:pass@localhost:5432/db",
        database_auto_migrate=False,
    )

    await startup_database(settings)
