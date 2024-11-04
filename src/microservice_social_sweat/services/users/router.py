import logging

import requests
from fastapi import APIRouter, HTTPException, Request, status

from microservice_social_sweat.services.utils import verify_user_id_is_the_same_from_jwt

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
) -> models.UpdateUserResponse:
    verify_user_id_is_the_same_from_jwt(request, user_id)

    try:
        result = controller.update_user(request=request, user_id=user_id, update_data=update_data)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e
    else:
        return result
