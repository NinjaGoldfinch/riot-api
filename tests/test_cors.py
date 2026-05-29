from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.cors import configure_cors


def test_settings_parses_cors_origins() -> None:
    settings = Settings(
        _env_file=None,
        cors_allowed_origins="http://localhost:3000, http://127.0.0.1:3000",
    )

    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


async def test_cors_allows_configured_origin() -> None:
    app = FastAPI()
    configure_cors(
        app,
        Settings(_env_file=None, cors_allowed_origins="http://localhost:3000"),
    )

    @app.get("/resource")
    async def resource() -> dict[str, str]:
        return {"status": "ok"}

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/resource", headers={"Origin": "http://localhost:3000"})

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"


async def test_cors_is_disabled_without_origins() -> None:
    app = FastAPI()
    configure_cors(app, Settings(_env_file=None, cors_allowed_origins=""))

    @app.get("/resource")
    async def resource() -> dict[str, str]:
        return {"status": "ok"}

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/resource", headers={"Origin": "http://localhost:3000"})

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers
