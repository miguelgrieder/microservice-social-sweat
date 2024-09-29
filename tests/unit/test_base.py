from typing import Any, Callable
from unittest.mock import patch

from fastapi import Request
from fastapi.testclient import TestClient

from microservice_social_sweat import main
from microservice_social_sweat.middlewares.clerk_middleware import ClerkMiddleware


def test_health_check_endpoint() -> None:
    async def mock_dispatch(
        _: ClerkMiddleware, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        return await call_next(request)

    with patch.object(ClerkMiddleware, "dispatch", new=mock_dispatch):
        with TestClient(app=main.app) as client:
            response = client.get("/health_check")

    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
