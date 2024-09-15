from typing import Any

from fastapi import Request

from microservice_social_sweat.services.activities.models import Filter



def filter_activities(request: Request, filter: Filter) -> Any:
    if filter.activity_id:
        activities = None
        for ac in activities_dummy_data:
            if int(ac["id"]) == filter.activity_id:
                activities = [ac]
                break
    else:
        activities = activities_dummy_data
    return {"activities": activities}
