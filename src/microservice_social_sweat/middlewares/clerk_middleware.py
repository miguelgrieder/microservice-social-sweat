import logging
from typing import Any, Callable, Optional

import jwt
from fastapi import HTTPException, Request
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from microservice_social_sweat import config

settings = config.get_settings()
log = logging.getLogger(__name__)


class ClerkMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.public_key = settings.clerk_jwt_public_key

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        if request.url.path in [
            "/docs",
            "/openapi.json",
            "/activities/",
            "/activities/",
            "/users/",
        ]:
            return await call_next(request)
        if request.method == "OPTIONS":
            # Allow preflight requests to pass through without authentication
            return await call_next(request)

        auth_header: Optional[str] = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        token: str = auth_header.split("Bearer ")[1]

        try:
            payload = jwt.decode(token, key=self.public_key, algorithms=["RS256"])
        except PyJWTError as e:
            if not settings.ignore_expired_jwt and isinstance(e, ExpiredSignatureError):
                raise HTTPException(status_code=401, detail="Invalid token") from e
            else:
                payload = jwt.decode(
                    token,
                    key=self.public_key,
                    algorithms=["RS256"],
                    options={"verify_exp": False},
                )
        request.state.user_id = payload["sub"]
        # Proceed to the next middleware or endpoint
        response = await call_next(request)
        return response
