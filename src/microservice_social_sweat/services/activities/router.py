import logging

import requests
from fastapi import APIRouter, HTTPException, Request, status

from microservice_social_sweat.services.utils import verify_user_id_is_the_same_from_jwt

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
    request: Request,
    create_activity_input: models.CreateActivityInput,
) -> models.CreateActivityResponse:
    verify_user_id_is_the_same_from_jwt(request, create_activity_input.activity.host.host_user_id)
    try:
        result = controller.create_activity(create_activity_input=create_activity_input)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e

    return result


@router.put("/update", status_code=status.HTTP_200_OK)
def update_activity(
    request: Request,
    update_activity_input: models.UpdateActivityInput,
) -> models.UpdateActivityResponse:
    try:
        result = controller.update_activity(request, update_activity_input=update_activity_input)
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=[{"msg": "HTTPError at external API call."}],
        ) from e

    return result


@router.put("/state", status_code=status.HTTP_201_CREATED)
def update_activity_state(
    request: Request,
    update_activity_state_input: models.UpdateActivityStateInput,
) -> models.UpdateActivityStateResponse:
    verify_user_id_is_the_same_from_jwt(request, update_activity_state_input.user_id)
    try:
        result = controller.update_activity_state(
            update_activity_state_input=update_activity_state_input
        )
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
    verify_user_id_is_the_same_from_jwt(request, user_interact_activity_input.user_id)
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
