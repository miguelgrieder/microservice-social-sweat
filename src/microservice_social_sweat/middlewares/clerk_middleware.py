import logging
from typing import Any, Callable, Optional

from clerk_backend_api import Clerk, Client
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from microservice_social_sweat import config

settings = config.get_settings()
log = logging.getLogger(__name__)


class ClerkMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.clerk_client = Clerk(
            bearer_auth=settings.clerk_api_secret_key,
            debug_logger=log if log else None,
        )

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        if request.url.path in ["/docs", "/openapi.json"]:
            response = await call_next(request)
            return response
        if request.method == "OPTIONS":
            # Allow preflight requests to pass through without authentication
            return await call_next(request)

        auth_header: Optional[str] = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        token: str = auth_header.split("Bearer ")[1]

        try:
            res: Optional[Client] = self.clerk_client.clients.verify(request={"token": token})
            if res is None:
                raise HTTPException(status_code=401, detail="Invalid token")  # noqa: TRY301
            request.state.user = res.id
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token") from e

        # Proceed to the next middleware or endpoint
        response = await call_next(request)
        return response
