from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "APP_ERROR"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ConfigurationError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "CONFIGURATION_ERROR"


class InvalidRegionError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "INVALID_REGION"


class RiotAPIError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    code = "RIOT_API_ERROR"


class RiotNotFoundError(RiotAPIError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "RIOT_NOT_FOUND"


class RiotForbiddenError(RiotAPIError):
    status_code = status.HTTP_502_BAD_GATEWAY
    code = "RIOT_FORBIDDEN"


class RiotRateLimitError(RiotAPIError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "RIOT_RATE_LIMITED"


class RiotUnavailableError(RiotAPIError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "RIOT_UNAVAILABLE"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": {"code": exc.code, "message": exc.message}},
        )
