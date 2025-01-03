import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from pydantic import ValidationError
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor

from microservice_social_sweat import config
from microservice_social_sweat.services.activities import models
from microservice_social_sweat.services.utils import verify_user_id_is_the_same_from_jwt

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
    combined_query = build_activity_query(filter_activity_input)
    activities = fetch_and_parse_activities(combined_query)

    return activities


def build_activity_query(filter_activity_input: models.FilterActivityInput) -> dict[str, Any]:
    query: dict[str, Any] = {}

    if filter_activity_input.enabled and not filter_activity_input.activity_id:
        query["enabled"] = filter_activity_input.enabled

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
        query["price.value"] = {"$lte": filter_activity_input.price}

    if filter_activity_input.sport_types:
        query["sport_type"] = {"$in": filter_activity_input.sport_types}

    combined_query = combine_datetime_querys(filter_activity_input, query)
    return combined_query


def fetch_and_parse_activities(combined_query: dict[str, Any]) -> list[models.Activity]:
    cursor: Cursor[Any] = activity_collection.find(combined_query)
    activities: list[models.Activity] = []
    failed_count = 0

    for activity_data in cursor:
        try:
            activity = models.Activity(**activity_data)
            activities.append(activity)
        except ValidationError:
            failed_count += 1
            mongo_id = (
                activity_data.get("_id") if isinstance(activity_data, dict) else activity_data
            )
            log.exception(f"Failed to parse activity mongo _id: {mongo_id}")
            continue

    if failed_count > 0:
        log.warning(f"Failed to parse {failed_count} activities.")

    return activities


def combine_datetime_querys(
    filter_activity_input: models.FilterActivityInput, query: dict[str, Any]
) -> dict[str, Any]:
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
    return combined_query


def filter_activities(
    request: Request, filter_activity_input: models.FilterActivityInput
) -> models.FilterActivityResponse:
    activities = load_activities_from_mongodb(filter_activity_input)
    return models.FilterActivityResponse(num_items=len(activities), activities=activities)


def create_activity(
    create_activity_input: models.CreateActivityInput,
) -> models.CreateActivityResponse:
    try:
        activity_data = create_activity_input.activity.model_dump()
        result = activity_collection.insert_one(activity_data)
        return models.CreateActivityResponse(id=str(result.inserted_id))
    except Exception as err:
        error_message = "MongoDB create_activity - failed to create activity"
        log.exception(error_message)
        raise err  # noqa: TRY201


def remove_none_values(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: remove_none_values(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_none_values(item) for item in data if item is not None]
    else:
        return data


def update_activity(
    request: Request,
    update_activity_input: models.UpdateActivityInput,
) -> models.UpdateActivityResponse:
    try:
        activity_id = update_activity_input.id
        # Retrieve the existing activity from MongoDB
        existing_activity = activity_collection.find_one({"id": activity_id})

        if not existing_activity:
            raise HTTPException(  # noqa: TRY301
                status_code=status.HTTP_404_NOT_FOUND,
                detail=[{"msg": f"Activity with id '{activity_id}' not found."}],
            )
        # get datetimes separated
        if update_activity_input and update_activity_input.update_activity_data:
            datetimes = update_activity_input.update_activity_data.datetimes
            update_activity_input.update_activity_data.datetimes = None

        # Merge existing data with the updated data
        update_data = (
            remove_none_values(update_activity_input.update_activity_data.model_dump())
            if update_activity_input.update_activity_data
            else {}
        )
        # Specific items
        if update_activity_input.max_participants is not None:
            update_data["participants"] = update_data.get("participants", {})
            update_data["participants"]["max"] = update_activity_input.max_participants

        merged_data = {**existing_activity, **update_data}

        if datetimes and datetimes.datetime_start is not None:
            merged_data["datetimes"] = merged_data.get("datetimes", {})
            merged_data["datetimes"]["datetime_start"] = datetimes.datetime_start
        if datetimes and datetimes.datetime_finish is not None:
            merged_data["datetimes"] = merged_data.get("datetimes", {})
            merged_data["datetimes"]["datetime_finish"] = datetimes.datetime_finish

        # Validate the merged data using the Activity model
        try:
            validated_activity = models.Activity(**merged_data)
        except ValidationError as validation_err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[
                    {
                        "msg": "Validation failed for updated activity data.",
                        "errors": validation_err.errors(),
                    }
                ],
            ) from validation_err

        verify_user_id_is_the_same_from_jwt(request, validated_activity.host.host_user_id)
        # Perform the update in MongoDB after validation
        result = activity_collection.update_one(
            {"id": activity_id},  # Find the activity by its 'id'
            {"$set": validated_activity.model_dump()},  # Use validated data for update
        )

        if result.matched_count == 0:
            raise HTTPException(  # noqa: TRY301
                status_code=status.HTTP_404_NOT_FOUND,
                detail=[{"msg": f"Activity with id '{activity_id}' not found."}],
            )

        return models.UpdateActivityResponse(id=activity_id)

    except Exception as err:
        error_message = "MongoDB update_activity - failed to update activity"
        log.exception(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=[{"msg": error_message}]
        ) from err


def update_activity_state(
    update_activity_state_input: models.UpdateActivityStateInput,
) -> models.UpdateActivityStateResponse:
    try:
        enabled = True if update_activity_state_input.action == "enable" else False
        filter_expression = {
            "id": update_activity_state_input.activity_id,
            "host.host_user_id": update_activity_state_input.user_id,
        }
        update_expression = {"$set": {"enabled": enabled}}
        if enabled:
            current_datetime = (
                datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            )
            update_expression["$set"]["datetimes.datetime_deleted"] = current_datetime  # type: ignore[assignment]

        result = activity_collection.update_many(filter_expression, update_expression)

        return models.UpdateActivityStateResponse(
            acknowledged=result.acknowledged,
            modified_count=result.modified_count,
            matched_count=result.matched_count,
        )
    except Exception as err:
        error_message = (
            f"MongoDB update_activity_state - failed to update activity "
            f"state {update_activity_state_input}"
        )
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

    if activity.activities:
        activity_data = activity.activities[0]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

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
