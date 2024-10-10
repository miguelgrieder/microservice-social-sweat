import logging

import requests
from fastapi import APIRouter, HTTPException, Request, status

from . import controller, models

log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
def filter_activities(
    request: Request, filter_activity_input: models.FilterActivityInput
) -> models.FilterActivityResponse:
    try:
        result = controller.filter_activities(
            request=request, filter_activity_input=filter_activity_input
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e

    return result


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_activity(
    create_activity_input: models.CreateActivityInput,
) -> models.CreateActivityResponse:
    try:
        result = controller.create_activity(create_activity_input=create_activity_input)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e

    return result


@router.post("/user_interact_activity")
async def user_interact_activity(
    request: Request, user_interact_activity_input: models.UserInteractActivityInput
) -> dict[str, str]:
    try:
        result = controller.user_interact_activity(
            request=request, user_interact_activity_input=user_interact_activity_input
        )
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e

    return result
