import logging
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor

from microservice_social_sweat import config
from microservice_social_sweat.services.activities.models import (
    Activity,
    FilterActivity,
    UserJoinActivity,
)

from . import models

settings = config.get_settings()
log = logging.getLogger(__name__)

# Setup MongoDB connection
client: MongoClient[Any] = MongoClient(
    f"mongodb://{settings.mongo_variables_username}:"
    f"{settings.mongo_variables_password}@"
    f"{settings.mongo_variables_host}:"
    f"{settings.mongo_variables_port}/"
)
db = client["social_sweat"]
activity_collection: Collection[dict[str, Any]] = db["activities"]


def load_activities_from_mongodb(filter_activity: FilterActivity) -> list[models.Activity]:
    query = {"enabled": True}
    if filter_activity.activity_id:
        query["id"] = str(filter_activity.activity_id)  # type: ignore[assignment]

    # Fetch data from MongoDB
    cursor: Cursor[Any] = activity_collection.find(query)
    activities = [models.Activity(**activity) for activity in cursor]
    return activities


def filter_activities(request: Request, filter_activity: FilterActivity) -> Any:
    activities = load_activities_from_mongodb(filter_activity)
    return {"activities": activities}


def create_activity(create_activity_input: models.CreateActivityInput) -> Any:
    try:
        activity_data = create_activity_input.activity.model_dump()
        result = activity_collection.insert_one(activity_data)
        return {"id": str(result.inserted_id)}
    except Exception as err:
        error_message = "MongoDB create_activity - failed to create activity"
        log.exception(error_message)
        raise err  # noqa: TRY201


def user_join_activity(request: Request, user_join_activity: UserJoinActivity) -> dict[str, str]:
    activity = filter_activities(
        request=request, filter_activity=FilterActivity(activity_id=user_join_activity.activity_id)
    )

    if not activity or not activity.get("activities"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    activity_data: Activity = activity["activities"][0]

    participants_user_ids: list[Optional[str]] = activity_data.participants.participants_user_id
    max_participants: Optional[int] = activity_data.participants.max

    if user_join_activity.user_id in participants_user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already joined the activity"
        )

    if max_participants is not None and len(participants_user_ids) >= max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity has reached its maximum number of participants",
        )

    participants_user_ids.append(user_join_activity.user_id)
    update_activity_participants(participants_user_ids, user_join_activity)

    return {"message": "User successfully joined the activity"}


def update_activity_participants(
    participants: list[Optional[str]], user_join_activity: UserJoinActivity
) -> None:
    update_result = db.activities.update_one(
        {"id": user_join_activity.activity_id},
        {"$set": {"participants.participants_user_id": participants}},
    )
    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update activity participants",
        )
