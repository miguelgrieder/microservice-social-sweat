from typing import Any

from fastapi import Request

activities_dummy_data = []


def get_activities(request: Request) -> Any:
    return {"activities": activities_dummy_data}
