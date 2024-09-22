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
            if filteruser.unsafe_metadata_role and role == filteruser.unsafe_metadata_role:
                # Extract required fields
                user_model = UserModel(
                    id=user["id"],
                    public_metadata=user.get("public_metadata", {}),
                    private_metadata=user.get("private_metadata"),
                    unsafe_metadata=user.get("unsafe_metadata", {}),
                    email_address=(
                        user.get("email_addresses", [{}])[0].get("email_address")
                        if user.get("email_addresses")
                        else None
                    ),
                    phone_number=(
                        user.get("phone_numbers", [{}])[0].get("phone_number")
                        if user.get("phone_numbers")
                        else None
                    ),
                    image_url=user.get("image_url"),
                    username=user.get("username"),
                    first_name=user.get("first_name"),
                    last_name=user.get("last_name"),
                    last_active_at=user.get("last_active_at"),
                    created_at=user.get("created_at"),
                )
                matched_users.append(user_model)

        users_list.extend(matched_users)

        if len(users) < limit:
            break

        offset += limit

    return users_list


def filter_users(request: Request, filter_user: FilterUser) -> Any:
    users = load_users_from_clerk(filter_user)
    return {"users": users}
