import logging
from typing import Any

import requests
from fastapi import Request

from microservice_social_sweat import config
from microservice_social_sweat.services.users.models import FilterUser, UserModel

settings = config.get_settings()
log = logging.getLogger(__name__)


def user_matches_filters(user_model: UserModel, filteruser: FilterUser) -> bool:
    if filteruser.id and user_model.id != filteruser.id:
        return False
    if filteruser.role and user_model.user_metadata.role != filteruser.role:
        return False
    return True


def fetch_all_users_from_clerk(headers: dict[str, str]) -> list[dict[str, str]]:
    all_users = []
    limit = 100
    offset = 0

    while True:
        params = {"limit": limit, "offset": offset}
        response = requests.get(
            f"{settings.clerk_api_url}/users",
            headers=headers,
            params=params,
            timeout=20,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch users: {response.status_code} {response.text}")

        users = response.json()

        if not users:
            break

        all_users.extend(users)

        if len(users) < limit:
            break

        offset += limit

    return all_users


def load_users_from_clerk(filteruser: FilterUser) -> list[UserModel]:
    headers = {
        "Authorization": f"Bearer {settings.clerk_api_secret_key}",
        "Content-Type": "application/json",
    }

    users_list = []

    # Fetch the user directly by ID
    if filteruser.id:
        response = requests.get(
            f"{settings.clerk_api_url}/users/{filteruser.id}",
            headers=headers,
            timeout=20,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch user: {response.status_code} {response.text}")
        user_data = response.json()
        user_model = UserModel.from_clerk_user_request(user_data)
        if user_matches_filters(user_model, filteruser):
            users_list.append(user_model)
        return users_list

    # Fetch all users and filter them
    all_users = fetch_all_users_from_clerk(headers)
    for user in all_users:
        user_model = UserModel.from_clerk_user_request(user)
        if user_matches_filters(user_model, filteruser):
            users_list.append(user_model)

    return users_list


def filter_users(request: Request, filter_user: FilterUser) -> Any:
    users = load_users_from_clerk(filter_user)
    return {"users": users}
