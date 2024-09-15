import logging
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Request, status

from . import controller

log = logging.getLogger(__name__)

router = APIRouter(prefix="/generic_prefix")


@router.get(
    "/",
    summary="",
    description="",
    response_model=Any,
    status_code=200,
)
async def foo() -> Any:
    result = await controller.foo()

    return result


@router.get("/external")
def bar(request: Request) -> Any:
    try:
        result = controller.bar(request=request)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e

    return result
