import json
from typing import Any

from fastapi import Request

from microservice_social_sweat.services.activities.models import FilterActiviity

from . import models


def load_activities_from_json(filename: str) -> list[models.Activity]:
    with open(filename, "r") as file:
        data = json.load(file)
    return [models.Activity(**item) for item in data]


def filter_activities(request: Request, filter_activity: FilterActiviity) -> Any:
    model_activities = load_activities_from_json(
        "src/microservice_social_sweat/services/activities/activities_data.json"
    )
    if filter_activity.activity_id:
        activities = None
        for activity in model_activities:
            if activity.id == filter_activity.activity_id:
                activities = [activity]
                break
    else:
        activities = model_activities
    return {"activities": activities}
