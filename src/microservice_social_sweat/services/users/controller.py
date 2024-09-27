import logging
from typing import Any

import requests
from fastapi import Request

from microservice_social_sweat import config
from microservice_social_sweat.services.users.models import FilterUser, UserModel

settings = config.get_settings()
log = logging.getLogger(__name__)


def load_users_from_clerk(filteruser: FilterUser) -> list[UserModel]:
    headers = {
        "Authorization": f"Bearer {settings.clerk_api_secret_key}",
        "Content-Type": "application/json",
    }

    users_list = []
    limit = 100
    offset = 0

    while True:
        matched_users = []
        params = {"limit": limit, "offset": offset}

        response = requests.get(
            f"{settings.clerk_api_url}/users", headers=headers, params=params, timeout=20
        )
        if response.status_code != 200:
            raise Exception(  # noqa: TRY002, TRY003
                f"Failed to fetch users: {response.status_code} {response.text}"
            )

        users = response.json()

        if not users:
            break

        for user in users:
            role = user.get("unsafe_metadata", {}).get("role")
            if filteruser.role and role == filteruser.role:
                user_model = UserModel.from_clerk_user_request(user)
                matched_users.append(user_model)

        users_list.extend(matched_users)

        if len(users) < limit:
            break

        offset += limit

    return users_list


def filter_users(request: Request, filter_user: FilterUser) -> Any:
    users = load_users_from_clerk(filter_user)
    return {"users": users}
