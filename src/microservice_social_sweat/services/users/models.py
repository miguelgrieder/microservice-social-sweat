from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

from microservice_social_sweat.services.activities.models import SportType


class FilterUser(BaseModel):
    role: str


class Role(str, Enum):
    coach = "coach"
    user = "user"
    company = "company"


class UserMetadata(BaseModel):
    role: Role
    sports: Optional[list[SportType]]
    birth_date: str


class UserModel(BaseModel):
    id: str
    user_metadata: UserMetadata
    email_address: Optional[str]
    phone_number: Optional[str]
    image_url: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    last_active_at: Optional[int]
    created_at: int

    @staticmethod
    def from_clerk_user_request(user: dict[str, Any]) -> "UserModel":
        role = user.get("unsafe_metadata", {}).get("role")
        sports = user.get("unsafe_metadata", {}).get("sports")
        birth_date = user.get("unsafe_metadata", {}).get("birth_date")

        user_metadata = UserMetadata(
            role=role,
            sports=sports,
            birth_date=birth_date,
        )

        return UserModel(
            id=user["id"],
            user_metadata=user_metadata,
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
