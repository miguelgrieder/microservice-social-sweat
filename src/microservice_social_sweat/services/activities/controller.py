import logging
from typing import Any, List

from fastapi import Request
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor

from microservice_social_sweat import config
from microservice_social_sweat.services.activities.models import FilterActiviity

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


def load_activities_from_mongodb(filter_activity: FilterActiviity) -> List[models.Activity]:
    query = {"enabled": True}
    if filter_activity.activity_id:
        query["id"] = str(filter_activity.activity_id)  # type: ignore[assignment]

    # Fetch data from MongoDB
    cursor: Cursor[Any] = activity_collection.find(query)
    activities = [models.Activity(**activity) for activity in cursor]
    return activities


def filter_activities(request: Request, filter_activity: FilterActiviity) -> Any:
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
        raise err
