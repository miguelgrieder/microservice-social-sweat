import logging
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Request, status

from . import controller, models

log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
def filter_users(
    request: Request, filter_user_input: models.FilterUserInput
) -> models.FilterUserResponse:
    try:
        result = controller.filter_users(request=request, filter_user_input=filter_user_input)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e

    return result


@router.put("/{user_id}")
def update_user_endpoint(
    request: Request, user_id: str, update_data: models.UpdateUserModel
) -> Any:
    # Check if the authenticated user is updating their own data
    # authenticated_user_id = request.state.user
    # if authenticated_user_id != user_id:
    #     raise HTTPException(status_code=403, detail="Forbidden: Cannot update other user's data")

    try:
        result = controller.update_user(request=request, user_id=user_id, update_data=update_data)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e
    else:
        return result
