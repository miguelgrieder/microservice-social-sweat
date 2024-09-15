from typing import Any

import requests
from fastapi import Request


async def foo() -> Any:
    return "hello world"


def bar(request: Request) -> Any:

    response = requests.request(
        "get",
        "http://localhost:8888/api",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
