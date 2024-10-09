import logging
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor

from microservice_social_sweat import config
from microservice_social_sweat.services.activities import models

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


def load_activities_from_mongodb(
    filter_activity_input: models.FilterActivityInput,
) -> list[models.Activity]:
    query: dict[str, Any] = {"enabled": True}

    if filter_activity_input.activity_id:
        query["id"] = filter_activity_input.activity_id

    if filter_activity_input.activity_name:
        query["name"] = {"$regex": filter_activity_input.activity_name, "$options": "i"}

    if filter_activity_input.participant_user_id:
        query["participants.participants_user_id"] = filter_activity_input.participant_user_id

    if filter_activity_input.host_user_id:
        query["host.host_user_id"] = filter_activity_input.host_user_id

    if filter_activity_input.activity_type:
        query["activity_type"] = filter_activity_input.activity_type

    if filter_activity_input.price is not None:
        query["price.value"] = int(filter_activity_input.price)  # TODO: Be float!

    if filter_activity_input.sport_types:
        query["sport_type"] = {"$in": filter_activity_input.sport_types}

    # Initialize datetime filter conditions
    datetime_filters: dict[str, Any] = {}

    if filter_activity_input.datetime_start:
        datetime_filters["datetimes.datetime_start"] = {
            "$gte": filter_activity_input.datetime_start.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        }

    if filter_activity_input.datetime_finish:
        datetime_filters["datetimes.datetime_finish"] = {
            "$lte": filter_activity_input.datetime_finish.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            + "Z"
        }

    # Apply conditional datetime filters only if activity_type is not 'spot'
    if datetime_filters:
        # Construct the conditional part of the query
        conditional_query = {
            "$or": [
                {"activity_type": "spot"},  # If activity_type is 'spot', ignore datetime filters
                {
                    "activity_type": {"$ne": "spot"},  # If not 'spot', apply datetime filters
                    **datetime_filters,
                },
            ]
        }

        # Combine the base query with the conditional query using $and
        combined_query = {"$and": [query, conditional_query]}
    else:
        # If no datetime filters, use the base query as is
        combined_query = query

    # Fetch data from MongoDB
    cursor: Cursor[Any] = activity_collection.find(combined_query)
    activities = [models.Activity(**activity) for activity in cursor]
    return activities


def filter_activities(request: Request, filter_activity_input: models.FilterActivityInput) -> Any:
    activities = load_activities_from_mongodb(filter_activity_input)
    return {"num_items": len(activities), "activities": activities}


def create_activity(create_activity_input: models.CreateActivityInput) -> Any:
    try:
        activity_data = create_activity_input.activity.model_dump()
        result = activity_collection.insert_one(activity_data)
        return {"id": str(result.inserted_id)}
    except Exception as err:
        error_message = "MongoDB create_activity - failed to create activity"
        log.exception(error_message)
        raise err  # noqa: TRY201


def user_interact_activity(
    request: Request, user_interact_activity_input: models.UserInteractActivityInput
) -> dict[str, str]:
    activity = filter_activities(
        request=request,
        filter_activity_input=models.FilterActivityInput(
            activity_id=user_interact_activity_input.activity_id
        ),
    )

    if not activity or not activity.get("activities"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    activity_data: models.Activity = activity["activities"][0]

    participants_user_ids: list[Optional[str]] = activity_data.participants.participants_user_id
    max_participants: Optional[int] = activity_data.participants.max

    if user_interact_activity_input.action == "join":
        if user_interact_activity_input.user_id in participants_user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already joined the activity"
            )

        if max_participants is not None and len(participants_user_ids) >= max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Activity has reached its maximum number of participants",
            )

        participants_user_ids.append(user_interact_activity_input.user_id)
        update_activity_participants(
            participants_user_ids, user_interact_activity_input.activity_id
        )
        return {"message": "User successfully joined the activity"}

    elif user_interact_activity_input.action == "leave":
        if user_interact_activity_input.user_id not in participants_user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a participant of the activity",
            )

        participants_user_ids.remove(user_interact_activity_input.user_id)
        update_activity_participants(
            participants_user_ids, user_interact_activity_input.activity_id
        )
        return {"message": "User successfully left the activity"}

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{user_interact_activity_input.action}'",
        )


def update_activity_participants(participants: list[Optional[str]], activity_id: str) -> None:
    update_result = db.activities.update_one(
        {"id": activity_id},
        {"$set": {"participants.participants_user_id": participants}},
    )
    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update activity participants",
        )
