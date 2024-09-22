import logging
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Request, status

from . import controller, models

log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
def filter_users(request: Request, filter_user: models.FilterUser) -> Any:
    try:
        result = controller.filter_users(request=request, filter_user=filter_user)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e

    return result
