import logging
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Request, status

from . import controller

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
def get_activities(request: Request) -> Any:
    try:
        result = controller.get_activities(request=request)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e

    return result
