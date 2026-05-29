from typing import Any

from pydantic import BaseModel


class PlatformStatusResponse(BaseModel):
    id: str
    name: str
    locales: list[str]
    maintenances: list[dict[str, Any]]
    incidents: list[dict[str, Any]]
