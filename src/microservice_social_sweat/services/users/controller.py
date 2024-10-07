import logging
from typing import Any

import requests
from fastapi import HTTPException, Request

from microservice_social_sweat import config
from microservice_social_sweat.services.users.models import (
    FilterUserInput,
    UpdateUserModel,
    UserModel,
)

settings = config.get_settings()
log = logging.getLogger(__name__)


def user_matches_filters(user_model: UserModel, filter_user_input: FilterUserInput) -> bool:
    if filter_user_input.id and user_model.id != filter_user_input.id:
        return False
    if filter_user_input.username and filter_user_input.username not in user_model.username:
        return False
    if filter_user_input.role and user_model.user_metadata.role != filter_user_input.role:
        return False
    if (
        filter_user_input.sport_type
        and user_model.user_metadata.sports
        and filter_user_input.sport_type not in user_model.user_metadata.sports
    ):
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


def load_users_from_clerk(filter_user_input: FilterUserInput) -> list[UserModel]:
    headers = {
        "Authorization": f"Bearer {settings.clerk_api_secret_key}",
        "Content-Type": "application/json",
    }

    users_list = []

    # Fetch the user directly by ID
    if filter_user_input.id:
        response = requests.get(
            f"{settings.clerk_api_url}/users/{filter_user_input.id}",
            headers=headers,
            timeout=20,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to fetch user: {response.status_code} {response.text}")
        user_data = response.json()
        user_model = UserModel.from_clerk_user_request(user_data)
        if user_matches_filters(user_model, filter_user_input):
            users_list.append(user_model)
        return users_list

    # Fetch all users and filter them
    all_users = fetch_all_users_from_clerk(headers)
    for user in all_users:
        try:
            user_model = UserModel.from_clerk_user_request(user)
            if user_matches_filters(user_model, filter_user_input):
                users_list.append(user_model)
        except:
            log.exception(f"Failed to load cler user {user}")

    return users_list


def filter_users(request: Request, filter_user_input: FilterUserInput) -> Any:
    users = load_users_from_clerk(filter_user_input)
    return {"num_items": len(users), "users": users}


def update_user(request: Request, user_id: str, update_data: UpdateUserModel) -> Any:

    headers = {
        "Authorization": f"Bearer {settings.clerk_api_secret_key}",
        "Content-Type": "application/json",
    }

    payload = build_update_user_clerk_payload(headers, update_data, user_id)
    try:
        response = requests.patch(
            f"{settings.clerk_api_url}/users/{user_id}",
            headers=headers,
            json=payload,
            timeout=20,
        )

        if response.status_code != 200:
            log.exception(f"Failed to update user: {response.status_code} {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.json())
        updated_user_data = response.json()
        updated_user = UserModel.from_clerk_user_request(updated_user_data)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return {"user": updated_user}


def build_update_user_clerk_payload(
    headers: dict[str, str], update_data: UpdateUserModel, user_id: str
) -> dict[str, Any]:

    clerk_user_metadatas = get_user_metadatas_clerk(headers, user_id)

    # Prepare the payload for the Clerk API update
    payload: dict[str, Any] = {}
    if update_data.first_name is not None:
        payload["first_name"] = update_data.first_name
    if update_data.last_name is not None:
        payload["last_name"] = update_data.last_name
    if update_data.username is not None:
        payload["username"] = update_data.username

    # Currently all user_metadata is inunsafe_metadata, so its here
    # Will need to change it when using other metadatas
    if update_data.user_metadata is not None:
        user_metadata_dict = update_data.user_metadata.model_dump(exclude_unset=True)
        payload["unsafe_metadata"] = user_metadata_dict

    # Merge current user metadata to don`t overwrite
    if payload.get("unsafe_metadata"):
        merged_unsafe_metadata = {
            **clerk_user_metadatas["existing_unsafe_metadata"],
            **payload["unsafe_metadata"],
        }
        payload["unsafe_metadata"] = merged_unsafe_metadata
    if payload.get("public_metadata") is not None:
        merged_public_metadata = {
            **clerk_user_metadatas["existing_public_metadata"],
            **payload["public_metadata"],
        }
        payload["public_metadata"] = merged_public_metadata
    if payload.get("private_metadata") is not None:
        merged_private_metadata = {
            **clerk_user_metadatas["existing_private_metadata"],
            **payload["private_metadata"],
        }
        payload["private_metadata"] = merged_private_metadata
    return payload


def get_user_metadatas_clerk(headers: dict[str, str], user_id: str) -> dict[str, Any]:
    try:
        existing_user_response = requests.get(
            f"{settings.clerk_api_url}/users/{user_id}",
            headers=headers,
            timeout=20,
        )
        if existing_user_response.status_code != 200:
            log.error(
                f"Failed to fetch existing user data: "
                f"{existing_user_response.status_code} {existing_user_response.text}"
            )
            raise HTTPException(
                status_code=existing_user_response.status_code,
                detail=existing_user_response.json(),
            )
        existing_user_data = existing_user_response.json()
    except requests.exceptions.RequestException as e:
        log.exception("Error fetching existing user data")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

    return {
        "existing_private_metadata": existing_user_data.get("private_metadata", {}),
        "existing_public_metadata": existing_user_data.get("public_metadata", {}),
        "existing_unsafe_metadata": existing_user_data.get("unsafe_metadata", {}),
    }
